"""Kmong mock listing adapter: K1..K7 over a runtime-provided ScopedPage.

Contract duties (common-integration-v1 RT-02..RT-04, I4):
- only registered operations with the exact binding digest recomputed from the accepted scope
- actual arguments come from the immutable scope, never from the caller
- report only what was observed; never change job state (runtime/CO own it)
- K6 response alone is never success; goal needs K7 independent readback by slot
"""
from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass, field
from urllib.parse import quote

from contracts.canonical import json_digest

from . import operations as ops_mod
from . import profile
from .errors import KmongError
from .page import KmongContext, NavigationUnknown, PageStructureError, PageView, UploadFile

SEP = ">"
DRAFT_RE = re.compile(r"^d-[0-9a-f]{16}$")
TEXT_KEYS = ("title", "description", "recruitment", "delivery", "process", "preparation")
PKG_INT = ("amount_vat_included_krw", "work_days", "revision_count", "minutes_per_session", "sessions")


@dataclass
class GoalReadback:
    verdict: str                      # GoalVerdict: confirmed | not_reached | unknown
    goal_observation: dict | None
    reason: str
    mismatches: list = field(default_factory=list)
    observation: dict | None = None   # K7 read observation the goal evidence travels with (S-OBSERVE)
    evidence: list = field(default_factory=list)


@dataclass
class StepOutcome:
    observation: dict
    evidence: list
    goal: GoalReadback | None = None


def _norm_text(v):
    return v.replace("\r\n", "\n") if isinstance(v, str) else v


def expected_snapshot(values: dict) -> dict:
    """Normalized comparable form of the approved values (also used for payload digest)."""
    out = {k: _norm_text(values.get(k)) for k in TEXT_KEYS}
    out["category_path"] = list(values["category_path"])
    out["region"] = dict(values["region"]) if values.get("delivery") == "offline" and values.get("region") else None
    out["packages"] = [dict(p) for p in profile.ordered_packages(values["packages"])]
    out["main_images"] = [img["digest"] for img in values["main_images"]]
    return out


def readback_snapshot(view: PageView) -> dict:
    """Normalize what the platform page actually shows. Raises PageStructureError if malformed."""
    try:
        out = {k: _norm_text(view.one(k)) for k in TEXT_KEYS}
        cat = view.one("category_path")
        out["category_path"] = cat.split(SEP) if cat is not None else None
        if view.one("region_key") is not None:
            out["region"] = {"region_key": view.one("region_key"), "district_key": view.one("district_key"),
                             "detail_address": view.one("detail_address"),
                             "public_scope_confirmed": view.one("public_scope_confirmed") == "true"}
        else:
            out["region"] = None
        pkgs = []
        for t in profile.TIERS:
            if view.one(f"pkg.{t}.title") is None:
                continue
            p = {"tier": t, "title": view.one(f"pkg.{t}.title"), "description": view.one(f"pkg.{t}.description"),
                 "period": view.one(f"pkg.{t}.period")}
            for k in PKG_INT:
                p[k] = int(view.one(f"pkg.{t}.{k}"))
            pkgs.append(p)
        out["packages"] = pkgs or None
        out["main_images"] = view.all("asset_digest")
        return out
    except (TypeError, ValueError) as e:
        raise PageStructureError(f"readback malformed: {e}") from e


def readback_values(observed: dict, scope: dict) -> dict:
    """Rebuild the accepted ``values`` shape from what the page showed (RT-04: actual readback).

    Only presentation is normalized (package tier order follows the accepted order, image refs are
    looked up by observed digest). Any value the page did not show identically yields a different
    payload digest, so the digest can equal digest(scope.values) only when the readback matches.
    """
    out = {k: observed[k] for k in TEXT_KEYS}
    out["category_path"] = observed["category_path"]
    if observed["region"] is not None:
        out["region"] = observed["region"]
    by_tier = {p["tier"]: p for p in observed["packages"] or []}
    order = [p["tier"] for p in scope["values"].get("packages") or []]
    out["packages"] = [by_tier[t] for t in order if t in by_tier] + [p for t, p in by_tier.items() if t not in order]
    refs = {a["digest"]: a for a in scope["assets"]}
    out["main_images"] = [refs.get(d, {"digest": d}) for d in observed["main_images"]]
    return out


def compare(expected: dict, observed: dict, keys) -> list[str]:
    snap_keys = {"region": "region", "main_images": "main_images"}
    return [k for k in keys if expected.get(snap_keys.get(k, k)) != observed.get(snap_keys.get(k, k))]


