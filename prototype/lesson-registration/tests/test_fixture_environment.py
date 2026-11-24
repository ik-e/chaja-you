"""Smoke tests for the synthetic fixture and local MVP development environment.

These tests do NOT demonstrate F1/F2/F3 implementation, an E2E result,
or authorization to use any external platform.
"""
from __future__ import annotations

import json
from pathlib import Path


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic-lesson-001.json"


def test_fixture_is_synthetic_and_mock_only() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert data["kind"] == "synthetic_test_fixture"
    assert data["environment"] == "mock"
    assert data["requires_real_identity"] is False
    assert data["provenance"]["contains_real_person_data"] is False
    assert data["status"] == "proposed_not_executed"


def test_fixture_has_minimum_non_sensitive_lesson_fields() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    facts = data["facts"]
    assert facts["sessions_per_month"] > 0
    assert facts["minutes_per_session"] > 0
    assert facts["price_krw_per_month"] > 0
    assert facts["additional_costs"] == "unconfirmed"
    assert data["media_refs"] == []
    assert data["expected_behavior"]["on_live_submission"] == "block"
    assert not any(
        key in data for key in ("password", "token", "cookies", "otp", "session")
    )
