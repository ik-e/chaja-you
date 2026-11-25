# 결정·근거·대안·영향 추적

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## common-integration-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · blob `9df34e576f8a7c63c7ee84d01893a77631ce0360`

### decisions

#### CS-01

- **ID** (`id`): CS-01
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 플랫폼 지식과 업무 포트 연결 방식
  - **options** (`options`): 고정 프로필 하나를 버전으로 조회 · 모듈별 규칙 복제 · 범용 AI 매번 절차 생성
  - **drivers** (`drivers`): REQ-02, REQ-03, REQ-06, REQ-07, REQ-09
  - **tradeoffs** (`tradeoffs`): 공통 registry 조회 필요 · 플랫폼별 정의만 추가, 공통 계약에 플랫폼 enum 없음
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): 기존 5개 업무 포트 및 버전 고정 registry; 값 스키마·절차·목표·작업 정의를 동일 참조로 조회. 새로운 업무 API/AI 재계획 없음.
    - **이유** (`reason`): S04/S09/S10의 필드·객체 차이를 독립 프로필로 보존하고 준비/실행/판정 규칙이 달라지지 않게 함.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 새 플랫폼 등록이 공통 계약 수정 없이 불가능하거나 같은 profile hash에서 내용이 다를 때
- **출처** (`source_refs`): data · profiles
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-03 · REQ-06 · REQ-07 · REQ-09
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): D1 · LD-01 · LD-04 · DC2
- **target&#95;refs** (`target_refs`): I1 · I2 · I4 · I5 · RUNTIME
- **계획 시험** (`planned_test_refs`): T5-03 · T5-13 · DV-04 · AT-04 · AT-05

#### CS-02

- **ID** (`id`): CS-02
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 준비/수정/승인 및 사용자 API 경계
  - **options** (`options`): 원본과 등록 요청의 기존 9개 API · 초안/계획/승인/작업 각각 API · 등록 전 변경 불가
  - **drivers** (`drivers`): REQ-01, REQ-02, REQ-03, REQ-05, REQ-08
  - **tradeoffs** (`tradeoffs`): V4.1 PrepareInput 변경은 내부 계약에만 적용 · UI 값 덮어쓰기 금지; 동일 프로필에서 필요한 질문만
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): 기존 /v1 API 9개 유지. H5는 현재 이슈 답변 외에 승인 전 표시 필드의 명시적 수정 제안을 허용. 서버가 현재 질문→field→answer&#95;id를 확정하여 PREP에 전달하고 다시 검사. 원본 사실 변경은 새 Source, 플랫폼별 선택은 등록 요청에만.
    - **이유** (`reason`): V4 Answer에는 issue&#95;id만 있어 PREP가 어떤 필드 답인지 모를 수 있고, 이슈 없는 표시값을 수정할 경로가 없다. 작은 타입 보완 2개로 최종 승인 1회와 원본 불변성 유지. 추가 계획 API 불필요.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 현 수정/질문 흐름으로 실제 사용자 오류 교정이 불가능할 때
- **출처** (`source_refs`): data · schema · iface
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-05 · REQ-08
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): D2 · D3 · D6 · D7 · LD-02 · LD-05 · DC1 · DC7
- **target&#95;refs** (`target_refs`): H1 · H2 · H3 · H4 · H5 · H7 · I2 · STATE · UI
- **계획 시험** (`planned_test_refs`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · T5-01 · T5-06

#### CS-03

- **ID** (`id`): CS-03
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 동기 준비/인증과 비동기 실행, 오류 표현
  - **options** (`options`): 준비/인증 bounded request, 실행만 비동기 · 전 단계 별도 job/polling · 브라우저 실행까지 HTTP 동기
  - **drivers** (`drivers`): REQ-01, REQ-03, REQ-04, REQ-05, REQ-08
  - **tradeoffs** (`tradeoffs`): bounded prepare/auth 실패 처리 필요 · 별도 준비 큐·상태·API 불필요
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): 원본/준비/인증 확인은 요청 내 완료 또는 명시적 오류/준비 이슈. 실행 H7은 durable 수락 직후 202, H8/9 저장 상태 조회. 오류 코드와 status mapping 통일. 준비·인증 시간 제한 수치는 구현 실험 후 설정.
    - **이유** (`reason`): 긴 브라우저 업무 수명을 UI 연결과 분리해야 하나 준비를 별도 job으로 만들 실측 근거 없음. 정상 업무 차단과 시스템 오류 구분.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 측정상 준비/인증이 요청 제한을 반복적으로 넘거나 UX 실패가 발생할 때
- **출처** (`source_refs`): iface · data · logic
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-04 · REQ-05 · REQ-08
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): D2 · D3 · C03 · LD-06 · DC7
- **target&#95;refs** (`target_refs`): H4 · H5 · H6 · H7 · H8 · H9 · I2 · I3 · I4 · STATE · UI
- **계획 시험** (`planned_test_refs`): T5-07 · AT-02 · T5-05 · DV-01 · DV-05

#### CS-04

- **ID** (`id`): CS-04
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 인증 확인에서 실행으로 연결 및 UI viewer 경계
  - **options** (`options`): 사용자 직접 인증 같은 서버 세션+제어권 인계 · 자격증명 수집/재로그인 · UI가 브라우저 기술 직접 제어
  - **drivers** (`drivers`): REQ-04, REQ-05, REQ-10
  - **tradeoffs** (`tradeoffs`): runtime이 viewer 클라이언트 경계를 제공해야 함 · 실제 전송·격리/TTL 구현 위임, 실제 권한 미확인
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): AuthOutput 내부 binding 고정; public AuthResponse는 grant와 안전한 표시 정보만. runtime 담당 viewer mount/dispose 인터페이스 제공, UI는 인증 완료 버튼·현재 grant만 사용. finish에서 인간 입력 차단 후 identity/target 확인; 실행 승인 후 동일 binding의 worker lease.
    - **이유** (`reason`): R05 로컬 합성 PoC의 동일 맥락·뷰어 종료 독립 근거, 외부 계정과 실행 세션 불일치 방지. 제품 UI와 remote 내부 전송 기술을 결합하지 않음.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 11/27 원격 독립 구현이 동일 인증 맥락·제어권·격리를 입증하지 못할 때
- **출처** (`source_refs`): direction · data · schema · phase
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): DIR-01 · DIR-02 · A4 · D3 · LD-06 · DC5
- **target&#95;refs** (`target_refs`): H6 · I3 · I4 · VIEWER · RUNTIME · UI · STORE
- **계획 시험** (`planned_test_refs`): AT-02 · AT-03 · T5-02 · DV-02 · DV-05

#### CS-05

- **ID** (`id`): CS-05
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 상태/승인/멱등성 및 외부 효과 직렬화
  - **options** (`options`): CO 단일 상태 소유+공통 저장 원자 경계+등록된 runtime command · 각 모듈 임의 상태/브라우저 직접 mutation · 별도 분산 이벤트/복구 시스템
  - **drivers** (`drivers`): REQ-05, REQ-08, REQ-10
  - **tradeoffs** (`tradeoffs`): 원자 저장·admission 경계를 구현/시험해야 함 · 분산 서비스·별도 취소/재개 불필요
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): CO만 업무 상태 전이 소유, STORE 원자 accept/admit/fence/observe/terminal; runtime gateway에 등록된 Operation만 허용. 같은 key 재조회; 다른 key로 동일 효과 재발급 차단. 오류에만 stopping→stopped, 새 admission 금지, pending unknown 보존, user cancel/resume/rollback 없음.
    - **이유** (`reason`): 상위 I2/I3·A2 요구를 만족하는 최소 직렬화. 승인 범위와 실제 operation을 일치시키고, 브라우저 효과의 exactly-once는 주장하지 않음.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 경쟁/응답 유실 시험에서 중복·미승인 동작 또는 활성 작업 방치 발생
- **출처** (`source_refs`): top · amend · data · logic
- **요구 참조** (`requirement_refs`): REQ-05 · REQ-08 · REQ-10
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): A2 · A3 · D3 · D5 · LD-06 · DC5 · C04 · C05
- **target&#95;refs** (`target_refs`): H7 · I4 · STATE · STORE · RUNTIME
- **계획 시험** (`planned_test_refs`): T5-01 · AT-03 · T5-12 · DV-01 · DV-02 · DV-04

#### CS-06

- **ID** (`id`): CS-06
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 결과의 증거와 실패 판정
  - **options** (`options`): 프로필 요구 증거를 실제 관측으로 대조 · 클릭 성공 또는 runner completed=등록 성공 · 모든 플랫폼 고정 재조회
  - **drivers** (`drivers`): REQ-06, REQ-07, REQ-08, REQ-10
  - **tradeoffs** (`tradeoffs`): 증거 관측·정규화가 플랫폼별 필요 · 불필요한 추가 조회 강제하지 않음
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): EXEC가 실제 관측·EvidenceRecord를 기록, RESULT는 profile goal/method/target/payload/asset 확인, CO가 판정 저장. 두 mock은 독립 readback, 다른 지원 profile은 신뢰 가능한 응답 증거 허용. 완료와 게시 구분, stopped 이후 확인 근거 추가 가능하지만 상태 재개 없음.
    - **이유** (`reason`): S04/S07의 접수 ID 및 재조회 대조가 필요하다는 근거, 숨고는 설정 저장 대상이 다름. 근거가 부족하면 unknown.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 결과를 판정할 증거가 부족하거나 실제 완료 객체가 변경될 때
