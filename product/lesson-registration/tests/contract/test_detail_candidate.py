"""Independent candidate checks; no actual product provider or real account."""
import asyncio
import concurrent.futures
import copy
import json
from pathlib import Path
import tempfile
import threading
import unittest

from contracts.canonical import asset_digest, json_digest
from contracts.detail_candidate import (profile_digest, payload_digest, binding_digest,
    effect_key, default_manifest, operations, check_readback)
from contracts.validation import SchemaCatalog
from evidence.detail_reference import Ledger, Denied, ViewerPolicy, RevisionGate

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT.parents[1] / "docs/artifacts/design/lesson-registration-20261124"

class DigestChecks(unittest.TestCase):
    def test_pinned_profile_and_computed_vectors(self):
        profiles = json.loads((DESIGN / "platform-profiles-v2.json").read_text())
        schema = json.loads((DESIGN / "data-schema-v4.1.json").read_text())
        catalog = SchemaCatalog(schema, profiles)
        replay = json.loads((ROOT/"fixtures/shared/replay.json").read_text())["platforms"]
        for entry in profiles["profiles"]:
            with self.subTest(platform=entry["platform"]):
                scope = copy.deepcopy(replay[entry["platform"]]["cases"]["I4"]["input"]["accepted"]["scope"])
                scope["profile_ref"]["digest"] = profile_digest(entry)
                catalog.named("Scope", scope)
                catalog.profile_values(entry["id"], scope["values"])
                ops = operations(scope, entry, default_manifest(entry))
                self.assertEqual(len(ops), len(entry["steps"]))
                for op in ops:
                    catalog.named("Operation", op)
                self.assertNotEqual(scope["profile_ref"]["digest"], "a"*64)
                self.assertNotEqual(payload_digest(scope["values"]), "b"*64)
                changed = copy.deepcopy(scope)
                changed["revision"] += 1
                updated = operations(changed, entry, default_manifest(entry))
                self.assertTrue(all(x["binding_digest"] != y["binding_digest"] for x,y in zip(ops,updated)))
                self.assertEqual([x["operation_id"] for x in ops],[x["operation_id"] for x in updated])
                bad = default_manifest(entry)
                bad[0]["action_key"] = "tampered"
                with self.assertRaises(ValueError):
                    operations(scope,entry,bad)

    def test_canonical_binding_and_stable_effect(self):
        t = {"environment":"mock","platform":"kmong","external_account_ref":"a","object_kind":"listing","slot_ref":"slot"}
        self.assertEqual(effect_key(t,"submit"), effect_key(dict(reversed(list(t.items()))),"submit"))
        self.assertNotEqual(effect_key(t,"submit"),effect_key({**t,"slot_ref":"other"},"submit"))
        self.assertNotEqual(binding_digest({"values": {"a":[1,2]}},{"step":"K6"}),
                            binding_digest({"values":{"a":[2,1]}},{"step":"K6"}))
        self.assertNotEqual(binding_digest({"x":1},{"action":"save"}),binding_digest({"x":1},{"action":"read"}))

    def test_observed_assets_order_and_missing_values(self):
        approved = {"title":"synthetic","values":[1,2]}
        digests = [asset_digest(b"one"),asset_digest(b"two")]
        self.assertEqual(check_readback(approved,copy.deepcopy(approved),digests,[b"one",b"two"]),"confirmed")
        self.assertEqual(check_readback(approved,approved,digests,[b"two",b"one"]),"not_reached")
        self.assertEqual(check_readback(approved,{"title":"synthetic"},digests,[b"one",b"two"]),"unknown")
        self.assertEqual(check_readback(approved,None,digests,None),"unknown")

class LedgerChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger = Ledger(Path(self.tmp.name)/"candidate.db")
        self.binding = {"connection_ref":"mock-connection","verified_generation":1,"account_ref":"mock-account"}
        self.op = {"operation_id":"op","step_id":"K6","action_key":"save","effect_class":"potential_effect","binding_digest":"a"*64}
        self.ops = [self.op]
        self.ledger.add("r","owner",self.binding,self.ops)

    def ready(self):
        claim = self.ledger.claim("r","owner")
        self.ledger.bind("r",claim,self.binding)
        return claim

    def admit(self,claim):
        return self.ledger.admit("r",claim,self.ops,self.op,"stable-effect")

    def test_eight_worker_claim_race(self):
        barrier = threading.Barrier(8)
        def attempt(_):
            barrier.wait(timeout=5)
            return self.ledger.claim("r","owner")
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            self.assertEqual(sum(c is not None for c in pool.map(attempt,range(8))),1)

    def test_foreign_owner_and_connection(self):
        self.assertIsNone(self.ledger.claim("r","other"))
        c = self.ledger.claim("r","owner")
        for wrong in ({**self.binding,"connection_ref":"other"},{**self.binding,"verified_generation":2},{**self.binding,"account_ref":"other"}):
            with self.assertRaises(Denied): self.ledger.bind("r",c,wrong)
        with self.assertRaises(Denied): self.ledger.bind("r","wrong-claim",self.binding)
        self.ledger.bind("r",c,self.binding)

    def test_unregistered_operation(self):
        c = self.ready()
        for field,value in (("operation_id","other"),("action_key","other"),("binding_digest","b"*64),("effect_class","read")):
            with self.assertRaises(Denied):
                self.ledger.admit("r",c,self.ops,{**self.op,field:value},"stable-effect")

    def test_permit_consumed_once(self):
        c = self.ready()
        token = self.admit(c)
        barrier = threading.Barrier(8)
        def consume(_):
            barrier.wait(timeout=5)
            try:
                self.ledger.consume("r",c,token)
                return 1
            except Denied: return 0
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            self.assertEqual(sum(pool.map(consume,range(8))),1)

    def test_fence_before_consume(self):
        c = self.ready()
        token = self.admit(c)
        self.ledger.fence("r",c)
        with self.assertRaises(Denied): self.ledger.consume("r",c,token)
        with self.assertRaises(Denied): self.admit(c)
        self.assertEqual(self.ledger.snapshot("r")[2],["blocked"])

    def test_consume_fence_concurrent(self):
        c = self.ready()
        token = self.admit(c)
        barrier = threading.Barrier(2)
        def consume():
            barrier.wait(timeout=5)
            try:
                self.ledger.consume("r",c,token)
                return True
            except Denied: return False
        def fence():
            barrier.wait(timeout=5)
            self.ledger.fence("r",c)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            a,b = pool.submit(consume),pool.submit(fence)
            won = a.result(timeout=10)
            b.result(timeout=10)
        self.assertEqual(self.ledger.snapshot("r")[2],["unknown" if won else "blocked"])

    def test_unknown_duplicate_other_registration(self):
        c = self.ready()
        token = self.admit(c)
        self.ledger.consume("r",c,token)
        self.ledger.fence("r",c)
        self.assertEqual(self.ledger.snapshot("r")[2],["unknown"])
        self.ledger.add("new","owner",self.binding,self.ops)
        n = self.ledger.claim("new","owner")
        self.ledger.bind("new",n,self.binding)
        with self.assertRaises(Denied):
            self.ledger.admit("new",n,self.ops,self.op,"stable-effect")

    def test_observation_admission_and_id_conflict(self):
        c = self.ready()
        token = self.admit(c)
        with self.assertRaises(Denied):
            self.ledger.observe("r",c,token,self.op,"e",{"v":1},"confirmed")
        self.ledger.consume("r",c,token)
        for args in (("wrong",token,self.op),(c,"wrong",self.op),(c,token,{**self.op,"operation_id":"other"})):
            with self.assertRaises(Denied):
                self.ledger.observe("r",*args,"e",{"v":1},"confirmed")
        self.ledger.observe("r",c,token,self.op,"e",{"v":1},"confirmed")
        v = self.ledger.snapshot("r")[1]
        self.ledger.observe("r",c,token,self.op,"e",{"v":1},"confirmed")
        self.assertEqual(self.ledger.snapshot("r")[1],v)
        with self.assertRaises(Denied):
            self.ledger.observe("r",c,token,self.op,"e",{"v":2},"confirmed")

    def test_finalize_snapshot_and_terminal_no_reopen(self):
        c = self.ready()
        token = self.admit(c)
        self.ledger.consume("r",c,token)
        old = self.ledger.snapshot("r")[1]
        self.ledger.observe("r",c,token,self.op,"e",{"v":1},"confirmed")
        with self.assertRaises(Denied): self.ledger.finalize("r",c,old,True,1)
        v = self.ledger.snapshot("r")[1]
        self.assertEqual(self.ledger.finalize("r",c,v,True,1),"done")
        with self.assertRaises(Denied): self.ledger.observe("r",c,token,self.op,"late",{},"confirmed")
        self.assertIsNone(self.ledger.claim("r","owner"))

    def test_missing_required_step_stops(self):
        c = self.ready()
        token = self.admit(c)
        self.ledger.consume("r",c,token)
        self.ledger.observe("r",c,token,self.op,"e",{"v":1},"confirmed")
        self.assertEqual(self.ledger.finalize("r",c,self.ledger.snapshot("r")[1],True,2),"stopped")
        self.assertIsNone(self.ledger.claim("r","owner"))

