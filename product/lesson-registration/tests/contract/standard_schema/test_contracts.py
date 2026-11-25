"""Standard schema and selected provider boundary checks, not product tests."""
import copy
import unittest
import dev
from contracts.interfaces import Providers, PortFailure
from contracts.validation import ContractViolation
from lesson_registration.composition.wiring import bind_ports
from stubs.replay_ports import ReplayProviders


class StandardContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = dev.pinned("data-schema-v4.1.json")
        cls.profiles = dev.pinned("platform-profiles-v2.json")
        cls.common = dev.pinned("common-integration-v1.json")
        cls.fixtures = dev.fixtures()

    def make(self, platform, *, providers=None):
        f = self.fixtures[platform]
        fake = ReplayProviders(f)
        bound = bind_ports(self.schema, self.profiles, self.common,
                           providers=providers or fake.bind())
        return f, fake, bound

    def test_all_named_replay_shapes(self):
        count = 0
        for platform, f in self.fixtures.items():
            _, _, bound = self.make(platform)
            for key, row in f["cases"].items():
                with self.subTest(platform=platform, case=key):
                    if row["input_type"]:
                        bound.catalog.named(row["input_type"], row["input"])
                        count += 1
                    if row["output_type"]:
                        bound.catalog.named(row["output_type"], row["output"])
                        count += 1
        print("named fixture payloads checked:", count)

    def test_http_named_shapes(self):
        routes = {row["id"]: row for row in self.common["routes"]}
        count = 0
        for platform, f in self.fixtures.items():
            _, _, bound = self.make(platform)
            for row in f["http"]:
                route = routes[row["id"]]
                with self.subTest(platform=platform, route=row["id"]):
                    if route["input"] is not None:
                        # GET query is normalized before validation; fixture None is empty query.
                        bound.catalog.named(route["input"], {} if row["method"] == "GET" and row["input"] is None else row["input"])
                        count += 1
                    bound.catalog.named(route["output"], row["output"])
                    count += 1
                    self.assertIn(row["status"], route["success"])
        print("HTTP fixture payloads checked:", count)

    def test_port_wiring_and_missing_unknown(self):
        for platform in self.fixtures:
            f, fake, bound = self.make(platform)
            for key in ("I1", "I2", "I3", "I4", "I5", "I2-missing", "I5-unknown"):
                row = f["cases"][key]
                self.assertEqual(bound.call(key.split("-")[0], row["input"]), row["output"])
            self.assertEqual(len(fake.calls), 7)
            self.assertFalse(bound.call("I2", f["cases"]["I2-missing"]["input"])["ready"])
            self.assertEqual(bound.call("I5", f["cases"]["I5-unknown"]["input"])["goal_verdict"], "unknown")

    def test_platform_specific_values(self):
        for p in self.profiles["profiles"]:
            _, _, bound = self.make(p["platform"])
            values = self.fixtures[p["platform"]]["cases"]["I2"]["output"]["values"]
            bound.catalog.profile_values(p["id"], values)
            required = p["value_schema"]["required"][0]
            bad = copy.deepcopy(values)
            bad.pop(required)
            with self.assertRaises(ContractViolation):
                bound.catalog.profile_values(p["id"], bad)

    def test_input_guards_before_provider(self):
        f, fake, bound = self.make("kmong")
        bad = copy.deepcopy(f["cases"]["I4"]["input"])
        bad["accepted"]["scope"]["profile_ref"]["environment"] = "live"
        with self.assertRaises(ContractViolation):
            bound.call("I4", bad)
        self.assertEqual(fake.calls, [])
        bad = copy.deepcopy(f["cases"]["I2"]["input"])
        bad["owner_ref"] = "unexpected"
        with self.assertRaises(ContractViolation):
            bound.call("I2", bad)
        with self.assertRaises(ContractViolation):
            bound.call("I0", {})
        with self.assertRaises(ContractViolation):
            bound.call("I1", "")
        self.assertEqual(fake.calls, [])

    def test_provider_error_and_invalid_output(self):
        f, fake, bound = self.make("kmong")
        with self.assertRaises(PortFailure) as cm:
            bound.call("I1", "wrong-selector")
        self.assertEqual(cm.exception.error["code"], "INVALID_REQUEST")
        class BadPrep:
            def prepare(self, request):
                return {"ready": True}
        _, _, bound = self.make("kmong", providers=Providers(fake, BadPrep(), fake, fake))
        with self.assertRaises(ContractViolation):
            bound.call("I2", f["cases"]["I2"]["input"])

    def test_false_ready_rejected(self):
        f, fake, _ = self.make("kmong")
        class BadPrep:
            def prepare(self, request):
                result = copy.deepcopy(f["cases"]["I2-missing"]["output"])
                result["ready"] = True
                return result
        _, _, bound = self.make("kmong", providers=Providers(fake, BadPrep(), fake, fake))
        with self.assertRaises(ContractViolation):
            bound.call("I2", f["cases"]["I2-missing"]["input"])

    def test_mismatched_auth_generation_rejected(self):
        f, fake, _ = self.make("kmong")
        class BadAuth:
            def authenticate(self, request):
                result = copy.deepcopy(f["cases"]["I3"]["output"])
                result["connection"]["verified_generation"] += 1
                return result
            def execute(self, request):
                raise AssertionError("must not execute")
        _, _, bound = self.make("kmong", providers=Providers(fake, fake, BadAuth(), fake))
        with self.assertRaises(ContractViolation):
            bound.call("I3", f["cases"]["I3"]["input"])

    def test_unfounded_success_rejected(self):
        f, fake, _ = self.make("kmong")
        class BadResult:
            def evaluate(self, request):
                return copy.deepcopy(f["cases"]["I5"]["output"])
        _, _, bound = self.make("kmong", providers=Providers(fake, fake, fake, BadResult()))
        request = copy.deepcopy(f["cases"]["I5-unknown"]["input"])
        request["report"].pop("goal_observation", None)
        request["evidence"] = []
        with self.assertRaises(ContractViolation):
            bound.call("I5", request)

    def test_datetime_and_digest_negative(self):
        _, _, bound = self.make("kmong")
        for value in ("bad-time", "2026-11-25"):
            with self.assertRaises(ContractViolation):
                bound.catalog.named("Timestamp", value)
        with self.assertRaises(ContractViolation):
            bound.catalog.named("Digest", "not-a-hash")
