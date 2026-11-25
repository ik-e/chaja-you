"""S4: admit / observe / fence / finalize, lost responses, crash recovery.

T5-12 (only registered bound actions, atomic admission, stale/post-fence denied, unknown kept)
and DV-01 (error-only stop, no later effects, absent/confirmed/unknown separated, no resume).
REQ-05, REQ-08.
"""

import json
import sqlite3
import threading
import unittest

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.gateway import StoreGateway, WorkerContext
from lesson_registration.app.store import Store, atomic, tx

from support import PLATFORMS, GatewayRuntime, SchemaPrep, TickClock, mock_image, temp_db

A = "owner-a"


class Base(unittest.TestCase):
    platform = "kmong"

    def setUp(self):
        self.path = temp_db(self)
        self.rt = GatewayRuntime(self.platform)
        self.co = self.make_co()
        self.rt.gateway = StoreGateway(Store(self.path), clock=TickClock(500))
        self.rid = self.accepted()

    def make_co(self):
        return Coordinator(Store(self.path), prep=SchemaPrep(self.platform), exec_port=self.rt, clock=TickClock())

    def accepted(self, text="합성 원본"):
        src = self.co.create_source(A, {"raw_text": text, "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}, {"img": mock_image()})
        reg = self.co.create_registration(A, {"source_id": src["source_id"], "selector": self.platform})
        rid = reg["registration_id"]
        r = self.co.authenticate(A, rid, {"action": "open", "expected_revision": reg["revision"]})["registration"]
        v = self.co.authenticate(A, rid, {"action": "finish", "expected_revision": r["revision"],
                                          "generation": r["auth"]["generation"]})["registration"]
        self.start_body = {"expected_revision": v["revision"], "review_digest": v["review"]["digest"],
                           "approved": True, "request_key": f"key-{rid}"}
        self.assertEqual(self.co.start(A, rid, self.start_body)[0], 202)
        return rid

    def job(self, rid=None):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute("SELECT * FROM jobs WHERE registration_id=?", (rid or self.rid,)).fetchone()

    def effects(self, rid=None):
        with sqlite3.connect(self.path) as conn:
            return dict(conn.execute("SELECT step_id, status FROM effects WHERE registration_id=?",
                                     (rid or self.rid,)).fetchall())

    def result(self, rid=None):
        return json.loads(self.job(rid)["result_json"])

    def assertCode(self, code, fn, *args):
        with self.assertRaises(AppError) as ctx:
            fn(*args)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)


class HappyPath(Base):
    def test_done_only_with_confirmed_goal_and_all_effects_resolved(self):
        self.assertEqual(self.co.run_job(self.rid), "done")
        self.assertEqual(set(self.effects().values()), {"confirmed"})
        self.assertEqual(set(self.effects()), {"K1", "K2", "K3", "K4", "K6"})  # reads reserve nothing
        res = self.result()
        contract.validate("Result", res)
        self.assertEqual(res["goal_verdict"], "confirmed")
        self.assertIsNone(self.job()["worker_lease"])
        view = self.co.get_registration(A, self.rid)
        self.assertEqual(view["job_state"], "done")

    def test_both_platforms(self):
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                self.platform = platform
                self.setUp()
                self.assertEqual(self.co.run_job(self.rid), "done")

    def test_run_job_is_one_shot(self):
        self.co.run_job(self.rid)
        self.assertEqual(self.co.run_job(self.rid), "done")
        self.assertEqual(self.rt.executions, 1)


class AdmissionGuards(Base):
    def setUp(self):
        super().setUp()
        self.gw = self.rt.gateway
        self.ctx = self.gw.acquire_context(self.rid)
        self.ops = {o["step_id"]: o for o in self.gw.expected_operations(self.ctx)}

    def test_exclusive_lease(self):
        self.assertCode("INVALID_PHASE", self.gw.acquire_context, self.rid)

    def test_stale_or_foreign_lease(self):
        self.assertCode("PERMISSION_DENIED", self.gw.admit, WorkerContext(self.rid, "lease-forged"), self.ops["K1"])
        self.assertEqual(self.effects(), {})

    def test_unregistered_step_and_wrong_binding_and_class(self):
        self.assertCode("PERMISSION_DENIED", self.gw.admit, self.ctx, {**self.ops["K1"], "step_id": "K99"})
        self.assertCode("PERMISSION_DENIED", self.gw.admit, self.ctx, {**self.ops["K2"], "binding_digest": "d" * 64})
        self.assertCode("PERMISSION_DENIED", self.gw.admit, self.ctx, {**self.ops["K6"], "effect_class": "read"})
        self.assertEqual(self.effects(), {})

    def test_same_effect_cannot_be_admitted_twice_even_with_new_operation_id(self):
        self.gw.admit(self.ctx, self.ops["K6"])
        self.assertCode("DUPLICATE_RISK", self.gw.admit, self.ctx, self.ops["K6"])
        self.assertCode("DUPLICATE_RISK", self.gw.admit, self.ctx, {**self.ops["K6"], "operation_id": "renamed"})
        self.assertEqual(self.effects(), {"K6": "reserved"})

    def test_reads_need_no_reservation(self):
        self.gw.admit(self.ctx, self.ops["K7"])
        self.assertEqual(self.effects(), {})

    def test_no_admission_after_fence_but_reads_allowed(self):
        self.gw.admit(self.ctx, self.ops["K1"])
        self.gw.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "page changed"})
        self.assertEqual(self.job()["state"], "stopping")
        self.assertEqual(self.effects(), {"K1": "unknown"})
        self.assertCode("INVALID_PHASE", self.gw.admit, self.ctx, self.ops["K2"])
        self.gw.admit(self.ctx, self.ops["K7"])  # late read-only check still allowed

    def test_observation_cannot_downgrade_confirmed(self):
        self.gw.admit(self.ctx, self.ops["K1"])
        target = json.loads(self.job()["accepted_scope_json"])["scope"]["target"]
        base = {"operation_id": self.ops["K1"]["operation_id"], "step_id": "K1", "target": target,
                "method": "runtime_observation", "evidence_refs": [], "observed_at": "2026-11-25T01:00:00Z"}
        self.gw.record_observation(self.ctx, {**base, "verdict": "confirmed"}, [])
        self.gw.record_observation(self.ctx, {**base, "verdict": "unknown", "observed_at": "2026-11-25T01:00:01Z"}, [])
        self.assertEqual(self.effects(), {"K1": "confirmed"})

    def test_foreign_target_observation_rejected(self):
        target = json.loads(self.job()["accepted_scope_json"])["scope"]["target"]
        obs = {"operation_id": "x", "step_id": "K1", "target": {**target, "slot_ref": "other"},
               "method": "runtime_observation", "verdict": "confirmed", "evidence_refs": [],
               "observed_at": "2026-11-25T01:00:00Z"}
        self.assertCode("PERMISSION_DENIED", self.gw.record_observation, self.ctx, obs, [])

    def test_terminal_is_never_reopened(self):
        with Store(self.path).connect() as conn, tx(conn):
            atomic.finalize(conn, self.rid, {"goal_verdict": "unknown"}, "2026-11-25T02:00:00Z")
        with Store(self.path).connect() as conn, tx(conn):
            with self.assertRaises(atomic.StoreRejected):
                atomic.finalize(conn, self.rid, {"goal_verdict": "confirmed"}, "2026-11-25T02:00:01Z")
        self.assertEqual(self.job()["state"], "stopped")


