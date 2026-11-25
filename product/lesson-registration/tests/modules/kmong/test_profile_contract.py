"""AC1 contract side: adapter registry/validation mirror the pinned kmong mock profile."""
import copy
import unittest

import support as s
from lesson_registration.platforms.kmong import KmongAdapter, profile
from lesson_registration.platforms.kmong.operations import list_operations


class ProfileMirror(unittest.TestCase):
    def test_binding_v1_matches_r03_and_common_reference_for_every_step(self):
        from lesson_registration.app.gateway import scope_binding_digest
        from contracts.detail_candidate import binding_digest
        accepted = s.base_accepted()
        operations = KmongAdapter(binding_version='binding.v1').operations(accepted)
        for operation, step in zip(operations, self.pin['steps']):
            definition = {'logical_operation_id': step['step_id'], 'step_id': step['step_id'],
                          'action_key': step['step_id'], 'effect_class': step['effect_class'],
                          'bindings': step['bindings']}
            self.assertEqual(operation['binding_digest'], scope_binding_digest(accepted['scope'], step))
            self.assertEqual(operation['binding_digest'], binding_digest(accepted['scope'], definition))

    def test_binding_v1_empty_binding_detects_approved_value_change(self):
        accepted = s.base_accepted()
        changed = copy.deepcopy(accepted)
        changed['scope']['values']['title'] = '변경된 합성 제목'
        adapter = KmongAdapter(binding_version='binding.v1')
        before = {op['step_id']: op['binding_digest'] for op in adapter.operations(accepted)}
        after = {op['step_id']: op['binding_digest'] for op in adapter.operations(changed)}
        self.assertNotEqual(before['K6'], after['K6'])

    @classmethod
    def setUpClass(cls):
        cls.pin = s.kmong_profile()
        cls.schema = s.data_schema()

    def test_steps_and_bindings_match_pin(self):
        pinned = [(x["step_id"], x["effect_class"], tuple(x["bindings"])) for x in self.pin["steps"]]
        mine = [(st, eff, tuple(b)) for st, _, eff, b in profile.STEPS]
        self.assertEqual(pinned, mine)

    def test_fields_goal_and_identity_match_pin(self):
        p = self.pin
        self.assertEqual((p["platform"], p["object_kind"], p["version"], p["environment"]),
                         (profile.PLATFORM, profile.OBJECT_KIND, profile.VERSION, profile.ENVIRONMENT))
        self.assertEqual(tuple(f["key"] for f in p["fields"]), profile.VALUE_KEYS)
        self.assertEqual(sorted(p["value_schema"]["required"]), sorted(profile.REQUIRED_KEYS))
        self.assertEqual((p["goal"]["kind"], p["goal"]["observed_state"]), (profile.GOAL_KIND, profile.GOAL_STATE))
        self.assertEqual(p["goal"]["methods"], ["independent_readback"])
        self.assertTrue(p["goal"]["requires_asset_digests"])

    def test_mock_site_options_match_fixture_rules(self):
        r, m = self.pin["fixture_rules"], s.mock_kmong
        self.assertEqual([tuple(c) for c in r["category_paths"]], list(m.CATEGORY_PATHS))
        self.assertEqual(tuple(r["tiers"]), m.TIERS)
        self.assertEqual(tuple(r["work_days"]), m.WORK_DAYS)
        self.assertEqual(tuple(r["revision_counts"]), m.REVISIONS)
        self.assertEqual(tuple(r["minutes"]), m.MINUTES)
        self.assertEqual(tuple(r["sessions"]), m.SESSIONS)
        self.assertEqual(tuple(r["periods"]), m.PERIODS)
        self.assertEqual([tuple(x) for x in r["region_pairs"]], list(m.REGION_PAIRS))
        self.assertEqual(tuple(r["exact_image_size"]), m.IMAGE_SIZE)
        self.assertEqual(tuple(r["exact_image_size"]), profile.IMAGE_SIZE)


class ValueValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pin = s.kmong_profile()
        defs = dict(s.dev.pinned("data-schema-v4.1.json")["$defs"])
        defs.update(pin["value_defs"])
        cls.value_schema = s.SchemaChecker({"$defs": {**defs, "KmongValues": pin["value_schema"]}})

    def schema_ok(self, values):
        return not self.value_schema.check(values, "KmongValues")

    def adapter_ok(self, values, assets):
        return not profile.validate_values(values, assets)

    def test_base_fixture_valid_both_ways(self):
        sc = s.base_accepted()["scope"]
        self.assertTrue(self.schema_ok(sc["values"]))
        self.assertEqual(profile.validate_values(sc["values"], sc["assets"]), [])

    def test_schema_level_mutations_agree_with_pinned_schema(self):
        sc = s.base_accepted()["scope"]
        mutations = {
            "title_short": lambda v: v.update(title="짧은제목"),
            "title_long": lambda v: v.update(title="가" * 31),
            "desc_short": lambda v: v.update(description="짧음"),
            "process_short": lambda v: v.update(process="x" * 49),
            "prep_ok_50": lambda v: v.update(preparation="x" * 50),
            "recruit_bad": lambda v: v.update(recruitment="vip"),
            "delivery_bad": lambda v: v.update(delivery="hybrid"),
            "no_title": lambda v: v.pop("title"),
            "extra_key": lambda v: v.update(price=1),
            "cat_empty": lambda v: v.update(category_path=[]),
            "two_packages": lambda v: v["packages"].pop(),
            "pkg_title_21": lambda v: v["packages"][0].update(title="가" * 21),
            "pkg_desc_61": lambda v: v["packages"][1].update(description="가" * 61),
            "pkg_neg_amount": lambda v: v["packages"][2].update(amount_vat_included_krw=-1),
            "pkg_zero_days": lambda v: v["packages"][0].update(work_days=0),
            "pkg_bool_sessions": lambda v: v["packages"][0].update(sessions=True),
            "pkg_extra": lambda v: v["packages"][0].update(extra="x"),
            "pkg_bad_tier": lambda v: v["packages"][0].update(tier="GOLD"),
            "images_none": lambda v: v.update(main_images=[]),
            "images_five": lambda v: v.update(main_images=v["main_images"] * 5),
        }
        for name, mut in mutations.items():
            with self.subTest(name):
                v = copy.deepcopy(sc["values"])
                mut(v)
                if name == "images_five":
                    self.assertFalse(self.schema_ok(v))
                    self.assertFalse(self.adapter_ok(v, sc["assets"]))
                    continue
                self.assertEqual(self.schema_ok(v), self.adapter_ok(v, sc["assets"]), name)

    def test_conditional_region(self):
        sc = s.base_accepted()["scope"]
        v = copy.deepcopy(sc["values"])
        v.pop("region")
        self.assertIn("region", [i["field"] for i in profile.validate_values(v, sc["assets"])])  # offline needs region
        v["delivery"] = "online"
        self.assertEqual(profile.validate_values(v, sc["assets"]), [])
        v["region"] = sc["values"]["region"]
        self.assertIn("region", [i["field"] for i in profile.validate_values(v, sc["assets"])])  # online forbids region
        v = copy.deepcopy(sc["values"])
        v["region"]["public_scope_confirmed"] = False
        self.assertTrue(profile.validate_values(v, sc["assets"]))

    def test_image_rules_beyond_schema(self):
        sc = s.base_accepted()["scope"]
        for name, change in {"size": {"width": 651}, "rights": {"rights_confirmed": False}, "mime": {"mime": "image/gif"}}.items():
            with self.subTest(name):
                v = copy.deepcopy(sc["values"])
                v["main_images"][0].update(change)
                self.assertTrue(profile.validate_values(v, sc["assets"]))
        v = copy.deepcopy(sc["values"])
        v["main_images"][0]["asset_id"] = "not-in-scope"
        self.assertTrue(profile.validate_values(v, sc["assets"]))
        self.assertEqual(profile.validate_values(sc["values"], sc["assets"]), [])
        issues = profile.validate_values({"title": 1, "x": 2}, [])
        self.assertTrue(issues)
        checker = s.data_schema()
        self.assertEqual([checker.check(i, "Issue") for i in issues], [[]] * len(issues))


class OperationRegistry(unittest.TestCase):
    def test_operations_are_contract_operations(self):
        acc = s.base_accepted()
        ops = KmongAdapter().operations(acc)
        checker = s.data_schema()
        self.assertEqual([o["step_id"] for o in ops], list(profile.STEP_IDS))
        for o in ops:
            self.assertEqual(checker.check(o, "Operation"), [])
        self.assertEqual(len({o["operation_id"] for o in ops}), 7)

    def test_identity_stable_digest_bound_to_values(self):
        a = s.base_accepted()
        b = copy.deepcopy(a)
        b["request_key"] = "another-request"
        b["scope"]["revision"] = 4
        b["scope"]["values"]["title"] = "합성 음악 레슨 안내 제목 수정"
        oa, ob = list_operations(a), list_operations(b)
        self.assertEqual([o["operation_id"] for o in oa], [o["operation_id"] for o in ob])
        self.assertNotEqual(oa[1]["binding_digest"], ob[1]["binding_digest"])   # K2 bound to title
        self.assertEqual(oa[0]["binding_digest"], ob[0]["binding_digest"])      # K1 binds no values
        c = copy.deepcopy(a)
        c["scope"]["target"]["slot_ref"] = "mock-slot-other"
        self.assertNotEqual(oa[5]["binding_digest"], list_operations(c)[5]["binding_digest"])  # target bound
        d = copy.deepcopy(a)
        d["scope"]["profile_ref"]["digest"] = "b" * 64
        self.assertNotEqual(oa[5]["binding_digest"], list_operations(d)[5]["binding_digest"])  # profile digest bound

    def test_matches_r03_store_gateway_registry(self):
        """STORE admits only operations whose digest it recomputes itself (app/gateway.py)."""
        from lesson_registration.app.gateway import binding_digest as store_binding_digest
        acc = s.base_accepted()
        scope, pin = acc["scope"], s.kmong_profile()
        expected = [{"operation_id": f"{scope['registration_id']}:{st['step_id']}", "step_id": st["step_id"],
                     "action_key": st["step_id"], "effect_class": st["effect_class"],
                     "binding_digest": store_binding_digest(scope, st)} for st in pin["steps"]]
        self.assertEqual(KmongAdapter().operations(acc), expected)

    def test_scope_pin_mismatch_refused(self):
        a = s.base_accepted()
        a["scope"]["profile_ref"]["version"] = "mock.v3"
        with self.assertRaises(s.KmongError) as e:
            KmongAdapter().operations(a)
        self.assertEqual(e.exception.code, "PROFILE_CHANGED")


if __name__ == "__main__":
    unittest.main()
