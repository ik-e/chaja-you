"""S1: STORE schema, immutable sources (H1~H3), owner isolation, cursor paging, persistence.

Covers part of T5-11 and REQ-01/REQ-10 for the source boundary.
"""

import sqlite3
import unittest

from lesson_registration.app import contract
from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.ids import bytes_digest
from lesson_registration.app.store import Store

from support import FixedClock, TickClock, mock_image, temp_db

A, B = "owner-a", "owner-b"


class Base(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.co = Coordinator(Store(self.path), clock=TickClock())

    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaises(AppError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)
        return ctx.exception

    def count(self, table):
        with sqlite3.connect(self.path) as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def with_image(self, owner=A, text="합성 원본", rights=True, part="img1"):
        return self.co.create_source(
            owner,
            {"raw_text": text, "new_assets": [{"part_name": part, "rights_confirmed": rights}]},
            {part: mock_image()},
        )


class CreateSource(Base):
    def test_text_only_source(self):
        v = self.co.create_source(A, {"raw_text": "합성 레슨 소개"})
        contract.validate("SourceView", v)
        self.assertEqual(v["raw_text"], "합성 레슨 소개")
        self.assertEqual(v["asset_refs"], [])
        self.assertNotIn("previous_source_id", v)

    def test_png_asset_metadata_from_bytes(self):
        v = self.with_image()
        ref = v["asset_refs"][0]
        data = mock_image()
        self.assertEqual(ref["mime"], "image/png")
        self.assertEqual((ref["width"], ref["height"]), (652, 488))
        self.assertEqual(ref["bytes"], len(data))
        self.assertEqual(ref["digest"], bytes_digest(data))
        self.assertTrue(ref["rights_confirmed"])

    def test_same_content_twice_creates_new_snapshot(self):
        a = self.co.create_source(A, {"raw_text": "같은 내용"})
        b = self.co.create_source(A, {"raw_text": "같은 내용"})
        self.assertNotEqual(a["source_id"], b["source_id"])
        self.assertEqual(self.count("sources"), 2)

    def test_new_version_keeps_previous_unchanged(self):
        v1 = self.with_image(text="버전1")
        v2 = self.co.create_source(
            A,
            {
                "raw_text": "버전2",
                "previous_source_id": v1["source_id"],
                "reuse_asset_ids": [v1["asset_refs"][0]["asset_id"]],
            },
        )
        self.assertEqual(v2["previous_source_id"], v1["source_id"])
        self.assertEqual(v2["asset_refs"], v1["asset_refs"])
        self.assertEqual(self.co.get_source(A, v1["source_id"]), v1)

    def test_empty_text_without_assets_rejected(self):
        self.assertCode("VALIDATION_FAILED", self.co.create_source, A, {"raw_text": "   "})
        self.assertEqual(self.count("sources"), 0)

    def test_image_only_source_allowed(self):
        v = self.with_image(text="")
        self.assertEqual(len(v["asset_refs"]), 1)


class RejectSource(Base):
    def test_unknown_key(self):
        self.assertCode("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x", "owner_ref": B})

    def test_rights_not_confirmed_stores_nothing(self):
        self.assertCode("VALIDATION_FAILED", self.with_image, rights=False)
        self.assertEqual(self.count("assets"), 0)
        self.assertEqual(self.count("sources"), 0)

    def test_missing_part(self):
        self.assertCode(
            "INVALID_REQUEST",
            self.co.create_source,
            A,
            {"raw_text": "x", "new_assets": [{"part_name": "img1", "rights_confirmed": True}]},
            {},
        )

    def test_extra_part(self):
        self.assertCode("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x"}, {"img1": mock_image()})

    def test_duplicate_part_name(self):
        spec = {"part_name": "img1", "rights_confirmed": True}
        self.assertCode(
            "INVALID_REQUEST",
            self.co.create_source,
            A,
            {"raw_text": "x", "new_assets": [spec, spec]},
            {"img1": mock_image()},
        )

    def test_non_image_bytes(self):
        self.assertCode(
            "VALIDATION_FAILED",
            self.co.create_source,
            A,
            {"raw_text": "x", "new_assets": [{"part_name": "f", "rights_confirmed": True}]},
            {"f": b"not an image at all"},
        )
        self.assertEqual(self.count("assets"), 0)