- **출처** (`source_refs`): top · data · profiles
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-08 · REQ-10
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): A2 · D4 · D5 · LD-07 · DC6
- **target&#95;refs** (`target_refs`): I4 · I5 · H8 · H9 · STATE · UI
- **계획 시험** (`planned_test_refs`): AT-04 · AT-05 · T5-13 · DV-01 · DV-03 · DV-04

#### CS-07

- **ID** (`id`): CS-07
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 최소 논리 통합 구조와 공통 저장 책임
  - **options** (`options`): 모듈형 앱+공통 영속 저장+격리 remote+독립 adapter · 업무별 microservice/브로커 · 각 담당이 별도 제품 정본
  - **drivers** (`drivers`): REQ-01, REQ-04, REQ-05, REQ-08, REQ-09, REQ-10, REQ-11
  - **tradeoffs** (`tradeoffs`): 통합 스택 결정 전 실행 가능한 실제 제품 skeleton 없음 · 담당자 내부 기술은 계약 호환 범위에서 위임
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): 한 제품 root와 공통 계약, 서버/준비/브라우저/플랫폼/UI/테스트 경계. 저장소 하나의 논리 정본과 runtime 격리. 모듈 경계·호출과 소유권·stub 우선 결정; 언어/DB/패키지/물리 배포·launch 구현은 11/27 근거 후.
    - **이유** (`reason`): 5인 팀, 단일 등록 업무, 원자 수락과 상태 일관성이 중요. 기존 WBS W01 및 독립 작업 그대로, 별도 서비스 배포/동기화 비용을 먼저 지지 않음.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 독립 검증 결과로 shared dependency/transport/isolated runtime이 결정되거나 단일 앱이 요구를 못 충족할 때
- **출처** (`source_refs`): direction · data · iface · phase · wbs
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-04 · REQ-05 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): DIR-02 · D8 · LD-08 · C06 · DC8 · B4-02 · R5-10
- **target&#95;refs** (`target_refs`): INTEGRATION · STORE · RUNTIME · VIEWER · I1 · I2 · I3 · I4 · I5
- **계획 시험** (`planned_test_refs`): T5-03 · T5-05 · T5-06 · AT-02 · DV-05

#### CS-08

- **ID** (`id`): CS-08
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 공통 시험 및 착수/통합 수용 기준
  - **options** (`options`): 현재 22개 시험 정합화·동일 후보 증거·stub→real 점진 통합 · 팀원별 성공 주장 합산 · 완성 후 일괄 연결
  - **drivers** (`drivers`): REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11
  - **tradeoffs** (`tradeoffs`): 실행 결과 수집은 후속 작업 필요 · 불필요한 새 평가 시스템 대신 기존 게이트 재사용
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): 22개 기존 제품 mock gate 유지 및 최신 의미로 갱신; T1~T6 독립 시험은 변경 없음. 동일 build/contract/fixture/environment 근거만, T5-08 실제 모델 시험 필수. stub을 기능 검증과 구분, 단계별 연결 기록. 12/8 크몽 우선/숨고 확장 미충족은 R01 판단.
    - **이유** (`reason`): 기존 test gate와 단계별 검증 체계 재사용. 다른 후보/환경/수동 대체 성공을 현재 전체 제품 성공으로 합산하지 않음.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 제품 범위·완료 조건·공통 계약이 변경되거나 공통 harness와 어댑터 결과가 확보될 때
- **출처** (`source_refs`): gate · trace · data · phase · wbs
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): A2 · A4 · LD-08 · DC8 · D8 · R5-09 · R5-11
- **target&#95;refs** (`target_refs`): GATE · INTEGRATION
- **계획 시험** (`planned_test_refs`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · AT-02 · AT-03 · T5-01 · T5-02 · T5-12 · T5-03 · T5-07 · AT-04 · AT-05 · T5-06 · T5-13 · T5-05 · DV-01 · DV-02 · DV-03 · DV-04 · DV-05

#### CS-09

- **ID** (`id`): CS-09
- **type&#95;id** (`type_id`): IT-19
- **상태** (`status`): provisional
- **evidence&#95;level** (`evidence_level`): sourced
- **fields** (`fields`)
  - **decision&#95;question** (`decision_question`): 설계 변경의 근거 추적 및 책임 배분
  - **options** (`options`): 기존 IT-19 및 추적 인덱스 이어서 갱신 · 새 ADR 체계/중복 요구사항 정본 · 별도 근거 없이 결정
  - **drivers** (`drivers`): REQ-09, REQ-11
  - **tradeoffs** (`tradeoffs`): 현재 적용 판정과 link 갱신 필요 · 일반 모델/검증기를 새로 만들지 않음
  - **selection&#95;and&#95;reason** (`selection_and_reason`)
    - **selection** (`selection`): IT-19 결정 기록으로 원문/버전/요구/선행/대안/선택/검증/작업을 연결. V0.6 추적 이력 보존, V0.9 현재 투영 및 supersession. 과거 근거 부족은 unknown/후속 해석으로 표기. 작업 배분은 실제 phase 이후 단일 책임자로 확정.
    - **이유** (`reason`): 기존 설계 정보 모델과 trace가 이미 목적을 충족하며 재설계로 링크만 끊겼음. 원본 중복·상태 승격 방지.
    - **scope** (`scope`): delegated logical common mock baseline; not independently human-adopted or implementation success
  - **authority&#95;ref** (`authority_ref`): LR-COMMON-01/authority
  - **재검토 조건** (`revisit_when`): 상위 의도/근거/계약/시험/작업 변경 때 영향 후보 검토
- **출처** (`source_refs`): trace · model · phase · wbs
- **요구 참조** (`requirement_refs`): REQ-09 · REQ-11
- **prior&#95;decision&#95;refs** (`prior_decision_refs`): D8 · LD-08 · DC8
- **target&#95;refs** (`target_refs`): TRACE · INTEGRATION · GATE
- **계획 시험** (`planned_test_refs`): T5-03 · DV-04

## trace-index-v0.9.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/trace-index-v0.9.json) · blob `987018e3e41f15521de6ba2fef33867cea81a88d`

### id

- LESSON-DESIGN-TRACE-V0.9

### status

- projection&#95;current&#95;candidate

### base_trace

- trace-index-v0.6.json

### model_ref

- docs/deliverables/planning-design-info-model.json

### date

- 2026-11-25

### purpose

- Existing trace extension, not second canonical decision/requirement source. Source&#95;ref+blob+locator resolves original. Later links are retrospective review relationships, not contemporaneous evidence or retroactive adoption.

### sources

- **model** (`model`)
  - **path** (`path`): docs/deliverables/planning-design-info-model.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): abcf59b611d3eccde0292f48af1c43fb76d65eb2
- **phase** (`phase`)
  - **path** (`path`): docs/human/phase-intents/PHASE-20261124-02.md
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 6b790bf85ed6295cb096e56560ddc86d34031087
- **plan** (`plan`)
  - **path** (`path`): docs/artifacts/planning/lesson-registration-20261123/proposal-v1.1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): a81b521898cc516cd88b8b53ec39dbf008b164eb
