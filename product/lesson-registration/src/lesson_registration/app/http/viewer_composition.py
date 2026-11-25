"""Explicit local Viewer composition; synthetic sessions are not production auth."""
import secrets
import time
from urllib.parse import urlsplit

from fastapi import Request
from starlette.responses import JSONResponse

from .api import create_app
from ..errors import AppError


class LocalSessions:
    def __init__(self, origin, owner, ttl=1800):
        parsed = urlsplit(origin)
        if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1") or parsed.path or parsed.query or parsed.fragment:
            raise ValueError("an explicit loopback HTTP origin is required")
        if not owner or ttl <= 0:
            raise ValueError("owner and positive session TTL required")
        self.origin, self.owner, self.ttl = origin, owner, ttl
        self.cookie = "lr_mock_session"
        self.sessions = {}

    def allowed(self, request):
        return (request.client is not None and request.client.host in ("127.0.0.1", "::1")
                and request.headers.get("host") == urlsplit(self.origin).netloc
                and request.headers.get("origin") == self.origin)

    def resolve(self, request):
        # Same-origin GET may omit Origin; WS and session creation require it.
        if (request.client is None or request.client.host not in ("127.0.0.1", "::1")
                or request.headers.get("host") != urlsplit(self.origin).netloc
                or request.headers.get("origin") not in (None, self.origin)):
            return None
        token = request.cookies.get(self.cookie)
        expiry = self.sessions.get(token, 0)
        if expiry <= time.monotonic():
            self.sessions.pop(token, None)
            return None
        return self.owner

    async def resolve_ws(self, websocket):
        return self.resolve(websocket) if self.allowed(websocket) else None


def create_viewer_app(coordinator, runtime, router_factory, *, service_origin, mock_owner):
    """R05 router_factory is explicitly supplied, never imported or faked implicitly.

    UI must use the configured same origin (serve/proxy UI and API together).
    POST /_mock/session selects the configured synthetic owner, not client input.
    """
    sessions = LocalSessions(service_origin, mock_owner)
    app = create_app(coordinator, owner_resolver=sessions.resolve,
                     allowed_origins=(service_origin,))

    @app.post("/_mock/session")
    async def open_session(request: Request):
        if not sessions.allowed(request):
            raise AppError("PERMISSION_DENIED", "local same-origin session required")
        now = time.monotonic()
        sessions.sessions = {k: v for k, v in sessions.sessions.items() if v > now}
        if len(sessions.sessions) >= 128:
            raise AppError("PERMISSION_DENIED", "local session limit reached")
        token = secrets.token_urlsafe(32)
        sessions.sessions[token] = now + sessions.ttl
        response = JSONResponse({"mock": True})
        response.set_cookie(sessions.cookie, token, httponly=True, samesite="strict",
                            max_age=sessions.ttl, path="/")
        return response

    app.include_router(router_factory(runtime, allowed_origin=service_origin,
                                      resolve_owner=sessions.resolve_ws))
    return app
