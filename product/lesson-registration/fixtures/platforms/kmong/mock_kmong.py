"""Synthetic Kmong-like listing site for r05-kmong tests (mock only, loopback only).

Not the real Kmong. Field names, limits and option lists follow the pinned mock profile
``kmong.service_listing.mock.v2`` and its fixture_rules; the title character rule follows
R05's manual observation of the registration form (TASK-045) and is a mock assumption.

The site intentionally does NOT block duplicate submissions; it only counts them, so tests
can prove the adapter/gateway prevent duplicates. Faults are configured in-process only.

Run standalone:  python fixtures/platforms/kmong/mock_kmong.py --port 0
"""
from __future__ import annotations

import argparse
import email
import email.policy
import hashlib
import html
import http.cookies
import os
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, quote, unquote, urlsplit

CATEGORY_PATHS = (("lesson", "music", "vocal_mock"), ("lesson", "music", "rap_mock"))
REGION_PAIRS = (("mock_region", "mock_district"),)
TIERS = ("STANDARD", "DELUXE", "PREMIUM")
WORK_DAYS = (7, 14, 30)
REVISIONS = (0, 1, 2)
MINUTES = (90, 180, 270)
SESSIONS = (4,)
PERIODS = ("month",)
IMAGE_SIZE = (652, 488)
TITLE_CHARS = re.compile(r"^[0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ +\-#/.()]+$")
SLOT_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
DRAFT_RE = re.compile(r"^d-[0-9a-f]{16}$")
MAX_BODY = 12 * 1024 * 1024
SEP = ">"


def image_size(data: bytes):
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return "image/png", int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                return None
            marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
            if marker in (0xC0, 0xC1, 0xC2):
                return "image/jpeg", int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
            i += 2 + length
    return None


def esc(v) -> str:
    return html.escape(str(v), quote=True)


