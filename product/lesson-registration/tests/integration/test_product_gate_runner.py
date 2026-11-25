"""R01 acceptance runner regressions; no gate is passed by these unit tests."""
import unittest
from evidence.product_gate import Case, gate_spec, verdict_for, build_report


class GateRunnerTests(unittest.TestCase):
    def test_pin_inventory_and_no_accidental_completion(self):
        _, gates = gate_spec()
        self.assertEqual(len(gates), 22)
        report = build_report()
        self.assertEqual(report["counts"], {"pass": 0, "fail": 0, "incomplete": 0, "not_run": 22})
        self.assertFalse(report["complete"])
        self.assertTrue(next(g for g in gates if g["id"] == "T5-08")["actual_model_required"])

    def test_verdict_requires_full_assertion_inventory_and_observations(self):
        case = Case(("a",), lambda _: {})
        self.assertEqual(verdict_for(case, {"verdict": "pass"}), "incomplete")
        good = {"checks": [{"id": "a", "passed": True, "expected": 1, "observed": 1}],
                "observations": {"input_candidate": {"case": "synthetic"},
                                 "response_state_mutations": {"external_mutation_count": 0},
                                 "trusted_evidence_or_absence": {"absence": True}}}
        self.assertEqual(verdict_for(case, good), "pass")
        good["checks"][0]["passed"] = False
        good.pop("observations")
        self.assertEqual(verdict_for(case, good), "fail")

    def test_empty_and_non_boolean_checks_rejected(self):
        case = Case(("a",), lambda _: {})
        self.assertEqual(verdict_for(case, {"checks": []}), "incomplete")
        self.assertEqual(verdict_for(case, {"checks": [{"id": "a", "passed": 1,
                                                         "expected": 1, "observed": 1}]}), "incomplete")

    def test_unknown_gate_selection_fails(self):
        with self.assertRaises(ValueError):
            build_report(selected="UNKNOWN")
