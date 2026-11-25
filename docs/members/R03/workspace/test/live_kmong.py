"""Experimental, operator supervised Kmong form runner.

This module never reuses the mock approval endpoint or its fixed prices.
Live execution is disabled unless explicitly enabled by the operator.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

LEVELS = ("STANDARD", "DELUXE", "PREMIUM")
REQUIRED_TEXT = ("service_title", "service_description", "process", "requirements")
PACKAGE_TEXT = ("title", "description")
PACKAGE_NUMBERS = ("price_krw_vat_included", "work_days", "revision_count", "minutes_per_session", "sessions")
PACKAGE_FLAGS = ("materials_included", "classroom_included")


def digest_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(data, image_path):
    """Return errors without inventing any real sale terms or option values."""
    errors = []
    for key in REQUIRED_TEXT:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(key)
    if len(data.get("service_title", "")) < 10 or len(data.get("service_title", "")) > 30:
        errors.append("service_title_length")
    if len(data.get("service_description", "")) < 100:
        errors.append("service_description_length")
    for key in ("process", "requirements"):
        if len(data.get(key, "")) < 50:
            errors.append(key + "_length")
    if data.get("category") != ["취미 레슨", "보컬·랩 레슨", "랩 레슨"]:
        errors.append("category")
    if data.get("delivery_mode") not in ("온라인", "오프라인"):
        errors.append("delivery_mode")
    for key in ("region_option", "recruitment_type", "expected_account"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(key)
        elif "교체" in data[key] or "실제 화면" in data[key]:
            errors.append(key + "_placeholder")
    if data.get("content_approved") is not True or data.get("image_rights_confirmed") is not True:
        errors.append("content_or_image_approval")
    packages = data.get("packages")
    if not isinstance(packages, dict) or set(packages) != set(LEVELS):
        errors.append("packages")
    else:
        for level, package in packages.items():
            if not isinstance(package, dict):
                errors.append(level)
                continue
            for key in PACKAGE_TEXT:
                value = package.get(key)
                if not isinstance(value, str) or not value.strip():
                    errors.append(level + "." + key)
                elif "실제" in value and ("과정명" in value or "제공 조건" in value):
                    errors.append(level + "." + key + "_placeholder")
            if len(str(package.get("title", ""))) > 20 or len(str(package.get("description", ""))) > 60:
                errors.append(level + ".text_length")
            for key in PACKAGE_NUMBERS:
                value = package.get(key)
                minimum = 0 if key == "revision_count" else 1
                if type(value) is not int or value < minimum:
                    errors.append(level + "." + key)
            for key in PACKAGE_FLAGS:
                if type(package.get(key)) is not bool:
                    errors.append(level + "." + key)
    if not image_path.is_file():
        errors.append("cover_image")
    else:
        try:
            with Image.open(image_path) as img:
                if img.format not in ("PNG", "JPEG") or img.width < 652 or img.height < 488:
                    errors.append("cover_image_format_or_size")
                img.verify()
        except Exception:
            errors.append("cover_image_invalid")
    return errors


def safe_kmong_page(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == "kmong.com" and parsed.path.startswith("/my-gigs/edit/")


def fingerprint(data, image_path):
    payload = {"listing": data, "image_sha256": digest_file(image_path)}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


async def verified_submit(adapter, data, image_path, approval, journal):
    """One attempt only. An uncertain result stays unknown and cannot auto retry."""
    if journal.exists():
        raise RuntimeError("이 공고에 대한 제출 시도 기록이 있습니다. 크몽에서 상태를 직접 확인하세요.")
    token = fingerprint(data, image_path)
    if approval != "제출 " + token[:12]:
        raise ValueError("최종 제출 승인 문구가 현재 내용 및 이미지와 일치하지 않습니다.")
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("x", encoding="utf-8") as out:
        json.dump({"status": "submitting", "fingerprint": token}, out)
    try:
        await adapter.click_submit_once()
        result = await adapter.check_receipt()
        status = "review_pending" if result is True else "unknown"
    except Exception:
        status = "unknown"
    journal.write_text(json.dumps({"status": status, "fingerprint": token}), encoding="utf-8")
    return status


class SkyvernLiveAdapter:
    def __init__(self, page):
        self.page = page

    async def fill_and_review(self, data, image_path):
        page = self.page
        # Skyvern prompts target visible labels; each operation is followed by a
        # full manual review because the site's actual DOM is not a stable API.
        await page.fill(prompt="기본 정보의 제목 입력칸", value=data["service_title"])
        for key, label in (("service_description", "서비스 설명"), ("process", "서비스 제공 절차"), ("requirements", "의뢰인 준비사항")):
            await page.fill(prompt=label + " 리치 텍스트 입력 영역", value=data[key])
        await page.act(prompt=f"주요 특징의 모집 형태에서 정확히 '{data['recruitment_type']}' 옵션을 선택하세요. 없으면 멈추세요.")
        await page.act(prompt=f"지역에서 '{data['delivery_mode']}'을 선택하고 지역·온라인 목록에서 정확히 '{data['region_option']}'을 선택하세요. 없으면 멈추세요.")
        await page.act(prompt="가격 정보 탭을 열고 패키지로 설정이 켜져 있는지 확인하세요. 제출이나 저장은 하지 마세요.")
        for level in LEVELS:
            p = data["packages"][level]
            for key, label in (("title", "제목"), ("description", "설명"), ("price_krw_vat_included", "금액(VAT 포함)")):
                await page.fill(prompt=f"가격 정보의 {level} 패키지 {label} 입력칸", value=str(p[key]))
            for key, label in (("work_days", "작업 기간"), ("revision_count", "수정 횟수"), ("minutes_per_session", "1회당 레슨시간 (분)"), ("sessions", "레슨 횟수")):
                await page.act(prompt=f"{level} 패키지의 {label}에서 정확히 '{p[key]}' 옵션을 선택하세요. 없으면 멈추세요.")
            for key, label in (("materials_included", "준비물 제공 포함"), ("classroom_included", "강의실 제공 포함")):
                await page.act(prompt=f"{level} 패키지의 '{label}' 체크박스를 {'체크' if p[key] else '체크 해제'}하세요.")
        await page.act(prompt="상세 정보 탭으로 이동하세요. 저장 또는 제출은 하지 마세요.")
        upload = page.locator(prompt="메인 이미지 업로드용 파일 input 요소")
        await upload.set_input_files(str(image_path.resolve()))
        print("입력 및 이미지 첨부 동작을 마쳤습니다. 화면의 모든 항목, 계정, 카테고리, 이미지 썸네일과 오류 표시를 직접 대조하세요.")

    async def click_submit_once(self):
        await self.page.click(prompt="이 서비스의 최종 '제출하기' 버튼")

    async def check_receipt(self):
        # A browser click or Skyvern completion is never evidence of acceptance.
        answer = input("크몽 서비스 관리 화면에서 이 공고의 심사 접수를 직접 확인했나요? 확인했으면 '심사접수 확인' 입력: ")
        return answer == "심사접수 확인"


async def run(args):
    listing_path = Path(args.listing)
    if not listing_path.is_file():
        raise ValueError(
            f"입력 파일이 없습니다: {listing_path}. "
            "먼저 Copy-Item .\\live_listing.example.json .\\data\\live_listing.json 으로 예시를 복사하고 실제 값으로 수정하세요."
        )
    data = json.loads(listing_path.read_text(encoding="utf-8"))
    image_path = Path(args.image).resolve()
    errors = validate(data, image_path)
    if errors:
        raise ValueError("입력 검증 실패: " + ", ".join(errors))
    token = fingerprint(data, image_path)
    print("검증 통과. 내용/이미지 지문:", token[:12])
    if args.command == "validate":
        return
    if os.environ.get("KMONG_LIVE_ENABLED") != "1":
        raise RuntimeError("실제 사이트 실행이 꺼져 있습니다. 팀 실험 범위와 플랫폼 허용 경로를 확인한 뒤 KMONG_LIVE_ENABLED=1로 설정하세요.")
    if args.command == "submit" and os.environ.get("KMONG_SUBMIT_ENABLED") != "1":
        raise RuntimeError("최종 제출 기능이 꺼져 있습니다.")
    journal = Path(args.journal).resolve()
    if args.command == "submit" and journal.exists():
        raise RuntimeError("기존 제출 시도가 있습니다. 먼저 크몽에서 실제 상태를 확인하세요.")
    from skyvern import Skyvern
    client = Skyvern.local()
    try:
        browser = await client.launch_local_browser(headless=False)
        page = await browser.new_page()
        await page.goto("https://kmong.com/")
        input("표시된 브라우저에서 직접 로그인하고 본인 공고의 랩 레슨 편집 화면을 연 뒤 Enter: ")
        if not safe_kmong_page(page.url):
            raise RuntimeError("예상한 크몽 공고 편집 화면이 아닙니다.")
        account = input("현재 화면의 계정 표시명을 입력하세요: ").strip()
        if account != data["expected_account"]:
            raise RuntimeError("승인된 계정과 현재 계정이 다릅니다.")
        category = input("현재 화면에 '취미 레슨 > 보컬·랩 레슨 > 랩 레슨'이 표시되면 동일 문구를 입력하세요: ").strip()
        if category != "취미 레슨 > 보컬·랩 레슨 > 랩 레슨":
            raise RuntimeError("승인된 카테고리와 다릅니다.")
        adapter = SkyvernLiveAdapter(page)
        await adapter.fill_and_review(data, image_path)
        if args.command == "fill":
            input("검토 후 Enter를 누르면 브라우저가 닫힙니다. 저장 또는 제출은 수행하지 않았습니다: ")
            return
        review = input("모든 필드·선택값·가격·이미지 썸네일을 화면에서 대조했고 오류가 없으면 '화면 확인' 입력: ")
        if review != "화면 확인":
            raise RuntimeError("화면 대조가 완료되지 않아 제출을 중단했습니다.")
        confirmation = input("이 공고를 지금 심사 접수하려면 '제출 " + token[:12] + "' 입력: ")
        print("결과:", await verified_submit(adapter, data, image_path, confirmation, journal))
        input("상태 확인 후 Enter를 누르면 브라우저가 닫힙니다: ")
    finally:
        await client.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "fill", "submit"))
    parser.add_argument("--listing", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--journal", default="data/live_submit_attempt.json")
    try:
        asyncio.run(run(parser.parse_args()))
    except (ValueError, RuntimeError) as exc:
        parser.exit(2, f"오류: {exc}\n")
