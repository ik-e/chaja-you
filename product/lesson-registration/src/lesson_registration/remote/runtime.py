"""EXEC provider: I3 (authenticate) and I4 (execute) over isolated remote browser sessions.

- I3 open/refresh/finish/close follow H6: open -> human(g) with a short-lived viewer grant;
  refresh rotates the grant (g+1, old grant invalid, same browser connection); finish fences
  human input, then verifies account, target and connection; close/timeout discards the
  connection and binding. Viewer disconnect is not a close.
- I4 reuses exactly the verified connection (same BrowserContext the human signed into),
  takes the exclusive lease, and drives the platform driver through BoundGateway only.
- Each registration gets its own BrowserContext; nothing is shared across sessions.
Mock environment only; no real platform login, credential storage or credential handling here:
the human types into the remote page through the viewer and the runtime never reads those values.
"""
from __future__ import annotations

import copy
import asyncio
import hashlib
import secrets
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from contracts.interfaces import PortFailure

from .bindings import PlatformBinding
from .browser import BrowserHost
from .gateway import BoundGateway, ExecutionGateway
from .page import BrowserScopedPage, origin_of
from .viewer import ViewerConnection

PRESTART = ("human", "verifying", "verified")


def _err(code: str, message: str) -> PortFailure:
    return PortFailure({"code": code, "message": message})


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class UtcClock:
    def now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_validate(name: str, value: dict) -> None:
    from lesson_registration.app import contract   # pinned schema loader (shared jsonschema catalog)
    contract.validate(name, value)


@dataclass(eq=False)
class RemoteSession:
    registration_id: str
    owner_ref: str
    binding: PlatformBinding
    generation: int
    state: str = "human"
    grant_hash: str | None = None
    grant_expires_at: float = 0.0
    grant_attached: bool = False
    input_lock: Any = None
    context: Any = None
    page_handle: Any = None
    cdp: Any = None
    scoped_page: Any = None
    identity: dict | None = None
    account_label: str | None = None
    connection_ref: str | None = None
    lease: str | None = None
    viewers: set = field(default_factory=set)
    audit: list = field(default_factory=list)
    last_frame: dict | None = None
    binding_timeout_ms: int = 15000
    last_activity: float = field(default_factory=time.monotonic)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def touch(self) -> None:
        self.last_activity = time.monotonic()

    def acquire_lease(self) -> bool:
        with self._lock:
            if self.lease is not None or self.state != "verified":
                return False
            self.lease, self.state = secrets.token_hex(8), "running"
            return True

    def release_lease(self) -> None:
        with self._lock:
            self.lease = None
            if self.state == "running":
                self.state = "verified"

    def broadcast(self, message: dict) -> None:
        for v in list(self.viewers):
            v.send(message)


