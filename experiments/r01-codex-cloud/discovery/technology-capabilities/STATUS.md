# 기존 기술 해결 능력 조사 상태

- 조사일: 2026-11-16 (KST)
- 저장소: `ik-e/chaja-you`
- 브랜치: `experiment/r01-codex-cloud-20261114`
- 조사 목적: 기존 기술이 해결하는 작업, 실제 입력·출력·메커니즘, 구현 보장과 한계를 파악한다. 신규 제품/사용자 고통 주장은 이번 작업 범위가 아니다.

## 산출물 상태

| 파일 | 상태 | 범위 |
|---|---|---|
| `01-capability-map.md` | 작성 완료 | 제품/명세/SDK/기억/CI의 능력과 미제공·미확인 구분 |
| `02-technology-cards.md` | 작성 완료 | 10개 기술군, 기능·X/E/C→Y·보장·한계·공식 1차 근거 |
| `03-patterns-and-reuse.md` | 작성 완료 | 재사용 원리 5개, 기존 기능 조합과 검증되지 않은 가설 |
| `04-demo-candidates.md` | 작성 완료 | synthetic data 기반 소형 데모 3개, 성공/실패 조건과 부담 |
| `STATUS.md` | 작성 완료 | 이 조사 상태와 출처/결정 사항 |

## 수행 상태

| 작업 | 상태 | 증거 |
|---|---|---|
| Cloud 환경 확인 | `passed` | 관리형 환경 `provider=cloud`, `observed_phase=running`, `connectivity=connected`; 환경 상태 관측은 2026-11-16 10:41 KST |
| 저장소/브랜치 확인 | `passed` | `/workspace/chaja-you`, branch `experiment/r01-codex-cloud-20261114`, 시작 HEAD `2265771ba0b65a296c17530c9c27b56a9714976d` |
| 지시서 및 선행 R01 자료 검토 | `passed` | 기술 조사 지시서, R4/R1 맥락, 기존 대안 조사와 문제 트리 자료를 확인. 기존 사용자 페인포인트 목록은 반복하지 않음 |
| 공식 문서/소스 열람 | `passed` | 아래 출처 목록; 날짜는 2026-11-16 KST |
| 신규 기술 설치·실행 | `not_run` | BMad/OpenSpec/Spec Kit/BATHOS/SDK를 설치하거나 데모 실행하지 않음 |
| 외부 API/model 호출 | `not_run` | 계정·비밀키·유료 API 사용 안 함 |
| 테스트 및 사용자 실증 | `not_run` | 데모 설계만 작성. synthetic data 이외의 실제 데이터나 사용자 접촉 없음 |
| 제품 구현 | `not_run` | 구현/아키텍처 작업 없음 |
| 외부 발송/공식 팀 산출물 변경 | `not_run` | 하지 않음 |
| 문서 diff 점검 | `passed` | 산출물 4개를 stage한 뒤 `git diff --cached --check` 통과. STATUS도 별도 stage 후 같은 점검 예정. |
| Commit | `passed` | 핵심 조사 산출물 4개 commit: `6dc7259b8c8f205ea89236cd02751ef955d5bfe0`. 이 STATUS는 후속 commit에서 커밋/검토 상태를 기록. |
| Push | 완료 보고에서 검증 | STATUS 포함 commit이 만들어진 뒤 원격 branch HEAD를 확인해 최종 보고에 남긴다. 이 줄은 push 성공을 미리 주장하지 않는다. |

## 출처와 조사 범위

