"""Registered K1..K7 operations and binding digests (RT-02 input).

Aligned with R03 StoreGateway (app/gateway.py, agreed 2026-11-25):
- operation_id ``{registration_id}:{step_id}``, action_key = step_id
- logical effect identity is (target, step_id) inside STORE, so a new operation_id,
  profile version, request or worker cannot bypass an existing effect
- binding_digest = canonical digest of {step_id, bound values, scope asset digests
  (only when main_images is bound), target, profile digest}
Canonical bytes come from the shared contracts.canonical helper. Explicit
binding.v1 mode binds the full Scope plus the step manifest, matching R03 and
the common reference. Legacy stays the default for existing isolated callers.
"""
from __future__ import annotations

import hashlib

from contracts.canonical import canonical_bytes, json_digest

from . import profile


def canonical(value) -> bytes:
    return canonical_bytes(value)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def operation_id(registration_id: str, step_id: str) -> str:
    return f"{registration_id}:{step_id}"


def binding_digest(scope: dict, step_id: str, bindings) -> str:
    bound = {k: scope["values"].get(k) for k in bindings}
    asset_digests = [a["digest"] for a in scope["assets"]] if "main_images" in bindings else []
    return json_digest({"step_id": step_id, "bound": bound, "asset_digests": asset_digests,
                        "target": scope["target"], "profile_digest": scope["profile_ref"]["digest"]})


def scope_binding_digest(scope: dict, step_id: str, effect_class: str, bindings) -> str:
    definition = {"logical_operation_id": step_id, "step_id": step_id, "action_key": step_id,
                  "effect_class": effect_class, "bindings": list(bindings)}
    return json_digest({"kind": "binding.v1", "scope_digest": json_digest(scope), "operation": definition})


def list_operations(accepted: dict, *, binding_version="legacy") -> list[dict]:
    if binding_version not in ("legacy", "binding.v1"):
        raise ValueError("unknown binding version")
    scope = accepted["scope"]
    return [{"operation_id": operation_id(scope["registration_id"], step_id), "step_id": step_id,
             "action_key": step_id, "effect_class": effect_class,
             "binding_digest": (scope_binding_digest(scope, step_id, effect_class, bindings)
                                if binding_version == "binding.v1" else binding_digest(scope, step_id, bindings))}
            for step_id, _action, effect_class, bindings in profile.STEPS]
