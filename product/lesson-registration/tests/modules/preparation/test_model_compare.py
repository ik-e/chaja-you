"""Offline checks for the opt-in, synthetic model comparison harness."""
import io
import json
import unittest
from unittest.mock import patch

import model_compare


class ModelComparisonTests(unittest.TestCase):
    def test_no_explicit_flag_makes_no_network_calls(self):
        with patch.object(model_compare.sys, "argv", ["model_compare.py"]), \
             patch.object(model_compare, "urlopen", side_effect=AssertionError("network called")):
            self.assertEqual(model_compare.main(), 2)

    def test_title_pass_and_unsupported_output_fail(self):
        candidate = {"field": "/title", "value": "합성 기타 레슨", "kind": "text", "quote": "합성 기타 레슨"}
        response = {"status": "completed", "usage": {"input_tokens": 20, "output_tokens": 10, "total_tokens": 30},
                    "output": [{"type": "message", "content": [{"type": "output_text",
                               "text": json.dumps({"candidates": [candidate]}, ensure_ascii=False)}]}]}

        class HTTPResponse(io.BytesIO):
            status = 200

        def open_fake(request, timeout):
            return HTTPResponse(json.dumps(response, ensure_ascii=False).encode())

        with patch.object(model_compare, "urlopen", open_fake):
            result = model_compare.run_case("synthetic-key", "fake-model", model_compare.cases()[0])
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["usage"]["total_tokens"], 30)
        self.assertNotIn("synthetic-key", json.dumps(result))
        self.assertFalse(model_compare.passed("title", {"values": {}, "issues": [], "facts": []}))

    def test_missing_case_does_not_pass_when_values_are_fabricated(self):
        result = {"ready": False, "values": {"packages": []}, "issues": [], "facts": []}
        self.assertFalse(model_compare.passed("price_missing", result))
        result = {"ready": False, "values": {"category": "fabricated"}, "issues": [], "facts": []}
        self.assertFalse(model_compare.passed("soomgo_missing", result))
