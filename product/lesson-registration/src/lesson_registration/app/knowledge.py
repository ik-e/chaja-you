"""KNOW: I1 selector -> ResolveOutput from the pinned platform-profiles registry.

Implements contracts.interfaces.Registry (resolve, get_profile).

Pure local lookup; no network. ProfileRef.digest is the SHA-256 of the
canonical pinned profile entry (value schema included), so any change to the
pinned profile surfaces as PROFILE_CHANGED on later lookups by ref.
"""

from __future__ import annotations

import copy
import re

from . import contract
from .errors import AppError
from .ids import digest

MAX_SELECTOR = 256
_SELECTOR_OK = re.compile(r"^[^\x00-\x1f\x7f]+$")


def _profile_view(entry: dict) -> dict:
    ref = {
        "platform": entry["platform"],
        "object_kind": entry["object_kind"],
        "version": entry["version"],
        "digest": digest(entry),
        "environment": entry["environment"],
    }
    return {
        "ref": ref,
        "routes": copy.deepcopy(entry["routes"]),
        "fields": copy.deepcopy(entry["fields"]),
        "prohibitions": copy.deepcopy(entry["prohibitions"]),
        "steps": copy.deepcopy(entry["steps"]),
        "goal": copy.deepcopy(entry["goal"]),
        "value_contract_ref": entry["id"],
        "evidence_ids": copy.deepcopy(entry["evidence_ids"]),
    }


class Knowledge:
    def __init__(self, registry: dict | None = None) -> None:
        registry = registry if registry is not None else contract.load("platform-profiles-v2.json")
        self._by_route: dict[str, dict] = {}
        self._by_key: dict[tuple, dict] = {}
        self._entries: dict[tuple, dict] = {}
        for entry in registry["profiles"]:
            if entry.get("environment") != "mock":
                continue  # only pinned mock profiles resolve
            view = _profile_view(entry)
            contract.validate("Profile", view)
            key = (entry["platform"], entry["object_kind"], entry["version"])
            self._by_key[key] = view
            self._entries[key] = entry
            for route in entry["routes"]:
                self._by_route[route] = view

    def resolve(self, selector: str) -> dict:
        """I1. Invalid syntax -> INVALID_REQUEST; unknown -> typed unsupported (normal result)."""
        if not isinstance(selector, str) or not selector.strip() or len(selector) > MAX_SELECTOR:
            raise AppError("INVALID_REQUEST", "selector length or syntax invalid")
        if not _SELECTOR_OK.fullmatch(selector):
            raise AppError("INVALID_REQUEST", "selector contains control characters")
        view = self._by_route.get(selector.strip().lower())
        if view is None:
            out = {"status": "unsupported", "reason": "지원 목록에 없는 등록 대상입니다."}
        else:
            out = {"status": "supported", "profile": copy.deepcopy(view)}
        contract.validate("ResolveOutput", out)
        return out

    def get_profile(self, ref: dict) -> dict:
        """Return the same pinned Profile for a ProfileRef; digest drift -> PROFILE_CHANGED."""
        key = (ref.get("platform"), ref.get("object_kind"), ref.get("version"))
        view = self._by_key.get(key)
        if view is None or view["ref"]["digest"] != ref.get("digest") or ref.get("environment") != "mock":
            raise AppError("PROFILE_CHANGED", "pinned profile no longer matches")
        return copy.deepcopy(view)

    def value_schema(self, ref: dict) -> dict:
        self.get_profile(ref)
        return copy.deepcopy(self._entries[(ref["platform"], ref["object_kind"], ref["version"])]["value_schema"])
