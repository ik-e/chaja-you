"""S2: KNOW (I1), registration create (H4) and pre-start edit (H5).

REQ-01 (missing questions, no invented values), REQ-02 (supported registry only),
REQ-03 (Preparation stored as returned, issues exposed), REQ-10 (owner isolation).
"""

import sqlite3
import unittest

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.app.store import Store

from support import PLATFORMS, SchemaPrep, TickClock, replay_cases, temp_db

A, B = "owner-a", "owner-b"


class KnowledgeResolve(unittest.TestCase):
    def setUp(self):
        self.know = Knowledge()

    def test_supported_profiles_match_replay_except_digest(self):
        for platform in PLATFORMS:
            out = self.know.resolve(platform)
            expected = replay_cases(platform)["I1"]["output"]
            self.assertEqual(out["status"], "supported")
            got, exp = dict(out["profile"]), dict(expected["profile"])
            got_ref, exp_ref = got.pop("ref"), exp.pop("ref")
            self.assertEqual(got, exp)
            self.assertEqual({k: v for k, v in got_ref.items() if k != "digest"},
                             {k: v for k, v in exp_ref.items() if k != "digest"})
            self.assertRegex(got_ref["digest"], r"^[a-f0-9]{64}$")

    def test_unknown_platform_is_typed_unsupported(self):
        out = self.know.resolve("taling")
        self.assertEqual(out["status"], "unsupported")
        contract.validate("ResolveOutput", out)

    def test_invalid_selector_syntax(self):
        for bad in ("", "   ", "x" * 257, "kmong\n"):
            with self.subTest(bad=bad[:10]), self.assertRaises(AppError) as ctx:
                self.know.resolve(bad)
            self.assertEqual(ctx.exception.code, "INVALID_REQUEST")

    def test_get_by_ref_and_digest_drift(self):
        ref = self.know.resolve("kmong")["profile"]["ref"]
        self.assertEqual(self.know.get(ref)["ref"], ref)
        with self.assertRaises(AppError) as ctx:
            self.know.get({**ref, "digest": "a" * 64})
        self.assertEqual(ctx.exception.code, "PROFILE_CHANGED")


class Base(unittest.TestCase):
    platform = "kmong"
    needs: tuple = ()

    def setUp(self):
        self.path = temp_db(self)
        self.prep = SchemaPrep(self.platform, needs=self.needs)
        self.co = Coordinator(Store(self.path), prep=self.prep, clock=TickClock())
        self.src = self.co.create_source(A, {"raw_text": "합성 원본"})

    def register(self, owner=A, selector=None):
        return self.co.create_registration(owner, {"source_id": self.src["source_id"],
                                                   "selector": selector or self.platform})

    def assertCode(self, code, fn, *args):
        with self.assertRaises(AppError) as ctx:
            fn(*args)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)
        return ctx.exception


