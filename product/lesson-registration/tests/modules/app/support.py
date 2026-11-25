"""Shared helpers for r03-app tests (not product code).

ReplayPrep/ReplayExec wrap ``dev.replay`` and therefore answer only the exact
pinned synthetic inputs. ScriptedExec lets a test inject arbitrary responses,
exceptions or callbacks for scenarios the shared replay does not cover
(unknown effects, lost responses, races).
"""

from __future__ import annotations

import json
import pathlib
import tempfile
from collections.abc import Callable

import dev

PLATFORMS = ("kmong", "soomgo")


def replay_cases(platform: str) -> dict:
    return dev.fixtures()[platform]["cases"]


def replay_http(platform: str) -> list[dict]:
    return dev.fixtures()[platform]["http"]


def temp_db() -> pathlib.Path:
    """Return a fresh SQLite file path inside a TemporaryDirectory kept alive by the caller."""
    d = tempfile.mkdtemp(prefix="r03-app-")
    return pathlib.Path(d) / "store.sqlite3"


class FixedClock:
    def __init__(self, value: str = "2026-11-25T00:00:00Z") -> None:
        self.value = value

    def now(self) -> str:
        return self.value


class ReplayPrep:
    def __init__(self, platform: str, case: str = "I2") -> None:
        self.platform = platform
        self.case = case
        self.calls: list[dict] = []

    def prepare(self, inp: dict) -> dict:
        self.calls.append(json.loads(json.dumps(inp)))
        return dev.replay(self.platform, self.case, inp)


class ReplayExec:
    def __init__(self, platform: str) -> None:
        self.platform = platform
        self.calls: list[tuple[str, dict]] = []

    def authenticate(self, inp: dict) -> dict:
        self.calls.append(("I3", inp))
        return dev.replay(self.platform, "I3", inp)

    def execute(self, inp: dict) -> dict:
        self.calls.append(("I4", inp))
        return dev.replay(self.platform, "I4", inp)


class ScriptedExec:
    """Return queued values; a queued Exception is raised, a callable is called with the input."""

    def __init__(self) -> None:
        self.auth: list[object] = []
        self.runs: list[object] = []
        self.calls: list[tuple[str, dict]] = []

    @staticmethod
    def _next(queue: list[object], inp: dict) -> dict:
        if not queue:
            raise AssertionError("ScriptedExec: no scripted response left")
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        if callable(item):
            return item(inp)  # type: ignore[operator]
        return item  # type: ignore[return-value]

    def authenticate(self, inp: dict) -> dict:
        self.calls.append(("I3", inp))
        return self._next(self.auth, inp)

    def execute(self, inp: dict) -> dict:
        self.calls.append(("I4", inp))
        return self._next(self.runs, inp)


Responder = Callable[[dict], dict]
