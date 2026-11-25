"""Bridge between SoomgoAdapter and StoreGateway / Runtime pipeline."""
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from .adapter import SoomgoAdapter
from .observation import render_synthetic_detail_html

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "platforms" / "soomgo"


class SoomgoGatewayRunner:
    """Executes SoomgoAdapter operations under the supervision of StoreGateway."""

    def __init__(self, adapter: Optional[SoomgoAdapter] = None):
        self.adapter = adapter or SoomgoAdapter(fixture_dir=str(FIXTURES_DIR))
        self.detail_html_path = FIXTURES_DIR / "service_detail.html"

    def run_registration(self, gateway: Any, context: Any, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Runs S1~S6 steps through Gateway admission and observation."""
        rid = scope["registration_id"]
        target = scope["target"]
        values = scope.get("values", {})
        now = "2026-11-25T01:00:00Z"

        if self.detail_html_path.exists():
            detail_html = self.detail_html_path.read_text(encoding="utf-8")
        else:
            detail_html = render_synthetic_detail_html(values)

        observations = []
        all_evidence = []

        for op in gateway.expected_operations(context):
            step_id = op["step_id"]

            # 1. Admit step via Gateway
            permit = gateway.admit(context, op)

            # 2. Execute step in SoomgoAdapter
            step_ctx = dict(values)
            step_ctx["expected_values"] = values
            step_ctx["expected_snapshot"] = values
            step_ctx["detail_html"] = detail_html

            adapter_res = self.adapter.execute_step(step_id, step_ctx)

            if adapter_res.get("status") == "failed":
                gateway.fence(rid, {"error": adapter_res.get("error", "ADAPTER_FAILED"), "step_id": step_id})
                return {"success": False, "failed_step": step_id, "error": adapter_res}

            # 3. Create Gateway Observation and Evidence strictly adhering to data-schema-v4.1
            ev_id = f"ev-{rid}-{step_id}"
            evidence_list = []
            method = "independent_readback" if step_id == "S6" else "runtime_observation"

            if step_id == "S6" and "evidence" in adapter_res:
                raw_ev = adapter_res["evidence"]
                goal_ev = {
                    "evidence_id": f"ev-{rid}-goal",
                    "registration_id": rid,
                    "target": target,
                    "kind": "goal",
                    "method": "independent_readback",
                    "observed_at": now,
                    "environment": "mock",
                    "operation_id": op["operation_id"],
                    "observed_state": "mock_saved",
                    "payload_digest": raw_ev.get("payload_digest"),
                    "asset_digests": [],
                }
                evidence_list.append(goal_ev)

            step_ev = {
                "evidence_id": ev_id,
                "registration_id": rid,
                "target": target,
                "kind": "operation",
                "method": method,
                "observed_at": now,
                "environment": "mock",
                "operation_id": op["operation_id"],
            }
            evidence_list.append(step_ev)

            obs = {
                "operation_id": op["operation_id"],
                "step_id": step_id,
                "target": target,
                "method": method,
                "verdict": "confirmed",
                "evidence_refs": [e["evidence_id"] for e in evidence_list],
                "observed_at": now,
            }

            gateway.record_observation(context, obs, evidence_list)
            observations.append(obs)
            all_evidence.extend(evidence_list)

        return {
            "success": True,
            "observations": observations,
            "evidence": all_evidence,
        }
