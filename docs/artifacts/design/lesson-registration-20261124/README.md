# 레슨 등록 설계 V0.1

> 2026-11-24 · R01 검토용 논리 설계 V0.1. 최종 제품 채택·본 구현·실서비스 실행 승인 아님. 기존 R03~R05 TASK 및 공통 시험 계약 변경 없음.

기준: [기획 V1.1](../../planning/lesson-registration-20261123/proposal-v1.1.md) · [점진적 설계 순서](../../../deliverables/PROGRESSIVE-DESIGN-ORDER.md) · [현 단계](../../../human/phase-intents/PHASE-20261124-02.md) · [독립 작업 계약](PLATFORM-INDEPENDENT-WORK.md).

| 범위 | 구조화 설계 | 검토 문서 |
|---|---|---|
| L2 사용자·FR/NFR·수용 조건 | [JSON](requirements-v0.1.json) | [요구사항](REQUIREMENTS-V0.1.md) |
| L3 업무 규칙/L5 데이터·상태 | [JSON](domain-workflow-v0.1.json) | [도메인·흐름](DOMAIN-WORKFLOW-V0.1.md) |
| L3 경계/L4 전략·책임/L5 논리 인터페이스 | [JSON](system-contracts-v0.1.json) | [시스템 계약](SYSTEM-CONTRACTS-V0.1.md) |
| L2~L6 검증·미결정 | [JSON](verification-decisions-v0.1.json) | [검증·결정](VERIFICATION-DECISIONS-V0.1.md) |

4개 JSON은 동일 ID/관계로 연결한다. Markdown은 동일 변경에서 동기화하는 검토 뷰이며 기존 project_docs.py가 자동 생성하지 않는다. 이전 Step2 잠정 문서의 당근·90분 30만원 예시는 현재 기준으로 사용하지 않는다. 실제 제출 문서·기획·TASK 및 공통 환경은 변경하지 않았다.

현재는 논리 설계 및 대안만 작성. 물리 실행 단위·기술·실제 정책·최종 범위와 본 구현 배정은 보류한다.