class SessionChecks(unittest.TestCase):
    def setUp(self):
        self.policy = ViewerPolicy("owner","reg","https://mock.invalid")
        self.token,self.gen = self.policy.issue("owner",0,10)
    def attach(self,**changes):
        args = dict(owner="owner",registration="reg",origin="https://mock.invalid",token=self.token,generation=self.gen,now=1)
        args.update(changes)
        return self.policy.attach(**args)

    def test_wrong_owner_registration_origin_expiry(self):
        for x in ({"owner":"other"},{"registration":"other"},{"origin":"https://other.invalid"},{"generation":0},{"now":10},{"token":"wrong"}):
            with self.assertRaises(Denied): self.attach(**x)
        self.assertTrue(self.attach())

    def test_single_use_and_refresh_revokes_input(self):
        conn = self.attach()
        with self.assertRaises(Denied): self.attach()
        self.policy.input(conn,self.gen,1,"text","synthetic-secret")
        token,gen = self.policy.issue("owner",2,10)
        self.assertEqual(self.policy.queue,[])
        with self.assertRaises(Denied): self.policy.input(conn,self.gen,3,"text","synthetic")
        with self.assertRaises(Denied): self.attach()
        self.assertTrue(self.attach(token=token,generation=gen,now=3))

    def test_finish_and_detach_and_no_secret_audit(self):
        conn = self.attach()
        with self.assertRaises(Denied): self.policy.input(conn,self.gen,1,"raw_cdp","synthetic")
        self.policy.input(conn,self.gen,1,"text","synthetic-secret")
        self.policy.finish("owner",self.gen)
        self.assertEqual(self.policy.queue,[])
        with self.assertRaises(Denied): self.policy.input(conn,self.gen,2,"key","a")
        self.policy.detach(conn)
        self.assertEqual(self.policy.state,"verifying")
        self.policy.close()
        self.assertIsNone(self.policy.connection)
        self.assertIsNone(self.policy.token_hash)
        audit = json.dumps(self.policy.audit)
        self.assertNotIn("synthetic-secret",audit)
        self.assertNotIn(self.token,audit)

    def test_expired_grant_and_detach_require_new_attach(self):
        conn = self.attach()
        with self.assertRaises(Denied): self.policy.input(conn,self.gen,10,"key","a")
        self.policy.detach(conn)
        with self.assertRaises(Denied): self.policy.input(conn,self.gen,2,"key","a")
        self.assertEqual(self.policy.state,"human")
        with self.assertRaises(Denied): self.attach()

class LifecycleChecks(unittest.TestCase):
    def test_prep_late_revision_rejected(self):
        gate = RevisionGate()
        version = gate.revision
        gate.invalidate()
        self.assertFalse(gate.commit(version,{"old":True}))
        self.assertTrue(gate.commit(gate.revision,{"new":True}))
        self.assertEqual(gate.value,{"new":True})

    def test_async_bridge_no_event_loop_block(self):
        async def run():
            release = threading.Event()
            entered = threading.Event()
            def worker():
                entered.set()
                return release.wait(timeout=2)
            t = asyncio.create_task(asyncio.to_thread(worker))
            try:
                # Both scheduling and release happen on event loop while worker waits.
                while not entered.is_set():
                    await asyncio.sleep(.001)
                self.assertFalse(t.done())
                release.set()
                self.assertTrue(await asyncio.wait_for(t,2))
            finally:
                release.set()
        asyncio.run(run())

if __name__ == "__main__":
    unittest.main(verbosity=2)
