"""Typed application errors and the HTTP status mapping from common-integration-v1 ``http``."""

from __future__ import annotations

STATUS: dict[str, int] = {
    "INVALID_REQUEST": 400,
    "UNAUTHENTICATED": 401,
    "PERMISSION_DENIED": 403,
    "NOT_FOUND": 404,
    "STALE_REVISION": 409,
    "APPROVAL_INVALID": 409,
    "IDEMPOTENCY_CONFLICT": 409,
    "INVALID_PHASE": 409,
    "ACCOUNT_MISMATCH": 409,
    "CONNECTION_MISMATCH": 409,
    "TARGET_AMBIGUOUS": 409,
    "DUPLICATE_RISK": 409,
    "PROFILE_CHANGED": 409,
    "VALIDATION_FAILED": 422,
    "FACT_CONFLICT": 422,
    "AUTH_REQUIRED": 422,
    "UNSUPPORTED_TARGET": 422,
    "MODEL_UNAVAILABLE": 503,
    "RUNTIME_ERROR": 503,
}

# Codes that only appear inside a persisted Result, never as an HTTP rejection.
RESULT_ONLY: frozenset[str] = frozenset({"EFFECT_UNKNOWN", "EVIDENCE_INSUFFICIENT"})


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        issues: list[dict] | None = None,
        current_revision: int | None = None,
    ) -> None:
        if code not in STATUS and code not in RESULT_ONLY:
            raise ValueError(f"unknown error code {code!r}")
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.issues = issues
        self.current_revision = current_revision

    @property
    def status(self) -> int:
        return STATUS.get(self.code, 500)

    def to_view(self) -> dict:
        """Return the ``Error`` $def shape (safe message only, no internals)."""
        view: dict = {"code": self.code, "message": self.message}
        if self.issues:
            view["issues"] = self.issues
        if self.current_revision is not None:
            view["current_revision"] = self.current_revision
        return view
