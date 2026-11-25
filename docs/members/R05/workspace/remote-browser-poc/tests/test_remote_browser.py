"""원격 브라우저 PoC 종단 시험.

'사용자'는 서버와 별개의 브라우저(Playwright)로 뷰어 웹페이지를 열고,
캔버스에 마우스 클릭과 키보드 입력을 보내 모의 사이트에 직접 로그인한다.
서버 프로그램은 비밀번호를 받지 않고, 같은 원격 브라우저 세션으로 등록 작업을 수행한다.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from PIL import Image
from playwright.sync_api import sync_playwright
from websockets.sync.client import connect as ws_connect

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
MOCK_PORT, CTL_PORT, CTL_TTL_PORT = 18001, 18002, 18003
MOCK = f"http://127.0.0.1:{MOCK_PORT}"
CTL = f"http://127.0.0.1:{CTL_PORT}"
PW_A, PW_B = "Mock-Pass-A!2026", "Mock-Pass-B!2026"
SAVE_DELAY = 1.5
RESULTS: list[dict] = []


def record(test: str, verdict: str, **observed):
    RESULTS.append({"test": test, "verdict": verdict, **observed})
    (EVIDENCE / "results.json").write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding="utf-8")


def _wait_http(url: str, timeout: float = 30) -> None:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if httpx.get(url, timeout=2).status_code < 500:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.3)
    raise RuntimeError(f"server not ready: {url}")


def _start(module: str, port: int, env: dict, log_name: str) -> subprocess.Popen:
    out = open(EVIDENCE / log_name, "w", encoding="utf-8")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{module}:app", "--port", str(port), "--no-access-log"],
        cwd=ROOT, env={**os.environ, **env}, stdout=out, stderr=subprocess.STDOUT,
    )


@pytest.fixture(scope="module")
def servers():
    EVIDENCE.mkdir(exist_ok=True)
    for f in EVIDENCE.glob("*"):
        f.unlink()
    mock = _start("mock_site.app", MOCK_PORT, {"MOCK_SAVE_DELAY_SEC": str(SAVE_DELAY)}, "mock_site.stdout.log")
    ctl_env = {"MOCK_BASE": MOCK, "CONTROL_LOG": str(EVIDENCE / "control_server.log.jsonl"), "EVIDENCE_DIR": str(EVIDENCE)}
    ctl = _start("control_server.app", CTL_PORT, ctl_env, "control_server.stdout.log")
    ctl_ttl = _start("control_server.app", CTL_TTL_PORT,
                     {**ctl_env, "SESSION_IDLE_TTL_SEC": "2", "CONTROL_LOG": str(EVIDENCE / "control_server_ttl.log.jsonl")},
                     "control_server_ttl.stdout.log")
    _wait_http(f"{MOCK}/login")
    _wait_http(f"{CTL}/")
    _wait_http(f"http://127.0.0.1:{CTL_TTL_PORT}/")
    yield
    for p in (ctl, ctl_ttl, mock):
        p.terminate()
        p.wait(timeout=10)


@pytest.fixture(scope="module")
def pw():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def state():
    return {}


def png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (652, 488), (40, 60, 140)).save(buf, format="PNG")
    return buf.getvalue()


def api(sid: str, token: str, method: str = "GET", path: str = "", **kw) -> httpx.Response:
    return httpx.request(method, f"{CTL}/api/sessions/{sid}{path}", headers={"X-Session-Token": token}, timeout=30, **kw)


def stats() -> dict:
    return httpx.get(f"{MOCK}/__test__/stats").json()


def open_viewer(pw, sid: str, token: str):
    """사용자의 일반 웹 브라우저로 뷰어 페이지를 연다 (서버 브라우저와 다른 프로세스)."""
    browser = pw.chromium.launch(channel=os.environ.get("CHROME_CHANNEL", "chrome") or None, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1000})
    page.goto(f"{CTL}/view/{sid}#t={token}")
    page.wait_for_function("document.getElementById('state').textContent.includes('페이지:')", timeout=15000)
    return browser, page


def remote_click(page, x: float, y: float) -> None:
    """원격 화면 좌표(1280x800)를 뷰어 캔버스 좌표로 바꿔 사용자 마우스로 클릭한다."""
    box = page.locator("#screen").bounding_box()
    page.mouse.click(box["x"] + x * box["width"] / 1280, box["y"] + y * box["height"] / 800)


def wait_status(sid: str, token: str, pred, timeout: float = 20) -> dict:
    end = time.time() + timeout
    last = None
    while time.time() < end:
        last = api(sid, token).json()
        if pred(last):
            return last
        time.sleep(0.25)
    raise AssertionError(f"status condition not met: {last}")


def canvas_not_blank(page) -> bool:
    return page.evaluate("""() => {
      const c = document.getElementById('screen'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
      let lit = 0; for (let i = 0; i < d.length; i += 4 * 97) { if (d[i] + d[i+1] + d[i+2] > 60) lit++; } return lit > 50; }""")


def login_through_viewer(page, username: str, password: str) -> None:
    remote_click(page, 190, 138)          # 원격 화면의 아이디 입력란
    page.keyboard.type(username, delay=20)
    remote_click(page, 190, 198)          # 비밀번호 입력란
    page.keyboard.type(password, delay=20)
    remote_click(page, 100, 260)          # 로그인 버튼


def ws_session(sid: str, token: str):
    ws = ws_connect(f"ws://127.0.0.1:{CTL_PORT}/ws/{sid}")
    ws.send(json.dumps({"t": "auth", "token": token}))
    return ws


def ws_wait(ws, types: set[str], timeout: float = 10) -> dict:
    end = time.time() + timeout
    while time.time() < end:
        msg = json.loads(ws.recv(timeout=max(0.1, end - time.time())))
        if msg["type"] in types:
            return msg
    raise AssertionError(f"no message of {types}")


# ---------------------------------------------------------------------------
def test_01_remote_view(servers, pw, state):
    r = httpx.post(f"{CTL}/api/sessions").json()
    state["a"] = (r["session_id"], r["token"])
    browser, page = open_viewer(pw, *state["a"])
    page.wait_for_function("(() => { const c=document.getElementById('screen'); return c && true })()")
    deadline = time.time() + 10
    while not canvas_not_blank(page) and time.time() < deadline:
        time.sleep(0.2)
    shown = canvas_not_blank(page)
    hash_removed = "#t=" not in page.url
    page.screenshot(path=str(EVIDENCE / "T01_viewer_remote_login_page.png"))
    state["viewer_a"] = (browser, page)
    record("T01 원격 화면 표시", "pass" if shown and hash_removed else "fail",
           canvas_has_frame=shown, token_removed_from_address_bar=hash_removed)
    assert shown and hash_removed


def test_02_user_logs_in_through_remote_browser(servers, state):
    sid, token = state["a"]
    _, page = state["viewer_a"]
    login_through_viewer(page, "tutor_a", PW_A)
    st = wait_status(sid, token, lambda s: s["page_path"] == "/dashboard")
    page.wait_for_function("document.getElementById('state').textContent.includes('/dashboard')", timeout=10000)
    time.sleep(0.8)
    page.screenshot(path=str(EVIDENCE / "T02_viewer_after_remote_login.png"))
    count = stats()["login_count"]["tutor_a"]
    record("T02 원격 브라우저로 사용자가 직접 로그인", "pass" if count == 1 else "fail",
           remote_page=st["page_path"], viewer_status_bar=page.locator("#state").inner_text(), mock_login_count=count)
    assert count == 1


def test_03_disconnect_then_server_continues(servers, state):
    sid, token = state["a"]
    browser, _ = state.pop("viewer_a")
    browser.close()                                   # 사용자가 웹페이지 접속을 종료
    st = wait_status(sid, token, lambda s: s["viewers"] == 0)
    img = png_bytes()
    body = {"title": "원격 브라우저 PoC 보컬 레슨", "description": "서버 작업이 입력한 설명입니다.",
            "price": 50000, "image_name": "main.png", "image_b64": base64.b64encode(img).decode()}
    t0 = time.time()
    h = api(sid, token, "POST", "/handoff", json=body)
    running = api(sid, token).json()
    done = wait_status(sid, token, lambda s: s["job"] and s["job"]["state"] == "done", timeout=40)
    s = stats()
    lesson = next((l for l in s["lessons"] if l["id"] == done["job"]["lesson_id"]), None)
    ok = (h.status_code == 202 and running["viewers"] == 0 and done["job"]["result_state"] == "mock_success"
          and lesson and lesson["owner"] == "tutor_a" and lesson["image_sha256"] == hashlib.sha256(img).hexdigest()
          and lesson["title"] == body["title"] and lesson["price"] == 50000)
    no_relogin = s["login_count"]["tutor_a"] == 1 and "login" not in " ".join(done["job"]["steps"])
    state["lesson_title"] = body["title"]
    record("T03 접속 종료 후 서버가 같은 세션으로 텍스트 입력·이미지 첨부·저장·결과 확인",
           "pass" if ok else "fail", viewers_during_job=running["viewers"], job=done["job"],
           elapsed_sec=round(time.time() - t0, 2), saved_lesson=lesson)
    record("T04 재로그인 없이 인증 페이지 접근", "pass" if no_relogin else "fail",
           mock_login_count=s["login_count"]["tutor_a"], job_steps=done["job"]["steps"])
    assert ok and no_relogin


def test_05_control_lock_and_auto_return(servers, state):
    sid, token = state["a"]
    ws = ws_session(sid, token)
    ws_wait(ws, {"status"})
    body = {"title": "제어권 시험", "description": "잠금 확인", "price": 1000, "image_b64": base64.b64encode(png_bytes()).decode()}
    assert api(sid, token, "POST", "/handoff", json=body).status_code == 202
    second = api(sid, token, "POST", "/handoff", json=body).status_code   # 중복 맡기기 차단
    ws.send(json.dumps({"t": "key", "key": "Tab"}))
    rejected = ws_wait(ws, {"input_rejected", "input_ok"})
    done = wait_status(sid, token, lambda s: s["job"]["state"] == "done", timeout=40)
    ws.send(json.dumps({"t": "key", "key": "Tab"}))
    accepted = ws_wait(ws, {"input_rejected", "input_ok"})
    ws.close()
    ok = (second == 409 and rejected["type"] == "input_rejected" and done["control"] == "user"
          and accepted["type"] == "input_ok" and done["job"]["result_state"] == "mock_success")
    record("T05 서버 작업 중 사용자 입력 차단, 완료 후 제어권 자동 반환", "pass" if ok else "fail",
           duplicate_handoff_status=second, input_during_job=rejected["type"],
           control_after_job=done["control"], input_after_job=accepted["type"])
    assert ok


def test_06_return_control_with_cancel(servers, state):
    sid, token = state["a"]
    before = len([l for l in stats()["lessons"] if l["owner"] == "tutor_a"])
    body = {"title": "중단 시험", "description": "제어권 회수", "price": 2000, "image_b64": base64.b64encode(png_bytes()).decode()}
    api(sid, token, "POST", "/handoff", json=body)
    no_cancel = api(sid, token, "POST", "/return").status_code
    r = api(sid, token, "POST", "/return", params={"cancel": "true"})
    st = r.json()
    time.sleep(SAVE_DELAY + 1)
    after = len([l for l in stats()["lessons"] if l["owner"] == "tutor_a"])
    ok = (no_cancel == 409 and r.status_code == 200 and st["control"] == "user"
          and st["job"]["result_state"] in {"cancelled", "unknown"} and after - before <= 1)
    record("T06 진행 중 제어권 회수(작업 중단)", "pass" if ok else "fail",
           return_without_cancel=no_cancel, result_state=st["job"]["result_state"],
           submitted=st["job"]["submitted"], lessons_added=after - before,
           note="제출 이후 중단되면 unknown으로 남기고 재시도하지 않는다")
    assert ok


def test_07_session_isolation(servers, state):
    sid_a, token_a = state["a"]
    r = httpx.post(f"{CTL}/api/sessions").json()
    sid_b, token_b = r["session_id"], r["token"]
    state["b"] = (sid_b, token_b)
    wrong_token = api(sid_b, token_a).status_code
    ws = ws_connect(f"ws://127.0.0.1:{CTL_PORT}/ws/{sid_b}")
    ws.send(json.dumps({"t": "auth", "token": token_a}))
    denied = json.loads(ws.recv(timeout=5))["type"]
    ws.close()
    body = {"title": "격리 시험", "description": "로그인 안 된 세션", "price": 1, "image_b64": base64.b64encode(png_bytes()).decode()}
    api(sid_b, token_b, "POST", "/handoff", json=body)
    done = wait_status(sid_b, token_b, lambda s: s["job"] and s["job"]["state"] == "done")
    s = stats()
    ok = (wrong_token == 404 and denied == "denied" and done["job"]["result_state"] == "needs_login"
          and not done["job"]["submitted"] and s["login_count"]["tutor_a"] == 1)
    record("T07 사용자별 세션 격리", "pass" if ok else "fail",
           other_token_status=wrong_token, other_token_ws=denied,
           new_session_job=done["job"]["result_state"], tutor_a_login_count=s["login_count"]["tutor_a"])
    assert ok


def test_08_image_failure_not_reported_as_success(servers, pw, state):
    sid_b, token_b = state["b"]
    browser, page = open_viewer(pw, sid_b, token_b)
    login_through_viewer(page, "tutor_b", PW_B)
    wait_status(sid_b, token_b, lambda s: s["page_path"] == "/dashboard")
    browser.close()
    body = {"title": "이미지 오류 시험", "description": "PNG가 아닌 파일", "price": 1,
            "image_name": "bad.png", "image_b64": base64.b64encode(b"not an image").decode()}
    api(sid_b, token_b, "POST", "/handoff", json=body)
    done = wait_status(sid_b, token_b, lambda s: s["job"]["state"] == "done", timeout=30)
    saved = [l for l in stats()["lessons"] if l["owner"] == "tutor_b"]
    ok = done["job"]["result_state"] == "failed" and not saved
    record("T08 이미지 첨부 실패를 성공으로 판정하지 않음", "pass" if ok else "fail",
           result_state=done["job"]["result_state"], message=done["job"]["message"], tutor_b_lessons=len(saved))
    assert ok


def test_09_end_session(servers, state):
    sid, token = state["a"]
    d = api(sid, token, "DELETE")
    after = api(sid, token).status_code
    ws = ws_connect(f"ws://127.0.0.1:{CTL_PORT}/ws/{sid}")
    ws.send(json.dumps({"t": "auth", "token": token}))
    denied = json.loads(ws.recv(timeout=5))["type"]
    ws.close()
    # 같은 사용자라도 새 세션은 로그인되어 있지 않아야 한다(쿠키가 폐기됨).
    r = httpx.post(f"{CTL}/api/sessions").json()
    body = {"title": "종료 후", "description": "새 세션", "price": 1, "image_b64": base64.b64encode(png_bytes()).decode()}
    api(r["session_id"], r["token"], "POST", "/handoff", json=body)
    fresh = wait_status(r["session_id"], r["token"], lambda s: s["job"] and s["job"]["state"] == "done")
    api(r["session_id"], r["token"], "DELETE")
    ok = d.status_code == 200 and after == 404 and denied == "denied" and fresh["job"]["result_state"] == "needs_login"
    record("T09 세션 종료", "pass" if ok else "fail", delete_status=d.status_code,
           status_after_delete=after, ws_after_delete=denied, new_session_job=fresh["job"]["result_state"])
    assert ok


def test_10_idle_timeout(servers):
    base = f"http://127.0.0.1:{CTL_TTL_PORT}"
    r = httpx.post(f"{base}/api/sessions").json()
    first = httpx.get(f"{base}/api/sessions/{r['session_id']}", headers={"X-Session-Token": r["token"]}).status_code
    time.sleep(4.5)
    later = httpx.get(f"{base}/api/sessions/{r['session_id']}", headers={"X-Session-Token": r["token"]}).status_code
    ok = first == 200 and later == 404
    record("T10 방치된 세션 자동 종료(TTL 2초 설정)", "pass" if ok else "fail", before=first, after_4_5s=later)
    assert ok


def test_12_auto_start_after_login(servers, pw, state):
    """레슨 내용을 미리 맡긴 세션: 사용자는 로그인만 하고 페이지를 닫는다. 서버가 자동으로 등록한다."""
    before = len(stats()["lessons"])
    img = png_bytes()
    job = {"title": "로그인만 하면 자동 등록", "description": "자동 시작 시험", "price": 30000,
           "image_name": "auto.png", "image_b64": base64.b64encode(img).decode()}
    r = httpx.post(f"{CTL}/api/sessions", json={"auto_job": job}).json()
    sid, token = r["session_id"], r["token"]
    browser, page = open_viewer(pw, sid, token)
    login_through_viewer(page, "tutor_b", PW_B)
    page.wait_for_function("document.getElementById('state').textContent.includes('서버')", timeout=15000)
    page.screenshot(path=str(EVIDENCE / "T12_viewer_auto_started.png"))
    browser.close()                                           # 로그인 직후 사용자가 떠남
    done = wait_status(sid, token, lambda s: s["job"] and s["job"]["state"] == "done", timeout=40)
    s = stats()
    lesson = next((l for l in s["lessons"] if l["id"] == done["job"]["lesson_id"]), None)
    log = (EVIDENCE / "control_server.log.jsonl").read_text(encoding="utf-8")
    handoff_calls = [l for l in log.splitlines() if f'"session": "{sid}"' in l and '"event": "handoff"' in l]
    ok = (done["job"]["result_state"] == "mock_success" and lesson and lesson["owner"] == "tutor_b"
          and lesson["image_sha256"] == hashlib.sha256(img).hexdigest() and len(s["lessons"]) == before + 1
          and not handoff_calls and f'"event": "auto_handoff", "session": "{sid}"' in log)
    record("T12 로그인만 하면 서버가 자동으로 이어서 등록", "pass" if ok else "fail",
           result_state=done["job"]["result_state"], lessons_added=len(s["lessons"]) - before,
           manual_handoff_calls=len(handoff_calls), viewers_during_job=done["viewers"])
    api(sid, token, "DELETE")
    assert ok


def test_11_no_sensitive_data_exposed(servers, state):
    secrets_to_find = [PW_A, PW_B, "mock_sid"]
    hits = {}
    for f in EVIDENCE.glob("*"):
        if f.suffix in {".log", ".jsonl", ".json", ".txt"}:
            text = f.read_text(encoding="utf-8", errors="ignore")
            found = [s for s in secrets_to_find if s in text]
            if found:
                hits[f.name] = found
    sid_b, token_b = state["b"]
    status_text = json.dumps(api(sid_b, token_b).json(), ensure_ascii=False)
    log_lines = [json.loads(l) for l in (EVIDENCE / "control_server.log.jsonl").read_text(encoding="utf-8").splitlines()]
    token_in_log = any(token_b in json.dumps(l) for l in log_lines)
    keystroke_events = [l for l in log_lines if l.get("event") == "input" and l.get("kind") != "mouse"]
    ok = not hits and not any(s in status_text for s in secrets_to_find) and not token_in_log and not keystroke_events
    record("T11 비밀번호·쿠키·세션 토큰·입력 길이 미노출", "pass" if ok else "fail",
           files_checked=sorted(f.name for f in EVIDENCE.glob("*")), hits=hits, token_in_log=token_in_log,
           keystroke_log_events=len(keystroke_events))
    assert ok
