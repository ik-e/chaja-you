"""contracts.interfaces.CoordinatorStore over SQLite: S-ACCEPT, S-FENCE, finalize.

``accept`` re-checks every guard against the freshly locked registration row, so a
change between the coordinator's pre-checks and the write can never be accepted.
"""

from __future__ import annotations

from collections.abc import Callable

from ..errors import AppError
from ..ids import digest
from ..ports import Clock
from . import atomic, repo
from .db import Store, tx


def request_digest(registration_id: str, start: dict) -> str:
    """Canonical start request incl. path id (contract state.revision)."""
    return digest({"path_id": registration_id, **start})


class SqliteCoordinatorStore:
    def __init__(self, store: Store, clock: Clock, view: Callable[[dict], dict]) -> None:
        self.store = store
        self.clock = clock
        self.view = view

    # CoordinatorStore.accept
    def accept(self, owner: str, registration_id: str, start: dict, scope: dict) -> dict:
        return self.accept_with_status(owner, registration_id, start, scope)[1]

    def accept_with_status(self, owner: str, registration_id: str, start: dict, scope: dict) -> tuple[bool, dict]:
        """Returns (replayed, RegistrationView). Exact-key replay is checked before any guard."""
        key_digest = request_digest(registration_id, start)
        now = self.clock.now()
        with self.store.connect() as conn, tx(conn):
            reg = repo.get_registration(conn, owner, registration_id)
            if reg is None:
                raise AppError("NOT_FOUND", "registration not found")
            prior = atomic.find_job_by_key(conn, owner, start["request_key"])
            if prior is not None:
                if prior["request_digest"] == key_digest:
                    return True, self.view(reg)
                raise AppError("IDEMPOTENCY_CONFLICT", "request_key reused with a different request",
                               current_revision=reg["revision"])
            cur = reg["revision"]
            if reg["job_state"] is not None or atomic.find_job(conn, registration_id) is not None:
                raise AppError("IDEMPOTENCY_CONFLICT", "registration already accepted under another key",
                               current_revision=cur)
            if start["expected_revision"] != cur or scope["revision"] != cur:
                raise AppError("STALE_REVISION", "registration changed", current_revision=cur)
            if reg["auth"]["state"] != "verified" or reg.get("connection") != scope["connection"]:
                raise AppError("AUTH_REQUIRED", "verified authentication required", current_revision=cur)
            trusted = reg["target"]["trusted"]
            if trusted["identity"] != scope["target"]:
                raise AppError("CONNECTION_MISMATCH", "target changed", current_revision=cur)
            if trusted["status"] == "ambiguous":
                raise AppError("TARGET_AMBIGUOUS", "target could not be identified safely", current_revision=cur)
            if trusted["status"] == "existing":
                raise AppError("DUPLICATE_RISK", "target already exists", current_revision=cur)
            review = reg.get("review")
            if review is None or not reg["preparation"]["ready"]:
                raise AppError("INVALID_PHASE", "registration is not ready for approval", current_revision=cur)
            if start["review_digest"] != review["digest"] or digest(scope) != review["digest"]:
                raise AppError("APPROVAL_INVALID", "approved review is not the current review", current_revision=cur)
            if atomic.blocking_jobs_for_target(conn, scope["target"], registration_id):
                raise AppError("DUPLICATE_RISK", "another registration has an unresolved or confirmed effect "
                               "on this target", current_revision=cur)
            accepted = {"scope": scope, "review_digest": review["digest"], "accepted_at": now,
                        "owner_ref": owner, "request_key": start["request_key"]}
            atomic.accept(conn, owner, registration_id, start["request_key"], key_digest, accepted, cur + 1, now)
            stored = repo.get_registration(conn, owner, registration_id)
        return False, self.view(stored)

    # CoordinatorStore.fence
    def fence(self, registration_id: str, error: dict) -> None:
        with self.store.connect() as conn, tx(conn):
            try:
                atomic.fence_existing(conn, registration_id, self.clock.now())
            except atomic.StoreRejected as exc:
                raise AppError(exc.code, exc.message) from None

    # CoordinatorStore.finalize -> "done" | "stopped"; a terminal state is returned unchanged, never reopened.
    def finalize(self, registration_id: str, result: dict) -> str:
        with self.store.connect() as conn, tx(conn):
            job = atomic.find_job(conn, registration_id)
            if job is None:
                raise AppError("NOT_FOUND", "no accepted job")
            if job["state"] in ("done", "stopped"):
                return job["state"]
            return atomic.finalize(conn, registration_id, result, self.clock.now())
