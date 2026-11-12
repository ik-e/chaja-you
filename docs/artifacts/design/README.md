# 설계 정본 공간

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
