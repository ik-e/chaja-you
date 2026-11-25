"""S6: attachment validation (T6-01, REQ-01/REQ-03 rights, REQ-10 owner isolation).

Only authorized, structurally valid PNG/JPEG bytes are stored and linked; the stored
digest equals the byte hash; every rejection leaves no rows behind.
"""

import sqlite3
import unittest
import zlib

from lesson_registration.app.coordinator import MAX_ASSET_BYTES, Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.ids import bytes_digest, inspect_image
from lesson_registration.app.store import Store
from lesson_registration.app.store import repo

from support import TickClock, mock_image, temp_db

A, B = "owner-a", "owner-b"


def png(width=4, height=3, *, extra=b"") -> bytes:
    def chunk(t, body):
        return len(body).to_bytes(4, "big") + t + body + zlib.crc32(t + body).to_bytes(4, "big")
    ihdr = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * width for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"") + extra


def jpeg(width=5, height=7, *, eoi=True) -> bytes:
    app0 = b"\xff\xe0" + (16).to_bytes(2, "big") + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof0 = (b"\xff\xc0" + (17).to_bytes(2, "big") + b"\x08" + height.to_bytes(2, "big") + width.to_bytes(2, "big")
            + b"\x03" + b"\x01\x11\x00\x02\x11\x00\x03\x11\x00")
    return b"\xff\xd8" + app0 + sof0 + b"\x00" * 8 + (b"\xff\xd9" if eoi else b"")


class Inspect(unittest.TestCase):
    def test_fixture_png(self):
        self.assertEqual(inspect_image(mock_image()), {"mime": "image/png", "width": 652, "height": 488})

    def test_generated_png_and_jpeg(self):
        self.assertEqual(inspect_image(png(4, 3)), {"mime": "image/png", "width": 4, "height": 3})
        self.assertEqual(inspect_image(jpeg(5, 7)), {"mime": "image/jpeg", "width": 5, "height": 7})

    def test_rejects_corrupt_or_odd_bytes(self):
        good = png()
        cases = {
            "truncated png": good[:-5],
            "bad crc": good[:20] + bytes([good[20] ^ 1]) + good[21:],
            "trailing bytes after IEND": png(extra=b"<script>"),
            "zero width": png(0, 3),
            "huge dimension": png(50000, 1),
            "jpeg without EOI": jpeg(eoi=False),
            "jpeg zero height": jpeg(5, 0),
            "gif": b"GIF89a" + b"\x00" * 20,
            "svg": b"<svg xmlns='http://www.w3.org/2000/svg'/>",
            "empty": b"",
        }
        for name, data in cases.items():
            with self.subTest(name):
                self.assertIsNone(inspect_image(data))


class Upload(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.co = Coordinator(Store(self.path), clock=TickClock())

    def upload(self, data, owner=A, rights=True, part="p", extra_input=None):
        body = {"raw_text": "x", "new_assets": [{"part_name": part, "rights_confirmed": rights}]}
        body.update(extra_input or {})
        return self.co.create_source(owner, body, {part: data})

    def rows(self):
        with sqlite3.connect(self.path) as conn:
            return tuple(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                         for t in ("sources", "assets", "source_assets"))

    def assertRejected(self, code, fn, *args, **kwargs):
        before = self.rows()
        with self.assertRaises(AppError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)
        self.assertEqual(self.rows(), before)

    def test_png_and_jpeg_stored_with_byte_hash(self):
        for data, mime in ((mock_image(), "image/png"), (jpeg(), "image/jpeg")):
            with self.subTest(mime=mime):
                v = self.upload((data, mime))
                ref = v["asset_refs"][0]
                self.assertEqual((ref["mime"], ref["bytes"], ref["digest"]), (mime, len(data), bytes_digest(data)))
                with Store(self.path).connect() as conn:
                    stored = repo.get_asset_blob(conn, A, ref["asset_id"])
                self.assertEqual(bytes_digest(stored), ref["digest"])

    def test_declared_type_mismatch(self):
        self.assertRejected("VALIDATION_FAILED", self.upload, (mock_image(), "image/jpeg"))
        self.assertRejected("VALIDATION_FAILED", self.upload, (jpeg(), "image/png"))

    def test_declared_type_with_parameters_is_normalised(self):
        self.upload((mock_image(), "Image/PNG; charset=binary"))

    def test_no_rights(self):
        self.assertRejected("VALIDATION_FAILED", self.upload, mock_image(), rights=False)

    def test_size_limits(self):
        self.assertRejected("VALIDATION_FAILED", self.upload, b"")
        oversized = png(extra=b"")  # valid structure, then pad past the limit inside a valid chunk
        big = oversized[:-12] + (b"\x00" * (MAX_ASSET_BYTES + 1)) + oversized[-12:]
        self.assertRejected("VALIDATION_FAILED", self.upload, big)

    def test_corrupt_bytes(self):
        self.assertRejected("VALIDATION_FAILED", self.upload, png()[:-3])
        self.assertRejected("VALIDATION_FAILED", self.upload, b"<svg/>")

    def test_non_file_part(self):
        self.assertRejected("INVALID_REQUEST", self.upload, "not-bytes")

    def test_foreign_and_missing_asset_reference(self):
        foreign = self.upload(mock_image(), owner=B)["asset_refs"][0]["asset_id"]
        self.assertRejected("NOT_FOUND", self.co.create_source, A, {"raw_text": "x", "reuse_asset_ids": [foreign]})
        self.assertRejected("NOT_FOUND", self.co.create_source, A, {"raw_text": "x", "reuse_asset_ids": ["asset-x"]})

    def test_external_reference_fields_rejected(self):
        self.assertRejected("INVALID_REQUEST", self.co.create_source, A,
                            {"raw_text": "x", "image_url": "https://example.com/a.png"})
        self.assertRejected("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x", "new_assets": [
            {"part_name": "p", "rights_confirmed": True, "url": "https://example.com/a.png"}]}, {"p": mock_image()})

    def test_multipart_missing_extra_duplicate(self):
        spec = {"part_name": "p", "rights_confirmed": True}
        self.assertRejected("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x", "new_assets": [spec]}, {})
        self.assertRejected("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x", "new_assets": [spec]},
                            {"p": mock_image(), "q": mock_image()})
        self.assertRejected("INVALID_REQUEST", self.co.create_source, A, {"raw_text": "x", "new_assets": [spec, spec]},
                            {"p": mock_image()})

    def test_one_bad_part_rejects_whole_upload(self):
        body = {"raw_text": "x", "new_assets": [{"part_name": "ok", "rights_confirmed": True},
                                                 {"part_name": "bad", "rights_confirmed": True}]}
        self.assertRejected("VALIDATION_FAILED", self.co.create_source, A, body,
                            {"ok": mock_image(), "bad": b"junk"})

    def test_reuse_keeps_identity(self):
        first = self.upload(mock_image())
        ref = first["asset_refs"][0]
        second = self.co.create_source(A, {"raw_text": "y", "reuse_asset_ids": [ref["asset_id"]]})
        self.assertEqual(second["asset_refs"], [ref])
        self.assertEqual(self.rows()[1], 1)  # no new asset row


if __name__ == "__main__":
    unittest.main()
