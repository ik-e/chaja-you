# 아이디어·후보 공간

이 디렉터리는 **가치가 있을 수 있지만 아직 현재 설계·범위·결정으로 채택되지 않은 아이디어, 가설, 대안, 미래 기능 후보**를 보존하는 AI 정본 공간이다.

후보는 현재 프로젝트 기준이 아니다. 후보가 존재한다는 이유만으로 TASK, 설계, 요구사항, 구현, 일정에 자동 적용하지 않는다.

## 기본 원칙

- 후보는 사람의 장기 Intent와 병행해 보존할 수 있지만 Intent·ADR·state·spec·task를 대신하지 않는다.
- AI는 일반 작업 시작 시 이 디렉터리를 기본 컨텍스트로 전부 읽지 않는다.
- 현재 TASK가 후보를 명시적으로 참조하거나, 아이데이션·대안 탐색·재검토가 목적일 때만 필요한 후보를 읽는다.
- 후보에는 **왜 가치가 있을 수 있는지**, **왜 아직 채택하지 않는지**, **무슨 근거가 생기면 다시 볼지**를 남긴다.
- 후보를 저장하는 것은 구현 승인이나 범위 확정을 의미하지 않는다.
- 후보가 현재 기준으로 승격되려면 필요한 조사·실험·비교를 거친 뒤 권한 있는 사람의 결정으로 Design·Spec·ADR·Task 등 적절한 정본에 반영한다.
- 후보가 폐기되더라도 과거 판단을 이해할 가치가 있으면 이유와 함께 기록을 보존한다.

## 승격 경로

```text
Candidate
   ↓ 필요한 근거가 생김
Research / Task / Run / Evaluation
   ↓
Human decision
   ↓
Design / Spec / ADR / Task / State
```

후보 공간은 **현재 시스템을 복잡하게 만들지 않고 가능성을 잃지 않기 위한 완충 지대**다. 후보를 많이 만드는 것 자체는 목표가 아니며, 현재 의사결정에 다시 사용할 가능성이 있는 아이디어만 보존한다.

새 후보를 만들 때는 [template.json](template.json)을 사용한다. 팀원이나 AI가 낸 원제안이 있으면 `proposed_by`와 `source_idea_refs`로 출처를 보존한다. 여러 사람이 비슷한 아이디어를 냈다면 후보를 중복 생성하기보다 하나의 Candidate로 병합하고 제안자·원제안 경로를 모두 남긴다.

팀원이 아직 정리되지 않은 아이디어를 제안할 때는 [팀 아이디어 Inbox](../../ideas/README.md)에 먼저 남길 수 있다. Candidate는 Inbox의 모든 아이디어를 자동 승격하는 공간이 아니라, 다시 검토할 가치가 있다고 판단된 아이디어를 중복·위험·재검토 조건과 함께 정리하는 공간이다.

## 현재 후보

- [CAND-001 · 의사결정 지원형 리서치](CAND-001.json)
- [CAND-002 · 정보가치 기반 조사 제어](CAND-002.json)
- [CAND-003 · Research State 독립 객체화](CAND-003.json)
- [CAND-004 · 질문별 증분 조사·Projection](CAND-004.json)
- [CAND-005 · Domain Profile](CAND-005.json)
- [CAND-006 · 두 번째 도메인 Transfer Test](CAND-006.json)
- [CAND-007 · 사용자 문제 검증 트랙](CAND-007.json)
- [CAND-008 · Benchmark·평가 Metric 체계](CAND-008.json)
- [CAND-009 · Source Registry / 인터넷 지도](CAND-009.json)
- [CAND-010 · Reviewed Research Experience + Retrieval](CAND-010.json)
- [CAND-011 · Research Execution Adapter 확장](CAND-011.json)
- [CAND-012 · 자유 역할·에이전트 생성](CAND-012.json)
- [CAND-013 · 범용 Workflow / Recovery Runtime](CAND-013.json)
- [CAND-014 · AI-native PR / Verification Workflow](CAND-014.json)
- [CAND-015 · 프로젝트 메타구조 개선군](CAND-015.json)

[AI 산출물 목차](../README.md)
