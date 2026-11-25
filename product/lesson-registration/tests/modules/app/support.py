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


def temp_db(case) -> pathlib.Path:
    """Fresh SQLite file path; the directory is removed when the test case finishes."""
    d = tempfile.TemporaryDirectory(prefix="r03-app-", ignore_cleanup_errors=True)
    case.addCleanup(d.cleanup)
    return pathlib.Path(d.name) / "store.sqlite3"


class FixedClock:
    def __init__(self, value: str = "2026-11-25T00:00:00Z") -> None:
        self.value = value

    def now(self) -> str:
        return self.value


class TickClock:
    """Each call returns the next second, so insertion order is visible in timestamps."""

    def __init__(self, start: int = 0) -> None:
        self.n = start

    def now(self) -> str:
        self.n += 1
        return f"2026-11-25T00:{self.n // 60:02d}:{self.n % 60:02d}Z"


def mock_image() -> bytes:
    return (pathlib.Path(dev.ROOT) / "fixtures" / "shared" / "mock-image.png").read_bytes()


class ReplayPrep:
    def __init__(self, platform: str, case: str = "I2") -> None:
        self.platform = platform
        self.case = case
        self.calls: list[dict] = []

    def prepare(self, inp: dict) -> dict:
        self.calls.append(json.loads(json.dumps(inp)))
        return dev.replay(self.platform, self.case, inp)


class SchemaPrep:
    """I2 fake for flow tests: validates PrepareInput shape and returns a pinned replay Preparation.

    Returns the ``I2`` (ready) output once every field in ``needs`` has a ResolvedAnswer,
    otherwise the ``I2-missing`` output. ``fail`` makes the next call raise.
    """

    def __init__(self, platform: str, needs: tuple[str, ...] = ()) -> None:
        self.platform = platform
        self.needs = needs
        self.calls: list[dict] = []
        self.fail: BaseException | None = None
        self.override: dict | None = None

    def prepare(self, inp: dict) -> dict:
        from lesson_registration.app import contract

        contract.validate("PrepareInput", inp)
        self.calls.append(json.loads(json.dumps(inp)))
        if self.fail is not None:
            err, self.fail = self.fail, None
            raise err
        if self.override is not None:
            return json.loads(json.dumps(self.override))
        answered = {a["field"] for a in inp["answers"]}
        case = "I2" if all(n in answered for n in self.needs) else "I2-missing"
        return json.loads(json.dumps(replay_cases(self.platform)[case]["output"]))


class FakeRuntime:
    """I3 fake with a small session model: open -> human(g), finish -> verified, refresh -> human(g+1), close.

    Knobs: ``target_status`` (new/existing/ambiguous), ``account_ref`` (mismatch when it differs
    from the target's account), ``fail_next`` (exception raised on the next call), ``slot``.
    """

    def __init__(self, platform: str) -> None:
        self.platform = platform
        self.object_kind = {"kmong": "service_listing", "soomgo": "service_configuration"}[platform]
        self.generation = 0
        self.target_status = "new"
        self.account_ref: str | None = None
        self.slot = f"mock-slot-{platform}"
        self.fail_next: BaseException | None = None
        self.calls: list[dict] = []
        self.runs: list[object] = []

    def authenticate(self, inp: dict) -> dict:
        from lesson_registration.app import contract

        contract.validate("AuthInput", inp)
        self.calls.append(json.loads(json.dumps(inp)))
        if self.fail_next is not None:
            err, self.fail_next = self.fail_next, None
            raise err
        action = inp["command"]["action"]
        if action in ("open", "refresh"):
            self.generation += 1
            g = self.generation
            return {"auth": {"state": "human", "generation": g},
                    "grant": {"generation": g, "viewer_grant": f"grant-{g}", "expires_at": "2027-01-01T00:00:00Z"}}
        if action == "close":
            return {"auth": {"state": "closed"}}
        account = f"mock-account-{self.platform}"
        return {
            "auth": {"state": "verified", "generation": self.generation, "account_label": "합성 계정"},
            "target": {
                "identity": {"environment": "mock", "platform": self.platform, "external_account_ref": account,
                             "object_kind": self.object_kind, "slot_ref": self.slot},
                "status": self.target_status, "evidence_ref": "synthetic-target-proof", "account_label": "합성 계정",
            },
            "connection": {"connection_ref": f"conn-{self.generation}", "verified_generation": self.generation,
                           "account_ref": self.account_ref or account},
        }

    def execute(self, inp: dict) -> dict:
        if not self.runs:
            raise AssertionError("FakeRuntime: no scripted execution")
        item = self.runs.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item(inp) if callable(item) else item  # type: ignore[operator,return-value]


