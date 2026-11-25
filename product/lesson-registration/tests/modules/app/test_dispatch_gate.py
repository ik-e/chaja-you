"""Controlled orderings across distinct gateway/coordinator Store instances."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch

from lesson_registration.app.gateway import StoreGateway
from lesson_registration.app.store import Store, tx
from test_s4_atomic import Base


class DispatchGateTests(Base):
    def prepare(self):
        g = self.rt.gateway
        ctx = g.acquire_context(self.rid)
        op = g.expected_operations(ctx)[0]
        return g, ctx, op, g.admit(ctx, op)

    def test_coordinator_fence_first_dispatch_never_called(self):
        g, ctx, op, permit = self.prepare()
        self.co.coord_store.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
        called = []
        self.assertCode("PERMISSION_DENIED", g.dispatch, ctx, permit, op, lambda: called.append(1))
        self.assertEqual(called, [])

    def test_fence_between_consume_and_callback_waits_then_blocks_next(self):
        g, ctx, op, permit = self.prepare()
        consumed, proceed, attempting, fenced = Event(), Event(), Event(), Event()
        invoked = []
        original = g.consume

        def consume(*args):
            original(*args)
            consumed.set()
            if not proceed.wait(5):
                raise AssertionError("test release timeout")

        def fence():
            attempting.set()
            self.co.coord_store.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
            fenced.set()

        def invoke():
            self.assertFalse(fenced.is_set())
            # A separate write succeeds: no SQLite transaction spans the callback.
            with Store(self.path).connect() as conn, tx(conn):
                conn.execute("UPDATE jobs SET updated_at=updated_at WHERE registration_id=?", (self.rid,))
            invoked.append(1)
            return "completed"

        with ThreadPoolExecutor(2) as pool, patch.object(g, 'consume', side_effect=consume):
            dispatch = pool.submit(g.dispatch, ctx, permit, op, invoke)
            try:
                self.assertTrue(consumed.wait(5))
                stop = pool.submit(fence)
                self.assertTrue(attempting.wait(5))
                self.assertFalse(fenced.wait(.1))
            finally:
                proceed.set()
            self.assertEqual(dispatch.result(5), "completed")
            stop.result(5)
        self.assertEqual(invoked, [1])
        self.assertEqual(self.job()["state"], "stopping")
        other = StoreGateway(Store(self.path))
        self.assertCode("PERMISSION_DENIED", other.dispatch, ctx, permit, op, lambda: invoked.append(2))
        self.assertEqual(invoked, [1])

    def test_failed_dispatch_fences_and_never_retries(self):
        g, ctx, op, permit = self.prepare()
        calls = []
        def invoke():
            calls.append(1)
            raise OSError("response lost")
        with self.assertRaises(OSError):
            g.dispatch(ctx, permit, op, invoke)
        self.assertEqual(self.effects()[op['step_id']], 'unknown')
        self.assertCode("PERMISSION_DENIED", g.dispatch, ctx, permit, op, invoke)
        self.assertEqual(calls, [1])

    def test_gateway_fence_and_restart_consumption(self):
        g, ctx, op, permit = self.prepare()
        self.assertEqual(g.dispatch(ctx, permit, op, lambda: 42), 42)
        other = StoreGateway(Store(self.path))
        self.assertCode("PERMISSION_DENIED", other.dispatch, ctx, permit, op, lambda: 43)
        other.fence(self.rid, {"code": "RUNTIME_ERROR", "message": "stop"})
        self.assertEqual(self.job()["state"], 'stopping')
