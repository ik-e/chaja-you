"""Simulated HTTP contract tests; these do not call a real model."""
import io
import json
import unittest
from urllib.error import URLError

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.preparation.openai_extractor import ExtractorResponseError, OpenAIResponsesExtractor
from lesson_registration.preparation.provider import PreparationProvider


class Response:
    def __init__(self, content):
        self.stream = io.BytesIO(content)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()

    def read(self, limit):
        return self.stream.read(limit)


def api_response(candidates):
    return json.dumps({"status": "completed", "output": [{"type": "message", "content": [
        {"type": "output_text", "text": json.dumps({"candidates": candidates}, ensure_ascii=False)}
    ]}]}, ensure_ascii=False).encode("utf-8")


def request():
    return {"source": {"source_id": "synthetic", "raw_text": "제목은 합성 기타 레슨입니다.",
                       "asset_refs": [], "created_at": "2026-11-25T00:00:00Z"},
            "profile": Knowledge().resolve("kmong")["profile"], "answers": []}


class ResponsesExtractorTests(unittest.TestCase):
    def extractor(self, body, calls=None):
        def opener(req, timeout):
            if calls is not None:
                calls.append((req, timeout))
            return Response(body)
        return OpenAIResponsesExtractor("test-key", "test-model", 5, synthetic_input_confirmed=True, opener=opener)

    def test_explicit_request_and_i2_grounding(self):
        calls = []
        candidate = {"field": "/title", "value": "합성 기타 레슨", "kind": "text", "quote": "합성 기타 레슨"}
        extractor = self.extractor(api_response([candidate]), calls)
        result = PreparationProvider(contract.catalog(), extractor).prepare(request())
        self.assertFalse(result["ready"])
        self.assertEqual(result["facts"][0]["value"], "합성 기타 레슨")
        self.assertNotIn("title", result["values"])
        req, timeout = calls[0]
        payload = json.loads(req.data)
        self.assertEqual(req.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(timeout, 5)
        self.assertFalse(payload["store"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertNotIn("test-key", json.dumps(payload))

    def test_literal_guard_drops_fabricated_response(self):
        candidate = {"field": "/title", "value": "없는 정보", "kind": "text", "quote": "없는 정보"}
        result = PreparationProvider(contract.catalog(), self.extractor(api_response([candidate]))).prepare(request())
        self.assertEqual(result["facts"], [])
        self.assertNotIn("title", result["values"])
        self.assertFalse(result["ready"])

    def test_integer_conversion_and_unconfirmed_price(self):
        candidate = {"field": "/packages", "value": "180000", "kind": "integer", "quote": "180,000원"}
        extractor = self.extractor(api_response([candidate]))
        self.assertEqual(extractor.extract("180,000원", [])[0]["value"], 180000)

    def test_malformed_incomplete_refusal_and_duplicate_keys_are_safe_errors(self):
        bodies = [b'not-json', b'{"status":"incomplete","output":[]}',
                  b'{"status":"completed","output":[{"type":"message","content":[{"type":"refusal"}]}]}',
                  b'{"status":"completed","status":"completed","output":[]}']
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(PortFailure) as error:
                PreparationProvider(contract.catalog(), self.extractor(body)).prepare(request())
            self.assertEqual(error.exception.error["code"], "RUNTIME_ERROR")

    def test_network_failure_is_model_unavailable_without_error_details(self):
        def fail(req, timeout):
            raise URLError("private network detail")
        extractor = OpenAIResponsesExtractor("test-key", "test-model", 5, synthetic_input_confirmed=True, opener=fail)
        with self.assertRaises(PortFailure) as error:
            PreparationProvider(contract.catalog(), extractor).prepare(request())
        self.assertEqual(error.exception.error["code"], "MODEL_UNAVAILABLE")
        self.assertNotIn("private network detail", str(error.exception.error))

    def test_configuration_requires_explicit_values(self):
        for key, model, timeout in [("", "model", 5), ("key", "", 5), ("key", "model", 0)]:
            with self.subTest(model=model, timeout=timeout), self.assertRaises(ValueError):
                OpenAIResponsesExtractor(key, model, timeout, synthetic_input_confirmed=True)
        with self.assertRaises(ValueError):
            OpenAIResponsesExtractor("key", "model", 5, synthetic_input_confirmed=False)


if __name__ == "__main__":
    unittest.main()
