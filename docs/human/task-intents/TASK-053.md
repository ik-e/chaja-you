# TASK-053 · 원격 브라우저 runtime·인증·뷰어 구현

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R05 · 패키지: r05-remote

## 목적

I3/I4 facade·runtime gateway·viewer client·STORE 호출; 실제 플랫폼별 업무 규칙 제외

## 작업 범위

- `product/lesson-registration/src/lesson_registration/remote/`
- `product/lesson-registration/tests/modules/remote/`

공통 계약: CS-04, CS-05, CS-07. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-053.json).

## 수용 기준

- r05-remote-AC1: I3/I4 facade와 RT-01~04, viewer 제공; 같은 인증 연결 인계
- r05-remote-AC2: 세션·계정·lease 격리, STORE admission 및 fence 연결; raw driver 노출 금지
- r05-remote-AC3: 중립 mock에서 실제 브라우저 제어·뷰어 분리·응답 유실 시험

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r05-remote`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-02, AT-03, T5-02, T5-12, DV-02, DV-05는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
