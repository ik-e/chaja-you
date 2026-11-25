# 공통 설계 최소 완결 · V1

2026-11-25 · R01 위임 범위 내 공통 논리 설계 결정. 물리 통합/신규 TASK/실서비스 실행은 승인하지 않는다.

## 기준 및 선택 근거

- [상위 논리 데이터 결정](logical-data-contract-decision-v1.json), [상세 데이터 V4](data-contract-v4.json), [공통 계약 V1](common-integration-v1.json), [스키마 V4.1](data-schema-v4.1.json), [플랫폼 프로필 V2](platform-profiles-v2.json).
- [기존 설계 체계에 연결한 결정 추적 V0.9](DECISION-TRACE-V0.9.md) · [구조화 조회 인덱스](trace-index-v0.9.json). 별도 일반 설계 모델을 만들지 않으며 원본 결정 및 과거 근거 상태 보존.
- V4.1은 등록 전 필드 수정 제안과 서버가 현재 질문 ID를 실제 필드에 연결한 정규화된 답변 타입만 추가한다. 신규 업무 API/상태 없음. 원본 사실의 변경은 새 버전, 플랫폼별 답변은 현재 요청에 한정. 승인 후 수정/취소/재개/rollback 없음.

| 결정 | 선택 | 핵심 근거 | 후속 재검토 |
|---|---|---|---|
| CS-01 | 기존 5개 업무 포트 및 버전 고정 registry; 값 스키마·절차·목표·작업 정의를 동일 참조로 조회. 새로운 업무 API/AI 재계획 없음. | S04/S09/S10의 필드·객체 차이를 독립 프로필로 보존하고 준비/실행/판정 규칙이 달라지지 않게 함. | 새 플랫폼 등록이 공통 계약 수정 없이 불가능하거나 같은 profile hash에서 내용이 다를 때 |
| CS-02 | 기존 /v1 API 9개 유지. H5는 현재 이슈 답변 외에 승인 전 표시 필드의 명시적 수정 제안을 허용. 서버가 현재 질문→field→answer_id를 확정하여 PREP에 전달하고 다시 검사. 원본 사실 변경은 새 Source, 플랫폼별 선택은 등록 요청에만. | V4 Answer에는 issue_id만 있어 PREP가 어떤 필드 답인지 모를 수 있고, 이슈 없는 표시값을 수정할 경로가 없다. 작은 타입 보완 2개로 최종 승인 1회와 원본 불변성 유지. 추가 계획 API 불필요. | 현 수정/질문 흐름으로 실제 사용자 오류 교정이 불가능할 때 |
| CS-03 | 원본/준비/인증 확인은 요청 내 완료 또는 명시적 오류/준비 이슈. 실행 H7은 durable 수락 직후 202, H8/9 저장 상태 조회. 오류 코드와 status mapping 통일. 준비·인증 시간 제한 수치는 구현 실험 후 설정. | 긴 브라우저 업무 수명을 UI 연결과 분리해야 하나 준비를 별도 job으로 만들 실측 근거 없음. 정상 업무 차단과 시스템 오류 구분. | 측정상 준비/인증이 요청 제한을 반복적으로 넘거나 UX 실패가 발생할 때 |
| CS-04 | AuthOutput 내부 binding 고정; public AuthResponse는 grant와 안전한 표시 정보만. runtime 담당 viewer mount/dispose 인터페이스 제공, UI는 인증 완료 버튼·현재 grant만 사용. finish에서 인간 입력 차단 후 identity/target 확인; 실행 승인 후 동일 binding의 worker lease. | R05 로컬 합성 PoC의 동일 맥락·뷰어 종료 독립 근거, 외부 계정과 실행 세션 불일치 방지. 제품 UI와 remote 내부 전송 기술을 결합하지 않음. | 11/27 원격 독립 구현이 동일 인증 맥락·제어권·격리를 입증하지 못할 때 |
| CS-05 | CO만 업무 상태 전이 소유, STORE 원자 accept/admit/fence/observe/terminal; runtime gateway에 등록된 Operation만 허용. 같은 key 재조회; 다른 key로 동일 효과 재발급 차단. 오류에만 stopping→stopped, 새 admission 금지, pending unknown 보존, user cancel/resume/rollback 없음. | 상위 I2/I3·A2 요구를 만족하는 최소 직렬화. 승인 범위와 실제 operation을 일치시키고, 브라우저 효과의 exactly-once는 주장하지 않음. | 경쟁/응답 유실 시험에서 중복·미승인 동작 또는 활성 작업 방치 발생 |
| CS-06 | EXEC가 실제 관측·EvidenceRecord를 기록, RESULT는 profile goal/method/target/payload/asset 확인, CO가 판정 저장. 두 mock은 독립 readback, 다른 지원 profile은 신뢰 가능한 응답 증거 허용. 완료와 게시 구분, stopped 이후 확인 근거 추가 가능하지만 상태 재개 없음. | S04/S07의 접수 ID 및 재조회 대조가 필요하다는 근거, 숨고는 설정 저장 대상이 다름. 근거가 부족하면 unknown. | 결과를 판정할 증거가 부족하거나 실제 완료 객체가 변경될 때 |
| CS-07 | 한 제품 root와 공통 계약, 서버/준비/브라우저/플랫폼/UI/테스트 경계. 저장소 하나의 논리 정본과 runtime 격리. 모듈 경계·호출과 소유권·stub 우선 결정; 언어/DB/패키지/물리 배포·launch 구현은 11/27 근거 후. | 5인 팀, 단일 등록 업무, 원자 수락과 상태 일관성이 중요. 기존 WBS W01 및 독립 작업 그대로, 별도 서비스 배포/동기화 비용을 먼저 지지 않음. | 독립 검증 결과로 shared dependency/transport/isolated runtime이 결정되거나 단일 앱이 요구를 못 충족할 때 |
| CS-08 | 22개 기존 제품 mock gate 유지 및 최신 의미로 갱신; T1~T6 독립 시험은 변경 없음. 동일 build/contract/fixture/environment 근거만, T5-08 실제 모델 시험 필수. stub을 기능 검증과 구분, 단계별 연결 기록. 12/8 크몽 우선/숨고 확장 미충족은 R01 판단. | 기존 test gate와 단계별 검증 체계 재사용. 다른 후보/환경/수동 대체 성공을 현재 전체 제품 성공으로 합산하지 않음. | 제품 범위·완료 조건·공통 계약이 변경되거나 공통 harness와 어댑터 결과가 확보될 때 |
| CS-09 | IT-19 결정 기록으로 원문/버전/요구/선행/대안/선택/검증/작업을 연결. V0.6 추적 이력 보존, V0.9 현재 투영 및 supersession. 과거 근거 부족은 unknown/후속 해석으로 표기. 작업 배분은 실제 phase 이후 단일 책임자로 확정. | 기존 설계 정보 모델과 trace가 이미 목적을 충족하며 재설계로 링크만 끊겼음. 원본 중복·상태 승격 방지. | 상위 의도/근거/계약/시험/작업 변경 때 영향 후보 검토 |

