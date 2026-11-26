"""Opt-in D05 integration probes; failures are recorded, not hidden by CI.

Run against a selected combination of R02/R03 code with PYTHONPATH=.:src.
No network, API key, or real account is used.
"""
import copy
import tempfile
import threading
import unittest
from pathlib import Path

import dev
from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.store import Store
from lesson_registration.preparation.deadline import DeadlineExtractor
from lesson_registration.preparation.provider import PreparationProvider
from test_provider import FakeExtractor


class SwitchExtractor(FakeExtractor):
    def __init__(self):
        super().__init__()
        self.pause_next = False
        self.started = threading.Event()
        self.release = threading.Event()

    def extract(self, source_text, fields):
        if self.pause_next:
            self.pause_next = False
            self.started.set()
            self.release.wait(2)
        return super().extract(source_text, fields)


class D05Probe(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.extractor = SwitchExtractor()
        self.provider = PreparationProvider(contract.catalog(), self.extractor)
        self.co = Coordinator(Store(Path(self.temp.name) / 'test.sqlite3'), prep=self.provider)
        source = self.co.create_source('synthetic-owner', {'raw_text': '첫 패키지 가격은 180000원입니다.'})
        self.view = self.co.create_registration('synthetic-owner', {'source_id': source['source_id'], 'selector': 'kmong'})
        self.values = copy.deepcopy(dev.fixtures()['kmong']['cases']['I2']['output']['values'])
        self.values['packages'][0]['amount_vat_included_krw'] = 180000

    def populate(self):
        answers = [{'issue_id': i['issue_id'], 'value': self.values[i['field'][1:]]}
                   for i in self.view['preparation']['issues']]
        self.view = self.co.edit_registration('synthetic-owner', self.view['registration_id'],
                    {'expected_revision': self.view['revision'], 'answers': answers})
        if any(i['field'] == '/region' for i in self.view['preparation']['issues']):
            self.view = self.co.edit_registration('synthetic-owner', self.view['registration_id'],
                        {'expected_revision': self.view['revision'],
                         'corrections': [{'field': '/region', 'value': self.values['region']}]})
        self.assertTrue(self.view['preparation']['ready'])

    def edit(self, field, value):
        return self.co.edit_registration('synthetic-owner', self.view['registration_id'],
            {'expected_revision': self.view['revision'], 'corrections': [{'field': field, 'value': value}]})

    def test_leaf_edit_keeps_siblings(self):
        self.populate()
        changed = self.edit('/packages/0/amount_vat_included_krw', 190000)
        self.assertEqual(changed['preparation']['values']['packages'][0]['amount_vat_included_krw'], 190000)
        self.assertEqual(changed['preparation']['values']['packages'][1:], self.values['packages'][1:])

    def test_source_conflict_keeps_previous_revision(self):
        self.populate()
        self.extractor.candidates = [{'field': '/packages/0/amount_vat_included_krw',
                                      'value': 180000, 'quote': '180000원'}]
        with self.assertRaises(AppError) as error:
            self.edit('/packages/0/amount_vat_included_krw', 190000)
        self.assertEqual(error.exception.code, 'FACT_CONFLICT')
        self.assertEqual(self.co.get_registration('synthetic-owner', self.view['registration_id'])['revision'], self.view['revision'])

    def test_missing_parent_does_not_replace_preparation(self):
        with self.assertRaises(AppError) as error:
            self.edit('/packages/0/amount_vat_included_krw', 190000)
        self.assertEqual(error.exception.code, 'VALIDATION_FAILED')
        self.assertEqual(self.co.get_registration('synthetic-owner', self.view['registration_id'])['revision'], self.view['revision'])

    def test_edit_timeout_keeps_previous_revision(self):
        self.populate()
        self.co.prep = PreparationProvider(contract.catalog(), DeadlineExtractor(self.extractor, 0.02))
        self.extractor.pause_next = True
        try:
            with self.assertRaises(AppError) as error:
                self.edit('/title', '합성 제목 수정')
            self.assertEqual(error.exception.code, 'MODEL_UNAVAILABLE')
            self.assertEqual(self.co.get_registration('synthetic-owner', self.view['registration_id'])['revision'], self.view['revision'])
        finally:
            self.extractor.release.set()

    def test_late_result_does_not_overwrite_new_revision(self):
        self.populate()
        self.extractor.pause_next = True
        output = []
        def old_edit():
            try:
                self.edit('/title', '오래된 합성 제목')
            except AppError as error:
                output.append(error.code)
        worker = threading.Thread(target=old_edit, daemon=True)
        worker.start()
        try:
            self.assertTrue(self.extractor.started.wait(1))
            new = self.edit('/title', '새 합성 제목')
        finally:
            self.extractor.release.set()
            worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(output, ['STALE_REVISION'])
        current = self.co.get_registration('synthetic-owner', self.view['registration_id'])
        self.assertEqual(current['revision'], new['revision'])
        self.assertEqual(current['preparation']['values']['title'], '새 합성 제목')


if __name__ == '__main__':
    unittest.main(verbosity=2)