class MockKmong:
    """In-process synthetic site. ``accounts`` maps account_ref -> random synthetic password."""

    def __init__(self, accounts=("mock-account-kmong",), port: int = 0):
        if os.environ.get("LR_ENVIRONMENT", "mock") != "mock":
            raise RuntimeError("mock only")
        self.accounts = {a: secrets.token_urlsafe(12) for a in accounts}
        self.sessions: dict[str, str] = {}
        self.drafts: dict[str, dict] = {}
        self.receipts: dict[tuple, list] = {}
        self.submissions = 0
        self.requests: list[tuple] = []
        self.faults: dict[str, str] = {}
        self.lock = threading.Lock()
        self.server = ThreadingHTTPServer(("127.0.0.1", port), self._handler())
        self.server.daemon_threads = True
        self.thread = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}"

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        if self.thread:
            self.thread.join(5)

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()

    # ---------- validation ----------
    @staticmethod
    def _text(form, name, lo, hi, errors):
        v = form.get(name, "").replace("\r\n", "\n")
        if not lo <= len(v) <= hi:
            errors.append(f"{name}: {lo}~{hi}자")
        return v

    def validate_basic(self, form):
        errors = []
        title = self._text(form, "title", 10, 30, errors)
        if title and not TITLE_CHARS.match(title):
            errors.append("title: 허용되지 않은 문자")
        cat = tuple(form.get("category_path", "").split(SEP))
        if cat not in CATEGORY_PATHS:
            errors.append("category_path: 목록에 없는 카테고리")
        out = {"title": title, "category_path": list(cat),
               "description": self._text(form, "description", 100, 20000, errors),
               "recruitment": form.get("recruitment", ""), "delivery": form.get("delivery", ""),
               "process": self._text(form, "process", 50, 20000, errors),
               "preparation": self._text(form, "preparation", 50, 20000, errors), "region": None}
        if out["recruitment"] not in ("individual", "group", "corporate"):
            errors.append("recruitment: 선택 필요")
        if out["delivery"] == "offline":
            pair = (form.get("region_key", ""), form.get("district_key", ""))
            addr = form.get("detail_address", "")
            if pair not in REGION_PAIRS:
                errors.append("region: 지역 선택 필요")
            if not 1 <= len(addr) <= 200:
                errors.append("detail_address: 1~200자")
            if form.get("public_scope_confirmed") != "true":
                errors.append("public_scope_confirmed: 공개 범위 확인 필요")
            out["region"] = {"region_key": pair[0], "district_key": pair[1], "detail_address": addr,
                             "public_scope_confirmed": True}
        elif out["delivery"] != "online":
            errors.append("delivery: 선택 필요")
        return out, errors

    def validate_packages(self, form):
        errors, pkgs = [], []
        for t in TIERS:
            def num(k, allowed=None, lo=0):
                raw = form.get(f"pkg.{t}.{k}", "")
                if not re.fullmatch(r"\d{1,15}", raw):
                    errors.append(f"{t}.{k}: 숫자 필요")
                    return None
                n = int(raw)
                if (allowed and n not in allowed) or n < lo:
                    errors.append(f"{t}.{k}: 허용되지 않은 값")
                return n
            p = {"tier": t, "title": form.get(f"pkg.{t}.title", ""), "description": form.get(f"pkg.{t}.description", ""),
                 "amount_vat_included_krw": num("amount_vat_included_krw"), "work_days": num("work_days", WORK_DAYS),
                 "revision_count": num("revision_count", REVISIONS), "minutes_per_session": num("minutes_per_session", MINUTES),
                 "sessions": num("sessions", SESSIONS), "period": form.get(f"pkg.{t}.period", "")}
            if not 1 <= len(p["title"]) <= 20:
                errors.append(f"{t}.title: 1~20자")
            if not 1 <= len(p["description"]) <= 60:
                errors.append(f"{t}.description: 1~60자")
            if p["period"] not in PERIODS:
                errors.append(f"{t}.period: 허용되지 않은 값")
            pkgs.append(p)
        return pkgs, errors

    def validate_images(self, files):
        errors = []
        if not 1 <= len(files) <= 4:
            errors.append("main_images: 1~4장")
        for name, data in files:
            info = image_size(data)
            if not info:
                errors.append(f"{name}: PNG/JPG만 가능")
            elif info[1:] != IMAGE_SIZE:
                errors.append(f"{name}: 652x488 필요")
        return errors

    # ---------- rendering ----------
    @staticmethod
    def field(name, value, tag="span"):
        return f'<{tag} data-field="{esc(name)}" style="white-space:pre-wrap">{esc(value)}</{tag}>'

    def page(self, key, body, account=None, draft=None, error_code=None, errors=()):
        head = []
        if account:
            head.append("<p>계정 " + self.field("account_ref", account) + "</p>")
        if draft:
            head.append("<p>초안 " + self.field("draft_id", draft["id"]) + " 슬롯 " + self.field("slot_ref", draft["slot"]) + "</p>")
        if error_code:
            head.append("<div role=alert>" + self.field("error_code", error_code) +
                        "".join("<p>" + self.field("error", e) + "</p>" for e in errors) + "</div>")
        return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Mock Kmong · {esc(key)}</title></head>'
                f'<body data-page="{esc(key)}"><header>합성 크몽 모의 사이트 (실제 크몽 아님)</header>'
                + "".join(head) + body + "</body></html>")

    @staticmethod
    def select(name, options, current=""):
        opts = "".join(f'<option value="{esc(v)}"{" selected" if str(v) == str(current) else ""}>{esc(label)}</option>'
                       for v, label in options)
        return f'<label>{esc(name)} <select name="{esc(name)}">{opts}</select></label>'

    def basic_form(self, d):
        b = d.get("basic") or {}
        r = b.get("region") or {}
        return (f'<form method="post" action="/gigs/{d["id"]}/basic">'
                f'<label>서비스 제목 <input name="title" value="{esc(b.get("title", ""))}"></label>'
                + self.select("category_path", [("", "선택")] + [(SEP.join(c), SEP.join(c)) for c in CATEGORY_PATHS],
                              SEP.join(b.get("category_path", [])))
                + f'<label>서비스 설명 <textarea name="description">{esc(b.get("description", ""))}</textarea></label>'
                + self.select("recruitment", [("", "선택"), ("individual", "개인레슨"), ("group", "그룹교육"), ("corporate", "기업강의")], b.get("recruitment", ""))
                + self.select("delivery", [("", "선택"), ("offline", "오프라인"), ("online", "온라인")], b.get("delivery", ""))
                + self.select("region_key", [("", "선택")] + [(p[0], p[0]) for p in REGION_PAIRS], r.get("region_key", ""))
                + self.select("district_key", [("", "선택")] + [(p[1], p[1]) for p in REGION_PAIRS], r.get("district_key", ""))
                + f'<label>상세주소 <input name="detail_address" value="{esc(r.get("detail_address", ""))}"></label>'
                + '<label><input type="checkbox" name="public_scope_confirmed" value="true"> 공개 범위 확인</label>'
                + f'<label>서비스 제공 절차 <textarea name="process">{esc(b.get("process", ""))}</textarea></label>'
                + f'<label>의뢰인 준비사항 <textarea name="preparation">{esc(b.get("preparation", ""))}</textarea></label>'
                + '<button type="submit" name="save_basic" value="1">저장 후 다음</button></form>')

    def packages_form(self, d):
        rows = []
        for t in TIERS:
            p = next((x for x in d.get("packages") or [] if x["tier"] == t), {})
            pre = f"pkg.{t}."
            rows.append(f"<fieldset><legend>{t}</legend>"
                        f'<input name="{pre}title" value="{esc(p.get("title", ""))}">'
                        f'<input name="{pre}description" value="{esc(p.get("description", ""))}">'
                        f'<input name="{pre}amount_vat_included_krw" value="{esc(p.get("amount_vat_included_krw", ""))}">'
                        + self.select(pre + "work_days", [("", "선택")] + [(v, v) for v in WORK_DAYS], p.get("work_days", ""))
                        + self.select(pre + "revision_count", [("", "선택")] + [(v, v) for v in REVISIONS], p.get("revision_count", ""))
                        + self.select(pre + "minutes_per_session", [("", "선택")] + [(v, v) for v in MINUTES], p.get("minutes_per_session", ""))
                        + self.select(pre + "sessions", [("", "선택")] + [(v, v) for v in SESSIONS], p.get("sessions", ""))
                        + self.select(pre + "period", [("", "선택")] + [(v, v) for v in PERIODS], p.get("period", ""))
                        + "</fieldset>")
        return (f'<form method="post" action="/gigs/{d["id"]}/packages">' + "".join(rows)
                + '<button type="submit" name="save_packages" value="1">저장 후 다음</button></form>')

    def values_html(self, v, image_digests):
        parts = [self.field(k, v[k]) for k in ("title", "description", "recruitment", "delivery", "process", "preparation") if v.get(k) is not None]
        if v.get("category_path"):
            parts.append(self.field("category_path", SEP.join(v["category_path"])))
        if v.get("region"):
            r = v["region"]
            parts += [self.field(k, r[k]) for k in ("region_key", "district_key", "detail_address")]
            parts.append(self.field("public_scope_confirmed", "true" if r["public_scope_confirmed"] else "false"))
        for p in v.get("packages") or []:
            parts += [self.field(f"pkg.{p['tier']}.{k}", p[k]) for k in p if k != "tier"]
        parts += [self.field("asset_digest", dg) for dg in image_digests]
        return "<dl>" + "".join(f"<div>{x}</div>" for x in parts) + "</dl>"

    @staticmethod
    def snapshot(d):
        v = dict(d.get("basic") or {})
        v["packages"] = d.get("packages")
        return v, [hashlib.sha256(data).hexdigest() for _, data in d.get("images") or []]

    # ---------- HTTP ----------
    def _handler(self):
        site = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def respond(self, status, body, location=None, cookie=None):
                raw = body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                if location:
                    self.send_header("Location", location)
                if cookie:
                    self.send_header("Set-Cookie", f"mk_sid={cookie}; Path=/; HttpOnly; SameSite=Strict")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def redirect(self, path, cookie=None):
                self.respond(303, "", location=path, cookie=cookie)

            def drop(self):
                self.close_connection = True   # commit happened, response never sent

            def body(self):
                n = int(self.headers.get("Content-Length", "0") or 0)
                if not 0 <= n <= MAX_BODY:
                    raise ValueError("body limit")
                return self.rfile.read(n)

            def form(self, raw):
                ctype = self.headers.get("Content-Type", "")
                if ctype.startswith("multipart/form-data"):
                    msg = email.message_from_bytes(b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw, policy=email.policy.HTTP)
                    fields, files = {}, []
                    for part in msg.iter_parts():
                        name = part.get_param("name", header="content-disposition")
                        data = part.get_payload(decode=True) or b""
                        if part.get_filename() is not None:
                            if data:
                                files.append((part.get_filename(), data))
                        else:
                            fields[name] = data.decode("utf-8")
                    return fields, files
                return dict(parse_qsl(raw.decode("utf-8"), keep_blank_values=True)), []

            def account(self):
                c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                sid = c["mk_sid"].value if "mk_sid" in c else ""
                return site.sessions.get(sid)

            def handle_any(self):
                try:
                    u = urlsplit(self.path)
                    path = u.path
                    raw = self.body() if self.command == "POST" else b""
                    with site.lock:
                        site.requests.append((self.command, path))
                        return self.route(path, raw)
                except (ValueError, UnicodeError, http.cookies.CookieError):
                    return self.respond(400, site.page("bad_request", "", error_code="INVALID_REQUEST"))

            do_GET = do_POST = handle_any

            def route(self, path, raw):
                if path == "/login":
                    if self.command == "GET":
                        return self.respond(200, site.page("login", '<form method="post" action="/login"><input name="username"><input name="password" type="password"><button type="submit" name="login" value="1">로그인</button></form>'))
                    f, _ = self.form(raw)
                    if site.accounts.get(f.get("username")) and secrets.compare_digest(site.accounts[f["username"]], f.get("password", "")):
                        sid = secrets.token_hex(16)
                        site.sessions[sid] = f["username"]
                        return self.redirect("/home", cookie=sid)
                    return self.respond(401, site.page("login", "", error_code="UNAUTHENTICATED"))
                acct = self.account()
                if acct is None:
                    return self.redirect("/login")
                if path == "/home":
                    return self.respond(200, site.page("home", '<a href="/gigs/new">새 서비스 등록</a>', acct))
                if path == "/gigs/new":
                    if self.command == "GET":
                        return self.respond(200, site.page("new_listing", '<form method="post" action="/gigs/new"><input name="slot_ref"><button type="submit" name="start" value="1">등록 시작</button></form>', acct))
                    f, _ = self.form(raw)
                    slot = f.get("slot_ref", "")
                    if not SLOT_RE.match(slot):
                        return self.respond(422, site.page("new_listing", "", acct, error_code="VALIDATION_FAILED", errors=["slot_ref"]))
                    if site.receipts.get((acct, slot)):
                        return self.respond(409, site.page("slot_exists", "", acct, error_code="DUPLICATE_RISK"))
                    if any(d["account"] == acct and d["slot"] == slot for d in site.drafts.values()):
                        return self.respond(409, site.page("slot_draft_exists", "", acct, error_code="TARGET_AMBIGUOUS"))
                    did = "d-" + secrets.token_hex(8)
                    site.drafts[did] = {"id": did, "account": acct, "slot": slot, "status": "draft"}
                    return self.redirect(f"/gigs/{did}/basic")
                m = re.fullmatch(r"/slots/([^/]+)/receipt", path)
                if m and self.command == "GET":
                    slot = unquote(m.group(1))
                    rs = site.receipts.get((acct, slot), [])
                    if site.faults.get("readback") == "drop":
                        return self.drop()
                    if not rs:
                        return self.respond(404, site.page("receipt_absent", site.field("slot_ref", slot), acct))
                    r = rs[-1]
                    v = dict(r["values"])
                    digests = list(r["image_digests"])
                    if site.faults.get("tamper_readback") == "title":
                        v["title"] = v["title"] + "X"
                    if site.faults.get("tamper_readback") == "image":
                        digests = ["0" * 64] + digests[1:]
                    body = (site.field("receipt_id", r["id"]) + site.field("state", "mock_submitted")
                            + site.field("slot_ref", slot) + site.field("receipt_count", len(rs)) + site.values_html(v, digests))
                    return self.respond(200, site.page("receipt", body, acct))
                m = re.fullmatch(r"/gigs/([^/]+)/(basic|images|packages|review|submit)", path)
                if not m or not DRAFT_RE.match(m.group(1)) or site.drafts.get(m.group(1), {}).get("account") != acct:
                    return self.respond(404, site.page("not_found", "", acct, error_code="NOT_FOUND"))
                d, step = site.drafts[m.group(1)], m.group(2)
                return getattr(self, "step_" + step)(acct, d, raw)

            def step_basic(self, acct, d, raw):
                if self.command == "GET":
                    return self.respond(200, site.page("basic", site.basic_form(d), acct, d))
                f, _ = self.form(raw)
                values, errors = site.validate_basic(f)
                if errors:
                    return self.respond(422, site.page("basic", site.basic_form(d), acct, d, "VALIDATION_FAILED", errors))
                d["basic"] = values
                return self.redirect(f"/gigs/{d['id']}/images")

            def step_images(self, acct, d, raw):
                form = (f'<form method="post" action="/gigs/{d["id"]}/images" enctype="multipart/form-data">'
                        '<input type="file" name="main_images" multiple accept="image/png,image/jpeg">'
                        '<button type="submit" name="save_images" value="1">저장 후 다음</button></form>')
                if self.command == "GET":
                    return self.respond(200, site.page("images", form, acct, d))
                _, files = self.form(raw)
                errors = site.validate_images(files)
                if errors:
                    return self.respond(422, site.page("images", form, acct, d, "VALIDATION_FAILED", errors))
                d["images"] = files
                return self.redirect(f"/gigs/{d['id']}/packages")

            def step_packages(self, acct, d, raw):
                if self.command == "GET":
                    return self.respond(200, site.page("packages", site.packages_form(d), acct, d))
                f, _ = self.form(raw)
                pkgs, errors = site.validate_packages(f)
                if errors:
                    return self.respond(422, site.page("packages", site.packages_form(d), acct, d, "VALIDATION_FAILED", errors))
                d["packages"] = pkgs
                return self.redirect(f"/gigs/{d['id']}/review")

            def step_review(self, acct, d, raw):
                if self.command != "GET":
                    return self.respond(405, site.page("not_allowed", "", acct))
                v, digests = site.snapshot(d)
                complete = bool(d.get("basic") and d.get("images") and d.get("packages"))
                body = site.values_html(v, digests) + site.field("complete", "true" if complete else "false")
                if complete:
                    body += (f'<form method="post" action="/gigs/{d["id"]}/submit">'
                             '<button type="submit" name="submit_review" value="1">심사 접수</button></form>')
                return self.respond(200, site.page("review", body, acct, d))

            def step_submit(self, acct, d, raw):
                if self.command != "POST":
                    return self.respond(405, site.page("not_allowed", "", acct))
                if not (d.get("basic") and d.get("images") and d.get("packages")):
                    return self.respond(422, site.page("review", "", acct, d, "VALIDATION_FAILED", ["incomplete"]))
                fault = site.faults.get("submit")
                if fault == "fail_before_commit":
                    return self.respond(503, site.page("unavailable", "", acct, d, "RUNTIME_ERROR", ["temporarily unavailable"]))
                if fault == "reject_validation":
                    return self.respond(422, site.page("review", "", acct, d, "VALIDATION_FAILED", ["rejected by mock rule"]))
                v, digests = site.snapshot(d)
                rid = "r-" + secrets.token_hex(8)
                site.receipts.setdefault((acct, d["slot"]), []).append({"id": rid, "values": v, "image_digests": digests})
                d["status"] = "submitted"
                site.submissions += 1
                if fault == "drop_after_commit":
                    return self.drop()
                body = site.field("receipt_id", rid) + site.field("state", "mock_submitted")
                return self.respond(200, site.page("submitted", body, acct, d))

        return Handler


def receipt_path(slot_ref: str) -> str:
    return "/slots/" + quote(slot_ref, safe="") + "/receipt"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    a = ap.parse_args()
    site = MockKmong(port=a.port)
    print(site.base_url, flush=True)
    for acct, pw in site.accounts.items():
        print(f"synthetic account {acct} / {pw}", flush=True)
    site.server.serve_forever()
