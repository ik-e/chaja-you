"""Platform bindings: what the runtime needs from each platform provider (explicit injection, IB-05).

A binding never receives the raw browser: identification, target resolution and every
operation act through ScopedPage. The runtime owns sessions, grants, leases and STORE calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from .page import NavigationUnknown, PageStructureError, PageView


class Driver(Protocol):
    """Platform operations (e.g. kmong.KmongAdapter): registry, one step, independent goal readback."""
    def operations(self, accepted: dict) -> list[dict]: ...
    def perform(self, ctx: Any, operation: dict) -> Any: ...       # outcome with .observation/.evidence[/.goal]
    def observe_goal(self, ctx: Any) -> Any: ...                  # readback with .verdict/.goal_observation/...


@dataclass(frozen=True)
class Identity:
    account_ref: str
    account_label: str


@dataclass(frozen=True)
class PlatformBinding:
    profile_id: str                       # "{platform}.{object_kind}.{version}"
    origin: str                           # fixed origin, e.g. http://127.0.0.1:8001 (mock)
    entry_path: str                       # first page shown to the human (login)
    identify: Callable[[Any], Identity | None]                 # (ScopedPage) -> signed-in account or None
    resolve_target: Callable[[Any, dict], tuple[str, str]]      # (ScopedPage, identity) -> (status, note)
    driver: Driver
    make_context: Callable[[dict, Any, Callable[[], str]], Any]  # (accepted, ScopedPage, now) -> driver ctx
    slot_for: Callable[[str], str] = lambda registration_id: f"slot-{registration_id}"
    unknown_exc: type = NavigationUnknown
    structure_exc: type = PageStructureError
    view_factory: Callable[..., Any] = PageView
    viewport: dict = field(default_factory=lambda: {"width": 1280, "height": 800})
    # Trusted composition factory only. The adapter receives its resulting restricted context.
    make_worker_context: Callable[[dict, Any, Callable[[], str], Any], Any] | None = None
