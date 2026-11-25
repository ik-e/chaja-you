# HTTP API·업무 포트·오류

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## common-integration-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · blob `9df34e576f8a7c63c7ee84d01893a77631ce0360`

### id

- LR-COMMON-01

### version

- 1.0

### date

- 2026-11-25

### status

- logical&#95;common&#95;baseline&#95;delegated&#95;physical&#95;gate&#95;pending

### authority

- **actor** (`actor`): R01
- **request** (`request`): 너가 권장한대로 공통 설계를 하는데 각 설계 결정 사항에 대해서 왜 그렇게 결정을 내렸는지 근거가 추적될 수 있으면 좋겠는데
- **scope** (`scope`): common logical design and traceability; no new task assignments, live or implementation authorization

### basis

- **commit** (`commit`): e847b634cf427ac1681eb39c4ad61d8c55e7b42f
- **data** (`data`): data-contract-v4.json
- **schema** (`schema`): data-schema-v4.1.json
- **profile** (`profile`): platform-profiles-v2.json
- **prior&#95;interface** (`prior_interface`): interface-contract-v3.json
- **approved** (`approved`): logical-data-contract-decision-v1.json
- **precedence** (`precedence`): Latest common contract replaces V3 wire/ports and refines V4 only stated delta. A2 overrides historical resume/cancel/rollback. V4 platform/profile mock definitions and independent T1~T6 unchanged.

### schema_delta

- **source** (`source`): data-schema-v4.json
- **changes** (`changes`): FieldCorrection and ResolvedAnswer added · PreparationEdit.corrections optional · PrepareInput.answers uses ResolvedAnswer, normalized server-side
- **이유** (`rationale`): CS-02: previous issue&#95;id-only transfer and no correction of reviewed field without existing issue; no new business endpoint or workflow state

### routes

#### H1

- **ID** (`id`): H1
- **method** (`method`): POST
- **path** (`path`): /v1/sources
- **input** (`input`): SourceInput
- **output** (`output`): SourceView
- **flow** (`flow`): F1
- **purpose** (`purpose`): 원본/첨부 생성
- **success** (`success`): `201`
- **preconditions** (`preconditions`): owner 인증; 기존 source/asset owner 일치; raw&#95;text 또는 권리 확인된 유효 asset
- **request&#95;and&#95;effect** (`request_and_effect`): application/json if no new files; multipart/form-data: manifest JSON SourceInput + exact new&#95;assets.part&#95;name parts; reject duplicate/missing/extra; bytes media verify; rights false or unsafe asset reject 422, keep existing immutable sources
- **response** (`response`): 201 new immutable snapshot; H1 no external mutation; client may explicitly retry if response lost; duplicate source alone no external effect
- **errors** (`errors`): INVALID&#95;REQUEST · VALIDATION&#95;FAILED · NOT&#95;FOUND · PERMISSION&#95;DENIED

#### H2

- **ID** (`id`): H2
- **method** (`method`): GET
- **path** (`path`): /v1/sources
- **input** (`input`): ListQuery
- **output** (`output`): SourceList
- **flow** (`flow`): F1
- **purpose** (`purpose`): 원본 목록
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner 인증
- **request&#95;and&#95;effect** (`request_and_effect`): ListQuery cursor/limit; default limit 20; opaque owner-bound cursor, order created&#95;at DESC then source&#95;id DESC; invalid cursor 400
- **response** (`response`): 200 persisted summaries; omit next&#95;cursor when end
- **errors** (`errors`): INVALID&#95;REQUEST · NOT&#95;FOUND

#### H3

- **ID** (`id`): H3
- **method** (`method`): GET
- **path** (`path`): /v1/sources/{id}
- **input** (`input`): `null`
- **output** (`output`): SourceView
- **flow** (`flow`): F1
- **purpose** (`purpose`): 원본 조회
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner 인증; id owner
- **request&#95;and&#95;effect** (`request_and_effect`): id path opaque source&#95;id; no body
- **response** (`response`): 200 persisted SourceView; other owner=404
- **errors** (`errors`): NOT&#95;FOUND

