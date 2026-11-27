"""Independent synthetic tests of the tentative I2 provider, without a real model."""
import copy
import dev
import tempfile
import unittest
from pathlib import Path

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
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

    def test_verbatim_source_text_is_retained_for_final_review(self):
        result = self.provider([{"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"}]).prepare(
            request("kmong", "제목은 합성 기타 레슨입니다."))
        self.assertEqual(result["facts"][0]["origin"]["locator"], "합성 기타 레슨")
        self.assertEqual(result["values"]["title"], "합성 기타 레슨")
        self.assertTrue(any(p["field"] == "/title" and p["kind"] == "direct" for p in result["provenance"]))
        self.assertFalse(any(i["field"] == "/title" for i in result["issues"]))

    def test_source_excerpt_with_extra_context_requires_confirmation(self):
        candidate = {"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨과 다른 레슨을 제공합니다"}
        result = self.provider([candidate]).prepare(request("kmong", candidate["quote"]))
        self.assertNotIn("title", result["values"])
        self.assertTrue(any(i["field"] == "/title" and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_model_top_level_key_without_slash_is_canonicalized(self):
        candidate = {"field": "title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"}
        result = self.provider([candidate]).prepare(request("kmong", "제목은 합성 기타 레슨입니다."))
        self.assertEqual(result["values"]["title"], "합성 기타 레슨")
        self.assertEqual(result["facts"][0]["path"], "/title")

    def test_unlabelled_source_text_does_not_become_a_title(self):
        candidate = {"field": "/title", "value": "합성 레슨 4회", "quote": "합성 레슨 4회"}
        result = self.provider([candidate]).prepare(request("kmong", "합성 레슨 4회. 가격은 상담 후 결정합니다."))
        self.assertNotIn("title", result["values"])
        self.assertTrue(any(i["field"] == "/title" and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_unknown_model_field_blocks_without_discarding_known_fact_or_exposing_field(self):
        candidates = [{"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"},
                      {"field": "/private-model-output", "value": "합성", "quote": "합성"}]
        result = self.provider(candidates).prepare(request("kmong", "제목은 합성 기타 레슨입니다."))
        self.assertEqual(result["values"]["title"], "합성 기타 레슨")
        self.assertTrue(any(i["field"] == "/" and i["code"] == "unsupported" and i["blocking"]
                            for i in result["issues"]))
        self.assertNotIn("private-model-output", repr(result))
        self.assertFalse(result["ready"])

    def test_numeric_evidence_with_wrong_or_missing_unit_is_not_promoted(self):
        cases = [('/packages/0/minutes_per_session', 90, '90회'),
                 ('/packages/0/sessions', 4, '4일'),
                 ('/packages/0/amount_vat_included_krw', 180000, '180000분'),
                 ('/packages/0/revision_count', 4, '수업 4회')]
        for field, value, quote in cases:
            with self.subTest(field=field):
                result = self.provider([{'field': field, 'value': value, 'quote': quote}]).prepare(
                    request('kmong', quote))
                self.assertFalse(result['ready'])
                self.assertFalse(any(f['path'] == field for f in result['facts']))
                self.assertTrue(any(i['field'] == field and i['code'] == 'rule_unverified' for i in result['issues']))

    def test_title_requires_explicit_adjacent_label_across_text_variants(self):
        for text, expected in [('제목: 합성 기타 레슨', True), ('제목은 합성 기타 레슨입니다.', True),
                               ('설명: 합성 기타 레슨', False), ('제목은 다른 내용. 합성 기타 레슨', False)]:
            with self.subTest(text=text):
                candidate = {'field': '/title', 'value': '합성 기타 레슨', 'quote': '합성 기타 레슨'}
                result = self.provider([candidate]).prepare(request('kmong', text))
                self.assertEqual('title' in result['values'], expected)
                if not expected:
                    self.assertTrue(any(i['field'] == '/title' and i['blocking'] for i in result['issues']))

    def test_numeric_evidence_preserves_unit_and_exact_number(self):
        candidate = {'field': '/packages/0/minutes_per_session', 'value': 90, 'quote': '190분 또는 90회'}
        result = self.provider([candidate]).prepare(request('kmong', candidate['quote']))
        self.assertFalse(any(f['path'] == candidate['field'] for f in result['facts']))
        self.assertTrue(any(i['field'] == candidate['field'] and i['code'] == 'rule_unverified'
                            for i in result['issues']))

    def test_vat_exclusion_without_packages_cannot_become_ready(self):
        result = self.provider().prepare(request('kmong', '첫 수업 180000원, 부가세 별도'))
        self.assertFalse(result['ready'])
        self.assertNotIn('packages', result['values'])
        self.assertTrue(any(i['field'] == '/packages' and i['blocking'] for i in result['issues']))

    def test_explicit_title_label_does_not_require_extra_confirmation(self):
        candidate = {"field": "/title", "value": "합성 기타 레슨", "quote": "제목은 합성 기타 레슨입니다."}
        result = self.provider([candidate]).prepare(request("kmong", candidate["quote"]))
        self.assertEqual(result["values"]["title"], "합성 기타 레슨")

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
        self.assertEqual(result["issues"], [])
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

    def test_nested_price_conflict_is_grounded_and_keeps_both_values(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values["packages"][0]["amount_vat_included_krw"] = 210000
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        candidate = {"field": "/packages/0/amount_vat_included_krw", "value": 180000, "quote": "180,000원"}
        result = self.provider([candidate]).prepare(request("kmong", "첫 번째 패키지 180,000원", answers))
        self.assertFalse(result["ready"])
        self.assertEqual(result["values"]["packages"][0]["amount_vat_included_krw"], 210000)
        self.assertTrue(any(f["path"] == candidate["field"] and f["value"] == 180000 for f in result["facts"]))
        self.assertTrue(any(i["field"] == candidate["field"] and i["code"] == "conflict" for i in result["issues"]))

    def test_matching_price_with_explicit_vat_inclusive_answer_is_ready(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values["packages"][0]["amount_vat_included_krw"] = 180000
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        candidate = {"field": "/packages/0/amount_vat_included_krw", "value": 180000, "quote": "180,000원"}
        result = self.provider([candidate]).prepare(request("kmong", "첫 패키지 180,000원", answers))
        self.assertTrue(result["ready"])
        self.assertFalse(any(i["field"] == candidate["field"] and i["code"] == "conflict" for i in result["issues"]))
        self.assertEqual(result["issues"], [])

    def test_nested_price_with_no_parent_requests_confirmation(self):
        candidate = {"field": "/packages/0/amount_vat_included_krw", "value": 180000, "quote": "180,000원"}
        result = self.provider([candidate]).prepare(request("kmong", "첫 번째 패키지 180,000원"))
        self.assertFalse(result["ready"])
        self.assertNotIn("packages", result["values"])
        self.assertTrue(any(i["field"] == candidate["field"] and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_vat_excluded_source_conflicts_with_vat_inclusive_answer(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values["packages"][0]["amount_vat_included_krw"] = 180000
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        field = "/packages/0/amount_vat_included_krw"
        for quote in ("180,000원 VAT 별도", "180,000원 부가세 불포함", "180,000원 별도 부가가치세"):
            with self.subTest(quote=quote):
                result = self.provider([{"field": field, "value": 180000, "quote": quote}]).prepare(
                    request("kmong", quote, answers))
                self.assertFalse(result["ready"])
                self.assertTrue(any(i["field"] == field and i["code"] == "conflict" for i in result["issues"]))

    def test_excluded_price_alias_never_becomes_inclusive_without_conflict(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        values["packages"][0]["amount_vat_included_krw"] = 180000
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        candidate = {"field": "/packages/0/amount_vat_excluded_krw", "value": 180000,
                     "quote": "180000원 VAT 별도"}
        result = self.provider([candidate]).prepare(request("kmong", candidate["quote"], answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == "/packages/0/amount_vat_included_krw" and i["code"] == "conflict"
                            for i in result["issues"]))

    def test_unqualified_price_alias_cannot_create_a_package(self):
        candidate = {"field": "/packages/0/price", "value": 180000, "quote": "180000원"}
        result = self.provider([candidate]).prepare(request("kmong", candidate["quote"]))
        self.assertFalse(result["ready"])
        self.assertNotIn("packages", result["values"])

    def test_source_vat_exclusion_is_blocked_when_model_omits_it(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("kmong", "첫 패키지 180000원 VAT 별도", answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == "/packages" and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_source_price_alternatives_block_when_model_omits_them(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        result = self.provider().prepare(request("kmong", "180000원 또는 210000원", answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == "/packages" and i["code"] == "rule_unverified" for i in result["issues"]))

    def test_two_nested_source_prices_block_and_preserve_evidence(self):
        field = "/packages/0/amount_vat_included_krw"
        candidates = [{"field": field, "value": 180000, "quote": "180,000원"},
                      {"field": field, "value": 210000, "quote": "210,000원"}]
        result = self.provider(candidates).prepare(request("kmong", "첫 패키지 180,000원 또는 210,000원"))
        self.assertEqual({f["value"] for f in result["facts"]}, {180000, 210000})
        self.assertTrue(any(i["field"] == field and i["code"] == "conflict" for i in result["issues"]))
        self.assertFalse(result["ready"])

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

    def test_r03_nested_edit_reuses_parent_answer_and_preserves_other_packages(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        with tempfile.TemporaryDirectory() as temp:
            co = Coordinator(Store(Path(temp) / "test.sqlite3"), prep=self.provider())
            source = co.create_source("test-owner", {"raw_text": "합성 입력"})
            view = co.create_registration("test-owner", {"source_id": source["source_id"], "selector": "kmong"})
            answers = [{"issue_id": issue["issue_id"], "value": values[issue["field"][1:]]}
                       for issue in view["preparation"]["issues"]]
            revised = co.edit_registration("test-owner", view["registration_id"],
                                           {"expected_revision": view["revision"], "answers": answers})
            updated = co.edit_registration("test-owner", view["registration_id"], {
                "expected_revision": revised["revision"],
                "corrections": [{"field": "/packages/0/amount_vat_included_krw", "value": 190000}]})
            self.assertTrue(updated["preparation"]["ready"])
            packages = updated["preparation"]["values"]["packages"]
            self.assertEqual(packages[0]["amount_vat_included_krw"], 190000)
            original_first = copy.deepcopy(values["packages"][0])
            original_first["amount_vat_included_krw"] = 190000
            self.assertEqual(packages[0], original_first)
            self.assertEqual(packages[1:], values["packages"][1:])
            self.assertEqual(revised["preparation"]["values"]["packages"], values["packages"])

    def test_nested_answers_stop_safely(self):
        answer = {"answer_id": "a", "field": "/packages/0/amount_vat_included_krw", "value": 180000}
        result = self.provider().prepare(request("kmong", "합성 입력", [answer]))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == answer["field"] and i["code"] == "unsupported" for i in result["issues"]))

    def test_nested_answer_with_parent_preserves_other_packages_and_input(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        before = copy.deepcopy(values)
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        field = "/packages/0/amount_vat_included_krw"
        answers.append({"answer_id": "correction", "field": field, "value": 190000})
        result = self.provider().prepare(request("kmong", "합성 입력", answers))
        self.assertTrue(result["ready"])
        self.assertEqual(result["values"]["packages"][0]["amount_vat_included_krw"], 190000)
        self.assertEqual(result["values"]["packages"][1:], before["packages"][1:])
        self.assertEqual(values, before)
        self.assertTrue(any(p["field"] == field and p["kind"] == "user_choice" for p in result["provenance"]))

    def test_nested_answer_against_source_is_blocked_even_with_parent(self):
        values = copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I2"]["output"]["values"])
        answers = [{"answer_id": "answer-" + key, "field": "/" + key, "value": value}
                   for key, value in values.items()]
        field = "/packages/0/amount_vat_included_krw"
        answers.append({"answer_id": "correction", "field": field, "value": 190000})
        candidate = {"field": field, "value": 180000, "quote": "180,000원"}
        result = self.provider([candidate]).prepare(request("kmong", "첫 패키지 180,000원", answers))
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["field"] == field and i["code"] == "conflict" for i in result["issues"]))

    def test_r03_direct_title_and_fact_conflict_preserve_previous_revision(self):
        candidate = {"field": "/title", "value": "합성 기타 레슨", "quote": "합성 기타 레슨"}
        with tempfile.TemporaryDirectory() as temp:
            co = Coordinator(Store(Path(temp) / "test.sqlite3"), prep=self.provider([candidate]))
            source = co.create_source("test-owner", {"raw_text": "제목은 합성 기타 레슨입니다."})
            view = co.create_registration("test-owner", {"source_id": source["source_id"], "selector": "kmong"})
            self.assertEqual(view["preparation"]["values"]["title"], "합성 기타 레슨")
            self.assertFalse(any(i["field"] == "/title" for i in view["preparation"]["issues"]))
            with self.assertRaises(AppError) as error:
                co.edit_registration("test-owner", view["registration_id"], {
                    "expected_revision": view["revision"],
                    "corrections": [{"field": "/title", "value": "서로 다른 제목"}]})
            self.assertEqual(error.exception.code, "FACT_CONFLICT")
            self.assertEqual(co.get_registration("test-owner", view["registration_id"])["revision"], view["revision"])

    def test_model_enum_candidate_does_not_bypass_selection(self):
        candidate = {"field": "/delivery", "value": "offline", "quote": "offline"}
        result = self.provider([candidate]).prepare(request("kmong", "합성 레슨 offline"))
        self.assertNotIn("delivery", result["values"])
        self.assertTrue(any(i["field"] == "/delivery" and i["code"] == "rule_unverified" for i in result["issues"]))

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