| 기술 | 열람한 공식 1차 출처 / 버전 | 직접 확인한 주장과 미확인 |
|---|---|---|
| ChatGPT Projects / Codex Cloud | [Projects 도움말](https://help.openai.com/en/articles/10169521-projects-in-chatgpt), [Codex Cloud 도움말](https://help.openai.com/en/articles/20001545-using-codex-cloud); 문서 페이지, 2026-11-16 확인 | 프로젝트 단위 문맥과 원 task 실행 환경 보존을 구분. 실제 계정의 모든 플랜 옵션을 검증하지 않음. |
| OpenSpec | [workflows](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/docs/workflows.md), [archive](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/archive.ts), [specs apply](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/specs-apply.ts), [validator](https://github.com/Fission-AI/OpenSpec/blob/ea635dd255f8686dcf48626bbcbe0e3fd59b6067/src/core/validation/validator.ts); `ea635dd255f8686dcf48626bbcbe0e3fd59b6067` | schema/artifact workflow와 archive gate/validator를 문서와 source에서 대조. CLI 실행은 안 함. |
| GitHub Spec Kit | [quickstart](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/quickstart.md), [agentic SDD](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/reference/agentic-sdd.md), [spec template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/spec-template.md), [plan template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/plan-template.md); `2ee2b1e8005905db05f5717300a469b3068b908f` | 설치/skill 호출 단계와 active feature 포인터, 템플릿 검토. agent workflow 미실행. |
| BMad | [bmad-build workflow](https://github.com/bmad-code-org/BMAD-METHOD/blob/e435a22574fe55722841086e5566420178b98df3/skills/method/bmad-build/workflow.md), [project-context skill](https://github.com/bmad-code-org/BMAD-METHOD/blob/e435a22574fe55722841086e5566420178b98df3/skills/method/bmad-project-context/SKILL.md); `e435a22574fe55722841086e5566420178b98df3` | 계획 readiness 추천과 repo 컨텍스트 승인 지침 열람. workflow를 실행하지 않음. |
| BATHOS | [README](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/README.md), [Architecture](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/docs/ARCHITECTURE-en.md), [Claude gate hook](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/.claude/hooks/gate-enforce.sh), [Codex gate hook](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/codex-adapter/hooks/pretooluse-gate.sh), [Portability note](https://github.com/taxideftis/bathos/blob/9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd/docs/PORTABILITY-kr.md); `prod` ref `9e2433cf6fe39d0bc84ccd1b62db1b91b7ec65dd` | hook 소스는 열람했지만 실행하지 않음. FAIL gate는 조건부이고 verdict 부재/불명은 fail-open. Rust engine 세부와 Codex Cloud 호환은 검증하지 않음. |
| LangGraph | [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers); official docs, 확인 Nov 16 | thread checkpoint, Store, interrupt/resume 조건. graph/checkpointer 실행 안 함. |
| OpenAI Agents SDK | [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/), [handoffs](https://openai.github.io/openai-agents-python/handoffs/), [sessions](https://openai.github.io/openai-agents-python/sessions/), [tracing](https://openai.github.io/openai-agents-python/tracing/), [HITL source docs](https://github.com/openai/openai-agents-python/blob/64fbde5d02b42ae5f9db668eb0184cdb3fc9d775/docs/human_in_the_loop.md); `64fbde5d02b42ae5f9db668eb0184cdb3fc9d775` | API 문서의 handoff/session/approval/state 구조 읽음. model/provider API 요청은 하지 않음. |
| Letta | [memory & dreaming](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/configuration/memory/index.md), [MemFS](https://github.com/letta-ai/letta-docs-md/blob/8fd860b127981c36e1c4d2d5c0cfb515c0a33331/concepts/memfs/index.md); docs commit `8fd860b127981c36e1c4d2d5c0cfb515c0a33331` | Git-backed storage, hierarchy, dream/review 조건, quota, semantic search 기본 미포함. Letta runtime은 실행 안 함. |
| Mem0 | [add](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/add.mdx), [update](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/update.mdx), [delete](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/docs/core-concepts/memory-operations/delete.mdx), [main.py](https://github.com/mem0ai/mem0/blob/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py); `f1791daa86d469249c9b002f62644d58a1eb96a0` | 문서와 Python add path의 additive/dedup 동작을 비교. docstring에 남은 add/update/delete 문구와 active code 차이를 기록; SDK 실행 안 함. |
| GitHub Actions/protection | [Workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows), [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches), [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches); 문서 페이지, 2026-11-16 확인 | workflow와 configured merge gate의 동작. 이 실험 branch/repo의 현재 branch protection 설정은 확인하지 않음. |

## 미확인 및 한계

- 이 조사는 문서와 일부 source/code template을 읽은 정적 조사다. 구현 결과, UX, 품질, 테스트 통과, 사용자 효용을 직접 측정하지 않았다.
- BATHOS의 README/architecture가 설명하는 Rust engine 보장과 테스트 수는 프로젝트 문서 보고다. 실제 gate hooks는 소스 확인했지만 실행하지 않았으며, gate는 verdict 부재/오류 가능 상태에서 fail-open이라 hard barrier를 일반화하지 않았다. Codex adapter hook 파일이 있지만 Codex Cloud live compatibility는 검증하지 않았다.
- Cloud 제품의 계정/플랜별 기능, SDK의 현재 요금·모델 제공자 비용, GitHub 저장소 설정값은 이번 문서 범위에서 조회하지 않았다.
- Mem0 add 문서는 additive라고 설명하고 OSS source는 hash 기반 중복 skip/new insert를 수행하지만 함수 docstring은 add/update/delete 판단을 말한다. 실제 update는 별도 ID API를 통해 명시하는 것으로 카드에서 설명했다. 더 최신 버전에서의 문구/행동 일치는 후속 실행에서 확인해야 한다.
- 문서에 기록한 “구현 보장”은 확인한 소스 범위의 동작이다. 특정 저장 backend, 운영 설정, 외부 서비스 통합 전체에 대한 종단 보증은 아니다.

## 다음 R01 판단 사항

1. 후속 실증을 명세 변화 추적(A), 승인 후 재개(B), 기억 교정(C) 가운데 무엇부터 할지 선택한다.
2. 기존 기술 단독 데모에서 확인할 관찰 기준(추적 가능성, side-effect 차단, 최신 기억 선택)을 구체화한다.
3. provider 호출이 필요한 경우 무료/local 방식 가능 여부와 별도 실행 승인 범위를 정한다. 본 조사에서는 유료/외부 API를 호출하지 않았다.

## Commit / push

- 산출물 커밋: `pending`
- 최종 branch HEAD: `pending`
- 원격 push 확인: `pending`
