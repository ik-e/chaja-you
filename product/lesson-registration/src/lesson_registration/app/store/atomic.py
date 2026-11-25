"""STORE atomic operations (common-integration-v1 ``storage.operations``).

accept (S-ACCEPT), acquire_lease (RT-01 lease), admit (S-ADMIT), observe (S-OBSERVE),
fence / finalize (S-FENCE). All functions run inside a caller-held
``BEGIN IMMEDIATE`` transaction and never call external ports.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3


class StoreRejected(Exception):
    """Typed STORE refusal; ``code`` is an Error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ---------- lookups ----------
def find_job_by_key(conn: sqlite3.Connection, owner_ref: str, request_key: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM jobs WHERE owner_ref=? AND request_key=?", (owner_ref, request_key)
    ).fetchone()


def find_job(conn: sqlite3.Connection, registration_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM jobs WHERE registration_id=?", (registration_id,)).fetchone()


def _job_or_raise(conn: sqlite3.Connection, registration_id: str) -> sqlite3.Row:
    job = find_job(conn, registration_id)
    if job is None:
        raise StoreRejected("NOT_FOUND", "no accepted job")
    return job


def target_key(identity: dict) -> str:
    return json.dumps(
        [identity["environment"], identity["platform"], identity["external_account_ref"],
         identity["object_kind"], identity["slot_ref"]],
        ensure_ascii=False,
    )


def effect_key(identity: dict, operation_id: str) -> str:
    """(environment, platform, external_account_ref, object_kind, slot_ref, logical_operation_id)."""
    return json.dumps(
        [identity["environment"], identity["platform"], identity["external_account_ref"],
         identity["object_kind"], identity["slot_ref"], operation_id],
        ensure_ascii=False,
    )


def blocking_jobs_for_target(conn: sqlite3.Connection, identity: dict, exclude_registration: str) -> list[str]:
    """Other accepted jobs on the same target whose effect is unresolved, confirmed or ambiguous.

    A stopped job blocks unless every effect it reserved is proven absent.
    """
    wanted = target_key(identity)
    blocking: list[str] = []
    for row in conn.execute(
        "SELECT registration_id, state, accepted_scope_json FROM jobs WHERE registration_id != ?",
        (exclude_registration,),
    ):
        scope = json.loads(row["accepted_scope_json"])["scope"]
        if target_key(scope["target"]) != wanted:
            continue
        if row["state"] != "stopped":
            blocking.append(row["registration_id"])
            continue
        open_effects = conn.execute(
            "SELECT 1 FROM effects WHERE registration_id=? AND status != 'absent' LIMIT 1",
            (row["registration_id"],),
        ).fetchone()
        if open_effects is not None:
            blocking.append(row["registration_id"])
    return blocking


# ---------- S-ACCEPT ----------
def accept(
    conn: sqlite3.Connection,
    owner_ref: str,
    registration_id: str,
    request_key: str,
    request_digest: str,
    accepted_scope: dict,
    new_revision: int,
    now: str,
) -> None:
    """Write immutable scope + key + active job and mark the registration started, together."""
    conn.execute(
        "INSERT INTO jobs(registration_id, owner_ref, request_key, request_digest, accepted_scope_json, state,"
        " accepted_at, updated_at) VALUES (?,?,?,?,?, 'active', ?, ?)",
        (registration_id, owner_ref, request_key, request_digest,
         json.dumps(accepted_scope, ensure_ascii=False, sort_keys=True), now, now),
    )
    cur = conn.execute(
        "UPDATE registrations SET job_state='active', revision=?, updated_at=?"
        " WHERE owner_ref=? AND registration_id=? AND job_state IS NULL",
        (new_revision, now, owner_ref, registration_id),
    )
    if cur.rowcount != 1:
        raise RuntimeError("registration changed during accept")  # caller's guards make this unreachable


# ---------- RT-01 lease ----------
def acquire_lease(conn: sqlite3.Connection, registration_id: str, lease: str, now: str) -> None:
    """Exclusive worker lease. Only an active job without a current worker may be leased."""
    job = _job_or_raise(conn, registration_id)
    if job["state"] != "active":
        raise StoreRejected("INVALID_PHASE", f"job is {job['state']}")
    if job["worker_lease"] is not None:
        raise StoreRejected("INVALID_PHASE", "job already has a worker")
    conn.execute("UPDATE jobs SET worker_lease=?, updated_at=? WHERE registration_id=?", (lease, now, registration_id))


# ---------- S-ADMIT ----------
def admit(
    conn: sqlite3.Connection,
    registration_id: str,
    lease: str,
    operation: dict,
    expected_binding: str,
    step_effect_class: str,
    now: str,
) -> str:
    """One-shot permit. Potential effects reserve a stable effect key before any external mutation."""
    job = _job_or_raise(conn, registration_id)
    if job["worker_lease"] is None or job["worker_lease"] != lease:
        raise StoreRejected("PERMISSION_DENIED", "stale or foreign worker lease")
    scope = json.loads(job["accepted_scope_json"])["scope"]
    if operation["step_id"] not in scope["procedure_ids"]:
        raise StoreRejected("PERMISSION_DENIED", "operation step is not in the accepted procedure")
    if operation["effect_class"] != step_effect_class:
        raise StoreRejected("PERMISSION_DENIED", "operation effect class differs from the profile step")
    if operation["binding_digest"] != expected_binding:
        raise StoreRejected("PERMISSION_DENIED", "operation is not bound to the accepted values")
    if operation["effect_class"] == "read":
        if job["state"] not in ("active", "stopping"):
            raise StoreRejected("INVALID_PHASE", f"job is {job['state']}")
        return f"read:{operation['operation_id']}"
    if job["state"] != "active":
        raise StoreRejected("INVALID_PHASE", "job is fenced; no new effects")
    # Logical operation identity is the profile step, so a new operation_id cannot bypass an existing effect.
    key = effect_key(scope["target"], operation["step_id"])
    existing = conn.execute("SELECT status FROM effects WHERE effect_key=?", (key,)).fetchone()
    if existing is not None and existing["status"] != "absent":
        raise StoreRejected("DUPLICATE_RISK", f"effect already {existing['status']}")
    conn.execute(
        "INSERT INTO effects(effect_key, registration_id, operation_id, step_id, action_key, effect_class,"
        " binding_digest, status, admitted_at) VALUES (?,?,?,?,?,?,?, 'reserved', ?)"
        " ON CONFLICT(effect_key) DO UPDATE SET status='reserved', registration_id=excluded.registration_id,"
        " admitted_at=excluded.admitted_at, resolved_at=NULL",
        (key, registration_id, operation["operation_id"], operation["step_id"], operation["action_key"],
         operation["effect_class"], operation["binding_digest"], now),
    )
    return f"effect:{key}"


# ---------- S-OBSERVE ----------
_REFINE = {
    # current status -> statuses an observation may move it to (confirmed is never downgraded)
    "reserved": {"confirmed", "absent", "unknown"},
    "unknown": {"confirmed", "absent"},
    "absent": {"confirmed"},
    "confirmed": set(),
}


def observe(
    conn: sqlite3.Connection,
    registration_id: str,
    lease: str | None,
    observation: dict,
    evidence: list[dict],
    now: str,
) -> None:
    """Record actual observations and evidence; dedupe by id.

    While the job runs the current lease is required. After a terminal state, late read-only
    evidence may refine existing effects but never reopens the job.
    """
    job = _job_or_raise(conn, registration_id)
    terminal = job["state"] in ("done", "stopped")
    if not terminal and (job["worker_lease"] is None or job["worker_lease"] != lease):
        raise StoreRejected("PERMISSION_DENIED", "stale or foreign worker lease")
    scope = json.loads(job["accepted_scope_json"])["scope"]
    if observation["target"] != scope["target"]:
        raise StoreRejected("PERMISSION_DENIED", "observation target differs from the accepted target")
    if observation["step_id"] not in scope["procedure_ids"]:
        raise StoreRejected("PERMISSION_DENIED", "observation step is not in the accepted procedure")
    for rec in evidence:
        if rec["registration_id"] != registration_id or rec["target"] != scope["target"]:
            raise StoreRejected("PERMISSION_DENIED", "evidence does not belong to this job")
    for rec in evidence:
        conn.execute(
            "INSERT OR IGNORE INTO evidence(evidence_id, registration_id, record_json, observed_at) VALUES (?,?,?,?)",
            (rec["evidence_id"], registration_id, json.dumps(rec, ensure_ascii=False, sort_keys=True),
             rec["observed_at"]),
        )
    obs_id = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
    conn.execute(
        "INSERT OR IGNORE INTO observations(observation_id, registration_id, operation_id, verdict, method,"
        " evidence_refs_json, observed_at) VALUES (?,?,?,?,?,?,?)",
        (obs_id, registration_id, observation["operation_id"], observation["verdict"], observation["method"],
         json.dumps({"observation": observation}, ensure_ascii=False, sort_keys=True), observation["observed_at"]),
    )
    key = effect_key(scope["target"], observation["step_id"])
    effect = conn.execute(
        "SELECT status FROM effects WHERE effect_key=? AND registration_id=?", (key, registration_id)
    ).fetchone()
    if effect is not None and observation["verdict"] in _REFINE[effect["status"]]:
        conn.execute("UPDATE effects SET status=?, resolved_at=? WHERE effect_key=?",
                     (observation["verdict"], now, key))


def record_goal_evidence(conn: sqlite3.Connection, registration_id: str, lease: str | None, record: dict) -> None:
    """Goal readback evidence (RT-04). Allowed while running (lease) or as late read-only evidence."""
    job = _job_or_raise(conn, registration_id)
    terminal = job["state"] in ("done", "stopped")
    if not terminal and (job["worker_lease"] is None or job["worker_lease"] != lease):
        raise StoreRejected("PERMISSION_DENIED", "stale or foreign worker lease")
    scope = json.loads(job["accepted_scope_json"])["scope"]
    if record["registration_id"] != registration_id or record["target"] != scope["target"] or record["kind"] != "goal":
        raise StoreRejected("PERMISSION_DENIED", "goal evidence does not belong to this job")
    conn.execute(
        "INSERT OR IGNORE INTO evidence(evidence_id, registration_id, record_json, observed_at) VALUES (?,?,?,?)",
        (record["evidence_id"], registration_id, json.dumps(record, ensure_ascii=False, sort_keys=True),
         record["observed_at"]),
    )


# ---------- S-FENCE ----------
def fence(conn: sqlite3.Connection, registration_id: str, now: str) -> bool:
    """active -> stopping; unproven reserved effects become unknown. Returns True if it changed state."""
    job = _job_or_raise(conn, registration_id)
    if job["state"] != "active":
        return False
    conn.execute("UPDATE jobs SET state='stopping', updated_at=? WHERE registration_id=?", (now, registration_id))
    conn.execute("UPDATE effects SET status='unknown' WHERE registration_id=? AND status='reserved'",
                 (registration_id,))
    _bump(conn, registration_id, "stopping", now)
    return True


def unresolved_effects(conn: sqlite3.Connection, registration_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM effects WHERE registration_id=? AND status IN ('reserved','unknown') ORDER BY admitted_at",
        (registration_id,),
    ).fetchall()


def finalize(conn: sqlite3.Connection, registration_id: str, result: dict, now: str) -> str:
    """Terminal commit. ``done`` only from active with a confirmed goal and no unresolved effects."""
    job = _job_or_raise(conn, registration_id)
    if job["state"] in ("done", "stopped"):
        raise StoreRejected("INVALID_PHASE", "terminal state is never reopened")
    can_finish = (job["state"] == "active" and result["goal_verdict"] == "confirmed"
                  and not unresolved_effects(conn, registration_id))
    if not can_finish and job["state"] == "active":
        fence(conn, registration_id, now)
    state = "done" if can_finish else "stopped"
    conn.execute(
        "UPDATE jobs SET state=?, result_json=?, worker_lease=NULL, updated_at=? WHERE registration_id=?",
        (state, json.dumps(result, ensure_ascii=False, sort_keys=True), now, registration_id),
    )
    _bump(conn, registration_id, state, now)
    return state


def stored_observations(conn: sqlite3.Connection, registration_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT evidence_refs_json FROM observations WHERE registration_id=? ORDER BY observed_at, observation_id",
        (registration_id,),
    ).fetchall()
    return [json.loads(r["evidence_refs_json"])["observation"] for r in rows]


def stored_evidence(conn: sqlite3.Connection, registration_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT record_json FROM evidence WHERE registration_id=? ORDER BY observed_at, evidence_id",
        (registration_id,),
    ).fetchall()
    return [json.loads(r["record_json"]) for r in rows]


def effects_of(conn: sqlite3.Connection, registration_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM effects WHERE registration_id=? ORDER BY admitted_at, effect_key", (registration_id,)
    ).fetchall()


def _bump(conn: sqlite3.Connection, registration_id: str, state: str, now: str) -> None:
    conn.execute(
        "UPDATE registrations SET job_state=?, revision=revision+1, updated_at=? WHERE registration_id=?",
        (state, now, registration_id),
    )
