# 기존 기술의 해결 능력 지도

- 조사 기준일: 2026-11-16 (KST)
- 저장소 기준: `experiment/r01-codex-cloud-20261114`
- 범위: 공개된 공식 문서와 지정한 저장소 버전. 제품 간 성능 순위나 사용자 고통의 강도는 평가하지 않는다.
- 상태: `확인`은 문서/소스에서 직접 기능이 확인됨, `부분`은 특정 경로나 조건에서만 지원, `미제공`은 해당 도구의 조사 범위에서 기능이 없거나 목적이 아님, `미확인`은 공개 근거로 판단하지 못함.

## 기술별 능력 매트릭스

| 해결 능력 | Projects | Codex Cloud | OpenSpec | Spec Kit | BMad | BATHOS | LangGraph | Agents SDK | Letta | Mem0 | GitHub Actions / 보호 규칙 |
|---|---|---|---|---|---|---|---|---|---|---|
| 목적·요구를 검토 가능한 산출물로 변환 | 부분: 프로젝트 지시·파일·대화 문맥 | 미제공: 실행 환경 | 확인: proposal/spec/design/tasks | 확인: spec/plan/tasks | 확인: 순차 워크플로 산출물 | 부분: discovery~story gate 산출물 | 미제공: 그래프 런타임 | 미제공: 에이전트 SDK | 미제공: 기억 계층 | 미제공: CI·병합 인프라 |
| 기존 목표와 새 조건의 차이·영향 관리 | 미확인: 전용 변경 추적 기능 | 미제공 | 확인: spec delta, sync, archive | 부분: clarify/plan 재생성·converge | 부분: 계획 문서 갱신 워크플로 | 부분: wave·manifest 기반 진행(프로젝트 주장) | 미제공 | 미제공 | 미제공 | 부분: 변경된 커밋에서 체크를 다시 실행할 수 있으나 의미상 영향 분석은 아님 |
| 장기 문맥·기억 재사용 | 부분: 프로젝트 대화·파일·지시 | 미제공: VM 보존과 사용자 기억은 별도 | 부분: 저장소 산출물의 Git 기록 | 부분: 저장소 내 feature/spec 기록 | 부분: 프로젝트 컨텍스트 파일 | 부분: 디스크 산출물/세션 복구(프로젝트 주장) | 부분: thread checkpoint + 별도 Store | 부분: session은 실행 간 대화 내역 | 확인: Git 기반 MemFS 파일 | 확인: ID 범위가 있는 메모리 저장·검색 | 미제공 |
| 작업 분해·담당 전환·인계 | 미제공 | 부분: 별도 Cloud task로 격리된 실행 | 확인: schema가 artifact 단계 정의 | 확인: task 목록·선후관계 | 확인: 역할/워크플로/단계별 핸드오프 | 확인(문서): 역할·wave·동시성 상한 | 확인: node/edge/state 기반 그래프 | 확인: 도구 형태의 handoff, 입력 필터 | 부분: memory subagent는 기억 유지 작업에 한정 | 미제공: 기억 API가 업무 workflow를 나누지는 않음 | 부분: job 간 산출물/의존성 구성 |
| 중단 후 상태 지속·재개 | 부분: 프로젝트 대화가 문맥 제공 | 확인: 원 task workspace 이어하기; 새 task와 분리 | 부분: 파일 상태를 사람이 다시 열어 이어감 | 부분: feature JSON·산출물 기반 재개 | 부분: workflow 상태/산출물 재사용 | 확인(문서): 저장된 세션 복구 | 확인: checkpointer checkpoint와 `thread_id` | 확인: 저장형 session 및 승인 중 RunState 직렬화 | 확인: commit/push된 memory가 다른 실행 컴퓨터에 동기화 | 부분: 지속 저장소·식별자·검색은 설정에 달림 | 부분: workflow run 상태는 CI 실행에 한정 |
| 행동 권한·인간 승인·검증 | 부분: 공유 프로젝트 접근 제어 | 부분: 연결 계정의 저장소 권한 및 환경 설정에 따름 | 부분: archive는 미완료 task를 경고/확인하지만 `--yes`로 진행 가능; `verify`는 AI 검토 | 부분: 미완료 checklist에서 구현 전 멈추도록 안내 | 부분: workflow의 승인 checkpoint; 지침 수준 | 부분: 감지된 FAIL은 hook이 차단; verdict/작업 판별 실패 시 fail-open | 확인: `interrupt()`에서 명시적 사람 결정 후 resume | 확인: 승인 필요 도구, 승인/거절 후 재개 | 부분: 스코프 ID·CRUD는 있으나 기억 수정의 사람 승인 절차는 별도 아님 | 확인: required check/review 설정이 병합을 막을 수 있음 |
| 자동 검증의 보장 경계 | 미확인 | 미제공 | 부분: delta validator는 구조 검사, AI verify는 병합/보관의 hard gate 아님 | 부분: analyze/converge는 에이전트 분석·수정 지침 | 부분: 체크리스트·리뷰가 model/workflow 의존 | 부분: Rust engine/gate는 프로젝트 주장; 이번 조사에서 소스 실행 검증 안 함 | 미제공: 상태 제어이지 결과 정답 보장 아님 | 부분: guardrail은 정책 판단, tracing은 관찰 기록 | 부분: `/doctor`는 기억 배치/중복/토큰 감사 | 부분: 저장·검색/ID 연산은 구현되나 추출·관련도 품질은 모델 의존 | 확인: 지정된 상태가 없으면 보호 branch 병합 불가; 테스트 자체의 충실성은 보장 안 함 |

