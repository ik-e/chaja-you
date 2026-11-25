"""AC1/AC2 (I3 + viewer): direct human sign-in through the viewer, grant/generation rules,
session isolation, origin pinning, timeout. Real browser (Playwright) against the neutral mock."""
import time
import unittest

import support as s
from contracts.interfaces import PortFailure
from lesson_registration.remote import RemoteRuntime
from lesson_registration.remote.browser import BrowserHost

REF = {"platform": "kmong", "object_kind": "service_listing", "version": "mock.v2", "digest": "a" * 64,
       "environment": "mock"}


def auth(rid, owner, action, **kw):
    cmd = {"action": action, "expected_revision": 1, **kw}
    return {"registration_id": rid, "profile_ref": REF, "owner_ref": owner, "command": cmd}


class BrowserCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = BrowserHost()

    @classmethod
    def tearDownClass(cls):
        cls.host.close()

    def setUp(self):
        self.other = s.NeutralSite().start()            # a different origin
        self.addCleanup(self.other.stop)
        self.site = s.NeutralSite(extra_html=f'<img src="{self.other.origin}/pixel.png">').start()
        self.addCleanup(self.site.stop)
        self.rt = RemoteRuntime([s.binding(self.site, s.NeutralDriver({}))], store=None, host=self.host)
        self.addCleanup(self.rt.close)

    def open(self, rid="reg-1", owner="owner-a"):
        out = self.rt.authenticate(auth(rid, owner, "open"))
        sink = s.Sink()
        viewer = self.rt.attach_viewer(out["grant"]["viewer_grant"], owner, sink)
        return out, sink, viewer

    def login(self, viewer, account="acct-a", logins=1):
        s.human_login_via_viewer(viewer, account, self.site.accounts[account])
        self.assertTrue(s.wait_until(lambda: self.site.logins >= logins), "viewer sign-in did not reach the site")

    def code(self, fn, *a):
        with self.assertRaises(PortFailure) as e:
            fn(*a)
        return e.exception.error["code"]


