# TASK-049 · 등록 정보 준비·AI 구조화 및 검증

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R02 · 패키지: r02-preparation

## 목적

PrepareInput→Preparation; AI 후보·근거·누락/충돌 검사; 12/4 인계 후보, 실제 모델/역량 확인

## 작업 범위

- `product/lesson-registration/src/lesson_registration/preparation/`
- `product/lesson-registration/fixtures/source/`
- `product/lesson-registration/tests/modules/preparation/`

공통 계약: CS-01, CS-02. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-049.json).

## 수용 기준

- r02-preparation-AC1: I2 구현: 실제 모델로 사실·근거·질문 생성, 양 플랫폼 프로필 검증
- r02-preparation-AC2: 가격/단위/VAT 누락·충돌 보존, 임의 값 생성 금지
- r02-preparation-AC3: 12/4까지 재현 명령과 합성 데이터·유지보수 인계

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r02-preparation`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-01, T5-08, T6-02는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
