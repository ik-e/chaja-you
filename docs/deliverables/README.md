# 기획·설계·AI 실행 정보 체계 · 검토용 V4

> **상태: 운영 설계 초안(제품·기술·기능 선택 아님)** · 작성 기준: 2026-11-18 · 책임: R01 · 현재 [Phase Intent](../human/phase-intents/PHASE-20261118-01.md)
>
> 목적은 **제출문서 16개를 각각 작성하는 것**이 아니라, 실제 작업에서 생기는 정보·근거를 한 번 구조화하여 공식 목차에 맞춰 필요할 때 **프로젝션하는 것**입니다. 현재 찾아you 기획/WBS는 제출용 잠정 스냅샷이며 실제 구현 기준으로 보류 중입니다.

## 바로 읽을 순서

1. **[V4 경량 AI 설계·실행 플레이북](AI-DESIGN-PLAYBOOK.md)**: 7개 작업 정보, S/M/H 설계 깊이, 최소 슬라이스와 실측·피드백 루프. 매 작업의 기본 진입점
2. [기획 → 설계 결정·정보 모델 V3](PLANNING-DESIGN-INFO-MODEL.md): 점진적 설계 결정 순서, 실제 정보 필드, 병렬 설계·확정 조건 및 추적 사례(2026-11-19 검토용 제안)
3. [점진적 설계 순서와 이번에 결정하지 않을 항목](PROGRESSIVE-DESIGN-ORDER.md): 큰 틀부터 구체화하는 L0~L7 판단·보류 기준
4. [정밀 설계 용어집](DESIGN-GLOSSARY.md): System / C4 실행 단위 / Component / Deployment 및 상태·계약 구분
5. [구성요소 설계 순서도·구조도](COMPONENT-DESIGN-VIEWS.md): System→실행 단위→컴포넌트→데이터·API·상태의 실제 설계 내용과 순서
6. [작업 정보 모델](WORK-MODEL.md): 어떤 정보가 어디에 있고 누가 소유하는가
7. [품질 게이트](QUALITY-GATES.md): 정보·문서·실측·제출을 언제 완료로 볼 수 있는가
8. [산출물 프로젝션 계약](PROJECTION-CONTRACT.md): 16개 공식 항목과 작업 정보를 어떻게 연결하는가
9. [원본·판단 근거](SOURCES-AND-DECISIONS.md): 공식 안내·교육 예시·국제 표준의 권위를 어떻게 구분하는가
10. [작업 사례](WORKFLOW-EXAMPLES.md): 두 트랙과 AI 초안·사람 검토의 실제 적용

**V4 시험 및 검증:** [AI 슬라이스 모의 예시](pilots/2026-11-19-planning-design-v2/AI-SLICE-EXAMPLE.json) · [경량 계약 검사](../../tools/check_ai_design_playbook.py) · [V4 평가 기록](pilots/2026-11-19-planning-design-v2/V4-REVIEW.md) · [전용 CI 워크플로](../../.github/workflows/ai-design-playbook-check.yml). 정식 기능 시험이나 사용자 가치 검증은 별개입니다.

**구조화 원본:** [기획·설계 V3 구조화 모델](planning-design-info-model.json) · [구성요소 설계 하위 모델](component-design-model.json) · [공통 상태·오류 계약](pilots/2026-11-19-planning-design-v2/DOMAIN-CONTRACT.json) · [후보 사례·검토 기록](pilots/2026-11-19-planning-design-v2/REVIEW.md) · [모델 검사 코드](../../tools/validate_planning_design_model.py) · [16개 산출물·근거·검증 매핑](registry.json) · [작업 정보 예시/스키마](work-record-template.json) · [제출 상태 기록 형식](submission-entry-template.json) · [공식 목차 대조 양식](official-outline-template.json)

**사용 원칙:** V3의 28개 정보 유형·202개 필드는 *전부 입력할 양식이 아니라 필요한 경우 참조할 사전*입니다. 실제 AI 작업은 기존 TASK 정본을 읽고, 변경 범위의 최소 계약만 정리한 뒤, 구현 가능한 작은 슬라이스를 실행·검증합니다.

## 기존 저장소와의 관계

- **기존 정본을 대체하지 않습니다.** [INTENT](../human/INTENT.md) → [Phase Intent](../human/phase-intents/README.md) → [CURRENT](../../CURRENT.md) → TASK/Spec/Run/Eval/ADR의 기존 관계를 유지합니다.
- [AI 원본](../artifacts/README.md)과 [TASK](../artifacts/tasks/README.md)·[프로젝션 생성기](../../tools/project_docs.py)를 재사용합니다. 새로운 Work Record는 현장 정보 유형을 정의하는 **제안 형식**으로, 기존 파일을 자동 변환하지 않습니다.
- 제출 상태의 현재 단일 정본은 [current.json](../artifacts/state/current.json) 및 **비공개 강사 대시보드**입니다. 이 레지스트리는 제출 완료 여부를 소유하지 않습니다.
- 공식 목차는 아직 16개 모두 검증되지 않았습니다. 교육용 Google Docs 예시는 01~12를 설명하지만 공식 의무 목차로 자동 승격하지 않습니다.
- GitHub에 **고정·비공개가 아닌 근거만** 둡니다. 비공개 대시보드 주소, 권한 없는 파일·개인정보·비밀값은 저장하지 않습니다.

## 범위 밖

실제 주제/FR/NFR/기술 스택 최종 선정, API·DB 구현, 시험을 하지 않은 결과값 작성, 강사 대시보드의 제출완료 처리 등은 이 체계 구축에 포함하지 않습니다.

## 단계별 도입

- **지금(11/18):** 유형·근거·품질 게이트·16개 매핑의 설계 기준만 고정해 공유 가능한 초안으로 보존
- **우선 제출(11/20):** 기존 찾아you 근거를 재사용하되 Step 1~2만 공식 형식과 대조해 잠정 제출본 작성
- **주제 선정(11/21 목표):** 실제 주제에 맞게 필요한 작업 영역과 산출물 입력을 정함. 재작성은 값과 관계를 중심으로 수행
- **이후 8주 내:** 실제 구현/검증 기록이 발생할 때만 결과 보고서에 편입. 없는 결과는 `not_run`/미확인으로 표시

**검증 주의:** 저장소 문서 검사/CI는 링크·ID·필드·해시 검증을 수행할 수 있어도, 사용자 Pain이나 성능을 객관적으로 입증할 수 없습니다.
