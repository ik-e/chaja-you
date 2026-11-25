"""Readback parser and evidence generation for Soomgo service configuration."""
import hashlib
from html.parser import HTMLParser
import json
import time
from typing import Any, Dict, List, Optional


class SoomgoDetailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.extracted_data: Dict[str, Any] = {}
        self.config_id: Optional[str] = None
        self._current_tag = None
        self._current_attrs = {}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "div" and attr_dict.get("id") == "service-summary-card":
            self.config_id = attr_dict.get("data-config-id")

        if tag == "span" and "data-key" in attr_dict:
            key = attr_dict["data-key"]
            if "data-values" in attr_dict:
                self.extracted_data[key] = [v.strip() for v in attr_dict["data-values"].split(",")]
            elif "data-value" in attr_dict:
                self.extracted_data[key] = attr_dict["data-value"]
            else:
                self._current_tag = key
                self._current_attrs = attr_dict

    def handle_data(self, data):
        if self._current_tag:
            self.extracted_data[self._current_tag] = data.strip()
            self._current_tag = None


def compute_payload_digest(payload: Dict[str, Any]) -> str:
    """Computes a deterministic SHA256 digest of normalized payload (pure 64-char hex)."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def extract_readback_from_html(html_content: str) -> Dict[str, Any]:
    parser = SoomgoDetailParser()
    parser.feed(html_content)
    return {
        "config_id": parser.config_id,
        "payload": parser.extracted_data,
    }


def render_synthetic_detail_html(values: Dict[str, Any], config_id: str = "cfg-soomgo-midi-99") -> str:
    """Helper to dynamically generate readback DOM HTML matching exact values."""
    daw_str = ",".join(values.get("daw", []))
    goals_str = ",".join(values.get("goals", []))
    ages_str = ",".join(values.get("ages", []))
    genders_str = ",".join(values.get("genders", []))
    format_str = ",".join(values.get("format", []))
    loc_str = ",".join(values.get("location_mode", []))
    keyboard_val = values.get("keyboard", "yes")

    return f"""<!DOCTYPE html>
<html>
<body>
  <div id="service-summary-card" data-config-id="{config_id}">
    <span data-key="category">{values.get('category', 'midi_mock')}</span>
    <span data-key="daw" data-values="{daw_str}"></span>
    <span data-key="goals" data-values="{goals_str}"></span>
    <span data-key="keyboard" data-value="{keyboard_val}"></span>
    <span data-key="ages" data-values="{ages_str}"></span>
    <span data-key="genders" data-values="{genders_str}"></span>
    <span data-key="format" data-values="{format_str}"></span>
    <span data-key="location_mode" data-values="{loc_str}"></span>
  </div>
</body>
</html>"""


def create_readback_evidence(
    step_id: str,
    observed_payload: Dict[str, Any],
    expected_snapshot: Dict[str, Any],
    evidence_id: str = "EV-SOOMGO-READBACK-001",
) -> Dict[str, Any]:
    """Generates an EvidenceRecord by comparing observed readback with expected snapshot."""
    observed_digest = compute_payload_digest(observed_payload)
    expected_digest = compute_payload_digest(expected_snapshot)

    verdict = "confirmed" if observed_digest == expected_digest else "failed"

    return {
        "id": evidence_id,
        "kind": "readback_observation",
        "step_id": step_id,
        "timestamp": int(time.time()),
        "observed_payload": observed_payload,
        "payload_digest": observed_digest,
        "expected_digest": expected_digest,
        "verdict": verdict,
    }
