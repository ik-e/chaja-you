"""Integration tests verifying SoomgoAdapter injection into Coordinator & StoreGateway."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

# Ensure app support helpers are importable
APP_MODULES_PATH = Path(__file__).resolve().parents[1] / "app"
if str(APP_MODULES_PATH) not in sys.path:
    sys.path.insert(0, str(APP_MODULES_PATH))

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.store import Store
from lesson_registration.platforms.soomgo import SoomgoAdapter, SoomgoGatewayRunner
from support import FakeRuntime, SchemaPrep, TickClock, mock_image, temp_db

OWNER = "instructor-soomgo"


class TestSoomgoGatewayIntegration(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.store = Store(self.path)
        self.rt = FakeRuntime("soomgo")
        self.clock = TickClock()
        self.co = Coordinator(self.store, prep=SchemaPrep("soomgo"), exec_port=self.rt, clock=self.clock)
        self.gateway = StoreGateway(self.store, clock=TickClock(500))
        self.runner = SoomgoGatewayRunner()

    def _setup_active_registration(self) -> str:
        """Sets up an accepted registration in SQLite store via Coordinator."""
        src = self.co.create_source(
            OWNER,
            {"raw_text": "숨고 MIDI 레슨 원본", "new_assets": [{"part_name": "img", "rights_confirmed": True}]},
            {"img": mock_image()},
        )
        reg = self.co.create_registration(OWNER, {"source_id": src["source_id"], "selector": "soomgo"})
        rid = reg["registration_id"]

        # Authenticate: open -> finish
        auth_open = self.co.authenticate(OWNER, rid, {"action": "open", "expected_revision": reg["revision"]})
        rev_after_open = auth_open["registration"]["revision"]
        auth_finish = self.co.authenticate(
            OWNER,
            rid,
            {"action": "finish", "expected_revision": rev_after_open, "generation": 1},
        )
        v = auth_finish["registration"]

        # Start job (202 Accepted)
        start_body = {
            "expected_revision": v["revision"],
            "review_digest": v["review"]["digest"],
            "approved": True,
            "request_key": f"key-{rid}",
        }
        status, _ = self.co.start(OWNER, rid, start_body)
        self.assertEqual(status, 202)
        return rid

    def test_soomgo_adapter_gateway_execution(self):
        """Verifies SoomgoAdapter runs under StoreGateway supervision and commits valid observations."""
        rid = self._setup_active_registration()
        ctx = self.gateway.acquire_context(rid)
        job = self.gateway._scope_profile(rid)
        scope = job[0]

        # Execute all S1~S6 operations via SoomgoGatewayRunner
        res = self.runner.run_registration(self.gateway, ctx, scope)

        self.assertTrue(res["success"])
        self.assertEqual(len(res["observations"]), 6)
        self.assertEqual(len(res["evidence"]), 7)

        # S6 Goal readback evidence check
        goal_ev = next(e for e in res["evidence"] if e["kind"] == "goal")
        self.assertEqual(goal_ev["observed_state"], "mock_saved")
        self.assertEqual(goal_ev["method"], "independent_readback")

    def test_unadmitted_operation_rejected_by_gateway(self):
        """Verifies StoreGateway rejects steps not defined in soomgo profile."""
        rid = self._setup_active_registration()
        ctx = self.gateway.acquire_context(rid)

        invalid_op = {
            "operation_id": f"{rid}:S99_unsupported",
            "step_id": "S99_unsupported",
            "action_key": "unsupported",
            "effect_class": "potential_effect",
            "binding_digest": "sha256:dummy",
        }

        with self.assertRaises(Exception):
            self.gateway.admit(ctx, invalid_op)


if __name__ == "__main__":
    unittest.main()