#### H4

- **ID** (`id`): H4
- **method** (`method`): POST
- **path** (`path`): /v1/registrations
- **input** (`input`): RegistrationInput
- **output** (`output`): RegistrationView
- **flow** (`flow`): F1/F2
- **purpose** (`purpose`): 등록 요청 생성 및 준비
- **success** (`success`): `201`
- **preconditions** (`preconditions`): owner owns source; selector only
- **request&#95;and&#95;effect** (`request_and_effect`): server resolves supported registry; unsupported/blocked persist normal view, no external navigation; supported prepares; model unavailable =&gt; persisted ready=false issue; no raw credentials
- **response** (`response`): 201 RegistrationView, job&#95;state=null, no start; synchronous bounded
- **errors** (`errors`): NOT&#95;FOUND · INVALID&#95;REQUEST · VALIDATION&#95;FAILED · MODEL&#95;UNAVAILABLE

#### H5

- **ID** (`id`): H5
- **method** (`method`): PATCH
- **path** (`path`): /v1/registrations/{id}
- **input** (`input`): PreparationEdit
- **output** (`output`): RegistrationView
- **flow** (`flow`): F2
- **purpose** (`purpose`): 등록 전 답변/수정
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner; job&#95;state=null; revision current; auth human/verifying must close first
- **request&#95;and&#95;effect** (`request_and_effect`): at least one source&#95;id/selector/answers/corrections. Source/selector changed -&gt; no simultaneous old answers/corrections; clear incompatible facts/answers and binding, regenerate. Same source&#95;id may explicitly reprepare after transient model failure. Current issue&#95;id-&gt;field; corrections reference valid profile field JSON Pointer; normalize server ResolvedAnswer; no direct values/status patch; duplicate/conflicting paths rejected. Shared fact correction needs new Source. Material change invalidates review/binding. Recalculate ready; source/profile unchanged retain compatible answers.
- **response** (`response`): 200 current RegistrationView, revision increment on persisted mutation; no browser mutation
- **errors** (`errors`): INVALID&#95;REQUEST · NOT&#95;FOUND · STALE&#95;REVISION · INVALID&#95;PHASE · VALIDATION&#95;FAILED · FACT&#95;CONFLICT · PROFILE&#95;CHANGED

#### H6

- **ID** (`id`): H6
- **method** (`method`): POST
- **path** (`path`): /v1/registrations/{id}/authentication
- **input** (`input`): AuthCommand
- **output** (`output`): AuthResponse
- **flow** (`flow`): F3
- **purpose** (`purpose`): 직접 인증 및 대상 확인
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner; job&#95;state=null; supported+ready for open; expected&#95;revision current; generation required for finish/close/refresh
- **request&#95;and&#95;effect** (`request_and_effect`): open from none/closed; return human grant. finish only human current generation: fence human then verify account, target, connection; verified even target existing/ambiguous but no review. close prestart only, fence and invalidate binding/review; refresh human only current generation; rotate grant, prior grant invalid; timeout closes/fences, no verified binding. Do not expose internal ref or credentials. Viewer disconnect not close command.
- **response** (`response`): 200 AuthResponse; grant only open/refresh; state/target on returned registration; 409 stale/phase, 503 runtime timeout/error with safe state reread
- **errors** (`errors`): INVALID&#95;REQUEST · NOT&#95;FOUND · STALE&#95;REVISION · INVALID&#95;PHASE · AUTH&#95;REQUIRED · ACCOUNT&#95;MISMATCH · CONNECTION&#95;MISMATCH · PERMISSION&#95;DENIED · RUNTIME&#95;ERROR

#### H7