## 고정할 연결 경계

| 업무 인터페이스 | 입력 | 출력 | 책임 |
|---|---|---|---|
| I1 | selector:string | ResolveOutput | CO → KNOW |
| I2 | PrepareInput | Preparation | CO → PREP |
| I3 | AuthInput | AuthOutput | CO → EXEC |
| I4 | ExecuteInput | ExecutionReport | CO → EXEC |
| I5 | EvaluateInput | Result | CO → RESULT |

| HTTP | 목적 | 입력 | 응답 |
|---|---|---|---|
| H1 `POST /v1/sources` | 원본/첨부 생성 | SourceInput | SourceView; 201 |
| H2 `GET /v1/sources` | 원본 목록 | ListQuery | SourceList; 200 |
| H3 `GET /v1/sources/{id}` | 원본 조회 | 없음 | SourceView; 200 |
| H4 `POST /v1/registrations` | 등록 요청 생성 및 준비 | RegistrationInput | RegistrationView; 201 |
| H5 `PATCH /v1/registrations/{id}` | 등록 전 답변/수정 | PreparationEdit | RegistrationView; 200 |
| H6 `POST /v1/registrations/{id}/authentication` | 직접 인증 및 대상 확인 | AuthCommand | AuthResponse; 200 |
| H7 `POST /v1/registrations/{id}/start` | 최종 승인 및 작업 수락 | StartInput | RegistrationView; 202/200 |
| H8 `GET /v1/registrations/{id}` | 등록 상세 및 결과 조회 | 없음 | RegistrationView; 200 |
| H9 `GET /v1/registrations` | 등록 목록 | ListQuery | RegistrationList; 200 |

