"""Port types come from the shared contract (contracts/interfaces.py); no local Protocol copies.

Only the app-local Clock lives here.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from contracts.interfaces import ExecutionPort, PortFailure, PreparationPort, Providers, Registry, ResultPort

from .ids import utc_now

__all__ = ["Clock", "ExecutionPort", "PortFailure", "PreparationPort", "Providers", "Registry", "ResultPort",
           "SystemClock"]


@runtime_checkable
class Clock(Protocol):
    def now(self) -> str: ...


class SystemClock:
    def now(self) -> str:
        return utc_now()