class DirectAuth(BrowserCase):
    def test_open_streams_frames_and_human_signs_in_through_viewer(self):
        out, sink, viewer = self.open()
        self.assertEqual(out["auth"], {"state": "human", "generation": 1})
        self.assertTrue(sink.wait_for(lambda m: m.get("t") == "frame"), "no screencast frame")
        self.login(viewer)
        fin = self.rt.authenticate(auth("reg-1", "owner-a", "finish", generation=1))
        self.assertEqual(fin["auth"]["state"], "verified")
        self.assertEqual(fin["connection"]["account_ref"], "acct-a")
        self.assertEqual(fin["target"]["identity"]["external_account_ref"], "acct-a")   # read from the page
        self.assertEqual(fin["connection"]["verified_generation"], 1)
        self.assertEqual(fin["target"]["status"], "new")

    def test_input_fenced_after_finish_and_audit_has_no_typed_text(self):
        _, sink, viewer = self.open()
        self.login(viewer)
        self.rt.authenticate(auth("reg-1", "owner-a", "finish", generation=1))
        self.assertFalse(viewer.receive({"t": "text", "text": "late input"}))
        self.assertTrue(sink.wait_for(lambda m: m.get("t") == "input_rejected"))
        audit = repr(self.rt.sessions["reg-1"].audit)
        self.assertNotIn(self.site.accounts["acct-a"], audit)
        self.assertNotIn("acct-a", audit)
        self.assertNotIn("late input", audit)

    def test_finish_without_sign_in_closes_session(self):
        self.open()
        self.assertEqual(self.code(self.rt.authenticate, auth("reg-1", "owner-a", "finish", generation=1)), "AUTH_REQUIRED")
        self.assertEqual(self.rt.sessions["reg-1"].state, "closed")

    def test_stale_generation_and_foreign_owner_denied(self):
        out, _, viewer = self.open()
        self.assertEqual(self.code(self.rt.authenticate, auth("reg-1", "owner-a", "finish", generation=7)),
                         "CONNECTION_MISMATCH")
        self.assertEqual(self.code(self.rt.authenticate, auth("reg-1", "owner-b", "close", generation=1)),
                         "PERMISSION_DENIED")
        self.assertEqual(self.code(self.rt.attach_viewer, out["grant"]["viewer_grant"], "owner-b", s.Sink()),
                         "PERMISSION_DENIED")
        self.assertEqual(self.code(self.rt.attach_viewer, "forged-grant", "owner-a", s.Sink()), "PERMISSION_DENIED")

    def test_refresh_rotates_grant_keeps_connection(self):
        out, old_sink, old_viewer = self.open()
        self.login(old_viewer)
        new = self.rt.authenticate(auth("reg-1", "owner-a", "refresh", generation=1))
        self.assertEqual(new["auth"]["generation"], 2)
        self.assertNotEqual(new["grant"]["viewer_grant"], out["grant"]["viewer_grant"])
        self.assertTrue(old_viewer.closed)
        self.assertFalse(old_viewer.receive({"t": "text", "text": "x"}))
        self.assertEqual(self.code(self.rt.attach_viewer, out["grant"]["viewer_grant"], "owner-a", s.Sink()),
                         "PERMISSION_DENIED")
        self.rt.attach_viewer(new["grant"]["viewer_grant"], "owner-a", s.Sink())
        fin = self.rt.authenticate(auth("reg-1", "owner-a", "finish", generation=2))
        self.assertEqual(fin["connection"]["verified_generation"], 2)
        self.assertEqual(self.site.logins, 1)                 # same browser connection, no second sign-in

    def test_close_discards_connection(self):
        out, _, viewer = self.open()
        self.login(viewer)
        self.assertEqual(self.rt.authenticate(auth("reg-1", "owner-a", "close", generation=1)), {"auth": {"state": "closed"}})
        self.assertTrue(viewer.closed)
        self.assertIsNone(self.rt.sessions["reg-1"].context)
        again = self.rt.authenticate(auth("reg-1", "owner-a", "open"))
        self.assertEqual(again["auth"]["generation"], 2)      # new generation, fresh browser context


class Isolation(BrowserCase):
    def test_sessions_do_not_share_browser_state(self):
        _, _, va = self.open("reg-a", "owner-a")
        self.login(va, "acct-a")
        _, _, vb = self.open("reg-b", "owner-a")
        b_page = self.rt.sessions["reg-b"].scoped_page
        self.assertEqual(b_page.goto("/account").page, "login")      # A's cookie not visible to B
        self.login(vb, "acct-b", logins=2)
        fa = self.rt.authenticate(auth("reg-a", "owner-a", "finish", generation=1))
        fb = self.rt.authenticate(auth("reg-b", "owner-a", "finish", generation=1))
        self.assertEqual((fa["connection"]["account_ref"], fb["connection"]["account_ref"]), ("acct-a", "acct-b"))
        self.assertNotEqual(fa["connection"]["connection_ref"], fb["connection"]["connection_ref"])

    def test_other_origins_blocked_and_navigation_pinned(self):
        _, _, viewer = self.open()
        self.login(viewer)
        page = self.rt.sessions["reg-1"].scoped_page
        self.assertEqual(page.goto("/account").page, "account")       # page embeds an image from another origin
        time.sleep(0.3)
        self.assertEqual(self.other.hits, 0)
        for bad in (self.other.origin + "/account", "//127.0.0.1/x", "account", "/a b"):
            with self.subTest(bad), self.assertRaises(s.PageStructureError):
                page.goto(bad)

    def test_idle_timeout_closes_prestart_session(self):
        self.rt.idle_ttl_sec = 0
        out, _, viewer = self.open()
        time.sleep(0.05)
        self.assertEqual(self.rt.reap(), ["reg-1"])
        self.assertTrue(viewer.closed)
        self.assertEqual(self.code(self.rt.attach_viewer, out["grant"]["viewer_grant"], "owner-a", s.Sink()),
                         "PERMISSION_DENIED")


if __name__ == "__main__":
    unittest.main()