- **harness** (`harness`)
  - **path** (`path`): prototype/lesson-registration/test-harness/CONTRACT.md
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): f93daf71aebc1a4272739956c7753968e7655d5b
- **trace** (`trace`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/trace-index-v0.6.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 57bf34466c96c7f86c3e1a630eedbd3c29647e41
- **v01verify** (`v01verify`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/verification-decisions-v0.1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): f2c0940ed7e10ca410e14896f789fc6752702488
- **v02** (`v02`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/detail-design-v0.2.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): ee0490e7bad742cb4e9cf3f593da1bc1421c16c2
- **review** (`review`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/review-v0.3.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 7961bce5e04b3377559dca93ee98df8c0dc2febf
- **direction** (`direction`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/direction-v0.4.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 54beb7c357e580b087442bb8f00e40ab2a3567af
- **requirements** (`requirements`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/implementation-v0.4.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): f7b49262a4d470f6a2764e0fd2c559e6358cc416
- **rules** (`rules`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/contract-v0.5.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): b773142f11580c098a5e90a99d4f633083b116ad
- **wbs** (`wbs`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/wbs-v0.5.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 5203828cc220187ec53d1602579b9e12ab1cf5d0
- **top** (`top`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/top-design-v1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 1ed54afd5b541fa3a9d4030267ba65c54729ff2b
- **amend** (`amend`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/top-design-amendment-v1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): ad4f09689896206163dfce72d972281b10075891
- **detail** (`detail`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/detail-decisions-v2.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 3c04b85cb9ee45d8aa21b9cfdea0713fe8dc3014
- **iface** (`iface`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/interface-contract-v3.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): e6b73da91c0856e815601739301a53adcc321e70
- **upper** (`upper`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/logical-data-contract-decision-v1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 7141bcc48dabc36e42736035f4a6fcc2b8526f34
- **data** (`data`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/data-contract-v4.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): edd84980d5df53c8df0800dd28f7878396ad4397
- **schema** (`schema`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): de6c147216ee68bae75a9d18f9127c327701fa5a
- **profiles** (`profiles`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/platform-profiles-v2.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): b0b2044526f63f0244d920f85b2d9676b94bbe72
- **logic** (`logic`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/logical-behavior-v5.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 2c13b86a44b10f7877678509819e97d1d1b72c17
- **gate** (`gate`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/detail-gate-v1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 55c66d285183fb4a8a12041b883c12e7775d12f7
- **common** (`common`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 9df34e576f8a7c63c7ee84d01893a77631ce0360
- **validation** (`validation`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/data-contract-validation-v4.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 0710bcf3676e23712e5d02d749e74d8cf47f9a6e
- **reviewEvidence** (`reviewEvidence`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/interface-review-evidence-v3.json
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 5c1d8d800a3f7a05fc93789938f6856519370dad
- **legacy&#95;validator** (`legacy_validator`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/validate-interface-review-v3.mjs
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 1d49665ea105450c87b97a6a7cd6f72aec869321
- **data&#95;validator** (`data_validator`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/validate-data-contract-v4.mjs
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 2484c5df659962145af1ee2d94dd36d1f41e5f6f
- **logic&#95;validator** (`logic_validator`)
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/validate-logical-v5.mjs
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): 660dd54af6cf7d2db72da25d724b728b00f1c550
- **validator** (`validator`)
  - **path** (`path`): tools/verify&#95;design&#95;stage.mjs
  - **commit** (`commit`): e71e8238a568e5661de46b354c72481d762bc381
  - **blob&#95;sha** (`blob_sha`): bdb4c90b3f699432343a0c8a3c77f668dc050546
- **S03** (`S03`)
  - **path** (`path`): docs/members/R02/workspace/2026-11-23&#95;lesson-pain-priority.md
  - **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
  - **blob&#95;sha** (`blob_sha`): c1aba280833039a5787b4460d948de231b44e135
  - **limit** (`limit`): 사용자 진술·회상·최신 확인값, 실측 없음
- **S04** (`S04`)
  - **path** (`path`): docs/members/R03/workspace/test/SPEC.md
  - **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
  - **blob&#95;sha** (`blob_sha`): 7ef82683df7826330ec00a1348b56c7b48973c0f
  - **limit** (`limit`): 크몽형 모의 실험, 고정 fixture
- **S07** (`S07`)
  - **path** (`path`): docs/members/R03/workspace/test/verification.json
  - **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
  - **blob&#95;sha** (`blob_sha`): 5a343dd028889970e2cd64dbf0f2bab4e27a5fb9
  - **limit** (`limit`): 19 pass 자기 보고, 모의 Skyvern 입력·첨부·영수증; 독립 재실행 아님
- **S08** (`S08`)
  - **path** (`path`): docs/members/R04/workspace/2026-11-24&#95;숨고&#95;고수등록&#95;교육신청&#95;사용자흐름&#95;서비스절차&#95;설계분석보고서.md
  - **commit** (`commit`): 926b5de7678f8984be035409d386c6347d749f56
  - **blob&#95;sha** (`blob_sha`): 0de56aa480c4d207a09f4f9f560d707f8004a979
  - **limit** (`limit`): 기존 고수 계정 관측 및 제안, 신규 가입·공개 추론 분리
- **S09** (`S09`)
  - **path** (`path`): docs/members/R04/workspace/2026-11-24&#95;숨고&#95;고수전환&#95;및&#95;등록절차&#95;화면스크린샷&#95;상세보고서.md
  - **commit** (`commit`): 926b5de7678f8984be035409d386c6347d749f56
  - **blob&#95;sha** (`blob_sha`): 4062a83b314fd6db11d4572edfefc8873a367287
  - **limit** (`limit`): STEP 06~12, 15, 16 보고서 관측; 스크린샷 원본 개별 검증 안 함
- **S10** (`S10`)
  - **path** (`path`): docs/members/R05/workspace/2026-11-24&#95;platform-input-skeleton.md
  - **commit** (`commit`): c5cef60dceb98390b008e7345fc5c0492695e8e3
  - **blob&#95;sha** (`blob_sha`): ba0a1f1d6243876929efd4b8aad6cd602570d47a
  - **limit** (`limit`): 수동 작성 화면·임시저장 보고, 플랫폼별 제약 후보; 실제 자동화 아님
- **S11** (`S11`)
  - **path** (`path`): docs/members/R05/workspace/2026-11-23&#95;lesson-technical-feasibility.md
  - **commit** (`commit`): c5cef60dceb98390b008e7345fc5c0492695e8e3
  - **blob&#95;sha** (`blob_sha`): 48428cf787b919f44245d584729ffdc62b6a1857
  - **limit** (`limit`): 공식/관찰/추정 구분, 운영사 허용 미확인
- **S12** (`S12`)
  - **path** (`path`): prototype/lesson-registration/test-harness/CONTRACT.md
  - **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
  - **blob&#95;sha** (`blob_sha`): f93daf71aebc1a4272739956c7753968e7655d5b
  - **limit** (`limit`): T1~T6, 변경하지 않음; release 미확인
- **EV-R05-REMOTE-20261124** (`EV-R05-REMOTE-20261124`)
  - **path** (`path`): docs/members/R05/workspace/remote-browser-poc/README.md
  - **commit** (`commit`): fc59a4b8f5e8adea3c4dc3b2264df2907131c018
  - **limit** (`limit`): 로컬 합성 환경, Chrome 프로세스 공유 BrowserContext, 실제 플랫폼·Docker/운영 격리·HTTPS/WSS 외부 접속·부하·IME 미검증.
  - **blob&#95;sha** (`blob_sha`): e50832e02312684798c9f65c25d2ee410d513e12

### precedence

- Current phase/permission and human top decisions first; A2 overrides legacy cancel/resume/rollback
- V4.1 schema delta and common-integration-v1 wire/ports/constraints current; V4 remaining data and profile V2 current; old contracts historical except explicitly retained requirements
- V0.6 trace historical; original status preserved; current status is projection, not actual product verification

### inventory

#### LR-D01

- **ID** (`id`): LR-D01
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `12`
  - **ID** (`id`): LR-D01
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): scope&#95;agreed&#95;live&#95;detail&#95;open
- **question** (`question`): 첫 제품 플랫폼·완료 단위
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-01 · DEC-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LR-D02

- **ID** (`id`): LR-D02
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `13`
  - **ID** (`id`): LR-D02
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): direction&#95;agreed&#95;live&#95;gate&#95;open
- **question** (`question`): 실행·인증·허용 경계
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-03 · DEC-04 · DEC-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LR-D03

- **ID** (`id`): LR-D03
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `14`
  - **ID** (`id`): LR-D03
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): logical&#95;boundary&#95;defined&#95;stack&#95;deferred
- **question** (`question`): 상위 실행 단위·스택·AI 구성
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-06 · DEC-10 · DEC-12
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LR-D04

- **ID** (`id`): LR-D04
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `15`
  - **ID** (`id`): LR-D04
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): logical&#95;wire&#95;storage&#95;defined&#95;physical&#95;deferred
- **question** (`question`): 물리 API·DB·저장·배포
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-11 · DEC-12
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LR-D05

- **ID** (`id`): LR-D05
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `16`
  - **ID** (`id`): LR-D05
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): first&#95;registration&#95;scope&#95;agreed&#95;value&#95;unverified
- **question** (`question`): 사용자 범위 및 사업 가치
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-01 · DEC-13 · DEC-17
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LR-D06

- **ID** (`id`): LR-D06
- **source&#95;ref** (`source_ref`): v01verify
- **locator** (`locator`)
  - **collection** (`collection`): records
  - **index** (`index`): `17`
  - **ID** (`id`): LR-D06
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): safety&#95;contract&#95;defined&#95;quantitative&#95;policy&#95;open
- **question** (`question`): 정량 품질·운영 정책
- **related&#95;later&#95;refs** (`related_later_refs`): DEC-13 · DEC-14 · DEC-15
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DEC-01

- **ID** (`id`): DEC-01
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): DEC-01
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): scope&#95;agreed&#95;live&#95;detail&#95;open
- **question** (`question`): MVP 지원 플랫폼
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-03 · DIR-04 · DC4
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-09
- **work&#95;refs** (`work_refs`): W01 · W09 · W13

#### DEC-02

- **ID** (`id`): DEC-02
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): DEC-02
- **original&#95;status** (`original_status`): partial
- **current&#95;status** (`current_status`): mock&#95;goal&#95;defined&#95;live&#95;unverified
- **question** (`question`): 플랫폼별 완료 범위
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-03 · DC3 · DC4 · DC6
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-08
- **work&#95;refs** (`work_refs`): W01 · W08 · W09 · W13

#### DEC-03

- **ID** (`id`): DEC-03
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): DEC-03
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): direction&#95;agreed
- **question** (`question`): 실행 구조
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-01 · A4
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **work&#95;refs** (`work_refs`): W04 · W07

#### DEC-04

- **ID** (`id`): DEC-04
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): DEC-04
- **original&#95;status** (`original_status`): external&#95;unverified
- **current&#95;status** (`current_status`): external&#95;gate&#95;open
- **question** (`question`): 운영사 허용
- **related&#95;later&#95;refs** (`related_later_refs`): B4-05 · R5-09
- **note** (`note`): 현 PHASE 실제 접근/제출 금지, mock 설계 진행 가능.
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-05 · REQ-10
- **work&#95;refs** (`work_refs`): W13 · W14 · W17

#### DEC-05

- **ID** (`id`): DEC-05
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): DEC-05
- **original&#95;status** (`original_status`): contract&#95;proposed
- **current&#95;status** (`current_status`): logical&#95;contract&#95;defined&#95;runtime&#95;unverified
- **question** (`question`): 계정·승인 결합
- **related&#95;later&#95;refs** (`related_later_refs`): R5-01 · R5-02 · R5-03 · R5-04 · D3 · DC5 · CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **work&#95;refs** (`work_refs`): W03 · W04 · W07

