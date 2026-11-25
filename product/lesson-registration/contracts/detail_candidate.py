"""D01 reference helpers, NOT adopted runtime API. Validate pinned schemas before use."""
from __future__ import annotations
from copy import deepcopy
from .canonical import json_digest, asset_digest

TARGET_FIELDS = ("environment", "platform", "external_account_ref", "object_kind", "slot_ref")

def profile_digest(entry):
    # Named Profile view is the digest domain; the raw registry is separately pinned.
    view = {
        "ref": {k: entry[k] for k in ("platform", "object_kind", "version", "environment")},
        **{k: deepcopy(entry[k]) for k in ("routes", "fields", "prohibitions", "steps", "goal", "evidence_ids")},
        "value_contract_ref": entry["id"],
    }
    return json_digest(view)

def payload_digest(values):
    return json_digest(values)

def binding_digest(scope, definition):
    return json_digest({"kind": "binding.v1", "scope_digest": json_digest(scope),
                        "operation": definition})

def effect_key(target, logical_id):
    return json_digest([target[k] for k in TARGET_FIELDS] + [logical_id])

def default_manifest(entry):
    # Only candidate one-op-per-step mapping; provider must confirm effect granularity.
    return [{"logical_operation_id": s["step_id"], "step_id": s["step_id"],
             "action_key": s["step_id"], "effect_class": s["effect_class"],
             "bindings": deepcopy(s["bindings"])} for s in entry["steps"]]

def operations(scope, entry, manifest):
    expected_ref = {k: entry[k] for k in ("platform", "object_kind", "version", "environment")}
    expected_ref["digest"] = profile_digest(entry)
    if scope["profile_ref"] != expected_ref or scope["target"]["environment"] != "mock":
        raise ValueError("profile or environment mismatch")
    if any(scope["target"][k] != entry[k] for k in ("platform", "object_kind")):
        raise ValueError("target mismatch")
    if scope["connection"]["account_ref"] != scope["target"]["external_account_ref"]:
        raise ValueError("account mismatch")
    if scope["procedure_ids"] != [s["step_id"] for s in entry["steps"]]:
        raise ValueError("procedure mismatch")
    # Pinned candidate manifest; actual adapter registry may propose finer units.
    if manifest != default_manifest(entry):
        raise ValueError("unregistered manifest")
    return [{"operation_id": json_digest({"registration": scope["registration_id"],
                                         "logical": m["logical_operation_id"]}),
             "step_id": m["step_id"], "action_key": m["action_key"],
             "effect_class": m["effect_class"], "binding_digest": binding_digest(scope, m)}
            for m in manifest]

def check_readback(expected_values, observed_values, expected_assets, observed_asset_bytes):
    """Synthetic actual-value comparison only; no inference or asset metadata reconstruction."""
    if observed_values is None or observed_asset_bytes is None:
        return "unknown"
    if set(observed_values) != set(expected_values):
        return "unknown"
    if payload_digest(observed_values) != payload_digest(expected_values):
        return "not_reached"
    if [asset_digest(b) for b in observed_asset_bytes] != expected_assets:
        return "not_reached"
    return "confirmed"
