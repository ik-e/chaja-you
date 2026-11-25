"""Unit tests for SoomgoAdapter, S1-S6 operations, and independent readback."""
from pathlib import Path
import unittest

from lesson_registration.platforms.soomgo import (
    SoomgoAdapter,
    create_readback_evidence,
    extract_readback_from_html,
    validate_soomgo_bindings,
)

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "platforms" / "soomgo"


class TestSoomgoAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SoomgoAdapter(fixture_dir=str(FIXTURES_DIR))
        self.valid_snapshot = {
            "category": "midi_mock",
            "daw": ["logic"],
            "goals": ["hobby"],
            "keyboard": "yes",
            "ages": ["20s"],
            "genders": ["female"],
            "format": ["individual"],
            "location_mode": ["studio"],
        }
        self.detail_html_path = FIXTURES_DIR / "service_detail.html"
        self.detail_html = self.detail_html_path.read_text(encoding="utf-8")

    def test_ac1_s1_to_s4_operation_lifecycle(self):
        """r04-soomgo-AC1: Sequential execution of S1-S4 operations with valid bindings."""
        # S1: check
        s1 = self.adapter.execute_step("S1")
        self.assertEqual(s1["status"], "success")

        # S2: select category
        s2 = self.adapter.execute_step("S2", {"category": "midi_mock"})
        self.assertEqual(s2["status"], "success")

        # S3: configure questions
        s3 = self.adapter.execute_step("S3", self.valid_snapshot)
        self.assertEqual(s3["status"], "success")
        self.assertEqual(s3["data"]["fields_configured"], 8)

        # S4: pre-save validation
        s4 = self.adapter.execute_step("S4", {"expected_values": self.valid_snapshot})
        self.assertEqual(s4["status"], "success")

    def test_ac2_single_save_and_independent_readback(self):
        """r04-soomgo-AC2: Single save enforcement and independent readback confirmation."""
        # S5: First save succeeds
        s5_first = self.adapter.execute_step("S5")
        self.assertEqual(s5_first["status"], "success")

        # S5: Second save is strictly blocked (1회 저장 원칙)
        s5_second = self.adapter.execute_step("S5")
        self.assertEqual(s5_second["status"], "failed")
        self.assertEqual(s5_second["error"], "MULTIPLE_SAVES_BLOCKED")

        # S6: Independent readback from actual fixture DOM
        s6 = self.adapter.execute_step(
            "S6",
            {
                "detail_html": self.detail_html,
                "expected_snapshot": self.valid_snapshot,
            },
        )
        self.assertEqual(s6["status"], "success")
        self.assertEqual(s6["verdict"], "confirmed")
        self.assertEqual(s6["config_id"], "cfg-soomgo-midi-99")
        self.assertIn("payload_digest", s6["evidence"])

    def test_ac3_error_and_unknown_handling(self):
        """r04-soomgo-AC3: Handles invalid category, response loss, and readback mismatch."""
        # 1. Invalid category in S2
        with self.assertRaises(ValueError):
            self.adapter.execute_step("S2", {"category": "invalid_piano"})

        # 2. Missing required field in S3
        invalid_fields = dict(self.valid_snapshot)
        del invalid_fields["daw"]
        with self.assertRaises(ValueError):
            self.adapter.execute_step("S3", invalid_fields)

        # 3. Simulated network timeout / response loss in S5 -> yields 'unknown'
        adapter2 = SoomgoAdapter()
        s5_lost = adapter2.execute_step("S5", {"simulate_lost_response": True})
        self.assertEqual(s5_lost["status"], "unknown")
        self.assertEqual(s5_lost["error"], "NETWORK_TIMEOUT")

        # 4. Readback payload mismatch in S6 -> yields 'failed'
        mismatched_snapshot = dict(self.valid_snapshot)
        mismatched_snapshot["goals"] = ["entrance"]  # HTML has 'hobby'
        s6_mismatch = self.adapter.execute_step(
            "S6",
            {
                "detail_html": self.detail_html,
                "expected_snapshot": mismatched_snapshot,
            },
        )
        self.assertEqual(s6_mismatch["status"], "failed")
        self.assertEqual(s6_mismatch["verdict"], "failed")


if __name__ == "__main__":
    unittest.main()
