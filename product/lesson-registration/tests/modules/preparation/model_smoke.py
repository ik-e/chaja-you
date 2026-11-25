"""Optional paid-model smoke test with a fixed synthetic lesson, run explicitly."""
import os
import sys

from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.preparation.openai_extractor import OpenAIResponsesExtractor
from lesson_registration.preparation.provider import PreparationProvider


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("OPENAI_MODEL", "")
    if not api_key or not model:
        print("미실행: OPENAI_API_KEY와 OPENAI_MODEL 환경 설정이 필요합니다.")
        return 2
    provider = PreparationProvider(contract.catalog(), OpenAIResponsesExtractor(
        api_key, model, timeout_seconds=30, synthetic_input_confirmed=True))
    request = {"source": {"source_id": "synthetic-smoke", "raw_text": "제목은 합성 기타 레슨입니다.",
                          "asset_refs": [], "created_at": "2026-11-25T00:00:00Z"},
               "profile": Knowledge().resolve("kmong")["profile"], "answers": []}
    try:
        result = provider.prepare(request)
    except PortFailure as exc:
        print("모델 시험 실패:", exc.error["code"])
        return 1
    title = [fact for fact in result["facts"]
             if fact["path"] == "/title" and fact["value"] == "합성 기타 레슨"]
    if not title or result["ready"] or result["values"].get("title") != "합성 기타 레슨":
        print("모델 시험 미충족: 합성 제목과 원문 근거를 확인하지 못했습니다.")
        return 1
    print("모델 시험 통과: 합성 제목·원문 근거를 준비하고 누락 항목으로 완료를 차단했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