## 읽는 법

1. “확인”은 그 도구가 모든 문제를 해결한다는 뜻이 아니다. 예를 들어 LangGraph의 `interrupt`는 재개 지점과 값을 관리하지만, 승인자가 요청의 의미를 이해했는지는 보증하지 않는다.
2. 제품/방법론(BMad, BATHOS), 명세 CLI(OpenSpec, Spec Kit), 실행 SDK(LangGraph, Agents SDK), 기억 저장소(Letta, Mem0), GitHub CI/보호 규칙은 서로 다른 층이다. 동일 척도로 비교할 수 없다.
3. BATHOS의 gate hook 코드는 열람했지만 실행하지 않았다. hook은 감지된 구현 진입 시도 + 읽힌 `FAIL`에서 차단하고, verdict 부재/알 수 없는 값은 통과시키므로 전면적·fail-closed 권한 경계가 아니다. Rust engine 자체는 실행하지 않았다.
4. `미제공`은 해당 후보의 범위에 맞춘 판단이다. 예컨대 GitHub Actions가 주변 제품과 연계해 명세를 검사할 수는 있지만 Actions 자체는 요구 명세 생성기가 아니다.

## 중요한 메커니즘 빠른 보기

| 메커니즘 | 입력 → 결과 | 기계적으로 고정되는 것 | 의미 판단에 남는 것 |
|---|---|---|---|
| 명세 artifact 사슬(OpenSpec / Spec Kit) | 요청·결정 → 명세 → 계획/작업 → 코드 검토 기준 | 파일 경로, 체크박스, delta 구조 검사, 활성 feature 포인터 | 명세의 완전성, 코드와 의도의 일치 |
| 체크포인트와 재개(LangGraph / Agents SDK) | 실행 state + thread/session ID → 저장된 state로 이어 실행 | 저장소에 남은 checkpoint/run state와 재개 API의 상태 연결 | 중복 side effect 방지, 요청 타당성, 외부 API의 멱등성은 별도 설계 |
| 기억의 위치와 검색(Letta / Mem0) | 대화/규칙 → 파일 또는 scoped memory → 후속 검색 | 파일 commit, ID scope, 명시적 update/delete API | 무엇을 기억할지, 오래된 기억의 유효성, 검색의 유용성 |
| 병합 전 hard gate(GitHub) | commit → Actions status + 리뷰 → 병합 허용/차단 | 보호 규칙으로 지정한 상태·리뷰 조건 | 체크가 실제 위험을 포착하는지, 예외/bypass 정책 |

세부 X/E/C→Y, 근거와 제한은 [기술 카드](02-technology-cards.md)를 참조한다. 출처 버전과 직접 확인 범위는 [STATUS](STATUS.md)에 정리했다.
