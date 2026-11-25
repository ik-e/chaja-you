# 설계 정본 공간

## 현재 제품의 설계 탐색

- [현행 AI용 인덱스](../../design/lesson-registration/CURRENT-DESIGN.json) · [현행 사람용 설계 기준](../../design/lesson-registration/CURRENT-DESIGN.md)
- [논리 채택 기록](lesson-registration-20261124/adoption-20261125.json) · [공통 구현 결정](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json)
- 아래 Target Design 가설 및 일반 계층은 설계 방법/이전 찾아you 기록이며 현재 레슨 등록 제품의 실행 지시가 아니다. 현행 적용은 위 인덱스 및 CURRENT의 Phase/TASK를 확인한다.

이 디렉터리는 찾아you의 설계를 **상위 가설 → 하위 검증 설계** 관계로 관리하는 AI 정본 공간이다.

## 설계 계층

1. **Human Intent** — `docs/human/INTENT.md`
   - 장기 목적, 가치, 제약, 결정 권한.
2. **Target Design Hypothesis** — `target_design.json`
   - 최종 시스템에 필요한 능력, 경계, 설계 가설, 열린 질문.
   - 구현 구조의 확정본이 아니다.
3. **Domain / MVP Design**
   - 향후 `domains/` 또는 기존 `specs/`, `planning/`에서 관리.
   - 특정 도메인과 최소 실험이 어떤 Target Design 가설을 검증하는지 명시한다.
4. **Component / Interface Design**
   - 향후 `components/` 또는 관련 TASK/spec에서 관리.
   - 현재 구현에 필요한 상태, 계약, API/인터페이스를 구체화한다.
5. **Implementation**
   - 실제 코드와 실행 환경.
6. **Evidence / Evaluation**
   - `docs/artifacts/runs/`, `docs/artifacts/evaluations/`, TASK result.
   - 결과를 Target Design 가설에 되돌린다.

## 하위 설계 문서 규칙

새 하위 설계는 가능한 범위에서 다음을 가진다.

- `parent_ref`: 어떤 상위 설계에서 도출되었는지
- `tests_hypotheses`: 어떤 capability/가설/질문을 검증하는지
- `scope_boundaries`: 이번 설계가 다루지 않는 것
- `revisit_when`: 어떤 관찰이나 결과가 나오면 다시 설계할지

상위에서 필요한 **능력과 질문은 top-down**으로 유지하고, 구체 구조의 공통화와 일반화는 **실제 도메인 구현과 평가에서 bottom-up**으로 확인한다.

사람용 Target Design은 `docs/design/TARGET-DESIGN.md`로 프로젝션한다. 사람이 수정 의견을 내면 먼저 정본 또는 Intent/ADR에 반영한 뒤 다시 생성한다.
