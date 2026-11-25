"""StoreGateway: the STORE surface the EXEC runtime (r05-remote) calls while executing.

The runtime receives this object by injection. It never changes job state
directly: it acquires the exclusive lease, asks for an admission before every
operation, records actual observations/evidence, and may request an error stop
(fence). Exact exposure (direct object vs port/transport) is to be agreed with
R05/R01 (SPEC §10).
"""

from __future__ import annotations

import json

from . import contract
from .errors import AppError
from .ids import digest, new_id
from .knowledge import Knowledge
from .ports import Clock, SystemClock
from .store import Store, tx
from .store import atomic


def binding_digest(scope: dict, step: dict) -> str:
    """Digest over the exact immutable values a step is bound to (proposal; agree with R05)."""
    bound = {k: scope["values"].get(k) for k in step["bindings"]}
    asset_digests = sorted(a["digest"] for a in scope["assets"]) if "main_images" in step["bindings"] else []
    return digest({"step_id": step["step_id"], "bound": bound, "asset_digests": asset_digests,
                   "target": scope["target"], "profile_digest": scope["profile_ref"]["digest"]})


class StoreGateway:
    def __init__(self, store: Store, knowledge: Knowledge | None = None, clock: Clock | None = None) -> None:
        self.store = store
        self.knowledge = knowledge or Knowledge()
        self.clock = clock or SystemClock()

    # RT-01
    def acquire(self, registration_id: str) -> dict:
        lease = new_id("lease")
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.acquire_lease, conn, registration_id, lease, self.clock.now())
        return {"registration_id": registration_id, "lease": lease}

    # RT-02 helper: the operations the accepted scope allows, with their binding digests
    def operations(self, ctx: dict) -> list[dict]:
        scope, profile = self._scope_profile(ctx["registration_id"])
        return [
            {"operation_id": f"{scope['registration_id']}:{s['step_id']}", "step_id": s["step_id"],
             "action_key": s["step_id"], "effect_class": s["effect_class"],
             "binding_digest": binding_digest(scope, s)}
            for s in profile["steps"]
        ]

    # S-ADMIT
    def admit(self, ctx: dict, operation: dict) -> str:
        contract.validate("Operation", operation)
        scope, profile = self._scope_profile(ctx["registration_id"])
        step = next((s for s in profile["steps"] if s["step_id"] == operation["step_id"]), None)
        if step is None:
            raise AppError("PERMISSION_DENIED", "unknown step")
        with self.store.connect() as conn, tx(conn):
            return self._run(atomic.admit, conn, ctx["registration_id"], ctx["lease"], operation,
                             binding_digest(scope, step), step["effect_class"], self.clock.now())

    # S-OBSERVE
    def observe(self, ctx: dict, observation: dict, evidence: list[dict]) -> None:
        contract.validate("Observation", observation)
        for rec in evidence:
            contract.validate("EvidenceRecord", rec)
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.observe, conn, ctx["registration_id"], ctx.get("lease"), observation, evidence,
                      self.clock.now())

    # RT-04 evidence
    def record_goal(self, ctx: dict, record: dict) -> None:
        contract.validate("EvidenceRecord", record)
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.record_goal_evidence, conn, ctx["registration_id"], ctx.get("lease"), record)

    # error stop requested by the runtime
    def fence(self, ctx: dict, error: dict) -> None:
        contract.validate("Error", error)
        with self.store.connect() as conn, tx(conn):
            job = atomic.find_job(conn, ctx["registration_id"])
            if job is None or job["worker_lease"] != ctx["lease"]:
                raise AppError("PERMISSION_DENIED", "stale or foreign worker lease")
            atomic.fence(conn, ctx["registration_id"], self.clock.now())

    def _scope_profile(self, registration_id: str) -> tuple[dict, dict]:
        with self.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
        if job is None:
            raise AppError("NOT_FOUND", "no accepted job")
        scope = json.loads(job["accepted_scope_json"])["scope"]
        return scope, self.knowledge.get(scope["profile_ref"])

    @staticmethod
    def _run(fn, *args):
        try:
            return fn(*args)
        except atomic.StoreRejected as exc:
            raise AppError(exc.code, exc.message) from None