class FenceRace(Base):
    def test_admit_and_fence_are_serialised(self):
        for round_ in range(15):
            with self.subTest(round=round_):
                self.setUp()
                gw = self.rt.gateway
                ctx = gw.acquire_context(self.rid)
                ops = [o for o in gw.expected_operations(ctx) if o["effect_class"] == "potential_effect"]
                start = threading.Barrier(2)
                after_fence: list[str] = []
                fenced = threading.Event()

                def worker():
                    start.wait()
                    for op in ops:
                        try:
                            gw.admit(ctx, op)
                            if fenced.is_set():
                                after_fence.append(op["step_id"])
                        except AppError:
                            pass

                def stopper():
                    start.wait()
                    gw.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
                    fenced.set()

                threads = [threading.Thread(target=worker), threading.Thread(target=stopper)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                self.assertEqual(after_fence, [])
                self.assertNotIn("reserved", self.effects().values())  # anything admitted pre-fence is unknown


class LostResponses(Base):
    def test_lost_before_any_effect_is_not_reached(self):
        self.rt.crash = ("K1", "before_admit")
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        res = self.result()
        self.assertEqual((res["goal_verdict"], self.effects()), ("not_reached", {}))
        self.assertEqual(res["error"]["code"], "RUNTIME_ERROR")

    def test_lost_after_effect_keeps_unknown_and_never_redispatches(self):
        self.rt.crash = ("K6", "after_admit")
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        eff = self.effects()
        self.assertEqual(eff["K6"], "unknown")
        self.assertEqual({eff[s] for s in ("K1", "K2", "K3", "K4")}, {"confirmed"})
        res = self.result()
        self.assertEqual((res["goal_verdict"], res["error"]["code"]), ("unknown", "EFFECT_UNKNOWN"))
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        self.assertEqual(self.rt.executions, 1)

    def test_runtime_error_report_fences(self):
        self.rt.goal = "none"
        self.rt.report_error = {"code": "RUNTIME_ERROR", "message": "unexpected page"}
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        self.assertEqual(self.result()["error"]["code"], "RUNTIME_ERROR")

    def test_no_goal_evidence_is_never_success(self):
        self.rt.goal = "none"
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        self.assertEqual(self.result()["goal_verdict"], "unknown")

    def test_mismatched_payload_is_not_reached(self):
        self.rt.goal = "bad_payload"
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        self.assertEqual(self.result()["goal_verdict"], "not_reached")

    def test_runtime_requested_fence_mid_run(self):
        def hook(step):
            if step == "K3":
                self.rt.gateway.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "condition lost"})
        self.rt.on_step = hook
        self.rt.goal = "none"
        self.assertEqual(self.co.run_job(self.rid), "stopped")
        self.assertNotIn("K4", self.effects())  # admission refused after fence -> run ended


