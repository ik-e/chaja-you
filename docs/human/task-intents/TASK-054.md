# TASK-054 · 크몽 등록 adapter 및 독립 mock 구현

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R05 · 패키지: r05-kmong

## 목적

크몽 adapter 및 합성 플랫폼 페이지/fixture; 접수 readback; runtime·공통 상태 변경 금지

## 작업 범위

- `product/lesson-registration/src/lesson_registration/platforms/kmong/`
- `product/lesson-registration/fixtures/platforms/kmong/`
- `product/lesson-registration/tests/modules/kmong/`

공통 계약: CS-01, CS-05, CS-06. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-054.json).

## 수용 기준

- r05-kmong-AC1: K1~K7 승인값·이미지·조건부 필드 일치, 등록된 operation만
- r05-kmong-AC2: 제출 1회와 독립 receipt/이미지 digest 대조, 오류·unknown 중복 차단
- r05-kmong-AC3: 자체 mock 페이지 및 gateway 주입 시험; 실제 제출 금지

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r05-kmong`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-04, T5-13, DV-03, DV-04는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