class CreateRegistration(Base):
    def test_supported_both_platforms(self):
        for platform in PLATFORMS:
            co = Coordinator(Store(temp_db(self)), prep=SchemaPrep(platform), clock=TickClock())
            src = co.create_source(A, {"raw_text": "x"})
            v = co.create_registration(A, {"source_id": src["source_id"], "selector": platform})
            contract.validate("RegistrationView", v)
            self.assertEqual((v["support"], v["revision"], v["job_state"]), ("supported", 1, None))
            self.assertEqual(v["auth"], {"state": "none"})
            self.assertTrue(v["preparation"]["ready"])
            self.assertEqual(v["profile_ref"]["platform"], platform)
            self.assertNotIn("review", v)

    def test_prepare_input_carries_source_and_pinned_profile(self):
        v = self.register()
        call = self.prep.calls[0]
        self.assertEqual(call["source"], self.src)
        self.assertEqual(call["profile"]["ref"], v["profile_ref"])
        self.assertEqual(call["answers"], [])

    def test_unsupported_persists_normal_view_without_prep(self):
        v = self.register(selector="taling")
        self.assertEqual(v["support"], "unsupported")
        self.assertFalse(v["preparation"]["ready"])
        self.assertNotIn("profile_ref", v)
        self.assertEqual(self.prep.calls, [])
        self.assertEqual(self.co.get_registration(A, v["registration_id"]), v)

    def test_other_owner_source_not_found(self):
        self.assertCode("NOT_FOUND", self.register, B)

    def test_prep_failure_persists_model_unavailable(self):
        self.prep.fail = TimeoutError("model timeout")
        v = self.register()
        self.assertFalse(v["preparation"]["ready"])
        self.assertEqual(v["preparation"]["issues"][0]["code"], "model_unavailable")

    def test_invalid_prep_output_is_runtime_error(self):
        self.prep.override = {"ready": True}
        self.assertCode("RUNTIME_ERROR", self.register)
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM registrations").fetchone()[0], 0)

    def test_ready_forced_false_when_blocking_issue(self):
        out = replay_cases("kmong")["I2-missing"]["output"]
        self.prep.override = {**out, "ready": True}
        self.assertFalse(self.register()["preparation"]["ready"])

    def test_no_prep_module_is_not_ready(self):
        co = Coordinator(Store(temp_db(self)), clock=TickClock())
        src = co.create_source(A, {"raw_text": "x"})
        v = co.create_registration(A, {"source_id": src["source_id"], "selector": "kmong"})
        self.assertFalse(v["preparation"]["ready"])


class MissingInformation(Base):
    needs = ("/title",)

    def test_missing_stays_blocked_and_no_value_invented(self):
        v = self.register()
        self.assertFalse(v["preparation"]["ready"])
        issue = v["preparation"]["issues"][0]
        self.assertEqual((issue["field"], issue["blocking"]), ("/title", True))

    def test_answer_resolves_issue_and_bumps_revision(self):
        v = self.register()
        issue = v["preparation"]["issues"][0]
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "answers": [{"issue_id": issue["issue_id"], "value": "합성 음악 레슨 안내 제목"}]})
        self.assertEqual(v2["revision"], 2)
        self.assertTrue(v2["preparation"]["ready"])
        sent = self.prep.calls[-1]["answers"]
        self.assertEqual(len(sent), 1)
        self.assertEqual((sent[0]["field"], sent[0]["origin_issue_id"]), ("/title", issue["issue_id"]))

    def test_answer_to_non_current_issue(self):
        v = self.register()
        self.assertCode("VALIDATION_FAILED", self.co.edit_registration, A, v["registration_id"],
                        {"expected_revision": 1, "answers": [{"issue_id": "nope", "value": "x"}]})


