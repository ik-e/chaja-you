# 공통 원리와 재사용 가능한 조합

- 조사 기준일: 2026-11-16 (KST)
- 목적: 현재 기술에서 이미 확인한 작동 방식을 분리해 적는다. 아래는 구현 지시나 신규 제품 주장으로 보지 않는다.

## 재사용 가치가 큰 기술 원리 5개

### 1. 의도 문서, 실행 작업, 완료 검토를 서로 연결된 별도 산출물로 둔다

OpenSpec은 proposal/spec delta/tasks와 기준 spec을 분리하고, Spec Kit은 spec→plan→tasks→implement→converge의 연결을 둔다. 이 구조에서는 새 조건을 코드에 바로 섞기 전에 바뀐 요구와 남아 있는 일을 확인할 수 있다.

- **실제 입력→출력:** 자연어 변경 + 기존 artifact → 새 proposal/spec delta/작업 목록 → 구현 뒤 검토 artifact.
- **보장:** 파일 경로와 템플릿, 일부 구조 검증, checkbox는 도구가 고정할 수 있다.
- **남는 판단:** 요구가 충분한지, 코드가 의도와 맞는지, 요구되지 않은 범위가 바뀌었는지는 모델/사람 리뷰에 남는다.
- **적합한 조합:** OpenSpec 또는 Spec Kit의 계획 문서 + GitHub PR/Actions. 같은 단계에 서로 다른 명세 프레임워크를 중복 설치할 필요는 없다.
- **근거:** [OpenSpec workflows](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/docs/workflows.md), [Spec Kit quickstart](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/quickstart.md).

### 2. “실행 상태”와 “장기 문맥”은 서로 다른 저장 수명으로 관리한다

LangGraph checkpoint는 한 `thread_id`의 실행 state를 복구하는 데 쓰고, Store는 thread를 넘는 app data를 둘 수 있다. Agents SDK session은 대화 내역을 이어주고, 승인 대기 중에는 RunState를 직렬화해 재개할 수 있다. Codex Cloud도 원 task의 workspace를 새 task와 분리한다. Letta/Mem0는 프로젝트/사용자 기억을 별도 저장한다.

