"""Alignment with the approved common implementation binding (contracts/, IB-01..05).

- Provider objects match contracts.interfaces Protocol method names/arity.
- Coordinator accepts an explicit Providers bundle (IB-05) and maps PortFailure safely.
- STORE capabilities expose CoordinatorStore / GatewayStore shapes (IB-03).
- Validation itself is the shared SchemaCatalog (test_s0); no second validator to compare.
"""

import inspect
import unittest

from contracts import interfaces as I
from contracts.interfaces import PortFailure, Providers

from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.app.result import ResultEvaluator
from lesson_registration.app.store import Store
from lesson_registration.app.store.coordinator_store import SqliteCoordinatorStore

from support import FakeRuntime, GatewayRuntime, SchemaPrep, TickClock, mock_image, temp_db

A = "owner-a"


def protocol_methods(proto) -> dict[str, int]:
    return {
        name: len(inspect.signature(fn).parameters)
        for name, fn in vars(proto).items()
        if callable(fn) and not name.startswith("_")
    }


class ProtocolShapes(unittest.TestCase):
    def assertConforms(self, obj, proto):
        for name, arity in protocol_methods(proto).items():
            with self.subTest(proto=proto.__name__, method=name):
                self.assertTrue(hasattr(obj, name), f"missing {name}")
                bound = inspect.signature(getattr(obj, name))
                self.assertEqual(len(bound.parameters), arity - 1, f"{name} arity")  # minus self

    def test_registry_and_result(self):
        self.assertConforms(Knowledge(), I.Registry)
        self.assertConforms(ResultEvaluator(), I.ResultPort)

    def test_store_capabilities(self):
        store = Store(temp_db(self))
        self.assertConforms(SqliteCoordinatorStore(store, TickClock(), lambda r: r), I.CoordinatorStore)
        self.assertConforms(StoreGateway(store), I.GatewayStore)

    def test_test_providers_match_ports(self):
        self.assertConforms(SchemaPrep("kmong"), I.PreparationPort)
        self.assertConforms(FakeRuntime("kmong"), I.ExecutionPort)


class ProvidersInjection(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.rt = GatewayRuntime("kmong")
        self.prep = SchemaPrep("kmong")
        providers = Providers(registry=Knowledge(), preparation=self.prep, execution=self.rt,
                              result=ResultEvaluator())
        self.co = Coordinator(Store(self.path), providers=providers, clock=TickClock())
        self.rt.gateway = StoreGateway(Store(self.path), clock=TickClock(500))
        self.src = self.co.create_source(A, {"raw_text": "x", "new_assets": [
            {"part_name": "i", "rights_confirmed": True}]}, {"i": mock_image()})

    def register(self):
        return self.co.create_registration(A, {"source_id": self.src["source_id"], "selector": "kmong"})

    def test_full_flow_with_providers_bundle(self):
        reg = self.register()
        rid = reg["registration_id"]
        r = self.co.authenticate(A, rid, {"action": "open", "expected_revision": 1})["registration"]
        v = self.co.authenticate(A, rid, {"action": "finish", "expected_revision": r["revision"],
                                          "generation": 1})["registration"]
        self.co.start(A, rid, {"expected_revision": v["revision"], "review_digest": v["review"]["digest"],
                               "approved": True, "request_key": "k"})
        self.assertEqual(self.co.run_job(rid), "done")

    def test_prep_port_failure_model_unavailable_is_persisted_issue(self):
        self.prep.fail = PortFailure({"code": "MODEL_UNAVAILABLE", "message": "model down"})
        v = self.register()
        self.assertEqual(v["preparation"]["issues"][0]["code"], "model_unavailable")

    def test_prep_port_failure_typed_and_unknown_codes(self):
        self.prep.fail = PortFailure({"code": "VALIDATION_FAILED", "message": "bad source"})
        with self.assertRaises(AppError) as ctx:
            self.register()
        self.assertEqual(ctx.exception.code, "VALIDATION_FAILED")
        self.prep.fail = PortFailure({"code": "IDEMPOTENCY_CONFLICT", "message": "not an I2 code"})
        with self.assertRaises(AppError) as ctx:
            self.register()
        self.assertEqual(ctx.exception.code, "RUNTIME_ERROR")
        self.prep.fail = PortFailure({"oops": True})
        with self.assertRaises(AppError) as ctx:
            self.register()
        self.assertEqual(ctx.exception.code, "RUNTIME_ERROR")

    def test_exec_port_failure_on_authenticate(self):
        reg = self.register()
        rid = reg["registration_id"]
        self.co.authenticate(A, rid, {"action": "open", "expected_revision": 1})
        self.rt.fail_next = PortFailure({"code": "ACCOUNT_MISMATCH", "message": "other account"})
        with self.assertRaises(AppError) as ctx:
            self.co.authenticate(A, rid, {"action": "finish", "expected_revision": 2, "generation": 1})
        self.assertEqual(ctx.exception.code, "ACCOUNT_MISMATCH")
        self.assertEqual(self.co.get_registration(A, rid)["auth"], {"state": "closed"})

    def test_exec_port_failure_on_execute_stops_with_typed_error(self):
        reg = self.register()
        rid = reg["registration_id"]
        r = self.co.authenticate(A, rid, {"action": "open", "expected_revision": 1})["registration"]
        v = self.co.authenticate(A, rid, {"action": "finish", "expected_revision": r["revision"],
                                          "generation": 1})["registration"]
        self.co.start(A, rid, {"expected_revision": v["revision"], "review_digest": v["review"]["digest"],
                               "approved": True, "request_key": "k"})

        def fail(_inp):
            raise PortFailure({"code": "RUNTIME_ERROR", "message": "browser closed"})
        self.rt.execute = fail
        self.assertEqual(self.co.run_job(rid), "stopped")
        res = self.co.get_registration(A, rid)["result"]
        self.assertEqual((res["goal_verdict"], res["error"]["message"]), ("not_reached", "browser closed"))


if __name__ == "__main__":
    unittest.main()
