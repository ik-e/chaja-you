"""Synthetic deadline and bounded-worker tests; no external API is called."""
import threading
import unittest

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.preparation.deadline import DeadlineExtractor
from lesson_registration.preparation.provider import PreparationProvider
from test_provider import request


class DelayedExtractor:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()
        self.calls = 0

    def extract(self, source_text, fields):
        self.calls += 1
        if self.calls > 1:
            return [{'field': '/title', 'value': '새 합성 제목', 'quote': '새 합성 제목'}]
        self.started.set()
        self.release.wait(1)
        self.finished.set()
        return [{'field': '/title', 'value': '이전 합성 제목', 'quote': '이전 합성 제목'}]


class DeadlineTests(unittest.TestCase):
    def test_timeout_is_safe_and_late_call_cannot_be_reused(self):
        delegate = DelayedExtractor()
        wrapper = DeadlineExtractor(delegate, 0.02)
        provider = PreparationProvider(contract.catalog(), wrapper)
        try:
            with self.assertRaises(PortFailure) as error:
                provider.prepare(request('kmong', '제목은 이전 합성 제목입니다.'))
            self.assertEqual(error.exception.error['code'], 'MODEL_UNAVAILABLE')
            self.assertTrue(delegate.started.is_set())
            with self.assertRaises(PortFailure) as busy:
                provider.prepare(request('kmong', '제목은 다른 합성 제목입니다.'))
            self.assertEqual(busy.exception.error['code'], 'MODEL_UNAVAILABLE')
        finally:
            delegate.release.set()
            self.assertTrue(delegate.finished.wait(1))
        # Wait for the timed-out worker to leave its bounded slot, then verify
        # that the next request receives only its own result.
        with wrapper._slot:
            pass
        newer = provider.prepare(request('kmong', '제목은 새 합성 제목입니다.'))
        self.assertEqual(newer['values']['title'], '새 합성 제목')
        self.assertFalse(any(f['value'] == '이전 합성 제목' for f in newer['facts']))

    def test_invalid_deadline_is_rejected(self):
        with self.assertRaises(ValueError):
            DeadlineExtractor(DelayedExtractor(), 0)
