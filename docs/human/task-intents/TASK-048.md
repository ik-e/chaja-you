# TASK-048 · 공통 계약·개발 환경 유지 및 점진 통합 검증

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R01 · 패키지: common

## 목적

공통 계약 핀·공통 fixture/stub·composition·통합 시험; 플랫폼 실행기 구현 제외

## 작업 범위

- `product/lesson-registration/WORKSPACE.json`
- `product/lesson-registration/README.md`
- `product/lesson-registration/dev.py`
- `product/lesson-registration/pyproject.toml`
- `product/lesson-registration/uv.lock`
- `product/lesson-registration/.gitignore`
- `product/lesson-registration/contracts/`
- `product/lesson-registration/src/lesson_registration/__init__.py`
- `product/lesson-registration/src/lesson_registration/composition/`
- `product/lesson-registration/fixtures/shared/`
- `product/lesson-registration/tests/contract/`
- `product/lesson-registration/tests/integration/`
- `product/lesson-registration/stubs/`
- `product/lesson-registration/evidence/`
- `product/lesson-registration/src/lesson_registration/platforms/__init__.py`
- `product/lesson-registration/AGENTS.md`
- `product/lesson-registration/WORK-PACKAGES.md`

공통 계약: CS-01, CS-07, CS-08, CS-09. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-048.json).

## 수용 기준

- common-AC1: 공통 계약 pin 및 경로 소유권 검증
- common-AC2: 모든 패키지 독립 smoke·fixture 검증
- common-AC3: 실제 제품 수용 시험은 별도로 판정

- 독립 실행: `uv run --locked --python 3.12 python dev.py test common`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-01, T5-08, T5-11, T6-01, T6-02, AT-02, AT-03, T5-01, T5-02, T5-12, T5-03, T5-07, AT-04, AT-05, T5-06, T5-13, T5-05, DV-01, DV-02, DV-03, DV-04, DV-05는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
