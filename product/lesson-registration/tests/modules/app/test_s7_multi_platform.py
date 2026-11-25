"""S7: one source, two platforms (T5-06, REQ-06/REQ-07, REQ-01 source immutability).

Kmong and Soomgo registrations made from the same source keep independent values,
target, approval, job and result; platform-local corrections stay local; a source fact
change is a new Source version and never alters what an earlier registration used.
"""

import sqlite3
import unittest

from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.store import Store

from support import GatewayRuntime, SchemaPrep, TickClock, mock_image, temp_db

A = "owner-a"


class MultiPrep:
    def __init__(self):
        self.by_platform = {p: SchemaPrep(p) for p in ("kmong", "soomgo")}

    def prepare(self, inp):
        return self.by_platform[inp["profile"]["ref"]["platform"]].prepare(inp)


class MultiRuntime:
    def __init__(self):
        self.by_platform = {p: GatewayRuntime(p) for p in ("kmong", "soomgo")}

    def authenticate(self, inp):
        return self.by_platform[inp["profile_ref"]["platform"]].authenticate(inp)

    def execute(self, inp):
        return self.by_platform[inp["accepted"]["scope"]["target"]["platform"]].execute(inp)


class OneSourceTwoPlatforms(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.rt = MultiRuntime()
        gw = StoreGateway(Store(self.path), clock=TickClock(500))
        for r in self.rt.by_platform.values():
            r.gateway = gw
        self.co = Coordinator(Store(self.path), prep=MultiPrep(), exec_port=self.rt, clock=TickClock())
        self.src = self.co.create_source(A, {"raw_text": "공통 원본", "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}, {"img": mock_image()})
        self.k = self.co.create_registration(A, {"source_id": self.src["source_id"], "selector": "kmong"})
        self.s = self.co.create_registration(A, {"source_id": self.src["source_id"], "selector": "soomgo"})

    def verify(self, rid):
        v = self.co.get_registration(A, rid)
        r = self.co.authenticate(A, rid, {"action": "open", "expected_revision": v["revision"]})["registration"]
        return self.co.authenticate(A, rid, {"action": "finish", "expected_revision": r["revision"],
                                             "generation": r["auth"]["generation"]})["registration"]

    def start(self, rid, key):
        v = self.verify(rid)
        return self.co.start(A, rid, {"expected_revision": v["revision"], "review_digest": v["review"]["digest"],
                                      "approved": True, "request_key": key})

    def test_independent_profiles_values_and_reviews(self):
        self.assertNotEqual(self.k["profile_ref"], self.s["profile_ref"])
        self.assertNotEqual(set(self.k["preparation"]["values"]), set(self.s["preparation"]["values"]))
        vk, vs = self.verify(self.k["registration_id"]), self.verify(self.s["registration_id"])
        self.assertNotEqual(vk["review"]["digest"], vs["review"]["digest"])
        self.assertEqual(vk["review"]["goal"], "mock_listing_receipt")
        self.assertEqual(vs["review"]["goal"], "mock_service_configuration_saved")

    def test_local_correction_does_not_touch_other_platform(self):
        before = self.co.get_registration(A, self.s["registration_id"])
        self.co.edit_registration(A, self.k["registration_id"], {
            "expected_revision": self.k["revision"], "corrections": [{"field": "/title", "value": "크몽 전용 제목"}]})
        self.assertEqual(self.co.get_registration(A, self.s["registration_id"]), before)
        self.assertEqual(self.co.get_registration(A, self.k["registration_id"])["revision"], 2)

    def test_approval_of_one_cannot_start_the_other(self):
        vk = self.verify(self.k["registration_id"])
        vs = self.verify(self.s["registration_id"])
        with self.assertRaises(AppError) as ctx:
            self.co.start(A, self.s["registration_id"], {
                "expected_revision": vs["revision"], "review_digest": vk["review"]["digest"],
                "approved": True, "request_key": "cross"})
        self.assertEqual(ctx.exception.code, "APPROVAL_INVALID")

    def test_both_run_to_independent_results(self):
        self.start(self.k["registration_id"], "k")
        self.start(self.s["registration_id"], "s")
        self.assertEqual(self.co.run_job(self.k["registration_id"]), "done")
        self.rt.by_platform["soomgo"].crash = ("S5", "after_admit")
        self.assertEqual(self.co.run_job(self.s["registration_id"]), "stopped")
        k = self.co.get_registration(A, self.k["registration_id"])
        s = self.co.get_registration(A, self.s["registration_id"])
        self.assertEqual((k["result"]["goal_verdict"], s["result"]["goal_verdict"]), ("confirmed", "unknown"))
        with sqlite3.connect(self.path) as conn:
            keys = [r[0] for r in conn.execute("SELECT effect_key FROM effects")]
        self.assertTrue(any('"kmong"' in key for key in keys) and any('"soomgo"' in key for key in keys))

    def test_unknown_on_one_platform_does_not_block_the_other(self):
        self.start(self.s["registration_id"], "s")
        self.rt.by_platform["soomgo"].crash = ("S5", "after_admit")
        self.co.run_job(self.s["registration_id"])
        self.assertEqual(self.start(self.k["registration_id"], "k")[0], 202)

    def test_new_source_version_leaves_earlier_registration_unchanged(self):
        self.start(self.k["registration_id"], "k")
        self.co.run_job(self.k["registration_id"])
        v2 = self.co.create_source(A, {"raw_text": "가격 정정 원본", "previous_source_id": self.src["source_id"],
                                       "reuse_asset_ids": [self.src["asset_refs"][0]["asset_id"]]})
        self.assertEqual(self.co.get_source(A, self.src["source_id"]), self.src)
        self.assertEqual(self.co.get_registration(A, self.k["registration_id"])["source_id"], self.src["source_id"])
        moved = self.co.edit_registration(A, self.s["registration_id"], {
            "expected_revision": self.s["revision"], "source_id": v2["source_id"]})
        self.assertEqual(moved["source_id"], v2["source_id"])
        self.assertEqual(self.co.get_registration(A, self.k["registration_id"])["source_id"], self.src["source_id"])


if __name__ == "__main__":
    unittest.main()