세부 호출 조건·오류·데이터 검사·저장 원자 경계·runtime gateway/viewer 제공 계약·UI 행동·통합 의존관계는 공통 계약 V1의 해당 항목이 정본이다. 실제 기술 및 내부 알고리즘은 담당자 위임. 정확한 작업 공간/공통 의존성/실행 명령/실제 stub package 및 adapter operation 등록은 11/27 통합 판단으로 남긴다.

## 검증 근거 및 종료 조건

- 기존 [설계 단계 검증기](../../../../tools/verify_design_stage.mjs), 기존 gate evaluator와 V4 검사기를 재사용한 [공통 계약 검증](validate-common-integration-v1.mjs) · [실행 결과](common-integration-validation-v1.json).
- 공통 검증 14/14, V4.1 스키마 참조 224/224, 기존 V4 검사 31/31, 신규 타입 예시 7/7, 합성 gate 판정 6/6, 결함 주입 6/6 탐지.
- 추적 인덱스 원문 source blob 38/38 일치, 결정/규칙 원본 위치 88/88 일치. 이전 설계 79개와 현재 결정 9개; V0.2 세부 표 행 157개는 원문 위치 보존. 과거 기록에 없는 이유를 소급 생성하지 않음.
- 검사 대상은 커밋 `485290a694a05db514855741d8d249a669507a10`, 인덱스 원문은 인덱스가 가리키는 각 고정 commit/blob. 위 검증은 JS 직접 실행 및 정적/합성 검사이며 실제 GitHub Actions/표준 JSON Schema 엔진/제품/DB 동시성/브라우저/실제 AI 검증은 아님. 22개 제품 시험은 **not_run**. 독립 T1~T6는 변경 없음.

## 남은 공통 착수 게이트 (11/27)

- 11/27 R01 independent R03/R04/R05 evidence review: common language/framework/DB/runtime transport/actual paths and commands, dependency lock, shared fixture/adapter manifest, minimal product skeleton smoke, single owners and WBS actual effort
- runtime operation registry exact action definitions, stable target resolution and physical atomic tests
- actual platform permission/goal/fields remain separate live gate

논리 공통 설계는 위임 결정과 선정 검증을 마쳤으나 **전체 공통 설계 종료 게이트는 미충족**: 실제 공통 실행 환경/작업 공간/공통 stub·실행 smoke/최종 단일 책임자 및 작업 배분을 확정해야 한다. 기존 PHASE-20261124-02와 TASK-043~045는 그대로 두며 실제 실행 승인·WBS 채택으로 처리하지 않는다.

## 변경 관리

기존 IT-19 원칙 적용: 원본 결정 변경 → source blob 확인 → 추적 관계와 영향 후보 갱신 → 관련 담당 검토 → 정적 검사 → 사람용 조회 뷰 갱신. 변경 영향은 자동 업무 할당이나 승인/무효화를 뜻하지 않는다. 독립 작업은 내부 설계를 위임하며 공통 계약/의존성에 영향을 주는 결정만 공동 검토한다.
