"""Neutral synthetic site for r05-remote tests (not any real platform; loopback only).

Login inputs sit at fixed coordinates so tests can sign in purely through viewer input.
A generic "work" object goes through value/file/mark/submit steps and can be read back by slot.
Duplicate submissions are NOT blocked here (only counted). Faults are in-process only.
"""
from __future__ import annotations

import email
import email.policy
import hashlib
import html
import http.cookies
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, unquote

LOGIN_POS = {"username": (190, 138), "password": (190, 198), "login": (100, 260)}


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def field(name, value):
    return f'<span data-field="{esc(name)}" style="white-space:pre-wrap">{esc(value)}</span>'


class NeutralSite:
    def __init__(self, accounts=("acct-a", "acct-b"), extra_html: str = ""):
        self.accounts = {a: secrets.token_urlsafe(10) for a in accounts}
        self.sessions: dict[str, str] = {}
        self.works: dict[str, dict] = {}
        self.receipts: dict[tuple, list] = {}
        self.posts: list[tuple] = []
        self.logins = 0
        self.submissions = 0
        self.submit_requests: list[dict] = []
        self.hits = 0
        self.faults: dict[str, str] = {}
        self.extra_html = extra_html
        self.lock = threading.Lock()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def origin(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def page(self, key, body, account=None):
        head = ("<p>" + field("account_ref", account) + "</p>") if account else ""
        return (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(key)}</title>'
                '<style>body{margin:0;font:14px sans-serif} .abs{position:absolute}</style></head>'
                f'<body data-page="{esc(key)}">{head}{body}</body></html>')

    def _handler(self):
        site = self

        class H(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def respond(self, status, body, location=None, cookie=None, ctype="text/html; charset=utf-8"):
                raw = body.encode() if isinstance(body, str) else body
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                if location:
                    self.send_header("Location", location)
                if cookie:
                    self.send_header("Set-Cookie", f"ns={cookie}; Path=/; HttpOnly")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def form(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length", "0") or 0))
                ctype = self.headers.get("Content-Type", "")
                if ctype.startswith("multipart/form-data"):
                    msg = email.message_from_bytes(b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw,
                                                   policy=email.policy.HTTP)
                    fields, files = {}, []
                    for part in msg.iter_parts():
                        data = part.get_payload(decode=True) or b""
                        if part.get_filename() is not None:
                            if data:
                                files.append(data)
                        else:
                            fields[part.get_param("name", header="content-disposition")] = data.decode()
                    return fields, files
                return dict(parse_qsl(raw.decode(), keep_blank_values=True)), []

            def account(self):
                c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
                return site.sessions.get(c["ns"].value) if "ns" in c else None

            def do_GET(self):
                with site.lock:
                    site.hits += 1
                    self.route("GET")

            def do_POST(self):
                with site.lock:
                    site.hits += 1
                    self.route("POST")

            def route(self, method):
                path = self.path.split("?", 1)[0]
                if path == "/pixel.png":
                    return self.respond(200, b"", ctype="image/png")
                if path == "/login":
                    if method == "GET":
                        x = LOGIN_POS
                        return self.respond(200, site.page("login", (
                            '<form method="post" action="/login">'
                            f'<input class="abs" name="username" autocomplete="off" style="left:{x["username"][0]-90}px;top:{x["username"][1]-12}px;width:180px;height:24px">'
                            f'<input class="abs" name="password" type="password" style="left:{x["password"][0]-90}px;top:{x["password"][1]-12}px;width:180px;height:24px">'
                            f'<button class="abs" type="submit" name="login" value="1" style="left:{x["login"][0]-50}px;top:{x["login"][1]-15}px;width:100px;height:30px">login</button>'
                            '</form>')))
                    f, _ = self.form()
                    if site.accounts.get(f.get("username")) and secrets.compare_digest(site.accounts[f["username"]], f.get("password", "")):
                        sid = secrets.token_hex(12)
                        site.sessions[sid] = f["username"]
                        site.logins += 1
                        return self.respond(303, "", location="/account", cookie=sid)
                    return self.respond(401, site.page("login", field("error", "bad login")))
                acct = self.account()
                if acct is None:
                    return self.respond(303, "", location="/login")
                if path == "/account":
                    return self.respond(200, site.page("account", field("account_label", f"합성 {acct}") + site.extra_html, acct))
                m = re.fullmatch(r"/slots/([^/]+)", path)
                if m:
                    if site.faults.get("readback") == "drop":
                        self.close_connection = True
                        return
                    rs = site.receipts.get((acct, unquote(m.group(1))), [])
                    if not rs:
                        return self.respond(404, site.page("slot_absent", "", acct))
                    r = rs[-1]
                    body = (field("receipt_id", r["id"]) + field("state", "mock_submitted") + field("slot_ref", r["slot"])
                            + field("receipt_count", len(rs)) + field("payload", r["payload"])
                            + "".join(field("asset_digest", d) for d in r["digests"]))
                    return self.respond(200, site.page("slot", body, acct))
                if path == "/work/new":
                    if method == "GET":
                        return self.respond(200, site.page("work_new", '<form method="post" action="/work/new"><input name="slot_ref"><button type="submit" name="start" value="1">start</button></form>', acct))
                    f, _ = self.form()
                    wid = "w-" + secrets.token_hex(6)
                    site.works[wid] = {"id": wid, "account": acct, "slot": f.get("slot_ref", ""), "payload": "", "files": [], "marks": []}
                    site.posts.append(("start", acct))
                    return self.respond(303, "", location=f"/work/{wid}")
                m = re.fullmatch(r"/work/(w-[0-9a-f]+)(?:/(values|files|mark|submit|submit-final))?", path)
                if not m or site.works.get(m.group(1), {}).get("account") != acct:
                    return self.respond(404, site.page("not_found", "", acct))
                w, step = site.works[m.group(1)], m.group(2)
                if method == "GET" and step is None:
                    digests = [hashlib.sha256(d).hexdigest() for d in w["files"]]
                    body = (field("work_id", w["id"]) + field("slot_ref", w["slot"]) + field("payload", w["payload"])
                            + "".join(field("asset_digest", d) for d in digests) + "".join(field("mark", s) for s in w["marks"])
                            + f'<form method="post" action="/work/{w["id"]}/values"><textarea name="payload"></textarea><button type="submit" name="save_values" value="1">save</button></form>'
                            + f'<form method="post" action="/work/{w["id"]}/files" enctype="multipart/form-data"><input type="file" name="files" multiple><button type="submit" name="save_files" value="1">upload</button></form>'
                            + f'<form method="post" action="/work/{w["id"]}/mark"><input name="step"><button type="submit" name="mark" value="1">mark</button></form>'
                            + f'<form method="post" action="/work/{w["id"]}/submit"><button type="submit" name="submit_work" value="1">submit</button></form>')
                    return self.respond(200, site.page("work", body, acct))
                if method != "POST" or step is None:
                    return self.respond(405, site.page("not_allowed", "", acct))
                f, files = self.form()
                site.posts.append((step, acct))
                if step in ('submit', 'submit-final'):
                    site.submit_requests.append({'path': path, 'method': method})
                    redirect = site.faults.get('submit_redirect') if step == 'submit' else None
                    destination = site.faults.get('redirect_target', f'/work/{w["id"]}/submit-final')
                    if redirect and site.faults.get('redirect_phase') == 'before_commit':
                        return self.respond(int(redirect), '', location=destination)
                if step == "values":
                    w["payload"] = f.get("payload", "").replace("\r\n", "\n")
                elif step == "files":
                    w["files"] = files
                elif step == "mark":
                    w["marks"].append(f.get("step", ""))
                elif step in ("submit", "submit-final"):
                    rid = "r-" + secrets.token_hex(6)
                    site.receipts.setdefault((acct, w["slot"]), []).append(
                        {"id": rid, "slot": w["slot"], "payload": w["payload"],
                         "digests": [hashlib.sha256(d).hexdigest() for d in w["files"]]})
                    site.submissions += 1
                    if redirect:
                        return self.respond(int(redirect), '', location=destination)
                    if site.faults.get("submit") == "drop_after_commit":
                        self.close_connection = True
                        return
                    return self.respond(200, site.page("submitted", field("receipt_id", rid) + field("state", "mock_submitted"), acct))
                return self.respond(303, "", location=f"/work/{w['id']}")

        return H
