"""Test-only helpers for r05-kmong: stdlib form client (ScopedPage), assets, fake gateway,
minimal JSON-schema checker for pinned contracts. Not product runtime."""
from __future__ import annotations

import copy
import http.client
import itertools
import json
import pathlib
import re
import secrets
import struct
import sys
import zlib
from html.parser import HTMLParser
from urllib.parse import urlencode, urlsplit

import dev
from lesson_registration.platforms.kmong import KmongError, NavigationUnknown, PageStructureError, PageView

ROOT = pathlib.Path(dev.ROOT)
sys.path.insert(0, str(ROOT / "fixtures" / "platforms" / "kmong"))
import mock_kmong  # noqa: E402

SHARED_IMAGE = ROOT / "fixtures" / "shared" / "mock-image.png"


# ---------------- HTML form client implementing ScopedPage ----------------
class _Parser(HTMLParser):
    VOID = {"input", "br", "img", "meta", "link", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.page, self.fields, self.forms = "", {}, []
        self._capture = []          # stack of [field_name, tag, buffer]
        self._form = None
        self._select = None
        self._textarea = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.page = a.get("data-page", "")
        for c in self._capture:
            if c[1] == tag:
                c[3] += 1
        if "data-field" in a and tag not in self.VOID:
            self._capture.append([a["data-field"], tag, [], 0])
        if tag == "form":
            self._form = {"action": a.get("action", ""), "method": a.get("method", "get").lower(),
                          "enctype": a.get("enctype", "application/x-www-form-urlencoded"),
                          "inputs": {}, "files": set(), "buttons": set()}
            self.forms.append(self._form)
        elif self._form is not None:
            name = a.get("name")
            if tag == "input" and name:
                t = a.get("type", "text")
                if t == "file":
                    self._form["files"].add(name)
                elif t == "checkbox":
                    self._form["inputs"].setdefault(name, None if "checked" not in a else a.get("value", "on"))
                else:
                    self._form["inputs"][name] = a.get("value", "")
            elif tag == "textarea" and name:
                self._textarea = name
                self._form["inputs"][name] = ""
            elif tag == "select" and name:
                self._select = name
                self._form["inputs"][name] = None
            elif tag == "option" and self._select:
                if self._form["inputs"][self._select] is None or "selected" in a:
                    self._form["inputs"][self._select] = a.get("value", "")
            elif tag == "button" and name:
                self._form["buttons"].add(name)

    def handle_endtag(self, tag):
        if tag == "form":
            self._form = None
        elif tag == "select":
            self._select = None
        elif tag == "textarea":
            self._textarea = None
        if self._capture and self._capture[-1][1] == tag:
            c = self._capture[-1]
            if c[3] == 0:
                self._capture.pop()
                self.fields.setdefault(c[0], []).append("".join(c[2]))
            else:
                c[3] -= 1

    def handle_data(self, data):
        for c in self._capture:
            c[2].append(data)
        if self._textarea and self._form is not None:
            self._form["inputs"][self._textarea] += data


class FormPage:
    """Minimal browser-like client: cookies, same-origin redirects, HTML forms. Origin is fixed."""

    def __init__(self, base_url: str, timeout: float = 3.0):
        u = urlsplit(base_url)
        self.host, self.port, self.timeout = u.hostname, u.port, timeout
        self.cookies: dict[str, str] = {}
        self._view = PageView("", 0, "")
        self._forms: list[dict] = []
        self._pending: dict[str, str] = {}
        self._files: dict[str, list] = {}
        self.log: list[tuple] = []

    def _request(self, method, path, body=None, ctype=None):
        for _ in range(5):
            if not path.startswith("/") or path.startswith("//"):
                raise PageStructureError("cross-origin navigation refused")
            conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
            headers = {}
            if self.cookies:
                headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
            if body is not None:
                headers["Content-Type"] = ctype
            try:
                conn.request(method, path, body=body, headers=headers)
                resp = conn.getresponse()
                raw = resp.read()
            except (OSError, http.client.HTTPException) as e:
                raise NavigationUnknown(f"{method} {path}: {type(e).__name__}") from e
            finally:
                conn.close()
            self.log.append((method, path, resp.status))
            for k, v in resp.getheaders():
                if k.lower() == "set-cookie":
                    name, _, rest = v.partition("=")
                    self.cookies[name] = rest.split(";", 1)[0]
            if resp.status in (301, 302, 303):
                loc = resp.getheader("Location", "")
                lu = urlsplit(loc)
                if lu.netloc and (lu.hostname, lu.port) != (self.host, self.port):
                    raise PageStructureError("cross-origin redirect refused")
                method, path, body = "GET", lu.path or "/", None
                continue
            p = _Parser()
            p.feed(raw.decode("utf-8"))
            self._view = PageView(path, resp.status, p.page, p.fields)
            self._forms, self._pending, self._files = p.forms, {}, {}
            return self._view
        raise PageStructureError("too many redirects")

    # ScopedPage
    def goto(self, path):
        return self._request("GET", path)

    def view(self):
        return self._view

    def fill(self, name, value):
        if not any(name in f["inputs"] for f in self._forms):
            raise PageStructureError(f"field {name} not on page {self._view.page}")
        self._pending[name] = value

    def attach(self, name, files):
        if not any(name in f["files"] for f in self._forms):
            raise PageStructureError(f"file input {name} not on page {self._view.page}")
        self._files[name] = list(files)

    def submit(self, control):
        form = next((f for f in self._forms if control in f["buttons"]), None)
        if form is None:
            raise PageStructureError(f"control {control} not on page {self._view.page}")
        data = {k: v for k, v in form["inputs"].items() if v is not None}
        data.update({k: v for k, v in self._pending.items() if k in form["inputs"]})
        data[control] = "1"
        if form["enctype"] == "multipart/form-data":
            boundary = "lr" + secrets.token_hex(12)
            parts = []
            for k, v in data.items():
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
            for k in form["files"]:
                for f in self._files.get(k, []):
                    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{f.filename}"\r\n'
                                 f"Content-Type: {f.mime}\r\n\r\n".encode() + f.data + b"\r\n")
            body = b"".join(parts) + f"--{boundary}--\r\n".encode()
            return self._request("POST", form["action"], body, f"multipart/form-data; boundary={boundary}")
        return self._request("POST", form["action"], urlencode(data).encode(), "application/x-www-form-urlencoded")