class EditRegistration(Base):
    def test_stale_revision_carries_current(self):
        v = self.register()
        self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "합성 절차 수정 문구"}]})
        err = self.assertCode("STALE_REVISION", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "다른 문구"}]})
        self.assertEqual(err.current_revision, 2)

    def test_correction_same_as_source_fact_is_allowed(self):
        v = self.register()
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/title", "value": "합성 음악 레슨 안내 제목"}]})
        self.assertEqual(v2["revision"], 2)
        self.assertEqual(self.prep.calls[-1]["answers"][0]["field"], "/title")

    def test_prep_conflict_on_corrected_field_needs_new_source(self):
        v = self.register()
        ready = replay_cases("kmong")["I2"]["output"]
        self.prep.override = {**ready, "ready": False, "issues": [
            {"issue_id": "conflict-1", "field": "/title", "code": "conflict",
             "message": "원본 사실과 다름", "blocking": True}]}
        self.assertCode("FACT_CONFLICT", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/title", "value": "다른 제목으로 바꿈"}]})
        self.assertEqual(self.co.get_registration(A, v["registration_id"])["revision"], 1)

    def test_platform_local_correction_is_passed_to_prep(self):
        v = self.register()
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/title", "value": "크몽용 제목"}]})
        self.assertEqual(v2["revision"], 2)
        sent = self.prep.calls[-1]["answers"]
        self.assertEqual((sent[0]["field"], sent[0]["value"]), ("/title", "크몽용 제목"))
        self.assertNotIn("origin_issue_id", sent[0])

    def test_invalid_pointer_and_duplicates(self):
        v = self.register()
        rid = v["registration_id"]
        self.assertCode("VALIDATION_FAILED", self.co.edit_registration, A, rid,
                        {"expected_revision": 1, "corrections": [{"field": "/no_such_field", "value": 1}]})
        self.assertCode("VALIDATION_FAILED", self.co.edit_registration, A, rid,
                        {"expected_revision": 1, "corrections": [{"field": "title", "value": 1}]})
        self.assertCode("INVALID_REQUEST", self.co.edit_registration, A, rid, {
            "expected_revision": 1,
            "corrections": [{"field": "/process", "value": "a"}, {"field": "/process", "value": "b"}]})
        self.assertCode("INVALID_REQUEST", self.co.edit_registration, A, rid, {
            "expected_revision": 1,
            "corrections": [{"field": "/packages", "value": []}, {"field": "/packages/0", "value": {}}]})

    def test_source_change_cannot_carry_answers(self):
        v = self.register()
        other = self.co.create_source(A, {"raw_text": "새 원본"})
        self.assertCode("INVALID_REQUEST", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "source_id": other["source_id"],
            "corrections": [{"field": "/process", "value": "x"}]})

    def test_source_change_clears_answers_and_reprepares(self):
        v = self.register()
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "합성 절차"}]})
        other = self.co.create_source(A, {"raw_text": "새 원본"})
        v3 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": v2["revision"], "source_id": other["source_id"]})
        self.assertEqual(v3["source_id"], other["source_id"])
        self.assertEqual(self.prep.calls[-1]["answers"], [])
        self.assertEqual(self.prep.calls[-1]["source"]["source_id"], other["source_id"])
        self.assertEqual(v3["revision"], 3)

    def test_selector_change_to_unsupported(self):
        v = self.register()
        v2 = self.co.edit_registration(A, v["registration_id"], {"expected_revision": 1, "selector": "taling"})
        self.assertEqual(v2["support"], "unsupported")
        self.assertNotIn("profile_ref", v2)

    def test_explicit_reprepare_after_model_failure(self):
        self.prep.fail = TimeoutError()
        v = self.register()
        self.assertFalse(v["preparation"]["ready"])
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "source_id": self.src["source_id"]})
        self.assertTrue(v2["preparation"]["ready"])
        self.assertEqual(v2["revision"], 2)

    def test_no_material_change_keeps_revision(self):
        v = self.register()
        v2 = self.co.edit_registration(A, v["registration_id"], {
            "expected_revision": 1, "source_id": self.src["source_id"]})
        self.assertEqual(v2["revision"], 1)

    def test_nothing_to_edit(self):
        v = self.register()
        self.assertCode("INVALID_REQUEST", self.co.edit_registration, A, v["registration_id"],
                        {"expected_revision": 1})

    def test_other_owner_cannot_edit_or_read(self):
        v = self.register()
        self.assertCode("NOT_FOUND", self.co.edit_registration, B, v["registration_id"], {
            "expected_revision": 1, "selector": "soomgo"})
        self.assertCode("NOT_FOUND", self.co.get_registration, B, v["registration_id"])

    def test_auth_in_progress_blocks_edit(self):
        v = self.register()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE registrations SET auth_json=? WHERE registration_id=?",
                         ('{"generation": 1, "state": "human"}', v["registration_id"]))
        self.assertCode("INVALID_PHASE", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "x"}]})

    def test_started_registration_blocks_edit(self):
        v = self.register()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE registrations SET job_state='active' WHERE registration_id=?",
                         (v["registration_id"],))
        self.assertCode("INVALID_PHASE", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "x"}]})

    def test_profile_drift_is_profile_changed(self):
        v = self.register()
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT profile_json FROM registrations").fetchone()[0]
            conn.execute("UPDATE registrations SET profile_json=?", (row.replace(v["profile_ref"]["digest"], "b" * 64),))
        self.assertCode("PROFILE_CHANGED", self.co.edit_registration, A, v["registration_id"], {
            "expected_revision": 1, "corrections": [{"field": "/process", "value": "x"}]})


if __name__ == "__main__":
    unittest.main()