class RemoteRuntime:
    """contracts.interfaces.ExecutionPort provider (I3, I4) plus the viewer attach point."""

    def __init__(self, bindings: list[PlatformBinding], store, *, host: BrowserHost | None = None,
                 clock=None, grant_ttl_sec: int = 600, idle_ttl_sec: int = 900,
                 validate: Callable[[str, dict], None] | None = None, slot_resolver=None,
                 late_read_authorizer=None):
        self.bindings = {b.profile_id: b for b in bindings}
        self.store = store
        self._own_host = host is None
        self.host = host or BrowserHost()
        self.clock = clock or UtcClock()
        self.grant_ttl_sec, self.idle_ttl_sec = grant_ttl_sec, idle_ttl_sec
        self.validate = validate or _default_validate
        self.slot_resolver = slot_resolver
        self.late_read_authorizer = late_read_authorizer
        self.sessions: dict[str, RemoteSession] = {}
        self.generations: dict[str, int] = {}
        self.gateway = ExecutionGateway(self, store)
        self._lock = threading.RLock()
        self.last_open_error: str | None = None

    # ================= I3 =================
    def authenticate(self, request: dict) -> dict:
        self.validate("AuthInput", request)
        rid, owner, cmd = request["registration_id"], request["owner_ref"], request["command"]
        ref = request["profile_ref"]
        binding = self.bindings.get(f"{ref['platform']}.{ref['object_kind']}.{ref['version']}")
        if binding is None or ref["environment"] != "mock":
            raise _err("PERMISSION_DENIED", "no mock runtime binding for this profile")
        with self._lock:
            self.reap()
            s = self.sessions.get(rid)
            if s is not None and s.owner_ref != owner:
                raise _err("PERMISSION_DENIED", "session belongs to another owner")
            action = cmd["action"]
            if action == "open":
                out = self._open(rid, owner, binding, s)
            else:
                if s is None or s.state not in PRESTART:
                    raise _err("AUTH_REQUIRED", "no open authentication session")
                if cmd["generation"] != s.generation:
                    raise _err("CONNECTION_MISMATCH", "stale authentication generation")
                out = getattr(self, "_" + action)(s, binding)
        self.validate("AuthOutput", out)
        return out

    def _open(self, rid, owner, binding, existing):
        if existing is not None and existing.state in PRESTART + ("running",):
            raise _err("PERMISSION_DENIED", "authentication session already open")
        g = self.generations.get(rid, 0) + 1
        self.generations[rid] = g
        s = RemoteSession(rid, owner, binding, g)
        try:
            self.host.run(self._start_browser(s))
        except Exception as e:
            s.audit.append({"event": "open_failed", "error": type(e).__name__, "at": self.clock.now()})
            self.last_open_error = f"{type(e).__name__}: {str(e)[:300]}"
            self._discard(s)
            raise _err("RUNTIME_ERROR", "remote browser could not open the platform entry page") from None
        self.sessions[rid] = s
        grant = self._issue_grant(s)
        s.audit.append({"event": "open", "generation": g, "at": self.clock.now()})
        return {"auth": {"state": "human", "generation": g}, "grant": grant}

    def _refresh(self, s, binding):
        if s.state != "human":
            raise _err("AUTH_REQUIRED", "refresh is only possible while the human is signing in")
        self.generations[s.registration_id] = s.generation = s.generation + 1
        old = list(s.viewers)
        grant = self._issue_grant(s)
        for v in old:                       # previous grant is invalid: detach its viewers
            v.send({"t": "status", "state": "grant_rotated"})
            v.dispose()
        s.audit.append({"event": "refresh", "generation": s.generation, "at": self.clock.now()})
        return {"auth": {"state": "human", "generation": s.generation}, "grant": grant}

    def _finish(self, s, binding):
        if s.state != "human":
            raise _err("AUTH_REQUIRED", "finish is only possible from human")
        s.state = "verifying"                       # fence human input first
        s.grant_hash = None
        s.broadcast({"t": "status", "state": "verifying"})
        try:
            self.host.run(self._drain_input(s))
            try:   # let an in-flight human navigation (sign-in redirect) settle before reading
                self.host.run(s.page_handle.wait_for_load_state("networkidle", timeout=5000))
            except Exception:
                pass
            ident = binding.identify(s.scoped_page)
            if ident is None:
                raise _err("AUTH_REQUIRED", "platform page is not signed in")
            identity = {"environment": "mock", "platform": binding.profile_id.split(".")[0],
                        "external_account_ref": ident.account_ref,
                        "object_kind": binding.profile_id.split(".")[1],
                        "slot_ref": (self.slot_resolver(s.registration_id, s.owner_ref, binding.profile_id)
                                     if self.slot_resolver else binding.slot_for(s.registration_id))}
            status, _note = binding.resolve_target(s.scoped_page, identity)
            if status not in ("new", "existing", "ambiguous"):
                raise _err("RUNTIME_ERROR", "target status not resolved")
        except PortFailure:
            self._close(s, binding)
            raise
        except Exception:
            self._close(s, binding)
            raise _err("RUNTIME_ERROR", "verification failed; session closed") from None
        s.identity, s.account_label = identity, ident.account_label
        s.connection_ref = "conn-" + secrets.token_hex(12)
        s.state = "verified"
        s.touch()
        s.broadcast({"t": "status", "state": "verified"})
        s.audit.append({"event": "verified", "generation": s.generation, "at": self.clock.now()})
        return {"auth": {"state": "verified", "generation": s.generation, "account_label": ident.account_label},
                "target": {"identity": copy.deepcopy(identity), "status": status,
                           "evidence_ref": "target-" + secrets.token_hex(8), "account_label": ident.account_label},
                "connection": {"connection_ref": s.connection_ref, "verified_generation": s.generation,
                               "account_ref": ident.account_ref}}

    def _close(self, s, binding=None):
        s.state = "closed"
        s.grant_hash = None
        s.identity = s.connection_ref = None
        s.broadcast({"t": "status", "state": "closed"})
        for v in list(s.viewers):
            v.dispose()
        self._discard(s)
        s.audit.append({"event": "closed", "at": self.clock.now()})
        return {"auth": {"state": "closed"}}

    # ================= I4 =================
    def execute(self, request: dict) -> dict:
        self.validate("ExecuteInput", request)
        accepted = request["accepted"]
        ctx = self.gateway.with_verified_connection(accepted)
        s = ctx.session
        s.broadcast({"t": "status", "state": "running"})
        bound = BoundGateway(self.gateway, ctx)
        try:
            driver = s.binding.driver
            if hasattr(driver, "run"):
                report = driver.run(bound)
            else:
                report = _default_run(bound)
            out = {"observations": copy.deepcopy(ctx.recorded)}
            goal = report.get("goal_observation")
            error = ctx.error or report.get("error")
            if (error and error.get("code") == "EFFECT_UNKNOWN" and goal is None
                    and self.late_read_authorizer is not None):
                try:                       # RT-04 late read: resolve unknown without any new effect
                    goal = self.gateway.observe_goal(ctx)
                    out["observations"] = copy.deepcopy(ctx.recorded)
                except PortFailure:
                    goal = None
            if goal is not None:
                out["goal_observation"] = goal
            if error:
                out["error"] = error
            self.validate("ExecutionReport", out)
            return out
        finally:
            s.audit.append({"event": "execution_end", "at": self.clock.now()})
            with self._lock:
                self._close(s)
                self.sessions.pop(s.registration_id, None)

    # ================= viewer =================
    def attach_viewer(self, viewer_grant: str, owner_ref: str, sink, *, generation=None) -> ViewerConnection:
        gh = _hash(viewer_grant) if isinstance(viewer_grant, str) else ""
        with self._lock:
            s = next((x for x in self.sessions.values() if x.grant_hash and secrets.compare_digest(x.grant_hash, gh)), None)
            if s is None or s.state != "human" or s.grant_expires_at <= time.monotonic():
                raise _err("PERMISSION_DENIED", "viewer grant is invalid or expired")
            if s.owner_ref != owner_ref:
                raise _err("PERMISSION_DENIED", "viewer grant belongs to another owner")
            if s.grant_attached or (generation is not None and generation != s.generation):
                raise _err("PERMISSION_DENIED", "viewer grant already used or stale")
            s.grant_attached = True
            conn = ViewerConnection(self, s, gh, sink)
            s.viewers.add(conn)
            s.touch()
            s.audit.append({"event": "viewer_attached", "generation": s.generation, "at": self.clock.now()})
        conn.send({"t": "status", "state": s.state, "generation": s.generation})
        if s.last_frame:
            conn.send(s.last_frame)
        return conn

    # ================= housekeeping =================
    def reap(self) -> list[str]:
        """Close prestart sessions idle beyond TTL (timeout = close, no verified binding kept)."""
        closed = []
        with self._lock:
            now = time.monotonic()
            for rid, s in list(self.sessions.items()):
                if s.state in PRESTART and now - s.last_activity > self.idle_ttl_sec:
                    self._close(s)
                    self.sessions.pop(rid, None)
                    closed.append(rid)
        return closed

    def close(self) -> None:
        with self._lock:
            for s in list(self.sessions.values()):
                self._close(s)
            self.sessions.clear()
        if self._own_host:
            self.host.close()

    # ================= browser plumbing =================
    async def _drain_input(self, session):
        async with session.input_lock:
            pass

    def _issue_grant(self, s: RemoteSession) -> dict:
        token = secrets.token_urlsafe(32)
        s.grant_hash = _hash(token)
        s.grant_attached = False
        s.grant_expires_at = time.monotonic() + self.grant_ttl_sec
        expires = (datetime.now(timezone.utc) + timedelta(seconds=self.grant_ttl_sec)).strftime("%Y-%m-%dT%H:%M:%SZ")
        s.touch()
        return {"generation": s.generation, "viewer_grant": token, "expires_at": expires}

    async def _start_browser(self, s: RemoteSession) -> None:
        s.input_lock = asyncio.Lock()
        b = s.binding
        s.context = await self.host.new_context(viewport=b.viewport, accept_downloads=False)
        origin = origin_of(b.origin)

        async def guard(route):
            try:
                await _guard(route)
            except Exception:
                pass   # context/page already closed while a request was in flight

        async def _guard(route):
            req = route.request
            if origin_of(req.url) != origin:
                await route.abort()                       # no other origin, ever
                return
            if req.method in ("GET", "HEAD"):
                await route.continue_()
                return
            # State-changing requests go out exactly once. Chromium's network stack silently
            # re-sends a POST whose connection closed without a response (observed: one click,
            # two submissions). A single-attempt fetch without redirects keeps a lost response
            # unknown instead of duplicating the effect; the browser still follows the redirect.
            try:
                resp = await route.fetch(max_redirects=0, max_retries=0, timeout=s.binding_timeout_ms)
            except Exception:
                s.audit.append({"event": "request_unanswered", "method": req.method, "at": self.clock.now()})
                await route.abort("failed")
                return
            await route.fulfill(response=resp)
        await s.context.route("**/*", guard)
        s.page_handle = await s.context.new_page()
        s.scoped_page = BrowserScopedPage(self.host, s.page_handle, origin, unknown_exc=b.unknown_exc,
                                          structure_exc=b.structure_exc, view_factory=b.view_factory)
        await s.page_handle.goto(origin + b.entry_path, wait_until="load")
        s.cdp = await s.context.new_cdp_session(s.page_handle)

        async def on_frame(params):
            try:
                await s.cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
            except Exception:
                return
            meta = params.get("metadata", {})
            frame = {"t": "frame", "data": params["data"], "w": meta.get("deviceWidth"), "h": meta.get("deviceHeight")}
            s.last_frame = frame
            s.broadcast(frame)
        s.cdp.on("Page.screencastFrame", lambda p: self.host.loop.create_task(on_frame(p)))
        await s.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 60,
                                                   "maxWidth": b.viewport["width"], "maxHeight": b.viewport["height"]})

    def _discard(self, s: RemoteSession) -> None:
        ctx, s.context = s.context, None
        s.page_handle = s.cdp = s.scoped_page = None
        if ctx is not None:
            try:
                self.host.run(ctx.close(), timeout=15)
            except Exception:
                pass


def _default_run(bound) -> dict:
    report: dict = {"observations": []}
    try:
        for op in bound.list_operations():
            report["observations"].append(bound.perform(op))
        report["goal_observation"] = bound.observe_goal()
    except PortFailure as e:
        report["error"] = e.error
    return report