#### DEC-06

- **ID** (`id`): DEC-06
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): DEC-06
- **original&#95;status** (`original_status`): contract&#95;proposed
- **current&#95;status** (`current_status`): logical&#95;boundary&#95;defined&#95;model&#95;unverified
- **question** (`question`): AI/코드 역할
- **related&#95;later&#95;refs** (`related_later_refs`): R5-08 · A1 · D2 · DC7
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-05
- **work&#95;refs** (`work_refs`): W19 · W03

#### DEC-07

- **ID** (`id`): DEC-07
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `6`
  - **ID** (`id`): DEC-07
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): delegated
- **question** (`question`): 실행 엔진
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-02 · B4-03 · D8
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-06 · REQ-07
- **work&#95;refs** (`work_refs`): W04 · W06 · W08

#### DEC-08

- **ID** (`id`): DEC-08
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `7`
  - **ID** (`id`): DEC-08
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): logical&#95;binding&#95;defined&#95;ttl&#95;deferred
- **question** (`question`): 세션 TTL·재인증
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-02 · A2 · DC5 · CS-04
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-08 · REQ-10
- **work&#95;refs** (`work_refs`): W04 · W11

#### DEC-09

- **ID** (`id`): DEC-09
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `8`
  - **ID** (`id`): DEC-09
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): independent&#95;jobs&#95;defined&#95;concurrency&#95;policy&#95;unselected
- **question** (`question`): 순차/동시 등록
- **related&#95;later&#95;refs** (`related_later_refs`): B4-02 · R5-06 · D3
- **note** (`note`): 개별 요청/결과 독립; 전역 동시성 정책은 미선정.
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-09
- **work&#95;refs** (`work_refs`): W01 · W03 · W09

#### DEC-10

- **ID** (`id`): DEC-10
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `9`
  - **ID** (`id`): DEC-10
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): logical&#95;boundary&#95;defined&#95;physical&#95;deferred
- **question** (`question`): 물리 실행 단위
- **related&#95;later&#95;refs** (`related_later_refs`): B4-02 · R5-10 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **work&#95;refs** (`work_refs`): W01 · W03 · W04

#### DEC-11

- **ID** (`id`): DEC-11
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `10`
  - **ID** (`id`): DEC-11
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): logical&#95;storage&#95;defined&#95;physical&#95;deferred
- **question** (`question`): DB·파일 저장
- **related&#95;later&#95;refs** (`related_later_refs`): B4-04 · LD-02 · LD-08 · CS-05 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-05 · REQ-08 · REQ-10
- **work&#95;refs** (`work_refs`): W03 · W16

#### DEC-12

- **ID** (`id`): DEC-12
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `11`
  - **ID** (`id`): DEC-12
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): logical&#95;wire&#95;defined&#95;stack&#95;deferred
- **question** (`question`): 스택·배포·물리 API
- **related&#95;later&#95;refs** (`related_later_refs`): DIR-02 · B4-04 · R5-11 · D7 · D8 · CS-02 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-03 · REQ-04 · REQ-10
- **work&#95;refs** (`work_refs`): W01 · W03 · W04 · W16

#### DEC-13

- **ID** (`id`): DEC-13
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `12`
  - **ID** (`id`): DEC-13
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): measurement&#95;gate&#95;open
- **question** (`question`): 성능·비용·직접 시간
- **related&#95;later&#95;refs** (`related_later_refs`): R5-08 · R5-09
- **note** (`note`): 시간/비용/가치 실측 없음.
- **요구 참조** (`requirement_refs`): REQ-11
- **work&#95;refs** (`work_refs`): W15 · W17

#### DEC-14

- **ID** (`id`): DEC-14
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `13`
  - **ID** (`id`): DEC-14
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): logical&#95;minimum&#95;control&#95;retention&#95;deferred
- **question** (`question`): 개인정보·로그·보존
- **related&#95;later&#95;refs** (`related_later_refs`): R5-03 · R5-04 · R5-09 · DC5 · CS-04
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-10
- **work&#95;refs** (`work_refs`): W04 · W11 · W13

#### DEC-15

- **ID** (`id`): DEC-15
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `14`
  - **ID** (`id`): DEC-15
- **original&#95;status** (`original_status`): partial
- **current&#95;status** (`current_status`): partially&#95;superseded&#95;error&#95;only&#95;stop
- **question** (`question`): 장애 복구·통지
- **related&#95;later&#95;refs** (`related_later_refs`): R5-03 · R5-04 · R5-05 · A2 · D4 · D5 · CS-05 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-08 · REQ-10
- **work&#95;refs** (`work_refs`): W03 · W04 · W11

#### DEC-16

- **ID** (`id`): DEC-16
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `15`
  - **ID** (`id`): DEC-16
- **original&#95;status** (`original_status`): open
- **current&#95;status** (`current_status`): reuse&#95;evidence&#95;review&#95;pending
- **question** (`question`): PoC 재사용
- **related&#95;later&#95;refs** (`related_later_refs`): R5-10 · R5-11 · D8 · CS-07 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-03 · REQ-04 · REQ-06 · REQ-07
- **work&#95;refs** (`work_refs`): W01 · W03 · W04 · W06 · W08

#### DEC-17

- **ID** (`id`): DEC-17
- **source&#95;ref** (`source_ref`): review
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `16`
  - **ID** (`id`): DEC-17
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): deferred&#95;out&#95;of&#95;scope
- **question** (`question`): 이행·환불
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): 환불/이행/사업화 범위 미추가.
- **요구 참조** (`requirement_refs`): REQ-11
- **work&#95;refs** (`work_refs`): W13 · W15

#### DIR-01

- **ID** (`id`): DIR-01
- **source&#95;ref** (`source_ref`): direction
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): DIR-01
- **original&#95;status** (`original_status`): decided
- **current&#95;status** (`current_status`): decided
- **question** (`question`): 목표 실행 구조
- **related&#95;later&#95;refs** (`related_later_refs`): A4 · CS-04
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DIR-02

- **ID** (`id`): DIR-02
- **source&#95;ref** (`source_ref`): direction
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): DIR-02
- **original&#95;status** (`original_status`): delegated&#95;with&#95;constraints
- **current&#95;status** (`current_status`): delegated&#95;with&#95;constraints
- **question** (`question`): 원격 브라우저 세부 구현
- **related&#95;later&#95;refs** (`related_later_refs`): A4 · D8 · CS-04 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DIR-03

- **ID** (`id`): DIR-03
- **source&#95;ref** (`source_ref`): direction
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): DIR-03
- **original&#95;status** (`original_status`): scope&#95;decided&#95;target&#95;detail&#95;pending
- **current&#95;status** (`current_status`): scope&#95;decided&#95;target&#95;detail&#95;pending
- **question** (`question`): 2026-12-08 MVP
- **related&#95;later&#95;refs** (`related_later_refs`): A4 · DC3 · DC4 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DIR-04

- **ID** (`id`): DIR-04
- **source&#95;ref** (`source_ref`): direction
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): DIR-04
- **original&#95;status** (`original_status`): goal&#95;decided&#95;acceptance&#95;pending
- **current&#95;status** (`current_status`): goal&#95;decided&#95;acceptance&#95;pending
- **question** (`question`): 2027-01-04 최종 목표
- **related&#95;later&#95;refs** (`related_later_refs`): A1 · LD-04 · DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-01

- **ID** (`id`): B4-01
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): B4-01
- **original&#95;status** (`original_status`): decided
- **current&#95;status** (`current_status`): direction&#95;agreed
- **question** (`question`): DIR-01~04 채택: 원격 브라우저, 구현자 세부 기술, 크몽→숨고, URL 지원 플랫폼 최초 등록.
- **related&#95;later&#95;refs** (`related_later_refs`): A4
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-02

- **ID** (`id`): B4-02
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): B4-02
- **original&#95;status** (`original_status`): proposed
- **current&#95;status** (`current_status`): refined&#95;logical&#95;topology
- **question** (`question`): 모듈형 앱 + 논리적으로 분리된 remote runtime, 하나의 영속 데이터 정본. 초기 지원은 플랫폼별 순차 job.
- **related&#95;later&#95;refs** (`related_later_refs`): D3 · C06 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-03

- **ID** (`id`): B4-03
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): B4-03
- **original&#95;status** (`original_status`): delegated
- **current&#95;status** (`current_status`): delegated
- **question** (`question`): CDP/noVNC/WebRTC, 자동화 엔진/브라우저/원격 격리 구체 구현; 명시 계약/시험·보안 준수.
- **related&#95;later&#95;refs** (`related_later_refs`): D8 · CS-04
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-04

- **ID** (`id`): B4-04
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): B4-04
- **original&#95;status** (`original_status`): proposed
- **current&#95;status** (`current_status`): historical&#95;stack&#95;candidate&#95;not&#95;adopted
- **question** (`question`): 공통 Python/FastAPI/관계형 DB 및 동일-origin UI 초기 기준. 구현자 검토·변경 조건 기록, 특정 프론트/DB 강제 전 검토.
- **related&#95;later&#95;refs** (`related_later_refs`): D8 · CS-07
- **note** (`note`): Python/FastAPI/DB 후보를 채택으로 승격하지 않음.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-05

