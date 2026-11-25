"""AC1-AC3: adapter against the synthetic Kmong mock with an injected fake gateway."""
import copy
import os
import unittest

import support as s
from lesson_registration.platforms.kmong import KmongAdapter, KmongContext, KmongError
from lesson_registration.platforms.kmong.adapter import expected_snapshot
from lesson_registration.app.result import evaluate as r03_evaluate
from lesson_registration.app.result import payload_digest as r03_payload_digest


class MockCase(unittest.TestCase):
    def setUp(self):
        self.site = s.mock_kmong.MockKmong(accounts=("mock-account-kmong", "mock-account-other")).start()
        self.addCleanup(self.site.stop)
        self.page = s.FormPage(self.site.base_url)
        self.adapter = KmongAdapter()
        self.checker = s.data_schema()

    def ctx(self, accepted=None, assets=None, login=True, account="mock-account-kmong"):
        if login:
            s.human_login(self.page, self.site, account)
        return KmongContext(accepted or s.base_accepted(), self.page, assets or s.default_assets(), s.fixed_clock)

    def run_flow(self, ctx, store=None):
        store = store or s.FakeStore()
        gw = s.FakeGateway(self.adapter, ctx, store)
        return gw, store, gw.run()

    def assert_contract(self, report, store):
        self.assertEqual(self.checker.check(report, "ExecutionReport"), [])
        for ev in store.evidence:
            self.assertEqual(self.checker.check(ev, "EvidenceRecord"), [], ev)
        ids = {e["evidence_id"] for e in store.evidence}
        for o in store.observations:
            self.assertTrue(set(o["evidence_refs"]) <= ids)
        self.assertTrue(all(p.startswith("/") for _, p, _ in self.page.log))   # fixed origin, relative paths only

    def steps(self, report):
        return [(o["step_id"], o["verdict"]) for o in report["observations"]]


class NormalPath(MockCase):
    def test_offline_single_image_end_to_end(self):
        ctx = self.ctx()
        _, store, report = self.run_flow(ctx)
        self.assert_contract(report, store)
        self.assertNotIn("error", report)
        self.assertEqual(self.steps(report), [(f"K{i}", "confirmed") for i in range(1, 8)])
        self.assertEqual(self.site.submissions, 1)
        scope = ctx.accepted["scope"]
        goal = report["goal_observation"]
        receipt = self.site.receipts[("mock-account-kmong", "mock-slot-kmong")][0]
        self.assertEqual(goal["external_ref"], receipt["id"])
        self.assertEqual(goal["asset_digests"], [a["digest"] for a in scope["values"]["main_images"]])
        self.assertEqual(goal["payload_digest"], r03_payload_digest(scope["values"]))   # R03 evaluator rule
        stored = dict(receipt["values"], main_images=receipt["image_digests"])
        self.assertEqual(stored, expected_snapshot(scope["values"]))   # platform side holds exactly approved values
        k6 = next(o for o in report["observations"] if o["step_id"] == "K6")
        self.assertEqual(k6["method"], "submission_response")
        self.assertEqual(goal["method"], "independent_readback")

    def test_r03_result_evaluator_confirms_goal(self):
        ctx = self.ctx()
        _, store, report = self.run_flow(ctx)
        result = r03_evaluate({"profile": s.kmong_profile(), "accepted": ctx.accepted, "report": report,
                               "evidence": store.evidence})
        self.assertEqual(result["goal_verdict"], "confirmed", result.get("error"))

    def test_r03_result_evaluator_rejects_tampered_readback(self):
        self.site.faults["tamper_readback"] = "title"
        ctx = self.ctx()
        _, store, report = self.run_flow(ctx)
        goal = self.adapter.observe_goal(ctx)
        report = dict(report, goal_observation=goal.goal_observation) if goal.goal_observation else report
        result = r03_evaluate({"profile": s.kmong_profile(), "accepted": ctx.accepted, "report": report,
                               "evidence": store.evidence + goal.evidence})
        self.assertNotEqual(result["goal_verdict"], "confirmed")
        self.assertEqual(goal.observation["verdict"], "confirmed")       # a receipt exists ...
        self.assertEqual(goal.verdict, "not_reached")                   # ... but it is not the approved one

    def test_platform_adapter_run_over_bound_gateway(self):
        ctx = self.ctx()
        store = s.FakeStore()
        report = self.adapter.run(s.BoundFake(s.FakeGateway(self.adapter, ctx, store)))
        self.assertEqual(self.checker.check(report, "ExecutionReport"), [])
        self.assertNotIn("error", report)
        self.assertEqual([o["step_id"] for o in report["observations"]], [f"K{i}" for i in range(1, 8)])
        self.assertEqual(self.site.submissions, 1)
        self.site.faults["submit"] = "drop_after_commit"
        other = self.adapter.run(s.BoundFake(s.FakeGateway(self.adapter, ctx, store)))
        self.assertEqual(other["error"]["code"], "DUPLICATE_RISK")   # same effect ledger: K1 not re-admitted
        self.assertEqual(self.site.submissions, 1)

    def test_online_three_images_no_region(self):
        assets = s.default_assets()
        acc = s.base_accepted()
        v = acc["scope"]["values"]
        v["delivery"], v["recruitment"] = "online", "group"
        v.pop("region")
        refs = [assets.add(f"img-{i}", s.make_png(rgb=(i * 40, 90, 150))) for i in range(3)]
        acc["scope"]["assets"] = refs
        v["main_images"] = refs
        ctx = self.ctx(acc, assets)
        _, store, report = self.run_flow(ctx)
        self.assert_contract(report, store)
        self.assertNotIn("error", report, report.get("error"))
        receipt = self.site.receipts[("mock-account-kmong", "mock-slot-kmong")][0]
        self.assertIsNone(receipt["values"]["region"])
        self.assertEqual(receipt["image_digests"], [r["digest"] for r in refs])
        self.assertEqual(report["goal_observation"]["asset_digests"], [r["digest"] for r in refs])


