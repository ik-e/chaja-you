"""RT-01..RT-04 runtime gateway over the R03 GatewayStore (S-ADMIT / S-OBSERVE / S-FENCE).

The runtime owns the opaque worker context and permit (IB-03). Platform drivers get only a
``BoundGateway`` (list_operations / perform / observe_goal) and a ScopedPage; no store, lease,
permit, raw browser or credential is reachable from them.

Order per operation: exact registry match -> STORE admit (durable) -> driver acts -> STORE
record_observation. Any error or unknown effect requests S-FENCE; nothing is retried.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from contracts.interfaces import PortFailure


def _error(code: str, message: str) -> dict:
    return {"code": code, "message": message[:500]}


def _store_failure(exc: Exception) -> dict:
    code = getattr(exc, "code", None)
    return _error(code if isinstance(code, str) else "RUNTIME_ERROR", "STORE rejected: " + str(getattr(exc, "message", "")))


@dataclass
class ExecContext:
    """Opaque to drivers. Holds the STORE worker context, never handed out."""
    registration_id: str
    accepted: dict
    session: Any
    store_ctx: Any
    driver_ctx: Any
    ops: list | None = None
    fenced: bool = False
    last_goal: Any = None
    recorded: list = field(default_factory=list)
    error: dict | None = None


class ExecutionGateway:
    """RuntimeGateway (contracts.interfaces) implementation."""

    def __init__(self, runtime, store):
        self._rt = runtime
        self._store = store

    # ---------- RT-01 ----------
    def with_verified_connection(self, accepted: dict) -> ExecContext:
        scope = accepted["scope"]
        rid = scope["registration_id"]
        s = self._rt.sessions.get(rid)
        if s is not None and s.state == "running":
            raise PortFailure(_error("INVALID_PHASE", "session already has a worker"))
        if s is None or s.state != "verified":
            raise PortFailure(_error("AUTH_REQUIRED", "no verified connection for this registration"))
        conn = scope["connection"]
        if (conn["connection_ref"] != s.connection_ref or conn["verified_generation"] != s.generation
                or conn["account_ref"] != s.identity["external_account_ref"]):
            raise PortFailure(_error("CONNECTION_MISMATCH", "accepted connection is not the verified session"))
        if scope["target"] != s.identity or conn["account_ref"] != scope["target"]["external_account_ref"]:
            raise PortFailure(_error("ACCOUNT_MISMATCH", "accepted target differs from the verified identity"))
        ref = scope["profile_ref"]
        if f"{ref['platform']}.{ref['object_kind']}.{ref['version']}" != s.binding.profile_id:
            raise PortFailure(_error("PROFILE_CHANGED", "accepted profile differs from the session binding"))
        if not s.acquire_lease():
            raise PortFailure(_error("INVALID_PHASE", "session already has a worker"))
        try:
            store_ctx = self._store.acquire_context(rid)
        except Exception as e:
            s.release_lease()
            raise PortFailure(_store_failure(e)) from None
        driver_ctx = s.binding.make_context(copy.deepcopy(accepted), s.scoped_page, self._rt.clock.now)
        return ExecContext(rid, copy.deepcopy(accepted), s, store_ctx, driver_ctx)

    # ---------- RT-02 ----------
    def list_operations(self, ctx: ExecContext) -> list[dict]:
        if ctx.ops is None:
            mine = ctx.session.binding.driver.operations(ctx.accepted)
            theirs = self._store.expected_operations(ctx.store_ctx) if hasattr(self._store, "expected_operations") else mine
            if mine != theirs:
                self._fence(ctx, _error("PROFILE_CHANGED", "driver operation registry differs from STORE"))
                raise PortFailure(ctx.error)
            ctx.ops = copy.deepcopy(mine)
        return copy.deepcopy(ctx.ops)

    # ---------- RT-03 ----------
    def perform(self, ctx: ExecContext, operation: dict) -> dict:
        if ctx.fenced:
            raise PortFailure(_error("INVALID_PHASE", "execution is fenced; no new operations"))
        if operation not in self.list_operations(ctx):
            self._fence(ctx, _error("INVALID_REQUEST", "operation is not registered for this accepted scope"))
            raise PortFailure(ctx.error)
        try:
            self._store.admit(ctx.store_ctx, copy.deepcopy(operation))   # durable before any browser command
        except Exception as e:
            self._fence(ctx, _store_failure(e))
            raise PortFailure(ctx.error) from None
        driver = ctx.session.binding.driver
        try:
            outcome = driver.perform(ctx.driver_ctx, copy.deepcopy(operation))
        except Exception as e:
            err, obs, evidence = self._driver_failure(ctx, operation, e)
            if obs is not None:
                self._record(ctx, obs, evidence)
            self._fence(ctx, err)
            raise PortFailure(err) from None
        self._record(ctx, outcome.observation, outcome.evidence)
        goal = getattr(outcome, "goal", None)
        if goal is not None:
            ctx.last_goal = goal
        return copy.deepcopy(outcome.observation)

    # ---------- RT-04 ----------
    def observe_goal(self, ctx: ExecContext) -> dict:
        goal = ctx.last_goal
        if goal is None or goal.verdict != "confirmed":
            try:
                goal = ctx.session.binding.driver.observe_goal(ctx.driver_ctx)   # read-only, no admission
            except Exception:
                raise PortFailure(_error("EVIDENCE_INSUFFICIENT", "goal readback was not observed")) from None
            if getattr(goal, "observation", None) is not None:
                self._record(ctx, goal.observation, getattr(goal, "evidence", []))
            ctx.last_goal = goal
        if goal.verdict != "confirmed" or not goal.goal_observation:
            raise PortFailure(_error("EVIDENCE_INSUFFICIENT", f"goal {goal.verdict}"))
        return copy.deepcopy(goal.goal_observation)

    # ---------- helpers ----------
    def _record(self, ctx, observation, evidence):
        try:
            self._store.record_observation(ctx.store_ctx, copy.deepcopy(observation), copy.deepcopy(list(evidence)))
        except Exception as e:
            self._fence(ctx, _store_failure(e))
            raise PortFailure(ctx.error) from None
        ctx.recorded.append(copy.deepcopy(observation))

    def _fence(self, ctx, error):
        if ctx.error is None:
            ctx.error = error
        if not ctx.fenced:
            ctx.fenced = True
            try:
                self._store.fence(ctx.registration_id, error)
            except Exception:
                pass   # CO also fences on the returned error; never retry an effect here

    def _driver_failure(self, ctx, operation, exc):
        to_error = getattr(exc, "to_error", None)
        err = to_error() if callable(to_error) else _error("RUNTIME_ERROR", f"driver failed: {type(exc).__name__}")
        obs = getattr(exc, "observation", None)
        evidence = list(getattr(exc, "evidence", []) or [])
        if obs is None:
            verdict = "unknown" if operation["effect_class"] == "potential_effect" else "absent"
            if verdict == "unknown":
                err = _error("EFFECT_UNKNOWN", f"driver stopped without an observation: {err['code']}")
            obs = {"operation_id": operation["operation_id"], "step_id": operation["step_id"],
                   "target": copy.deepcopy(ctx.accepted["scope"]["target"]), "method": "runtime_observation",
                   "verdict": verdict, "evidence_refs": [], "observed_at": self._rt.clock.now()}
        return err, obs, evidence


class BoundGateway:
    """contracts.interfaces.BoundGateway: the only gateway surface a platform driver sees."""

    __slots__ = ("_list", "_perform", "_goal")

    def __init__(self, gateway: ExecutionGateway, ctx: ExecContext):
        self._list = lambda: gateway.list_operations(ctx)
        self._perform = lambda op: gateway.perform(ctx, op)
        self._goal = lambda: gateway.observe_goal(ctx)

    def list_operations(self) -> list[dict]:
        return self._list()

    def perform(self, operation: dict) -> dict:
        return self._perform(operation)

    def observe_goal(self) -> dict:
        return self._goal()
