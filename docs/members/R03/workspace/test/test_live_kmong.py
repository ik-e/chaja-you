import asyncio
import json
from pathlib import Path

from PIL import Image

from live_kmong import fingerprint, safe_kmong_page, validate, verified_submit


def fixture(tmp_path):
    data = json.loads(Path(__file__).with_name("live_listing.example.json").read_text(encoding="utf-8"))
    data.update(expected_account="강사", content_approved=True, image_rights_confirmed=True,
                service_title="실제 랩 레슨 서비스 제목입니다", service_description="실제 수업 내용입니다. " * 12,
                process="실제 수업 절차입니다. " * 8, requirements="실제 수업 준비사항입니다. " * 8,
                recruitment_type="개인 수업")
    for p in data["packages"].values():
        p.update(title="랩 레슨 과정", description="수업 4회 제공", price_krw_vat_included=100000, work_days=4, minutes_per_session=90, sessions=4)
    image = tmp_path / "cover.png"
    Image.new("RGB", (652, 488), "blue").save(image)
    return data, image


def test_validate_requires_complete_real_values(tmp_path):
    data, image = fixture(tmp_path)
    assert validate(data, image) == []
    data["packages"]["STANDARD"]["price_krw_vat_included"] = 0
    data["image_rights_confirmed"] = False
    assert "STANDARD.price_krw_vat_included" in validate(data, image)
    assert "content_or_image_approval" in validate(data, image)


def test_host_and_edit_path_only():
    assert safe_kmong_page("https://kmong.com/my-gigs/edit/123")
    assert not safe_kmong_page("https://kmong.com.evil.test/my-gigs/edit/123")
    assert not safe_kmong_page("http://kmong.com/my-gigs/edit/123")
    assert not safe_kmong_page("https://kmong.com/")


class Adapter:
    def __init__(self, receipt):
        self.calls = 0
        self.receipt = receipt

    async def click_submit_once(self):
        self.calls += 1

    async def check_receipt(self):
        if isinstance(self.receipt, Exception):
            raise self.receipt
        return self.receipt


def test_submit_requires_current_approval_and_no_retry(tmp_path):
    data, image = fixture(tmp_path)
    adapter = Adapter(True)
    journal = tmp_path / "attempt.json"
    token = fingerprint(data, image)
    try:
        asyncio.run(verified_submit(adapter, data, image, "제출 wrong", journal))
    except ValueError:
        pass
    else:
        assert False
    assert adapter.calls == 0
    status = asyncio.run(verified_submit(adapter, data, image, "제출 " + token[:12], journal))
    assert status == "review_pending" and adapter.calls == 1
    try:
        asyncio.run(verified_submit(adapter, data, image, "제출 " + token[:12], journal))
    except RuntimeError:
        pass
    else:
        assert False
    assert adapter.calls == 1


def test_uncertain_receipt_stays_unknown(tmp_path):
    data, image = fixture(tmp_path)
    adapter = Adapter(TimeoutError())
    journal = tmp_path / "attempt.json"
    status = asyncio.run(verified_submit(adapter, data, image, "제출 " + fingerprint(data, image)[:12], journal))
    assert status == "unknown" and adapter.calls == 1
    assert json.loads(journal.read_text())["status"] == "unknown"
