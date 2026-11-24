"""원격 브라우저 제어 서버 PoC.

- 서버에서 Chrome을 띄우고, 사용자별로 분리된 BrowserContext(쿠키 저장소가 따로인 창)를 만든다.
- 화면은 Chrome DevTools Protocol의 Page.startScreencast로 JPEG 프레임을 받아 WebSocket으로 중계한다.
- 사용자의 마우스·키보드 입력은 같은 WebSocket으로 받아 Playwright 입력으로 재생한다.
- 사용자가 로그인한 뒤 제어권을 넘기면, 서버 작업이 같은 BrowserContext(같은 쿠키)로 등록 업무를 수행한다.
- 뷰어 접속이 끊겨도 세션과 작업은 서버에서 계속된다.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from pydantic import BaseModel, Field

MOCK_BASE = os.environ.get("MOCK_BASE", "http://127.0.0.1:8001")
VIEWPORT = {"width": 1280, "height": 800}
CHROME_CHANNEL = os.environ.get("CHROME_CHANNEL", "chrome") or None  # 비우면 Playwright 번들 Chromium
IDLE_TTL_SEC = float(os.environ.get("SESSION_IDLE_TTL_SEC", "900"))
JOB_STEP_TIMEOUT_MS = int(os.environ.get("JOB_STEP_TIMEOUT_MS", "15000"))
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = Path(os.environ.get("CONTROL_LOG", BASE_DIR / "evidence" / "control_server.log.jsonl"))
EVIDENCE_DIR = Path(os.environ.get("EVIDENCE_DIR", BASE_DIR / "evidence"))

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
_log = logging.getLogger("control")
_log.setLevel(logging.INFO)
_fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(message)s"))
_log.addHandler(_fh)


def audit(event: str, **fields: Any) -> None:
    """감사 로그. 입력 문자·키 값·쿠키·비밀번호는 절대 넣지 않는다(호출부에서 넘기지 않음)."""
    _log.info(json.dumps({"ts": round(time.time(), 3), "event": event, **fields}, ensure_ascii=False))


# ---------------------------------------------------------------------------
# 세션
# ---------------------------------------------------------------------------
@dataclass
class Job:
    state: str = "running"            # running | done
    result_state: str | None = None   # mock_success | failed | unknown | needs_login | needs_confirmation | cancelled
    steps: list[str] = field(default_factory=list)
    submitted: bool = False
    lesson_id: int | None = None
    message: str | None = None
    evidence: str | None = None
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    def public(self) -> dict[str, Any]:
        return {
            "state": self.state, "result_state": self.result_state, "steps": self.steps,
            "submitted": self.submitted, "lesson_id": self.lesson_id, "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class RemoteSession:
    id: str
    token: str
    context: BrowserContext
    page: Page
    control: str = "user"             # user | server
    viewers: set[WebSocket] = field(default_factory=set)
    job: Job | None = None
    job_task: asyncio.Task | None = None
    last_frame: str | None = None
    last_activity: float = field(default_factory=time.time)
    frames_sent: int = 0
    closed: bool = False

    def touch(self) -> None:
        self.last_activity = time.time()

    def public(self) -> dict[str, Any]:
        path = self.page.url.split("?", 1)[0].replace(MOCK_BASE, "") if not self.closed else None
        return {
            "session_id": self.id, "control": self.control, "page_path": path,
            "viewers": len(self.viewers), "job": self.job.public() if self.job else None,
        }


class Manager:
    def __init__(self) -> None:
        self._pw = None
        self.browser: Browser | None = None
        self.sessions: dict[str, RemoteSession] = {}

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(channel=CHROME_CHANNEL, headless=True)
        audit("browser_started", version=self.browser.version)

    async def stop(self) -> None:
        for sid in list(self.sessions):
            await self.close(sid, reason="server_shutdown")
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()

    async def create(self) -> RemoteSession:
        assert self.browser
        # 세션마다 새 BrowserContext: 쿠키·저장소가 다른 세션과 공유되지 않는다.
        context = await self.browser.new_context(viewport=VIEWPORT, locale="ko-KR")
        page = await context.new_page()
        s = RemoteSession(id=secrets.token_hex(8), token=secrets.token_urlsafe(24), context=context, page=page)
        self.sessions[s.id] = s
        # 페이지 이동 시 뷰어 상태줄(현재 경로·제어 주체)을 갱신한다.
        page.on("framenavigated", lambda f: asyncio.ensure_future(push_status(s)) if f == page.main_frame and not s.closed else None)
        await self._start_screencast(s)
        await page.goto(f"{MOCK_BASE}/login")
        audit("session_created", session=s.id)
        return s

    async def _start_screencast(self, s: RemoteSession) -> None:
        cdp = await s.context.new_cdp_session(s.page)

        async def on_frame(evt: dict[str, Any]) -> None:
            try:
                await cdp.send("Page.screencastFrameAck", {"sessionId": evt["sessionId"]})
            except Exception:
                return
            s.last_frame = evt["data"]
            await broadcast(s, {"type": "frame", "data": evt["data"]})

        cdp.on("Page.screencastFrame", lambda e: asyncio.ensure_future(on_frame(e)))
        await cdp.send("Page.startScreencast", {
            "format": "jpeg", "quality": 60, "maxWidth": VIEWPORT["width"], "maxHeight": VIEWPORT["height"],
        })

    def get(self, sid: str, token: str | None) -> RemoteSession:
        s = self.sessions.get(sid)
        # 토큰 비교는 상수 시간으로. 다른 세션 토큰으로는 접근 불가.
        if not s or not token or not secrets.compare_digest(s.token, token):
            raise HTTPException(status_code=404, detail="session not found")
        return s

    async def close(self, sid: str, reason: str) -> None:
        s = self.sessions.pop(sid, None)
        if not s:
            return
        s.closed = True
        if s.job_task and not s.job_task.done():
            s.job_task.cancel()
        for ws in list(s.viewers):
            try:
                await ws.send_json({"type": "closed", "reason": reason})
                await ws.close()
            except Exception:
                pass
        s.viewers.clear()
        s.last_frame = None
        await s.context.close()   # 쿠키·로컬 저장소가 메모리에서 함께 폐기된다.
        audit("session_closed", session=sid, reason=reason)

    async def reaper(self) -> None:
        while True:
            await asyncio.sleep(1)
            now = time.time()
            for sid, s in list(self.sessions.items()):
                busy = s.job_task is not None and not s.job_task.done()
                if not s.viewers and not busy and now - s.last_activity > IDLE_TTL_SEC:
                    await self.close(sid, reason="idle_timeout")


MANAGER = Manager()


async def broadcast(s: RemoteSession, msg: dict[str, Any]) -> None:
    for ws in list(s.viewers):
        try:
            await ws.send_json(msg)
            if msg.get("type") == "frame":
                s.frames_sent += 1
        except Exception:
            s.viewers.discard(ws)


async def push_status(s: RemoteSession) -> None:
    await broadcast(s, {"type": "status", **s.public()})


# ---------------------------------------------------------------------------
# 서버 작업: 모의 사이트 레슨 등록
# ---------------------------------------------------------------------------
class LessonJob(BaseModel):
    title: str = Field(min_length=1, max_length=30)
    description: str = Field(min_length=1)
    price: int = Field(ge=0)
    image_name: str = "image.png"
    image_b64: str


async def run_registration(s: RemoteSession, data: LessonJob) -> None:
    job = s.job
    assert job
    page = s.page
    page.set_default_timeout(JOB_STEP_TIMEOUT_MS)
    image = base64.b64decode(data.image_b64)
    image_sha = hashlib.sha256(image).hexdigest()

    def step(name: str) -> None:
        job.steps.append(name)
        audit("job_step", session=s.id, step=name)

    try:
        step("open_form")
        await page.goto(f"{MOCK_BASE}/lessons/new")
        if "/login" in page.url:
            # 재로그인을 시도하지 않는다. 서버는 비밀번호를 갖고 있지 않다.
            job.result_state, job.message = "needs_login", "인증된 세션이 없어 사용자의 로그인이 필요합니다."
            return
        step("fill_text")
        await page.fill("#title", data.title)
        await page.fill("#description", data.description)
        await page.fill("#price", str(data.price))
        step("attach_image")
        mime = "image/png" if image[:4] == b"\x89PNG" else "image/jpeg"
        # 이미지는 디스크에 쓰지 않고 메모리 버퍼로 첨부한다.
        await page.set_input_files("#image", {"name": data.image_name, "mimeType": mime, "buffer": image})
        step("submit")
        job.submitted = True   # 이 시점 이후 실패는 중복 제출 위험 때문에 재시도하지 않는다.
        async with page.expect_navigation():
            await page.click("#save")
        step("verify_result")
        if await page.locator("#error").count():
            job.result_state = "failed"
            job.message = (await page.locator("#error").inner_text()).strip()
            return
        if not await page.locator("#saved").count():
            job.result_state, job.message = "unknown", "저장 결과 화면을 확인하지 못했습니다."
            return
        got = {
            "title": await page.locator("#r-title").inner_text(),
            "description": await page.locator("#r-description").inner_text(),
            "price": int(await page.locator("#r-price").inner_text()),
            "sha": await page.locator("#r-image-sha").inner_text(),
        }
        job.lesson_id = int(await page.locator("#lesson-id").inner_text())
        expected = {"title": data.title, "description": data.description, "price": data.price, "sha": image_sha}
        if got == expected:
            job.result_state = "mock_success"
        else:
            job.result_state = "needs_confirmation"
            job.message = "저장된 값이 요청 값과 다릅니다: " + ",".join(k for k in expected if got[k] != expected[k])
        shot = EVIDENCE_DIR / f"result_{s.id}_lesson{job.lesson_id}.png"
        await page.screenshot(path=str(shot))
        job.evidence = shot.name
    except asyncio.CancelledError:
        job.result_state = "unknown" if job.submitted else "cancelled"
        job.message = "작업이 중단되었습니다."
        raise
    except Exception as e:  # 타임아웃·연결 오류 등
        job.result_state = "unknown" if job.submitted else "failed"
        job.message = f"{type(e).__name__}"
    finally:
        job.state, job.finished_at = "done", time.time()
        s.control = "user"  # 작업이 끝나면 제어권을 사용자에게 자동 반환
        s.touch()
        audit("job_done", session=s.id, result_state=job.result_state, submitted=job.submitted,
              lesson_id=job.lesson_id, elapsed=round(job.finished_at - job.started_at, 2))
        if not s.closed:
            await push_status(s)


# ---------------------------------------------------------------------------
# 입력 중계
# ---------------------------------------------------------------------------
async def apply_input(s: RemoteSession, ev: dict[str, Any]) -> None:
    page, t = s.page, ev.get("t")
    if t == "mouse":
        x, y = float(ev["x"]), float(ev["y"])
        btn = ev.get("button", "left")
        action = ev.get("action", "click")
        if action == "move":
            await page.mouse.move(x, y)
        elif action == "down":
            await page.mouse.move(x, y)
            await page.mouse.down(button=btn)
        elif action == "up":
            await page.mouse.move(x, y)
            await page.mouse.up(button=btn)
        else:
            await page.mouse.click(x, y, button=btn)
    elif t == "wheel":
        await page.mouse.wheel(float(ev.get("dx", 0)), float(ev.get("dy", 0)))
    elif t == "key":
        await page.keyboard.press(str(ev["key"]))
    elif t == "text":
        await page.keyboard.type(str(ev["text"]))
    elif t == "nav" and ev.get("action") in {"back", "reload"}:
        await (page.go_back() if ev["action"] == "back" else page.reload())
    else:
        raise ValueError("unsupported input")


# ---------------------------------------------------------------------------
# HTTP / WebSocket
# ---------------------------------------------------------------------------
app = FastAPI(title="remote-browser-control-poc")


@app.on_event("startup")
async def _startup() -> None:
    await MANAGER.start()
    app.state.reaper = asyncio.create_task(MANAGER.reaper())


@app.on_event("shutdown")
async def _shutdown() -> None:
    app.state.reaper.cancel()
    await MANAGER.stop()


@app.post("/api/sessions")
async def create_session():
    s = await MANAGER.create()
    return {"session_id": s.id, "token": s.token, "viewer_path": f"/view/{s.id}#t={s.token}"}


@app.get("/api/sessions/{sid}")
async def session_status(sid: str, x_session_token: str | None = Header(None)):
    return MANAGER.get(sid, x_session_token).public()


@app.post("/api/sessions/{sid}/handoff", status_code=202)
async def handoff(sid: str, body: LessonJob, x_session_token: str | None = Header(None)):
    s = MANAGER.get(sid, x_session_token)
    if s.control != "user" or (s.job_task and not s.job_task.done()):
        raise HTTPException(status_code=409, detail="job already running")
    s.control, s.job = "server", Job()
    s.touch()
    audit("handoff", session=sid, viewers=len(s.viewers))
    await push_status(s)
    # 작업은 뷰어 WebSocket과 무관한 서버 태스크로 실행된다.
    s.job_task = asyncio.create_task(run_registration(s, body))
    return s.public()


@app.post("/api/sessions/{sid}/return")
async def return_control(sid: str, cancel: bool = Query(False), x_session_token: str | None = Header(None)):
    s = MANAGER.get(sid, x_session_token)
    running = s.job_task is not None and not s.job_task.done()
    if running and not cancel:
        raise HTTPException(status_code=409, detail="job running; use cancel=true")
    if running:
        s.job_task.cancel()
        try:
            await s.job_task
        except asyncio.CancelledError:
            pass
    s.control = "user"
    s.touch()
    audit("control_returned", session=sid, cancelled=running)
    await push_status(s)
    return s.public()


@app.delete("/api/sessions/{sid}")
async def delete_session(sid: str, x_session_token: str | None = Header(None)):
    MANAGER.get(sid, x_session_token)
    await MANAGER.close(sid, reason="user_ended")
    return {"closed": sid}


@app.websocket("/ws/{sid}")
async def ws_view(ws: WebSocket, sid: str):
    # 토큰은 URL(접속 로그에 남음)이 아니라 연결 직후 첫 메시지로 받는다.
    await ws.accept()
    try:
        first = await asyncio.wait_for(ws.receive_json(), timeout=5)
        s = MANAGER.get(sid, first.get("token") if first.get("t") == "auth" else None)
    except (HTTPException, asyncio.TimeoutError, WebSocketDisconnect, ValueError):
        audit("viewer_denied", session=sid)
        try:
            await ws.send_json({"type": "denied"})
            await ws.close(code=4404)
        except Exception:
            pass
        return
    s.viewers.add(ws)
    s.touch()
    audit("viewer_connected", session=sid, viewers=len(s.viewers))
    await ws.send_json({"type": "status", **s.public()})
    if s.last_frame:
        await ws.send_json({"type": "frame", "data": s.last_frame})
    seq = 0
    try:
        while True:
            ev = await ws.receive_json()
            seq += 1
            s.touch()
            if s.control != "user":
                audit("input_rejected", session=sid)
                await ws.send_json({"type": "input_rejected", "seq": seq, "reason": "server_control"})
                continue
            try:
                await apply_input(s, ev)
                # 감사 로그에는 마우스 누름·이동 종류만 남긴다. 키보드 입력은 건마다 기록하면
                # 비밀번호 길이가 드러나므로 기록하지 않는다.
                if ev.get("t") == "mouse" and ev.get("action") in {"down", "click"}:
                    audit("input", session=sid, kind="mouse", action=ev.get("action"))
                await ws.send_json({"type": "input_ok", "seq": seq})
            except Exception as e:
                await ws.send_json({"type": "input_error", "seq": seq, "error": type(e).__name__})
    except WebSocketDisconnect:
        pass
    finally:
        s.viewers.discard(ws)
        audit("viewer_disconnected", session=sid, viewers=len(s.viewers))


@app.get("/view/{sid}", response_class=HTMLResponse)
async def viewer(sid: str):
    return HTMLResponse((BASE_DIR / "control_server" / "viewer.html").read_text(encoding="utf-8"))


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse((BASE_DIR / "control_server" / "index.html").read_text(encoding="utf-8"))
