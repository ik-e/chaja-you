# TASK-050 · 공통 앱·API·저장·결과 판정 구현

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R03 · 패키지: r03-app

## 목적

H1~H9·CO·KNOW·STORE·RESULT; 원자 수락/admit/observe/fence와 API; 별도 브라우저·PREP 구현 제외

## 작업 범위

- `product/lesson-registration/src/lesson_registration/app/`
- `product/lesson-registration/tests/modules/app/`

공통 계약: CS-01, CS-02, CS-03, CS-05, CS-06. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-050.json).

## 수용 기준

- r03-app-AC1: H1~H9, I1/I5 구현 및 I2/I3/I4 주입; 소유권·revision 검사
- r03-app-AC2: 영속 저장 원자 accept/admit/fence, 중복·경쟁·응답 유실 테스트
- r03-app-AC3: 실제 관측 근거 없으면 성공 금지; 오류 중단 및 조회 복구

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r03-app`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID T5-01, T5-05, T5-06, T5-11, T5-12, T6-01, DV-01는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