class KmongAdapter:
    profile_id = profile.PROFILE_ID

    # ---------- PlatformAdapter (contracts.interfaces) ----------
    def run(self, gateway) -> dict:
        """Drive the registered operations through the runtime's BoundGateway, in order, once each.

        The gateway does admission/observation/fence; this loop never retries and stops at the
        first error. Returns an ExecutionReport-shaped dict.
        """
        from contracts.interfaces import PortFailure

        report: dict = {"observations": []}
        try:
            for op in gateway.list_operations():
                report["observations"].append(gateway.perform(op))
            report["goal_observation"] = gateway.observe_goal()
        except PortFailure as e:
            report["error"] = e.error
        return report

    # ---------- RT-02 ----------
    def operations(self, accepted: dict) -> list[dict]:
        self._check_scope(accepted)
        return ops_mod.list_operations(accepted)

    def validate(self, accepted: dict) -> list[dict]:
        scope = accepted["scope"]
        return profile.validate_values(scope["values"], scope["assets"])

    # ---------- RT-03 ----------
    def perform(self, ctx: KmongContext, operation: dict) -> StepOutcome:
        scope = ctx.accepted["scope"]
        self._check_scope(ctx.accepted)
        registered = {o["operation_id"]: o for o in ops_mod.list_operations(ctx.accepted)}
        if registered.get(operation.get("operation_id")) != operation:
            raise KmongError("INVALID_REQUEST", "operation is not registered for this accepted scope", "absent")
        issues = self.validate(ctx.accepted)
        if issues:
            obs = self._observation(ctx, scope, operation, "runtime_observation", "absent", [])
            raise KmongError("VALIDATION_FAILED", "accepted values violate the kmong mock profile", "absent",
                             issues=issues, observation=obs)
        handler = getattr(self, "_" + operation["step_id"].lower())
        try:
            return handler(ctx, scope, operation)
        except KmongError as e:
            if e.observation is None:   # every admitted operation reports an observation (S-OBSERVE)
                e.observation = self._observation(ctx, scope, operation, "runtime_observation", e.verdict, e.evidence)
            raise
        except NavigationUnknown as e:
            verdict = "unknown" if operation["effect_class"] == "potential_effect" else "absent"
            code = "EFFECT_UNKNOWN" if verdict == "unknown" else "RUNTIME_ERROR"
            obs = self._observation(ctx, scope, operation, "runtime_observation", verdict, [])
            raise KmongError(code, f"no trustworthy response: {e}", verdict, observation=obs) from e
        except PageStructureError as e:
            verdict = "unknown" if operation["effect_class"] == "potential_effect" else "absent"
            obs = self._observation(ctx, scope, operation, "runtime_observation", verdict, [])
            raise KmongError("RUNTIME_ERROR", f"page differs from profile: {e}", verdict, observation=obs) from e

    # ---------- RT-04 ----------
    def observe_goal(self, ctx: KmongContext) -> GoalReadback:
        """Read-only independent readback by slot; safe after fence (no effects)."""
        scope = ctx.accepted["scope"]
        self._check_scope(ctx.accepted)
        op = next(o for o in ops_mod.list_operations(ctx.accepted) if o["step_id"] == "K7")
        try:
            view = ctx.page.goto(self._receipt_path(scope))
        except NavigationUnknown as e:
            obs = self._observation(ctx, scope, op, "independent_readback", "unknown", [])
            return GoalReadback("unknown", None, f"readback not observed: {e}", observation=obs)
        goal, ev = self._judge_receipt(ctx, scope, view, op)
        goal.observation = self._observation(ctx, scope, op, "independent_readback", self._k7_verdict(goal), [ev])
        goal.evidence = [ev]
        return goal

    # ---------- steps ----------
    def _k1(self, ctx, scope, op):
        view = ctx.page.goto("/gigs/new")
        self._require_account(view, scope)
        if view.page != "new_listing":
            raise PageStructureError(f"unexpected page {view.page}")
        ctx.page.fill("slot_ref", scope["target"]["slot_ref"])
        view = ctx.page.submit("start")
        code = view.one("error_code")
        if view.page == "slot_exists" or code == "DUPLICATE_RISK":
            raise self._fail(ctx, scope, op, "DUPLICATE_RISK", "slot already has a listing receipt", "absent", view)
        if view.page == "slot_draft_exists" or code == "TARGET_AMBIGUOUS":
            raise self._fail(ctx, scope, op, "TARGET_AMBIGUOUS", "slot already has an unfinished draft", "absent", view)
        if view.page != "basic" or not DRAFT_RE.match(view.one("draft_id") or ""):
            raise PageStructureError(f"draft not opened (page {view.page}, status {view.status})")
        self._require_account(view, scope)
        if view.one("slot_ref") != scope["target"]["slot_ref"]:
            raise self._fail(ctx, scope, op, "TARGET_AMBIGUOUS", "draft slot differs from target", "confirmed", view)
        ev = self._evidence(ctx, scope, op, "operation", "runtime_observation",
                            payload={"draft_id": view.one("draft_id"), "slot_ref": view.one("slot_ref")})
        return StepOutcome(self._observation(ctx, scope, op, "runtime_observation", "confirmed", [ev]), [ev])

    def _k2(self, ctx, scope, op):
        v = scope["values"]
        draft = self._open_step(ctx, scope, "basic")
        for k in ("title", "description", "recruitment", "delivery", "process", "preparation"):
            ctx.page.fill(k, v[k])
        ctx.page.fill("category_path", SEP.join(v["category_path"]))
        if v["delivery"] == "offline":
            r = v["region"]
            for k in ("region_key", "district_key", "detail_address"):
                ctx.page.fill(k, r[k])
            ctx.page.fill("public_scope_confirmed", "true")
        result = ctx.page.submit("save_basic")
        return self._saved_and_verified(ctx, scope, op, draft, result, "images", self._step_bindings("K2"))

    def _k3(self, ctx, scope, op):
        draft = self._open_step(ctx, scope, "images")
        files = []
        for img in scope["values"]["main_images"]:
            data = ctx.assets.read(img["asset_id"], img["digest"])
            if hashlib.sha256(data).hexdigest() != img["digest"] or len(data) != img["bytes"]:
                raise KmongError("VALIDATION_FAILED", f"asset {img['asset_id']} digest/size mismatch", "absent")
            ext = "png" if img["mime"] == "image/png" else "jpg"
            files.append(UploadFile(f"{img['asset_id']}.{ext}", img["mime"], data))
        ctx.page.attach("main_images", files)
        result = ctx.page.submit("save_images")
        return self._saved_and_verified(ctx, scope, op, draft, result, "packages", ("main_images",))

    def _k4(self, ctx, scope, op):
        draft = self._open_step(ctx, scope, "packages")
        for p in profile.ordered_packages(scope["values"]["packages"]):
            for k in profile.PACKAGE_KEYS[1:]:
                ctx.page.fill(f"pkg.{p['tier']}.{k}", str(p[k]))
        result = ctx.page.submit("save_packages")
        return self._saved_and_verified(ctx, scope, op, draft, result, "review", ("packages",))

    def _k5(self, ctx, scope, op):
        draft = self._current_draft(ctx, scope)
        view = ctx.page.goto(f"/gigs/{draft}/review")
        self._require_draft(view, scope, draft)
        mismatches = compare(expected_snapshot(scope["values"]), readback_snapshot(view), profile.VALUE_KEYS)
        if mismatches or view.one("complete") != "true":
            raise self._fail(ctx, scope, op, "VALIDATION_FAILED",
                             f"pre-submit values differ: {mismatches or ['incomplete']}", "absent", view)
        ev = self._evidence(ctx, scope, op, "operation", "form_read",
                            payload=readback_snapshot(view), assets=view.all("asset_digest"))
        return StepOutcome(self._observation(ctx, scope, op, "form_read", "confirmed", [ev]), [ev])

    def _k6(self, ctx, scope, op):
        draft = self._current_draft(ctx, scope)
        # adapter-side duplicate guard, independent of gateway admission
        pre = ctx.page.goto(self._receipt_path(scope))
        if pre.page != "receipt_absent":
            raise self._fail(ctx, scope, op, "DUPLICATE_RISK",
                             f"slot readback before submit is not absent (page {pre.page})", "absent", pre)
        view = ctx.page.goto(f"/gigs/{draft}/review")
        self._require_draft(view, scope, draft)
        if view.one("complete") != "true":
            raise self._fail(ctx, scope, op, "VALIDATION_FAILED", "draft incomplete before submit", "absent", view)
        result = ctx.page.submit("submit_review")
        if result.page == "submitted" and result.status == 200 and result.one("receipt_id"):
            ev = self._evidence(ctx, scope, op, "operation", "submission_response",
                                state=result.one("state"), external_ref=result.one("receipt_id"))
            return StepOutcome(self._observation(ctx, scope, op, "submission_response", "confirmed", [ev]), [ev])
        if 400 <= result.status < 500 and result.one("error_code") == "VALIDATION_FAILED":
            raise self._fail(ctx, scope, op, "VALIDATION_FAILED", "submission rejected before acceptance", "absent", result)
        # 5xx or unexpected page: platform may or may not have accepted
        raise self._fail(ctx, scope, op, "EFFECT_UNKNOWN",
                         f"submission outcome not established (status {result.status}, page {result.page})", "unknown", result)

    def _k7(self, ctx, scope, op):
        view = ctx.page.goto(self._receipt_path(scope))
        goal, ev = self._judge_receipt(ctx, scope, view, op)
        verdict = self._k7_verdict(goal)
        obs = self._observation(ctx, scope, op, "independent_readback", verdict, [ev])
        goal.observation, goal.evidence = obs, [ev]
        if goal.verdict != "confirmed":
            code = "DUPLICATE_RISK" if goal.reason == "multiple_receipts" else "EVIDENCE_INSUFFICIENT"
            raise KmongError(code, f"goal not confirmed: {goal.reason} {goal.mismatches}", verdict,
                             observation=obs, evidence=[ev], goal=goal)
        return StepOutcome(obs, [ev], goal)

    # ---------- helpers ----------
    @staticmethod
    def _k7_verdict(goal: GoalReadback) -> str:
        if goal.reason in ("mismatch", "multiple_receipts"):
            return "confirmed"   # a receipt exists; it just is not the approved single listing
        return {"confirmed": "confirmed", "not_reached": "absent"}.get(goal.verdict, "unknown")

    def _judge_receipt(self, ctx, scope, view, op=None):
        if view.page == "receipt_absent":
            ev = self._evidence(ctx, scope, op, "goal", "independent_readback", state="absent")
            return GoalReadback("not_reached", None, "absent"), ev
        if view.page != "receipt":
            ev = self._evidence(ctx, scope, op, "goal", "independent_readback", state="unreadable")
            return GoalReadback("unknown", None, f"unexpected page {view.page}"), ev
        observed = readback_snapshot(view)
        payload_digest = json_digest(readback_values(observed, scope))
        ev = self._evidence(ctx, scope, op, "goal", "independent_readback", state=view.one("state"),
                            payload_digest=payload_digest, assets=observed["main_images"],
                            external_ref=view.one("receipt_id"))
        if view.one("slot_ref") != scope["target"]["slot_ref"] or view.one("account_ref") != scope["target"]["external_account_ref"]:
            return GoalReadback("unknown", None, "target mismatch"), ev
        if view.one("receipt_count") != "1":
            return GoalReadback("not_reached", None, "multiple_receipts"), ev
        mismatches = compare(expected_snapshot(scope["values"]), observed, profile.VALUE_KEYS)
        if view.one("state") != profile.GOAL_STATE:
            mismatches.append("state")
        if mismatches:
            return GoalReadback("not_reached", None, "mismatch", mismatches), ev
        goal = {"goal_kind": scope["goal_kind"], "target": dict(scope["target"]), "method": "independent_readback",
                "observed_state": view.one("state"), "payload_digest": payload_digest,
                "external_ref": view.one("receipt_id"), "asset_digests": observed["main_images"],
                "evidence_ref": ev["evidence_id"], "observed_at": ev["observed_at"], "environment": "mock"}
        return GoalReadback("confirmed", goal, "matched"), ev

    def _saved_and_verified(self, ctx, scope, op, draft, result, next_page, keys):
        if result.page != next_page:
            if result.one("error_code") == "VALIDATION_FAILED" and 400 <= result.status < 500:
                raise self._fail(ctx, scope, op, "VALIDATION_FAILED",
                                 "platform rejected: " + "; ".join(result.all("error")), "absent", result)
            raise PageStructureError(f"save did not advance (page {result.page}, status {result.status})")
        self._require_draft(result, scope, draft)
        review = ctx.page.goto(f"/gigs/{draft}/review")
        self._require_draft(review, scope, draft)
        observed = readback_snapshot(review)
        mismatches = compare(expected_snapshot(scope["values"]), observed, keys)
        if mismatches:
            raise self._fail(ctx, scope, op, "VALIDATION_FAILED", f"saved values differ: {mismatches}", "confirmed", review)
        ev = self._evidence(ctx, scope, op, "operation", "form_read",
                            payload={k: observed.get(k) for k in keys},
                            assets=observed["main_images"] if "main_images" in keys else None)
        # return the page to the step just saved is not needed; next step navigates itself
        return StepOutcome(self._observation(ctx, scope, op, "form_read", "confirmed", [ev]), [ev])

    def _open_step(self, ctx, scope, step):
        draft = self._current_draft(ctx, scope)
        view = ctx.page.goto(f"/gigs/{draft}/{step}")
        self._require_draft(view, scope, draft)
        if view.page != step:
            raise PageStructureError(f"expected {step} page, got {view.page}")
        return draft

    def _current_draft(self, ctx, scope):
        view = ctx.page.view()
        draft = view.one("draft_id") or ""
        if not DRAFT_RE.match(draft) or view.one("slot_ref") != scope["target"]["slot_ref"]:
            raise PageStructureError("no current draft for target slot in this connection")
        return draft

    def _require_draft(self, view, scope, draft):
        self._require_account(view, scope)
        if view.one("draft_id") != draft or view.one("slot_ref") != scope["target"]["slot_ref"]:
            raise PageStructureError(f"page not bound to draft {draft}")

    @staticmethod
    def _require_account(view, scope):
        if view.page == "login":
            raise KmongError("AUTH_REQUIRED", "connection is not authenticated", "absent")
        acct = view.one("account_ref")
        if acct != scope["target"]["external_account_ref"] or acct != scope["connection"]["account_ref"]:
            raise KmongError("ACCOUNT_MISMATCH", "page account differs from verified binding", "absent")

    @staticmethod
    def _receipt_path(scope):
        return "/slots/" + quote(scope["target"]["slot_ref"], safe="") + "/receipt"

    @staticmethod
    def _step_bindings(step_id):
        return next(s[3] for s in profile.STEPS if s[0] == step_id)

    @staticmethod
    def _check_scope(accepted):
        scope = accepted["scope"]
        ref, target = scope["profile_ref"], scope["target"]
        expected = (profile.PLATFORM, profile.OBJECT_KIND, profile.VERSION, profile.ENVIRONMENT)
        if (ref["platform"], ref["object_kind"], ref["version"], ref["environment"]) != expected:
            raise KmongError("PROFILE_CHANGED", "scope is not pinned to kmong.service_listing.mock.v2", "absent")
        if (target["environment"], target["platform"], target["object_kind"]) != (profile.ENVIRONMENT, profile.PLATFORM, profile.OBJECT_KIND):
            raise KmongError("UNSUPPORTED_TARGET", "target is not a mock kmong service listing", "absent")
        if tuple(scope["procedure_ids"]) != profile.STEP_IDS or scope["goal_kind"] != profile.GOAL_KIND:
            raise KmongError("PROFILE_CHANGED", "procedure or goal differs from profile", "absent")

    def _fail(self, ctx, scope, op, code, message, verdict, view):
        ev = self._evidence(ctx, scope, op, "error", "runtime_observation",
                            payload={"page": view.page, "status": view.status, "error_code": view.one("error_code"),
                                     "errors": view.all("error")})
        obs = self._observation(ctx, scope, op, "runtime_observation", verdict, [ev])
        return KmongError(code, message, verdict, observation=obs, evidence=[ev])

    @staticmethod
    def _observation(ctx, scope, op, method, verdict, evidence):
        return {"operation_id": op["operation_id"], "step_id": op["step_id"], "target": dict(scope["target"]),
                "method": method, "verdict": verdict, "evidence_refs": [e["evidence_id"] for e in evidence],
                "observed_at": ctx.now()}

    @staticmethod
    def _evidence(ctx, scope, op, kind, method, *, payload=None, assets=None, state=None, external_ref=None,
                  payload_digest=None):
        ev = {"evidence_id": "kmong-ev-" + secrets.token_hex(8), "registration_id": scope["registration_id"],
              "target": dict(scope["target"]), "kind": kind, "method": method, "observed_at": ctx.now(),
              "environment": "mock"}
        if op is not None:
            ev["operation_id"] = op["operation_id"]
        if state:
            ev["observed_state"] = state
        if payload is not None and payload_digest is None:
            payload_digest = ops_mod.sha256(ops_mod.canonical(payload))
        if payload_digest:
            ev["payload_digest"] = payload_digest
        if assets is not None:
            ev["asset_digests"] = list(assets)
        if external_ref:
            ev["external_ref"] = external_ref
        return ev
