# TASK-052 · 숨고 등록 adapter 및 독립 mock 구현

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R04 · 패키지: r04-soomgo

## 목적

숨고 adapter 및 합성 플랫폼 페이지/fixture; 서비스 설정 관측; 원격 runtime·공통 상태 변경 금지

## 작업 범위

- `product/lesson-registration/src/lesson_registration/platforms/soomgo/`
- `product/lesson-registration/fixtures/platforms/soomgo/`
- `product/lesson-registration/tests/modules/soomgo/`

공통 계약: CS-01, CS-05, CS-06. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-052.json).

## 수용 기준

- r04-soomgo-AC1: S1~S6 등록된 operation 및 승인된 설정값 사용
- r04-soomgo-AC2: 저장 1회와 독립 readback 확인, 잘못된 대상·응답 유실 실패 검사
- r04-soomgo-AC3: 자체 mock 페이지/fixture 및 gateway 주입 시험; 실제 서비스 금지

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r04-soomgo`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-05, T5-13, DV-03, DV-04는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
