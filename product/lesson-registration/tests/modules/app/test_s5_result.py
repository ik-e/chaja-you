"""S5: RESULT (I5) rules, H8 detail with progress/result, H9 list.

AC3 (no success without real observation), T5-05 (reconnect, owner/non-owner, GET has no
side effects), REQ-06/07 (independent readback must match), REQ-08 (result/next action).
"""

import copy
import json
import sqlite3
import unittest

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.result import evaluate, payload_digest
from lesson_registration.app.store import Store

from support import PLATFORMS, GatewayRuntime, SchemaPrep, TickClock, mock_image, replay_cases, temp_db

A, B = "owner-a", "owner-b"


def replay_i5(platform, *, fix_payload=True):
    """Replay I5 input; its payload digest is a placeholder, so optionally set the real digest."""
    inp = copy.deepcopy(replay_cases(platform)["I5"]["input"])
    if fix_payload:
        pd = payload_digest(inp["accepted"]["scope"]["values"])
        inp["report"]["goal_observation"]["payload_digest"] = pd
        for rec in inp["evidence"]:
            if rec["kind"] == "goal":
                rec["payload_digest"] = pd
    return inp


class EvaluateRules(unittest.TestCase):
    def test_replay_i5_confirmed_matches_verdict_and_effects(self):
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                out = evaluate(replay_i5(platform))
                expected = replay_cases(platform)["I5"]["output"]
                contract.validate("Result", out)
                self.assertEqual(out["goal_verdict"], "confirmed")
                self.assertEqual(out["effects"], expected["effects"])
                self.assertNotIn("error", out)

    def test_replay_placeholder_payload_is_not_success(self):
        self.assertEqual(evaluate(replay_i5("kmong", fix_payload=False))["goal_verdict"], "not_reached")

    def test_replay_i5_unknown(self):
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                case = replay_cases(platform)["I5-unknown"]
                out = evaluate(copy.deepcopy(case["input"]))
                self.assertEqual(out["goal_verdict"], "unknown")
                self.assertEqual(out["error"], case["output"]["error"])

    def mutate(self, fn):
        inp = replay_i5("kmong")
        fn(inp)
        return evaluate(inp)

    def test_no_goal_observation(self):
        out = self.mutate(lambda i: i["report"].pop("goal_observation"))
        self.assertEqual((out["goal_verdict"], out["error"]["code"]), ("unknown", "EVIDENCE_INSUFFICIENT"))

    def test_goal_without_matching_stored_evidence(self):
        def drop(i):
            i["evidence"] = [e for e in i["evidence"] if e["kind"] != "goal"]
        self.assertEqual(self.mutate(drop)["goal_verdict"], "unknown")

    def test_goal_differs_from_stored_record(self):
        def tamper(i):
            i["report"]["goal_observation"]["observed_state"] = "something_else"
        self.assertEqual(self.mutate(tamper)["goal_verdict"], "unknown")

    def test_method_not_allowed_by_profile(self):
        def m(i):
            i["report"]["goal_observation"]["method"] = "submission_response"
            for e in i["evidence"]:
                if e["kind"] == "goal":
                    e["method"] = "submission_response"
        self.assertEqual(self.mutate(m)["goal_verdict"], "unknown")

    def test_wrong_target(self):
        def t(i):
            other = {**i["accepted"]["scope"]["target"], "slot_ref": "other-slot"}
            i["report"]["goal_observation"]["target"] = other
            for e in i["evidence"]:
                if e["kind"] == "goal":
                    e["target"] = other
        self.assertEqual(self.mutate(t)["goal_verdict"], "not_reached")

    def test_price_change_is_not_success(self):
        def price(i):
            i["accepted"]["scope"]["values"]["packages"][0]["price_krw"] = 1
        out = self.mutate(price)
        self.assertEqual(out["goal_verdict"], "not_reached")

    def test_missing_image_digest_is_not_success(self):
        def img(i):
            i["report"]["goal_observation"]["asset_digests"] = []
            for e in i["evidence"]:
                if e["kind"] == "goal":
                    e["asset_digests"] = []
        self.assertEqual(self.mutate(img)["goal_verdict"], "not_reached")

    def test_unknown_effect_blocks_confirmed(self):
        def unk(i):
            i["report"]["observations"][5]["verdict"] = "unknown"
        out = self.mutate(unk)
        self.assertEqual((out["goal_verdict"], out["error"]["code"]), ("unknown", "EFFECT_UNKNOWN"))

    def test_evaluator_error_fails_closed(self):
        out = evaluate({"profile": {}, "accepted": {}, "report": {}, "evidence": []})
        self.assertEqual(out["goal_verdict"], "unknown")
        contract.validate("Result", out)


