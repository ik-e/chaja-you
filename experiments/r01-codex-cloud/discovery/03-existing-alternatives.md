# 03 — 기존 대안과 사건별 잔여 문제

- 확인일: 2026-11-16 (KST)
- 원칙: 공식 문서에 기능이 있다는 사실은 실제 사용자 고통이 해소됐다는 증거가 아니다. 반대로 공개 이슈 한 건은 제품 전체가 문제를 해결하지 못한다는 증거가 아니다.

## 대안 비교

| 대안 | 현재 제공되는 부분 | 실제 사용자 방식/보고 | 증거가 남긴 질문 |
|---|---|---|---|
| BATHOS | 역할 기반 에이전트와 여러 작업 단계, readiness/hard gate, 리뷰·이력·세션 복구를 제공한다고 프로젝트가 문서화. v0.4.0은 early/dogfood 상태이며 외부 파일럿 전이라고 FAQ가 밝힘. 사용량 안내는 multi-agent flow의 토큰/쿼터 비용을 경고 | #39 사용자는 safe Git branch 명령이 차단돼 switch -c로 바꾸고 삭제에서 -D가 안내됐다고 보고 | 오탐이 현재 버전에서 해결됐는지 unknown. 여러 역할/게이트가 이 사례에서 필요했는지와 총 비용도 미검증 |
| BMad Method | 역할별 분석·기획·개발/검토 workflow, 결정·프로젝트 context 유지, 작업 규모에 따른 프로세스 조절을 공식 README가 설명 | #3194 사용자는 BMad 6.12.1 + Claude Code headless에서 endpoint 하나 요청이 광범위한 sweep과 quota 소진으로 커졌다고 보고 | 보고는 특정 headless 모드·설정의 단일 사건. 잘 설정된 대화형/범위 제한 workflow에서 반복되는지, 최신 버전에서 달라졌는지 unknown |
| OpenSpec | proposal/spec/design/tasks, delta 변경, validate/archive, 팀 PR/workflow, Store/workset을 제공. 결정과 변경 기록을 남기며 일부 누락을 늦게라도 막음 | #725: Store/workset으로 계획·저장소 접근은 도울 수 있지만 maintainer는 repo target 자동 분배나 per-repo edit bound를 제공하지 않는다고 설명. 사용자는 수동 task/repo 지정 또는 각 repo의 local root/별도 변경을 선택. #1112/#1669의 archive guard는 일부 손실을 막지만 시점이 늦거나 열린 변경 간 충돌은 놓침. #1697은 rename 오탐 guard를 보고 | 특정 버전 동작인지, 현행 릴리스의 coverage와 사용자의 실제 우회 비용은 unknown. guard로 막은 손실과 오탐의 균형은 사용 사례별 검증이 필요 |
| 강한 Codex/ChatGPT 프로젝트 지침 | Codex prompting guide는 CWD의 AGENTS.md 지침을 계층적으로 읽어 프로젝트 규칙을 전달. ChatGPT Projects는 프로젝트별 채팅·파일·지침 및 project memory를 제공. 문서/대화/판단을 다시 찾기 쉽게 함 | Codex #16911에서 사용자는 MCP의 Allow always 뒤에도 반복 승인 프롬프트를 보고. BMad #3194도 caller brief의 scope가 headless workflow의 필수 범위를 제한하지 못했다고 보고 | 지침과 context는 기본 반복 설명을 줄일 수 있으나 실제 도구 승인 scope의 지속성이나 변경 뒤 어느 결정만 무효화할지를 자동 판정한다는 근거는 아님 |
| 수동 checklist/저장소별 작업 | 각 repo/작업에 범위를 직접 지정하고 완료 여부를 직접 확인할 수 있음. 도구 설치 없이 적용 가능 | OpenSpec #725 maintainer는 현시점 수동 target/repo 지시가 가능한 모델이라고 설명. #1112 댓글 사용자는 프로젝트 local blocked_by gate를 별도로 구축 | 수작업 시간·유지비는 측정되지 않음. 소규모 변경에서는 새 도구보다 checklist가 더 나은 대안일 수 있음 |