- **ID** (`id`): B4-05
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): B4-05
- **original&#95;status** (`original_status`): external&#95;gate
- **current&#95;status** (`current_status`): external&#95;gate&#95;open
- **question** (`question`): 실환경 정책/권한·계정 안정 식별·실제 효과/증거·운영 보안·비용/가치. 모의 성공과 실서비스 완료 구분.
- **related&#95;later&#95;refs** (`related_later_refs`): A4 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### B4-06

- **ID** (`id`): B4-06
- **source&#95;ref** (`source_ref`): requirements
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): B4-06
- **original&#95;status** (`original_status`): conditional
- **current&#95;status** (`current_status`): live&#95;scope&#95;open
- **question** (`question`): 숨고 실제 등록 객체·완료 정의, 12/8 두 번째 경로 범위 및 1/4 지원 플랫폼 목록은 기존 조사/통합 결과로 R01 검토. 범위 축소는 명시 결정.
- **related&#95;later&#95;refs** (`related_later_refs`): DC4 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-01

- **ID** (`id`): R5-01
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `0`
  - **ID** (`id`): R5-01
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): partially&#95;superseded&#95;single&#95;approval
- **question** (`question`): 계획 승인
- **related&#95;later&#95;refs** (`related_later_refs`): A2 · D2 · D3 · LD-06 · CS-02 · CS-05
- **note** (`note`): 기존 여러 승인 단계는 D2/D3 단일 최종 승인으로 대체.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-02

- **ID** (`id`): R5-02
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `1`
  - **ID** (`id`): R5-02
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): refined&#95;no&#95;separate&#95;business&#95;resources
- **question** (`question`): 증거 계층
- **related&#95;later&#95;refs** (`related_later_refs`): DC5 · DC6 · CS-04
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-03

- **ID** (`id`): R5-03
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `2`
  - **ID** (`id`): R5-03
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): partially&#95;superseded&#95;no&#95;user&#95;cancel&#95;resume
- **question** (`question`): 제어권과 직렬화
- **related&#95;later&#95;refs** (`related_later_refs`): A2 · A3 · DC5 · CS-05
- **note** (`note`): 사용자 실행 중 중단/변경/재개는 A2로 대체.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-04

- **ID** (`id`): R5-04
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `3`
  - **ID** (`id`): R5-04
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): superseded&#95;postaccept&#95;rebind&#95;resume
- **question** (`question`): 재연결
- **related&#95;later&#95;refs** (`related_later_refs`): A2 · DC5 · CS-04 · CS-05
- **note** (`note`): 수락 이후 재연결/재개 폐기; 실행 전 재확인 및 종료 후 읽기 증거만 허용.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-05

- **ID** (`id`): R5-05
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `4`
  - **ID** (`id`): R5-05
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): retained
- **question** (`question`): 재접속 UX
- **related&#95;later&#95;refs** (`related_later_refs`): D3 · CS-03 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-06

- **ID** (`id`): R5-06
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `5`
  - **ID** (`id`): R5-06
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): refined&#95;independent&#95;requests
- **question** (`question`): 한 번 입력·다중 대상
- **related&#95;later&#95;refs** (`related_later_refs`): D6 · LD-02 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-07

- **ID** (`id`): R5-07
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `6`
  - **ID** (`id`): R5-07
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): retained&#95;registry&#95;guard
- **question** (`question`): 지원과 실행 판정
- **related&#95;later&#95;refs** (`related_later_refs`): LD-04 · DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-08

- **ID** (`id`): R5-08
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `7`
  - **ID** (`id`): R5-08
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): retained&#95;ai&#95;boundary&#95;model&#95;unverified
- **question** (`question`): AI 최소 제품 경로
- **related&#95;later&#95;refs** (`related_later_refs`): D2 · DC1 · DC7 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-09

- **ID** (`id`): R5-09
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `8`
  - **ID** (`id`): R5-09
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): refined&#95;mock&#95;goal&#95;error&#95;only&#95;stop
- **question** (`question`): 목표 및 release 경계
- **related&#95;later&#95;refs** (`related_later_refs`): A2 · A4 · DC6 · CS-06 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-10

- **ID** (`id`): R5-10
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `9`
  - **ID** (`id`): R5-10
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): refined&#95;logical&#95;boundary&#95;technology&#95;deferred
- **question** (`question`): 최소 구현
- **related&#95;later&#95;refs** (`related_later_refs`): D8 · C06 · CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### R5-11

- **ID** (`id`): R5-11
- **source&#95;ref** (`source_ref`): rules
- **locator** (`locator`)
  - **collection** (`collection`): rules
  - **index** (`index`): `10`
  - **ID** (`id`): R5-11
- **original&#95;status** (`original_status`): historical&#95;rule&#95;candidate
- **current&#95;status** (`current_status`): refined&#95;common&#95;contract&#95;launch&#95;deferred
- **question** (`question`): 최소 실행·개발 환경
- **related&#95;later&#95;refs** (`related_later_refs`): D8 · CS-07 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### A1

- **ID** (`id`): A1
- **source&#95;ref** (`source_ref`): amend
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): A1
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;amendment
- **question** (`question`): 사전 확보 플랫폼 지식에 따라 사람의 최초 등록 업무를 대행; 원본과 플랫폼 요구 사항 사전 검사
- **related&#95;later&#95;refs** (`related_later_refs`): D1 · D2 · DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### A2

- **ID** (`id`): A2
- **source&#95;ref** (`source_ref`): amend
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): A2
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;amendment
- **question** (`question`): 실행 후 사용자 중단/변경/재개/rollback 없음; 오류 시에만 중단 후 결과 반환
- **related&#95;later&#95;refs** (`related_later_refs`): D5 · LD-07 · CS-05 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### A3

- **ID** (`id`): A3
- **source&#95;ref** (`source_ref`): amend
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): A3
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;amendment
- **question** (`question`): 멱등성은 키/논리 효과 식별을 기본 원칙으로 두고 물리 구현은 세부 설계
- **related&#95;later&#95;refs** (`related_later_refs`): D5 · C04 · CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### A4

- **ID** (`id`): A4
- **source&#95;ref** (`source_ref`): amend
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): A4
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;amendment
- **question** (`question`): 서버 원격 브라우저 구조 및 크몽 우선·숨고 확장 유지; 기술 위임, mock-only phase 유지
- **related&#95;later&#95;refs** (`related_later_refs`): D8 · DC8 · CS-04 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D1

- **ID** (`id`): D1
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): D1
- **original&#95;status** (`original_status`): R01&#95;agreed
- **current&#95;status** (`current_status`): R01&#95;agreed
- **question** (`question`): 하나의 고정 플랫폼 프로필 버전을 준비/실행/판정이 함께 참조
- **related&#95;later&#95;refs** (`related_later_refs`): LD-01 · LD-04 · DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D2

- **ID** (`id`): D2
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): D2
- **original&#95;status** (`original_status`): R01&#95;agreed
- **current&#95;status** (`current_status`): R01&#95;agreed
- **question** (`question`): 원본과 플랫폼 조건을 내부 검사, 불확실한 정보만 질문, 인증 후 한 번 최종 등록 정보 확인 및 실행 승인
- **related&#95;later&#95;refs** (`related_later_refs`): LD-05 · LD-06 · DC7 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D3

- **ID** (`id`): D3
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): D3
- **original&#95;status** (`original_status`): R01&#95;agreed&#95;refinement
- **current&#95;status** (`current_status`): R01&#95;agreed&#95;refinement
- **question** (`question`): 준비부터 결과까지 하나의 등록 요청 식별자, 수락 시 불변 실행 범위를 내부 snapshot으로 고정
- **related&#95;later&#95;refs** (`related_later_refs`): LD-02 · LD-06 · DC5 · CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D4

- **ID** (`id`): D4
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): D4
- **original&#95;status** (`original_status`): R01&#95;agreed
- **current&#95;status** (`current_status`): R01&#95;agreed
- **question** (`question`): 결과 판정 책임 분리, 신뢰할 수 있는 증거가 충분한 경우 추가 조회 없음; 프로필이 요구할 때만 readback
- **related&#95;later&#95;refs** (`related_later_refs`): LD-07 · DC6 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D5

- **ID** (`id`): D5
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): D5
- **original&#95;status** (`original_status`): R01&#95;agreed
- **current&#95;status** (`current_status`): R01&#95;agreed
- **question** (`question`): 업무상 의미 있는 단계와 외부 효과의 실행 전 기록/관측/결과만 보존, 기본 키 관리
- **related&#95;later&#95;refs** (`related_later_refs`): LD-07 · CS-05 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D6

- **ID** (`id`): D6
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): D6
- **original&#95;status** (`original_status`): delegated&#95;design
- **current&#95;status** (`current_status`): delegated&#95;design
- **question** (`question`): 원본 버전은 독립 재사용, 개별 플랫폼 답변/변환은 그 요청에만 적용; 공통 사실 변경은 명시적인 새 원본 버전
- **related&#95;later&#95;refs** (`related_later_refs`): LD-02 · DC1 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D7

- **ID** (`id`): D7
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `6`
  - **ID** (`id`): D7
- **original&#95;status** (`original_status`): delegated&#95;design&#95;candidate
- **current&#95;status** (`current_status`): delegated&#95;design&#95;candidate
- **question** (`question`): 사용자 HTTP는 원본과 등록 요청 두 업무 자원; 인증 명령은 등록 요청의 하위 동작; 내부 단계/승인/효과 관리 API 없음
- **related&#95;later&#95;refs** (`related_later_refs`): C03 · CS-02 · CS-03
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### D8

