# 기존 기술 카드: 입력·메커니즘·경계

- 확인 시점: 2026-11-16 (KST)
- 작업 상태와 근거 상태는 별개다. 모든 코드/API 예시는 설계 설명이며 직접 실행하지 않아 `not_run`이다.
- `documented`: 공식 문서, `source_inspected`: 공식 저장소 파일을 열람, `self_reported`: 프로젝트가 자기 구현/수치를 보고, `unknown`: 이 조사에서 확인하지 않음.

## 1. ChatGPT Projects와 Codex Cloud

### A. Projects — 프로젝트 경계 안의 문맥 묶음

- **문맥:** 주제별 파일·대화·지시를 반복적으로 다시 설명하고 찾아야 하는 작업.
- **X/E/C → Y:** 프로젝트 지시, 업로드 파일, 프로젝트 안의 대화/연결 자료 + 해당 프로젝트에서 시작한 질의 → 그 범위의 문맥을 참조한 답변. 기존 대화를 프로젝트로 옮기면 프로젝트 파일과 지시를 해당 채팅에서 이어 쓴다.
- **메커니즘:** 프로젝트는 채팅, 파일, 지시, 연결 앱 자료를 한 공간에 두고, 응답을 프로젝트 source로 저장할 수도 있다. 공유 프로젝트에서는 역할별 접근 권한을 둔다.
- **보장/경계:** 프로젝트 지시가 그 프로젝트 안에서 전역 사용자 지시보다 우선한다는 동작은 문서화되어 있다. “관련 문맥을 사용한다”는 것이 정확한 회상, 최신성 판별, 특정 결정을 자동 폐기하는 것을 보장하지 않는다.
- **작은 예:** 가짜 프로젝트의 `policy.md`와 제품 배경 파일을 넣고, 프로젝트 지시를 적은 다음 질의한다. 기존의 일반 채팅을 옮겨 context를 이어 받는 흐름도 문서에 있다. **상태: documented; not_run.**
- **비용/제약:** 업로드·앱 연결 가능 여부와 파일 한도는 계정/플랜 기능에 따름. 프로젝트 공유는 수신자 권한 범위가 확대되는 행위이므로 공유 설정이 필요하다.
- **재사용 힌트:** 작업별 지시와 자료의 경계를 두면 문맥 혼입을 줄이는 데 쓸 수 있다. 유효 기간이 지난 결정을 무효화하는 버전 규칙은 별도 설계해야 한다.
- **근거:** [Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt) (OpenAI 도움말, 페이지 업데이트 Nov 14로 표시; 확인 Nov 16). **근거 상태: documented.**

### B. Codex Cloud — 분리된 비동기 실행 환경과 원 task 재개

- **문맥:** 개발자가 자리를 비워도 원격 코드 작업이 계속되거나, 동일 작업을 나중에 이어야 하는 경우.
- **X/E/C → Y:** 저장소와 환경 설정 + 하나의 Codex task → 별도 작업 공간에서 실행된 변경 결과; 원래 task를 다시 열어 상태·변경을 계속 이어갈 수 있다.
- **메커니즘:** Codex Cloud는 관리형 컴퓨터, repository checkout, 도구·의존성 설정을 제공한다. task별 workspace와 파일 변경은 격리된다. 문서상 마지막 task/턴 이후 7일 이내 저장 VM 상태를 복구할 수 있으며, 새 task는 다른 task의 미커밋 변경을 받지 않는다.
- **보장/경계:** task workspace 분리와 원 task 재개가 문서화되어 있다. VM 보존은 대화 전체의 무기한 기억이 아니며, task 간 공유를 뜻하지 않는다. GitHub 접근은 연결된 사용자 권한을 따르고 VM이 권한을 확대하지 않는다.
- **작은 예:** repository를 연결하고 task를 생성 → 환경에서 변경·커밋 → 나중에 같은 task를 열어 이어서 작업. 새 task가 이전 uncommitted 파일을 보는 것으로 가정하지 않는다. **상태: documented; not_run.**
- **비용/제약:** 관리형 실행 자원·네트워크 정책·repo 권한·환경 설정에 의존. 새 task에는 환경 설정 변경이 반영될 수 있지만 이미 실행 중인 작업에는 기존 상태가 유지된다.
- **재사용 힌트:** “대화 기억”과 “실행 파일/작업 상태”를 독립된 보존 범위로 모델링하는 방식.
- **근거:** [Using Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud) (OpenAI 도움말, 확인 Nov 16). **근거 상태: documented.**

