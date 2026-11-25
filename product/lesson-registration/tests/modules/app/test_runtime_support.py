"""Actual SQLite approval/lineage boundaries for the R05 injection points."""
from dataclasses import replace
import json

from lesson_registration.app.runtime_support import RuntimeSupport
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.app.store import Store, tx
from test_s4_atomic import Base, A
from support import mock_image
from lesson_registration.app.gateway import scope_binding_digest
from contracts.detail_candidate import binding_digest as reference_binding


class RuntimeSupportTests(Base):
    def setUp(self):
        super().setUp()
        self.support = RuntimeSupport(Store(self.path), Knowledge())

    def test_full_scope_digest_includes_values_for_empty_binding(self):
        scope = json.loads(self.job()["accepted_scope_json"])["scope"]
        profile = Knowledge().get_profile(scope["profile_ref"])
        step = next(s for s in profile["steps"] if s["step_id"] == "K6")
        definition = {"logical_operation_id": "K6", "step_id": "K6", "action_key": "K6",
                      "effect_class": step["effect_class"], "bindings": step["bindings"]}
        original = scope_binding_digest(scope, step)
        self.assertEqual(original, reference_binding(scope, definition))
        scope["values"]["title"] = "tampered title"
        self.assertNotEqual(original, scope_binding_digest(scope, step))

    def test_lineage_same_slot_other_platform_distinct(self):
        reg = self.co.get_registration(A, self.rid)
        src = self.co.create_source(A, {"raw_text": "version two", "previous_source_id": reg["source_id"]})
        newer = self.co.create_registration(A, {"source_id": src["source_id"], "selector": "kmong"})
        pid = "kmong.service_listing.mock.v2"
        first = self.support.slot_resolver(self.rid, A, pid)
        self.assertEqual(first, self.support.slot_resolver(newer["registration_id"], A, pid))
        self.assertCode("NOT_FOUND", self.support.slot_resolver, self.rid, "foreign", pid)
        self.assertCode("PROFILE_CHANGED", self.support.slot_resolver, self.rid, A, "wrong")

    def test_asset_checks_lease_approval_and_fence(self):
        ctx = self.rt.gateway.acquire_context(self.rid)
        asset = json.loads(self.job()["accepted_scope_json"])["scope"]["assets"][0]
        self.assertEqual(self.support.read_approved_asset(ctx, asset["asset_id"]), mock_image())
        self.assertCode("PERMISSION_DENIED", self.support.read_approved_asset, replace(ctx, lease="wrong"), asset["asset_id"])
        self.assertCode("PERMISSION_DENIED", self.support.read_approved_asset, ctx, "unapproved")
        self.rt.gateway.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
        self.assertCode("PERMISSION_DENIED", self.support.read_approved_asset, ctx, asset["asset_id"])

    def test_corrupt_bytes_are_rejected(self):
        ctx = self.rt.gateway.acquire_context(self.rid)
        asset = json.loads(self.job()["accepted_scope_json"])["scope"]["assets"][0]
        with self.co.store.connect() as conn, tx(conn):
            conn.execute("UPDATE assets SET blob=? WHERE asset_id=?", (b"corrupt", asset["asset_id"]))
        self.assertCode("RUNTIME_ERROR", self.support.read_approved_asset, ctx, asset["asset_id"])

    def test_permit_is_one_shot_and_fence_blocks_consumption(self):
        gateway = self.rt.gateway
        ctx = gateway.acquire_context(self.rid)
        ops = gateway.expected_operations(ctx)
        permit = gateway.admit(ctx, ops[0])
        self.assertCode("PERMISSION_DENIED", gateway.consume, ctx, permit, ops[1])
        gateway.consume(ctx, permit, ops[0])
        self.assertCode("PERMISSION_DENIED", gateway.consume, ctx, permit, ops[0])
        pending = gateway.admit(ctx, ops[1])
        gateway.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
        self.assertCode("PERMISSION_DENIED", gateway.consume, ctx, pending, ops[1])
