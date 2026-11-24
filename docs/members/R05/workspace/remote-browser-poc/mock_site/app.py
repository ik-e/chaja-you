"""모의 레슨 등록 사이트 (실제 크몽·숨고가 아님).

가상 계정으로 로그인한 뒤 레슨 글(제목·설명·가격·대표 이미지)을 저장하고
결과 페이지에서 확인하는 최소 흐름만 제공한다. 데이터는 메모리에만 둔다.
"""
from __future__ import annotations

import asyncio
import hashlib
import html
import os
import secrets
import time
from dataclasses import dataclass, field

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

# 가상 계정: 시험 전용 값. 실제 서비스 계정이 아니다.
# 비밀번호는 환경변수로 바꿀 수 있다.
ACCOUNTS = {
    "tutor_a": os.environ.get("MOCK_PW_TUTOR_A", "Mock-Pass-A!2026"),
    "tutor_b": os.environ.get("MOCK_PW_TUTOR_B", "Mock-Pass-B!2026"),
}
SAVE_DELAY_SEC = float(os.environ.get("MOCK_SAVE_DELAY_SEC", "0"))
MAX_IMAGE_BYTES = 2 * 1024 * 1024
COOKIE = "mock_sid"


@dataclass
class Lesson:
    id: int
    owner: str
    title: str
    description: str
    price: int
    image_sha256: str
    image_bytes: bytes = field(repr=False)
    created_at: float


app = FastAPI(title="mock-lesson-site")
SESSIONS: dict[str, str] = {}          # 쿠키 값 -> 사용자
LOGIN_COUNT: dict[str, int] = {u: 0 for u in ACCOUNTS}
LOGIN_PAGE_VIEWS: dict[str, int] = {"count": 0}
LESSONS: list[Lesson] = []


