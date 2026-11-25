"""Pinned contract loading and validation through the shared standard validator.

Pins come from WORKSPACE.json; each file is checked against its git blob id
(CRLF normalised for Windows working copies). Validation delegates to the
common ``contracts.validation.SchemaCatalog`` (Draft 2020-12 jsonschema, IB-02)
so there is a single validation standard; this module only maps violations to
the app's ``AppError``.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from functools import lru_cache

from contracts.validation import ContractViolation, SchemaCatalog

from .errors import AppError

PRODUCT_ROOT = pathlib.Path(__file__).resolve().parents[3]
REPO_ROOT = PRODUCT_ROOT.parents[1]


def _blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    workspace = json.loads((PRODUCT_ROOT / "WORKSPACE.json").read_text(encoding="utf-8"))
    pins = [p for p in workspace["pins"] if p["path"].endswith("/" + name)]
    if len(pins) != 1:
        raise RuntimeError(f"no unique pin for {name}")
    pin = pins[0]
    raw = (REPO_ROOT / pin["path"]).read_bytes()
    if _blob_id(raw) != pin["blob"]:
        raw = raw.replace(b"\r\n", b"\n")
        if _blob_id(raw) != pin["blob"]:
            raise RuntimeError(f"pinned contract differs: {pin['path']}")
    return json.loads(raw)


@lru_cache(maxsize=1)
def catalog() -> SchemaCatalog:
    return SchemaCatalog(load("data-schema-v4.1.json"), load("platform-profiles-v2.json"))


def schema_defs() -> dict:
    return load("data-schema-v4.1.json")["$defs"]


def validate(def_name: str, value: object) -> None:
    """Raise AppError(INVALID_REQUEST) when ``value`` does not match ``$defs[def_name]``."""
    if def_name not in schema_defs():
        raise RuntimeError(f"unknown $def {def_name}")
    try:
        catalog().named(def_name, value)
    except ContractViolation:
        raise AppError("INVALID_REQUEST", f"{def_name} does not match the contract") from None


def is_valid(def_name: str, value: object) -> bool:
    try:
        validate(def_name, value)
    except AppError:
        return False
    return True


def profile_values_valid(profile_id: str, values: dict) -> bool:
    """Platform values against the pinned profile value schema (shared + profile-local defs)."""
    try:
        catalog().profile_values(profile_id, values)
    except ContractViolation:
        return False
    return True
