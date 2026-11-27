# HRESP-20261127-02 · V3.1 잠정 기준 논리 DB 착수

- 날짜: 2026-11-27
- 권위: R01 대화 지시 (AI 기록)
- target: TASK-058 / INTENT-DESIGN-003

## 사용자 입력 원문

> 우선 잠정적으로 3.1 기준으로 DB 설계하면 좋을 것 같은데 괜찮나?

> 그러면 권장대로 진행해봐

## 적용

직전 권장 진행 범위인 V3.1-R1을 잠정 설계 기준선으로 pin하고 사용자 스토리별 데이터 요구·논리 엔티티/관계·ERD·양방향 추적까지 진행한다. 팀 검토 결과로 변경될 수 있으며 사용자 스토리와 논리 DB의 최종 승인 또는 물리 PostgreSQL schema/마이그레이션/API 구현을 의미하지 않는다.

- 기준: [V3.1-R1 사용자 스토리](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/artifacts/planning/lesson-registration-20261126/integrated/v3.1/user-stories.json) (blob `d11f63353fd48bee4126d7fd916a6d870f55410f`)
- 후보: [논리 DB](../../artifacts/planning/lesson-registration-20261126/integrated/db-design.json), [논리 ERD](../../review/lesson-registration/LOGICAL-DB-ERD-V1.0.md)
- 기존 서비스 범위 V1.0, mock-only, 다른 팀원 작업/구현 보류 유지. 기존 SQLite 및 상위 논리 계약 보존. Notion 중복 기록 없음.

DB 설계 과정에서 확인된 범위·권리·실제 플랫폼 규칙 등 미결정 사항은 R01 판단/근거 검증으로 돌려보낸다.
