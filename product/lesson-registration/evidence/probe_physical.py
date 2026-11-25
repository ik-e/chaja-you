"""Synthetic technology probe, not product acceptance; no real sites or accounts."""
import asyncio
import concurrent.futures
import pathlib
import sqlite3
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from jsonschema import Draft202012Validator

class Probe(unittest.TestCase):
    def test_http_ws_thread_bridge(self):
        app = FastAPI()
        @app.get("/probe")
        async def probe():
            return {"value": await asyncio.to_thread(lambda: 1)}
        @app.websocket("/probe")
        async def socket(ws: WebSocket):
            await ws.accept()
            await ws.send_json(await ws.receive_json())
            await ws.close()
        with TestClient(app) as c:
            self.assertEqual(c.get("/probe").json(), {"value": 1})
            with c.websocket_connect("/probe") as ws:
                ws.send_json({"synthetic": True})
                self.assertEqual(ws.receive_json(), {"synthetic": True})

    def test_sqlite_competing_insert(self):
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / "probe.db"
            with sqlite3.connect(path) as c:
                c.execute("CREATE TABLE admissions(effect TEXT PRIMARY KEY)")
            def insert(_):
                with sqlite3.connect(path, timeout=3, isolation_level=None) as c:
                    c.execute("BEGIN IMMEDIATE")
                    n = c.execute("INSERT OR IGNORE INTO admissions VALUES (?)", ("effect",)).rowcount
                    c.commit()
                    return n
            with concurrent.futures.ThreadPoolExecutor(4) as pool:
                self.assertEqual(sum(pool.map(insert, range(8))), 1)

    def test_jsonschema(self):
        validator = Draft202012Validator({"type":"object","properties":{"id":{"type":"integer"}},"required":["id"]})
        self.assertTrue(validator.is_valid({"id":1}))
        self.assertFalse(validator.is_valid({"id":"1"}))

    def test_loopback_context_and_screencast(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>synthetic</h1>")
            def log_message(self, *args): pass
        with HTTPServer(("127.0.0.1",0), Handler) as server:
            t = threading.Thread(target=server.serve_forever,daemon=True)
            t.start()
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    try:
                        a, other = browser.new_context(), browser.new_context()
                        page = a.new_page()
                        page.goto(f"http://127.0.0.1:{server.server_port}/",timeout=10000)
                        self.assertEqual(page.locator("h1").inner_text(),"synthetic")
                        a.add_cookies([{"name":"mock","value":"synthetic","url":page.url}])
                        self.assertFalse(other.cookies())
                        cdp = a.new_cdp_session(page)
                        frames = []
                        def receive(frame):
                            frames.append(bool(frame["data"]))
                            cdp.send("Page.screencastFrameAck",{"sessionId":frame["sessionId"]})
                        cdp.on("Page.screencastFrame",receive)
                        cdp.send("Page.startScreencast",{"format":"jpeg","quality":50})
                        page.wait_for_timeout(1000)
                        cdp.send("Page.stopScreencast")
                        self.assertTrue(any(frames))
                        cdp.detach()
                    finally: browser.close()
            finally:
                server.shutdown()
                t.join()

if __name__ == "__main__":
    unittest.main(verbosity=2)