- **ID** (`id`): H7
- **method** (`method`): POST
- **path** (`path`): /v1/registrations/{id}/start
- **input** (`input`): StartInput
- **output** (`output`): RegistrationView
- **flow** (`flow`): F4/F5
- **purpose** (`purpose`): 최종 승인 및 작업 수락
- **success** (`success`): `202` · `200`
- **preconditions** (`preconditions`): owner; id owned; exact current revision/review digest, ready, verified/new, supported, scope/permission/connection current
- **request&#95;and&#95;effect** (`request_and_effect`): lookup owner+start request&#95;key before stale/phase checks (after authentication/owner check); same key+same canonical payload -&gt; persisted same registration (200); same key different payload -&gt; 409; different key on accepted registration -&gt; 409; new registration same unresolved/confirmed effect/ambiguous target blocked. Accept snapshot + key + active state atomically before dispatch; no additional user approval/cancel/resume
- **response** (`response`): 202 first durable acceptance; 200 exact replay; job execution errors afterward stored, not HTTP rejection; response lost retry exact key
- **errors** (`errors`): INVALID&#95;REQUEST · NOT&#95;FOUND · STALE&#95;REVISION · APPROVAL&#95;INVALID · INVALID&#95;PHASE · AUTH&#95;REQUIRED · ACCOUNT&#95;MISMATCH · CONNECTION&#95;MISMATCH · TARGET&#95;AMBIGUOUS · DUPLICATE&#95;RISK · IDEMPOTENCY&#95;CONFLICT · PERMISSION&#95;DENIED · PROFILE&#95;CHANGED

#### H8

- **ID** (`id`): H8
- **method** (`method`): GET
- **path** (`path`): /v1/registrations/{id}
- **input** (`input`): `null`
- **output** (`output`): RegistrationView
- **flow** (`flow`): F6
- **purpose** (`purpose`): 등록 상세 및 결과 조회
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner; id owned
- **request&#95;and&#95;effect** (`request_and_effect`): GET persisted view only; no external mutation/readback; terminal result mandatory; progress advisory; poll without keeping viewer alive
- **response** (`response`): 200 RegistrationView; use revision to ignore stale UI response
- **errors** (`errors`): NOT&#95;FOUND

#### H9

- **ID** (`id`): H9
- **method** (`method`): GET
- **path** (`path`): /v1/registrations
- **input** (`input`): ListQuery
- **output** (`output`): RegistrationList
- **flow** (`flow`): F6
- **purpose** (`purpose`): 등록 목록
- **success** (`success`): `200`
- **preconditions** (`preconditions`): owner 인증
- **request&#95;and&#95;effect** (`request_and_effect`): ListQuery cursor/limit; default 20; opaque owner-bound cursor ordered creation then registration&#95;id; no external access
- **response** (`response`): 200 RegistrationList; no internal connection/viewer secret
- **errors** (`errors`): INVALID&#95;REQUEST · NOT&#95;FOUND

### ports

#### I1

- **ID** (`id`): I1
- **consumer** (`consumer`): CO
- **provider** (`provider`): KNOW
- **input** (`input`): selector:string
- **output** (`output`): ResolveOutput
- **pre** (`pre`): selector allowed length; pure local registry lookup; no arbitrary network
- **post** (`post`): supported carries immutable ProfileRef and resolvable value&#95;contract&#95;ref/manifest; unsupported/blocked typed normal; exact identity validated
- **failure** (`failure`): invalid syntax INVALID&#95;REQUEST; corrupt/missing pinned registry PROFILE&#95;CHANGED/RUNTIME&#95;ERROR; no execution
- **calls** (`calls`): CO resolves once, PREP/EXEC/RESULT retrieve same pinned content by ref, not re-resolve selector
- **refs** (`refs`): B01 · V02

#### I2

- **ID** (`id`): I2
- **consumer** (`consumer`): CO
- **provider** (`provider`): PREP
- **input** (`input`): PrepareInput
- **output** (`output`): Preparation
- **pre** (`pre`): owner-scoped SourceView, exact pinned Profile, normalized ResolvedAnswer&#91;&#93; for current source/profile, no auth secrets
- **post** (`post`): values/facts/provenance/issues; computed ready; source facts/units not overwritten; no external platform mutation
- **failure** (`failure`): missing/conflict/invalid/model unavailable -&gt; blocking Issue (ready=false); schema/runtime failures typed error; no start
- **refs** (`refs`): B02 · V01 · V03 · V04 · V05