class CrashRecovery(Base):
    def test_worker_crash_then_recover_stops_and_keeps_unknown(self):
        gw = self.rt.gateway
        ctx = gw.acquire_context(self.rid)
        op = next(o for o in gw.expected_operations(ctx) if o["step_id"] == "K1")
        gw.admit(ctx, op)  # ...process dies here
        restarted = self.make_co()
        self.assertEqual(restarted.recover(), [self.rid])
        self.assertEqual(self.job()["state"], "stopped")
        self.assertEqual(self.effects(), {"K1": "unknown"})
        self.assertEqual(restarted.run_job(self.rid), "stopped")
        self.assertEqual(self.rt.executions, 0)

    def test_accepted_but_never_dispatched_is_stopped_not_resumed(self):
        self.assertEqual(self.make_co().recover(), [self.rid])
        res = self.result()
        self.assertEqual((self.job()["state"], res["goal_verdict"]), ("stopped", "not_reached"))

    def test_late_read_evidence_refines_without_reopening(self):
        self.rt.crash = ("K6", "after_admit")
        self.co.run_job(self.rid)
        target = json.loads(self.job()["accepted_scope_json"])["scope"]["target"]
        obs = {"operation_id": "late", "step_id": "K6", "target": target, "method": "independent_readback",
               "verdict": "confirmed", "evidence_refs": [], "observed_at": "2026-11-25T03:00:00Z"}
        self.rt.gateway.record_observation(self.rt.ctx, obs, [])  # stale context: late read-only evidence
        self.assertEqual(self.effects()["K6"], "confirmed")
        self.assertEqual(self.job()["state"], "stopped")


class DuplicateIntent(Base):
    def test_after_unknown_stop_no_new_effect_by_any_key(self):
        self.rt.crash = ("K6", "after_admit")
        self.co.run_job(self.rid)
        self.assertEqual(self.co.start(A, self.rid, self.start_body)[0], 200)  # same key: replay only
        self.assertCode("IDEMPOTENCY_CONFLICT", self.co.start, A, self.rid, {**self.start_body, "request_key": "k2"})
        other = self.accepted_or_error()
        self.assertEqual(other, "DUPLICATE_RISK")

    def accepted_or_error(self):
        try:
            self.accepted(text="같은 대상 다른 원본")
        except AppError as exc:
            return exc.code
        return "accepted"


if __name__ == "__main__":
    unittest.main()
