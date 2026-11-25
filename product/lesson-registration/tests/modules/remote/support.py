"""Test-only helpers for r05-remote: neutral driver bound to the pinned kmong mock profile steps,
viewer client stub, R03 Coordinator/StoreGateway wiring. Not product code."""
from __future__ import annotations

import json
import pathlib
import tempfile
import threading
import time
from dataclasses import dataclass, field

import dev
from contracts.canonical import canonical_bytes, json_digest
from lesson_registration.app.gateway import binding_digest as store_binding_digest
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.remote import Identity, PlatformBinding, UploadFile
from lesson_registration.remote.page import NavigationUnknown, PageStructureError

from neutral_site import LOGIN_POS, NeutralSite  # noqa: F401  (re-export)

ROOT = pathlib.Path(dev.ROOT)
MOCK_IMAGE = (ROOT / "fixtures" / "shared" / "mock-image.png").read_bytes()
PROFILE_ID = "kmong.service_listing.mock.v2"


class DriverError(Exception):
    def __init__(self, code, message, verdict, observation=None, evidence=None):
        super().__init__(code)
        self.code, self.message, self.verdict = code, message, verdict
        self.observation, self.evidence = observation, list(evidence or [])

    def to_error(self):
        return {"code": self.code, "message": self.message}


@dataclass
class Outcome:
    observation: dict
    evidence: list
    goal: object = None


@dataclass
class Readback:
    verdict: str
    goal_observation: dict | None
    observation: dict | None = None
    evidence: list = field(default_factory=list)


class NeutralDriver:
    """Drives the neutral site through ScopedPage for the pinned kmong steps K1..K7 (test stand-in
    for a platform adapter; uses R03's operation/digest rule so STORE admits it)."""

    def __init__(self, assets: dict[str, bytes]):
        self.assets = assets
        self.knowledge = Knowledge()
        self.calls: list[str] = []
        self.rogue: dict | None = None

    def operations(self, accepted):
        scope = accepted["scope"]
        steps = self.knowledge.get_profile(scope["profile_ref"])["steps"]
        return [{"operation_id": f"{scope['registration_id']}:{s['step_id']}", "step_id": s["step_id"],
                 "action_key": s["step_id"], "effect_class": s["effect_class"],
                 "binding_digest": store_binding_digest(scope, s)} for s in steps]

    def run(self, bound):
        from contracts.interfaces import PortFailure
        report = {"observations": []}
        try:
            for op in bound.list_operations():
                if self.rogue and op["step_id"] == self.rogue["before"]:
                    bound.perform(self.rogue["op"])
                report["observations"].append(bound.perform(op))
            report["goal_observation"] = bound.observe_goal()
        except PortFailure as e:
            report["error"] = e.error
        return report

    # ---- helpers ----
    def _obs(self, ctx, op, method, verdict, evidence):
        return {"operation_id": op["operation_id"], "step_id": op["step_id"], "target": ctx["scope"]["target"],
                "method": method, "verdict": verdict, "evidence_refs": [e["evidence_id"] for e in evidence],
                "observed_at": ctx["now"]()}

    def _ev(self, ctx, op, kind, method, **extra):
        ev = {"evidence_id": f"ev-{op['step_id'] if op else 'goal'}-{time.monotonic_ns()}",
              "registration_id": ctx["scope"]["registration_id"], "target": ctx["scope"]["target"], "kind": kind,
              "method": method, "observed_at": ctx["now"](), "environment": "mock"}
        if op:
            ev["operation_id"] = op["operation_id"]
        ev.update(extra)
        return ev

    def perform(self, ctx, op):
        self.calls.append(op["step_id"])
        page, scope = ctx["page"], ctx["scope"]
        step = op["step_id"]
        try:
            if step == "K1":
                page.goto("/work/new")
                page.fill("slot_ref", scope["target"]["slot_ref"])
                v = page.submit("start")
                if v.page != "work" or v.one("slot_ref") != scope["target"]["slot_ref"]:
                    raise DriverError("RUNTIME_ERROR", "work not opened", "unknown")
                ctx["work"] = v.path
            elif step in ("K2", "K3", "K4"):
                page.goto(ctx["work"])
                if step == "K2":
                    page.fill("payload", canonical_bytes(scope["values"]).decode())
                    v = page.submit("save_values")
                    if v.one("payload") != canonical_bytes(scope["values"]).decode():
                        raise DriverError("VALIDATION_FAILED", "saved payload differs", "confirmed")
                elif step == "K3":
                    page.attach("files", [UploadFile(f"{a['asset_id']}.png", a["mime"], self.assets[a["digest"]])
                                          for a in scope["assets"]])
                    v = page.submit("save_files")
                    if v.all("asset_digest") != [a["digest"] for a in scope["assets"]]:
                        raise DriverError("VALIDATION_FAILED", "uploaded digests differ", "confirmed")
                else:
                    page.fill("step", step)
                    page.submit("mark")
            elif step == "K5":
                v = page.goto(ctx["work"])
                if v.one("payload") != canonical_bytes(scope["values"]).decode():
                    raise DriverError("VALIDATION_FAILED", "review differs", "absent")
            elif step == "K6":
                if page.goto("/slots/" + scope["target"]["slot_ref"]).page != "slot_absent":
                    raise DriverError("DUPLICATE_RISK", "slot already has a receipt", "absent")
                page.goto(ctx["work"])
                v = page.submit("submit_work")
                if v.page != "submitted":
                    raise DriverError("EFFECT_UNKNOWN", f"submit outcome {v.status}", "unknown")
                ev = self._ev(ctx, op, "operation", "submission_response", external_ref=v.one("receipt_id"))
                return Outcome(self._obs(ctx, op, "submission_response", "confirmed", [ev]), [ev])
            elif step == "K7":
                rb = self._readback(ctx, op)
                if rb.verdict != "confirmed":
                    raise DriverError("EVIDENCE_INSUFFICIENT", "goal not confirmed", rb.observation["verdict"],
                                      rb.observation, rb.evidence)
                return Outcome(rb.observation, rb.evidence, rb)
        except NavigationUnknown as e:
            verdict = "unknown" if op["effect_class"] == "potential_effect" else "absent"
            raise DriverError("EFFECT_UNKNOWN" if verdict == "unknown" else "RUNTIME_ERROR", str(e), verdict,
                              self._obs(ctx, op, "runtime_observation", verdict, [])) from None
        except DriverError as e:
            if e.observation is None:
                e.observation = self._obs(ctx, op, "runtime_observation", e.verdict, [])
            raise
        ev = self._ev(ctx, op, "operation", "form_read")
        return Outcome(self._obs(ctx, op, "form_read", "confirmed", [ev]), [ev])

    def _readback(self, ctx, op):
        scope = ctx["scope"]
        v = ctx["page"].goto("/slots/" + scope["target"]["slot_ref"])
        if v.page != "slot":
            ev = self._ev(ctx, op, "goal", "independent_readback", observed_state="absent")
            return Readback("not_reached", None, self._obs(ctx, op, "independent_readback", "absent", [ev]), [ev])
        pd = json_digest(json.loads(v.one("payload") or "null"))
        digests = v.all("asset_digest")
        ev = self._ev(ctx, op, "goal", "independent_readback", observed_state=v.one("state"), payload_digest=pd,
                      asset_digests=digests, external_ref=v.one("receipt_id"))
        obs = self._obs(ctx, op, "independent_readback", "confirmed", [ev])
        ok = (v.one("receipt_count") == "1" and pd == json_digest(scope["values"])
              and digests == [a["digest"] for a in scope["assets"]])
        goal = {"goal_kind": scope["goal_kind"], "target": scope["target"], "method": "independent_readback",
                "observed_state": v.one("state"), "payload_digest": pd, "external_ref": v.one("receipt_id"),
                "asset_digests": digests, "evidence_ref": ev["evidence_id"], "observed_at": ev["observed_at"],
                "environment": "mock"}
        return Readback("confirmed" if ok else "not_reached", goal if ok else None, obs, [ev])

    def observe_goal(self, ctx):
        k7 = next(o for o in self.operations({"scope": ctx["scope"]}) if o["step_id"] == "K7")
        try:
            return self._readback(ctx, k7)
        except NavigationUnknown:
            return Readback("unknown", None, self._obs(ctx, k7, "independent_readback", "unknown", []), [])


