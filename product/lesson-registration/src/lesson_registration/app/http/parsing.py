"""Bounded UTF-8 JSON and MIME parsing without additional shared dependencies.

The stdlib MIME parser is used only for a buffered, size-limited mock upload.
Nested MIME, transfer encodings, duplicate headers/parts and defects are rejected.
"""
import json
from email import policy
from email.parser import BytesParser

from ..errors import AppError


def invalid():
    return AppError("INVALID_REQUEST", "요청 형식을 확인해 주세요.")


def json_object(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("non-finite JSON")

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        if not isinstance(result, dict):
            raise ValueError("object required")
        return result
    except (ValueError, UnicodeError, RecursionError):
        raise invalid() from None


def source_parts(raw, content_type):
    try:
        if "\r" in content_type or "\n" in content_type:
            raise ValueError("header")
        msg = BytesParser(policy=policy.default).parsebytes(
            b"Content-Type: " + content_type.encode("ascii") + b"\r\nMIME-Version: 1.0\r\n\r\n" + raw)
        if msg.get_content_type() != "multipart/form-data" or not msg.is_multipart():
            raise ValueError("multipart required")
        if any(p.defects for p in msg.walk()):
            raise ValueError("malformed MIME")
        parts = {}
        manifest = None
        for part in msg.iter_parts():
            if part.is_multipart() or part.get_content_disposition() != "form-data":
                raise ValueError("nested or invalid part")
            if any(len(part.get_all(h, [])) > 1 for h in part.keys()):
                raise ValueError("duplicate header")
            if part.get("Content-Transfer-Encoding") is not None:
                raise ValueError("encoded part")
            name = part.get_param("name", header="content-disposition")
            if not name or name in parts:
                raise ValueError("duplicate or unnamed part")
            data = part.get_payload(decode=True)
            parts[name] = (data, part.get("Content-Type"))
            if name == "manifest":
                if part.get_content_type() != "application/json":
                    raise ValueError("JSON manifest required")
                manifest = json_object(data)
            elif part.get_filename() is None or part.get("Content-Type") is None:
                raise ValueError("file and media type required")
        if manifest is None:
            raise ValueError("missing manifest")
        del parts["manifest"]
        return manifest, parts
    except (ValueError, UnicodeError, TypeError):
        raise invalid() from None
