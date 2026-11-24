# V0.3 · 논리 데이터 및 API 계약

> [구조화 정본](data-api-v0.3.json) · [핵심 계약](CONTRACTS-V0.3.md). 논리 스키마이며 물리 DB/HTTP/정식 wire schema 또는 구현 완료를 의미하지 않는다.

## 타입

id는 불투명 참조, digest는 정규화할 내용 지문, timestamp는 절대 시각, []는 배열. json은 필드 규칙 검증 대상. 선택 필드는 생략 가능. JobState/EffectState/EffectClass는 핵심 계약 참조.

| enum | 값 |
| --- | --- |
| Environment | mock, live |
| Origin | user_input, source_extract, model_proposal, derived, platform_observation |
| Verification | unverified, confirmed, missing, conflicting, rejected |
| Requiredness | required, optional, conditional, unknown |
| Confidence | official, reported_observation, mock_assumption, unverified |
| Controller | none, human, automation |
| Auth | unverified, verified, expired, closed |
| IntentKind | create, update |
| Error | unauthenticated, not_authorized, not_found, stale_revision, approval_invalid, account_mismatch, identity_unverified, permission_denied, live_blocked, rule_unverified, input_conflict, rights_unknown, target_ambiguous, duplicate_risk, idempotency_conflict, lease_invalid, auth_required, effect_unknown, evidence_insufficient, operation_out_of_scope, validation_failed |


## 스키마

### Version

불변 버전 참조.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| version | positive_int | Y |

### Fact

confirmed는 확인 근거 필요, derived는 입력·식 필요. 누락/충돌 실행 차단.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| source | Version | Y |
| path | string | Y |
| value | json | N |
| unit | string | N |
| origin | Origin | Y |
| verification | Verification | Y |
| provenance | id[] | Y |
| derivation_inputs | id[] | N |
| formula | string | N |

### Media

파생 이미지 새 버전·지문, 실제 자료 금지.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| asset | Version | Y |
| digest | digest | Y |
| mime | string | Y |
| bytes | nonnegative_int | Y |
| width | positive_int | N |
| height | positive_int | N |
| rights_confirmed | boolean | Y |
| permitted_use | string[] | Y |
| parent | Version | N |

### FieldRule

조건/옵션/제약은 스냅샷에 속함. 미확인 규칙 확정 금지.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| key | string | Y |
| requiredness | Requiredness | Y |
| condition | json | N |
| value_type | string | Y |
| unit | string | N |
| options | json[] | N |
| constraints | json | Y |
| confidence | Confidence | Y |
| environment | Environment | Y |
| evidence | id[] | Y |
| checked_at | timestamp | Y |

### RuleSnapshot

규칙 변경 시 재승인.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| rule | Version | Y |
| platform | string | Y |
| object_kind | string | Y |
| fields | FieldRule[] | Y |
| flow_revision | positive_int | Y |
| evidence_spec | id | Y |
| environment | Environment | Y |

### Mapping

선택 필드 생략과 빈 값 구별.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| key | string | Y |
| value | json | N |
| unit | string | N |
| fact_refs | id[] | Y |
| transform_id | id | Y |
| verification | Verification | Y |
| issues | Error[] | Y |

### Account

합성 계정의 신뢰된 식별만. 표시명/쿠키 아님.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| account_ref | id | Y |
| owner_ref | id | Y |
| platform | string | Y |
| environment | Environment | Y |
| stable_subject_ref | id | Y |
| verified_at | timestamp | Y |
| evidence_ref | id | Y |
| revision | positive_int | Y |

### Target

안정 대상 키; 외부 객체 매핑 유일.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| environment | Environment | Y |
| platform | string | Y |
| account_ref | id | Y |
| object_kind | string | Y |
| slot_ref | id | Y |
| external_object_ref | id | N |

### Connection

자격증명 저장 없음.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| account_ref | id | N |
| platform | string | Y |
| environment | Environment | Y |
| auth | Auth | Y |
| revision | positive_int | Y |
| lease_generation | positive_int | Y |
| expires_at | timestamp | N |

### Lease

게이트웨이 강제 필요.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| connection_ref | id | Y |
| controller | Controller | Y |
| generation | positive_int | Y |
| expires_at | timestamp | Y |
| revoked | boolean | Y |

### Operation

