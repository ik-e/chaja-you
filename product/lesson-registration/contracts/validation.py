"""Executable named-schema boundary checks; uses standard Draft 2020-12.

Install the independent candidate validation tool as documented in PLAN.md.
No fallback to shape-only validation if jsonschema is missing.
Schema inputs are pinned by the caller; no network resolution.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from .interfaces import PortFailure, Providers


class ContractViolation(ValueError):
    """Boundary rejected; do not expose submitted values or validator traces."""


class SchemaCatalog:
    def __init__(self, schema: dict, profiles: dict):
        from jsonschema import Draft202012Validator, FormatChecker
        from referencing import Registry
        self.cls = Draft202012Validator
        self.format_checker = FormatChecker()
        self.registry = Registry()
        self.schema = deepcopy(schema)
        self.profiles = deepcopy(profiles)
        self.cls.check_schema(self.schema)
        self._audit_refs(self.schema)
        for profile in self.profiles["profiles"]:
            self.cls.check_schema(self._profile_schema(profile))
            self._audit_refs(self._profile_schema(profile))

    @staticmethod
    def _audit_refs(node: Any) -> None:
        # All current references are local. New external refs need explicit review.
        if isinstance(node, dict):
            if "$ref" in node and not node["$ref"].startswith("#/$defs/"):
                raise ContractViolation("external or unsupported schema reference")
            for value in node.values():
                SchemaCatalog._audit_refs(value)
        elif isinstance(node, list):
            for value in node:
                SchemaCatalog._audit_refs(value)

    def _profile_schema(self, profile: dict) -> dict:
        defs = deepcopy(self.schema["$defs"])
        local = profile.get("value_defs", {})
        if set(defs) & set(local):
            raise ContractViolation("profile shadows a shared definition")
        defs.update(deepcopy(local))
        return {"$schema": self.schema["$schema"], "$defs": defs,
                **deepcopy(profile["value_schema"])}

    def _validate(self, schema: dict, value: Any, label: str) -> None:
        validator = self.cls(schema, format_checker=self.format_checker, registry=self.registry)
        if not validator.is_valid(value):
            raise ContractViolation(f"invalid {label}")

    def named(self, name: str, value: Any) -> None:
        if name not in self.schema["$defs"]:
            raise ContractViolation("unknown schema name")
        self._validate({"$schema": self.schema["$schema"], "$defs": self.schema["$defs"],
                        "$ref": "#/$defs/" + name}, value, name)

    def profile_values(self, profile_id: str, values: dict) -> None:
        found = [p for p in self.profiles["profiles"] if p["id"] == profile_id]
        if len(found) != 1:
            raise ContractViolation("unknown or ambiguous profile")
        self._validate(self._profile_schema(found[0]), values, "profile values")


class CheckedPorts:
    """Small composable caller-side guard; not a state machine or permission gate.

    The adopted common-integration JSON supplies port IDs and schema names.
    Selected relational guards below are necessary, not sufficient, for
    actual provider conformance. Real storage/runtime/evidence remain separate.
    """
    def __init__(self, catalog: SchemaCatalog, common: dict, providers: Providers):
        self.catalog = catalog
        self.definitions = {p["id"]: p for p in common["ports"]}
        self.methods = providers.methods()
        if set(self.definitions) != set(self.methods):
            raise ContractViolation("port registration mismatch")

    def call(self, port_id: str, value: Any) -> dict:
        definition = self.definitions.get(port_id)
        if definition is None:
            raise ContractViolation("unknown port")
        if definition["input"] == "selector:string":
            if not isinstance(value, str) or not value.strip():
                raise ContractViolation("invalid selector")
        else:
            self.catalog.named(definition["input"], value)
        try:
            response = self.methods[port_id](deepcopy(value))
        except PortFailure as exc:
            self.catalog.named("Error", exc.error)
            raise
        self.catalog.named(definition["output"], response)
        if port_id == "I2" and response["ready"]:
            if any(issue["blocking"] for issue in response["issues"]):
                raise ContractViolation("ready contradicts blocking issue")
        if port_id == "I3" and response["auth"]["state"] == "verified":
            if response["connection"]["verified_generation"] != response["auth"]["generation"]:
                raise ContractViolation("verified generation mismatch")
            if response["connection"]["account_ref"] != response["target"]["identity"]["external_account_ref"]:
                raise ContractViolation("verified account mismatch")
        if port_id == "I5" and response["goal_verdict"] == "confirmed":
            if not value["report"].get("goal_observation") or not value["evidence"] or not response["evidence"]:
                raise ContractViolation("confirmed result missing observation/evidence")
        return deepcopy(response)
