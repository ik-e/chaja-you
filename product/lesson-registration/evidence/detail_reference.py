"""Isolated SQLite/capability reference, deliberately NOT product or real auth/runtime.

Models authorization linearization and evidence CAS, not external dispatch atomicity.
All identities and simulated observations in tests are synthetic.
"""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import secrets
import sqlite3
import threading
from contracts.canonical import json_digest

class Denied(Exception):
    pass

def require(ok):
    if not ok:
        raise Denied("candidate guard rejected")

class Ledger:
    def __init__(self, path):
        self.path = path
        with self.tx() as c:
            c.execute("CREATE TABLE jobs(id TEXT PRIMARY KEY, owner TEXT, binding TEXT, ops TEXT, state TEXT, claim TEXT, bound INTEGER DEFAULT 0, version INTEGER DEFAULT 0)")
            c.execute("CREATE TABLE admissions(token TEXT PRIMARY KEY, job TEXT, op TEXT, logical_effect TEXT UNIQUE, status TEXT)")
            c.execute("CREATE TABLE evidence(id TEXT PRIMARY KEY, job TEXT, op TEXT, body TEXT)")

    @contextmanager
    def tx(self):
        c = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        c.row_factory = sqlite3.Row
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.commit()
        except BaseException:
            c.rollback()
            raise
        finally:
            c.close()

    def add(self, job, owner, binding, ops):
        # Trusted accepted snapshot passed by test; not public H7 implementation.
        with self.tx() as c:
            c.execute("INSERT INTO jobs(id,owner,binding,ops,state) VALUES(?,?,?,?, 'active')",
                      (job, owner, json_digest(binding), json_digest(ops)))

    def claim(self, job, owner):
        claim = secrets.token_hex(16)
        with self.tx() as c:
            n = c.execute("UPDATE jobs SET claim=? WHERE id=? AND owner=? AND state='active' AND claim IS NULL",
                          (claim, job, owner)).rowcount
            return claim if n == 1 else None

    def _job(self, c, job, claim):
        r = c.execute("SELECT * FROM jobs WHERE id=?", (job,)).fetchone()
        require(r is not None and claim is not None and r["claim"] == claim)
        return r

    def bind(self, job, claim, connection):
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] == "active" and r["binding"] == json_digest(connection) and not r["bound"])
            c.execute("UPDATE jobs SET bound=1 WHERE id=?", (job,))

    def admit(self, job, claim, ops, op, logical_effect):
        # ops is a trusted registry snapshot; runtime derives logical_effect, never client input.
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] == "active" and r["bound"] and r["ops"] == json_digest(ops) and op in ops)
            token = secrets.token_hex(16)
            try:
                c.execute("INSERT INTO admissions VALUES(?,?,?,?, 'reserved')",
                          (token, job, json_digest(op), logical_effect))
            except sqlite3.IntegrityError as exc:
                raise Denied("duplicate reservation") from None
            c.execute("UPDATE jobs SET version=version+1 WHERE id=?", (job,))
            return token

    def consume(self, job, claim, token):
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] == "active" and r["bound"])
            n = c.execute("UPDATE admissions SET status='in_flight' WHERE token=? AND job=? AND status='reserved'", (token,job)).rowcount
            require(n == 1)
            c.execute("UPDATE jobs SET version=version+1 WHERE id=?", (job,))

    def fence(self, job, claim):
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] in ("active", "stopping"))
            c.execute("UPDATE jobs SET state='stopping',version=version+1 WHERE id=?", (job,))
            # Unconsumed reservations never enter candidate dispatch; no real external absence asserted.
            c.execute("UPDATE admissions SET status='blocked' WHERE job=? AND status='reserved'", (job,))
            c.execute("UPDATE admissions SET status='unknown' WHERE job=? AND status='in_flight'", (job,))

    def observe(self, job, claim, token, op, evidence_id, observed, verdict):
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] in ("active", "stopping") and r["bound"])
            a = c.execute("SELECT * FROM admissions WHERE token=? AND job=?", (token,job)).fetchone()
            require(a is not None and a["op"] == json_digest(op) and
                    a["status"] in ("in_flight","unknown","confirmed","absent"))
            require(verdict in ("confirmed","absent","unknown"))
            # This only models trusted evidence identity; not proof of actual readback.
            body = json_digest({"observed": observed, "verdict": verdict})
            prior = c.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
            if prior:
                require(prior["job"] == job and prior["op"] == a["op"] and prior["body"] == body)
                return
            require(a["status"] in ("in_flight","unknown") or a["status"] == verdict)
            c.execute("INSERT INTO evidence VALUES(?,?,?,?)", (evidence_id,job,a["op"],body))
            c.execute("UPDATE admissions SET status=? WHERE token=?", (verdict,token))
            c.execute("UPDATE jobs SET version=version+1 WHERE id=?", (job,))

    def snapshot(self, job):
        with self.tx() as c:
            r = c.execute("SELECT state,version FROM jobs WHERE id=?", (job,)).fetchone()
            statuses = [x[0] for x in c.execute("SELECT status FROM admissions WHERE job=?",(job,))]
            return r["state"],r["version"],statuses

    def finalize(self, job, claim, version, confirmed_goal, required_count):
        # Synthetic goal boolean is injected by the independent test, not a product I5.
        with self.tx() as c:
            r = self._job(c, job, claim)
            require(r["state"] in ("active","stopping") and r["version"] == version)
            statuses = [x[0] for x in c.execute("SELECT status FROM admissions WHERE job=?",(job,))]
            done = (r["state"] == "active" and confirmed_goal and len(statuses) == required_count
                    and required_count > 0 and all(s == "confirmed" for s in statuses))
            if not done:
                c.execute("UPDATE admissions SET status='unknown' WHERE job=? AND status IN ('reserved','in_flight')", (job,))
            state = "done" if done else "stopped"
            c.execute("UPDATE jobs SET state=?,claim=NULL,bound=0,version=version+1 WHERE id=?", (state,job))
            return state

