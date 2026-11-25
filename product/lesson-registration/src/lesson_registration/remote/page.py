"""ScopedPage over a controlled browser page: the only browser capability a platform driver gets.

No raw Page/driver, cookies, CDP or credentials leave this object (RT-01). Navigation is limited
to relative paths on the binding's fixed origin, and the browser context aborts requests to any
other origin. Field conventions (shared with platform mocks): ``<body data-page>`` names the page,
``[data-field]`` elements carry observable values, forms use ``name`` attributes and submit
``button[name]`` controls.

Exception classes are injectable so a platform driver can keep catching its own types
(e.g. kmong.page.NavigationUnknown) until a shared ScopedPage contract exists.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence
from urllib.parse import urlsplit


class NavigationUnknown(Exception):
    """Request may have reached the site but no trustworthy response was observed."""


class PageStructureError(Exception):
    """Expected control/field missing or navigation left the bound origin."""


@dataclass(frozen=True)
class UploadFile:
    filename: str
    mime: str
    data: bytes


@dataclass(frozen=True)
class PageView:
    path: str
    status: int
    page: str
    fields: dict = field(default_factory=dict)

    def one(self, name: str, default: str | None = None) -> str | None:
        v = self.fields.get(name)
        return v[0] if v else default

    def all(self, name: str) -> list[str]:
        return list(self.fields.get(name, []))


_SNAPSHOT_JS = """() => {
  const fields = {};
  for (const el of document.querySelectorAll('[data-field]')) {
    (fields[el.dataset.field] = fields[el.dataset.field] || []).push(el.textContent);
  }
  return {page: document.body ? (document.body.dataset.page || '') : '', fields};
}"""
_PATH_RE = re.compile(r"^/(?!/)[^\s\\#]*$")


def _attr(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def origin_of(url: str) -> str:
    u = urlsplit(url)
    return f"{u.scheme}://{u.netloc}"


class BrowserScopedPage:
    def __init__(self, host, page, origin: str, *, unknown_exc=NavigationUnknown, structure_exc=PageStructureError,
                 view_factory=PageView, timeout_ms: int = 10000):
        self._host, self._page, self._origin = host, page, origin.rstrip("/")
        self._unknown, self._structure, self._view_factory = unknown_exc, structure_exc, view_factory
        self._timeout = timeout_ms
        self._status = 0

    # ---- internals (browser loop) ----
    async def _snapshot(self):
        url = self._page.url
        if url.startswith("chrome-error:") or origin_of(url) != self._origin:
            raise self._unknown(f"page left bound origin or failed to load ({urlsplit(url).scheme})")
        data = await self._page.evaluate(_SNAPSHOT_JS)
        return self._view_factory(urlsplit(url).path, self._status, data["page"], data["fields"])

    def _target(self, path: str) -> str:
        if not isinstance(path, str) or not _PATH_RE.match(path):
            raise self._structure("navigation must be a relative path on the bound origin")
        return self._origin + path

    async def _goto(self, path):
        from playwright.async_api import Error as PwError
        target = self._target(path)
        for attempt in (1, 2):
            try:
                resp = await self._page.goto(target, wait_until="load", timeout=self._timeout)
                break
            except PwError as e:
                # A GET is safe to repeat once when a still-running navigation (e.g. the human's
                # sign-in redirect) interrupted it; anything else stays unknown.
                if attempt == 1 and "interrupted by another navigation" in str(e):
                    await self._page.wait_for_load_state("load", timeout=self._timeout)
                    continue
                raise self._unknown(f"GET {path}: {type(e).__name__}") from None
        self._status = resp.status if resp is not None else 0
        return await self._snapshot()

    async def _locator(self, selector, what):
        loc = self._page.locator(selector)
        if await loc.count() == 0:
            raise self._structure(f"{what} not on page")
        return loc.first

    async def _fill(self, name, value):
        el = await self._locator(f'[name="{_attr(name)}"]', f"field {name}")
        tag, typ, own = await el.evaluate("e => [e.tagName.toLowerCase(), (e.type || '').toLowerCase(), e.value]")
        if tag == "select":
            await el.select_option(value=value, timeout=self._timeout)
        elif typ == "checkbox":
            if value in ("true", "on", own):
                await el.check(timeout=self._timeout)
            else:
                await el.uncheck(timeout=self._timeout)
        elif typ == "file":
            raise self._structure(f"field {name} is a file input")
        else:
            await el.fill(value, timeout=self._timeout)

    async def _attach(self, name, files):
        el = await self._locator(f'input[type="file"][name="{_attr(name)}"]', f"file input {name}")
        await el.set_input_files([{"name": f.filename, "mimeType": f.mime, "buffer": f.data} for f in files],
                                 timeout=self._timeout)

    async def _submit(self, control):
        from playwright.async_api import Error as PwError
        btn = await self._locator(f'button[name="{_attr(control)}"], input[type="submit"][name="{_attr(control)}"]',
                                  f"control {control}")
        try:
            async with self._page.expect_navigation(wait_until="load", timeout=self._timeout) as nav:
                await btn.click(timeout=self._timeout)
            resp = await nav.value
        except PwError as e:
            raise self._unknown(f"submit {control}: {type(e).__name__}") from None
        self._status = resp.status if resp is not None else 0
        return await self._snapshot()

    # ---- ScopedPage (sync) ----
    def goto(self, path: str):
        return self._host.run(self._goto(path))

    def view(self):
        return self._host.run(self._snapshot())

    def fill(self, name: str, value: str) -> None:
        self._host.run(self._fill(name, value))

    def attach(self, name: str, files: Sequence) -> None:
        self._host.run(self._attach(name, files))

    def submit(self, control: str):
        return self._host.run(self._submit(control))
