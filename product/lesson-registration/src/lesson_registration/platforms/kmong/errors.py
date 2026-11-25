"""Typed adapter error carrying what was actually observed."""
from __future__ import annotations


class KmongError(Exception):
    """``code`` is a data-schema Error code. ``verdict`` describes the operation's effect:
    ``absent`` = no effect happened, ``unknown`` = effect may have happened,
    ``confirmed`` = effect happened but the step cannot continue."""

    def __init__(self, code: str, message: str, verdict: str = "absent", *, issues=None,
                 observation=None, evidence=None, goal=None):
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.verdict = code, message, verdict
        self.issues = list(issues or [])
        self.observation = observation
        self.evidence = list(evidence or [])
        self.goal = goal

    def to_error(self) -> dict:
        out = {"code": self.code, "message": self.message}
        if self.issues:
            out["issues"] = self.issues
        return out