class ViewerPolicy:
    """In-memory grant/input gate reference. No actual websocket, browser or service authentication."""
    def __init__(self, owner, registration, origin):
        self.owner, self.registration, self.origin = owner, registration, origin
        self.lock = threading.Lock()
        self.generation = 0
        self.state = "human"
        self.token_hash = None
        self.connection = None
        self.expires = 0
        self.queue = []
        self.audit = []

    def issue(self, owner, now, ttl):
        with self.lock:
            require(owner == self.owner and self.state == "human" and ttl > 0)
            token = secrets.token_urlsafe(32)
            self.generation += 1
            self.token_hash = hashlib.sha256(token.encode()).digest()
            self.connection = None
            self.queue.clear()
            self.expires = now + ttl
            self.audit.append("issue")
            return token, self.generation

    def attach(self, owner, registration, origin, token, generation, now):
        with self.lock:
            require(self.state == "human" and owner == self.owner and registration == self.registration
                    and origin == self.origin and generation == self.generation and now < self.expires
                    and self.token_hash is not None
                    and secrets.compare_digest(self.token_hash, hashlib.sha256(token.encode()).digest()))
            self.token_hash = None
            self.connection = secrets.token_hex(16)
            self.audit.append("attach")
            return self.connection

    def input(self, conn, generation, now, kind, value):
        with self.lock:
            require(self.state == "human" and conn is not None and conn == self.connection
                    and generation == self.generation and now < self.expires
                    and kind in ("pointer","wheel","key","text") and len(self.queue) < 8)
            self.queue.append((kind, value))
            # Do not audit input event contents, lengths, or counts.

    def finish(self, owner, generation):
        with self.lock:
            require(owner == self.owner and self.state == "human" and generation == self.generation)
            self.state = "verifying"
            self.connection = self.token_hash = None
            self.queue.clear()
            self.audit.append("finish")

    def detach(self, conn):
        with self.lock:
            if conn == self.connection:
                self.connection = None
                self.queue.clear()
                self.audit.append("detach")

    def close(self):
        with self.lock:
            self.state = "closed"
            self.connection = self.token_hash = None
            self.queue.clear()
            self.audit.append("close")

class RevisionGate:
    def __init__(self):
        self.lock = threading.Lock()
        self.revision = 1
        self.value = None
    def invalidate(self):
        with self.lock:
            self.revision += 1
    def commit(self, version, value):
        with self.lock:
            if version != self.revision:
                return False
            self.value = deepcopy(value)
            self.revision += 1
            return True
