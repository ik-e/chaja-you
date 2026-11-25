"""Viewer server side: CDP screencast frames out, human input in (transport-neutral).

R05 proposal for the R03/R04 transport (to be agreed; contracts/viewer.d.ts is the client side):
- the server endpoint authenticates the owner, then calls ``RemoteRuntime.attach_viewer(grant, owner, sink)``
- ``sink(message)`` receives ``{"t":"status",...}`` and ``{"t":"frame","data":<base64 jpeg>,"w","h"}``
- client messages go to ``ViewerConnection.receive``:
  ``{"t":"mouse","type":"move|down|up|click|wheel","x","y","button"?,"dx"?,"dy"?}``,
  ``{"t":"key","type":"press|down|up","key"}``, ``{"t":"text","text"}``
- input is accepted only while the session is ``human`` and the grant is current; after
  ``finish``/``close`` or grant rotation input is refused (``input_rejected``) and old grants detach.
- ``dispose()`` only detaches this viewer; it never closes the session or cancels a job.
Audit records keep event kinds only (no typed text or keys).
"""
from __future__ import annotations

import threading
import time

MOUSE_TYPES = {"move", "down", "up", "click", "wheel"}
KEY_TYPES = {"press", "down", "up"}
BUTTONS = {"left", "middle", "right"}
MAX_TEXT = 512


class ViewerConnection:
    def __init__(self, runtime, session, grant_hash: str, sink):
        self._rt, self.session, self.grant_hash, self._sink = runtime, session, grant_hash, sink
        self.closed = False
        self._lock = threading.Lock()
        self._pending = 0

    # server -> client
    def send(self, message: dict) -> None:
        if self.closed:
            return
        try:
            self._sink(message)
        except Exception:
            self.dispose()

    # client -> server
    def receive(self, message: dict) -> bool:
        s = self.session
        ok = (not self.closed and s.state == "human" and s.grant_hash == self.grant_hash
              and s.grant_expires_at > time.monotonic() and isinstance(message, dict))
        action = _input_action(message, s.binding.viewport) if ok else None
        if action is None:
            s.audit.append({"event": "input_rejected", "at": self._rt.clock.now()})
            self.send({"t": "input_rejected", "state": s.state})
            return False
        with self._lock:
            if self.closed or self._pending >= 32:
                return False
            self._pending += 1
        s.touch()
        kind = action[0]
        s.audit.append({"event": "input", "kind": kind, "at": self._rt.clock.now()})
        self._rt.host.spawn(self._apply_when_current(action))
        return True

    async def _apply_when_current(self, action):
        s = self.session
        try:
            async with s.input_lock:
                if (self.closed or s.state != "human" or s.grant_hash != self.grant_hash
                        or s.grant_expires_at <= time.monotonic()):
                    return
                await _apply_input(s.page_handle, action)
        finally:
            with self._lock:
                self._pending -= 1

    def dispose(self) -> None:
        with self._lock:
            if self.closed:
                return
            self.closed = True
        self.session.viewers.discard(self)
        self.session.audit.append({"event": "viewer_disposed", "at": self._rt.clock.now()})


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi


def _input_action(m: dict, viewport: dict):
    t = m.get("t")
    if t == "mouse" and m.get("type") in MOUSE_TYPES:
        if not (_num(m.get("x"), 0, viewport["width"]) and _num(m.get("y"), 0, viewport["height"])):
            return None
        button = m.get("button", "left")
        if button not in BUTTONS:
            return None
        if m["type"] == "wheel":
            if not (_num(m.get("dx", 0), -5000, 5000) and _num(m.get("dy", 0), -5000, 5000)):
                return None
            return ("wheel", m["x"], m["y"], m.get("dx", 0), m.get("dy", 0))
        return ("mouse", m["type"], m["x"], m["y"], button)
    if t == "key" and m.get("type") in KEY_TYPES and isinstance(m.get("key"), str) and 0 < len(m["key"]) <= 32:
        return ("key", m["type"], m["key"])
    if t == "text" and isinstance(m.get("text"), str) and 0 < len(m["text"]) <= MAX_TEXT:
        return ("text", m["text"])
    return None


async def _apply_input(page, action) -> None:
    try:
        kind = action[0]
        if kind == "mouse":
            _, typ, x, y, button = action
            if typ == "click":
                await page.mouse.click(x, y, button=button)
            else:
                await page.mouse.move(x, y)
                if typ == "down":
                    await page.mouse.down(button=button)
                elif typ == "up":
                    await page.mouse.up(button=button)
        elif kind == "wheel":
            _, x, y, dx, dy = action
            await page.mouse.move(x, y)
            await page.mouse.wheel(dx, dy)
        elif kind == "key":
            _, typ, key = action
            await getattr(page.keyboard, typ)(key)
        elif kind == "text":
            await page.keyboard.insert_text(action[1])
    except Exception:
        pass   # page navigating/closed; the human retries, nothing is executed on their behalf
