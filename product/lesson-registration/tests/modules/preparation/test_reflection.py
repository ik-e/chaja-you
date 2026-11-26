"""Synthetic-only tests for the optional bounded reflection candidate."""
import copy
import unittest

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.preparation.provider import PreparationProvider
from lesson_registration.preparation.reflection import BoundedReflectionExtractor
from test_provider import FakeExtractor, request


class Corrector:
    def __init__(self, result=None, fail=False):
        self.result = result
        self.fail = fail
        self.calls = []

    def correct(self, source_text, fields, candidates, diagnostics):
        self.calls.append(copy.deepcopy(diagnostics))
        if self.fail:
            raise TimeoutError('private details')
        return copy.deepcopy(self.result)


class ReflectionTests(unittest.TestCase):
    def provider(self, initial, corrector):
        return PreparationProvider(contract.catalog(), BoundedReflectionExtractor(FakeExtractor(initial), corrector))

    def test_single_format_correction_preserves_other_grounded_candidates(self):
        initial = [{'field': '/title', 'value': '합성 기타 레슨', 'quote': '합성 기타 레슨'},
                   {'field': '/unknown-price', 'value': 180000, 'quote': '180000원'}]
        repaired = [{'field': '/packages/0/price', 'value': 180000, 'quote': '180000원'}]
        corrector = Corrector(repaired)
        result = self.provider(initial, corrector).prepare(request('kmong', '제목은 합성 기타 레슨입니다. 첫 패키지 180000원'))
        self.assertEqual(len(corrector.calls), 1)
        self.assertEqual(corrector.calls[0], ['unsupported_field'])
        self.assertEqual(result['values']['title'], '합성 기타 레슨')
        self.assertTrue(any(f['path'] == '/packages/0/amount_vat_included_krw' for f in result['facts']))
        self.assertFalse(result['ready'])

    def test_synthetic_ab_corrects_field_without_promoting_missing_vat(self):
        initial = [{'field': '/unknown-price', 'value': 180000, 'quote': '180000원'}]
        inp = request('kmong', '첫 패키지 180000원')
        baseline = PreparationProvider(contract.catalog(), FakeExtractor(initial)).prepare(inp)
        repair = Corrector([{'field': '/packages/0/price', 'value': 180000, 'quote': '180000원'}])
        revised = self.provider(initial, repair).prepare(inp)
        self.assertTrue(any(i['code'] == 'unsupported' for i in baseline['issues']))
        self.assertTrue(any(f['path'] == '/packages/0/amount_vat_included_krw' for f in revised['facts']))
        self.assertFalse(baseline['ready'])
        self.assertFalse(revised['ready'])
        self.assertNotIn('packages', revised['values'])

    def test_correction_cannot_change_or_drop_quote_or_value(self):
        original = [{'field': '/unknown-price', 'value': 180000, 'quote': '180000원'}]
        for repaired in ([], [{'field': '/packages/0/price', 'value': 210000, 'quote': '180000원'}]):
            with self.subTest(repaired=repaired):
                corrector = Corrector(repaired)
                result = self.provider(original, corrector).prepare(request('kmong', '첫 패키지 180000원'))
                self.assertEqual(len(corrector.calls), 1)
                self.assertTrue(any(i['code'] == 'unsupported' and i['blocking'] for i in result['issues']))
                self.assertFalse(result['ready'])
                self.assertNotIn('packages', result['values'])

    def test_source_price_conflict_is_preserved_without_correction(self):
        field = '/packages/0/price'
        initial = [{'field': field, 'value': 180000, 'quote': '180000원'},
                   {'field': field, 'value': 210000, 'quote': '210000원'}]
        corrector = Corrector([])
        result = self.provider(initial, corrector).prepare(request('kmong', '180000원 또는 210000원'))
        self.assertEqual(corrector.calls, [])
        self.assertTrue(any(i['code'] == 'conflict' and i['blocking'] for i in result['issues']))

    def test_ungrounded_value_is_not_a_correction_opportunity(self):
        initial = [{'field': '/unknown-price', 'value': 210000, 'quote': '180000원'}]
        corrector = Corrector([])
        result = self.provider(initial, corrector).prepare(request('kmong', '180000원'))
        self.assertEqual(corrector.calls, [])
        self.assertFalse(result['ready'])
        self.assertNotIn('packages', result['values'])

    def test_corrector_timeout_maps_to_safe_model_unavailable(self):
        initial = [{'field': '/unknown-price', 'value': 180000, 'quote': '180000원'}]
        with self.assertRaises(PortFailure) as error:
            self.provider(initial, Corrector(fail=True)).prepare(request('kmong', '180000원'))
        self.assertEqual(error.exception.error['code'], 'MODEL_UNAVAILABLE')
        self.assertNotIn('private details', str(error.exception.error))