#### I3

- **ID** (`id`): I3
- **consumer** (`consumer`): CO
- **provider** (`provider`): EXEC
- **input** (`input`): AuthInput
- **output** (`output`): AuthOutput
- **pre** (`pre`): current registration context, pinned profile, owner and auth command; open ready; current rev/generation checks; runtime reads current target intent from CO-owned state
- **post** (`post`): verified carries trusted target+ConnectionBinding; open/refresh only human grant; close/failure fence; no job fabricated
- **failure** (`failure`): prestart no mutation beyond scoped authentication/target read; wrong/unknown account/expired generation/timeout -&gt; unverified or closed; typed Error, no start
- **refs** (`refs`): B03 · V06

#### I4

- **ID** (`id`): I4
- **consumer** (`consumer`): CO
- **provider** (`provider`): EXEC
- **input** (`input`): ExecuteInput
- **output** (`output`): ExecutionReport
- **pre** (`pre`): durably accepted immutable scope, active state, pinned profile/runtime binding, exclusive worker lease current, mock permission
- **post** (`post`): observations and errors linked to persisted evidence; gateway command admission before potential mutation; only actual observations; no direct job state change by adapter
- **failure** (`failure`): on unexpected error fence via common store, stop future effects; report known/unknown/absence; if runner crashes CO detects orphan and stops, not resume
- **refs** (`refs`): B04 · B05 · V06 · V07

#### I5

- **ID** (`id`): I5
- **consumer** (`consumer`): CO
- **provider** (`provider`): RESULT
- **input** (`input`): EvaluateInput
- **output** (`output`): Result
- **pre** (`pre`): same pinned profile and AcceptedScope; trusted stored ExecutionReport/EvidenceRecord&#91;&#93;; no browser commands
- **post** (`post`): profile goal/proof and scope compared; done only verified goal with no unresolved effects; otherwise stopped outcome, next&#95;action; CO commits result
- **failure** (`failure`): insufficient/mismatched evidence never success; evaluator error fail closed/unknown unless authoritative absence; terminal record persists
- **refs** (`refs`): B05 · B06 · V08 · V09

### http

- **base** (`base`): /v1
- **auth** (`auth`): owner from authenticated app context; path ids opaque; never accept client owner&#95;ref, approval plan, state, credentials; not found or foreign owner 404
- **content** (`content`): application/json except H1 described; named $defs validation (not schema root); unknown keys rejected; UTC timestamps; profile validation and relational guards additional; responses redacted
- **error&#95;schema** (`error_schema`): Error
- **status&#95;codes** (`status_codes`)
  - **400** (`400`): INVALID&#95;REQUEST
  - **401** (`401`): UNAUTHENTICATED
  - **403** (`403`): PERMISSION&#95;DENIED
  - **404** (`404`): NOT&#95;FOUND
  - **409** (`409`): STALE&#95;REVISION · APPROVAL&#95;INVALID · IDEMPOTENCY&#95;CONFLICT · INVALID&#95;PHASE · ACCOUNT&#95;MISMATCH · CONNECTION&#95;MISMATCH · TARGET&#95;AMBIGUOUS · DUPLICATE&#95;RISK · PROFILE&#95;CHANGED
  - **422** (`422`): VALIDATION&#95;FAILED · FACT&#95;CONFLICT · AUTH&#95;REQUIRED · UNSUPPORTED&#95;TARGET
  - **503** (`503`): MODEL&#95;UNAVAILABLE · RUNTIME&#95;ERROR
- **result&#95;only&#95;codes** (`result_only_codes`): EFFECT&#95;UNKNOWN · EVIDENCE&#95;INSUFFICIENT
- **note** (`note`): H4 unsupported/blocked and model issue are normal view when persisted; 503 when cannot complete bounded dependency/transaction. For failures after accepted H7 only persisted job result. All errors carry safe Error message; 409 current&#95;revision when owner allowed. Server unexpected internal errors use 500/RUNTIME&#95;ERROR only when safe response; no stack traces. 401/404/403 common guards apply to all routes.

