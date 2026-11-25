"""S3: authentication (H6), review digest, final approval and atomic acceptance (H7).

T5-01 and REQ-05 (approval/permission guards, zero effect when invalid),
REQ-10 (no internal binding in views).
"""

import json
import sqlite3
import threading
import unittest

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.ids import digest
from lesson_registration.app.store import Store

from support import PLATFORMS, FakeRuntime, SchemaPrep, TickClock, mock_image, temp_db

A, B = "owner-a", "owner-b"


class Base(unittest.TestCase):
    platform = "kmong"

    def setUp(self):
        self.path = temp_db(self)
        self.rt = FakeRuntime(self.platform)
        self.dispatched: list[str] = []
        self.co = self.make_co()
        src = self.co.create_source(A, {"raw_text": "합성 원본", "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}, {"img": mock_image()})
        self.reg = self.co.create_registration(A, {"source_id": src["source_id"], "selector": self.platform})
        self.rid = self.reg["registration_id"]

    def make_co(self, path=None):
        return Coordinator(Store(path or self.path), prep=SchemaPrep(self.platform), exec_port=self.rt,
                           clock=TickClock(), on_accepted=self.dispatched.append)

    def assertCode(self, code, fn, *args):
        with self.assertRaises(AppError) as ctx:
            fn(*args)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)
        return ctx.exception

    def rev(self):
        return self.co.get_registration(A, self.rid)["revision"]

    def open(self):
        return self.co.authenticate(A, self.rid, {"action": "open", "expected_revision": self.rev()})

    def finish(self, generation=None):
        g = generation if generation is not None else self.co.get_registration(A, self.rid)["auth"]["generation"]
        return self.co.authenticate(A, self.rid, {"action": "finish", "expected_revision": self.rev(),
                                                  "generation": g})

    def verified(self):
        self.open()
        return self.finish()["registration"]

    def start_input(self, view, key="key-1", **over):
        body = {"expected_revision": view["revision"], "review_digest": view["review"]["digest"],
                "approved": True, "request_key": key}
        body.update(over)
        return body

    def jobs(self):
        with sqlite3.connect(self.path) as conn:
            return conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]


