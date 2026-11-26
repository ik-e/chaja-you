# 음악 레슨 강사 등록 지원 서비스 · API 설계 문서

> DLV-03 · 2026-11-26 · 강사 1차 피드백 반영 개정 후보. 기준 ced14b6. 현행 H1~H9/V4.1은 이전 mock 계약의 구체 예시이며, V1.2 사용자 스토리·DB 이후 새 API는 별도 확정. PostgreSQL 목표, 현행 SQLite 시험 이력 및 실제 전환 미완료. [보완 기록](../artifacts/planning/lesson-registration-20261123/instructor-feedback-20261126.json).

[현행 설계](../design/lesson-registration/CURRENT-DESIGN.md) · [공통 V1](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [V4.1 schema](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · [합성 요청/응답 원본](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/product/lesson-registration/fixtures/shared/replay.json) · [작성 가이드](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/Step2/API설계문서_작성법.html).

## 0. 현행 V1.2 설계 입력과 기존 API의 관계

V1.2에서 신규·추가 등록뿐 아니라 기존 게시물 연결/수정/갱신 및 상태 관리가 설계 입력이다. TASK-055~058로 범위를 확정하고 DB 설계 이후 API·프로토콜을 구체화한다. 아래 H1~H9·I1~I5는 구현 및 시험 이력이 있는 **이전 최초 등록 mock 계약**을 사례로 문서화한 것이다. 새 기능의 endpoint·상태/식별자를 확정하지 않는다.

| V1.2 사용자 행동/피처 | 기존 API 재사용/검토 입력 | 새 DB 이후 결정할 계약 |
| --- | --- | --- |
| 원본 입력·재사용·수정 F01~F05 | H1~H3 불변 원본/버전 | 원본·버전·삭제/연결 해제의 범위 및 소유권 |
| 지원 업무/대상·준비 F06~F11 | H4/H5, I1/I2, Preparation | 플랫폼×업무 지원/제약, 대상 객체 및 충돌/질문/정정 |
| 인증·계정·기존 객체·차이·승인 F12~F18 | H6/H7 | 서비스 인증, 외부 계정 권한·업무별 대상 및 승인 전후 snapshot |
| 신규/수정/갱신 F19~F21 | H7/I4는 최초 등록 사례 | 외부 객체 식별, 독립 업무 ID/operation 종류/동시성 및 오류 |
| 결과·이력·상태 조회/갱신 F22~F29 | H8/H9/I5 | job vs 플랫폼 고유 상태, last observed/조회 실패, 새 상태 갱신 요청·후속 조치 |

[R02 조사 원본](https://github.com/ik-e/chaja-you/blob/bb73955af88c4c7b41255f0d8b5c5c2de213d2cd/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json)은 아직 진행 중; R01 승인 통합 스토리·DB 없음. 따라서 신규/수정/갱신/상태 갱신 계약은 설계 입력으로만 표시한다. 현재 응답 예시와 강사 피드백 보완은 기존 계약의 정확한 표현 및 후속 설계 조건이다. [실제 설계 입력](../artifacts/planning/lesson-registration-20261126/instructor-api-db-design-inputs.json).

## 1. 공통 정보와 인증

| 항목 | 설계 |
| --- | --- |
| Base path | /v1, 배포 주소 미정, mock-only |
| 서비스 인증 | 현행 서버 owner_resolver 주입 / 명시 활성화한 loopback X-Mock-Owner만 시험용. 제품은 서버가 인증된 앱 계정→owner를 확인; 클라이언트 owner_ref/승인·상태/credential 신뢰 금지. 실제 로그인 방식은 설계 후보 |
| 외부 인증 | H6 직접 합성 인증; public AuthResponse grant 및 안전한 표시 정보만, 내부 ConnectionBinding 비공개 |
| API 문서 | 현재 S8은 /docs, /redoc, /openapi.json 비활성화. 계약 schema/replay 기반 문서; 실제 배포 공개 여부 미정 |
| 스키마 | V4.1 named schema 및 profile별 schema, unknown 필드 거절, UTC timestamp, 관계·권한 가드 |
| 버전 | /v1이 현행, 이전 /api/v1 후보는 이력 |
| 오류 | Error {code,message,issues?,current_revision?}; stack trace·비밀 미반환 |

### 1.1 서비스 자체 인증과 외부 인증 구분

서비스 로그인(우리 서비스의 사용자)과 H6의 외부 레슨 플랫폼 인증은 별도이다. 현재 앱은 trusted owner_resolver 또는 명시 활성화한 loopback X-Mock-Owner 중 하나만 사용한다. 개발 헤더는 실제 신원 인증이 아니며 외부 배포에서 금지한다. 일반 사용자 요청·viewer WebSocket의 owner를 같은 서버 검증 컨텍스트에서 확인하고 외부 grant로 owner를 파생하지 않는다.

**제품 설계 후보:** 같은 origin의 서버 검증 앱 세션(HTTPS, HttpOnly/Secure/SameSite 쿠키, 세션 만료·로그아웃, 변경 요청 CSRF/Origin 검사 및 WS origin·owner·registration 검증). 세션/인증 방식 자체와 실제 가입·로그인·계정 삭제는 사용자 스토리 범위 결정 후 확정한다. 토큰·비밀번호·외부 세션 입력을 업무 DB/증거에 저장하지 않는다. 실제 서비스 인증 미구현.

| 요청·조건 | 서버 처리 | 응답 예시(합성, 시험 전) |
| --- | --- | --- |
| GET /v1/sources/{id}, 인증 없음/만료 | 검증된 owner 없음, 저장소 접근 전 거절 | 401 `{"code":"UNAUTHENTICATED","message":"인증이 필요합니다."}` |
| GET /v1/registrations/{id}, 타 owner | 존재 여부나 상태를 공개하지 않음 | 404 `{"code":"NOT_FOUND","message":"등록 정보를 찾을 수 없습니다."}` |
| H4/H7, 원본/등록이 타 owner | 연결·수락·외부 효과 0, 404 | 위 NOT_FOUND 예시 |
| 검증된 본인, 업무 권한 제한 | permission 확인 실패 시 거절 | 403 PERMISSION_DENIED (외부 효과 0) |

[현행 HTTP owner 처리](https://github.com/ik-e/chaja-you/blob/ced14b622dca5b1c96aeb0e8cf73b5668bfba458/product/lesson-registration/src/lesson_registration/app/http/api.py) · [실제 설계 입력](../artifacts/planning/lesson-registration-20261126/instructor-api-db-design-inputs.json).

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

### 3.1 공통 응답 중첩 필드와 읽기용 예시

H4/H5/H7/H8이 공유하는 RegistrationView의 실제 V4.1 정의를 풀어 쓴다. H7 첫 수락에서 새로운 job_id를 반환하지 않고 registration_id를 반환한다. 현행 mock에서는 등록당 작업 0..1이며 H8은 같은 ID로 조회한다. V1.2의 추가·수정·갱신 작업 식별자는 확정 스토리 및 새 DB 모델에서 재검토한다.

**RegistrationView**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| registration_id | Id | 필수 |
| source_id | Id | 필수 |
| revision | Revision | 필수 |
| support | supported / unsupported / blocked | 필수 |
| profile_ref | ProfileRef | 선택 |
| preparation | Preparation | 필수 |
| auth | AuthView | 필수 |
| target | TargetView | 선택 |
| review | ReviewView | 선택 |
| job_state | null / JobState | 필수 |
| progress | Progress | 선택 |
| result | Result | 선택 |

**Preparation**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| ready | boolean | 필수 |
| values | Values | 필수 |
| facts | array&lt;Fact&gt; | 필수 |
| issues | array&lt;Issue&gt; | 필수 |
| provenance | array&lt;Provenance&gt; | 필수 |

**Issue**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| issue_id | Id | 필수 |
| field | Id | 필수 |
| code | missing / conflict / invalid / rule_unverified / rights_unknown / unsupported / permission_denied / model_unavailable | 필수 |
| message | Text | 필수 |
| blocking | boolean | 필수 |

**Fact**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| fact_id | Id | 필수 |
| path | Id | 필수 |
| value | Value | 필수 |
| origin | FactOrigin | 필수 |

**FactOrigin**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| kind | source / answer | 필수 |
| ref | Id | 필수 |
| locator | Text | 필수 |

**Provenance**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| field | Id | 필수 |
| kind | direct / wording / selection / derived / user_choice | 필수 |
| fact_refs | array&lt;Id&gt; | 필수 |
| note | Text | 선택 |

**AuthView**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| state | none / human / verifying / verified / closed | 필수 |
| generation | Revision | 선택 |
| account_label | Text | 선택 |

**Progress**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| step_index | integer | 필수 |
| step_count | integer | 필수 |
| confirmed_steps | array&lt;StepView&gt; | 필수 |
| current_step | StepView | 선택 |

**StepView**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| step_id | Id | 필수 |
| label | Text | 필수 |
| status | pending / confirmed / absent / unknown / error | 필수 |

**Result**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| goal_verdict | GoalVerdict | 필수 |
| environment | Environment | 필수 |
| effects | array&lt;EffectSummary&gt; | 필수 |
| evidence | array&lt;EvidenceView&gt; | 필수 |
| error | Error | 선택 |
| next_action | Text | 필수 |

**EffectSummary**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| step_id | Id | 필수 |
| operation_id | Id | 필수 |
| verdict | confirmed / absent / unknown | 필수 |
| evidence_refs | array&lt;Id&gt; | 필수 |

**EvidenceView**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| evidence_id | Id | 필수 |
| kind | operation / goal / error | 필수 |
| method | EvidenceMethod | 필수 |
| target_label | Text | 필수 |
| summary | Text | 필수 |
| observed_at | Timestamp | 필수 |
| environment | Environment | 필수 |

**Error**

| 필드 | 자료형 / 값 | 필수 |
| --- | --- | --- |
| code | INVALID_REQUEST / UNAUTHENTICATED / NOT_FOUND / UNSUPPORTED_TARGET / VALIDATION_FAILED / MODEL_UNAVAILABLE / AUTH_REQUIRED / ACCOUNT_MISMATCH / TARGET_AMBIGUOUS / DUPLICATE_RISK / PERMISSION_DENIED / STALE_REVISION / APPROVAL_INVALID / IDEMPOTENCY_CONFLICT / INVALID_PHASE / RUNTIME_ERROR / EFFECT_UNKNOWN / EVIDENCE_INSUFFICIENT / PROFILE_CHANGED / CONNECTION_MISMATCH / FACT_CONFLICT | 필수 |
| message | Text | 필수 |
| issues | array&lt;Issue&gt; | 선택 |
| current_revision | Revision | 선택 |

**상태 의미:** job_state=null(아직 수락 전), active(수락·실행), stopping(오류로 종료 중), done(신뢰 가능한 목표 확인), stopped(오류 종료). Result.goal_verdict는 confirmed/not_reached/unknown이며 job_state 및 외부 플랫폼 접수/심사/공개 상태와 별개다. GET은 저장 결과만 읽는다. step.status의 pending 등은 job_state가 아니다.

**예시 A — 가격 충돌(H4 201, 저장 가능한 차단 초안)**

```json
{
  "registration_id": "registration-price-conflict-mock",
  "source_id": "source-price-conflict-mock",
  "revision": 1,
  "support": "supported",
  "profile_ref": {
    "platform": "kmong",
    "object_kind": "service_listing",
    "version": "mock.v2",
    "digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "environment": "mock"
  },
  "preparation": {
    "ready": false,
    "values": {},
    "facts": [],
    "issues": [
      {
        "issue_id": "issue-price-1",
        "field": "/packages/0/amount_vat_included_krw",
        "code": "conflict",
        "message": "원본의 STANDARD 가격이 25만원과 30만원으로 서로 다릅니다. 실제 VAT 포함 가격을 확인해 주세요.",
        "blocking": true
      }
    ],
    "provenance": []
  },
  "auth": {
    "state": "none"
  },
  "job_state": null
}
```

사용자는 표시된 질문에 H5의 current issue/field 및 expected_revision으로 답한다. 원본 사실과 충돌하는 값을 추측하거나 임의 변경하지 않는다. source 사실 자체가 바뀌면 새 Source. ready=false이므로 실행 수락 불가. 위 예시는 계약 설명용 합성 응답이며 실제 시험 결과 아님.

**예시 B — H7 승인·수락(202), H8 진행 조회(200)**

H7 요청은 expected_revision·review_digest·approved·request_key를 포함하고, 서버는 승인·권한을 확인해 작업을 저장한 다음 registration_id를 반환한다. 아래는 고정 합성 replay의 응답 **부분 발췌**(나머지 필수 필드 및 전체 요청은 [JSON 전체 예시](api-feedback-examples-20261126.json)).

```json
{
  "registration_id": "registration-kmong",
  "revision": 4,
  "job_state": "active",
  "progress": {
    "step_index": 0,
    "step_count": 7,
    "confirmed_steps": []
  }
}
```

GET /v1/registrations/registration-kmong으로 진행·최종 상태를 조회한다. 동일 요청 재조회는 기존 작업만 반환(200), 새 외부 등록이 아니다.

**예시 C — H8 독립 접수 확인(200, 부분 발췌)**

```json
{
  "registration_id": "registration-kmong",
  "revision": 5,
  "job_state": "done",
  "result": {
    "goal_verdict": "confirmed",
    "environment": "mock",
    "effects": [
      {
        "step_id": "K6",
        "operation_id": "mock-op-K6",
        "verdict": "confirmed",
        "evidence_refs": [
          "mock-ev-K6"
        ]
      },
      {
        "step_id": "K7",
        "operation_id": "mock-op-K7",
        "verdict": "confirmed",
        "evidence_refs": [
          "mock-ev-K7"
        ]
      }
    ],
    "evidence": [
      {
        "evidence_id": "mock-goal-kmong",
        "kind": "goal",
        "method": "independent_readback",
        "target_label": "합성 등록 대상",
        "summary": "Synthetic replay only",
        "observed_at": "2026-11-25T00:00:00Z",
        "environment": "mock"
      }
    ],
    "next_action": "합성 결과 확인"
  }
}
```

**예시 D — 접수 응답 유실·독립 확인 불가(200, result 부분 발췌)**

```json
{
  "registration_id": "registration-kmong",
  "job_state": "stopped",
  "result": {
    "goal_verdict": "unknown",
    "environment": "mock",
    "effects": [
      {
        "step_id": "K6",
        "operation_id": "mock-op-K6",
        "verdict": "unknown",
        "evidence_refs": []
      }
    ],
    "evidence": [],
    "error": {
      "code": "EFFECT_UNKNOWN",
      "message": "접수 응답 유실 후 독립 조회로 접수 여부를 확인하지 못했습니다."
    },
    "next_action": "결과 미확인: 자동 재등록하지 않습니다. 사용자에게 확인 필요 상태를 안내합니다."
  }
}
```

D는 설계 예시(시험 전)이다. 오류 중단 후 저장된 관측/독립 증거로 판정하며 증거가 없으면 unknown. 자동 재등록 금지. H8 조회 응답 자체는 200이어도 업무 성공을 뜻하지 않는다.

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

EFFECT_UNKNOWN/EVIDENCE_INSUFFICIENT는 수락 후 결과에만 사용. 예상 밖 내부 장애는 안전한 500/RUNTIME_ERROR. 저장 가능한 H4 unsupported/blocked/model issue는 정상 RegistrationView. H7 가드 미충족 시 외부 효과 0, 동일 key 재조회와 외부 동작 재실행 구분. mock-only. [PR #44 세부 권한/보안 후보](https://github.com/ik-e/chaja-you/pull/44)는 main에 병합됐으며 실제 연결은 별도 검증한다.

## 5. Tool 정의 및 실행 계약

| ID | 호출 → 제공 | 입력 → 출력 | 제약 |
| --- | --- | --- | --- |
| I1 | CO → KNOW | selector:string → ResolveOutput | 고정 registry, 임의 URL 금지 |
| I2 | CO → PREP | PrepareInput → Preparation | source/profile/answers, 출처·질문·검증, 실행 권한 없음 |
| I3 | CO → EXEC | AuthInput → AuthOutput | 현재 auth/generation/target, 내부 binding |
| I4 | CO → EXEC | ExecuteInput → ExecutionReport | AcceptedScope·exclusive lease·등록 operation, 실제 관측 |
| I5 | CO → RESULT | EvaluateInput → Result | 신뢰 가능한 저장 evidence로 판정, 외부 동작 없음 |

[공통 Python Protocol](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/product/lesson-registration/contracts/interfaces.py)의 with_verified_connection/list_operations/perform/observe_goal 및 STORE accept/admit/record_observation/fence/finalize는 내부 경계, 외부 API나 자유 LLM Tool 아님. adapter는 BoundGateway만 사용. Viewer mount/dispose 및 CDP+WebSocket 방향, 세부 메시지·grant/claim/permit은 PR #44 병합 기준의 실제 연결 검증 대상. PREP는 인증정보/브라우저 조작 권한 없음.

## 6. Timeout·재시도·멱등성과 검증

| 상황 | 계약 |
| --- | --- |
| PREP/인증 timeout | bounded, blocking issue 또는 typed error, 허위 ready/verified 금지; 수치 실측 후 |
| H7 응답 유실 | 동일 key/동일 요청으로 수락 조회, 다른 payload/key로 중복 실행 금지 |
| 외부 효과 유실 | fence, known/unknown 보존; 잠재 효과 자동 재실행 금지 |
| 종료 | CO 단일 전이, active→done 또는 active→stopping→stopped, 수락 이후 취소/수정/재개/rollback 없음 |
| 조회 | H8/H9 persisted view, GET 외부 동작 없음, detach≠cancel |
| 검증 | 동일 후보 22개 제품 gate 및 T5-08 실제 모델. S8 route 구현 확인; 실제 provider/DB 매핑·권한·경쟁 통합 시험 이후 갱신 |

현재 문서는 채택 설계의 제출용 사본이며 실제 HTTP 동작/제품·운영 보안 완료 증거가 아니다.

### 최신 S8 구현 대조 (11/25, main 4992959)

[HTTP 코드](https://github.com/ik-e/chaja-you/blob/4992959c08a12ad81a983ea4a89fed0837c0f1f8/product/lesson-registration/src/lesson_registration/app/http/api.py) · [R03 실행 기록](https://github.com/ik-e/chaja-you/blob/4992959c08a12ad81a983ea4a89fed0837c0f1f8/docs/artifacts/runs/TASK-050-s8-http-20261125.json): H1~H9 구현, 합성 provider/실제 loopback HTTP 독립 시험 191개(HTTP 14개) 통과 보고. 개발 인증 X-Mock-Owner는 명시 활성화·loopback 전용, owner_resolver 주입, exact origin allowlist, no-store. strict JSON 및 bounded multipart 총 body 16MiB는 담당자 mock 임시값(공통 운영 제한 확정 아님). /docs 및 OpenAPI 경로는 코드상 비활성화. 실제 provider·viewer·UI 및 22개 제품 gate 미실행. 경로 검사 실패는 일일 문서 경로로 기록되어 있음.

### 6.1 모델 호출 제한 및 실패 분기

| 항목 | 시험 후보(최종 확정 전) |
| --- | --- |
| PREP 전체 제한 | I2 호출 시작부터 추출·선택적 검증/보정 포함 최대 30초를 초기 시험 설정으로 제안. 외부 호출은 DB transaction 밖에서 수행; 늦은 결과는 revision CAS로 폐기. 원격 호출 종료 자체를 가정하지 않음. |
| 자동 전송 재시도 | 초기 후보 0회(클라이언트 SDK 내부 자동 retry 포함 비활성화/상한 확인). timeout, 429/5xx, 네트워크 오류의 성공률·비용·시간 실측 후 제한된 재시도 필요성 판단. 400/권한/잘못된 schema/가격 충돌은 전송 재시도로 해결하지 않음. 자기성찰 후보 교정 1회와 전송 재시도는 별도. |
| 저장 가능한 H4 model unavailable | 정상적으로 차단 초안을 저장할 수 있으면 201 RegistrationView, preparation.ready=false, issues[].code=model_unavailable, job_state=null. |
| 요청 자체 실패 | 제한 내 안전한 준비/저장 완료 불가 또는 transaction 실패면 503 MODEL_UNAVAILABLE 또는 RUNTIME_ERROR. 성공한 초안으로 표시하지 않음; DB 반영·실패 원자성 확인. |
| H5 실패/경쟁 | 기존 저장 preparation/answers/revision 보존, 늦은 결과로 덮어쓰지 않음. 실제 blocking response/503 매핑 및 현재 revision 처리는 D05 계약에서 확정. FACT_CONFLICT는 고정 계약 422. |
| 사용자 행동 | 결과 확인·질문에 응답·새 요청 등은 승인된 스토리 범위에서만. H7 수락 이후 외부 작업 자동 재실행/재개 없음. |

H4 저장 가능한 예: [model_blocked_draft JSON](api-feedback-examples-20261126.json) (ready=false, model_unavailable). 요청 실패 예: HTTP 503 `{"code":"RUNTIME_ERROR","message":"등록 준비 요청을 완료하지 못했습니다."}`. D05의 기존 R02/R03 probe는 5건 중 1건 통과·4건 미충족으로 보고되었으므로 완료 주장이 아니다. [R02 PLAN](https://github.com/ik-e/chaja-you/blob/ced14b622dca5b1c96aeb0e8cf73b5668bfba458/product/lesson-registration/tests/modules/preparation/PLAN.md). 11/27 설계/일정 검토 후보에서 R01이 사용자 스토리 및 오류 분기·가용성을 확인하고, 기존 구현 재개 후 R02/R03 동일 후보 합성 deadline/429/5xx/malformed/late revision/중첩 보존/저장 실패 시험과 비용·시간 관측으로 확정한다. 실제 모델 추가 호출은 별도 승인. 확정된 운영 수치 아님.

### 6.2 계약 고정·변경 이력

| 계약/근거 | 고정 참조 |
| --- | --- |
| 현재 참조 커밋 | [ced14b6](https://github.com/ik-e/chaja-you/commit/ced14b622dca5b1c96aeb0e8cf73b5668bfba458) |
| named JSON Schema V4.1 | [파일](https://github.com/ik-e/chaja-you/blob/ced14b622dca5b1c96aeb0e8cf73b5668bfba458/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · blob `de6c147216ee68bae75a9d18f9127c327701fa5a` |
| 공통 V1 / H1~H9 | [계약](https://github.com/ik-e/chaja-you/blob/ced14b622dca5b1c96aeb0e8cf73b5668bfba458/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) |
| 양 플랫폼 합성 replay | [파일](https://github.com/ik-e/chaja-you/blob/ced14b622dca5b1c96aeb0e8cf73b5668bfba458/product/lesson-registration/fixtures/shared/replay.json) · blob `f0fa01a2694b5698d7b7789282a7eabbb792cffa` |
| 읽기용 추가 JSON | [api-feedback-examples-20261126.json](api-feedback-examples-20261126.json) · 출처와 사례별 고정 replay/설계 예시 구분 |
| 실제 독립 HTTP 시험 | [S8 11/25 run](https://github.com/ik-e/chaja-you/blob/4992959c08a12ad81a983ea4a89fed0837c0f1f8/docs/artifacts/runs/TASK-050-s8-http-20261125.json) · 14 HTTP 포함 191 독립 시험, 이전 SQLite·합성 provider |
| 11/26 개정 | 본문 중첩 응답/예시, 인증·timeout 분기와 고정 이력 추가. wire/schema 자체 변경 없음. 새 V1.2 범위·PostgreSQL의 API 영향은 [TASK-058 후속 입력](../artifacts/planning/lesson-registration-20261126/instructor-api-db-design-inputs.json)에서 관리. |

현행 /docs·/redoc·/openapi.json은 비활성화. 문서 제공은 고정 계약·replay 방식으로 대응하며, OpenAPI 생성·개발 환경 제한 공개는 필요 시 후속 검토(외부 공개하지 않음). 새 계약은 기준 commit/schema blob/주요 변경/호환성/시험 입력·실행 commit/판정을 함께 기록한다. 새 사례의 실제 실행과 schema/profile/semantic 전체 검증은 미실행.