## 2. OpenSpec — proposal·spec delta·변경 후 archive

- **문맥:** 구현 중 새 조건이 들어와도 기존 요구를 어떤 변경으로 반영할지 추적해야 하는 저장소 작업.
- **기능 1 — artifact workflow:** X = 자연어 변경 요청 + 현재 spec; E = schema가 정한 작업 artifact 순서; Y = proposal/spec/design/tasks가 생성·갱신되어 구현자가 실행할 변경 단위로 이어짐. `openspec` CLI는 템플릿·상태·지시와 artifact 경로를 결정적으로 다루고, 계획 문서 자체 내용은 assistant가 작성한다.
- **기능 2 — apply/sync/archive:** 기존 spec에 대한 delta를 검증하고 적용하여 기존 기준 명세를 갱신한다. `verify`는 빠진 내용·일관성을 AI가 검토하는 단계다.
- **기계적 보장:** validator는 파일/블록 구조, 중복 target, rename 짝과 경로 안전성 등의 규칙을 확인한다. `archive`는 task checkbox를 읽지만 미완료가 hard gate는 아니다. 대화형 확인을 받거나 비대화형 기본 모드에서는 정지하며, `--yes`로 경고 후 진행 가능하다. 코드에서 확인한 범위를 넘어서 원자적 전체 rollback을 주장하지 않는다.
- **비보장:** `verify`는 AI 검토이며 archive를 막지 않는다. spec 완전성, 테스트 충분성, 코드가 의도대로 동작함은 사람/CI의 책임이다.
- **작은 예:** 현재 가짜 사양 → 변경 proposal 생성 → 새 요구의 spec delta와 task 작성 → 구현 → verify → 승인된 시점에 sync/archive. 미완료 task를 남긴 채 `--yes`를 붙이면 경고 후 archive가 계속될 수 있다. **상태: documented + source_inspected; not_run.**
- **비용/제약:** 저장소 안의 파일/CLI 및 사용 중인 assistant가 필요. CLI가 입력 의도를 스스로 판단하거나 여러 repository로 task를 배정하지 않는다.
- **재사용 힌트:** 현재 요구와 제안된 변경을 분리 저장하고, 변경을 기준 spec으로 옮기는 시점을 명시하는 설계.
- **근거:** [Workflows](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/docs/workflows.md), [archive.ts](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/archive.ts), [specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/specs-apply.ts), [validator.ts](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/validation/validator.ts). 기준 ref: `ea635dd255f8686dcf48626bbcbe0e3fd59b6067` (main, 확인 Nov 16). **근거 상태: documented + source_inspected.**

## 3. GitHub Spec Kit — 자연어 의도를 개발 artifact로 연결

