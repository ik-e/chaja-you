# 음악 레슨 강사 등록 지원 서비스 · API 설계 문서

> DLV-03 · 2026-11-25 · 기준 main f5e6857 · 채택 공통 V1/V4.1 반영 후보. R03 S8 실제 HTTP/OpenAPI 및 공식 제출·접수 미확인. [11/23 이전 후보](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/step2/API_설계_문서.md).

[현행 설계](../design/lesson-registration/CURRENT-DESIGN.md) · [공통 V1](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [V4.1 schema](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · [합성 요청/응답 원본](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/product/lesson-registration/fixtures/shared/replay.json) · [작성 가이드](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/Step2/API설계문서_작성법.html).

## 1. 공통 정보와 인증

| 항목 | 설계 |
| --- | --- |
| Base path | /v1, 배포 주소 미정, mock-only |
| 서비스 인증 | 서버 인증 컨텍스트의 owner, client owner_ref/승인 plan/상태/credentials 신뢰 금지. 실제 제품 인증 방식 미확정 |
| 외부 인증 | H6 직접 합성 인증; public AuthResponse grant 및 안전한 표시 정보만, 내부 ConnectionBinding 비공개 |
| API 문서 | FastAPI /docs/OpenAPI 실출력은 S8 이후 대조 |
| 스키마 | V4.1 named schema 및 profile별 schema, unknown 필드 거절, UTC timestamp, 관계·권한 가드 |
| 버전 | /v1이 현행, 이전 /api/v1 후보는 이력 |
| 오류 | Error {code,message,issues?,current_revision?}; stack trace·비밀 미반환 |

## 2. API 목록 및 요구사항

| ID | Method | Path | 역할 | 요구 | 정상 코드 |
| --- | --- | --- | --- | --- | --- |
| H1 | POST | `/v1/sources` | 원본/첨부 생성 | REQ-01/10 | 201 |
| H2 | GET | `/v1/sources` | 원본 목록 | REQ-01/10 | 200 |
| H3 | GET | `/v1/sources/{id}` | 원본 조회 | REQ-01/10 | 200 |
| H4 | POST | `/v1/registrations` | 등록 요청 생성 및 준비 | REQ-01/02/03 | 201 |
| H5 | PATCH | `/v1/registrations/{id}` | 등록 전 답변/수정 | REQ-03/05 | 200 |
| H6 | POST | `/v1/registrations/{id}/authentication` | 직접 인증 및 대상 확인 | REQ-04/05/10 | 200 |
| H7 | POST | `/v1/registrations/{id}/start` | 최종 승인 및 작업 수락 | REQ-05/06/07/08/10 | 202/200 |
| H8 | GET | `/v1/registrations/{id}` | 등록 상세 및 결과 조회 | REQ-08/10 | 200 |
| H9 | GET | `/v1/registrations` | 등록 목록 | REQ-08/10 | 200 |

## 3. 엔드포인트별 상세 계약

중첩 필드/enum/제약은 V4.1 named type을 따른다. 전체 요청/응답 예시는 [replay.json](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/product/lesson-registration/fixtures/shared/replay.json)의 platforms.kmong/soomgo.http에서 각 method/path로 확인 가능하다. 독립 합성 예시이며 실제 실행 세션 아님. H7 aaaa digest는 자리표시자이므로 유효 승인으로 쓰지 않는다.

### H1 · POST /v1/sources

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 원본/첨부 생성 · REQ-01/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | SourceInput; ID opaque, GET 목록은 query |
| 처리·권한 | owner 원본/첨부 불변 snapshot. JSON 또는 신규 파일 multipart manifest+정확한 part; 크기·MIME·바이트·권리·소유자·누락/초과/중복 part 검사. 외부 효과 없음. |
| 정상 코드/출력 | 201 · SourceView |
| 오류 코드 | INVALID_REQUEST, VALIDATION_FAILED, NOT_FOUND, PERMISSION_DENIED; 공통 401/403/404 |
| 요청 예시(합성) | `{"raw_text":"합성 레슨 소개"}` |
| 응답 예시 | SourceView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| raw_text | string | 필수 | minLength=0 |
| previous_source_id | Id | 선택 | V4.1 제약 |
| reuse_asset_ids | array<Id> | 선택 | 중복 금지 |
| new_assets | array<AssetInput> | 선택 | V4.1 제약 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| source_id | Id | 필수 | V4.1 제약 |
| previous_source_id | Id | 선택 | V4.1 제약 |
| raw_text | string | 필수 | minLength=0 |
| asset_refs | array<AssetRef> | 필수 | V4.1 제약 |
| created_at | Timestamp | 필수 | V4.1 제약 |

### H2 · GET /v1/sources

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 원본 목록 · REQ-01/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | ListQuery; ID opaque, GET 목록은 query |
| 처리·권한 | owner 목록, cursor/limit(기본 20, 1~100), created_at DESC/source_id DESC, 종료 시 next_cursor 생략. |
| 정상 코드/출력 | 200 · SourceList |
| 오류 코드 | INVALID_REQUEST, NOT_FOUND; 공통 401/403/404 |
| 요청 예시(합성) | `GET /v1/sources?limit=20` |
| 응답 예시 | SourceList; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| cursor | Id | 선택 | V4.1 제약 |
| limit | integer | 선택 | min=1, max=100 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| items | array<SourceSummary> | 필수 | V4.1 제약 |
| next_cursor | Id | 선택 | V4.1 제약 |

### H3 · GET /v1/sources/{id}

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 원본 조회 · REQ-01/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | 본문 없음; ID opaque, GET 목록은 query |
| 처리·권한 | owner의 불변 원본만 조회, 다른 owner/없는 ID 404. |
| 정상 코드/출력 | 200 · SourceView |
| 오류 코드 | NOT_FOUND; 공통 401/403/404 |
| 요청 예시(합성) | `GET /v1/sources/source-kmong` |
| 응답 예시 | SourceView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| — | — | — | 본문 없음 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| source_id | Id | 필수 | V4.1 제약 |
| previous_source_id | Id | 선택 | V4.1 제약 |
| raw_text | string | 필수 | minLength=0 |
| asset_refs | array<AssetRef> | 필수 | V4.1 제약 |
| created_at | Timestamp | 필수 | V4.1 제약 |

### H4 · POST /v1/registrations

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 등록 요청 생성 및 준비 · REQ-01/02/03 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | RegistrationInput; ID opaque, GET 목록은 query |
| 처리·권한 | source 소유 확인, 고정 selector registry, 지원 시 PREP. 미지원/차단/model issue는 저장 가능한 정상 view. job_state=null. |
| 정상 코드/출력 | 201 · RegistrationView |
| 오류 코드 | NOT_FOUND, INVALID_REQUEST, VALIDATION_FAILED, MODEL_UNAVAILABLE; 공통 401/403/404 |
| 요청 예시(합성) | `{"source_id":"source-kmong","selector":"kmong"}` |
| 응답 예시 | RegistrationView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| source_id | Id | 필수 | V4.1 제약 |
| selector | string | 필수 | minLength=1, maxLength=2048 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| registration_id | Id | 필수 | V4.1 제약 |
| source_id | Id | 필수 | V4.1 제약 |
| revision | Revision | 필수 | V4.1 제약 |
| support | supported / unsupported / blocked | 필수 | V4.1 제약 |
| profile_ref | ProfileRef | 선택 | V4.1 제약 |
| preparation | Preparation | 필수 | V4.1 제약 |
| auth | AuthView | 필수 | V4.1 제약 |
| target | TargetView | 선택 | V4.1 제약 |
| review | ReviewView | 선택 | V4.1 제약 |
| job_state | union | 필수 | V4.1 제약 |
| progress | Progress | 선택 | V4.1 제약 |
| result | Result | 선택 | V4.1 제약 |

### H5 · PATCH /v1/registrations/{id}

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 등록 전 답변/수정 · REQ-03/05 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | PreparationEdit; ID opaque, GET 목록은 query |
| 처리·권한 | prestart/current revision만. human/verifying는 먼저 close. source/selector 변경 시 오래된 답변 혼합 금지, 현재 issue→field 및 JSON Pointer 정정 검사. 원본 사실 변경은 새 Source. material 변경 시 review/binding 무효화. |
| 정상 코드/출력 | 200 · RegistrationView |
| 오류 코드 | INVALID_REQUEST, NOT_FOUND, STALE_REVISION, INVALID_PHASE, VALIDATION_FAILED, FACT_CONFLICT, PROFILE_CHANGED; 공통 401/403/404 |
| 요청 예시(합성) | `{"expected_revision":1,"corrections":[{"field":"/title","value":"합성 음악 레슨 안내 제목"}]}` |
| 응답 예시 | RegistrationView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| expected_revision | Revision | 필수 | V4.1 제약 |
| source_id | Id | 선택 | V4.1 제약 |
| selector | string | 선택 | minLength=1, maxLength=2048 |
| answers | array<Answer> | 선택 | V4.1 제약 |
| corrections | array<FieldCorrection> | 선택 | V4.1 제약 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| registration_id | Id | 필수 | V4.1 제약 |
| source_id | Id | 필수 | V4.1 제약 |
| revision | Revision | 필수 | V4.1 제약 |
| support | supported / unsupported / blocked | 필수 | V4.1 제약 |
| profile_ref | ProfileRef | 선택 | V4.1 제약 |
| preparation | Preparation | 필수 | V4.1 제약 |
| auth | AuthView | 필수 | V4.1 제약 |
| target | TargetView | 선택 | V4.1 제약 |
| review | ReviewView | 선택 | V4.1 제약 |
| job_state | union | 필수 | V4.1 제약 |
| progress | Progress | 선택 | V4.1 제약 |
| result | Result | 선택 | V4.1 제약 |

### H6 · POST /v1/registrations/{id}/authentication

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 직접 인증 및 대상 확인 · REQ-04/05/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | AuthCommand; ID opaque, GET 목록은 query |
| 처리·권한 | prestart/ready/current revision. open/refresh grant, finish에서 인간 입력 차단 후 계정·대상·binding 확인, existing/ambiguous이면 review 없음. close prestart만, stale generation 거절, timeout 폐기. detach≠close. |
| 정상 코드/출력 | 200 · AuthResponse |
| 오류 코드 | INVALID_REQUEST, NOT_FOUND, STALE_REVISION, INVALID_PHASE, AUTH_REQUIRED, ACCOUNT_MISMATCH, CONNECTION_MISMATCH, PERMISSION_DENIED, RUNTIME_ERROR; 공통 401/403/404 |
| 요청 예시(합성) | `{"action":"open","expected_revision":1} 또는 {"action":"finish","expected_revision":2,"generation":1}` |
| 응답 예시 | AuthResponse; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| open.action | "open" | 필수 | V4.1 제약 |
| open.expected_revision | Revision | 필수 | V4.1 제약 |
| finish.action | "finish" | 필수 | V4.1 제약 |
| finish.expected_revision | Revision | 필수 | V4.1 제약 |
| finish.generation | Revision | 필수 | V4.1 제약 |
| close.action | "close" | 필수 | V4.1 제약 |
| close.expected_revision | Revision | 필수 | V4.1 제약 |
| close.generation | Revision | 필수 | V4.1 제약 |
| refresh.action | "refresh" | 필수 | V4.1 제약 |
| refresh.expected_revision | Revision | 필수 | V4.1 제약 |
| refresh.generation | Revision | 필수 | V4.1 제약 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| registration | RegistrationView | 필수 | V4.1 제약 |
| grant | AuthGrant | 선택 | V4.1 제약 |

### H7 · POST /v1/registrations/{id}/start

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 최종 승인 및 작업 수락 · REQ-05/06/07/08/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | StartInput; ID opaque, GET 목록은 query |
| 처리·권한 | owner 확인 후 exact key replay를 stale/phase보다 먼저. 현재 review/revision·ready·new target·verified binding·permission 원자 검증. snapshot/key/active 저장 후 202. 같은 key·요청은 200, 충돌/중복 409. 수락 후 오류는 저장 결과. |
| 정상 코드/출력 | 202 / 200 · RegistrationView |
| 오류 코드 | INVALID_REQUEST, NOT_FOUND, STALE_REVISION, APPROVAL_INVALID, INVALID_PHASE, AUTH_REQUIRED, ACCOUNT_MISMATCH, CONNECTION_MISMATCH, TARGET_AMBIGUOUS, DUPLICATE_RISK, IDEMPOTENCY_CONFLICT, PERMISSION_DENIED, PROFILE_CHANGED; 공통 401/403/404 |
| 요청 예시(합성) | `{"expected_revision":3,"review_digest":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","approved":true,"request_key":"synthetic-start-kmong"}` |
| 응답 예시 | RegistrationView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| expected_revision | Revision | 필수 | V4.1 제약 |
| review_digest | Digest | 필수 | V4.1 제약 |
| approved | true | 필수 | V4.1 제약 |
| request_key | string | 필수 | minLength=1, maxLength=128 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| registration_id | Id | 필수 | V4.1 제약 |
| source_id | Id | 필수 | V4.1 제약 |
| revision | Revision | 필수 | V4.1 제약 |
| support | supported / unsupported / blocked | 필수 | V4.1 제약 |
| profile_ref | ProfileRef | 선택 | V4.1 제약 |
| preparation | Preparation | 필수 | V4.1 제약 |
| auth | AuthView | 필수 | V4.1 제약 |
| target | TargetView | 선택 | V4.1 제약 |
| review | ReviewView | 선택 | V4.1 제약 |
| job_state | union | 필수 | V4.1 제약 |
| progress | Progress | 선택 | V4.1 제약 |
| result | Result | 선택 | V4.1 제약 |

### H8 · GET /v1/registrations/{id}

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 등록 상세 및 결과 조회 · REQ-08/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | 본문 없음; ID opaque, GET 목록은 query |
| 처리·권한 | owner 저장된 상세/결과 조회. GET 외부 readback/변경 없음, UI revision 역전 무시. |
| 정상 코드/출력 | 200 · RegistrationView |
| 오류 코드 | NOT_FOUND; 공통 401/403/404 |
| 요청 예시(합성) | `GET /v1/registrations/registration-kmong` |
| 응답 예시 | RegistrationView; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| — | — | — | 본문 없음 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| registration_id | Id | 필수 | V4.1 제약 |
| source_id | Id | 필수 | V4.1 제약 |
| revision | Revision | 필수 | V4.1 제약 |
| support | supported / unsupported / blocked | 필수 | V4.1 제약 |
| profile_ref | ProfileRef | 선택 | V4.1 제약 |
| preparation | Preparation | 필수 | V4.1 제약 |
| auth | AuthView | 필수 | V4.1 제약 |
| target | TargetView | 선택 | V4.1 제약 |
| review | ReviewView | 선택 | V4.1 제약 |
| job_state | union | 필수 | V4.1 제약 |
| progress | Progress | 선택 | V4.1 제약 |
| result | Result | 선택 | V4.1 제약 |

### H9 · GET /v1/registrations

| 항목 | 계약 |
| --- | --- |
| 목적/요구 | 등록 목록 · REQ-08/10 |
| 인증·헤더 | 서버 검증 owner, JSON Content-Type(H1 새 파일만 multipart) |
| 경로/입력 | ListQuery; ID opaque, GET 목록은 query |
| 처리·권한 | owner 등록 목록, owner-bound cursor/limit, 생성순서·등록 ID 정렬, 내부 비밀 미노출. |
| 정상 코드/출력 | 200 · RegistrationList |
| 오류 코드 | INVALID_REQUEST, NOT_FOUND; 공통 401/403/404 |
| 요청 예시(합성) | `GET /v1/registrations?limit=20` |
| 응답 예시 | RegistrationList; 아래 필드와 고정 replay.http의 method/path별 JSON 참조 |

**입력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| cursor | Id | 선택 | V4.1 제약 |
| limit | integer | 선택 | min=1, max=100 |

**출력 필드**

| 필드 | 타입/참조 | 필수 여부 | 제약 |
| --- | --- | --- | --- |
| items | array<RegistrationSummary> | 필수 | V4.1 제약 |
| next_cursor | Id | 선택 | V4.1 제약 |


공통 409 예시(합성): `{"code":"STALE_REVISION","message":"등록 정보가 변경되었습니다.","current_revision":4}`. 다른 owner에 현재 revision을 공개하지 않는다.

## 4. 입력·권한 검증 및 공통 오류

| HTTP | Error.code |
| --- | --- |
| 400 | INVALID_REQUEST |
| 401 | UNAUTHENTICATED |
| 403 | PERMISSION_DENIED |
| 404 | NOT_FOUND |
| 409 | STALE_REVISION, APPROVAL_INVALID, IDEMPOTENCY_CONFLICT, INVALID_PHASE, ACCOUNT_MISMATCH, CONNECTION_MISMATCH, TARGET_AMBIGUOUS, DUPLICATE_RISK, PROFILE_CHANGED |
| 422 | VALIDATION_FAILED, FACT_CONFLICT, AUTH_REQUIRED, UNSUPPORTED_TARGET |
| 503 | MODEL_UNAVAILABLE, RUNTIME_ERROR |

EFFECT_UNKNOWN/EVIDENCE_INSUFFICIENT는 수락 후 결과에만 사용. 예상 밖 내부 장애는 안전한 500/RUNTIME_ERROR. 저장 가능한 H4 unsupported/blocked/model issue는 정상 RegistrationView. H7 가드 미충족 시 외부 효과 0, 동일 key 재조회와 외부 동작 재실행 구분. mock-only. [PR #44 세부 권한/보안 후보](https://github.com/ik-e/chaja-you/pull/44)는 검토 중.

## 5. Tool 정의 및 실행 계약

| ID | 호출 → 제공 | 입력 → 출력 | 제약 |
| --- | --- | --- | --- |
| I1 | CO → KNOW | selector:string → ResolveOutput | 고정 registry, 임의 URL 금지 |
| I2 | CO → PREP | PrepareInput → Preparation | source/profile/answers, 출처·질문·검증, 실행 권한 없음 |
| I3 | CO → EXEC | AuthInput → AuthOutput | 현재 auth/generation/target, 내부 binding |
| I4 | CO → EXEC | ExecuteInput → ExecutionReport | AcceptedScope·exclusive lease·등록 operation, 실제 관측 |
| I5 | CO → RESULT | EvaluateInput → Result | 신뢰 가능한 저장 evidence로 판정, 외부 동작 없음 |

[공통 Python Protocol](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/product/lesson-registration/contracts/interfaces.py)의 with_verified_connection/list_operations/perform/observe_goal 및 STORE accept/admit/record_observation/fence/finalize는 내부 경계, 외부 API나 자유 LLM Tool 아님. adapter는 BoundGateway만 사용. Viewer mount/dispose 및 CDP+WebSocket 방향, 세부 메시지·grant/claim/permit은 PR #44 검토 후보. PREP는 인증정보/브라우저 조작 권한 없음.

## 6. Timeout·재시도·멱등성과 검증

| 상황 | 계약 |
| --- | --- |
| PREP/인증 timeout | bounded, blocking issue 또는 typed error, 허위 ready/verified 금지; 수치 실측 후 |
| H7 응답 유실 | 동일 key/동일 요청으로 수락 조회, 다른 payload/key로 중복 실행 금지 |
| 외부 효과 유실 | fence, known/unknown 보존; 잠재 효과 자동 재실행 금지 |
| 종료 | CO 단일 전이, active→done 또는 active→stopping→stopped, 수락 이후 취소/수정/재개/rollback 없음 |
| 조회 | H8/H9 persisted view, GET 외부 동작 없음, detach≠cancel |
| 검증 | 동일 후보 22개 제품 gate 및 T5-08 실제 모델. S8 route/OpenAPI, DB 매핑, 권한·경쟁 실제 시험 이후 갱신 |

현재 문서는 채택 설계의 제출용 사본이며 실제 HTTP 동작/제품·운영 보안 완료 증거가 아니다.