동일 논리 효과의 ID 안정, 승인 범위에 결합.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| target | Target | Y |
| plan_revision | positive_int | Y |
| effect_class | EffectClass | Y |
| allowed_origin | id | Y |
| approved_fields | string[] | Y |
| before_spec | id | Y |
| after_spec | id | Y |
| evidence_spec | id | Y |
| digest | digest | Y |

### Approval

계정 확인 뒤 실행 승인. actor는 인증에서 도출.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| actor_ref | id | Y |
| source | Version | Y |
| draft | Version | Y |
| rule | Version | Y |
| media | Version[] | Y |
| target | Target | Y |
| goal | string | Y |
| plan_revision | positive_int | Y |
| operations | id[] | Y |
| digest | digest | Y |
| revision | positive_int | Y |
| revoked_at | timestamp | N |

### Permission

사용자 승인과 별도, live 차단.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| permission | Version | Y |
| environment | Environment | Y |
| platform | string | Y |
| object_kind | string | Y |
| allowed_actions | string[] | Y |
| policy_evidence | id[] | Y |
| allowed | boolean | Y |
| expires_at | timestamp | N |

### Intent

서버가 기존 대상/의도/효과 조회.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| target | Target | Y |
| kind | IntentKind | Y |
| goal | string | Y |
| source_ref | id | Y |
| revision | positive_int | Y |
| effect_refs | id[] | Y |

### Attempt

admission 기록은 외부 성공 아님.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| job_ref | id | Y |
| operation_ref | id | Y |
| account_ref | id | Y |
| approval_ref | id | Y |
| approval_revision | positive_int | Y |
| permission | Version | Y |
| lease_generation | positive_int | N |
| effect_state | EffectState | Y |
| admitted_at | timestamp | N |
| evidence_refs | id[] | Y |

### Evidence

계정/객체/환경/동작 일치, 비밀값 제외.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| job_ref | id | Y |
| attempt_ref | id | N |
| target | Target | Y |
| kind | string | Y |
| observed_at | timestamp | Y |
| values | json | Y |
| collector_ref | id | Y |
| redacted_artifact_ref | id | N |

### Result

append-only 결과.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| job_ref | id | Y |
| revision | positive_int | Y |
| goal | string | Y |
| state | JobState | Y |
| goal_evidence | id[] | Y |
| partial_effects | id[] | Y |
| unresolved_attempts | id[] | Y |
| retry_blocked | boolean | Y |
| reasons | Error[] | Y |

### ObjectObservation

job 완료와 별도 후속 관측.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| target | Target | Y |
| stage | string | Y |
| observed_at | timestamp | Y |
| evidence_refs | id[] | Y |
| revision | positive_int | Y |

### Job

가상 계정 simulator도 동일 가드.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| intent_ref | id | Y |
| approval_ref | id | Y |
| permission | Version | Y |
| connection_ref | id | N |
| state | JobState | Y |
| revision | positive_int | Y |
| operation_refs | id[] | Y |
| stop_reason | string | N |
| result | Result | N |

### SourceRequest

클라이언트 confirmed 주장은 서버 확인 필요.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| source_text | string | Y |
| facts | Fact[] | Y |
| media | Version[] | Y |
| previous | Version | N |
| key | string | Y |

### SourceResponse

누락/충돌 포함 검토용 버전 생성 가능.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| source | Version | Y |
| facts | Fact[] | Y |
| issues | Error[] | Y |

### MediaRequest

인증된 별도 업로드 경계.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| upload_ref | id | Y |
| rights_confirmed | boolean | Y |
| permitted_use | string[] | Y |
| key | string | Y |

### DraftRequest

계정 미연결 초안 가능.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| source | Version | Y |
| platform | string | Y |
| object_kind | string | Y |
| rule | Version | Y |
| goal | string | Y |
| key | string | Y |

### DraftResponse

검토 결과.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| draft | Version | Y |
| source | Version | Y |
| rule | Version | Y |
| mappings | Mapping[] | Y |
| media | Version[] | Y |
| issues | Error[] | Y |
| digest | digest | Y |

### DraftEdit

내용 의미 변경 시 원본 갱신.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| draft | Version | Y |
| edits | Mapping[] | Y |
| key | string | Y |

### ConnectRequest

mock only.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| platform | string | Y |
| environment | Environment | Y |
| key | string | Y |

### HandoffRequest

계정 식별자는 신뢰된 관측에서 도출.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| connection_ref | id | Y |
| expected_generation | positive_int | Y |
| controller | Controller | Y |
| key | string | Y |