- **ID** (`id`): D8
- **source&#95;ref** (`source_ref`): detail
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `7`
  - **ID** (`id`): D8
- **original&#95;status** (`original_status`): deferred
- **current&#95;status** (`current_status`): deferred
- **question** (`question`): 구체적 DB 테이블/프레임워크/브라우저/배포 선택 미확정
- **related&#95;later&#95;refs** (`related_later_refs`): CS-07 · CS-08
- **note** (`note`): 11/27 독립 실행 결과 후 공통 기술 경계 결정.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C01

- **ID** (`id`): C01
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): C01
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): refined
- **question** (`question`): 공통 업무 데이터 3개 구조와 타입이 명시된 하위 값; 별도 테이블 수 미정
- **related&#95;later&#95;refs** (`related_later_refs`): LD-02 · DC1 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C02

- **ID** (`id`): C02
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): C02
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): superseded&#95;closed&#95;platform&#95;enum
- **question** (`question`): 공통 봉투는 닫힌 스키마, 실제 등록값은 플랫폼 프로필 타입과 별도 조건 검사
- **related&#95;later&#95;refs** (`related_later_refs`): LD-01 · LD-04 · DC2 · CS-01
- **note** (`note`): 공통 플랫폼 enum은 V4 개방 ID+registry로 대체.
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C03

- **ID** (`id`): C03
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): C03
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): refined
- **question** (`question`): 9개 업무 API 유지, 인증은 등록 요청의 open/finish/close/refresh 명령. 준비/인증 확인은 설정된 시간 내 응답, 실패는 실행 수락 전 안내; 실행만 비동기 job, GET 조회
- **related&#95;later&#95;refs** (`related_later_refs`): CS-02 · CS-03
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C04

- **ID** (`id`): C04
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): C04
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): refined
- **question** (`question`): 서버가 승인 범위 digest와 revision을 생성하고 start에서 원자 수락; 일반적인 요청 키·대상/동작 키
- **related&#95;later&#95;refs** (`related_later_refs`): CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C05

- **ID** (`id`): C05
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): C05
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): refined
- **question** (`question`): 준비/인증/실행/판정의 5개 업무 포트, 실행기는 의미 있는 단계 내 실제 mutation 경계에서만 durable admission; 판정은 프로필 증거
- **related&#95;later&#95;refs** (`related_later_refs`): CS-05 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C06

- **ID** (`id`): C06
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): C06
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): retained&#95;logical&#95;technology&#95;deferred
- **question** (`question`): 웹 UI + 하나의 논리 앱 + 공통 영속 저장소 + 격리된 원격 브라우저 실행 영역, 추가 microservice/메시지 브로커 없음; 같은 프로세스/별도 실행자 여부는 후속
- **related&#95;later&#95;refs** (`related_later_refs`): CS-07
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### C07

- **ID** (`id`): C07
- **source&#95;ref** (`source_ref`): iface
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `6`
  - **ID** (`id`): C07
- **original&#95;status** (`original_status`): candidate
- **current&#95;status** (`current_status`): retained&#95;mock&#95;only
- **question** (`question`): 지원 프로필과 실제 플랫폼 규칙의 검증 수준을 명시; 현재 두 mock value schema는 통합 설계 fixture, 실제 업체 필드나 팀원 독립 계약 강제 아님
- **related&#95;later&#95;refs** (`related_later_refs`): DC3 · DC4 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-01

- **ID** (`id`): LD-01
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `0`
  - **ID** (`id`): LD-01
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 공통 업무에서 사용하는 정보의 의미와 전달만 공통 계약으로 정의하고 플랫폼별 항목·타입·필수/조건부 제약·절차·완료 조건은 플랫폼 프로필이 정의한다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-02

- **ID** (`id`): LD-02
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `1`
  - **ID** (`id`): LD-02
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 원본(Source), 플랫폼 프로필(Profile), 등록 요청(Registration)의 3개 핵심 논리 구조를 유지한다. 준비·인증·승인 범위·진행·결과는 등록 요청에 속하는 정보이며 독립 업무 자원을 강제하지 않는다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC1 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-03

- **ID** (`id`): LD-03
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `2`
  - **ID** (`id`): LD-03
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 동일 의미의 정보는 동일 타입을 사용하며 데이터의 생성·수신·변경·검증 책임을 명시한다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC5 · DC6 · CS-01 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-04

- **ID** (`id`): LD-04
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `3`
  - **ID** (`id`): LD-04
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 등록값은 해당 프로필의 계약으로 검사한다. 공통 식별자는 특정 플랫폼 열거형에 묶지 않고 서버의 지원 프로필 조회 및 유효성 검사로 제한한다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC2 · CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-05

- **ID** (`id`): LD-05
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `4`
  - **ID** (`id`): LD-05
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 준비 결과는 등록값·정보 근거·문제를 전달한다. 준비 완료 여부는 필수 조건 충족 및 해결되지 않은 차단 문제 여부에서 도출하며 별도 독립 상태로 관리하지 않는다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC7 · CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-06

- **ID** (`id`): LD-06
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `5`
  - **ID** (`id`): LD-06
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 실행 범위는 승인된 등록값·원본/프로필 버전·인증된 계정 및 대상·확인된 연결을 결합하여 고정한다. 승인 참조는 등록 요청 내 고정 범위를 식별하며 별도 계획 생성이나 승인 관리 자원을 추가하지 않는다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC5 · CS-04 · CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-07

- **ID** (`id`): LD-07
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `6`
  - **ID** (`id`): LD-07
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 등록 결과는 목표 판정·확인된 수행/효과·관측 대상과 방식이 포함된 근거·오류를 제공한다. 목표 달성은 해당 프로필의 완료 조건으로 판정한다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC6 · CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### LD-08

- **ID** (`id`): LD-08
- **source&#95;ref** (`source_ref`): upper
- **locator** (`locator`)
  - **collection** (`collection`): principles
  - **index** (`index`): `7`
  - **ID** (`id`): LD-08
- **original&#95;status** (`original_status`): human&#95;agreed
- **current&#95;status** (`current_status`): human&#95;agreed&#95;upper&#95;contract
- **question** (`question`): 공통 타입·플랫폼 규칙·업무 관계·실행 조건·결과 검사를 각 책임 경계에서 수행한다. 논리 계약과 물리적 저장 및 코드 구조를 구분한다.
- **related&#95;later&#95;refs** (`related_later_refs`): DC8 · CS-07 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC1

- **ID** (`id`): DC1
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): DC1
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 원본의 불변 원문·자료, 등록 요청 내 fact/근거
- **related&#95;later&#95;refs** (`related_later_refs`): CS-02
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC2

- **ID** (`id`): DC2
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): DC2
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 프로필에 실제 입력값 스키마·제약·절차·완료 조건
- **related&#95;later&#95;refs** (`related_later_refs`): CS-01
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC3

- **ID** (`id`): DC3
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): DC3
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 크몽 패키지의 누락 화면 항목 및 모집 형태·지역·이미지 목록
- **related&#95;later&#95;refs** (`related_later_refs`): CS-01 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC4

- **ID** (`id`): DC4
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): DC4
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 숨고 서비스 설정과 고수 프로필/견적 분리
- **related&#95;later&#95;refs** (`related_later_refs`): CS-01 · CS-08
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC5

- **ID** (`id`): DC5
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): DC5
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 인증 결과의 내부 연결 바인딩을 승인 범위에 포함
- **related&#95;later&#95;refs** (`related_later_refs`): CS-04 · CS-05
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC6

- **ID** (`id`): DC6
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): DC6
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 관측 대상·방법·근거 연결과 프로필별 완료 조건
- **related&#95;later&#95;refs** (`related_later_refs`): CS-06
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC7

- **ID** (`id`): DC7
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `6`
  - **ID** (`id`): DC7
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 준비 완료는 검증의 계산값, 검사 책임 명시
- **related&#95;later&#95;refs** (`related_later_refs`): CS-02 · CS-03
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### DC8

- **ID** (`id`): DC8
- **source&#95;ref** (`source_ref`): data
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `7`
  - **ID** (`id`): DC8
- **original&#95;status** (`original_status`): delegated&#95;mock&#95;baseline
- **current&#95;status** (`current_status`): delegated&#95;mock&#95;design&#95;checked
- **question** (`question`): 기존 API 경계 유지, 세부 기술·미확인 항목만 보류
- **related&#95;later&#95;refs** (`related_later_refs`): CS-07 · CS-08 · CS-09
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): `[]`
- **work&#95;refs** (`work_refs`): `[]`

#### CS-01

- **ID** (`id`): CS-01
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `0`
  - **ID** (`id`): CS-01
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 플랫폼 지식과 업무 포트 연결 방식
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-03 · REQ-06 · REQ-07 · REQ-09
- **work&#95;refs** (`work_refs`): W01 · W03 · W06 · W08 · W10

#### CS-02

- **ID** (`id`): CS-02
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `1`
  - **ID** (`id`): CS-02
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 준비/수정/승인 및 사용자 API 경계
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-05 · REQ-08
- **work&#95;refs** (`work_refs`): W01 · W02 · W19 · W03 · W05

#### CS-03

- **ID** (`id`): CS-03
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `2`
  - **ID** (`id`): CS-03
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 동기 준비/인증과 비동기 실행, 오류 표현
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-04 · REQ-05 · REQ-08
- **work&#95;refs** (`work_refs`): W01 · W03 · W05

