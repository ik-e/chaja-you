# HRESP-20261126-02 · 제출용 피드백 대응과 PostgreSQL 목표 방향

- 일자: 2026-11-26
- 권위: R01 대화 지시 (AI 정리)
- target: DLV-01~04, TASK-058, PHASE-20261126-01
- 지시: 강사 피드백을 먼저 제출용에 보완하고 실제 작업용도 진행될 수 있도록 한다. SQLite 대신 PostgreSQL을 사용하는 방향을 반영한다.

## 적용 경계

- 최종 제품/통합 DB 목표를 PostgreSQL로 잡는다. 기존 SQLite 구현·독립 검증과 기존 pin/lock/계약은 이력 및 영향 검토 기준으로 보존하고, 실제 전환은 확정된 사용자 스토리 및 DB 설계와 구현 영향 확인 후 별도 진행한다. DB 실행·설치·마이그레이션 완료로 표시하지 않는다.
- 활성 [PHASE-20261126-01](../phase-intents/PHASE-20261126-01.md), TASK-055~058과 INTENT-DESIGN-003 유지. R01은 TASK-058에서 사용자 스토리·범위 결정 후 DB 설계, 이후 API·프로토콜 입력을 책임진다. 이전 TASK-048~054는 보류 유지, R03 신규 TASK 배정하지 않는다.
- 나머지 인증 방식·상태 정본의 물리 표현·timeout/재시도·보존기간 등은 AI가 제출용 보완을 위해 제시한 설계/검증 후보이며 R01 확정 결정이 아니다. 실제 제품에서 검증 필요.
- [피드백 추적](../../artifacts/planning/lesson-registration-20261123/instructor-feedback-20261126.json) 및 [실제 설계 입력](../../artifacts/planning/lesson-registration-20261126/instructor-api-db-design-inputs.json). 새 범위에 대한 실제 플랫폼 실행 승인, 제품 시험 완료, 공식 제출/접수, 공수 확정은 별개.
