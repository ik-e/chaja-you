"""H1-H9 adapter. Explicit mock-only composition; no implicit providers/auth."""
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from .. import contract
from ..errors import AppError
from ..service import AppService
from .parsing import invalid, json_object, source_parts


def create_app(coordinator, *, owner_resolver=None, dev_owner_header=False,
               allowed_origins=(), max_body_bytes=16 * 1024 * 1024):
    """Create one ASGI app per DB. owner_resolver(Request)->str is trusted sync code.

    dev_owner_header explicitly enables X-Mock-Owner on loopback only. It is
    synthetic test identity, never production authentication. Viewer is separate.
    Origins are exact explicit UI origins; unlisted browser origins are denied.
    """
    if os.getenv("LR_ENVIRONMENT", "mock") != "mock":
        raise ValueError("only mock environment is supported")
    if owner_resolver is not None and dev_owner_header:
        raise ValueError("choose one owner resolver")
    if "*" in allowed_origins or max_body_bytes <= 0:
        raise ValueError("explicit origins and positive body limit required")
    service = AppService(coordinator)

    @asynccontextmanager
    async def lifespan(app):
        await run_in_threadpool(service.start)
        try:
            yield
        finally:
            await run_in_threadpool(service.close)

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.service = service

    def error_response(exc, status=None):
        return JSONResponse(exc.to_view(), status_code=status or exc.status,
                            headers={"Cache-Control": "no-store"})

    @app.middleware("http")
    async def boundary(request, call_next):
        origin = request.headers.get("origin")
        if origin is not None and origin not in allowed_origins:
            return error_response(AppError("PERMISSION_DENIED", "허용되지 않은 요청 출처입니다."))
        if dev_owner_header and (request.client is None or request.client.host not in ("127.0.0.1", "::1")
                                 or request.url.hostname not in ("127.0.0.1", "localhost", "::1")):
            return error_response(AppError("PERMISSION_DENIED", "개발 인증은 loopback 전용입니다."))
        if request.method == "OPTIONS" and origin is not None:
            response = JSONResponse(None, status_code=200)
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Mock-Owner"
        else:
            try:
                response = await call_next(request)
            except Exception:
                response = error_response(AppError("RUNTIME_ERROR", "요청을 처리하지 못했습니다."), 500)
        response.headers["Cache-Control"] = "no-store"
        if origin is not None:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        return response

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        return error_response(exc)

    async def owner(request):
        if dev_owner_header:
            values = request.headers.getlist("x-mock-owner")
            value = values[0] if len(values) == 1 else None
        elif owner_resolver is not None:
            value = await run_in_threadpool(owner_resolver, request)
        else:
            value = None
        if not isinstance(value, str) or not value or len(value) > 256 or any(ord(c) < 32 for c in value):
            raise AppError("UNAUTHENTICATED", "인증이 필요합니다.")
        return value

    async def body(request, multipart=False):
        data = bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data) > max_body_bytes:
                raise invalid()
        ct = request.headers.get("content-type", "")
        media = ct.split(";")[0].strip().lower()
        if multipart and media == "multipart/form-data":
            return source_parts(bytes(data), ct)
        if media != "application/json":
            raise invalid()
        value = json_object(bytes(data))
        return (value, {}) if multipart else value

    def query(request):
        result = {}
        for key, value in request.query_params.multi_items():
            if key in result:
                raise invalid()
            if key == "limit":
                if not value.isascii() or not value.isdecimal() or len(value) > 3:
                    raise invalid()
                value = int(value)
            result[key] = value
        contract.validate("ListQuery", result)
        return result

    async def respond(method, output, *args, status=200):
        value = await run_in_threadpool(method, *args)
        # Server output violations are internal failures, not client errors.
        if not contract.is_valid(output, value):
            return error_response(AppError("RUNTIME_ERROR", "응답을 구성하지 못했습니다."), 500)
        return JSONResponse(value, status_code=status)

    @app.post("/v1/sources")
    async def create_source(request: Request):
        identity = await owner(request)
        manifest, files = await body(request, multipart=True)
        return await respond(coordinator.create_source, "SourceView", identity, manifest, files, status=201)

    @app.get("/v1/sources")
    async def list_sources(request: Request):
        return await respond(coordinator.list_sources, "SourceList", await owner(request), query(request))

    @app.get("/v1/sources/{id}")
    async def get_source(id: str, request: Request):
        return await respond(coordinator.get_source, "SourceView", await owner(request), id)

    @app.post("/v1/registrations")
    async def create_registration(request: Request):
        identity = await owner(request)
        return await respond(coordinator.create_registration, "RegistrationView", identity,
                             await body(request), status=201)

    @app.patch("/v1/registrations/{id}")
    async def edit_registration(id: str, request: Request):
        identity = await owner(request)
        return await respond(coordinator.edit_registration, "RegistrationView", identity, id, await body(request))

    @app.post("/v1/registrations/{id}/authentication")
    async def authenticate(id: str, request: Request):
        identity = await owner(request)
        return await respond(coordinator.authenticate, "AuthResponse", identity, id, await body(request))

    @app.post("/v1/registrations/{id}/start")
    async def start(id: str, request: Request):
        identity = await owner(request)
        payload = await body(request)
        if service.pool is None:
            raise AppError("RUNTIME_ERROR", "실행기가 준비되지 않았습니다.")
        status, value = await run_in_threadpool(coordinator.start, identity, id, payload)
        return JSONResponse(value, status_code=status)

    @app.get("/v1/registrations/{id}")
    async def get_registration(id: str, request: Request):
        return await respond(coordinator.get_registration, "RegistrationView", await owner(request), id)

    @app.get("/v1/registrations")
    async def list_registrations(request: Request):
        return await respond(coordinator.list_registrations, "RegistrationList", await owner(request), query(request))

    return app
