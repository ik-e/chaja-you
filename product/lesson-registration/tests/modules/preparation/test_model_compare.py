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

    def test_fixture_digest_change_blocks_before_network(self):
        with patch.object(model_compare, 'FIXTURE_SHA256', 'not-the-fixture-digest'), \
             patch.object(model_compare, 'urlopen', side_effect=AssertionError('network called')):
            with self.assertRaises(ValueError):
                model_compare.cases()

    def test_approved_plan_caps_at_40_calls_without_live_network(self):
        fake_result = {'verdict': 'pass', 'http_status': 200, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
        with patch.object(model_compare.sys, 'argv', ['model_compare.py', '--run']), \
             patch.dict(model_compare.os.environ, {'OPENAI_API_KEY': 'fake-test-key'}), \
             patch.object(model_compare, 'run_case', return_value=fake_result) as fake_run, \
             patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(model_compare.main(), 0)
        self.assertEqual(fake_run.call_count, 40)
        self.assertNotIn('fake-test-key', output.getvalue())

    def test_estimate_limit_stops_before_next_call(self):
        expensive = {'verdict': 'pass', 'http_status': 200,
                     'usage': {'input_tokens': 1_000_000, 'output_tokens': 1_000_000}}
        with patch.object(model_compare.sys, 'argv', ['model_compare.py', '--run']), \
             patch.dict(model_compare.os.environ, {'OPENAI_API_KEY': 'fake-test-key'}), \
             patch.object(model_compare, 'run_case', return_value=expensive) as fake_run, \
             patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(model_compare.main(), 1)
        self.assertEqual(fake_run.call_count, 1)
        self.assertIn('estimated_budget', output.getvalue())

    def test_missing_usage_stops_before_next_call(self):
        with patch.object(model_compare.sys, 'argv', ['model_compare.py', '--run']), \
             patch.dict(model_compare.os.environ, {'OPENAI_API_KEY': 'fake-test-key'}), \
             patch.object(model_compare, 'run_case', return_value={'verdict': 'error', 'http_status': 200, 'usage': None}) as fake_run, \
             patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(model_compare.main(), 1)
        self.assertEqual(fake_run.call_count, 1)
        self.assertIn('usage_unavailable', output.getvalue())
