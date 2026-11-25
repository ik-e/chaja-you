"""Exercise the R03 explicit synthetic CLI on both profiles, real loopback HTTP."""
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import time
import unittest

import httpx
from evidence.product_gate import probe_environment

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "http://localhost:8080"


class MockLauncherTests(unittest.TestCase):
    def test_both_profile_launchers(self):
        for platform in ("kmong", "soomgo"):
            with self.subTest(platform=platform):
                child = subprocess.Popen(
                    [sys.executable, "tests/modules/app/mock_server.py", "--platform", platform,
                     "--origin", ORIGIN], cwd=ROOT, env=probe_environment(),
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
                try:
                    line = queue.Queue()
                    threading.Thread(target=lambda: line.put(child.stdout.readline()), daemon=True).start()
                    match = re.fullmatch(r"Mock API: (http://127\.0\.0\.1:\d+)\s*", line.get(timeout=15))
                    self.assertIsNotNone(match, "launcher must report a loopback URL")
                    with httpx.Client(base_url=match[1], headers={"X-Mock-Owner": "demo-a"},
                                      timeout=2, trust_env=False) as client:
                        until = time.monotonic() + 10
                        while True:
                            try:
                                response = client.get("/v1/sources")
                                break
                            except httpx.TransportError:
                                if child.poll() is not None or time.monotonic() > until:
                                    self.fail("mock API did not start")
                                time.sleep(.05)
                        self.assertEqual(response.status_code, 200)
                        created = client.post("/v1/sources", json={"raw_text": "synthetic launcher check"},
                                              headers={"Origin": ORIGIN})
                        self.assertEqual(created.status_code, 201)
                        self.assertEqual(created.headers.get("access-control-allow-origin"), ORIGIN)
                        self.assertEqual(created.headers.get("cache-control"), "no-store")
                        path = "/v1/sources/" + created.json()["source_id"]
                        self.assertEqual(client.get(path).status_code, 200)
                        self.assertEqual(client.get(path, headers={"X-Mock-Owner": "demo-b"}).status_code, 404)
                finally:
                    child.terminate()
                    try:
                        child.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=5)
                    child.stdout.close()
