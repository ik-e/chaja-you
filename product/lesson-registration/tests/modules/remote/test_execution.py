"""AC1-AC3 (I4 + STORE): R03 Coordinator (H6/H7/run_job) + R03 StoreGateway + this runtime,
real browser on the neutral mock. Same verified connection is handed to the worker; STORE
admission precedes every browser action; lost response stays unknown and is never resent."""
import json
import sqlite3
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import support as s
from contracts.interfaces import PortFailure
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.store import Store
from lesson_registration.remote import BoundGateway, RemoteRuntime
from lesson_registration.remote.browser import BrowserHost

OWNER = "owner-a"


class Flow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = BrowserHost()

    @classmethod
    def tearDownClass(cls):
        cls.host.close()

    def setUp(self):
        self.site = s.NeutralSite().start()
        self.addCleanup(self.site.stop)
        self.path = s.temp_db(self)
        self.gateway = StoreGateway(Store(self.path))
        self.driver = s.NeutralDriver({})
        self.rt = RemoteRuntime([s.binding(self.site, self.driver)], self.gateway, host=self.host)
        self.addCleanup(self.rt.close)
        self.co = Coordinator(Store(self.path), prep=s.ReplayPrep(), exec_port=self.rt)

    # --- H1..H7 with a human signing in through the viewer between open and finish ---
    def accept(self, account="acct-a"):
        src = self.co.create_source(OWNER, {"raw_text": "합성 원본", "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}, {"img": s.MOCK_IMAGE})
        reg = self.co.create_registration(OWNER, {"source_id": src["source_id"], "selector": "kmong"})
        rid = reg["registration_id"]
        opened = self.co.authenticate(OWNER, rid, {"action": "open", "expected_revision": reg["revision"]})
        self.sink = s.Sink()
        self.viewer = self.rt.attach_viewer(opened["grant"]["viewer_grant"], OWNER, self.sink)
        s.human_login_via_viewer(self.viewer, account, self.site.accounts[account])
        self.assertTrue(s.wait_until(lambda: self.site.logins >= 1))
        r = opened["registration"]
        v = self.co.authenticate(OWNER, rid, {"action": "finish", "expected_revision": r["revision"],
                                              "generation": r["auth"]["generation"]})["registration"]
        self.assertEqual(v["auth"]["state"], "verified")
        scope_assets = self.co.get_source(OWNER, src["source_id"])["asset_refs"]
        self.driver.assets = {a["digest"]: s.MOCK_IMAGE for a in scope_assets}
        body = {"expected_revision": v["revision"], "review_digest": v["review"]["digest"], "approved": True,
                "request_key": f"key-{rid}"}
        self.assertEqual(self.co.start(OWNER, rid, body)[0], 202)
        return rid

    def effects(self, rid):
        with sqlite3.connect(self.path) as conn:
            return dict(conn.execute("SELECT step_id, status FROM effects WHERE registration_id=?", (rid,)).fetchall())

    def job(self, rid):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return dict(conn.execute("SELECT * FROM jobs WHERE registration_id=?", (rid,)).fetchone())

    def result(self, rid):
        return self.co.get_registration(OWNER, rid)


class EndToEnd(Flow):
    def test_same_connection_executes_and_goal_confirmed(self):
        rid = self.accept()
        self.viewer.dispose()                         # viewer detach is not a cancel
        self.assertEqual(self.co.run_job(rid), "done")
        self.assertEqual(self.site.logins, 1)         # worker reused the human's signed-in connection
        self.assertEqual(self.site.submissions, 1)
        self.assertEqual(set(self.effects(rid).values()), {"confirmed"})
        receipt = self.site.receipts[("acct-a", f"slot-{rid}")][0]
        accepted = json.loads(self.job(rid)["accepted_scope_json"])
        self.assertEqual(json.loads(receipt["payload"]), accepted["scope"]["values"])
        self.assertEqual(self.driver.calls, ["K1", "K2", "K3", "K4", "K5", "K6", "K7"])
        self.assertNotIn(rid, self.rt.sessions)       # connection discarded after the job

    def test_lost_submit_response_unknown_not_resent(self):
        rid = self.accept()
        self.site.faults["submit"] = "drop_after_commit"
        state = self.co.run_job(rid)
        self.assertEqual(self.site.submissions, 1)
        self.assertIn(self.effects(rid)["K6"], ("unknown", "confirmed"))   # late readback may resolve it
        self.assertNotEqual(state, "active")
        self.assertEqual(self.co.run_job(rid), state)                       # no second dispatch
        self.assertEqual(self.site.submissions, 1)
        self.assertEqual(self.driver.calls.count("K6"), 1)


class PostRedirects(Flow):
    def assert_redirect_blocked(self, status, phase, *, other_origin=False):
        rid = self.accept()
        session = self.rt.sessions[rid]
        self.site.faults.update(submit_redirect=str(status), redirect_phase=phase)
        if other_origin:
            other = s.NeutralSite().start()
            self.addCleanup(other.stop)
            self.site.faults['redirect_target'] = other.origin + '/unexpected-effect'
        state = self.co.run_job(rid)
        blocked = [event for event in session.audit if event['event'] == 'redirect_blocked']
        self.assertEqual([(event['method'], event['status']) for event in blocked], [('POST', status)])
        self.assertEqual(state, 'stopped')
        self.assertEqual(self.effects(rid)['K6'], 'unknown')
        self.assertEqual(self.result(rid)['result']['goal_verdict'], 'unknown')
        self.assertEqual(self.driver.calls.count('K6'), 1)
        self.assertEqual(len(self.site.submit_requests), 1, 'redirect must not dispatch another POST')
        self.assertEqual(self.site.submit_requests[0]['method'], 'POST')
        self.assertTrue(self.site.submit_requests[0]['path'].endswith('/submit'))
        self.assertEqual(self.site.submissions, 1 if phase == 'after_commit' else 0)
        self.assertEqual(self.co.run_job(rid), state)
        self.assertEqual(len(self.site.submit_requests), 1)
        self.assertEqual(self.site.submissions, 1 if phase == 'after_commit' else 0)
        if other_origin:
            self.assertEqual(other.hits, 0)

    def test_307_before_commit_does_not_forward_post(self):
        self.assert_redirect_blocked(307, 'before_commit')

    def test_308_before_commit_does_not_forward_post(self):
        self.assert_redirect_blocked(308, 'before_commit')

    def test_307_after_commit_has_one_receipt_and_no_forwarded_post(self):
        self.assert_redirect_blocked(307, 'after_commit')

    def test_308_after_commit_has_one_receipt_and_no_forwarded_post(self):
        self.assert_redirect_blocked(308, 'after_commit')

    def test_307_external_redirect_has_no_destination_request(self):
        self.assert_redirect_blocked(307, 'after_commit', other_origin=True)

    def test_308_external_redirect_has_no_destination_request(self):
        self.assert_redirect_blocked(308, 'after_commit', other_origin=True)


class Denials(Flow):
    def test_stale_connection_denied_with_zero_mutation(self):
        rid = self.accept()
        self.rt.sessions[rid].connection_ref = "conn-forged"
        posts = len(self.site.posts)
        self.assertEqual(self.co.run_job(rid), "stopped")
        self.assertEqual(len(self.site.posts), posts)
        self.assertEqual(self.effects(rid), {})

    def test_unregistered_operation_fences_with_zero_mutation(self):
        rid = self.accept()
        posts = len(self.site.posts)
        self.driver.rogue = {"before": "K1", "op": {"operation_id": f"{rid}:K9", "step_id": "K9", "action_key": "delete",
                                                    "effect_class": "potential_effect", "binding_digest": "0" * 64}}
        self.assertEqual(self.co.run_job(rid), "stopped")
        self.assertEqual(len(self.site.posts), posts)
        self.assertEqual(self.effects(rid), {})
        self.assertEqual(self.driver.calls, [])

    def test_exclusive_lease_and_scope_bound_gateway(self):
        rid = self.accept()
        accepted = json.loads(self.job(rid)["accepted_scope_json"])
        ctx = self.rt.gateway.with_verified_connection(accepted)
        with self.assertRaises(PortFailure) as e:              # second worker on the same connection
            self.rt.gateway.with_verified_connection(accepted)
        self.assertEqual(e.exception.error["code"], "INVALID_PHASE")
        bound = BoundGateway(self.rt.gateway, ctx)
        self.assertEqual(sorted(n for n in dir(bound) if not n.startswith("__")),
                         ["_goal", "_list", "_perform", "list_operations", "observe_goal", "perform"])
        with self.assertRaises(AttributeError):
            bound.store = self.gateway                          # __slots__: nothing can be attached
        ops = bound.list_operations()
        self.assertEqual(ops, self.gateway.expected_operations(ctx.store_ctx))
        tampered = dict(ops[1], binding_digest="f" * 64)
        with self.assertRaises(PortFailure) as e:
            bound.perform(tampered)
        self.assertEqual(e.exception.error["code"], "INVALID_REQUEST")
        with self.assertRaises(PortFailure) as e:
            bound.perform(ops[0])                               # fenced after the violation
        self.assertEqual(e.exception.error["code"], "INVALID_PHASE")
        self.assertEqual(self.driver.calls, [])


class BrowserDispatchRaces(Flow):
    def ready_to_submit(self):
        rid = self.accept()
        ctx = self.rt.gateway.with_verified_connection(json.loads(self.job(rid)['accepted_scope_json']))
        bound = BoundGateway(self.rt.gateway, ctx)
        operations = bound.list_operations()
        for operation in operations[:5]:
            bound.perform(operation)
        return rid, bound, operations[5:]

    def test_fence_after_admit_before_dispatch_has_zero_browser_submits(self):
        rid, bound, operations = self.ready_to_submit()
        admit = self.gateway.admit

        def stop_after_admit(context, operation):
            permit = admit(context, operation)
            self.co.coord_store.fence(rid, {'code': 'RUNTIME_ERROR', 'message': 'synthetic stop'})
            return permit

        with patch.object(self.gateway, 'admit', side_effect=stop_after_admit):
            with self.assertRaises(PortFailure) as error:
                bound.perform(operations[0])
        self.assertEqual(error.exception.error['code'], 'PERMISSION_DENIED')
        self.assertEqual(self.site.submissions, 0)
        self.assertNotIn('K6', self.driver.calls)

    def assert_dispatch_fence_race(self, *, response_lost):
        rid, bound, operations = self.ready_to_submit()
        if response_lost:
            self.site.faults['submit'] = 'drop_after_commit'
        consumed, release, attempting, fenced = [threading.Event() for _ in range(4)]
        consume = self.gateway.consume

        def pause_after_consume(*args):
            consume(*args)
            consumed.set()
            if not release.wait(5):
                raise AssertionError('synthetic dispatch barrier timed out')

        def fence():
            attempting.set()
            self.co.coord_store.fence(rid, {'code': 'RUNTIME_ERROR', 'message': 'synthetic stop'})
            fenced.set()

        with ThreadPoolExecutor(2) as pool, patch.object(self.gateway, 'consume', side_effect=pause_after_consume):
            executing = pool.submit(bound.perform, operations[0])
            try:
                self.assertTrue(consumed.wait(5))
                stopping = pool.submit(fence)
                self.assertTrue(attempting.wait(5))
                self.assertFalse(fenced.wait(.1))
                self.assertEqual(self.site.submissions, 0)
            finally:
                release.set()
            if response_lost:
                with self.assertRaises(PortFailure) as error:
                    executing.result(15)
                self.assertEqual(error.exception.error['code'], 'EFFECT_UNKNOWN')
            else:
                self.assertEqual(executing.result(15)['verdict'], 'confirmed')
            stopping.result(10)
        self.assertEqual(self.site.submissions, 1)
        self.assertEqual(self.driver.calls.count('K6'), 1)
        with self.assertRaises(PortFailure):
            bound.perform(operations[1])
        self.assertNotIn('K7', self.driver.calls)
        self.assertEqual(self.site.submissions, 1)
        if response_lost:
            self.assertEqual(self.effects(rid)['K6'], 'unknown')
        state = self.co.run_job(rid)
        self.assertNotEqual(state, 'active')
        self.assertEqual(self.co.run_job(rid), state)
        self.assertEqual(self.site.submissions, 1)

    def test_consume_then_fence_waits_for_real_browser_dispatch(self):
        self.assert_dispatch_fence_race(response_lost=False)

    def test_consume_then_fence_lost_response_stays_unknown(self):
        self.assert_dispatch_fence_race(response_lost=True)


if __name__ == "__main__":
    unittest.main()
