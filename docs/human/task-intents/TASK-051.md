# TASK-051 · 등록 지원 웹 UI 구현

- authority: R01 (HRESP-20261125-01의 배정 지시)
- drafted_by: AI
- status: 배정 기록, 세부 설계·공수는 담당자 검토
- 담당: R04 · 패키지: r04-web

## 목적

H1~H9 및 Viewer의 소비자; 화면·접속/승인/결과 UI; 서버·remote 구현 제외

## 작업 범위

- `product/lesson-registration/web/`
- `product/lesson-registration/tests/modules/web/`

공통 계약: CS-02, CS-03, CS-04, CS-06. [설계 검토 홈](../../design/lesson-registration/README.md) · [작업 공간](../../../product/lesson-registration/WORKSPACE.json) · [TASK 원본](../../artifacts/tasks/TASK-051.json).

## 수용 기준

- r04-web-AC1: H1~H9 사용자 흐름과 viewer mount/dispose 연동
- r04-web-AC2: 승인 전 정보 확인·수정, stale revision 처리, 승인 후 변경·취소·재개 금지
- r04-web-AC3: 독립 mock API 기반 UI 시험, unknown과 confirmed 구분

- 독립 실행: `uv run --locked --python 3.12 python dev.py test r04-web`
- 먼저 자신의 PLAN.md에 목적, 상세 결정·근거, 구현 순서, 시험·완료 조건을 기록한다. 스택과 공수 확인 후 세부 일정 제시. 제품 시험 ID AT-02, T5-05, T6-02, DV-05는 통합 수용 계약이며 bootstrap pass와 구분.
- 실제 플랫폼·계정·민감정보 금지. 자기 영역 국소 변경은 자율. 공유 계약/경계/의존성 및 범위 변경, 다른 담당 작업 변경은 R01에게 영향·대안을 제시. 완료는 실제 시험 근거로 판정.
