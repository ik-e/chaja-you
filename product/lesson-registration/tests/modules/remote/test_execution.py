"""AC1-AC3 (I4 + STORE): R03 Coordinator (H6/H7/run_job) + R03 StoreGateway + this runtime,
real browser on the neutral mock. Same verified connection is handed to the worker; STORE
admission precedes every browser action; lost response stays unknown and is never resent."""
import json
import sqlite3
import unittest

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


if __name__ == "__main__":
    unittest.main()