- **재사용 포인트:** 저장 단위에 소유자·thread/task scope·만료·재개 키를 명시한다. 작업을 이어갈 state와 사용자가 장기간 기억하길 바라는 사실을 같은 저장소로 가정하지 않는다.
- **한계:** 지속 상태가 있다고 side effect가 exactly-once가 되는 것은 아니다. 재실행에 대비해 idempotency key나 중복 방지 규칙이 별도로 필요하다.
- **적합한 조합:** LangGraph 또는 Agents SDK 하나의 execution runtime + Letta/Mem0 등 별도의 memory 계층. 이 경계는 통합 동작을 이번 조사에서 검증한 것은 아니다.
- **근거:** [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Agents SDK sessions](https://openai.github.io/openai-agents-python/sessions/), [Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud).

### 3. 필요 문맥을 scope와 index로 찾아 현재 입력에 넣는다

ChatGPT Projects는 관련 파일/채팅/지시를 프로젝트 공간 안에 둔다. Letta MemFS는 상위 기억 일부를 매 turn 포함하고 깊은 디렉터리는 index를 거쳐 필요 시 읽는다. Mem0는 `user_id`/`agent_id`/`run_id` 범위로 기록/검색 대상을 한정한다.

- **입력→결과:** project/thread/user/agent 식별자 + query → 허용 범위 내 파일·검색 결과를 현재 reasoning에 제공.
- **보장/한계:** scope·경로·ID와 일부 기계적 필터는 설정할 수 있다. context가 “적절한 것만” 검색되는지, 충돌하는 두 결정 중 어느 것이 최신인지의 보장은 따로 없다.
- **적합한 조합:** 프로젝트 지시는 작업 규칙에, 검색 가능한 기억은 ID가 있는 기록에 사용하고 각각 최신 날짜·출처·유효 범위를 갖게 한다.
- **근거:** [ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt), [Letta MemFS](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/concepts/memfs/index.md), [Mem0 add](https://github.com/mem0ai/mem0/blob/1c44857758d972c58754ed6352217158a4f15204/docs/core-concepts/memory-operations/add.mdx).

### 4. 사람 승인·에이전트 판단과 실제 side-effect/merge gate를 분리한다

LangGraph `interrupt`와 Agents SDK의 `needs_approval`은 실행 상태를 pause/resume한다. GitHub required status/review는 repository 병합 조건을 강제할 수 있다. BATHOS는 hook/gate가 구현 wave를 막는다고 설명하지만 그 주장은 이 조사에서 source execution으로 재검증하지 않았다.

- **재사용 포인트:** 승인 대상을 정확히 식별하고(`tool`, `memory update`, `merge` 등), 승인 당시 입력을 고정하며, 승인 전 side-effect를 시작하지 않는다. 최종 병합은 사람/agent의 말뿐 아니라 실제 branch 보호 규칙으로 막는다.
- **보장/한계:** runtime이 승인 상태를 알고 있어도 그 runtime을 우회하는 다른 경로까지 차단하지 않을 수 있다. GitHub gate는 지정한 status/review의 부재를 막지만 검사의 정확성을 대신하지 않는다.
- **적합한 조합:** SDK 승인 요청 + GitHub protected-branch rule. 사용자 승인이 없는 공개 PR 작성 또는 자동 merge는 별도 정책이 필요하며 이번 조사에서 설정하지 않았다.
- **근거:** [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Agents SDK human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/), [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

### 5. 변경된 기억을 식별·교정·버전 이력으로 확인한다

Letta MemFS는 memory file 변경을 Git commit으로 남긴다. Mem0는 `add` 결과에 memory ID를 주고, 명시적 `update`/`delete` 및 history를 제공한다. 문서의 update 절차는 기존 ID를 찾고 고친 뒤 search로 확인한다.

- **재사용 포인트:** 기억 단위 ID/경로, 생성·수정 주체/시각, 수정 전에 읽을 원본, 후속 검색 확인을 묶는다. 이 구조는 오래된 선호를 조용히 덮어쓰는 문제를 보이게 한다.
- **보장/한계:** Git history 또는 memory operation history는 무엇을 저장했는지를 보존하지만, 저장 내용이 사실인지 증명하지 않는다. Mem0의 자동 추출은 LLM에 의존하고 hash 기반 dedup은 의미상 동등한 사실을 전부 통합하지 않는다.
- **적합한 조합:** 파일 중심 작업 기억은 MemFS; 검색·ID 기반 사실 기억은 Mem0 같은 memory API를 사용할 수 있다. storage 정책과 사용자 동의는 도입 환경에서 따로 검토해야 한다.
- **근거:** [Letta MemFS](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/concepts/memfs/index.md), [Mem0 update](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/update.mdx), [Mem0 source](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py).

## 기존 기술 조합으로 가능한 사례

| 사례 | 기존 기능 조합 | 결과와 경계 |
|---|---|---|
| 새 요구가 들어왔을 때 변경/유지 작업 구분 | OpenSpec의 spec delta + tasks + Git diff/PR | 바뀐 artifact와 작업 목록은 비교 가능하다. 자동으로 완벽한 영향 분석을 보장하지는 않는다. |
| 승인 대기 중인 위험 행동을 나중에 재개 | LangGraph interrupt 또는 Agents SDK approval + 저장형 state/session | 중단·재개 상태는 관리한다. side effect idempotency와 외부 시스템 정책은 별도다. |
| 장기 선호를 교정하고 이후 검색 확인 | Letta memory file/commit 또는 Mem0 memory ID/update/search | 저장 이력과 결과 확인이 가능하다. 기억 추출/관련도는 model-dependent다. |
| 지정 테스트/리뷰 전 병합을 막음 | GitHub Actions + protected branch required checks/reviews | 설정한 merge 조건을 강제할 수 있다. 현재 저장소의 보호 설정 여부는 본 조사에서 판단하지 않았다. |

## 별도 가설로 남기는 것

어떤 조합이 R01의 타겟 사용자에게 가장 큰 비용 감소를 주는지, 과거 결정의 만료/범위 변경이 실제로 얼마나 자주 문제를 만드는지, 자동 기억 수정에 어떤 승인 수준을 원하는지는 사용자 인터뷰와 후속 비교 실증이 필요하다. 기존 기능을 확인한 것만으로 시장 차별성이나 제품 기회를 주장하지 않는다.