class Flow(unittest.TestCase):
    platform = "kmong"

    def setUp(self):
        self.path = temp_db(self)
        self.rt = GatewayRuntime(self.platform)
        self.co = self.make_co()
        self.rt.gateway = StoreGateway(Store(self.path), clock=TickClock(500))

    def make_co(self):
        return Coordinator(Store(self.path), prep=SchemaPrep(self.platform), exec_port=self.rt, clock=TickClock())

    def accepted(self, owner=A, text="합성 원본"):
        co = self.co
        src = co.create_source(owner, {"raw_text": text, "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}, {"img": mock_image()})
        reg = co.create_registration(owner, {"source_id": src["source_id"], "selector": self.platform})
        rid = reg["registration_id"]
        r = co.authenticate(owner, rid, {"action": "open", "expected_revision": reg["revision"]})["registration"]
        v = co.authenticate(owner, rid, {"action": "finish", "expected_revision": r["revision"],
                                         "generation": r["auth"]["generation"]})["registration"]
        co.start(owner, rid, {"expected_revision": v["revision"], "review_digest": v["review"]["digest"],
                              "approved": True, "request_key": f"key-{rid}"})
        return rid

    def snapshot(self):
        with sqlite3.connect(self.path) as conn:
            return [conn.execute(f"SELECT * FROM {t} ORDER BY 1").fetchall()
                    for t in ("registrations", "jobs", "effects", "observations", "evidence")]


class DetailView(Flow):
    def test_active_progress_before_run(self):
        rid = self.accepted()
        v = self.co.get_registration(A, rid)
        self.assertEqual(v["job_state"], "active")
        self.assertEqual((v["progress"]["step_index"], v["progress"]["step_count"]), (0, 7))
        self.assertEqual(v["progress"]["current_step"]["status"], "pending")
        self.assertNotIn("result", v)

    def test_done_view_has_full_progress_and_result(self):
        rid = self.accepted()
        self.co.run_job(rid)
        v = self.co.get_registration(A, rid)
        contract.validate("RegistrationView", v)
        self.assertEqual(v["job_state"], "done")
        self.assertEqual(v["progress"]["step_index"], 7)
        self.assertNotIn("current_step", v["progress"])
        self.assertEqual(v["result"]["goal_verdict"], "confirmed")
        self.assertEqual(v["result"]["next_action"], "모의 등록이 확인되었습니다.")

    def test_stopped_view_shows_unknown_step_and_next_action(self):
        self.rt.crash = ("K6", "after_admit")
        rid = self.accepted()
        self.co.run_job(rid)
        v = self.co.get_registration(A, rid)
        self.assertEqual(v["job_state"], "stopped")
        self.assertEqual(v["progress"]["step_index"], 5)  # K1~K5 confirmed (K5 is a read check)
        self.assertEqual(v["progress"]["current_step"], {"step_id": "K6", "label": "모의 심사 접수 1회",
                                                         "status": "unknown"})
        k6 = next(e for e in v["result"]["effects"] if e["step_id"] == "K6")
        self.assertEqual(k6["verdict"], "unknown")
        self.assertIn("자동 재제출하지 않습니다", v["result"]["next_action"])

    def test_get_has_no_side_effects(self):
        rid = self.accepted()
        self.co.run_job(rid)
        before = self.snapshot()
        for _ in range(5):
            self.co.get_registration(A, rid)
            self.co.list_registrations(A)
        self.assertEqual(self.snapshot(), before)

    def test_non_owner_404(self):
        rid = self.accepted()
        with self.assertRaises(AppError) as ctx:
            self.co.get_registration(B, rid)
        self.assertEqual(ctx.exception.code, "NOT_FOUND")

    def test_reconnect_after_restart_sees_persisted_job(self):
        rid = self.accepted()
        active_view = self.co.get_registration(A, rid)
        restarted = self.make_co()
        self.assertEqual(restarted.get_registration(A, rid), active_view)
        self.co.run_job(rid)
        self.assertEqual(self.make_co().get_registration(A, rid)["job_state"], "done")

    def test_revision_increases_through_execution(self):
        rid = self.accepted()
        r1 = self.co.get_registration(A, rid)["revision"]
        self.rt.crash = ("K6", "after_admit")
        self.co.run_job(rid)
        self.assertGreater(self.co.get_registration(A, rid)["revision"], r1)


class ListView(Flow):
    def test_list_summaries_and_owner_scope(self):
        done = self.accepted(text="a")
        self.co.run_job(done)
        self.rt.slot = "mock-slot-second"  # a different target; the same one would be DUPLICATE_RISK
        pending = self.accepted(text="b")
        src = self.co.create_source(B, {"raw_text": "b의 원본"})
        self.co.create_registration(B, {"source_id": src["source_id"], "selector": "kmong"})
        out = self.co.list_registrations(A)
        contract.validate("RegistrationList", out)
        by_id = {i["registration_id"]: i for i in out["items"]}
        self.assertEqual(set(by_id), {done, pending})
        self.assertEqual(by_id[done]["goal_verdict"], "confirmed")
        self.assertNotIn("goal_verdict", by_id[pending])
        text = json.dumps(out)
        self.assertNotIn("conn-", text)
        self.assertNotIn("mock-account", text)

    def test_paging_and_cursor_binding(self):
        ids = []
        for i in range(5):
            src = self.co.create_source(A, {"raw_text": str(i)})
            ids.append(self.co.create_registration(A, {"source_id": src["source_id"],
                                                       "selector": "taling"})["registration_id"])
        p1 = self.co.list_registrations(A, {"limit": 2})
        p2 = self.co.list_registrations(A, {"limit": 2, "cursor": p1["next_cursor"]})
        p3 = self.co.list_registrations(A, {"limit": 2, "cursor": p2["next_cursor"]})
        seen = [i["registration_id"] for p in (p1, p2, p3) for i in p["items"]]
        self.assertEqual(seen, ids[::-1])
        self.assertNotIn("next_cursor", p3)
        with self.assertRaises(AppError):
            self.co.list_registrations(B, {"cursor": p1["next_cursor"]})
        with self.assertRaises(AppError):  # source cursors are not registration cursors
            self.co.list_sources(A, {"cursor": p1["next_cursor"]})


if __name__ == "__main__":
    unittest.main()
