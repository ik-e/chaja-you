"""Shared deterministic byte vectors; not product proof."""
import json
import pathlib
import unittest
from contracts.canonical import canonical_bytes, json_digest, asset_digest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class CanonicalContract(unittest.TestCase):
    def test_golden_vectors(self):
        data = json.loads((ROOT / "fixtures/shared/canonical-vectors.json").read_text(encoding="utf-8"))
        for row in data["vectors"]:
            with self.subTest(row=row["sha256"]):
                self.assertEqual(canonical_bytes(row["value"]), row["canonical_utf8"].encode("utf-8"))
                self.assertEqual(json_digest(row["value"]), row["sha256"])
                self.assertEqual(json_digest(dict(reversed(list(row["value"].items())))), row["sha256"])

    def test_arrays_unicode_distinct(self):
        self.assertNotEqual(json_digest([1, 2]), json_digest([2, 1]))
        self.assertNotEqual(json_digest("e\u0301"), json_digest("\u00e9"))

    def test_fail_closed(self):
        for value in (1.0, float("nan"), 1 << 53, -(1 << 53), {1: "x"},
                      (1,), "\ud800", {"nested": [float("inf")]}):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                canonical_bytes(value)

    def test_asset_raw_bytes(self):
        self.assertEqual(asset_digest(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertNotEqual(asset_digest(b"abc"), json_digest("abc"))
        with self.assertRaises(ValueError):
            asset_digest("abc")
