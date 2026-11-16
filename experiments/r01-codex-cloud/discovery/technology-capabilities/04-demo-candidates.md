# 기존 기술만으로 가능한 후속 실증 후보

- 작성일: 2026-11-16 (KST)
- 상태: 설계 후보만 작성했다. 데모·테스트·유료 API·사용자 접촉은 실행하지 않았다 (`not_run`).
- 목적: 신규 제품을 만들지 않고 기존 기술의 구체 기능을 작은 fake-data scenario로 관찰할 수 있도록 한다.

## 후보 A — 조건 변경 뒤 유지/수정 작업 구분

- **질문:** 새로운 조건이 기존 요구와 구현 작업 중 무엇을 바꾸는지 명세 도구가 얼마나 추적 가능하게 표현하는가?
- **도구:** OpenSpec 한 가지를 택한다. 선택 시점의 version/commit과 CLI/agent 조합을 기록한다.
- **가짜 입력:** “초안은 이메일로 발송”이라는 작은 workflow spec + acceptance criteria 3개. 새 조건은 “승인하지 않은 경우 이메일 발송 금지, 미리보기만 제공”으로 제한한다.
- **예상 결과:** delta proposal에서 영향을 받는 acceptance criteria와 task를 바꾸고, 독립된 logging requirement는 그대로 유지한다. archive 전에 남은 task 상태가 드러난다.
- **성공 조건:** 변경/유지 목록을 spec/task path에 연결, 보호 대상 logging task가 불필요하게 삭제되지 않음, 구현 전 사람 검토 가능. `verify` 통과만으로 완료로 판정하지 않는다.
- **실패 조건:** 조건이 코드/작업으로 옮겨지지 않음, 무관 task가 사라짐, archive 상태가 구현 완료와 혼동됨.
- **예상 부담:** 1개 sandbox repo, 3~5개 artifact, 2~4개 작은 task. 무료/local 실행 가능 여부를 먼저 확인하고, model/API 호출이 필요하면 별도 승인 전에는 중지한다.
- **현재 상태:** 설계만 완료, **not_run**.

## 후보 B — 사람 승인 대기 후 동일 실행 상태로 재개

- **질문:** 승인 전과 승인 후 상태를 명시해 외부 작업을 pause/resume할 수 있는가?
- **도구:** LangGraph `interrupt`와 작은 deterministic local graph 또는 Agents SDK의 승인 상태 API 중 하나. 한 데모 안에서 두 framework를 섞지 않는다.
- **가짜 입력:** 테스트용 `send_preview(recipient="demo@example.invalid", body="fake")` 호출. network 송신 없이 승인 전/거절/승인 세 경로가 로컬 기록에만 남도록 한다.
- **예상 결과:** 첫 run은 승인 payload를 내고 pause; reject는 호출하지 않음; approve는 동일 thread/session state에서 한 번만 후속 단계를 완료.
- **성공 조건:** 승인 전 side-effect 없음, 세 경로의 상태를 log로 구별, 재개 후 실행 ID 유지, 재실행 시 중복 호출 없음 또는 중복 방지 범위를 명확히 기록.
- **실패 조건:** pause 전에 mock side-effect 발생, thread/state 연결 실패, 재개 중복 효과, 승인이 요청 내용과 연결되지 않음.
- **예상 부담:** Python 환경과 로컬 state 저장소 1개. LangGraph InMemorySaver는 process restart 증명을 못 하므로 디스크 checkpointer 선택 필요; Agents SDK 경로는 provider API를 필요로 할 수 있다.
- **현재 상태:** 설계만 완료, **not_run**.

## 후보 C — 교정된 기억의 저장과 후속 재검색

- **질문:** 사용자가 정정한 선호가 이전 기록에 혼재하지 않고 이후 질의에 반영되는가?
- **도구:** Mem0 OSS의 `add → memory ID → explicit update → search` 경로 또는 Letta MemFS의 file edit/commit/search. 한 run에서는 한 시스템만 선택한다.
- **가짜 입력:** 사용자 “Alex는 보통 커피를 마신다”; 이후 “Alex는 이제 디카페인만 선호한다.”; query “커피 추천 시 어떤 제한이 있나?” 저장값은 모두 synthetic.
- **예상 결과:** Mem0 선택 시 기존 ID의 내용을 update하고 검색 결과에서 최신 제한을 확인한다. Letta 선택 시 기준 memory file을 고치고 commit diff 및 후속 파일 retrieval을 확인한다.
- **성공 조건:** 변경 전·후 기록을 나란히 검토 가능, query가 최신 선호를 반환, 오래된 기록이 남을 경우 적용 우선순위/삭제 여부가 관찰 가능.
- **실패 조건:** 새 사실만 추가해 모순이 남음, 이전 사실이 계속 우선됨, 검색은 되지만 수정 출처/이력이 불명확함.
- **예상 부담:** Mem0 OSS는 model/embedding backend가 필요할 수 있으므로 완전 local/free 구성 여부를 사전에 평가; 아니면 provider call 없이 Letta 문서 파일 버전 관리만 실증한다. 외부 API를 자동 호출하지 않는다.
- **현재 상태:** 설계만 완료, **not_run**.

## 후보 선택 전 R01 판단

데모 목적을 “변경 영향의 가시성”, “승인 후 실행 재개”, “장기 기억 교정” 중 어디에 둘지 먼저 정해야 한다. B는 승인 시점의 side-effect 통제를 보고, C는 저장/검색 모델을 비교하므로 관찰 결과가 다르다. 이번 기술 조사 결과만으로 어느 축이 타겟 사용자에게 더 중요하다고 정하지 않는다.
