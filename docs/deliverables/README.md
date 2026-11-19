# 기획 → 시스템 설계 통합 정보 모델

> **상태: R01 검토용 설계 초안 · 2026-11-19.** 사용자 문제와 제품 요구에서 시스템·컴포넌트·데이터·API·UI·보안·배포로 점진적으로 구체화합니다. **검증·테스트 설계는 모든 수준에 포함**되며, 실제 시험 수행 결과는 별도로 관리합니다.
> [현재 Phase Intent](../human/phase-intents/PHASE-20261118-01.md)와 기존 GitHub 정보 정본은 변경하지 않습니다. 미선정 제품·미실행 테스트를 확정/성공으로 오해하지 않습니다.

## 기획·설계 정보 모델을 읽는 순서

1. **[기획 → 시스템 설계 + 수준별 검증/시험 설계](PLANNING-DESIGN-INFO-MODEL.md)** — 전체 정보 구조와 두 개의 연결 다이어그램
2. **[점진적 설계 결정 순서](PROGRESSIVE-DESIGN-ORDER.md)** — L0~L6의 현재 결정·유보·검증 항목, L7 후속 전달
3. [정밀 용어집](DESIGN-GLOSSARY.md) — 문제/도메인/시스템/실행 단위/컴포넌트/배포/Validation/Verification 구분
4. [구성요소·테스트 추적·시퀀스·데이터 관계도](COMPONENT-DESIGN-VIEWS.md) — 구체적 구조와 그 구성요소별 시험 설계
5. [기획·설계 구조화 정보 모델 JSON](planning-design-info-model.json) — 단계·정보 속성·관계·각 단계 검증 설계
6. [구성요소 정보 모델 JSON](component-design-model.json) — 논리 실행 단위·컴포넌트 책임과 계약·검증 참조

## 기존 프로젝트 정보 체계와의 연계

- [WORK-MODEL](WORK-MODEL.md)은 기존 13개 정보 영역과 정보 정본의 원칙을 설명합니다. 별도 문서 13개 작성을 강제하지 않습니다.
- [산출물 프로젝션 계약](PROJECTION-CONTRACT.md)과 [레지스트리](registry.json)는 공식 제출 양식에 필요한 정보를 참조하는 수단이지, 설계 결정을 내리는 순서는 아닙니다.
- [산출물 품질·제출 게이트](QUALITY-GATES.md)의 제출·접수 확인은 기획/설계의 검증·시험 설계와 구분합니다.
- 가상의 [CAND-016 정보 추적](pilots/2026-11-19-planning-design-v2/CAND-016-TRACE.json), [공통 업무 계약](pilots/2026-11-19-planning-design-v2/DOMAIN-CONTRACT.json), [구조 검증 기록](pilots/2026-11-19-planning-design-v2/REVIEW.md)은 사례 검토용이며 실제 제품 승인이나 실측이 아닙니다.
- [구조 검사](../../tools/validate_planning_design_model.py)는 타입·참조·관계·기본 계약이 일치하는지 확인합니다. 실제 사용자 문제·가치·구현 성능까지 확인하는 시험은 아닙니다.

## 설계와 분리한 후속 활동

**AI 작업 운영 플레이북:** [AI-DESIGN-PLAYBOOK.md](AI-DESIGN-PLAYBOOK.md)는 기존 실험 기록으로 보존하되 **기획·설계 정보 모델의 기본 진입점이 아닙니다.** AI 작업 위임·S/M/H 작업 모드·자율 실행 루프는 별개로 검토합니다. [관련 운영 검토](pilots/2026-11-19-planning-design-v2/V4-REVIEW.md) · [운영 예시](pilots/2026-11-19-planning-design-v2/AI-SLICE-EXAMPLE.json).

**실제 시험과 문서 제출:** 설계 단계에서는 시험의 대상·조건·환경·예상 결과·판정 기준을 정의합니다. 실행한 시험의 증거는 Run/Eval에 별도로 기록하고, WBS·TASK와 제출 상태도 각자 기존 정본을 유지합니다.

## 남아 있는 확인

정보 모델은 설계 방향과 최소 정보 계약을 제안할 뿐 모든 프로젝트에 최적인 순서임을 증명하지는 않습니다. 실제 선정된 제품의 대표 시나리오에서 '문제→요구→구성요소→상태/데이터/API/UI→테스트 설계'를 추적하고 누락/중복·품질 제약을 검토해야 합니다.
