"""Optional same-origin Viewer routes. R03 injects the authenticated owner resolver.

Import this module only with the approved ``app`` dependency group installed.
No owner is accepted from message bodies. No credentials or frames are logged.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import time
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from contracts.interfaces import PortFailure


def viewer_router(runtime, *, allowed_origin: str, resolve_owner):
    """Return routes for explicit inclusion in R03's app.

    ``await resolve_owner(websocket)`` must return a service-authenticated owner
    or None. The router never derives authority from a grant or a client header.
    ``allowed_origin`` comes from trusted service configuration.
    """
    router = APIRouter()

    @router.get('/remote/viewer.js')
    async def viewer_module():
        return FileResponse(Path(__file__).with_name('viewer.js'), media_type='text/javascript',
                            headers={'Cache-Control': 'no-store'})

    @router.websocket('/remote/viewer/ws')
    async def viewer_socket(websocket: WebSocket):
        if websocket.query_params or websocket.headers.get('origin') != allowed_origin:
            await websocket.close(code=1008)
            return
        owner = await resolve_owner(websocket)
        if not isinstance(owner, str) or not owner:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        connection = None
        tasks = []
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=5)
            if len(raw) > 4096:
                await websocket.close(code=1008)
                return
            message = json.loads(raw)
            grant = message.get('grant') if isinstance(message, dict) else None
            if (message.get('t') != 'attach' or not isinstance(grant, dict)
                    or not isinstance(grant.get('viewer_grant'), str)
                    or type(grant.get('generation')) is not int):
                await websocket.close(code=1008)
                return
            queue = asyncio.Queue(maxsize=8)
            overflow = asyncio.Event()
            loop = asyncio.get_running_loop()

            def enqueue(message):
                if queue.full():
                    overflow.set()
                else:
                    queue.put_nowait(message)

            def sink(message):
                loop.call_soon_threadsafe(enqueue, message)

            connection = await asyncio.to_thread(runtime.attach_viewer, grant['viewer_grant'], owner,
                                                 sink, generation=grant['generation'])
            del grant, message, raw

            async def send_frames():
                while True:
                    await websocket.send_json(await queue.get())

            async def receive_input():
                window, count = time.monotonic(), 0
                while True:
                    raw = await websocket.receive_text()
                    if len(raw) > 4096:
                        return
                    now = time.monotonic()
                    if now - window >= 1:
                        window, count = now, 0
                    count += 1
                    if count > 120:
                        return
                    message = json.loads(raw)
                    if not isinstance(message, dict):
                        return
                    connection.receive(message)

            tasks = [asyncio.create_task(send_frames()), asyncio.create_task(receive_input()),
                     asyncio.create_task(overflow.wait())]
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except (PortFailure, ValueError, AttributeError, WebSocketDisconnect, asyncio.TimeoutError):
            pass
        finally:
            for task in tasks:
                task.cancel()
            for task in tasks:
                with contextlib.suppress(asyncio.CancelledError, WebSocketDisconnect, RuntimeError, ValueError):
                    await task
            if connection is not None:
                connection.dispose()
            with contextlib.suppress(RuntimeError, WebSocketDisconnect):
                await websocket.close(code=1008)

    return router