def _user(request: Request) -> str | None:
    return SESSIONS.get(request.cookies.get(COOKIE, ""))


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{margin:0;font-family:sans-serif;background:#f6f7fb}}
header{{height:56px;background:#3b3fd8;color:#fff;display:flex;align-items:center;padding:0 24px;font-weight:bold}}
main{{padding:24px}}
label{{display:block;margin-top:12px;font-size:14px}}
input,textarea{{font-size:16px}}
</style></head><body><header>모의 레슨 플랫폼 (시험용)</header><main>{body}</main></body></html>"""
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse("/dashboard" if _user(request) else "/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(error: str = ""):
    LOGIN_PAGE_VIEWS["count"] += 1
    msg = '<p id="err" style="position:absolute;left:40px;top:300px;color:#c00">아이디 또는 비밀번호가 맞지 않습니다.</p>' if error else ""
    # 원격 조작 시험이 마우스 좌표로 입력할 수 있도록 위치를 고정한다.
    return _page(
        "로그인",
        f"""<form id="login" method="post" action="/login">
<input id="username" name="username" placeholder="아이디" autocomplete="username"
 style="position:absolute;left:40px;top:120px;width:300px;height:36px">
<input id="password" name="password" type="password" placeholder="비밀번호" autocomplete="current-password"
 style="position:absolute;left:40px;top:180px;width:300px;height:36px">
<button id="submit" type="submit" style="position:absolute;left:40px;top:240px;width:120px;height:40px">로그인</button>
</form>{msg}""",
    )


@app.post("/login")
def login(username: str = Form(""), password: str = Form("")):
    if ACCOUNTS.get(username) and secrets.compare_digest(ACCOUNTS[username], password):
        sid = secrets.token_urlsafe(24)
        SESSIONS[sid] = username
        LOGIN_COUNT[username] += 1
        resp = RedirectResponse("/dashboard", status_code=303)
        resp.set_cookie(COOKIE, sid, httponly=True, samesite="lax")
        return resp
    return RedirectResponse("/login?error=1", status_code=303)


@app.get("/logout")
def logout(request: Request):
    SESSIONS.pop(request.cookies.get(COOKIE, ""), None)
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(COOKIE)
    return resp


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = _user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    mine = [l for l in LESSONS if l.owner == user]
    items = "".join(f'<li><a href="/lessons/{l.id}">{html.escape(l.title)}</a></li>' for l in mine)
    return _page(
        "대시보드",
        f'<h2 id="who">{html.escape(user)} 님 대시보드</h2>'
        f'<p><a id="new" href="/lessons/new">새 레슨 등록</a></p><ul id="mine">{items}</ul>',
    )


@app.get("/lessons/new", response_class=HTMLResponse)
def new_lesson(request: Request):
    if not _user(request):
        return RedirectResponse("/login", status_code=303)
    return _page(
        "레슨 등록",
        """<h2>레슨 등록</h2><form id="lesson" method="post" action="/lessons" enctype="multipart/form-data">
<label>제목 <input id="title" name="title" maxlength="30" required style="width:400px"></label>
<label>설명<br><textarea id="description" name="description" rows="6" cols="60" required></textarea></label>
<label>가격(원) <input id="price" name="price" type="number" min="0" required></label>
<label>대표 이미지 <input id="image" name="image" type="file" accept="image/png,image/jpeg" required></label>
<p><button id="save" type="submit">저장</button></p></form>""",
    )


@app.post("/lessons")
async def create_lesson(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    image: UploadFile = File(...),
):
    user = _user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    data = await image.read()
    is_png = data[:8] == b"\x89PNG\r\n\x1a\n"
    is_jpg = data[:3] == b"\xff\xd8\xff"
    if not (is_png or is_jpg) or len(data) > MAX_IMAGE_BYTES:
        return _page("오류", '<p id="error">이미지 업로드 실패: PNG/JPG 2MB 이하만 가능합니다.</p>')
    if not (1 <= len(title) <= 30):
        return _page("오류", '<p id="error">제목은 1–30자여야 합니다.</p>')
    if SAVE_DELAY_SEC:
        await asyncio.sleep(SAVE_DELAY_SEC)
    lesson = Lesson(
        id=len(LESSONS) + 1, owner=user, title=title, description=description, price=price,
        image_sha256=hashlib.sha256(data).hexdigest(), image_bytes=data, created_at=time.time(),
    )
    LESSONS.append(lesson)
    return RedirectResponse(f"/lessons/{lesson.id}", status_code=303)


@app.get("/lessons/{lesson_id}", response_class=HTMLResponse)
def lesson_detail(lesson_id: int, request: Request):
    user = _user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    lesson = next((l for l in LESSONS if l.id == lesson_id and l.owner == user), None)
    if not lesson:
        return _page("없음", '<p id="error">레슨을 찾을 수 없습니다.</p>')
    return _page(
        "등록 결과",
        f"""<h2 id="saved">저장 완료</h2>
<p>번호: <span id="lesson-id">{lesson.id}</span></p>
<p>제목: <span id="r-title">{html.escape(lesson.title)}</span></p>
<p>설명: <span id="r-description">{html.escape(lesson.description)}</span></p>
<p>가격: <span id="r-price">{lesson.price}</span>원</p>
<p>이미지 SHA-256: <span id="r-image-sha">{lesson.image_sha256}</span></p>
<img id="r-image" src="/lessons/{lesson.id}/image" style="max-width:320px">""",
    )


@app.get("/lessons/{lesson_id}/image")
def lesson_image(lesson_id: int, request: Request):
    user = _user(request)
    lesson = next((l for l in LESSONS if l.id == lesson_id and l.owner == user), None)
    if not lesson:
        return Response(status_code=404)
    media = "image/png" if lesson.image_bytes[:4] == b"\x89PNG" else "image/jpeg"
    return Response(lesson.image_bytes, media_type=media)


@app.get("/__test__/stats")
def stats():
    """시험 관측용. 비밀번호·쿠키는 내보내지 않는다."""
    return JSONResponse({
        "login_count": LOGIN_COUNT,
        "login_page_views": LOGIN_PAGE_VIEWS["count"],
        "lessons": [
            {"id": l.id, "owner": l.owner, "title": l.title, "price": l.price, "image_sha256": l.image_sha256}
            for l in LESSONS
        ],
    })
