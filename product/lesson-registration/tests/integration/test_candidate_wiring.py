"""Composition can receive provider replacements; this test is not product execution."""
import unittest
import dev
from stubs.replay_ports import ReplayProviders


class CompositionSkeleton(unittest.TestCase):
    def test_separate_instances_and_no_implicit_provider(self):
        fixture = dev.fixtures()["kmong"]
        left, right = ReplayProviders(fixture), ReplayProviders(fixture)
        self.assertIsNot(left.bind().registry, right.bind().registry)
        self.assertEqual(left.resolve("kmong"), fixture["cases"]["I1"]["output"])
        self.assertEqual(left.calls, ["I1"])
        self.assertEqual(right.calls, [])