class OnlyRegisteredOperations(MockCase):
    def test_tampered_or_foreign_operation_not_executed(self):
        ctx = self.ctx()
        ops = self.adapter.operations(ctx.accepted)
        before = len(self.site.requests)
        bad = [dict(ops[1], binding_digest="0" * 64), dict(ops[5], action_key="delete_listing"),
               dict(ops[0], effect_class="read"), dict(ops[0], operation_id="kmong-other")]
        for op in bad:
            with self.subTest(op=op), self.assertRaises(KmongError) as e:
                self.adapter.perform(ctx, op)
            self.assertEqual(e.exception.code, "INVALID_REQUEST")
            gw = s.FakeGateway(self.adapter, ctx, s.FakeStore())
            with self.assertRaises(s.Denied):
                gw.perform(op)
        self.assertEqual(len(self.site.requests), before)

    def test_invalid_values_fail_before_any_page_action(self):
        acc = s.base_accepted()
        acc["scope"]["values"]["description"] = "짧은 설명"
        ctx = self.ctx(acc)
        before = len(self.site.requests)
        _, store, report = self.run_flow(ctx)
        self.assertEqual(report["error"]["code"], "VALIDATION_FAILED")
        self.assertEqual(self.checker.check(report, "ExecutionReport"), [])
        self.assertEqual(len(self.site.requests), before)
        self.assertEqual(self.site.drafts, {})

    def test_platform_rule_rejection_is_absent_not_success(self):
        acc = s.base_accepted()
        acc["scope"]["values"]["title"] = "합성 음악 레슨 안내 제목!"   # schema-valid, mock title chars reject '!'
        _, store, report = self.run_flow(self.ctx(acc))
        self.assertEqual(report["error"]["code"], "VALIDATION_FAILED")
        self.assertEqual(self.steps(report), [("K1", "confirmed"), ("K2", "absent")])
        self.assertEqual(self.site.submissions, 0)
        self.assert_contract(report, store)


class ConnectionBinding(MockCase):
    def test_not_signed_in(self):
        _, _, report = self.run_flow(self.ctx(login=False))
        self.assertEqual(report["error"]["code"], "AUTH_REQUIRED")
        self.assertEqual(self.site.drafts, {})

    def test_signed_in_as_other_account(self):
        _, _, report = self.run_flow(self.ctx(account="mock-account-other"))
        self.assertEqual(report["error"]["code"], "ACCOUNT_MISMATCH")
        self.assertEqual(self.site.drafts, {})