def human_login(page: FormPage, site, account: str = "mock-account-kmong", password: str | None = None):
    """Stands in for the user signing in through the viewer (not adapter work)."""
    page.goto("/login")
    page.fill("username", account)
    page.fill("password", site.accounts[account] if password is None else password)
    return page.submit("login")


# ---------------- synthetic assets ----------------
def make_png(width=652, height=488, rgb=(200, 80, 40)) -> bytes:
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    row = b"\x00" + bytes(rgb) * width
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height, 9)) + chunk(b"IEND", b""))


class Assets:
    def __init__(self):
        self.blobs: dict[tuple, bytes] = {}

    def add(self, asset_id: str, data: bytes, mime="image/png", width=652, height=488) -> dict:
        import hashlib
        ref = {"asset_id": asset_id, "digest": hashlib.sha256(data).hexdigest(), "mime": mime, "bytes": len(data),
               "width": width, "height": height, "rights_confirmed": True}
        self.blobs[(asset_id, ref["digest"])] = data
        return ref

    def read(self, asset_id, digest):
        return self.blobs[(asset_id, digest)]


def base_accepted() -> dict:
    """Accepted scope from the common replay example (R01 fixture, read-only)."""
    return copy.deepcopy(dev.fixtures()["kmong"]["cases"]["I4"]["input"]["accepted"])


def default_assets() -> Assets:
    a = Assets()
    ref = base_accepted()["scope"]["assets"][0]
    a.blobs[(ref["asset_id"], ref["digest"])] = SHARED_IMAGE.read_bytes()
    return a


_clock = itertools.count()


def fixed_clock():
    n = next(_clock)
    return f"2026-11-25T00:{n // 60 % 60:02d}:{n % 60:02d}Z"


# ---------------- fake gateway (stands in for r05-remote + r03 STORE) ----------------
class FakeStore:
    """Effect ledger keyed by stable logical operation id (S-ADMIT/S-OBSERVE/S-FENCE semantics)."""

    def __init__(self):
        self.effects: dict[str, str] = {}
        self.fenced: set[str] = set()
        self.observations: list[dict] = []
        self.evidence: list[dict] = []
        self.dispatches: list[str] = []


