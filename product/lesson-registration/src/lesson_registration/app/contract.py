"""Load pinned contract files and validate values against named ``$defs``.

Pins come from WORKSPACE.json. Each file is checked against its git blob id
(after normalising CRLF to LF, since working copies may be converted on
Windows). The validator implements exactly the JSON Schema keywords used by
data-schema-v4.1; an unknown keyword raises instead of silently passing.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime
from functools import lru_cache

from .errors import AppError
from .ids import canonical

PRODUCT_ROOT = pathlib.Path(__file__).resolve().parents[3]
REPO_ROOT = PRODUCT_ROOT.parents[1]

SUPPORTED_KEYWORDS = frozenset(
    {
        "$ref", "type", "properties", "required", "additionalProperties", "enum", "const",
        "oneOf", "anyOf", "items", "minItems", "maxItems", "uniqueItems", "minimum", "maximum",
        "minLength", "maxLength", "pattern", "format",
        # annotations
        "description", "title", "$comment", "examples", "default",
    }
)


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


def schema_defs() -> dict:
    return load("data-schema-v4.1.json")["$defs"]


class _Invalid(Exception):
    def __init__(self, path: str, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _date_time(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return "T" in value


def _check(schema: dict, value: object, path: str, defs: dict) -> None:
    unknown = set(schema) - SUPPORTED_KEYWORDS
    if unknown:
        raise RuntimeError(f"unsupported schema keyword(s) {sorted(unknown)} at {path}")

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise RuntimeError(f"unsupported $ref {ref}")
        _check(defs[ref[len("#/$defs/"):]], value, path, defs)

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](value) for t in types):
            raise _Invalid(path, f"expected {'/'.join(types)}")

    if "const" in schema and canonical(value) != canonical(schema["const"]):
        raise _Invalid(path, "const mismatch")
    if "enum" in schema and not any(canonical(value) == canonical(e) for e in schema["enum"]):
        raise _Invalid(path, "not in enum")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise _Invalid(path, "too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise _Invalid(path, "too long")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise _Invalid(path, "pattern mismatch")
        if schema.get("format") == "date-time" and not _date_time(value):
            raise _Invalid(path, "not date-time")

    if _TYPES["number"](value):
        if "minimum" in schema and value < schema["minimum"]:
            raise _Invalid(path, "below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise _Invalid(path, "above maximum")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise _Invalid(path, "too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise _Invalid(path, "too many items")
        if schema.get("uniqueItems") and len({canonical(v) for v in value}) != len(value):
            raise _Invalid(path, "duplicate items")
        if "items" in schema:
            for i, item in enumerate(value):
                _check(schema["items"], item, f"{path}/{i}", defs)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                raise _Invalid(f"{path}/{key}", "required")
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                _check(props[key], item, f"{path}/{key}", defs)
            elif extra is False:
                raise _Invalid(f"{path}/{key}", "unknown key")
            elif isinstance(extra, dict):
                _check(extra, item, f"{path}/{key}", defs)

    if "anyOf" in schema:
        if not any(_passes(s, value, path, defs) for s in schema["anyOf"]):
            raise _Invalid(path, "no anyOf branch matched")
    if "oneOf" in schema:
        matched = sum(_passes(s, value, path, defs) for s in schema["oneOf"])
        if matched != 1:
            raise _Invalid(path, f"oneOf matched {matched} branches")


def _passes(schema: dict, value: object, path: str, defs: dict) -> bool:
    try:
        _check(schema, value, path, defs)
    except _Invalid:
        return False
    return True


def validate(def_name: str, value: object) -> None:
    """Raise AppError(INVALID_REQUEST) when ``value`` does not match ``$defs[def_name]``."""
    defs = schema_defs()
    if def_name not in defs:
        raise RuntimeError(f"unknown $def {def_name}")
    try:
        _check(defs[def_name], value, "", defs)
    except _Invalid as exc:
        raise AppError(
            "INVALID_REQUEST",
            f"{def_name} invalid at {exc.path or '/'}: {exc.reason}",
        ) from None


def is_valid(def_name: str, value: object) -> bool:
    try:
        validate(def_name, value)
    except AppError:
        return False
    return True
