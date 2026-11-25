"""Server canonical byte primitive for existing data-contract-v4 canonical rule.
Scope/values/profile selection and observed normalization are provider responsibilities.
Do not hash unvalidated wire input or accept client digests as authority.
"""
from __future__ import annotations
import hashlib
import json

SAFE_INTEGER = (1 << 53) - 1

def _validate(value):
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if not -SAFE_INTEGER <= value <= SAFE_INTEGER:
            raise ValueError("integer outside interoperable range")
        return
    if type(value) is str:
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeError:
            raise ValueError("invalid unicode scalar") from None
        return
    if type(value) is list:
        for child in value:
            _validate(child)
        return
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ValueError("non-string object key")
            _validate(key)
            _validate(child)
        return
    raise ValueError("unsupported canonical JSON type")

def canonical_bytes(value) -> bytes:
    """UTF-8, Python Unicode codepoint key order, compact JSON, no normalization."""
    _validate(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def json_digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def asset_digest(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise ValueError("asset digest needs exact bytes")
    return hashlib.sha256(raw).hexdigest()
