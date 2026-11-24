# Step 1·2 V3 — 공식 가이드/계약 결함 보완 파일럿

> **기존 V1·V2 및 Step1/WBS/TASK/Phase 정본/대시보드 비간섭** · 2026-11-18 기준 · **공식 제출/실제 제품 선정 아님**

## 검토할 문서

| 항목 | 링크 | 기준 |
| --- | --- | --- |
| 기획서 | [Step1 기획서](STEP1-%EA%B8%B0%ED%9A%8D%EC%84%9C.md) | 강사 DOCX 샘플 3개 대항목 + 사용자 문제/가치 가설 |
| WBS | [Step1 WBS](STEP1-WBS.md) | DOCX 샘플 4개 대항목 + 현재 두 트랙/조건부 전체 마감 |
| API | [Step2 API](STEP2-API-%EC%84%A4%EA%B3%84.md) | Step2 공식 작성 가이드의 계약·권한·Tool·실행 정책 |
| DB | [Step2 DB](STEP2-DB-%EC%8A%A4%ED%82%A4%EB%A7%88.md) | Step2 작성 가이드 ERD/컬럼·권한·세션·pgvector·인덱스 |

**목차 흐름 평가:** [V3 REVIEW](REVIEW.md) · [공통 계약](contract.json) · [생성 입력](model.json)

- 실제 개발/제출 정본은 변경하지 않습니다. 강사님/매니저님께 공유한 **방향**을 현재 전제로 삼되, 정식 승인이나 변경 마감일을 추정하지 않습니다.
- `model.json`은 파일럿 4개 문서의 입력 정본, `contract.json`은 Step2 필드·권한·API/DB 관계의 의미 정본입니다. API/DB의 **본문 수치·데이터·예시는 실제 실행이 아닙니다**.
- [기존 V2](../2026-11-18-v2/README.md) 및 [원본 가이드 감사](../../../guidelines/instructor-snapshots/reviews/STEP1-STEP2-V2-GUIDE-AUDIT-20261118.md)는 변경 없이 비교 이력으로 유지됩니다.

## 재생성 및 확인

```bash
python tools/pilot_step1_step2_v3.py --check
python tools/pilot_step1_step2_v3.py
```

생성기는 지정 V3 폴더 **4개 Markdown만** 생성/검사합니다. 별도 CI에서 계약 참조·유효 JSON·Mermaid fence를 검사하지만 **제품 E2E/데이터베이스 SQL이나 렌더된 DOCX**를 검증한 것은 아닙니다.
