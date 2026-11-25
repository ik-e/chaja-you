"""Soomgo adapter implementing S1-S6 operations and single-save/readback constraints."""
from typing import Any, Dict, List, Optional

from .observation import create_readback_evidence, extract_readback_from_html
from .operations import STEPS, validate_soomgo_bindings


class SoomgoAdapter:
    """Mock-only platform adapter for Soomgo MIDI lesson configuration."""

    def __init__(self, fixture_dir: Optional[str] = None):
        self.fixture_dir = fixture_dir
        self.save_count = 0
        self.current_step = None
        self.bound_values: Dict[str, Any] = {}
        self.last_evidence: Optional[Dict[str, Any]] = None

    def execute_step(self, step_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if step_id not in STEPS:
            raise ValueError(f"지원하지 않는 숨고 step_id: {step_id}")

        self.current_step = step_id

        if step_id == "S1":
            # Read existing categories
            return {
                "step_id": "S1",
                "status": "success",
                "data": {"account_status": "active", "has_midi": False},
            }

        elif step_id == "S2":
            # Enter category slot
            category = context.get("category", "midi_mock")
            if category != "midi_mock":
                raise ValueError(f"비정상 카테고리 진입 시도: {category}")
            self.bound_values["category"] = category
            return {
                "step_id": "S2",
                "status": "success",
                "data": {"category": category, "slot_ready": True},
            }

        elif step_id == "S3":
            # Configure questions (7 fields)
            validate_soomgo_bindings(context)
            self.bound_values.update(context)
            return {
                "step_id": "S3",
                "status": "success",
                "data": {"fields_configured": len(context)},
            }

        elif step_id == "S4":
            # Pre-save verification against bound snapshot
            expected = context.get("expected_values", self.bound_values)
            validate_soomgo_bindings(expected)
            return {
                "step_id": "S4",
                "status": "success",
                "data": {"matches_expected": True, "field_count": len(expected)},
            }

        elif step_id == "S5":
            # Single save execution constraint (CS-05 / DV-03)
            self.save_count += 1
            if self.save_count > 1:
                return {
                    "step_id": "S5",
                    "status": "failed",
                    "error": "MULTIPLE_SAVES_BLOCKED",
                    "message": f"1회 저장 원칙 위반: 저장 호출 횟수 {self.save_count}",
                }
            # Check for simulated lost response error
            if context.get("simulate_lost_response"):
                return {
                    "step_id": "S5",
                    "status": "unknown",
                    "error": "NETWORK_TIMEOUT",
                    "message": "저장 요청 후 응답이 유실되었습니다.",
                }

            return {
                "step_id": "S5",
                "status": "success",
                "data": {"config_id": "cfg-soomgo-midi-99", "saved": True},
            }

        elif step_id == "S6":
            # Independent readback
            html_content = context.get("detail_html")
            expected_snapshot = context.get("expected_snapshot", self.bound_values)

            if not html_content:
                return {
                    "step_id": "S6",
                    "status": "failed",
                    "error": "READBACK_SOURCE_MISSING",
                    "message": "독립 조회를 위한 상세 HTML 소스가 누락되었습니다.",
                }

            readback = extract_readback_from_html(html_content)
            observed_payload = readback["payload"]
            evidence = create_readback_evidence(
                step_id="S6",
                observed_payload=observed_payload,
                expected_snapshot=expected_snapshot,
            )
            self.last_evidence = evidence

            return {
                "step_id": "S6",
                "status": "success" if evidence["verdict"] == "confirmed" else "failed",
                "config_id": readback["config_id"],
                "evidence": evidence,
                "verdict": evidence["verdict"],
            }