class Authenticate(Base):
    def test_open_returns_grant_only_in_response(self):
        r = self.open()
        contract.validate("AuthResponse", r)
        self.assertEqual(r["registration"]["auth"], {"state": "human", "generation": 1})
        self.assertEqual(r["grant"]["generation"], 1)
        self.assertEqual(r["registration"]["revision"], 2)
        with sqlite3.connect(self.path) as conn:
            dump = " ".join(str(x) for x in conn.execute("SELECT * FROM registrations").fetchone())
        self.assertNotIn("grant-1", dump)

    def test_finish_verified_without_internal_binding_in_view(self):
        self.open()
        r = self.finish()
        v = r["registration"]
        self.assertNotIn("grant", r)
        self.assertEqual(v["auth"]["state"], "verified")
        self.assertEqual(v["target"]["status"], "new")
        self.assertIn("review", v)
        text = json.dumps(r, ensure_ascii=False)
        for secret in ("conn-1", "mock-account-kmong", "mock-slot-kmong", "synthetic-target-proof"):
            self.assertNotIn(secret, text)

    def test_review_digest_and_content(self):
        v = self.verified()
        review = v["review"]
        contract.validate("ReviewView", review)
        self.assertEqual(review["procedure"][0], "신규 등록 화면 진입")
        self.assertEqual(review["goal"], "mock_listing_receipt")
        self.assertEqual(len(review["assets"]), 1)

    def test_stale_generation_and_refresh_rotation(self):
        self.open()
        r = self.co.authenticate(A, self.rid, {"action": "refresh", "expected_revision": self.rev(), "generation": 1})
        self.assertEqual(r["grant"]["generation"], 2)
        self.assertCode("STALE_REVISION", self.finish, 1)
        self.assertEqual(self.finish(2)["registration"]["auth"]["state"], "verified")

    def test_finish_requires_human_state(self):
        self.assertCode("INVALID_PHASE", self.finish, 0)

    def test_open_requires_ready(self):
        co = Coordinator(Store(temp_db(self)), prep=SchemaPrep("kmong", needs=("/title",)),
                         exec_port=self.rt, clock=TickClock())
        src = co.create_source(A, {"raw_text": "x"})
        v = co.create_registration(A, {"source_id": src["source_id"], "selector": "kmong"})
        self.assertCode("INVALID_PHASE", co.authenticate, A, v["registration_id"],
                        {"action": "open", "expected_revision": 1})

    def test_account_mismatch_closes_and_has_no_review(self):
        self.open()
        self.rt.account_ref = "someone-else"
        err = self.assertCode("ACCOUNT_MISMATCH", self.finish)
        v = self.co.get_registration(A, self.rid)
        self.assertEqual(v["auth"], {"state": "closed"})
        self.assertNotIn("review", v)
        self.assertEqual(err.current_revision, v["revision"])

    def test_runtime_timeout_closes_safely(self):
        self.open()
        self.rt.fail_next = TimeoutError()
        self.assertCode("RUNTIME_ERROR", self.finish)
        self.assertEqual(self.co.get_registration(A, self.rid)["auth"], {"state": "closed"})

    def test_close_invalidates_binding(self):
        self.verified()
        r = self.co.authenticate(A, self.rid, {"action": "close", "expected_revision": self.rev(), "generation": 1})
        self.assertEqual(r["registration"]["auth"], {"state": "closed"})
        self.assertNotIn("review", r["registration"])
        self.assertNotIn("target", r["registration"])

    def test_existing_target_has_no_review(self):
        self.rt.target_status = "existing"
        v = self.verified()
        self.assertEqual(v["target"]["status"], "existing")
        self.assertNotIn("review", v)

    def test_edit_after_verify_invalidates_review(self):
        v = self.verified()
        v2 = self.co.edit_registration(A, self.rid, {"expected_revision": v["revision"],
                                                     "corrections": [{"field": "/title", "value": "크몽용 제목"}]})
        self.assertEqual(v2["auth"], {"state": "closed"})
        self.assertNotIn("review", v2)

    def test_other_owner_cannot_authenticate(self):
        self.assertCode("NOT_FOUND", self.co.authenticate, B, self.rid, {"action": "open", "expected_revision": 1})


