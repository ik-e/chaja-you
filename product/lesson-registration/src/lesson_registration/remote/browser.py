"""Browser host: one Playwright/Chromium instance on a private event-loop thread.

Public calls are synchronous (contracts.interfaces is a sync binding); async Playwright stays
behind this bridge so callers never block an event loop they own (PD / IB note).
Each remote session gets its own BrowserContext (cookies/storage isolated).
"""
from __future__ import annotations

import asyncio
import os
import threading
from typing import Any, Awaitable


class BrowserHost:
    def __init__(self, *, channel: str | None = None, headless: bool = True, timeout_sec: float = 60.0):
        # LR_BROWSER_CHANNEL=chrome lets an owner machine use installed Chrome when the pinned
        # Chromium download is unavailable; default is the Playwright-managed Chromium (CI).
        self.channel = channel if channel is not None else (os.environ.get("LR_BROWSER_CHANNEL") or None)
        self.headless = headless
        self.timeout_sec = timeout_sec
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, name="lr-remote-browser", daemon=True)
        self._thread.start()
        self._pw = None
        self._browser = None
        try:
            self.run(self._start())
        except BaseException:
            self.close()
            raise

    async def _start(self):
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        kwargs: dict[str, Any] = {"headless": self.headless}
        if self.channel:
            kwargs["channel"] = self.channel
        self._browser = await self._pw.chromium.launch(**kwargs)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def run(self, coro: Awaitable, timeout: float | None = None):
        """Run a coroutine on the browser loop and wait for it (never call from that loop)."""
        if threading.current_thread() is self._thread:
            raise RuntimeError("BrowserHost.run called from the browser loop")
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(self.timeout_sec if timeout is None else timeout)

    def spawn(self, coro: Awaitable) -> None:
        """Fire-and-forget on the browser loop (used for viewer input/frames)."""
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def new_context(self, **kwargs):
        return await self._browser.new_context(**kwargs)

    def version(self) -> str:
        return self._browser.version if self._browser else ""

    def close(self) -> None:
        async def _stop():
            if self._browser is not None:
                await self._browser.close()
            if self._pw is not None:
                await self._pw.stop()
            pending = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
        try:
            if self._loop.is_running() and (self._browser is not None or self._pw is not None):
                asyncio.run_coroutine_threadsafe(_stop(), self._loop).result(self.timeout_sec)
        finally:
            self._browser = self._pw = None
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(10)
            if not self._thread.is_alive():
                self._loop.close()
