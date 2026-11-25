"""Independent synthetic tests of the tentative I2 provider, without a real model."""
import copy
import dev
import tempfile
import unittest
from pathlib import Path

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.app.store import Store
from lesson_registration.preparation.provider import PreparationProvider


class FakeExtractor:
    def __init__(self, candidates=None, fail=False):
        self.candidates = candidates if candidates is not None else []
        self.fail = fail

    def extract(self, source_text, fields):
        if self.fail:
            raise TimeoutError("private provider details")
        return copy.deepcopy(self.candidates)


def request(platform, text, answers=None):
    return {
        "source": {"source_id": "source-test", "raw_text": text, "asset_refs": [],
                   "created_at": "2026-11-25T00:00:00Z"},
        "profile": Knowledge().resolve(platform)["profile"],
        "answers": answers or [],
    }


class PreparationTests(unittest.TestCase):
    def provider(self, candidates=None, fail=False):
        return PreparationProvider(contract.catalog(), FakeExtractor(candidates, fail))

    def test_missing_fields_block_both_platforms(self):
        for platform in ("kmong", "soomgo"):
            with self.subTest(platform=platform):
                result = self.provider().prepare(request(platform, "합성 레슨"))
                contract.catalog().named("Preparation", result)
                self.assertFalse(result["ready"])
                self.assertEqual(result["values"], {})
                self.assertTrue(any(issue["code"] == "missing" and issue["blocking"]
                                    for issue in result["issues"]))

    def test_source_candidate_is_retained_but_needs_confirmation(self):
        result = self.provider([{"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"}]).prepare(
            request("kmong", "제목은 합성 기타 레슨입니다."))
        self.assertEqual(result["facts"][0]["origin"]["locator"], "합성 기타 레슨")
        self.assertNotIn("title", result["values"])
        self.assertTrue(any(i["field"] == "/title" and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_ungrounded_candidate_is_never_returned(self):
        result = self.provider([{"field": "/title", "value": "거짓 요금", "quote": "합성 레슨"}]).prepare(
            request("kmong", "합성 레슨"))
        self.assertEqual(result["facts"], [])
        self.assertEqual(result["values"], {})
        self.assertTrue(any(i["field"] == "/title" and i["code"] == "missing" for i in result["issues"]))

    def test_conflicting_source_and_answer_are_preserved(self):
        candidate = {"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"}
        answer = {"answer_id": "answer-1", "field": "/title", "value": "새로운 레슨 제목"}
        result = self.provider([candidate]).prepare(request("kmong", "합성 기타 레슨", [answer]))
        self.assertFalse(result["ready"])
        self.assertEqual({f["value"] for f in result["facts"]}, {"합성 기타 레슨", "새로운 레슨 제목"})
        self.assertTrue(any(i["field"] == "/title" and i["code"] == "conflict" for i in result["issues"]))
        self.assertNotIn("title", result["values"])

    def test_valid_user_answers_for_soomgo_validate_profile(self):
        values = {"category": "midi_mock", "daw": ["logic"], "goals": ["hobby"],
                  "keyboard": "no", "ages": ["20s"], "genders": ["female"],
                  "format": ["individual"], "location_mode": ["studio"]}
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("soomgo", "합성 입력", answers))
        self.assertTrue(result["ready"])
        self.assertEqual(result["values"], values)
        contract.catalog().profile_values("soomgo.service_configuration.mock.v2", result["values"])
        self.assertEqual(len(result["provenance"]), len(values))

    def test_kmong_valid_answers_and_three_package_profile(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        for package in values["packages"]:
            package["amount_vat_included_krw"] = 180000
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("kmong", "합성 입력", answers))
        self.assertTrue(result["ready"])
        self.assertEqual(result["values"], values)
        contract.catalog().profile_values("kmong.service_listing.mock.v2", result["values"])

    def test_kmong_mock_rules_block_unknown_minutes_and_repeated_tier(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values["packages"][0]["minutes_per_session"] = 75
        values["packages"][1]["tier"] = values["packages"][0]["tier"]
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("kmong", "합성 입력", answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == "/packages" and i["code"] == "invalid" for i in result["issues"]))

    def test_kmong_offline_requires_explicit_region(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values.pop("region")
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("kmong", "합성 입력", answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == "/region" and i["code"] == "missing" for i in result["issues"]))

    def test_two_source_price_candidates_keep_both_and_block(self):
        candidates = [{"field": "/packages", "value": 180000, "quote": "180,000원"},
                      {"field": "/packages", "value": 210000, "quote": "210,000원"}]
        result = self.provider(candidates).prepare(request("kmong", "4회 180,000원 혹은 210,000원"))
        self.assertFalse(result["ready"])
        self.assertEqual({f["value"] for f in result["facts"]}, {180000, 210000})
        self.assertTrue(any(i["field"] == "/packages" and i["code"] == "conflict" for i in result["issues"]))
        self.assertNotIn("packages", result["values"])

    def test_missing_vat_does_not_create_packages(self):
        result = self.provider().prepare(request("kmong", "합성 레슨 4회 총액 180,000원"))
        self.assertFalse(result["ready"])
        self.assertNotIn("packages", result["values"])
        self.assertTrue(any(i["field"] == "/packages" and i["code"] == "missing" for i in result["issues"]))

    def test_invalid_user_answers_do_not_mark_ready(self):
        values = {"category": "midi_mock", "daw": ["unknown"], "goals": ["hobby"],
                  "keyboard": "no", "ages": ["20s"], "genders": ["female"],
                  "format": ["individual"], "location_mode": ["studio"]}
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("soomgo", "합성 입력", answers))
        self.assertFalse(result["ready"])
        self.assertEqual((result["issues"][0]["code"], result["issues"][0]["field"]), ("invalid", "/daw"))

    def test_nested_answers_stop_safely(self):
        answer = {"answer_id": "a", "field": "/packages/0/amount_vat_included_krw", "value": 180000}
        result = self.provider().prepare(request("kmong", "합성 입력", [answer]))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == answer["field"] and i["code"] == "unsupported" for i in result["issues"]))

    def test_model_unavailable_is_safe_typed_failure(self):
        with self.assertRaises(PortFailure) as error:
            self.provider(fail=True).prepare(request("kmong", "합성 입력"))
        self.assertEqual(error.exception.error["code"], "MODEL_UNAVAILABLE")
        self.assertNotIn("private provider details", str(error.exception.error))

    def test_untrusted_profile_and_bad_model_response_fail_closed(self):
        altered = request("kmong", "합성 입력")
        altered["profile"]["fields"][0]["requirement"] = "optional"
        with self.assertRaises(PortFailure) as error:
            self.provider().prepare(altered)
        self.assertEqual(error.exception.error["code"], "PROFILE_CHANGED")
        with self.assertRaises(PortFailure) as error:
            self.provider([{"field": "/title", "value": "x"}]).prepare(request("kmong", "x"))
        self.assertEqual(error.exception.error["code"], "RUNTIME_ERROR")

    def test_r03_answers_make_soomgo_ready(self):
        values = {"category": "midi_mock", "daw": ["logic"], "goals": ["hobby"],
                  "keyboard": "no", "ages": ["20s"], "genders": ["female"],
                  "format": ["individual"], "location_mode": ["studio"]}
        with tempfile.TemporaryDirectory() as temp:
            co = Coordinator(Store(Path(temp) / "test.sqlite3"), prep=self.provider())
            source = co.create_source("test-owner", {"raw_text": "합성 입력"})
            view = co.create_registration("test-owner", {"source_id": source["source_id"], "selector": "soomgo"})
            self.assertFalse(view["preparation"]["ready"])
            answers = [{"issue_id": issue["issue_id"], "value": values[issue["field"][1:]]}
                       for issue in view["preparation"]["issues"]]
            revised = co.edit_registration("test-owner", view["registration_id"],
                                           {"expected_revision": view["revision"], "answers": answers})
            self.assertTrue(revised["preparation"]["ready"])
            self.assertEqual(revised["preparation"]["values"], values)
            self.assertEqual(co.get_registration("test-owner", view["registration_id"])["preparation"],
                             revised["preparation"])

    def test_r03_app_persists_model_failure_for_both_profiles(self):
        for platform in ("kmong", "soomgo"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp:
                co = Coordinator(Store(Path(temp) / "test.sqlite3"), prep=self.provider(fail=True))
                source = co.create_source("test-owner", {"raw_text": "합성 입력"})
                view = co.create_registration("test-owner", {"source_id": source["source_id"], "selector": platform})
                self.assertFalse(view["preparation"]["ready"])
                self.assertEqual(view["preparation"]["issues"][0]["code"], "model_unavailable")
                self.assertEqual(co.get_registration("test-owner", view["registration_id"])["preparation"], view["preparation"])
