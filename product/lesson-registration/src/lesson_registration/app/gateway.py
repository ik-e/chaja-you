"""STORE capability for the EXEC runtime (r05-remote): contracts.interfaces.GatewayStore.

IB-03: the runtime owns the opaque context and permit; adapters never see either.
STORE still has to know which worker is current, so the runtime obtains its
context from ``acquire_context`` (inside RT-01 with_verified_connection) and
passes it back unchanged. The runtime never changes job state; it asks for an
admission before each operation, records actual observations/evidence (goal
readback evidence included) and may request an error stop.

Extra helpers beyond the protocol: ``acquire_context`` (lease registration) and
``expected_operations`` (binding digests STORE will accept). Both to be confirmed
with R05 (SPEC §10).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

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


@dataclass(frozen=True)
class WorkerContext:
    """Opaque to adapters; held by the runtime, interpreted only by STORE."""

    registration_id: str
    lease: str


@dataclass(frozen=True)
class Permit:
    """One-shot admission token returned to the runtime (never user-visible)."""

    registration_id: str
    step_id: str
    token: str


class StoreGateway:
    def __init__(self, store: Store, knowledge: Knowledge | None = None, clock: Clock | None = None) -> None:
        self.store = store
        self.knowledge = knowledge or Knowledge()
        self.clock = clock or SystemClock()

    # RT-01 support: register the exclusive worker lease for an accepted active job.
    def acquire_context(self, registration_id: str) -> WorkerContext:
        lease = new_id("lease")
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.acquire_lease, conn, registration_id, lease, self.clock.now())
        return WorkerContext(registration_id, lease)

    # RT-02 support: operations STORE will admit, with their binding digests.
    def expected_operations(self, context: WorkerContext) -> list[dict]:
        scope, profile = self._scope_profile(context.registration_id)
        return [
            {"operation_id": f"{scope['registration_id']}:{s['step_id']}", "step_id": s["step_id"],
             "action_key": s["step_id"], "effect_class": s["effect_class"],
             "binding_digest": binding_digest(scope, s)}
            for s in profile["steps"]
        ]

    # S-ADMIT
    def admit(self, context: WorkerContext, operation: dict) -> Permit:
        contract.validate("Operation", operation)
        scope, profile = self._scope_profile(context.registration_id)
        step = next((s for s in profile["steps"] if s["step_id"] == operation["step_id"]), None)
        if step is None:
            raise AppError("PERMISSION_DENIED", "unknown step")
        with self.store.connect() as conn, tx(conn):
            token = self._run(atomic.admit, conn, context.registration_id, context.lease, operation,
                              binding_digest(scope, step), step["effect_class"], self.clock.now())
        return Permit(context.registration_id, operation["step_id"], token)

    # S-OBSERVE (goal readback evidence is passed here too, with its read-step observation)
    def record_observation(self, context: WorkerContext, observation: dict, evidence: list[dict]) -> dict:
        contract.validate("Observation", observation)
        for rec in evidence:
            contract.validate("EvidenceRecord", rec)
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.observe, conn, context.registration_id, context.lease, observation, evidence,
                      self.clock.now())
        return observation

    # S-FENCE requested by the runtime: stops future effects; CO commits the terminal result.
    def fence(self, registration_id: str, error: dict) -> None:
        contract.validate("Error", error)
        with self.store.connect() as conn, tx(conn):
            self._run(atomic.fence_existing, conn, registration_id, self.clock.now())

    def _scope_profile(self, registration_id: str) -> tuple[dict, dict]:
        with self.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
        if job is None:
            raise AppError("NOT_FOUND", "no accepted job")
        scope = json.loads(job["accepted_scope_json"])["scope"]
        return scope, self.knowledge.get_profile(scope["profile_ref"])

    @staticmethod
    def _run(fn, *args):
        try:
            return fn(*args)
        except atomic.StoreRejected as exc:
            raise AppError(exc.code, exc.message) from None
