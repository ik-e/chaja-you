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


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_DIMENSION = 20000  # provisional sanity bound (SPEC §10)


def inspect_image(data: bytes) -> dict | None:
    """Return {mime, width, height} for a structurally complete PNG/JPEG, else None.

    PNG: signature, IHDR first (length 13), every chunk CRC valid, ends exactly at IEND.
    JPEG: SOI, well-formed segments up to a SOF0/1/2 frame header, ends with EOI.
    Dimensions must be 1..MAX_DIMENSION. Nothing is decoded or executed.
    """
    info = _inspect_png(data) if data.startswith(PNG_SIGNATURE) else (
        _inspect_jpeg(data) if data.startswith(b"\xff\xd8") else None)
    if info is None:
        return None
    if not (0 < info["width"] <= MAX_DIMENSION and 0 < info["height"] <= MAX_DIMENSION):
        return None
    return info


def _inspect_png(data: bytes) -> dict | None:
    import zlib

    i = len(PNG_SIGNATURE)
    first = True
    info = None
    while i + 12 <= len(data):
        length = int.from_bytes(data[i:i + 4], "big")
        ctype = data[i + 4:i + 8]
        end = i + 12 + length
        if end > len(data):
            return None
        crc = int.from_bytes(data[i + 8 + length:end], "big")
        if crc != zlib.crc32(data[i + 4:i + 8 + length]):
            return None
        if first:
            if ctype != b"IHDR" or length != 13:
                return None
            info = {"mime": "image/png", "width": int.from_bytes(data[i + 8:i + 12], "big"),
                    "height": int.from_bytes(data[i + 12:i + 16], "big")}
            first = False
        if ctype == b"IEND":
            return info if end == len(data) else None  # trailing bytes after IEND are rejected
        i = end
    return None


def _inspect_jpeg(data: bytes) -> dict | None:
    if not data.endswith(b"\xff\xd9"):
        return None
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            return None
        marker = data[i + 1]
        if marker == 0xFF:  # fill byte
            i += 1
            continue
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            return None  # unexpected standalone marker before a frame header
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if length < 2 or i + 2 + length > len(data):
            return None
        if marker in (0xC0, 0xC1, 0xC2):
            if length < 8:
                return None
            return {"mime": "image/jpeg", "width": int.from_bytes(data[i + 7:i + 9], "big"),
                    "height": int.from_bytes(data[i + 5:i + 7], "big")}
        i += 2 + length
    return None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
