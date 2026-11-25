"""S0: pinned contract loading, $defs validator, error mapping and port protocols."""

import copy
import json
import unittest

from lesson_registration.app import contract
from lesson_registration.app.errors import STATUS, AppError
from lesson_registration.app.ids import digest
from lesson_registration.app.ports import Clock, ExecPort, PrepPort

from support import PLATFORMS, FixedClock, ReplayExec, ReplayPrep, ScriptedExec, replay_cases


class PinnedContracts(unittest.TestCase):
    def test_all_pins_load_with_matching_blob(self):
        for name in (
            "data-schema-v4.1.json",
            "platform-profiles-v2.json",
            "common-integration-v1.json",
            "trace-index-v0.9.json",
        ):
            self.assertIsInstance(contract.load(name), dict, name)

    def test_schema_uses_only_supported_keywords(self):
        # Validating every replay case walks the schema; an unsupported keyword raises RuntimeError.
        for platform in PLATFORMS:
            for row in replay_cases(platform).values():
                for kind in ("input", "output"):
                    if row.get(f"{kind}_type"):
                        contract.is_valid(row[f"{kind}_type"], row[kind])

    def test_error_status_table_matches_contract(self):
        http = contract.load("common-integration-v1.json")["http"]
        expected = {code: int(s) for s, codes in http["status_codes"].items() for code in codes}
        self.assertEqual(STATUS, expected)
        for code in http["result_only_codes"]:
            self.assertNotIn(code, STATUS)


class ReplayFixturesValidate(unittest.TestCase):
    def test_every_typed_replay_case_matches_schema(self):
        for platform in PLATFORMS:
            for case, row in replay_cases(platform).items():
                for kind in ("input", "output"):
                    def_name = row.get(f"{kind}_type")
                    if def_name:
                        with self.subTest(platform=platform, case=case, kind=kind):
                            contract.validate(def_name, row[kind])


class ValidatorRejects(unittest.TestCase):
    def setUp(self):
        self.good = copy.deepcopy(replay_cases("kmong")["I2"]["input"]["source"])
        contract.validate("SourceView", self.good)

    def assertInvalid(self, def_name, value):
        with self.assertRaises(AppError) as ctx:
            contract.validate(def_name, value)
        self.assertEqual(ctx.exception.code, "INVALID_REQUEST")
        self.assertEqual(ctx.exception.status, 400)

    def test_unknown_key(self):
        self.good["owner_ref"] = "someone"
        self.assertInvalid("SourceView", self.good)

    def test_missing_required(self):
        del self.good["raw_text"]
        self.assertInvalid("SourceView", self.good)

    def test_enum_violation(self):
        self.good["asset_refs"][0]["mime"] = "image/gif"
        self.assertInvalid("SourceView", self.good)

    def test_bool_is_not_integer(self):
        self.good["asset_refs"][0]["bytes"] = True
        self.assertInvalid("SourceView", self.good)

    def test_digest_pattern(self):
        self.good["asset_refs"][0]["digest"] = "XYZ"
        self.assertInvalid("SourceView", self.good)

    def test_timestamp_format(self):
        self.good["created_at"] = "yesterday"
        self.assertInvalid("SourceView", self.good)

    def test_environment_must_be_mock(self):
        ref = copy.deepcopy(replay_cases("kmong")["I2"]["input"]["profile"]["ref"])
        contract.validate("ProfileRef", ref)
        ref["environment"] = "live"
        self.assertInvalid("ProfileRef", ref)

    def test_one_of_auth_command(self):
        contract.validate("AuthCommand", {"action": "open", "expected_revision": 1})
        self.assertInvalid("AuthCommand", {"action": "finish", "expected_revision": 1})
        self.assertInvalid("AuthCommand", {"action": "delete", "expected_revision": 1})

    def test_start_input_requires_literal_true(self):
        ok = {"expected_revision": 3, "review_digest": "a" * 64, "approved": True, "request_key": "k1"}
        contract.validate("StartInput", ok)
        self.assertInvalid("StartInput", {**ok, "approved": False})


class ErrorsAndIds(unittest.TestCase):
    def test_error_view_is_schema_valid(self):
        err = AppError("STALE_REVISION", "revision changed", current_revision=4)
        self.assertEqual(err.status, 409)
        contract.validate("Error", err.to_view())

    def test_unknown_error_code_rejected(self):
        with self.assertRaises(ValueError):
            AppError("SOMETHING_ELSE", "x")

    def test_digest_is_order_independent(self):
        self.assertEqual(digest({"a": 1, "b": [1, 2]}), digest({"b": [1, 2], "a": 1}))
        self.assertRegex(digest({"x": "가"}), r"^[a-f0-9]{64}$")


class Ports(unittest.TestCase):
    def test_fakes_satisfy_protocols(self):
        self.assertIsInstance(ReplayPrep("kmong"), PrepPort)
        self.assertIsInstance(ReplayExec("kmong"), ExecPort)
        self.assertIsInstance(ScriptedExec(), ExecPort)
        self.assertIsInstance(FixedClock(), Clock)

    def test_replay_prep_returns_valid_preparation(self):
        for platform in PLATFORMS:
            for case in ("I2", "I2-missing"):
                inp = replay_cases(platform)[case]["input"]
                out = ReplayPrep(platform, case).prepare(json.loads(json.dumps(inp)))
                contract.validate("Preparation", out)

    def test_replay_rejects_non_exact_input(self):
        inp = copy.deepcopy(replay_cases("kmong")["I2"]["input"])
        inp["answers"] = [{"answer_id": "x", "field": "title", "value": "y"}]
        with self.assertRaises(ValueError):
            ReplayPrep("kmong").prepare(inp)

    def test_missing_case_keeps_ready_false(self):
        for platform in PLATFORMS:
            out = replay_cases(platform)["I2-missing"]["output"]
            self.assertFalse(out["ready"])
            self.assertTrue(any(i["blocking"] for i in out["issues"]))


if __name__ == "__main__":
    unittest.main()
