"""Registered K1..K7 operations and binding digests (RT-02 input)."""
from __future__ import annotations

import hashlib
import json

from . import profile


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def operation_id(target: dict, step_id: str, action_key: str) -> str:
    """Stable logical operation id: same target slot + step => same id, so a retry,
    new worker or new request key cannot mint a fresh effect identity."""
    return "kmong-" + sha256(canonical({"profile": profile.PROFILE_ID, "target": target,
                                         "step_id": step_id, "action_key": action_key}))[:40]


def bound_values(values: dict, bindings) -> dict:
    out = {}
    for k in bindings:
        v = values.get(k)
        if k == "packages" and isinstance(v, list):
            v = profile.ordered_packages(v)
        out[k] = v
    return out


def binding_digest(scope: dict, step_id: str, action_key: str, bindings) -> str:
    return sha256(canonical({"profile": profile.PROFILE_ID, "step_id": step_id, "action_key": action_key,
                             "target": scope["target"], "registration_id": scope["registration_id"],
                             "revision": scope["revision"], "values": bound_values(scope["values"], bindings)}))


def list_operations(accepted: dict) -> list[dict]:
    scope = accepted["scope"]
    ops = []
    for step_id, action_key, effect_class, bindings in profile.STEPS:
        ops.append({"operation_id": operation_id(scope["target"], step_id, action_key), "step_id": step_id,
                    "action_key": action_key, "effect_class": effect_class,
                    "binding_digest": binding_digest(scope, step_id, action_key, bindings)})
    return ops