### TargetRequest

문구만으로 신규 슬롯 우회 금지.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| connection_ref | id | Y |
| object_kind | string | Y |
| existing_slot | id | N |
| distinct_intent | string | N |
| goal | string | Y |
| key | string | Y |

### TargetResponse

계정 확인과 기존 효과 검사.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| target | Target | Y |
| account | Account | Y |
| eligible | boolean | Y |
| issues | Error[] | Y |

### ApprovalRequest

서버가 전체 범위 대조.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| source | Version | Y |
| draft | Version | Y |
| rule | Version | Y |
| media | Version[] | Y |
| target | Target | Y |
| goal | string | Y |
| plan_revision | positive_int | Y |
| operations | id[] | Y |
| digest | digest | Y |
| explicit_consent | boolean | Y |
| key | string | Y |

### JobRequest

intent_ref 서버 결정.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| target | Target | Y |
| goal | string | Y |
| kind | IntentKind | Y |
| approval_ref | id | Y |
| connection_ref | id | N |
| key | string | Y |

### DispatchRequest

내부 게이트웨이 전용.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| job_ref | id | Y |
| operation_ref | id | Y |
| expected_revision | positive_int | Y |
| expected_generation | positive_int | N |
| digest | digest | Y |

### DispatchResponse

실제 관측 별도 기록.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| attempt | Attempt | Y |
| job | Job | Y |

### ReconcileRequest

읽기 전용, 증거 출처 확인.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| job_ref | id | Y |
| expected_revision | positive_int | Y |
| evidence_refs | id[] | Y |
| key | string | Y |

### ResumeRequest

unknown 직접 실행 금지.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| job_ref | id | Y |
| expected_revision | positive_int | Y |
| approval_ref | id | Y |
| explicit_resume | boolean | Y |
| key | string | Y |

### StopRequest

취소·철회·종료.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| expected_revision | positive_int | Y |
| reason | string | Y |
| key | string | Y |

### ReadRequest

owner-scoped.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| ref | id | Y |
| after_revision | positive_int | N |

### ErrorResponse

타 사용자 존재/민감정보 노출 금지.

| 필드 | 타입 | 필수 |
| --- | --- | --- |
| code | Error | Y |
| message | string | Y |
| retry_blocked | boolean | Y |
| related_refs | id[] | Y |
| current_revision | positive_int | N |


## 논리 API

| ID | 동작 | 입력 | 출력 | 경계 |
| --- | --- | --- | --- | --- |
| V3-A01 | prepare_source | SourceRequest | SourceResponse | owner |
| V3-A02 | record_media | MediaRequest | Media | owner |
| V3-A03 | prepare_draft | DraftRequest | DraftResponse | owner |
| V3-A04 | edit_draft | DraftEdit | DraftResponse | owner |
| V3-A05 | connect_mock | ConnectRequest | Connection | owner |
| V3-A06 | handoff_verify | HandoffRequest | Connection | owner+gateway |
| V3-A07 | resolve_target | TargetRequest | TargetResponse | verified identity |
| V3-A08 | approve_execution | ApprovalRequest | Approval | owner |
| V3-A09 | request_job | JobRequest | Job | owner |
| V3-A10 | admit_dispatch | DispatchRequest | DispatchResponse | internal gateway |
| V3-A11 | read_result | ReadRequest | Result | owner read |
| V3-A12 | reconcile | ReconcileRequest | Job | authorized read |
| V3-A13 | resume | ResumeRequest | Job | owner |
| V3-A14 | cancel | StopRequest | Job | owner |
| V3-A15 | revoke | StopRequest | Approval | owner |
| V3-A16 | close_connection | StopRequest | Connection | owner+gateway |
| V3-A17 | read_object_observation | ReadRequest | ObjectObservation | owner read |


- 공통 ErrorResponse. mutation revision 또는 idempotency key 검사, owner는 인증에서 도출. 실제 wire schema/HTTP·DB·업로드 프로토콜 미확정.
- 뷰어 접속 비밀은 일반 응답 제외, 별도 단기 인증 경로. 실제 물리 강제는 PoC 필요.
- Operation의 효과/JobState/EffectState는 core-contract-v0.3.json 참조. 모든 ID 참조는 소유권·환경·버전 검사.
- 기존 V0.2 필드 매핑 및 공통 하네스 계약을 보존하며 여기서 명시한 의미만 교정.