## 공식 자료

- [BATHOS README](https://github.com/taxideftis/bathos/blob/prod/README.md), [FAQ](https://github.com/taxideftis/bathos/blob/prod/docs/FAQ-en.md), [quota 안내](https://github.com/taxideftis/bathos/blob/prod/docs/QUOTA-en.md): 프로젝트 제공 기능·성숙도·사용량 주의. 자체 문서이며 외부 효능 검증은 아님.
- [BMad Method README](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/README.md): 현재 stable/v6과 개발 중 v7 구분, 역할·context·right-sized process 설명.
- [OpenSpec team workflow](https://github.com/Fission-AI/OpenSpec/blob/main/docs/team-workflow.md), [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md): 변경 산출물과 팀 사용 흐름. [#725 maintainer 설명](https://github.com/Fission-AI/OpenSpec/issues/725#issuecomment-5573214645)은 Stores/workset이 계획을 중앙화해도 repo task를 나누거나 edit permission을 강제하지 않는다고 명시.
- [Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide), [ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt), [Memory FAQ](https://help.openai.com/en/articles/8590148-memory-in-chatgpt): 프로젝트 instruction/context를 전달하는 현재 대안. 이 문서들은 승인 정책의 자동 범위 재평가를 주장하지 않음.

## 사건별 잔여 대조

1. **여러 repo 적용**: OpenSpec Store/workset은 중앙 계획과 context에 도움. 실제 보고에서 남은 것은 수동 repo/task 라우팅, 권한이 나뉜 적용, 모든 repo가 성공했는지 확인하는 일. 잔여 문제의 일반 빈도는 미확인.
2. **검증/guard**: OpenSpec validate/archive와 BATHOS guard는 중요 누락이나 위험 명령을 잡을 수 있다. 사건 #1697/#39에서는 정상 변경도 막았다는 보고가 있어 오탐 비용을 함께 재야 함.
3. **목적·범위 반복 전달**: AGENTS.md, 프로젝트 지침, BMad context는 기존 강한 대안이다. #3194는 제한 brief와 headless 기본 절차의 충돌을 보고하지만, 프로젝트 지침을 더 잘 구성해도 남는지 확인되지 않았다.
4. **반복 승인**: Codex에는 Allow always가 있다. #16911은 이미 그 선택 뒤에도 같은 도구에 질문이 반복됐다는 자기 보고이므로 “승인 기능이 없다”는 문제 정의는 부정확하다. 현재 릴리스 상태와 재현 조건은 미확인.
5. **장기 판단 기록**: OpenSpec archive가 이후 참여자에게 결정 이유를 제공한 긍정 사례가 있다. “현재 도구는 기억하지 못한다”는 일반 주장은 근거와 충돌한다. 잔여 후보는 기록 자체가 아니라 범위·상태의 정확한 적용 여부다.

## 대조군의 잠정 판정

- 기존 대안으로 이미 할 수 있는 일: 프로젝트 목적/규칙 공유, 변경 proposal과 결정 보관, 요구사항 검증, 승인 gate, 다중 repo context 열기, 완료 후 근거 기록.
- 공개 제보에서 의심되는 미해결 구간: 대상별 권한/작업 라우팅, partial apply의 truthful status, validate와 archive 사이의 늦은 실패, 과잉 승인·guard가 만드는 재작업.
- 실제 사용자에게 남는 순수 비용: 조사 자료로는 시간·반복률·금액을 대부분 측정하지 못함.
- 따라서 새 기능 차별점이나 제품 부재를 선언하지 않는다. 다음 실험에서 우선 현행 강한 Codex 지침·자료 대안만으로 충분한지 확인한다.