- **문맥:** 개발자가 요구·설계·task 순서를 직접 산출물로 옮기고 구현 범위를 추적해야 하는 작업.
- **기능 1 — spec/clarify/plan/tasks:** X = 자연어 기능 요구와 모호점 → specify가 spec 작성, clarify가 표적 질문을 통해 spec 갱신, plan이 설계/연구 artifact 생성, tasks가 dependency 순서가 있는 작업 목록 생성.
- **기능 2 — analyze/implement/converge:** analyze는 spec/plan/tasks 간 일관성을 읽기 전용으로 검토한다. implement는 task를 dependency 순으로 실행하고 체크되지 않은 checklist가 있으면 진행 전 사용자에게 확인하도록 유도한다. converge는 코드와 spec/plan/task를 맞춰 보고 남은 gap에 task를 추가한다.
- **메커니즘과 보장:** 워크플로의 주 실행 단위는 agent skill/prompt와 repository template이고, CLI는 초기화/설정 설치를 담당한다. active feature는 `.specify/feature.json` 포인터로 정한다. 선택적 Git 확장과 포인터 JSON은 별개다. 파일/포인터의 존재는 deterministic하지만 agent의 검토 품질은 보장되지 않는다.
- **작은 예:** CLI로 repo를 초기화 → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` → `/speckit-converge`. checklist의 reviewer-defined 항목을 완료 인증으로 간주하지 않는다. **상태: documented + source_inspected(templates); not_run.**
- **비용/제약:** 설치된 coding agent와 repo instruction 파일에 의존. 프롬프트는 의미적 일관성 검토를 요청하지만, 분석을 CI에서 강제하거나 승인되지 않은 코드가 저장되지 않도록 하는 격리 경계는 아니다.
- **재사용 힌트:** “무엇을/어떻게/어떤 순서로 구현할지”를 서로 참조하는 artifact로 분리하고, 구현 뒤 spec과 코드의 역방향 gap 검토를 두는 방식.
- **근거:** [Quickstart](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/quickstart.md), [Agentic SDD](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/reference/agentic-sdd.md), [spec template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/spec-template.md), [plan template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/plan-template.md). 기준 ref: `2ee2b1e8005905db05f5717300a469b3068b908f` (main, 확인 Nov 16). **근거 상태: documented + source_inspected.**

## 4. BMad Method — 순차 역할 워크플로와 검토 가능한 프로젝트 컨텍스트

- **문맥:** 큰 제품/개발 요청을 분석·계획·구현·검토로 나누고, 각 단계의 산출물과 다음 단계의 입력을 정해야 하는 경우.
- **기능 1 — right-sized workflow:** 입력은 user intent와 workflow 선택(route/review). route·review 값은 template이 검사한다. plan readiness 항목은 파일/경로가 있는 task, dependency 순서, testable Given/When/Then acceptance criteria, TBD가 없는 산출물, 충분한 정합성을 포함한다. task scope/길이 추천은 문서에 명시된 권장이지 hard gate가 아니다.
- **기능 2 — 프로젝트 컨텍스트 갱신:** repository 지침·설정·CI·문서·코드를 살피고, 기존 주장과 실행 명령을 근거에 대조해 보존/수정/이동/자동화/삭제 제안과 provenance를 만든다. 쓰기 전에 승인 단계를 둔다. 사용자는 파일 전체 삭제가 아니라 제안된 block을 승인하며, 삭제는 명시적 근거를 요구한다.
- **메커니즘과 보장:** workflow는 필요한 단계 지침을 순차로 열어 읽고, 상태를 산출물 frontmatter/대화에 기록하며 checkpoint에서 사용자 입력을 기다리도록 프롬프트화되어 있다. 승인/체크포인트는 workflow instruction에 의존하며 파일시스템 권한의 안전 장벽 자체는 아니다.
- **작은 예:** 기존 AGENTS 지침을 읽고, 실행 스크립트와 대조 → 각 claim에 파일 근거/위험을 붙인 변경안 → 사용자가 한 block을 승인 → 해당 block만 반영. 이 세션에서는 실행하지 않았다. **상태: documented + source_inspected; not_run.**
- **비용/제약:** 설치된 compatible agent와 repo 탐색 시간, 단계별 모델 호출이 필요. concurrent agent 실행은 런타임 지원 및 사용자 환경에 따라 달라진다. 의미 정확도는 모델 검토에 의존한다.
- **재사용 힌트:** 프로젝트 기억을 변경하기 전에 현재 source와 revision에 대조하고, 제안 단위로 provenance와 사용자 승인을 남기는 방식.
- **근거:** [bmad-build workflow](https://github.com/bmad-code-org/BMAD-METHOD/blob/e435a22574fe55722841086e5566420178b98df3/skills/method/bmad-build/workflow.md), [project-context skill](https://github.com/bmad-code-org/BMAD-METHOD/blob/e435a22574fe55722841086e5566420178b98df3/skills/method/bmad-project-context/SKILL.md). 기준 ref: `e435a22574fe55722841086e5566420178b98df3` (main, 확인 Nov 16). **근거 상태: documented + source_inspected.**

## 5. BATHOS — wave·역할·gate를 묶는 AI 개발팀 오케스트레이션

- **문맥:** 넓은 코드 변경에서 제품 발견부터 구현·검증까지 여러 역할/작업을 단계별로 조율해야 하는 경우.
- **기능 1 — scale-adaptive waves:** 프로젝트 문서상 입력 규모/새로움/규제/팀 조건에 따라 분석·발견·설계·story gate·구현·검증 wave를 선택하고, manifest에서 수준과 사용자 확인을 관리한다. 구현/검토 역할을 여러 에이전트로 나누며 동시성은 상한을 둔다.
- **기능 2 — gate/audit/session:** README와 architecture 문서는 Rust engine의 manifest/state·wave·gate·audit chain, hook 연결, 세션 복구를 설명한다. 실제 `gate-enforce.sh`와 Codex `pretooluse-gate.sh`는 구현 wave 진입 시도와 현재 verdict를 읽어 조건을 판정한다.
- **실제 gate 경계:** Claude hook은 구현 진입으로 감지하지 못하면 바로 통과한다. Codex hook도 설정된 도구 이름/경로/웨이브 진입 pattern을 trigger로 쓴다. 두 hook 모두 verdict를 읽지 못하면 경고 후 통과하며, 알 수 없는 verdict 값도 통과한다. 그래서 `FAIL` 차단은 해당 trigger와 verdict를 정확히 읽었을 때의 조건부 enforcement다. 정상 경로의 `FAIL`은 exit code 2로 막고, `PASS`/`CONCERNS`는 진행을 허용한다.
- **보장/한계:** hook 소스에서 위 조건과 exit code를 확인했지만 실행하지 않았다. Rust engine 내부의 manifest validation/audit chain은 README/architecture 문서로 확인했고 source/test 실행은 하지 않았다. README는 early/dogfood maturity를 밝힌다. 저장소에 Codex adapter hook이 있으나 portability 문서는 runtime glue 재설계와 live verification을 별도 단계로 설명하므로 Codex Cloud 호환성은 확인되지 않았다.
- **작은 예:** 작은 가짜 기능의 규모를 입력 → 낮은 complexity wave 선택 → story gate에 `FAIL`이 있는 manifest를 준비하고 이름이 trigger에 잡히는 구현 진입을 시도하면 exit 2를 기대한다. verdict를 제거한 경우에는 경고 후 통과한다. 실행은 후속 실증으로 남긴다. **상태: documented + source_inspected(hooks) + self_reported(engine claims); not_run.**
- **비용/제약:** README 기준 Claude Code 2.1.32+ 및 실험적 Agent Teams 의존, 역할·wave가 늘면 모델 사용량도 증가. 프로젝트 보고 테스트는 이 조사에서 재실행하지 않았다.
- **재사용 힌트:** 복잡도에 따라 의식적으로 workflow 폭을 줄이고, 앞 단계의 acceptance gate를 후속 실행의 명시적 조건으로 잇는 구상.
- **근거:** [공식 README](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/README.md), [Architecture](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/docs/ARCHITECTURE-en.md), [Claude gate hook](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/.claude/hooks/gate-enforce.sh), [Codex pre-tool hook](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/codex-adapter/hooks/pretooluse-gate.sh), [Portability note](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/docs/PORTABILITY-kr.md). prod ref `9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd`, 확인 Nov 16. **근거 상태: documented + source_inspected(hooks) + self_reported(engine claims); no execution.**

## 6. LangGraph — state graph의 checkpoint와 interrupt

- **문맥:** 여러 단계의 agent/program 흐름 중간에 중단·대기·분기하고 같은 실행 state로 이어가야 하는 응용.
- **기능 1 — checkpoint/persistence:** X = graph state + `thread_id`; 매 super-step의 state/metadata가 checkpointer에 저장되어 그 thread의 작업 상태로 복원된다. Store는 별도로 thread 간 application data를 저장한다.
- **기능 2 — human interrupt:** node 안의 `interrupt(payload)`가 실행을 멈추고 payload를 외부에 노출한다. 같은 graph/checkpointer와 같은 `thread_id`에서 `Command(resume=value)`로 진행한다.
- **메커니즘/보장:** 저장소 구현이 체크포인트 데이터를 제공하는 범위에서 state 복구와 resume 연결이 된다. `InMemorySaver`는 프로세스 종료 후 durable하지 않으며 production에는 영속 checkpointer가 필요하다. 중단 지점이 side effect를 실행하지 않도록 배치해야 하고, 재실행/중복 효과의 멱등성은 graph 코드가 담당한다.
- **작은 예:** 가짜 workflow: 입력 검증 node → `interrupt({"action": "send-preview", ...})` → 승인 후 같은 thread 재개 → 출력 기록. 승인 도중 thread ID/저장소를 바꾸면 이전 checkpoint와 연결되지 않는다. **상태: documented; not_run.**
- **비용/제약:** persistent backend 운영, checkpoint 저장/정리, thread 식별자 관리가 필요하다. checkpoint는 사용자 장기기억이 아니며 Store의 선택/갱신 로직도 application 책임이다.
- **재사용 힌트:** 대화 요약이 아니라 실행 state의 경계에서 실제 중단과 복구를 표현하는 방식.
- **근거:** [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers). official docs, 확인 Nov 16. **근거 상태: documented.**

## 7. OpenAI Agents SDK — handoff, session, 승인이 붙은 도구 실행

- **문맥:** 대화 에이전트가 다른 전문 에이전트나 외부 도구로 작업을 넘기고, 승인·실행 내역을 연결해야 하는 경우.
- **기능 1 — handoff와 input filter:** 에이전트의 handoff는 모델이 호출하는 `transfer_to_<agent>` 도구다. target, handoff metadata, 다음 agent에게 전달할 history filter를 지정할 수 있다. 기본은 전체 대화 이력이며 filter가 선택한 입력으로 handoff한다.
- **기능 2 — needs_approval/RunState:** 도구를 승인 필요로 설정하면 run이 interruption 상태가 된다. 직렬화 가능한 `RunState`를 저장해 승인/거절 후 재개할 수 있다. 같은 session 또는 같은 session ID와 같은 저장 backend로 이어갈 수 있다.
- **기능 3 — sessions/tracing:** 세션 구현은 여러 run에 걸쳐 대화 내역을 저장한다. trace에는 model/tool/handoff/guardrail/custom span이 남아 실행을 관찰할 수 있다.
- **보장/경계:** SDK가 승인 상태/재개 구조를 관리하고, 안전하게 인자를 판단할 수 없는 상황은 fail closed한다고 문서화한다. 이는 도구 정책이 전체 외부 side-effect에 완전 매개됐음을 증명하지 않는다. session history는 semantic profile/memory와 다르다. ZDR 조직에서는 tracing이 제공되지 않는다.
- **작은 예:** `needs_approval=True`인 가짜 `send_email` 도구 호출 → serialized RunState 보관 → 사람이 승인 → 같은 state/session으로 재개하고 trace 확인. 모델 API에 연결해 실행하지 않았다. **상태: documented + source_inspected(docs); not_run.**
- **비용/제약:** compatible model provider, session store, approval UI/운영자가 필요. 실제 model call은 비용/자격 증명이 필요할 수 있어 이번 조사에서 하지 않았다.
- **재사용 힌트:** 승인 대상을 도구 호출 단위로 표시해 run을 pause/resume하며, handoff에 꼭 필요한 정보만 필터링하는 방식.
- **근거:** [Human in the loop](https://openai.github.io/openai-agents-python/human_in_the_loop/), [Handoffs](https://openai.github.io/openai-agents-python/handoffs/), [Sessions](https://openai.github.io/openai-agents-python/sessions/), [Tracing](https://openai.github.io/openai-agents-python/tracing/), [docs/human_in_the_loop.md](https://github.com/openai/openai-agents-python/blob/64fbde5d02b42ae5f9db668eb0184cdb3fc9d775/docs/human_in_the_loop.md). 기준 ref: `64fbde5d02b42ae5f9db668eb0184cdb3fc9d775` (main, 확인 Nov 16). **근거 상태: documented + source_inspected(docs).**

## 8. Letta — Git 기반 파일 기억과 얕은/깊은 문맥 계층

- **문맥:** 여러 대화에 걸쳐 지속할 작업 규칙·사용자 선호·프로젝트 사실을 유지하면서 현재 system prompt에 넣는 문맥은 작게 하고 싶은 경우.
- **기능 1 — MemFS:** 각 agent의 memory가 Git repository이고, 일반 파일 도구로 읽고 쓰는 실제 checkout으로 보인다. commit/push 뒤 다른 Cloud computer의 projection에 동기화되며, local-only agent는 사용자가 backup해야 한다.
- **기능 2 — 기억의 계층:** root memory 파일은 매 turn system prompt에 실리고, 하위 directory는 `MEMORY.md` index가 필요할 때 찾아가는 구조다. `/init`, `/remember`, `/memory`, `/doctor`가 점검·기록 흐름을 제공한다.
- **기능 3 — dreaming:** 설정한 step 수 또는 context compaction에 background subagent가 최근 대화를 요약·통합해 기억 갱신을 제안할 수 있다. 선택형 agent review도 별도 background conversation이며 사용자 승인을 요청하지 않는다.
- **보장/경계:** Git commit은 version history와 저장된 상태의 경계를 제공한다. 반면 모델이 올바른 사실을 기억으로 남기고 적절한 파일을 선택하는 일은 agent의 판단이다. 기본 MemFS는 semantic/vector index를 포함하지 않는다. 문서상 cloud 저장량은 Free 5 MiB, Pro 50 MiB/repository.
- **작은 예:** `human.md`에 가짜 preference를 기록 → commit → 이후 agent 환경에서 파일이 보이는지 확인. `/doctor`는 중복/배치/system-prompt 토큰을 감사하는 흐름이다. **상태: documented + source_inspected; not_run.**
- **비용/제약:** agent별 memory repo; cloud storage quota; local agent의 백업은 사용자 책임. Dreaming과 agent review에는 추가 model token이 든다. background review는 human approval과 동일하지 않다.
- **재사용 힌트:** 자주 쓰는 얕은 기억을 prompt에 상주시켜 두고 나머지는 index를 통한 탐색으로 지연 로드하며, 변경에 Git history를 쓰는 방식.
- **근거:** [Memory & dreaming](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/configuration/memory/index.md), [MemFS](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/concepts/memfs/index.md). 기준 docs ref: `8fd860b127981c36e1c4d2d5c0cfb515c0a33331` (main, 확인 Nov 16). **근거 상태: documented + source_inspected(docs).**

## 9. Mem0 — scoped memory 추출·중복 억제·명시적 갱신

- **문맥:** 대화에서 재사용 가치가 있는 사실을 분리 저장하고 user/agent/run 단위로 검색·수정해야 하는 응용.
- **기능 1 — add:** X = 문자열 또는 message 배열 + 최소 하나의 `user_id`/`agent_id`/`run_id` + metadata/expiration; 기본 `infer=True`에서는 embedding 검색으로 기존 기억 일부를 찾고 LLM 추출을 거쳐 신규 memory 후보를 만든다. 현재 OSS 구현은 기존 결과와 hash를 대조하고 새 `ADD` record를 넣는다. `infer=False`는 system 메시지를 건너뛰고 입력 메시지 텍스트를 raw memory로 추가한다.
- **기능 2 — search/update/delete:** 검색 결과는 ID/본문/score를 돌려준다. 사람이 선택한 `memory_id`로 명시적 update를 하고 필요하면 검색으로 확인할 수 있다. 별도의 delete API는 ID, ID 목록, 또는 scope/filter 기준 삭제를 지원한다. expiration date가 지난 항목은 기본 search/get_all에서 숨기지만 ID로 읽는 동작은 다르다.
- **문서와 소스의 구분:** 현재 add 가이드는 additive storage라고 설명한다. Python `Memory.add` docstring에는 LLM이 add/update/delete를 결정한다고 남아 있지만, 같은 pinned `main.py`의 활성 V3 pipeline은 `ADDITIVE_EXTRACTION_PROMPT`, hash 중복 제거와 신규 `insert`를 수행하며 기존 기억 update/delete 호출은 이 add 경로에 없다. 여기서는 문서의 “additive”와 확인된 구현을 기준으로 하고, 함수 docstring과 설명의 차이를 명시적 버전/변경 검토 항목으로 남긴다. 별도 `update()`는 선택한 ID의 내용을 덮어쓴다.
- **보장/경계:** scope ID 필수, 형식 검증, 중복 hash skip, 명시적 ID update/delete 등은 구현에서 확인된다. 추출되는 사실, query의 관련도, memory freshness는 LLM/embedding/ranker에 의존한다. Hash dedup은 의미가 같은 문장을 모두 잡는 보장이 아니다. OSS SDK를 실사용하려면 storage와 model/embedding provider 설정이 필요하다.
- **작은 예:** 가짜 user ID에 선호 대화를 `add` → result memory ID 확인 → 선호 변경을 명시적 `update(memory_id, text=...)`로 저장 → search로 최신 표현 확인. 이 SDK 호출은 provider를 사용하므로 실행하지 않았다. **상태: documented + source_inspected; not_run.**
- **비용/제약:** OSS는 관리형 인프라가 아니며 개발자가 backend·LLM·embedding 구성을 책임진다. Platform API는 외부 호출/요금이 발생할 수 있어 사용하지 않았다. `infer=False`와 `infer=True` 혼용은 중복 저장을 유발할 수 있다는 공식 주의가 있다.
- **재사용 힌트:** 기억의 scope를 명시하고, 기록과 명시적 교정을 분리해 수정 대상을 ID로 좁히며, 결과를 후속 검색으로 재확인하는 방식.
- **근거:** [Add Memory](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/add.mdx), [Update Memory](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/update.mdx), [Delete Memory](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/delete.mdx), [main.py](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py). 기준 ref: `f1791daa86d469249c9b002f62644d58a1eb96a0` (main, 확인 Nov 16). **근거 상태: documented + source_inspected.**

## 10. GitHub Actions + protected branch — 테스트 결과와 리뷰를 병합 조건에 연결

- **문맥:** 자동 검사와 사람 리뷰가 PR마다 수행되고, 조건이 안 맞으면 지정 branch 병합을 막아야 하는 repository 운영.
- **기능 1 — workflow:** 입력 = `.github/workflows/*.yml` + repository event/수동/스케줄; 처리 = runner에서 job/step 실행; 결과 = commit 또는 PR에 check/status가 연결된다. 여러 workflow/job으로 build, test 등을 나눌 수 있다.
- **기능 2 — required checks/reviews:** repository 관리자가 보호 규칙에서 지정 status와 승인 수를 설정하면 해당 조건이 성공/승인 상태가 될 때까지 보호 branch 병합을 막는다. stale approval, 최근 push 승인, status source 앱 고정 등 옵션이 있다.
- **기계적 보장:** branch 보호가 적용되고 bypass가 허용되지 않는 구성에서는 지정된 check/review 상태가 없을 때 merge가 막힌다. required check가 성공했다고 코드가 안전하거나 검사의 범위가 충분하다는 뜻은 아니다. 체크를 skip/neutral/success 처리 가능한 정책과 직접 status를 쓸 수 있는 identity의 신뢰도도 확인해야 한다.
- **작은 예:** PR에서 unit test workflow 실행 → `unit-tests`를 required status로 등록 → 실패/미완료이면 merge disabled; 적정 승인 수가 충족되면 병합 가능. 이 repository의 보호 규칙 설정값은 이번 기술 기능 조사 범위에서 읽지 않았다. **상태: documented; not_run.**
- **비용/제약:** runner 실행 시간/동시성/권한/secret 관리 및 branch protection의 관리자 설정이 필요하다. public repo 여부/플랜 등에 따라 보호 규칙 사용 가능성이 다르다.
- **재사용 힌트:** 의미 해석이 필요한 agent 판단과 확정적 merge 조건을 분리하고, 실제로 통제하고 싶은 저장 경계에 hard gate를 둔다.
- **근거:** [GitHub Actions workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows), [Managing protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches), [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). 공식 문서, 확인 Nov 16. **근거 상태: documented.**
