"""UI Workflow Controller enforcing R01 team leader directive rules."""
from typing import Any, Dict, Optional, Tuple

from web.api.client import WebApiClient


class UiWorkflowController:
    """Manages UI transition states, viewer mounting flow, and result evaluation."""

    def __init__(self, client: WebApiClient):
        self.client = client
        # Rule 7: Do NOT keep AuthGrant in any state attributes

    def start_job(self, reg_id: str, request_key: str, snapshot_digest: str) -> Dict[str, Any]:
        """Rule 2: H7 handles 202 (initial) and 200 (idempotent replay)."""
        payload = {
            "request_key": request_key,
            "snapshot_digest": snapshot_digest,
        }
        status, data = self.client.start(reg_id, payload)
        return {
            "status_code": status,
            "is_initial": (status == 202),
            "is_replay": (status == 200),
            "registration": data,
        }

    def inspect_progress(self, reg_id: str) -> Dict[str, Any]:
        """Rule 3: Polls job_state and progress during execution."""
        reg = self.client.get_registration(reg_id)
        return {
            "job_state": reg.get("job_state"),
            "progress": reg.get("progress"),
            "status": reg.get("status"),
            "is_running": reg.get("job_state") in ("pending", "active", "stopping"),
        }

    def evaluate_final_result(self, reg_id: str) -> Dict[str, Any]:
        """Rules 4 & 5: Shows stored result, strictly blocks auto-retry on unknown verdict."""
        reg = self.client.get_registration(reg_id)
        result = reg.get("result")

        if not result:
            return {
                "completed": False,
                "job_state": reg.get("job_state"),
                "message": "작업이 아직 완료되지 않았습니다.",
            }

        verdict = result.get("verdict", "unknown")

        if verdict == "unknown":
            # Rule 5: Strictly block automatic retry, guide human action
            return {
                "completed": True,
                "verdict": "unknown",
                "allow_auto_retry": False,
                "action_message": "등록 결과가 불확실(unknown)합니다. 중복 등록 방지를 위해 자동 재시도를 차단합니다. 플랫폼 관리자 페이지에서 직접 확인해 주세요.",
                "evidence": result.get("evidence", []),
                "result": result,
            }
        elif verdict == "confirmed":
            return {
                "completed": True,
                "verdict": "confirmed",
                "allow_auto_retry": False,
                "action_message": "모의 서비스 설정 등록이 성공적으로 완료되었습니다.",
                "evidence": result.get("evidence", []),
                "result": result,
            }
        else:  # failed / stopped
            return {
                "completed": True,
                "verdict": "failed",
                "allow_auto_retry": False,
                "action_message": "등록 처리가 실패하였습니다. 오류 사유를 확인한 후 필요한 경우 수동으로 재진행하십시오.",
                "error": result.get("error"),
                "result": result,
            }

    def relay_auth_grant_to_viewer(self, reg_id: str, auth_command: str = "open") -> Dict[str, Any]:
        """Rule 7: AuthGrant delivered only to auth screen, never persisted in this controller."""
        payload = {"command": auth_command}
        auth_resp = self.client.authenticate(reg_id, payload)
        grant = auth_resp.get("grant")
        # Return grant to caller (UI viewer mount) without retaining it in self
        return {
            "reg_id": reg_id,
            "viewer_grant": grant,
            "expiry": auth_resp.get("expiry"),
        }