#### CS-04

- **ID** (`id`): CS-04
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `3`
  - **ID** (`id`): CS-04
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 인증 확인에서 실행으로 연결 및 UI viewer 경계
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **work&#95;refs** (`work_refs`): W04 · W05 · W07 · W11

#### CS-05

- **ID** (`id`): CS-05
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `4`
  - **ID** (`id`): CS-05
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 상태/승인/멱등성 및 외부 효과 직렬화
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-05 · REQ-08 · REQ-10
- **work&#95;refs** (`work_refs`): W03 · W04 · W07 · W11

#### CS-06

- **ID** (`id`): CS-06
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `5`
  - **ID** (`id`): CS-06
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 결과의 증거와 실패 판정
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-08 · REQ-10
- **work&#95;refs** (`work_refs`): W03 · W06 · W08 · W07 · W09

#### CS-07

- **ID** (`id`): CS-07
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `6`
  - **ID** (`id`): CS-07
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 최소 논리 통합 구조와 공통 저장 책임
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-04 · REQ-05 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **work&#95;refs** (`work_refs`): W01 · W03 · W04 · W05 · W06 · W08

#### CS-08

- **ID** (`id`): CS-08
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `7`
  - **ID** (`id`): CS-08
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 공통 시험 및 착수/통합 수용 기준
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **work&#95;refs** (`work_refs`): W01 · W07 · W09 · W14 · W17

#### CS-09

- **ID** (`id`): CS-09
- **source&#95;ref** (`source_ref`): common
- **locator** (`locator`)
  - **collection** (`collection`): decisions
  - **index** (`index`): `8`
  - **ID** (`id`): CS-09
- **original&#95;status** (`original_status`): provisional
- **current&#95;status** (`current_status`): provisional&#95;common&#95;baseline
- **question** (`question`): 설계 변경의 근거 추적 및 책임 배분
- **related&#95;later&#95;refs** (`related_later_refs`): `[]`
- **note** (`note`): `null`
- **요구 참조** (`requirement_refs`): REQ-09 · REQ-11
- **work&#95;refs** (`work_refs`): W01 · W07 · W17

### legacy_detail_refs

- **source** (`source`): v02
- **sections** (`sections`)
  - **[0] **
    - **file** (`file`): DETAIL-DATA-V0.2.md
    - **tables** (`tables`)
      - **[0] **
        - **title** (`title`): D-A. 요구에서 상세 계약으로
        - **row&#95;ids** (`row_ids`): DD-01 · DD-02 · DD-03 · DD-04
      - **[1] **
        - **title** (`title`): D-B. 공통 사실 사전
        - **row&#95;ids** (`row_ids`): F01 · F02 · F03 · F04 · F05 · F06 · F07 · F08 · F09 · F10 · F11 · F12 · F13 · F14 · F15
      - **[2] **
        - **title** (`title`): D-C. 논리 엔터티 필드와 무결성
        - **row&#95;ids** (`row_ids`): E01 · E02 · E03 · E04 · E05 · E06 · E07 · E08 · E09 · E10 · E11 · E12 · E13 · E14 · E15
      - **[3] **
        - **title** (`title`): D-D. 검증 및 변환 규칙
        - **row&#95;ids** (`row_ids`): M01 · M02 · M03 · M04 · M05 · M06
  - **[1] **
    - **file** (`file`): DETAIL-PLATFORM-FLOWS-V0.2.md
    - **tables** (`tables`)
      - **[0] **
        - **title** (`title`): P-A. 대상 및 목표
        - **row&#95;ids** (`row_ids`): P-K · P-S · P-T
      - **[1] **
        - **title** (`title`): P-B. 크몽 필드 매핑 후보
        - **row&#95;ids** (`row_ids`): K01 · K02 · K03 · K04 · K05 · K06 · K07 · K08 · K09 · K10
      - **[2] **
        - **title** (`title`): P-C. 크몽 실행 및 증거 체크포인트
        - **row&#95;ids** (`row_ids`): KF01 · KF02 · KF03 · KF04 · KF05 · KF06
      - **[3] **
        - **title** (`title`): P-D. 숨고 필드 매핑 후보
        - **row&#95;ids** (`row_ids`): Sg01 · Sg02 · Sg03 · Sg04 · Sg05 · Sg06 · Sg07 · Sg08 · Sg09
      - **[4] **
        - **title** (`title`): P-E. 숨고 실행 및 증거 체크포인트
        - **row&#95;ids** (`row_ids`): SF01 · SF02 · SF03 · SF04 · SF05 · SF06
      - **[5] **
        - **title** (`title`): P-F. 탈잉 확장 및 차이 보존
        - **row&#95;ids** (`row_ids`): Tg01 · Tg02 · Tg03 · Tg04
  - **[2] **
    - **file** (`file`): DETAIL-SYSTEM-V0.2.md
    - **tables** (`tables`)
      - **[0] **
        - **title** (`title`): S-A. 논리 모듈 상세
        - **row&#95;ids** (`row_ids`): C01a · C02a · C03a · C04a · C04b · C05a · C06a · C07a
      - **[1] **
        - **title** (`title`): S-B. 우리 서비스 사용자 흐름 (TO-BE, 화면 후보)
        - **row&#95;ids** (`row_ids`): U01 · U02 · U03 · U04 · U05 · U06 · U07 · U08
      - **[2] **
        - **title** (`title`): S-C. 논리 API → HTTP 후보 (구현 지시 아님)
        - **row&#95;ids** (`row_ids`): A01 · A02 · A03 · A04 · A05 · A06 · A07 · A08 · A09 · A10 · A11
      - **[3] **
        - **title** (`title`): S-D. 작업/관측/오류 상태 계약 보완
        - **row&#95;ids** (`row_ids`): ST01 · ST02 · ST03 · ST04 · ST05 · ST06 · ST07 · ST08
      - **[4] **
        - **title** (`title`): S-E. 원격 브라우저 후보 세션·제어권 수명주기
        - **row&#95;ids** (`row_ids`): RB01 · RB02 · RB03 · RB04 · RB05 · RB06 · RB07 · RB08
      - **[5] **
        - **title** (`title`): S-F. 보안·배치 후보와 기술 판단
        - **row&#95;ids** (`row_ids`): SEC01 · SEC02 · SEC03 · SEC04 · SEC05 · SEC06 · SEC07 · SEC08
  - **[3] **
    - **file** (`file`): DETAIL-VERIFICATION-V0.2.md
    - **tables** (`tables`)
      - **[0] **
        - **title** (`title`): V-A. 근거의 채택과 잔여 불일치
        - **row&#95;ids** (`row_ids`): EV01 · EV02 · EV03 · EV04 · EV05 · EV06
      - **[1] **
        - **title** (`title`): V-B. 검증 추적 매트릭스
        - **row&#95;ids** (`row_ids`): VT01 · VT02 · VT03 · VT04 · VT05 · VT06 · VT07 · VT08 · VT09 · VT10 · VT11
      - **[2] **
        - **title** (`title`): V-C. 설계·채택 게이트
        - **row&#95;ids** (`row_ids`): G1 · G2 · G3 · G4 · G5 · G6
      - **[3] **
        - **title** (`title`): V-D. 팀원 산출물 재사용 계획 (배정 아님)
        - **row&#95;ids** (`row_ids`): W01 · W02 · W03 · W04 · W05
- **scope** (`scope`): Earlier V0.2 detailed rows reference original table/evidence; not retrospectively reconstructed into standalone ADRs.

### current_trace

#### CS-01

- **ID** (`id`): CS-01
- **requirements** (`requirements`): REQ-02 · REQ-03 · REQ-06 · REQ-07 · REQ-09
- **prior** (`prior`): D1 · LD-01 · LD-04 · DC2
- **sources** (`sources`): data · profiles
- **targets** (`targets`): I1 · I2 · I4 · I5 · RUNTIME
- **planned&#95;checks** (`planned_checks`): T5-03 · T5-13 · DV-04 · AT-04 · AT-05
- **work&#95;candidates** (`work_candidates`): W01 · W03 · W06 · W08 · W10
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-02

- **ID** (`id`): CS-02
- **requirements** (`requirements`): REQ-01 · REQ-02 · REQ-03 · REQ-05 · REQ-08
- **prior** (`prior`): D2 · D3 · D6 · D7 · LD-02 · LD-05 · DC1 · DC7
- **sources** (`sources`): data · schema · iface
- **targets** (`targets`): H1 · H2 · H3 · H4 · H5 · H7 · I2 · STATE · UI
- **planned&#95;checks** (`planned_checks`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · T5-01 · T5-06
- **work&#95;candidates** (`work_candidates`): W01 · W02 · W19 · W03 · W05
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-03

- **ID** (`id`): CS-03
- **requirements** (`requirements`): REQ-01 · REQ-03 · REQ-04 · REQ-05 · REQ-08
- **prior** (`prior`): D2 · D3 · C03 · LD-06 · DC7
- **sources** (`sources`): iface · data · logic
- **targets** (`targets`): H4 · H5 · H6 · H7 · H8 · H9 · I2 · I3 · I4 · STATE · UI
- **planned&#95;checks** (`planned_checks`): T5-07 · AT-02 · T5-05 · DV-01 · DV-05
- **work&#95;candidates** (`work_candidates`): W01 · W03 · W05
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-04

