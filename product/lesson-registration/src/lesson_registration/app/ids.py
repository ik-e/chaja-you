"""Opaque ids, canonical JSON digests and UTC timestamps."""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone


def new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(12)}"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    """SHA-256 hex of the canonical JSON form."""
    return hashlib.sha256(canonical(value)).hexdigest()


def bytes_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
