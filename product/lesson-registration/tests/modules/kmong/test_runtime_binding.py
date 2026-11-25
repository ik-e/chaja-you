"""Scoped asset checks and optional real Runtime/Coordinator integration."""
import copy
import tempfile
import time
import unittest
from pathlib import Path

import dev
import support as s
from lesson_registration.platforms.kmong import KmongError
from lesson_registration.platforms.kmong.runtime_binding import ApprovedAssets, mock_runtime_binding

try:
    from lesson_registration.remote import RemoteRuntime
    from lesson_registration.remote.browser import BrowserHost
except ImportError:
    RemoteRuntime = None


class AssetChecks(unittest.TestCase):
    def test_outside_scope_and_wrong_digest_never_read(self):
        ref = s.base_accepted()['scope']['assets'][0]
        calls = []
        assets = ApprovedAssets([ref], lambda asset_id: calls.append(asset_id))
        for asset_id, digest in [('foreign', ref['digest']), (ref['asset_id'], '0' * 64)]:
            with self.assertRaises(KmongError):
                assets.read(asset_id, digest)
        self.assertEqual(calls, [])

    def test_raw_bytes_verified_before_upload(self):
        ref = s.base_accepted()['scope']['assets'][0]
        assets = ApprovedAssets([ref], lambda _: s.SHARED_IMAGE.read_bytes())
        self.assertEqual(assets.read(ref['asset_id'], ref['digest']), s.SHARED_IMAGE.read_bytes())
        with self.assertRaises(KmongError):
            ApprovedAssets([ref], lambda _: b'changed').read(ref['asset_id'], ref['digest'])


class ReplayPrep:
    def prepare(self, inp):
        prepared = copy.deepcopy(dev.fixtures()['kmong']['cases']['I2']['output'])
        prepared['values']['main_images'] = copy.deepcopy(inp['source']['asset_refs'])
        return prepared


@unittest.skipIf(RemoteRuntime is None, 'requires combined R05 remote + kmong snapshot')
class RealRuntime(unittest.TestCase):
    def setUp(self):
        from lesson_registration.app.coordinator import Coordinator
        from lesson_registration.app.gateway import StoreGateway
        from lesson_registration.app.store import Store
        from lesson_registration.app.runtime_support import RuntimeSupport
        from lesson_registration.app.knowledge import Knowledge
        self.site = s.mock_kmong.MockKmong().start()
        self.addCleanup(self.site.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        store = Store(Path(self.temp.name) / 'app.sqlite3')
        self.store = store
        self.host = BrowserHost()
        self.addCleanup(self.host.close)
        support = RuntimeSupport(store, Knowledge())
        binding = mock_runtime_binding(self.site.base_url,
            approved_reader_for_worker=lambda context: lambda asset_id: support.read_approved_asset(context, asset_id),
            binding_version='binding.v1')
        self.gateway = StoreGateway(store, binding_version='binding.v1')
        self.rt = RemoteRuntime([binding], self.gateway, host=self.host, slot_resolver=support.slot_resolver)
        self.addCleanup(self.rt.close)
        self.co = Coordinator(store, prep=ReplayPrep(), exec_port=self.rt)

    def accept(self):
        owner = 'mock-owner'
        source = self.co.create_source(owner, {'raw_text': '합성 보컬 레슨', 'new_assets': [
            {'part_name': 'image', 'rights_confirmed': True}]}, {'image': s.SHARED_IMAGE.read_bytes()})
        reg = self.co.create_registration(owner, {'source_id': source['source_id'], 'selector': 'kmong'})
        rid = reg['registration_id']
        opened = self.co.authenticate(owner, rid, {'action': 'open', 'expected_revision': reg['revision']})
        viewer = self.rt.attach_viewer(opened['grant']['viewer_grant'], owner, lambda _: None)
        # Use the viewer event channel. Locate synthetic controls only to obtain click coordinates.
        async def positions():
            page = self.rt.sessions[rid].page_handle
            return [await page.locator(selector).bounding_box() for selector in
                    ['input[name=username]', 'input[name=password]', 'button[name=login]']]
        boxes = self.host.run(positions())
        for box, text in zip(boxes[:2], ['mock-account-kmong', self.site.accounts['mock-account-kmong']]):
            viewer.receive({'t': 'mouse', 'type': 'click', 'x': box['x'] + 5, 'y': box['y'] + 5})
            viewer.receive({'t': 'text', 'text': text})
        box = boxes[2]
        viewer.receive({'t': 'mouse', 'type': 'click', 'x': box['x'] + 5, 'y': box['y'] + 5})
        deadline = time.monotonic() + 8
        while len(self.site.sessions) < 1 and time.monotonic() < deadline:
            time.sleep(.05)
        self.assertEqual(len(self.site.sessions), 1)
        reg = opened['registration']
        verified = self.co.authenticate(owner, rid, {'action': 'finish', 'expected_revision': reg['revision'],
                                                      'generation': reg['auth']['generation']})['registration']
        self.assertEqual(verified['auth']['state'], 'verified')
        self.co.start(owner, rid, {'expected_revision': verified['revision'], 'review_digest': verified['review']['digest'],
                                   'approved': True, 'request_key': 'mock-start-' + rid})
        return owner, rid

    def test_same_browser_real_adapter_store_and_readback(self):
        owner, rid = self.accept()
        self.assertEqual(self.co.run_job(rid), 'done')
        self.assertEqual(self.site.submissions, 1)
        self.assertEqual(len(self.site.sessions), 1)
        self.assertEqual(self.co.get_registration(owner, rid)['result']['goal_verdict'], 'confirmed')
        with self.store.connect() as connection:
            row = connection.execute('SELECT COUNT(*) AS total, SUM(consumed) AS used FROM dispatch_permits '
                                     'WHERE registration_id=?', (rid,)).fetchone()
        self.assertEqual((row['total'], row['used']), (7, 7))

    def test_lost_response_has_one_submission_and_no_redispatch(self):
        _, rid = self.accept()
        self.site.faults['submit'] = 'drop_after_commit'
        state = self.co.run_job(rid)
        self.assertEqual(self.site.submissions, 1)
        self.assertEqual(self.co.run_job(rid), state)
        self.assertEqual(self.site.submissions, 1)

    def test_worker_reader_authorization_failure_stops_before_upload(self):
        from unittest.mock import patch
        owner, rid = self.accept()
        with patch('lesson_registration.app.runtime_support.RuntimeSupport.read_approved_asset',
                   side_effect=PermissionError('synthetic lease revoked')):
            self.assertEqual(self.co.run_job(rid), 'stopped')
        self.assertEqual(self.site.submissions, 0)
        self.assertEqual(self.co.get_registration(owner, rid)['result']['error']['code'], 'PERMISSION_DENIED')
