"""Actual browser mount and WebSocket tests on loopback synthetic sites only."""
import asyncio
import socket
import threading
import time
import unittest

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from playwright.sync_api import sync_playwright

import support as s
from contracts.interfaces import PortFailure
from lesson_registration.remote import RemoteRuntime
from lesson_registration.remote.browser import BrowserHost
from lesson_registration.remote.transport import viewer_router
from test_auth_viewer import auth


class Transport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = BrowserHost()

    @classmethod
    def tearDownClass(cls):
        cls.host.close()

    def setUp(self):
        self.site = s.NeutralSite().start()
        self.addCleanup(self.site.stop)
        self.rt = RemoteRuntime([s.binding(self.site, s.NeutralDriver({}))], None, host=self.host)
        self.addCleanup(self.rt.close)

    def app(self, origin):
        app = FastAPI()

        async def owner(ws):
            # Synthetic service session, never a production identity provider.
            return {'session-a': 'owner-a', 'session-b': 'owner-b'}.get(ws.cookies.get('session'))

        app.include_router(viewer_router(self.rt, allowed_origin=origin, resolve_owner=owner))

        @app.get('/')
        def index():
            return FileResponse(s.ROOT / 'web' / 'index.html')

        @app.get('/app.js')
        def ui_script():
            return FileResponse(s.ROOT / 'web' / 'app.js', media_type='text/javascript')

        return app

    def opened(self):
        return self.rt.authenticate(auth('reg-1', 'owner-a', 'open'))['grant']

    def test_expired_grant_cannot_attach_over_websocket(self):
        grant = self.opened()
        self.rt.sessions['reg-1'].grant_expires_at = time.monotonic() - 1
        with TestClient(self.app('http://testserver')) as client:
            client.cookies.set('session', 'session-a')
            with client.websocket_connect('/remote/viewer/ws', headers={'origin': 'http://testserver'}) as ws:
                ws.send_json({'t': 'attach', 'grant': grant})
                self.assertEqual(ws.receive()['type'], 'websocket.close')
        self.assertEqual(len(self.rt.sessions['reg-1'].viewers), 0)
        self.assertFalse(self.rt.sessions['reg-1'].grant_attached)

    def test_expiry_after_attach_rejects_input(self):
        grant = self.opened()
        sink = s.Sink()
        viewer = self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', sink)
        self.rt.sessions['reg-1'].grant_expires_at = time.monotonic() - 1
        self.assertFalse(viewer.receive({'t': 'text', 'text': 'expired-input'}))
        self.assertIsNotNone(sink.wait_for(lambda msg: msg.get('t') == 'input_rejected'))
        audit = self.rt.sessions['reg-1'].audit
        self.assertFalse(any(event['event'] == 'input' for event in audit))
        self.assertNotIn('expired-input', repr(audit))

    def test_two_concurrent_attaches_have_exactly_one_winner(self):
        grant = self.opened()
        barrier = threading.Barrier(3)
        outcomes = []
        lock = threading.Lock()

        def attach():
            barrier.wait(timeout=5)
            try:
                connection = self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', s.Sink())
                result = ('attached', connection)
            except PortFailure as error:
                result = ('denied', error.error['code'])
            with lock:
                outcomes.append(result)

        workers = [threading.Thread(target=attach) for _ in range(2)]
        for worker in workers:
            worker.start()
        barrier.wait(timeout=5)
        for worker in workers:
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertEqual(sorted(kind for kind, _ in outcomes), ['attached', 'denied'])
        self.assertEqual(next(value for kind, value in outcomes if kind == 'denied'), 'PERMISSION_DENIED')
        self.assertEqual(len(self.rt.sessions['reg-1'].viewers), 1)

    def test_socket_disconnect_requires_refresh_before_reconnect(self):
        grant = self.opened()
        context = self.rt.sessions['reg-1'].context
        headers = {'origin': 'http://testserver'}
        with TestClient(self.app('http://testserver')) as client:
            client.cookies.set('session', 'session-a')
            with client.websocket_connect('/remote/viewer/ws', headers=headers) as ws:
                ws.send_json({'t': 'attach', 'grant': grant})
                self.assertEqual(ws.receive_json()['state'], 'human')
            self.assertTrue(s.wait_until(lambda: not self.rt.sessions['reg-1'].viewers))
            self.assertIs(self.rt.sessions['reg-1'].context, context)
            self.assertEqual(self.rt.sessions['reg-1'].state, 'human')
            with client.websocket_connect('/remote/viewer/ws', headers=headers) as ws:
                ws.send_json({'t': 'attach', 'grant': grant})
                self.assertEqual(ws.receive()['type'], 'websocket.close')
            fresh = self.rt.authenticate(auth('reg-1', 'owner-a', 'refresh', generation=1))['grant']
            with client.websocket_connect('/remote/viewer/ws', headers=headers) as ws:
                ws.send_json({'t': 'attach', 'grant': fresh})
                self.assertEqual(ws.receive_json()['generation'], 2)
            self.assertIs(self.rt.sessions['reg-1'].context, context)

    def test_atomic_grant_reuse_and_stale_generation(self):
        grant = self.opened()
        with self.assertRaises(PortFailure):
            self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', s.Sink(), generation=99)
        viewer = self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', s.Sink(), generation=1)
        viewer.dispose()
        with self.assertRaises(PortFailure):
            self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', s.Sink(), generation=1)

    def test_websocket_origin_owner_and_url_rejected(self):
        grant = self.opened()
        with TestClient(self.app('http://testserver')) as client:
            client.cookies.set('session', 'session-b')
            with client.websocket_connect('/remote/viewer/ws', headers={'origin': 'http://testserver'}) as ws:
                ws.send_json({'t': 'attach', 'grant': grant})
                self.assertEqual(ws.receive()['type'], 'websocket.close')
            client.cookies.set('session', 'session-a')
            for path, origin in [('/remote/viewer/ws', 'http://foreign.invalid'),
                                 ('/remote/viewer/ws?grant=synthetic', 'http://testserver')]:
                with self.subTest(path=path, origin=origin), self.assertRaises(WebSocketDisconnect):
                    with client.websocket_connect(path, headers={'origin': origin}):
                        self.fail('forbidden connection accepted')
            with client.websocket_connect('/remote/viewer/ws', headers={'origin': 'http://testserver'}) as ws:
                ws.send_json({'t': 'attach', 'grant': grant})
                self.assertEqual(ws.receive_json()['state'], 'human')

    def serve_ui(self):
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        origin = f'http://127.0.0.1:{listener.getsockname()[1]}'
        server = uvicorn.Server(uvicorn.Config(self.app(origin), log_level='critical', access_log=False))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
        thread.start()

        def shutdown():
            server.should_exit = True
            thread.join(10)
            listener.close()

        self.addCleanup(shutdown)
        self.assertTrue(s.wait_until(lambda: server.started))
        return origin

    def test_actual_mount_login_finish_detach(self):
        origin = self.serve_ui()
        grant = self.opened()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.context.add_cookies([{'name': 'session', 'value': 'session-a', 'url': origin}])
                requests = []
                page.on('request', lambda r: requests.append(r.url))
                page.goto(origin)
                page.locator('.tab-btn[data-target="surface-auth"]').click()
                page.evaluate('''async grant => {
                    const {mount} = await import('/remote/viewer.js');
                    window.mount = mount; window.events = [];
                    window.handle = mount(document.querySelector('#viewer-container'), grant, e => events.push(e));
                }''', grant)
                page.wait_for_function("events.includes('ready') && document.querySelector('canvas').width === 1280")
                canvas = page.locator('canvas')
                for field, text in [('username', 'acct-a'), ('password', self.site.accounts['acct-a'])]:
                    x, y = s.LOGIN_POS[field]
                    box = canvas.bounding_box()
                    canvas.click(position={'x': x * box['width'] / 1280, 'y': y * box['height'] / 800})
                    # Text is entered through DOM key events and the real WS, never the remote driver.
                    page.keyboard.type(text)
                x, y = s.LOGIN_POS['login']
                box = canvas.bounding_box()
                canvas.click(position={'x': x * box['width'] / 1280, 'y': y * box['height'] / 800})
                self.assertTrue(s.wait_until(lambda: self.site.logins == 1))
                self.rt.authenticate(auth('reg-1', 'owner-a', 'finish', generation=1))
                page.wait_for_timeout(100)
                before = len([x for x in self.rt.sessions['reg-1'].audit if x['event'] == 'input'])
                canvas.click(position={'x': 10, 'y': 10})
                page.keyboard.type('blocked-after-finish')
                page.wait_for_timeout(100)
                self.assertEqual(before, len([x for x in self.rt.sessions['reg-1'].audit if x['event'] == 'input']))
                page.evaluate('handle.dispose(); handle.dispose()')
                self.assertEqual(page.locator('canvas').count(), 0)
                self.assertEqual(self.rt.sessions['reg-1'].state, 'verified')
                self.assertTrue(all('grant=' not in url for url in requests))
                self.assertEqual(page.evaluate('localStorage.length + sessionStorage.length'), 0)
            finally:
                browser.close()

    def test_browser_rapid_remount_and_immediate_dispose(self):
        origin = self.serve_ui()
        grant = self.opened()
        context = self.rt.sessions['reg-1'].context
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.context.add_cookies([{'name': 'session', 'value': 'session-a', 'url': origin}])
                page.goto(origin)
                page.locator('.tab-btn[data-target="surface-auth"]').click()
                page.evaluate('''async () => {
                    window.mount = (await import('/remote/viewer.js')).mount;
                    window.viewerEvents = [];
                }''')
                # Tear down during CONNECTING, before the first attach can finish.
                page.evaluate('''grant => {
                    const handle = mount(document.querySelector('#viewer-container'), grant);
                    handle.dispose(); handle.dispose();
                }''', grant)
                self.assertEqual(page.locator('canvas').count(), 0)
                for generation in range(1, 4):
                    fresh = self.rt.authenticate(auth('reg-1', 'owner-a', 'refresh', generation=generation))['grant']
                    page.evaluate('''grant => {
                        window.viewerEvents = [];
                        window.handle = mount(document.querySelector('#viewer-container'), grant,
                                              event => viewerEvents.push(event));
                    }''', fresh)
                    page.wait_for_function("viewerEvents.includes('ready')", timeout=5000)
                    self.assertEqual(page.locator('canvas').count(), 1)
                    self.assertEqual(len(self.rt.sessions['reg-1'].viewers), 1)
                    page.evaluate('handle.dispose()')
                    self.assertEqual(page.locator('canvas').count(), 0)
                    self.assertTrue(s.wait_until(lambda: not self.rt.sessions['reg-1'].viewers))
                page.keyboard.type('input-after-detach')
                self.assertFalse(any(item['event'] == 'input' for item in self.rt.sessions['reg-1'].audit))
                self.assertIs(self.rt.sessions['reg-1'].context, context)
                self.assertEqual(self.rt.sessions['reg-1'].state, 'human')
            finally:
                browser.close()

    def test_finish_discards_queued_input(self):
        from unittest.mock import patch
        grant = self.opened()
        viewer = self.rt.attach_viewer(grant['viewer_grant'], 'owner-a', s.Sink())
        s.human_login_via_viewer(viewer, 'acct-a', self.site.accounts['acct-a'])
        self.assertTrue(s.wait_until(lambda: self.site.logins == 1))
        locked = threading.Event()
        release = threading.Event()

        async def block():
            async with self.rt.sessions['reg-1'].input_lock:
                locked.set()
                await asyncio.to_thread(release.wait)

        self.host.spawn(block())
        self.assertTrue(locked.wait(2))
        self.addCleanup(release.set)
        errors = []

        def finish():
            try:
                self.rt.authenticate(auth('reg-1', 'owner-a', 'finish', generation=1))
            except Exception as exc:
                errors.append(type(exc).__name__)

        with patch('lesson_registration.remote.viewer._apply_input') as applied:
            viewer.receive({'t': 'text', 'text': 'must-be-discarded'})
            worker = threading.Thread(target=finish)
            worker.start()
            self.assertTrue(s.wait_until(lambda: self.rt.sessions['reg-1'].state == 'verifying'))
            release.set()
            worker.join(10)
            self.assertFalse(worker.is_alive())
            self.assertEqual(errors, [])
            applied.assert_not_called()