class Start(Base):
    def test_accept_then_exact_replay(self):
        v = self.verified()
        status, started = self.co.start(A, self.rid, self.start_input(v))
        self.assertEqual(status, 202)
        self.assertEqual((started["job_state"], started["revision"]), ("active", v["revision"] + 1))
        self.assertNotIn("review", started)
        self.assertEqual(self.dispatched, [self.rid])
        status2, again = self.co.start(A, self.rid, self.start_input(v))
        self.assertEqual((status2, again), (200, started))
        self.assertEqual(self.dispatched, [self.rid])
        self.assertEqual(self.jobs(), 1)

    def test_same_key_different_payload(self):
        v = self.verified()
        self.co.start(A, self.rid, self.start_input(v))
        self.assertCode("IDEMPOTENCY_CONFLICT", self.co.start, A, self.rid,
                        self.start_input(v, expected_revision=v["revision"] + 5))

    def test_different_key_after_accept(self):
        v = self.verified()
        self.co.start(A, self.rid, self.start_input(v))
        self.assertCode("IDEMPOTENCY_CONFLICT", self.co.start, A, self.rid, self.start_input(v, key="key-2"))
        self.assertEqual(self.jobs(), 1)

    def test_replay_precedes_stale_check(self):
        v = self.verified()
        self.co.start(A, self.rid, self.start_input(v))
        # revision moved on after accept, but the exact original request still replays
        self.assertEqual(self.co.start(A, self.rid, self.start_input(v))[0], 200)

    def test_forged_or_stale_digest_zero_effect(self):
        v = self.verified()
        self.assertCode("APPROVAL_INVALID", self.co.start, A, self.rid, self.start_input(v, review_digest="b" * 64))
        self.assertCode("STALE_REVISION", self.co.start, A, self.rid,
                        self.start_input(v, expected_revision=v["revision"] - 1))
        self.assertEqual((self.jobs(), self.dispatched), (0, []))

    def test_old_review_after_reverify_rejected(self):
        v1 = self.verified()
        self.co.edit_registration(A, self.rid, {"expected_revision": v1["revision"],
                                                "corrections": [{"field": "/title", "value": "크몽용 제목"}]})
        v2 = self.verified()
        self.assertNotEqual(v1["review"]["digest"], v2["review"]["digest"])
        self.assertCode("APPROVAL_INVALID", self.co.start, A, self.rid,
                        self.start_input(v2, review_digest=v1["review"]["digest"]))

    def test_requires_verified_auth(self):
        v = self.co.get_registration(A, self.rid)
        self.assertCode("AUTH_REQUIRED", self.co.start, A, self.rid, {
            "expected_revision": v["revision"], "review_digest": "a" * 64, "approved": True, "request_key": "k"})

    def test_ambiguous_and_existing_targets_blocked(self):
        for status, code in (("ambiguous", "TARGET_AMBIGUOUS"), ("existing", "DUPLICATE_RISK")):
            with self.subTest(status=status):
                self.rt.target_status = status
                v = self.verified()
                self.assertCode(code, self.co.start, A, self.rid, {
                    "expected_revision": v["revision"], "review_digest": "a" * 64, "approved": True,
                    "request_key": f"k-{status}"})
                self.co.authenticate(A, self.rid, {"action": "close", "expected_revision": self.rev(),
                                                   "generation": self.rt.generation})

    def test_other_registration_same_target_blocked(self):
        v = self.verified()
        self.co.start(A, self.rid, self.start_input(v))
        src = self.co.create_source(A, {"raw_text": "다른 원본"})
        other = self.co.create_registration(A, {"source_id": src["source_id"], "selector": self.platform})
        self.rid = other["registration_id"]
        v2 = self.verified()
        self.assertCode("DUPLICATE_RISK", self.co.start, A, self.rid, self.start_input(v2, key="key-other"))

    def test_other_owner_start_not_found(self):
        v = self.verified()
        self.assertCode("NOT_FOUND", self.co.start, B, self.rid, self.start_input(v))

    def test_edit_and_auth_blocked_after_start(self):
        v = self.verified()
        _, s = self.co.start(A, self.rid, self.start_input(v))
        self.assertCode("INVALID_PHASE", self.co.edit_registration, A, self.rid,
                        {"expected_revision": s["revision"], "corrections": [{"field": "/title", "value": "x"}]})
        self.assertCode("INVALID_PHASE", self.co.authenticate, A, self.rid,
                        {"action": "close", "expected_revision": s["revision"], "generation": 1})

    def test_accepted_scope_is_immutable_snapshot(self):
        v = self.verified()
        self.co.start(A, self.rid, self.start_input(v))
        with sqlite3.connect(self.path) as conn:
            scope = json.loads(conn.execute("SELECT accepted_scope_json FROM jobs").fetchone()[0])
        contract.validate("AcceptedScope", scope)
        self.assertEqual(scope["review_digest"], v["review"]["digest"])
        self.assertEqual(scope["scope"]["revision"], v["revision"])
        self.assertEqual(scope["scope"]["assets"], v["review"]["assets"])
        # data-contract-v4: the review digest is the canonical digest of the exact internal Scope
        self.assertEqual(digest(scope["scope"]), v["review"]["digest"])

    def test_both_platforms_accept(self):
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                self.platform = platform
                self.setUp()
                v = self.verified()
                self.assertEqual(self.co.start(A, self.rid, self.start_input(v))[0], 202)


class StartRace(Base):
    def test_concurrent_different_keys_accept_exactly_once(self):
        for round_ in range(20):
            with self.subTest(round=round_):
                self.setUp()
                v = self.verified()
                results: list[object] = []
                barrier = threading.Barrier(4)

                def attempt(key):
                    co = self.make_co()
                    barrier.wait()
                    try:
                        results.append(co.start(A, self.rid, self.start_input(v, key=key))[0])
                    except AppError as exc:
                        results.append(exc.code)

                threads = [threading.Thread(target=attempt, args=(f"k{i}",)) for i in range(4)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                self.assertEqual(results.count(202), 1, results)
                self.assertTrue(all(r == 202 or r in ("IDEMPOTENCY_CONFLICT", "STALE_REVISION") for r in results),
                                results)
                self.assertEqual(self.jobs(), 1)


if __name__ == "__main__":
    unittest.main()