- **ID** (`id`): CS-04
- **requirements** (`requirements`): REQ-04 · REQ-05 · REQ-10
- **prior** (`prior`): DIR-01 · DIR-02 · A4 · D3 · LD-06 · DC5
- **sources** (`sources`): direction · data · schema · phase
- **targets** (`targets`): H6 · I3 · I4 · VIEWER · RUNTIME · UI · STORE
- **planned&#95;checks** (`planned_checks`): AT-02 · AT-03 · T5-02 · DV-02 · DV-05
- **work&#95;candidates** (`work_candidates`): W04 · W05 · W07 · W11
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-05

- **ID** (`id`): CS-05
- **requirements** (`requirements`): REQ-05 · REQ-08 · REQ-10
- **prior** (`prior`): A2 · A3 · D3 · D5 · LD-06 · DC5 · C04 · C05
- **sources** (`sources`): top · amend · data · logic
- **targets** (`targets`): H7 · I4 · STATE · STORE · RUNTIME
- **planned&#95;checks** (`planned_checks`): T5-01 · AT-03 · T5-12 · DV-01 · DV-02 · DV-04
- **work&#95;candidates** (`work_candidates`): W03 · W04 · W07 · W11
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-06

- **ID** (`id`): CS-06
- **requirements** (`requirements`): REQ-06 · REQ-07 · REQ-08 · REQ-10
- **prior** (`prior`): A2 · D4 · D5 · LD-07 · DC6
- **sources** (`sources`): top · data · profiles
- **targets** (`targets`): I4 · I5 · H8 · H9 · STATE · UI
- **planned&#95;checks** (`planned_checks`): AT-04 · AT-05 · T5-13 · DV-01 · DV-03 · DV-04
- **work&#95;candidates** (`work_candidates`): W03 · W06 · W08 · W07 · W09
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-07

- **ID** (`id`): CS-07
- **requirements** (`requirements`): REQ-01 · REQ-04 · REQ-05 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **prior** (`prior`): DIR-02 · D8 · LD-08 · C06 · DC8 · B4-02 · R5-10
- **sources** (`sources`): direction · data · iface · phase · wbs
- **targets** (`targets`): INTEGRATION · STORE · RUNTIME · VIEWER · I1 · I2 · I3 · I4 · I5
- **planned&#95;checks** (`planned_checks`): T5-03 · T5-05 · T5-06 · AT-02 · DV-05
- **work&#95;candidates** (`work_candidates`): W01 · W03 · W04 · W05 · W06 · W08
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-08

- **ID** (`id`): CS-08
- **requirements** (`requirements`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **prior** (`prior`): A2 · A4 · LD-08 · DC8 · D8 · R5-09 · R5-11
- **sources** (`sources`): gate · trace · data · phase · wbs
- **targets** (`targets`): GATE · INTEGRATION
- **planned&#95;checks** (`planned_checks`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · AT-02 · AT-03 · T5-01 · T5-02 · T5-12 · T5-03 · T5-07 · AT-04 · AT-05 · T5-06 · T5-13 · T5-05 · DV-01 · DV-02 · DV-03 · DV-04 · DV-05
- **work&#95;candidates** (`work_candidates`): W01 · W07 · W09 · W14 · W17
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

#### CS-09

- **ID** (`id`): CS-09
- **requirements** (`requirements`): REQ-09 · REQ-11
- **prior** (`prior`): D8 · LD-08 · DC8
- **sources** (`sources`): trace · model · phase · wbs
- **targets** (`targets`): TRACE · INTEGRATION · GATE
- **planned&#95;checks** (`planned_checks`): T5-03 · DV-04
- **work&#95;candidates** (`work_candidates`): W01 · W07 · W17
- **work&#95;state** (`work_state`): proposed&#95;not&#95;assigned

### requirements

#### REQ-01

- **ID** (`id`): REQ-01
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): FR-01 · V3-R08
- **current&#95;decisions** (`current_decisions`): CS-02 · CS-03 · CS-07 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-01 · T5-08 · T5-11 · T6-01 · T5-06
- **note** (`note`): `null`

#### REQ-02

- **ID** (`id`): REQ-02
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): DIR-04 · V3-R02 · V3-R09
- **current&#95;decisions** (`current_decisions`): CS-01 · CS-02 · CS-08
- **planned&#95;checks** (`planned_checks`): T5-07
- **note** (`note`): `null`

#### REQ-03

- **ID** (`id`): REQ-03
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): FR-02 · V3-R08 · V3-R09 · V3-R12
- **current&#95;decisions** (`current_decisions`): CS-01 · CS-02 · CS-03 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-01 · T5-08 · T5-11 · T6-02 · T5-03 · T5-07 · DV-04
- **note** (`note`): `null`

#### REQ-04

- **ID** (`id`): REQ-04
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): DIR-01 · DIR-02 · V3-R01 · V3-R05 · V3-R11
- **current&#95;decisions** (`current_decisions`): CS-03 · CS-04 · CS-07 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-02 · T5-02 · T5-03 · DV-02 · DV-05
- **note** (`note`): `null`

#### REQ-05

- **ID** (`id`): REQ-05
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): FR-03 · V3-R01 · V3-R02 · V3-R03 · V3-R04 · V3-R05
- **current&#95;decisions** (`current_decisions`): CS-02 · CS-03 · CS-04 · CS-05 · CS-07 · CS-08
- **planned&#95;checks** (`planned_checks`): T6-02 · AT-03 · T5-01 · T5-02 · T5-12 · T5-07 · DV-01 · DV-02 · DV-04
- **note** (`note`): `null`

#### REQ-06

- **ID** (`id`): REQ-06
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): DIR-03 · FR-04 · V3-R07
- **current&#95;decisions** (`current_decisions`): CS-01 · CS-06 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-04 · T5-06 · T5-13 · DV-03
- **note** (`note`): `null`

#### REQ-07

- **ID** (`id`): REQ-07
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): DIR-03 · FR-04 · V3-R07
- **current&#95;decisions** (`current_decisions`): CS-01 · CS-06 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-05 · T5-06 · T5-13 · DV-03
- **note** (`note`): `null`

#### REQ-08

- **ID** (`id`): REQ-08
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): FR-05 · FR-06 · V3-R06 · V3-R07
- **current&#95;decisions** (`current_decisions`): CS-02 · CS-03 · CS-05 · CS-06 · CS-07 · CS-08
- **planned&#95;checks** (`planned_checks`): AT-04 · AT-05 · T5-05 · DV-01 · DV-03 · DV-05
- **note** (`note`): Legacy explicit resume clause superseded by A2 and CS-05/06; original retained.

#### REQ-09

- **ID** (`id`): REQ-09
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): DIR-04 · V3-R09
- **current&#95;decisions** (`current_decisions`): CS-01 · CS-07 · CS-08 · CS-09
- **planned&#95;checks** (`planned_checks`): T5-03 · AT-05 · T5-06 · T5-13 · DV-04
- **note** (`note`): `null`

#### REQ-10

- **ID** (`id`): REQ-10
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): V3-R05 · V3-R11
- **current&#95;decisions** (`current_decisions`): CS-04 · CS-05 · CS-06 · CS-07 · CS-08
- **planned&#95;checks** (`planned_checks`): T6-01 · AT-02 · AT-03 · T5-12 · T5-05 · DV-01 · DV-02 · DV-03 · DV-05
- **note** (`note`): `null`

#### REQ-11

- **ID** (`id`): REQ-11
- **source** (`source`): requirements
- **original&#95;prior&#95;refs** (`original_prior_refs`): V3-R13 · V3-R14
- **current&#95;decisions** (`current_decisions`): CS-07 · CS-08 · CS-09
- **planned&#95;checks** (`planned_checks`): T5-08 · T5-03
- **note** (`note`): `null`

### actual_evidence

- **design** (`design`)
  - **[0] **
    - **source** (`source`): validation
    - **kind** (`kind`): selected&#95;synthetic&#95;design&#95;check
    - **counts** (`counts`): 31/31 on V4 before V4.1; not integrated product
    - **refs** (`refs`): DC1 · DC2 · DC3 · DC4 · DC5 · DC6 · DC7
  - **[1] **
    - **source** (`source`): reviewEvidence
    - **kind** (`kind`): historical&#95;design&#95;review
    - **refs** (`refs`): C01 · C02 · C03 · C04 · C05 · C06 · C07
  - **[2] **
    - **source** (`source`): EV-R05-REMOTE-20261124
    - **kind** (`kind`): team&#95;reported&#95;local&#95;mock&#95;poc
    - **refs** (`refs`): DIR-01 · DIR-02 · CS-04
- **product&#95;verified&#95;by** (`product_verified_by`): `[]`
- **planned&#95;check&#95;relation** (`planned_check_relation`): planned&#95;check&#95;by; product test execution not run

### update_rule

- 원본 변경→source blob 확인→유효 레코드/관계 갱신→영향 후보 산출→담당 검토→정적 검사→사람용 뷰 재생성. 영향 후보는 자동 승인/무효화 또는 업무 배정이 아니다.

### limits

- Decision inventory covers explicit IDs LR-D01~06, DEC-01~17, DIR-01~04, B4-01~06, R5-01~11, A1~4, D1~8, C01~07, LD-01~08, DC1~8, CS-01~09. Earlier V0.2 rows are traceable to original tables, not retroactively authored decisions.
- Historical rationale not present in original remains unrecorded; new relations are retrospective review.
- No implementation assignment; WBS refs candidates. No physical stack closure/live approval.

