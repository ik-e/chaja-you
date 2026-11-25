"""Explicit mock Runtime binding. The caller supplies a restricted approved-asset reader.

The reader is per accepted registration. R03 must enforce owner/lease authorization
inside that reader. No STORE, filesystem path or raw browser is exposed to the adapter.
"""
import hashlib

from .adapter import KmongAdapter
from .errors import KmongError
from .page import KmongContext, NavigationUnknown, PageStructureError, PageView
from .profile import PROFILE_ID


class ApprovedAssets:
    def __init__(self, refs, read):
        self._refs = {ref['asset_id']: dict(ref) for ref in refs}
        self._read = read

    def read(self, asset_id, digest):
        ref = self._refs.get(asset_id)
        if ref is None or ref['digest'] != digest:
            raise KmongError('PERMISSION_DENIED', 'asset is outside accepted scope', 'absent')
        try:
            data = self._read(asset_id)
        except Exception:
            raise KmongError('PERMISSION_DENIED', 'approved asset could not be read', 'absent') from None
        if (not isinstance(data, bytes) or len(data) != ref['bytes']
                or hashlib.sha256(data).hexdigest() != digest):
            raise KmongError('VALIDATION_FAILED', 'approved asset bytes differ', 'absent')
        return data


def mock_runtime_binding(origin, approved_reader_for_scope):
    """Build a PlatformBinding when the remote package is present.

    ``approved_reader_for_scope(accepted) -> read(asset_id)`` is an internal
    injection point awaiting the R03 approved asset API. It must authorize each
    read against the current registration, owner and lease.
    """
    from lesson_registration.remote import Identity, PlatformBinding

    def identify(page):
        view = page.goto('/home')
        account = view.one('account_ref')
        return Identity(account, account) if view.page == 'home' and account else None

    def resolve_target(page, identity):
        from urllib.parse import quote
        view = page.goto('/slots/' + quote(identity['slot_ref'], safe='') + '/receipt')
        if view.one('account_ref') != identity['external_account_ref']:
            return 'ambiguous', 'account not verified'
        if view.page == 'receipt_absent':
            return 'new', 'no receipt observed'
        if view.page == 'receipt':
            return 'existing', 'receipt observed'
        return 'ambiguous', 'target not resolved'

    def make_context(accepted, page, now):
        assets = ApprovedAssets(accepted['scope']['assets'], approved_reader_for_scope(accepted))
        return KmongContext(accepted, page, assets, now)

    return PlatformBinding(PROFILE_ID, origin, '/login', identify, resolve_target, KmongAdapter(), make_context,
                           unknown_exc=NavigationUnknown, structure_exc=PageStructureError,
                           view_factory=PageView)
