"""Optional bounded synchronous extractor deadline.

The remote call may continue after timeout; its result is never returned to a
later call. One daemon worker per wrapper prevents accumulating pending calls.
"""
from __future__ import annotations

import queue
import threading

from .provider import Extractor


class DeadlineExtractor:
    def __init__(self, delegate: Extractor, timeout_seconds: float):
        if timeout_seconds <= 0:
            raise ValueError('positive timeout required')
        self.delegate = delegate
        self.timeout_seconds = timeout_seconds
        self._slot = threading.Lock()

    def extract(self, source_text: str, fields: list[dict]) -> list[dict]:
        if not self._slot.acquire(blocking=False):
            raise TimeoutError('previous model call is still running')
        output: queue.Queue = queue.Queue(maxsize=1)

        def invoke():
            try:
                output.put((True, self.delegate.extract(source_text, fields)))
            except BaseException as exc:
                output.put((False, exc))
            finally:
                self._slot.release()

        try:
            threading.Thread(target=invoke, daemon=True).start()
        except Exception:
            self._slot.release()
            raise
        try:
            ok, value = output.get(timeout=self.timeout_seconds)
        except queue.Empty:
            raise TimeoutError('model deadline exceeded') from None
        if ok:
            return value
        if isinstance(value, Exception):
            raise value
        raise RuntimeError('model worker failed')
