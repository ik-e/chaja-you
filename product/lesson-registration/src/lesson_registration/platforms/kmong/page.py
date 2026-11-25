"""Narrow page capability handed to the adapter by the runtime (RT-01 scoped context).

The adapter never receives a raw browser driver, cookies or credentials. The runtime
(r05-remote) implements ``ScopedPage`` over its controlled browser, pinned to the mock
origin; tests implement it with a stdlib HTML form client.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, Sequence


class NavigationUnknown(Exception):
    """Request may have reached the site but no trustworthy response was observed."""


class PageStructureError(Exception):
    """Expected control/field missing; page differs from the registered profile."""


@dataclass(frozen=True)
class UploadFile:
    filename: str
    mime: str
    data: bytes


@dataclass(frozen=True)
class PageView:
    path: str
    status: int
    page: str                      # value of <body data-page>
    fields: dict = field(default_factory=dict)  # data-field name -> [text, ...]

    def one(self, name: str, default: str | None = None) -> str | None:
        v = self.fields.get(name)
        return v[0] if v else default

    def all(self, name: str) -> list[str]:
        return list(self.fields.get(name, []))


class ScopedPage(Protocol):
    def goto(self, path: str) -> PageView: ...
    def fill(self, name: str, value: str) -> None: ...
    def attach(self, name: str, files: Sequence[UploadFile]) -> None: ...
    def submit(self, control: str) -> PageView: ...
    def view(self) -> PageView: ...


class AssetSource(Protocol):
    def read(self, asset_id: str, digest: str) -> bytes: ...


@dataclass(frozen=True)
class KmongContext:
    accepted: dict                 # AcceptedScope (immutable, already durably accepted)
    page: ScopedPage
    assets: AssetSource
    now: Callable[[], str]