class GatewayRuntime(FakeRuntime):
    """I3 from FakeRuntime + an I4 that really goes through StoreGateway (admit -> act -> observe).

    Knobs: ``crash`` = (step_id, "before_admit"|"after_admit") raises ConnectionError there;
    ``goal`` = "ok" | "none" | "bad_payload" | "bad_assets"; ``report_error`` = Error dict;
    ``on_step`` = callable(step_id) hook (e.g. to fence mid-run).
    """

    def __init__(self, platform: str) -> None:
        super().__init__(platform)
        self.gateway = None
        self.crash: tuple[str, str] | None = None
        self.goal = "ok"
        self.report_error: dict | None = None
        self.on_step = None
        self.executions = 0
        self.ctx: dict | None = None

    def execute(self, inp: dict) -> dict:
        from lesson_registration.app import contract
        from lesson_registration.app.result import payload_digest

        contract.validate("ExecuteInput", inp)
        self.executions += 1
        scope = inp["accepted"]["scope"]
        rid = scope["registration_id"]
        ctx = self.gateway.acquire_context(rid)
        self.ctx = ctx
        observations = []
        now = "2026-11-25T01:00:00Z"
        for op in self.gateway.expected_operations(ctx):
            step = op["step_id"]
            if self.on_step is not None:
                self.on_step(step)
            if self.crash == (step, "before_admit"):
                raise ConnectionError("lost before admit")
            self.gateway.admit(ctx, op)
            if self.crash == (step, "after_admit"):
                raise ConnectionError("lost after admit")
            ev = {"evidence_id": f"ev-{rid}-{step}", "registration_id": rid, "target": scope["target"],
                  "kind": "operation", "method": "runtime_observation", "observed_at": now,
                  "environment": "mock", "operation_id": op["operation_id"]}
            obs = {"operation_id": op["operation_id"], "step_id": step, "target": scope["target"],
                   "method": "runtime_observation", "verdict": "confirmed", "evidence_refs": [ev["evidence_id"]],
                   "observed_at": now}
            self.gateway.record_observation(ctx, obs, [ev])
            observations.append(obs)
        report: dict = {"observations": observations}
        if self.goal != "none":
            profile_goal = self.gateway.knowledge.get_profile(scope["profile_ref"])["goal"]
            pd = payload_digest(scope["values"]) if self.goal != "bad_payload" else "c" * 64
            assets = [a["digest"] for a in scope["assets"]] if self.goal != "bad_assets" else []
            goal = {"goal_kind": profile_goal["kind"], "target": scope["target"], "method": "independent_readback",
                    "observed_state": profile_goal["observed_state"], "payload_digest": pd,
                    "external_ref": f"receipt-{rid}", "asset_digests": assets, "evidence_ref": f"goal-{rid}",
                    "observed_at": now, "environment": "mock"}
            # Goal readback evidence travels with the final read-step observation (GatewayStore.record_observation).
            self.gateway.record_observation(ctx, observations[-1], [{
                "evidence_id": goal["evidence_ref"], "registration_id": rid, "target": scope["target"],
                "kind": "goal", "method": "independent_readback", "observed_at": now, "environment": "mock",
                "observed_state": goal["observed_state"], "payload_digest": pd, "asset_digests": assets,
                "external_ref": goal["external_ref"]}])
            report["goal_observation"] = goal
        if self.report_error is not None:
            report["error"] = self.report_error
        return report


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
