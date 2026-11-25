"""Loopback HTTP and WS use the same synthetic session authority."""
import unittest
from fastapi import APIRouter, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from lesson_registration.app.http.viewer_composition import create_viewer_app
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.store import Store
from support import temp_db


def router_factory(runtime, *, allowed_origin, resolve_owner):
    router = APIRouter()

    @router.websocket('/remote/viewer/ws')
    async def ws(socket: WebSocket):
        owner = await resolve_owner(socket)
        if owner is None:
            await socket.close(code=1008)
            return
        await socket.accept()
        await socket.send_json({"owner": owner})
        await socket.close()
    return router


class ViewerCompositionTests(unittest.TestCase):
    def test_shared_cookie_authority_and_foreign_origin(self):
        origin = 'http://127.0.0.1:8011'
        co = Coordinator(Store(temp_db(self)))
        app = create_viewer_app(co, object(), router_factory,
                               service_origin=origin, mock_owner='demo-a')
        with TestClient(app, base_url=origin, client=('127.0.0.1', 1234)) as c:
            self.assertEqual(c.get('/v1/sources').status_code, 401)
            self.assertEqual(c.post('/_mock/session').status_code, 403)
            self.assertEqual(c.post('/_mock/session', headers={'Origin': 'http://evil.test'}).status_code, 403)
            r = c.post('/_mock/session', headers={'Origin': origin})
            self.assertEqual(r.status_code, 200)
            self.assertIn('HttpOnly', r.headers['set-cookie'])
            self.assertEqual(c.get('/v1/sources').status_code, 200)
            with c.websocket_connect('ws://127.0.0.1:8011/remote/viewer/ws', headers={'Origin': origin}) as ws:
                self.assertEqual(ws.receive_json(), {'owner': 'demo-a'})
            with self.assertRaises(WebSocketDisconnect):
                with c.websocket_connect('ws://127.0.0.1:8011/remote/viewer/ws', headers={'Origin': 'http://evil.test'}):
                    pass
            c.cookies.clear()
            with self.assertRaises(WebSocketDisconnect):
                with c.websocket_connect('ws://127.0.0.1:8011/remote/viewer/ws', headers={'Origin': origin}):
                    pass