def identify(page):
    v = page.goto("/account")
    if v.page != "account":
        return None
    return Identity(v.one("account_ref"), v.one("account_label"))


def resolve_target(page, identity):
    v = page.goto("/slots/" + identity["slot_ref"])
    return ("new" if v.page == "slot_absent" else "existing"), v.page


def binding(site: NeutralSite, driver: NeutralDriver) -> PlatformBinding:
    return PlatformBinding(
        profile_id=PROFILE_ID, origin=site.origin, entry_path="/login", identify=identify,
        resolve_target=resolve_target, driver=driver,
        make_context=lambda accepted, page, now: {"scope": accepted["scope"], "page": page, "now": now},
        unknown_exc=NavigationUnknown, structure_exc=PageStructureError)


class Sink:
    """Viewer client stand-in collecting server messages."""

    def __init__(self):
        self.messages: list[dict] = []
        self.cv = threading.Condition()

    def __call__(self, msg):
        with self.cv:
            self.messages.append(msg)
            self.cv.notify_all()

    def wait_for(self, pred, timeout=8.0):
        end = time.monotonic() + timeout
        with self.cv:
            while True:
                hit = next((m for m in self.messages if pred(m)), None)
                if hit is not None:
                    return hit
                left = end - time.monotonic()
                if left <= 0:
                    return None
                self.cv.wait(left)

    def frames(self):
        return [m for m in self.messages if m.get("t") == "frame"]


def human_login_via_viewer(viewer, username, password):
    """Only viewer messages: what a person does in the remote browser (no adapter involvement)."""
    for name, text in (("username", username), ("password", password)):
        x, y = LOGIN_POS[name]
        assert viewer.receive({"t": "mouse", "type": "click", "x": x, "y": y})
        assert viewer.receive({"t": "text", "text": text})
    x, y = LOGIN_POS["login"]
    assert viewer.receive({"t": "mouse", "type": "click", "x": x, "y": y})


def wait_until(pred, timeout=8.0, step=0.05):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(step)
    return False


def temp_db(case) -> pathlib.Path:
    d = tempfile.mkdtemp(prefix="r05-remote-")
    case.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
    return pathlib.Path(d) / "app.sqlite3"


class ReplayPrep:
    """I2 stand-in: pinned replay Preparation for kmong (R02 provider is out of scope here)."""

    def prepare(self, inp):
        return json.loads(json.dumps(dev.fixtures()["kmong"]["cases"]["I2"]["output"]))
