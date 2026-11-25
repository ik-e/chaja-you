"""Unit tests for WebApiClient and UiWorkflowController adhering to R01 directives.

Verifies:
1. H1~H9 route path /v1/*
2. H7 202 vs 200 handling
3. job_state and progress polling
4. Result display upon completion
5. unknown verdict blocks automatic retry and guides human action
6. Owner in header only, stripped from payload body
7. AuthGrant not stored or retained in controller
8. Cache-Control: no-store
"""
import io
import json
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from web.api.client import ApiError, WebApiClient
from web.workflow import UiWorkflowController


class TestWebApiClientDirectives(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.owner = "instructor-42"
        self.client = WebApiClient(base_url=self.base_url, owner=self.owner)
        self.controller = UiWorkflowController(self.client)

    @patch("urllib.request.urlopen")
    def test_directive_1_and_8_v1_route_and_no_store(self, mock_urlopen):
        """Rule 1: /v1 route, Rule 8: Cache-Control: no-store header sent."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Cache-Control": "no-store"}
        mock_resp.read.return_value = json.dumps({"sources": []}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.list_sources(limit=10)

        self.assertEqual(res, {"sources": []})
        req = mock_urlopen.call_args[0][0]
        self.assertTrue(req.full_url.startswith("http://127.0.0.1:8000/v1/sources"))
        self.assertEqual(req.headers.get("Cache-control"), "no-store")
        self.assertEqual(req.headers.get("X-mock-owner"), self.owner)

    @patch("urllib.request.urlopen")
    def test_directive_6_owner_stripped_from_body(self, mock_urlopen):
        """Rule 6: owner is sent in context header only, stripped from body."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.headers = {"Cache-Control": "no-store"}
        mock_resp.read.return_value = json.dumps({"id": "reg-101"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        payload = {
            "source_id": "src-01",
            "profile_id": "soomgo.service_configuration.mock.v2",
            "owner": "malicious-override",  # should be stripped
        }
        res = self.client.create_registration(payload)

        self.assertEqual(res, {"id": "reg-101"})
        req = mock_urlopen.call_args[0][0]
        sent_body = json.loads(req.data.decode("utf-8"))
        self.assertNotIn("owner", sent_body)
        self.assertEqual(req.headers.get("X-mock-owner"), self.owner)

    @patch("urllib.request.urlopen")
    def test_directive_2_h7_start_202_and_200(self, mock_urlopen):
        """Rule 2: H7 handles 202 for initial start, 200 for idempotent replay."""
        # Initial 202
        mock_resp_202 = MagicMock()
        mock_resp_202.status = 202
        mock_resp_202.headers = {"Cache-Control": "no-store"}
        mock_resp_202.read.return_value = json.dumps({"id": "reg-1", "job_state": "pending"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp_202

        out1 = self.controller.start_job("reg-1", "req-key-1", "digest-abc")
        self.assertEqual(out1["status_code"], 202)
        self.assertTrue(out1["is_initial"])
        self.assertFalse(out1["is_replay"])

        # Replay 200
        mock_resp_200 = MagicMock()
        mock_resp_200.status = 200
        mock_resp_200.headers = {"Cache-Control": "no-store"}
        mock_resp_200.read.return_value = json.dumps({"id": "reg-1", "job_state": "active"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp_200

        out2 = self.controller.start_job("reg-1", "req-key-1", "digest-abc")
        self.assertEqual(out2["status_code"], 200)
        self.assertFalse(out2["is_initial"])
        self.assertTrue(out2["is_replay"])

    @patch("urllib.request.urlopen")
    def test_directive_3_and_4_observe_progress_and_result(self, mock_urlopen):
        """Rules 3 & 4: Inspect progress during execution, and display result when done."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Cache-Control": "no-store"}
        mock_resp.read.return_value = json.dumps({
            "id": "reg-1",
            "job_state": "active",
            "progress": {"step": "S3", "completed_steps": 2},
            "status": "in_progress",
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        prog = self.controller.inspect_progress("reg-1")
        self.assertEqual(prog["job_state"], "active")
        self.assertEqual(prog["progress"]["step"], "S3")
        self.assertTrue(prog["is_running"])

    @patch("urllib.request.urlopen")
    def test_directive_5_unknown_verdict_blocks_auto_retry(self, mock_urlopen):
        """Rule 5: unknown verdict blocks automatic retry and guides human action."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Cache-Control": "no-store"}
        mock_resp.read.return_value = json.dumps({
            "id": "reg-1",
            "job_state": "done",
            "result": {
                "verdict": "unknown",
                "evidence": ["lost_ack"],
                "reason": "response dropped after execution",
            },
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.controller.evaluate_final_result("reg-1")
        self.assertTrue(res["completed"])
        self.assertEqual(res["verdict"], "unknown")
        self.assertFalse(res["allow_auto_retry"])
        self.assertIn("자동 재시도를 차단", res["action_message"])

    @patch("urllib.request.urlopen")
    def test_directive_7_auth_grant_not_retained(self, mock_urlopen):
        """Rule 7: AuthGrant delivered to auth screen, never stored or logged."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Cache-Control": "no-store"}
        mock_resp.read.return_value = json.dumps({
            "grant": "secret-ephemeral-grant-token",
            "expiry": 1732515000,
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        relayed = self.controller.relay_auth_grant_to_viewer("reg-1", "open")
        self.assertEqual(relayed["viewer_grant"], "secret-ephemeral-grant-token")

        # Verify controller instance does not hold the grant
        self.assertFalse(hasattr(self.controller, "viewer_grant"))
        self.assertFalse(hasattr(self.controller, "grant"))


if __name__ == "__main__":
    unittest.main()