class OwnerIsolation(Base):
    def test_other_owner_get_is_not_found(self):
        v = self.co.create_source(A, {"raw_text": "A의 원본"})
        self.assertCode("NOT_FOUND", self.co.get_source, B, v["source_id"])

    def test_other_owner_previous_source_rejected(self):
        v = self.co.create_source(A, {"raw_text": "A의 원본"})
        self.assertCode(
            "NOT_FOUND", self.co.create_source, B, {"raw_text": "x", "previous_source_id": v["source_id"]}
        )

    def test_other_owner_asset_reuse_rejected(self):
        v = self.with_image(owner=A)
        self.assertCode(
            "NOT_FOUND",
            self.co.create_source,
            B,
            {"raw_text": "x", "reuse_asset_ids": [v["asset_refs"][0]["asset_id"]]},
        )
        self.assertEqual(self.count("sources"), 1)

    def test_list_only_own_sources(self):
        self.co.create_source(A, {"raw_text": "a"})
        self.co.create_source(B, {"raw_text": "b"})
        self.assertEqual([i["excerpt"] for i in self.co.list_sources(A)["items"]], ["a"])

    def test_unknown_id_not_found(self):
        self.assertCode("NOT_FOUND", self.co.get_source, A, "source-missing")


class ListPaging(Base):
    def test_order_limit_and_cursor(self):
        ids = [self.co.create_source(A, {"raw_text": f"원본 {i}"})["source_id"] for i in range(5)]
        page1 = self.co.list_sources(A, {"limit": 2})
        contract.validate("SourceList", page1)
        self.assertEqual([i["source_id"] for i in page1["items"]], ids[::-1][:2])
        page2 = self.co.list_sources(A, {"limit": 2, "cursor": page1["next_cursor"]})
        page3 = self.co.list_sources(A, {"limit": 2, "cursor": page2["next_cursor"]})
        seen = [i["source_id"] for p in (page1, page2, page3) for i in p["items"]]
        self.assertEqual(seen, ids[::-1])
        self.assertNotIn("next_cursor", page3)

    def test_default_limit_is_20(self):
        for i in range(21):
            self.co.create_source(A, {"raw_text": str(i)})
        out = self.co.list_sources(A)
        self.assertEqual(len(out["items"]), 20)
        self.assertIn("next_cursor", out)

    def test_same_timestamp_tiebreak_by_source_id_desc(self):
        co = Coordinator(Store(temp_db(self)), clock=FixedClock())
        ids = [co.create_source(A, {"raw_text": str(i)})["source_id"] for i in range(3)]
        listed = [i["source_id"] for i in co.list_sources(A)["items"]]
        self.assertEqual(listed, sorted(ids, reverse=True))

    def test_tampered_cursor_rejected(self):
        for i in range(3):
            self.co.create_source(A, {"raw_text": str(i)})
        cursor = self.co.list_sources(A, {"limit": 1})["next_cursor"]
        body, sig = cursor.split(".")
        self.assertCode("INVALID_REQUEST", self.co.list_sources, A, {"cursor": body + "x." + sig})
        self.assertCode("INVALID_REQUEST", self.co.list_sources, A, {"cursor": "garbage"})

    def test_cursor_bound_to_owner(self):
        for i in range(3):
            self.co.create_source(A, {"raw_text": str(i)})
            self.co.create_source(B, {"raw_text": str(i)})
        cursor = self.co.list_sources(A, {"limit": 1})["next_cursor"]
        self.assertCode("INVALID_REQUEST", self.co.list_sources, B, {"cursor": cursor})

    def test_limit_bounds(self):
        self.assertCode("INVALID_REQUEST", self.co.list_sources, A, {"limit": 0})
        self.assertCode("INVALID_REQUEST", self.co.list_sources, A, {"limit": 101})


class Persistence(Base):
    def test_reopen_store_keeps_sources_and_cursors(self):
        v = self.with_image()
        for i in range(2):
            self.co.create_source(A, {"raw_text": str(i)})
        cursor = self.co.list_sources(A, {"limit": 1})["next_cursor"]
        reopened = Coordinator(Store(self.path), clock=TickClock(100))
        self.assertEqual(reopened.get_source(A, v["source_id"]), v)
        self.assertEqual(len(reopened.list_sources(A, {"cursor": cursor})["items"]), 2)


if __name__ == "__main__":
    unittest.main()
