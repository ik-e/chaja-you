"""S8 real loopback HTTP, injected synthetic providers, persistent SQLite.

AC1/AC2/AC3; REQ-01/05/08/10. Does not claim actual UI/viewer or product gates.
"""
from contextlib import contextmanager
import json
import socket
import threading
import time
import unittest
from unittest.mock import patch

import httpx
import uvicorn

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError, STATUS
from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.http import create_app
from lesson_registration.app.store import Store
from support import GatewayRuntime, SchemaPrep, mock_image, temp_db


@contextmanager
def running(app):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="critical",
                                          access_log=False, ws="none"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started:
            if not thread.is_alive() or time.monotonic() > deadline:
                raise AssertionError("server failed to start")
            time.sleep(.01)
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5,
                          headers={"X-Mock-Owner": "owner-a"}, trust_env=False) as client:
            yield client
    finally:
        server.should_exit = True
        thread.join(10)
        sock.close()
        if thread.is_alive():
            raise AssertionError("server did not shut down")


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.rt = GatewayRuntime("kmong")
        self.co = Coordinator(Store(self.path), prep=SchemaPrep("kmong"), exec_port=self.rt)
        self.rt.gateway = StoreGateway(Store(self.path))

    def app(self, **kw):
        return create_app(self.co, dev_owner_header=True, **kw)

    def source(self, client):
        manifest = {"raw_text": "합성 원본", "new_assets": [{"part_name": "img", "rights_confirmed": True}]}
        r = client.post("/v1/sources", files=[
            ("manifest", (None, json.dumps(manifest), "application/json")),
            ("img", ("mock.png", mock_image(), "image/png"))])
        self.assertEqual(r.status_code, 201, r.text)
        contract.validate("SourceView", r.json())
        return r.json()

    def ready(self, client):
        src = self.source(client)
        r = client.post("/v1/registrations", json={"source_id": src["source_id"], "selector": self.rt.platform})
        self.assertEqual(r.status_code, 201, r.text)
        reg = r.json()
        url = "/v1/registrations/" + reg["registration_id"]
        r = client.patch(url, json={"expected_revision": reg["revision"], "source_id": src["source_id"]})
        self.assertEqual(r.status_code, 200, r.text)
        reg = r.json()
        opened = client.post(url + "/authentication", json={"action": "open", "expected_revision": reg["revision"]})
        self.assertEqual(opened.status_code, 200, opened.text)
        contract.validate("AuthResponse", opened.json())
        reg = opened.json()["registration"]
        finished = client.post(url + "/authentication", json={"action": "finish", "expected_revision": reg["revision"],
                                                             "generation": reg["auth"]["generation"]})
        self.assertEqual(finished.status_code, 200, finished.text)
        reg = finished.json()["registration"]
        body = {"expected_revision": reg["revision"], "review_digest": reg["review"]["digest"],
                "approved": True, "request_key": "http-start"}
        return src, url, body

    def terminal(self, client, url):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            r = client.get(url)
            self.assertEqual(r.status_code, 200, r.text)
            if r.json()["job_state"] in ("done", "stopped"):
                return r.json()
            time.sleep(.01)
        self.fail("worker did not reach a terminal state")

    def test_h1_to_h9_and_idempotency(self):
        with running(self.app()) as client:
            src, url, body = self.ready(client)
            self.assertEqual(client.get("/v1/sources/" + src["source_id"]).json(), src)
            for path, shape in (("/v1/sources", "SourceList"), ("/v1/registrations", "RegistrationList")):
                r = client.get(path + "?limit=1")
                self.assertEqual(r.status_code, 200)
                contract.validate(shape, r.json())
            r = client.post(url + "/start", json=body)
            self.assertEqual(r.status_code, 202, r.text)
            contract.validate("RegistrationView", r.json())
            done = self.terminal(client, url)
            self.assertEqual(done["job_state"], "done")
            self.assertEqual(done["result"]["goal_verdict"], "confirmed")
            self.assertEqual(client.post(url + "/start", json=body).status_code, 200)
            self.assertEqual(client.post(url + "/start", json={**body, "request_key": "other"}).status_code, 409)
            self.assertEqual(self.rt.executions, 1)
            self.assertNotIn("connection_ref", json.dumps(done))
            self.assertEqual(client.get(url).headers["cache-control"], "no-store")

    def test_worker_outlives_response_and_poll_does_not_block(self):
        entered, release = threading.Event(), threading.Event()
        def block(step):
            if step == "K1":
                entered.set()
                if not release.wait(5):
                    raise RuntimeError("test timeout")
        self.rt.on_step = block
        with running(self.app()) as client:
            try:
                _, url, body = self.ready(client)
                self.assertEqual(client.post(url + "/start", json=body).status_code, 202)
                self.assertTrue(entered.wait(2))
                self.assertEqual(client.get(url).json()["job_state"], "active")
                self.assertEqual(client.post(url + "/start", json=body).status_code, 200)
                self.assertEqual(self.rt.executions, 1)
            finally:
                release.set()
            self.assertEqual(self.terminal(client, url)["job_state"], "done")

    def test_soomgo_full_http_flow(self):
        self.rt = GatewayRuntime("soomgo")
        self.rt.gateway = StoreGateway(Store(self.path))
        self.co = Coordinator(Store(self.path), prep=SchemaPrep("soomgo"), exec_port=self.rt)
        with running(self.app()) as client:
            _, url, body = self.ready(client)
            self.assertEqual(client.post(url + "/start", json=body).status_code, 202)
            self.assertEqual(self.terminal(client, url)["job_state"], "done")

    def test_slow_prep_does_not_block_get(self):
        entered, release = threading.Event(), threading.Event()
        original = self.co.prep.prepare
        def slow(inp):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("test timeout")
            return original(inp)
        with running(self.app()) as client:
            src = self.source(client)
            responses = []
            with patch.object(self.co.prep, "prepare", side_effect=slow):
                thread = threading.Thread(target=lambda: responses.append(client.post("/v1/registrations", json={
                    "source_id": src["source_id"], "selector": "kmong"})))
                thread.start()
                try:
                    self.assertTrue(entered.wait(2))
                    self.assertEqual(client.get("/v1/sources", timeout=1).status_code, 200)
                finally:
                    release.set()
                    thread.join(5)
            self.assertEqual(responses[0].status_code, 201)

    def test_lost_start_response_retries_without_new_execution(self):
        entered, release = threading.Event(), threading.Event()
        def block(step):
            if step == "K1":
                entered.set()
                release.wait(5)
        self.rt.on_step = block
        with running(self.app()) as client:
            _, url, body = self.ready(client)
            raw = json.dumps(body).encode()
            port = client.base_url.port
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=3) as sock:
                    sock.sendall((f"POST {url}/start HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                                  "X-Mock-Owner: owner-a\r\nContent-Type: application/json\r\n"
                                  f"Content-Length: {len(raw)}\r\n\r\n").encode() + raw)
                    self.assertTrue(entered.wait(2))
                    # Close without reading the H7 response.
                self.assertEqual(client.post(url + "/start", json=body).status_code, 200)
                self.assertEqual(self.rt.executions, 1)
            finally:
                release.set()
            self.assertEqual(self.terminal(client, url)["job_state"], "done")

    def test_runtime_failure_is_persisted_not_http_rejection(self):
        self.rt.crash = ("K6", "after_admit")
        with running(self.app()) as client:
            _, url, body = self.ready(client)
            self.assertEqual(client.post(url + "/start", json=body).status_code, 202)
            result = self.terminal(client, url)
            self.assertEqual(result["job_state"], "stopped")
            self.assertEqual(result["result"]["goal_verdict"], "unknown")
            self.assertEqual(client.post(url + "/start", json=body).status_code, 200)
            self.assertEqual(self.rt.executions, 1)

    def test_owner_required_foreign_404_body_cannot_set_owner(self):
        with running(self.app()) as client:
            src = self.source(client)
            path = "/v1/sources/" + src["source_id"]
            self.assertEqual(client.get(path, headers={"X-Mock-Owner": "owner-b"}).status_code, 404)
            self.assertEqual(client.get(path, headers={"X-Mock-Owner": ""}).status_code, 401)
            self.assertEqual(client.post("/v1/sources", json={"raw_text": "x", "owner_ref": "owner-b"}).status_code, 400)
        with running(create_app(self.co)) as client:
            self.assertEqual(client.get("/v1/sources").status_code, 401)

    def test_strict_json_and_list_query(self):
        with running(self.app()) as client:
            for raw in (b'{"raw_text":"a","raw_text":"b"}', b'{"raw_text":NaN}', b'[]', b'{', b'\xff'):
                with self.subTest(raw=raw):
                    self.assertEqual(client.post("/v1/sources", content=raw,
                                                 headers={"Content-Type": "application/json"}).status_code, 400)
            for query in ("limit=0", "limit=abc", "limit=1&limit=2", "owner_ref=other", "cursor=bogus"):
                self.assertEqual(client.get("/v1/sources?" + query).status_code, 400)
            self.assertEqual(client.post("/v1/sources", content="text").status_code, 400)

    def test_multipart_rejects_duplicates_missing_extra_mime_and_truncation(self):
        manifest = ("manifest", (None, json.dumps({"raw_text": "x", "new_assets": [
            {"part_name": "img", "rights_confirmed": True}]}), "application/json"))
        img = ("img", ("mock.png", mock_image(), "image/png"))
        with running(self.app()) as client:
            for parts, status in (([manifest], 400), ([manifest, img, img], 400),
                                  ([manifest, manifest, img], 400), ([img], 400),
                                  ([manifest, img, ("extra", ("x", b"x", "image/png"))], 400),
                                  ([manifest, ("img", ("x", mock_image(), "image/jpeg"))], 422)):
                self.assertEqual(client.post("/v1/sources", files=parts).status_code, status)
            r = client.post("/v1/sources", content=b'--x\r\nContent-Disposition: form-data; name="manifest"\r\n\r\n{}',
                            headers={"Content-Type": "multipart/form-data; boundary=x"})
            self.assertEqual(r.status_code, 400)
            self.assertEqual(client.get("/v1/sources").json()["items"], [])

    def test_body_limit(self):
        with running(self.app(max_body_bytes=32)) as client:
            self.assertEqual(client.post("/v1/sources", json={"raw_text": "x" * 33}).status_code, 400)

    def test_all_error_statuses_and_internal_redaction(self):
        with running(self.app()) as client:
            for code, status in STATUS.items():
                with self.subTest(code=code), patch.object(self.co, "list_sources", side_effect=AppError(code, "safe")):
                    r = client.get("/v1/sources")
                    self.assertEqual(r.status_code, status)
                    contract.validate("Error", r.json())
            with patch.object(self.co, "list_sources", side_effect=RuntimeError("private-internal-value")):
                r = client.get("/v1/sources")
                self.assertEqual(r.status_code, 500)
                self.assertEqual(r.json()["code"], "RUNTIME_ERROR")
                self.assertNotIn("private-internal-value", r.text)

    def test_origin_allowlist_and_host(self):
        origin = "http://127.0.0.1:4321"
        with running(self.app(allowed_origins=(origin,))) as client:
            self.assertEqual(client.get("/v1/sources", headers={"Origin": "https://other.invalid"}).status_code, 403)
            r = client.options("/v1/sources", headers={"Origin": origin, "Access-Control-Request-Method": "POST"})
            self.assertEqual(r.headers["access-control-allow-origin"], origin)
            self.assertEqual(client.get("/v1/sources", headers={"Host": "other.invalid"}).status_code, 403)

    def test_startup_recovers_unfinished_without_dispatch(self):
        # Create an accepted scope with no HTTP dispatcher, simulating a crash.
        with running(self.app()) as client:
            _, url, body = self.ready(client)
        rid = url.rsplit("/", 1)[-1]
        self.assertEqual(self.co.start("owner-a", rid, body)[0], 202)
        with running(self.app()) as client:
            view = client.get(url).json()
            self.assertEqual(view["job_state"], "stopped")
            self.assertEqual(client.post(url + "/start", json=body).status_code, 200)
            self.assertEqual(self.rt.executions, 0)

    def test_dispatch_failure_preserves_202_and_stops(self):
        app = self.app()
        with running(app) as client:
            _, url, body = self.ready(client)
            with patch.object(app.state.service.pool, "submit", side_effect=RuntimeError("queue unavailable")):
                self.assertEqual(client.post(url + "/start", json=body).status_code, 202)
            self.assertEqual(client.get(url).json()["job_state"], "stopped")
            self.assertEqual(self.rt.executions, 0)