class Denied(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class FakeGateway:
    def __init__(self, adapter, ctx, store: FakeStore):
        self.adapter, self.ctx, self.store = adapter, ctx, store
        self.registry = adapter.operations(ctx.accepted)
        self.reg_id = ctx.accepted["scope"]["registration_id"]

    def admit(self, op):
        if self.reg_id in self.store.fenced:
            raise Denied("INVALID_PHASE")
        if op not in self.registry:
            raise Denied("INVALID_REQUEST")
        if op["effect_class"] == "potential_effect":
            if self.store.effects.get(op["operation_id"]) in ("pending", "confirmed", "unknown"):
                raise Denied("DUPLICATE_RISK")
            self.store.effects[op["operation_id"]] = "pending"
        self.store.dispatches.append(op["step_id"])

    def perform(self, op):
        self.admit(op)
        try:
            out = self.adapter.perform(self.ctx, op)
        except KmongError as e:
            if op["effect_class"] == "potential_effect":
                self.store.effects[op["operation_id"]] = "unknown" if e.verdict == "unknown" else (
                    "confirmed" if e.verdict == "confirmed" else "absent")
            if e.observation:
                self.store.observations.append(e.observation)
            self.store.evidence += e.evidence
            self.store.fenced.add(self.reg_id)
            raise
        if op["effect_class"] == "potential_effect":
            self.store.effects[op["operation_id"]] = out.observation["verdict"]
        self.store.observations.append(out.observation)
        self.store.evidence += out.evidence
        return out

    def run(self) -> dict:
        """I4-like loop: registered operations in order; stop at first error; readback goal."""
        report = {"observations": []}
        start = len(self.store.observations)
        try:
            for op in self.registry:
                out = self.perform(op)
                if out.goal and out.goal.goal_observation:
                    report["goal_observation"] = out.goal.goal_observation
        except KmongError as e:
            report["error"] = e.to_error()
        except Denied as e:
            report["error"] = {"code": e.code, "message": "admission denied"}
        report["observations"] = self.store.observations[start:]
        return report


# ---------------- minimal JSON schema check for pinned contracts ----------------
class SchemaChecker:
    def __init__(self, root: dict):
        self.root = root

    def errors(self, value, schema, path="$"):
        if "$ref" in schema:
            name = schema["$ref"].split("/")[-1]
            return self.errors(value, self.root["$defs"][name], path)
        errs = []
        if "anyOf" in schema:
            if all(self.errors(value, s, path) for s in schema["anyOf"]):
                errs.append(f"{path}: no anyOf match")
            return errs
        if "const" in schema and value != schema["const"]:
            errs.append(f"{path}: const")
        if "enum" in schema and value not in schema["enum"]:
            errs.append(f"{path}: enum {value!r}")
        t = schema.get("type")
        checks = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
                  "string": lambda v: isinstance(v, str), "boolean": lambda v: isinstance(v, bool),
                  "null": lambda v: v is None, "integer": lambda v: isinstance(v, int) and not isinstance(v, bool)}
        if t and not checks[t](value):
            return errs + [f"{path}: type {t}"]
        if isinstance(value, str):
            if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", 10**9):
                errs.append(f"{path}: length")
            if "pattern" in schema and not re.search(schema["pattern"], value):
                errs.append(f"{path}: pattern")
        if isinstance(value, int) and not isinstance(value, bool):
            if value < schema.get("minimum", -10**18) or value > schema.get("maximum", 10**18):
                errs.append(f"{path}: range")
        if isinstance(value, list):
            if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 10**9):
                errs.append(f"{path}: items count")
            if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
                errs.append(f"{path}: unique")
            for i, v in enumerate(value):
                if "items" in schema:
                    errs += self.errors(v, schema["items"], f"{path}[{i}]")
        if isinstance(value, dict):
            props = schema.get("properties", {})
            for k in schema.get("required", []):
                if k not in value:
                    errs.append(f"{path}.{k}: required")
            for k, v in value.items():
                if k in props:
                    errs += self.errors(v, props[k], f"{path}.{k}")
                elif schema.get("additionalProperties") is False:
                    errs.append(f"{path}.{k}: additional")
                elif isinstance(schema.get("additionalProperties"), dict):
                    errs += self.errors(v, schema["additionalProperties"], f"{path}.{k}")
        return errs

    def check(self, value, def_name):
        return self.errors(value, {"$ref": "#/$defs/" + def_name})


def data_schema() -> SchemaChecker:
    return SchemaChecker(dev.pinned("data-schema-v4.1.json"))


def kmong_profile() -> dict:
    return next(p for p in dev.pinned("platform-profiles-v2.json")["profiles"] if p["id"] == "kmong.service_listing.mock.v2")


class BoundFake:
    """contracts.interfaces.BoundGateway over FakeGateway: Observation dicts out, PortFailure on error."""

    def __init__(self, gateway: FakeGateway):
        self.gw = gateway

    def list_operations(self):
        return [dict(o) for o in self.gw.registry]

    def perform(self, operation):
        from contracts.interfaces import PortFailure
        try:
            return self.gw.perform(operation).observation
        except KmongError as e:
            raise PortFailure(e.to_error()) from e
        except Denied as e:
            raise PortFailure({"code": e.code, "message": "admission denied"}) from e

    def observe_goal(self):
        from contracts.interfaces import PortFailure
        goal = self.gw.adapter.observe_goal(self.gw.ctx)
        if goal.observation:
            self.gw.store.observations.append(goal.observation)
            self.gw.store.evidence += goal.evidence
        if goal.verdict != "confirmed":
            raise PortFailure({"code": "EVIDENCE_INSUFFICIENT", "message": f"goal {goal.verdict}: {goal.reason}"})
        return goal.goal_observation
