"""Injection points for modules owned by other packages.

I2 (PREP, r02-preparation) and I3/I4 (EXEC, r05-remote) are consumed here only
through these protocols. Payloads are plain dicts shaped by data-schema-v4.1
``$defs``; the coordinator validates every return value before use.
Synchronous calls are the starting assumption (SPEC §10).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .ids import utc_now


@runtime_checkable
class PrepPort(Protocol):
    def prepare(self, inp: dict) -> dict:
        """I2: PrepareInput -> Preparation."""
        ...


@runtime_checkable
class ExecPort(Protocol):
    def authenticate(self, inp: dict) -> dict:
        """I3: AuthInput -> AuthOutput."""
        ...

    def execute(self, inp: dict) -> dict:
        """I4: ExecuteInput -> ExecutionReport."""
        ...


@runtime_checkable
class Clock(Protocol):
    def now(self) -> str: ...


class SystemClock:
    def now(self) -> str:
        return utc_now()
