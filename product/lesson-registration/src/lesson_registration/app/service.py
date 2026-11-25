"""Single-process mock service lifecycle; workers outlive individual HTTP requests.

One service per database. Provider calls must be bounded by the provider; Python
threads cannot forcibly interrupt a hung browser/SDK call. No replay fallback.
"""
from concurrent.futures import ThreadPoolExecutor
import json

from .store import atomic


class AppService:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.pool = None

    def start(self):
        if self.pool is not None or self.coordinator.on_accepted is not None:
            raise RuntimeError("coordinator already has a dispatcher")
        self.coordinator.recover()
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="registration")
        self.coordinator.on_accepted = self.submit

    def submit(self, registration_id):
        # Called only after durable acceptance; errors now belong to the job.
        try:
            self.pool.submit(self._run, registration_id)
        except Exception:
            self._stop(registration_id)

    def _run(self, registration_id):
        try:
            self.coordinator.run_job(registration_id)
        except Exception:
            self._stop(registration_id)

    def _stop(self, registration_id):
        co = self.coordinator
        with co.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
        if job is not None:
            co._conclude(registration_id, json.loads(job["accepted_scope_json"]), None,
                         {"code": "RUNTIME_ERROR", "message": "실행기를 중단했습니다. 자동 재개하지 않습니다."})

    def close(self):
        # ASGI has drained HTTP requests before shutdown; drain accepted workers.
        if self.pool is not None:
            self.pool.shutdown(wait=True)
            self.pool = None
            self.coordinator.on_accepted = None


def serve(coordinator, **http_options):
    """Explicit local launcher. Prints only the bound URL; never request/grant data."""
    import socket
    import uvicorn
    from .http import create_app

    app = create_app(coordinator, **http_options)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        print(f"Mock API: http://127.0.0.1:{sock.getsockname()[1]}", flush=True)
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0,
                                              access_log=False, ws="none"))
        server.run(sockets=[sock])