class SubmitOnceAndUnknown(MockCase):
    def test_lost_submit_response_is_unknown_then_no_resubmit_and_readback_resolves(self):
        self.site.faults["submit"] = "drop_after_commit"
        ctx = self.ctx()
        _, store, report = self.run_flow(ctx)
        self.assert_contract(report, store)
        self.assertEqual(report["error"]["code"], "EFFECT_UNKNOWN")
        self.assertEqual(self.steps(report)[-1], ("K6", "unknown"))
        self.assertNotIn("goal_observation", report)
        self.assertEqual(self.site.submissions, 1)
        k6 = self.adapter.operations(ctx.accepted)[5]
        # same registration: fenced
        with self.assertRaises(s.Denied) as e:
            s.FakeGateway(self.adapter, ctx, store).perform(k6)
        self.assertEqual(e.exception.code, "INVALID_PHASE")
        # another worker with the same effect ledger: duplicate denied by stable operation id
        other = s.FakeStore()
        other.effects = dict(store.effects)
        with self.assertRaises(s.Denied) as e:
            s.FakeGateway(self.adapter, ctx, other).perform(k6)
        self.assertEqual(e.exception.code, "DUPLICATE_RISK")
        self.site.faults.clear()
        goal = self.adapter.observe_goal(ctx)
        self.assertEqual(goal.verdict, "confirmed")
        self.assertEqual(self.checker.check(goal.goal_observation, "GoalObservation"), [])
        self.assertEqual(self.checker.check(goal.observation, "Observation"), [])   # stored with the goal evidence
        self.assertEqual((goal.observation["step_id"], goal.observation["verdict"]), ("K7", "confirmed"))
        self.assertEqual(self.site.submissions, 1)

    def test_server_error_before_commit_is_unknown_until_readback_says_absent(self):
        self.site.faults["submit"] = "fail_before_commit"
        ctx = self.ctx()
        _, _, report = self.run_flow(ctx)
        self.assertEqual(report["error"]["code"], "EFFECT_UNKNOWN")
        self.assertEqual(self.steps(report)[-1], ("K6", "unknown"))
        goal = self.adapter.observe_goal(ctx)
        self.assertEqual((goal.verdict, goal.reason), ("not_reached", "absent"))
        self.assertEqual(self.site.submissions, 0)

    def test_explicit_rejection_is_absent(self):
        self.site.faults["submit"] = "reject_validation"
        _, _, report = self.run_flow(self.ctx())
        self.assertEqual(report["error"]["code"], "VALIDATION_FAILED")
        self.assertEqual(self.steps(report)[-1], ("K6", "absent"))
        self.assertEqual(self.site.submissions, 0)

    def test_adapter_guard_blocks_second_submit_even_without_gateway(self):
        ctx = self.ctx()
        _, store, report = self.run_flow(ctx)
        self.assertNotIn("error", report)
        k6 = self.adapter.operations(ctx.accepted)[5]
        draft = next(iter(self.site.drafts))
        self.page.goto(f"/gigs/{draft}/review")
        with self.assertRaises(KmongError) as e:
            self.adapter.perform(ctx, k6)
        self.assertEqual((e.exception.code, e.exception.verdict), ("DUPLICATE_RISK", "absent"))
        self.assertEqual(self.site.submissions, 1)

    def test_new_run_on_already_submitted_slot_stops_at_k1(self):
        _, _, first = self.run_flow(self.ctx())
        self.assertNotIn("error", first)
        _, _, second = self.run_flow(self.ctx(), s.FakeStore())
        self.assertEqual(second["error"]["code"], "DUPLICATE_RISK")
        self.assertEqual(self.steps(second), [("K1", "absent")])
        self.assertEqual(self.site.submissions, 1)


class IndependentReadback(MockCase):
    def test_readback_mismatch_is_never_success(self):
        for fault, field in (("title", "title"), ("image", "main_images")):
            with self.subTest(fault):
                site = s.mock_kmong.MockKmong().start()
                self.addCleanup(site.stop)
                page = s.FormPage(site.base_url)
                s.human_login(page, site)
                site.faults["tamper_readback"] = fault
                ctx = KmongContext(s.base_accepted(), page, s.default_assets(), s.fixed_clock)
                _, store, report = self.run_flow(ctx)
                self.assertEqual(report["error"]["code"], "EVIDENCE_INSUFFICIENT")
                self.assertNotIn("goal_observation", report)
                goal = self.adapter.observe_goal(ctx)
                self.assertEqual((goal.verdict, goal.reason, goal.mismatches), ("not_reached", "mismatch", [field]))
                self.assertEqual(site.submissions, 1)

    def test_readback_unobserved_is_unknown(self):
        ctx = self.ctx()
        self.site.faults["readback"] = "drop"
        self.assertEqual(self.adapter.observe_goal(ctx).verdict, "unknown")

    def test_duplicate_receipts_detected(self):
        ctx = self.ctx()
        _, _, report = self.run_flow(ctx)
        key = ("mock-account-kmong", "mock-slot-kmong")
        self.site.receipts[key].append(copy.deepcopy(self.site.receipts[key][0]))   # simulate an out-of-band duplicate
        goal = self.adapter.observe_goal(ctx)
        self.assertEqual((goal.verdict, goal.reason), ("not_reached", "multiple_receipts"))


class MockOnly(unittest.TestCase):
    def test_mock_refuses_non_mock_environment(self):
        old = os.environ.get("LR_ENVIRONMENT")
        os.environ["LR_ENVIRONMENT"] = "live"
        try:
            with self.assertRaises(RuntimeError):
                s.mock_kmong.MockKmong()
        finally:
            if old is None:
                os.environ.pop("LR_ENVIRONMENT")
            else:
                os.environ["LR_ENVIRONMENT"] = old

    def test_mock_binds_loopback_only(self):
        site = s.mock_kmong.MockKmong()
        try:
            self.assertEqual(site.server.server_address[0], "127.0.0.1")
        finally:
            site.server.server_close()


if __name__ == "__main__":
    unittest.main()
