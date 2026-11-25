# r03-app 개발 설계서 (SPEC) — TASK-050

- 작성일: 2026-11-25 · 작성: R03 · 상위 문서: [PLAN.md](PLAN.md)
- 계약 정본(이 문서보다 우선): `common-integration-v1.json`(routes·ports·http·state·storage·runtime), `data-schema-v4.1.json`(`$defs`), `platform-profiles-v2.json` — WORKSPACE.json `pins`의 commit/blob 고정본
- 공통 replay: `fixtures/shared/replay.json` (kmong·soomgo 각각 I1, I2, I2-missing, I3, I4, I5, I5-unknown, RT-03, RT-04, VIEWER, H1~H9)
- 이 문서는 PLAN §4의 구현 순서 S0~S8을 단계별 개발 명세로 풀어 쓴 것이다. 각 단계는 **목표 → 파일 → 인터페이스 → 처리 규칙 → 시험 → 완료 조건** 순서로 적는다.

## 0. 공통 전제

### 0.1 실행 환경

- Python 3.12, **표준 라이브러리만** 사용(제품 `pyproject.toml`의 `dependencies = []`). HTTP 프레임워크는 S8에서 R01 결정 후 추가.
- 시험: `unittest`. `dev.py test r03-app`이 `tests/modules/app`에서 `test_*.py`를 찾아 실행하고, `PYTHONPATH`에 제품 root와 `src`가 들어간다. 따라서 import는 `from lesson_registration.app import ...`.
- 실행 명령: `cd product/lesson-registration && uv run --locked --python 3.12 python dev.py test r03-app`
- 환경 변수 `LR_ENVIRONMENT`는 `mock`만 허용(dev.py가 강제). 앱도 `environment != "mock"` 입력을 거부한다.

### 0.2 패키지 구조 (최종)

```
src/lesson_registration/app/
  __init__.py
  contract.py        # 고정 계약 로드·blob 검증, $defs 검증기
  errors.py          # AppError(code, message, issues, current_revision) + HTTP status 매핑
  ids.py             # opaque id·digest·canonical JSON·UTC 시각
  ports.py           # PrepPort(I2), ExecPort(I3/I4) Protocol + Clock
  knowledge.py       # KNOW: I1 resolve, profile 조회
  store/
    __init__.py
    schema.sql       # 테이블 정의
    db.py            # 연결·트랜잭션 헬퍼
    repo.py          # Source/Registration 저장·조회
    atomic.py        # accept / admit / observe / fence / finalize
  coordinator.py     # CO: H1~H9 유스케이스, 상태 전이
  result.py          # RESULT: I5 evaluate
  service.py         # 조립(App): store + KNOW + RESULT + 주입 포트
  http/              # S8: 프레임워크 어댑터 (결정 후)
tests/modules/app/
  PLAN.md  SPEC.md
  support.py         # 테스트 공용: 임시 DB, replay 기반 fake 포트, fixture 로더
  test_bootstrap.py  # 기존(R01) — 유지
  test_s0_contract.py ... test_s8_http.py
```

### 0.3 공통 규칙

| 규칙 | 구현 |
|---|---|
| owner | 모든 유스케이스 첫 인자 `owner_ref: str`. 클라이언트 입력에서 owner를 받지 않는다. 타 owner 자원은 `NOT_FOUND` |
| 입력 검증 | `$defs` 이름 단위 검증, **모르는 key 거부**. 실패 시 `INVALID_REQUEST`(형식) / `VALIDATION_FAILED`(의미) |
| ID | `ids.new_id(prefix)` = prefix + `-` + `secrets.token_hex(12)`. path id는 opaque |
| digest | canonical JSON(`sort_keys=True, separators=(",",":"), ensure_ascii=False`) UTF-8의 SHA-256 hex |
| 시각 | UTC ISO-8601 `Z`. 테스트는 고정 Clock 주입 |
| 응답 | View 타입만 반환. `connection_ref`·`account_ref`·`viewer_grant` 이외 secret·내부 binding은 절대 포함하지 않음 |
| 트랜잭션 중 외부 호출 금지 | STORE 트랜잭션 안에서 포트(I2~I4) 호출하지 않는다(계약: "no callbacks while atomic lock") |

### 0.3.1 승인된 공통 구현 계약과의 대응 (main `75caa4e`, IB-01~05)

| 공통 계약 (`contracts/interfaces.py`) | r03-app 구현 |
|---|---|
| `Registry.resolve / get_profile` | `knowledge.Knowledge` |
| `ResultPort.evaluate` | `result.ResultEvaluator` (순수 `result.evaluate` 감쌈) |
| `PreparationPort` / `ExecutionPort` | 주입받음 (`ports.PrepPort` / `ExecPort`와 같은 메서드) |
| `Providers(registry, preparation, execution, result)` | `Coordinator(store, providers=...)` (개별 인자도 허용, 자동 fake 없음) |
| `PortFailure(error)` | `_port_error`: 경로별 허용 코드만 유지, 나머지는 `RUNTIME_ERROR`. PREP의 `MODEL_UNAVAILABLE`은 저장되는 준비 이슈 |
| `CoordinatorStore.accept / fence / finalize` | `store.coordinator_store.SqliteCoordinatorStore` (accept는 잠근 행으로 모든 가드 재검사) |
| `GatewayStore.admit / record_observation / fence` | `gateway.StoreGateway` |

`check-changes --base`의 공통 기준 SHA: `75caa4e` (main 병합 기준).

### 0.4 오류 → HTTP status (common-integration-v1 `http.status_codes`)

| status | code |
|---|---|
| 400 | INVALID_REQUEST |
| 401 | UNAUTHENTICATED |
| 403 | PERMISSION_DENIED |
| 404 | NOT_FOUND |
| 409 | STALE_REVISION, APPROVAL_INVALID, IDEMPOTENCY_CONFLICT, INVALID_PHASE, ACCOUNT_MISMATCH, CONNECTION_MISMATCH, TARGET_AMBIGUOUS, DUPLICATE_RISK, PROFILE_CHANGED |
| 422 | VALIDATION_FAILED, FACT_CONFLICT, AUTH_REQUIRED, UNSUPPORTED_TARGET |
| 503 | MODEL_UNAVAILABLE, RUNTIME_ERROR |
| 결과 전용 | EFFECT_UNKNOWN, EVIDENCE_INSUFFICIENT (HTTP 응답이 아니라 `Result.error`에만) |

409 응답에는 owner가 볼 수 있으면 `current_revision`을 넣는다. 예상 못 한 내부 오류는 500 + `RUNTIME_ERROR`, stack trace 금지.

---

## S0. 계약 로드·검증기·포트 정의

**목표:** 고정 계약을 코드에서 읽고, `$defs` 단위로 입력·출력을 검증하며, 외부 모듈(I2/I3/I4) 주입 지점을 만든다.

**파일:** `contract.py`, `errors.py`, `ids.py`, `ports.py`, `tests/modules/app/support.py`, `test_s0_contract.py`

### S0-1 contract.py

```python
def load(name: str) -> dict
    # WORKSPACE.json pins에서 path가 "/"+name으로 끝나는 항목을 찾아
    # repo root 기준 파일을 읽고 git blob sha1("blob {len}\0"+bytes) == pin.blob 확인. 불일치 → RuntimeError
def validate(def_name: str, value: object) -> None   # 실패 시 AppError(INVALID_REQUEST, issues=[...])
```

- 검증기는 스키마에서 실제로 쓰는 키워드만 지원한다: `type, properties, required, additionalProperties, enum, const, $ref, oneOf, anyOf, items, minItems, maxItems, uniqueItems, minimum, maximum, minLength, maxLength, pattern, format(date-time만)`.
- 모르는 키워드가 스키마에 나오면 시험에서 실패시켜 조용히 통과하지 않게 한다.

### S0-2 errors.py

```python
class AppError(Exception):
    code: str; message: str; issues: list | None; current_revision: int | None
    def to_view(self) -> dict          # Error $def 형태
STATUS: dict[str, int]                 # §0.4 표
```

### S0-3 ports.py

```python
class PrepPort(Protocol):     # I2 (R02)
    def prepare(self, inp: dict) -> dict            # PrepareInput -> Preparation
class ExecPort(Protocol):     # I3/I4 (R05)
    def authenticate(self, inp: dict) -> dict       # AuthInput -> AuthOutput
    def execute(self, inp: dict) -> dict            # ExecuteInput -> ExecutionReport
class Clock(Protocol):
    def now(self) -> str
```

- 포트 반환값은 CO가 `validate("Preparation"|"AuthOutput"|"ExecutionReport", ...)`로 검사한 뒤 쓴다. 형식 위반은 `RUNTIME_ERROR`.
- 동기 호출로 시작한다. 비동기·타임아웃 형식은 R02·R05와 합의 후 바꾼다(PLAN §7).

### S0-4 support.py (테스트 공용)

- `temp_db()` — `tempfile` 경로의 SQLite 파일
- `ReplayPrep`, `ReplayExec` — `dev.replay(platform, case, value)`를 감싼 fake. **정확히 일치하는 입력만** 응답하므로, 다른 입력용 fake(`ScriptedExec`: 시나리오별 응답·예외·지연을 주입)도 함께 둔다
- `FIXED_CLOCK`

**시험(test_s0_contract.py)**
- 4개 pin 모두 blob 일치로 로드된다
- replay의 모든 case `input/output`이 각 `input_type/output_type`으로 검증 통과
- 모르는 key 하나를 추가하면 실패, 필수 key 하나를 빼면 실패, enum 밖 값이면 실패
- `ReplayPrep/ReplayExec`가 Protocol을 만족

**완료:** 위 시험 통과 + `test_bootstrap.py` 유지 통과

---

## S1. STORE 스키마·원본(Source) 저장·소유권

**목표:** 영속 저장소를 만들고 H1~H3(원본)을 CO 수준에서 구현한다.

**파일:** `store/schema.sql`, `store/db.py`, `store/repo.py`, `coordinator.py`(원본 부분), `test_s1_source.py`

### S1-1 연결 규칙 (db.py)

- `sqlite3.connect(path, isolation_level=None)` + `PRAGMA journal_mode=WAL`, `PRAGMA foreign_keys=ON`, `busy_timeout=5000`
- `with tx(conn):` → `BEGIN IMMEDIATE` … `COMMIT`/`ROLLBACK`. 모든 쓰기는 이 헬퍼로만 한다.

### S1-2 테이블 (schema.sql)

```sql
sources(source_id PK, owner_ref, previous_source_id NULL, raw_text, created_at)
assets(asset_id PK, owner_ref, digest, mime, bytes, width, height, rights_confirmed, blob BLOB, created_at)
source_assets(source_id, asset_id, ord, PRIMARY KEY(source_id, asset_id))
registrations(registration_id PK, owner_ref, source_id, selector, support, profile_json NULL,
              preparation_json, answers_json, revision INTEGER, auth_json, target_json NULL,
              connection_json NULL, review_json NULL, job_state NULL, created_at, updated_at)
jobs(registration_id PK, owner_ref, request_key, request_digest, accepted_scope_json, state,
     result_json NULL, worker_lease NULL, accepted_at, updated_at,
     UNIQUE(owner_ref, request_key))
effects(effect_key PK, registration_id, operation_id, step_id, action_key, effect_class,
        binding_digest, status /* reserved|confirmed|absent|unknown */, admitted_at, resolved_at NULL)
observations(observation_id PK, registration_id, operation_id, verdict, method, evidence_refs_json, observed_at)
evidence(evidence_id PK, registration_id, record_json, observed_at)
```

- 원본·첨부는 UPDATE/DELETE 경로를 만들지 않는다(불변).

### S1-3 유스케이스

```python
create_source(owner_ref, source_input: dict, new_files: dict[str, bytes]) -> SourceView   # H1
list_sources(owner_ref, query: dict) -> SourceList                                        # H2
get_source(owner_ref, source_id) -> SourceView                                            # H3
```

**H1 처리 규칙**
1. `validate("SourceInput")`. `raw_text`가 비었고 첨부도 없으면 `VALIDATION_FAILED`
2. `previous_source_id`, `reuse_asset_ids`는 같은 owner 소유여야 함 → 아니면 `NOT_FOUND`
3. `new_assets[].part_name`과 `new_files` key가 정확히 일치(누락·추가·중복 → `INVALID_REQUEST`)
4. 바이트 검사: PNG/JPEG 시그니처로 MIME 판정, 크기·가로·세로를 헤더에서 읽음. `rights_confirmed=false` 또는 형식 불일치 → `VALIDATION_FAILED`(422), 저장하지 않음
5. 한 트랜잭션에서 sources·assets·source_assets 저장 → 201 `SourceView`
6. 첨부 세부 검증(T6-01 전체)은 S6에서 확장하고, S1에서는 PNG 정상 경로와 rights=false 거부만 구현

**H2:** `limit` 기본 20(1~100), 정렬 `created_at DESC, source_id DESC`. cursor = owner와 마지막 키를 담은 opaque 토큰(base64 JSON + HMAC). 다른 owner의 cursor나 변조된 cursor → `INVALID_REQUEST`. 끝이면 `next_cursor` 생략.
**H3:** 다른 owner → `NOT_FOUND`.

**시험(test_s1_source.py)** — T5-11 일부
- 정상 생성 후 같은 내용으로 다시 만들면 새 source_id(중복 원본은 외부 효과 없음)
- `previous_source_id`로 새 버전 생성, 이전 원본은 그대로
- 타 owner의 source·asset 참조 → `NOT_FOUND`
- 모르는 key, part_name 누락·추가 → `INVALID_REQUEST`
- rights_confirmed=false → `VALIDATION_FAILED`, 저장 0건
- H2 정렬·limit·cursor, 변조 cursor 거부
- DB 연결을 닫았다 다시 열어도 원본 유지(영속성)

**완료:** 시험 통과, H1~H3 반환값이 `SourceView/SourceList` 검증 통과

---

## S2. KNOW(I1)·등록 생성·준비 수정(H4, H5)

**목표:** selector를 프로필로 해석하고, PREP을 불러 등록 요청을 만들고, 승인 전 답변·수정을 처리한다.

**파일:** `knowledge.py`, `coordinator.py`(등록 준비 부분), `test_s2_prepare.py`

### S2-1 KNOW

```python
class Knowledge:
    def __init__(self, profiles: dict)              # platform-profiles-v2.json 고정본
    def resolve(self, selector: str) -> dict        # I1: ResolveOutput
    def get(self, ref: dict) -> dict                # ProfileRef로 동일 Profile 반환, digest 불일치 → PROFILE_CHANGED
```

- 로컬 registry 조회만 한다. 네트워크 접근 없음.
- 길이 초과·형식 오류 selector → `INVALID_REQUEST`. 없는 플랫폼 → `{"status":"unsupported","reason":...}`(정상 응답).
- CO는 selector를 **한 번만** 해석하고 이후엔 `ProfileRef`로만 조회한다.
- W10(URL registry)은 TASK-050 범위 밖이므로 selector는 `kmong`/`soomgo` 같은 등록 키만 지원한다.

### S2-2 H4 create_registration(owner_ref, RegistrationInput) -> RegistrationView

1. `validate`, source 소유 확인(`NOT_FOUND`)
2. `resolve(selector)`. unsupported/blocked면 `support`만 기록한 정상 View 저장 후 201(외부 접근 없음)
3. supported면 `PrepareInput{source, profile, answers: []}`로 `PrepPort.prepare` 호출 — **트랜잭션 밖에서**
4. PREP이 모델 불가 이슈(`model_unavailable`)를 주면 `ready=false`인 정상 View로 저장. 포트 자체가 예외로 실패하면 503 `MODEL_UNAVAILABLE`
5. 저장: `revision=1`, `auth={"state":"none"}`, `job_state=null`, review 없음 → 201

### S2-3 H5 edit_registration(owner_ref, id, PreparationEdit) -> RegistrationView

선행 검사 순서: 소유 → `job_state is null`(아니면 `INVALID_PHASE`) → `expected_revision == revision`(아니면 `STALE_REVISION` + current_revision) → auth가 `human`/`verifying`이면 `INVALID_PHASE`

| 입력 | 처리 |
|---|---|
| `source_id`/`selector` 변경 | 같은 요청에 answers·corrections 금지(`INVALID_REQUEST`). 호환 안 되는 facts·answers·binding 삭제, 다시 resolve·prepare |
| 같은 source_id 재지정 | 일시적 모델 실패 후 명시적 재준비 허용 |
| `answers[]` | `issue_id`가 **현재** 이슈여야 함. 서버가 issue→field를 찾아 `ResolvedAnswer{answer_id,field,value,origin_issue_id}`로 정규화 |
| `corrections[]` | `field`가 프로필 필드의 유효한 JSON Pointer(`/` + 프로필 field key로 시작)여야 함. `origin_issue_id` 없는 ResolvedAnswer로 PREP에 전달. PREP이 **방금 수정한 field**에 blocking `conflict` 이슈를 돌려주면 저장하지 않고 `FACT_CONFLICT`(새 Source 필요) |
| 같은 field 중복·충돌 | `INVALID_REQUEST` |

- 정규화된 answers로 `prepare` 재호출 → ready 재계산
- 실제로 바뀐 게 있을 때만 `revision += 1`, 기존 review·binding 무효화
- 프로필 digest가 바뀌었으면 `PROFILE_CHANGED`

**시험(test_s2_prepare.py)**
- kmong·soomgo 각각: I1 replay와 같은 Profile 해석
- unsupported selector → 201, `support="unsupported"`, PREP 호출 0회
- I2-missing → `ready=false`, blocking issue 유지, 가격 값 생성 안 함
- 답변 → revision 증가, 이전 review 무효
- 오래된 expected_revision → 409 `STALE_REVISION` + current_revision
- 존재하지 않는 issue_id, 잘못된 field pointer, 같은 field 중복 → 거부
- source 변경 + answers 동시 → `INVALID_REQUEST`
- 변화 없는 PATCH는 revision 그대로

**완료:** 시험 통과, H4/H5 응답이 `RegistrationView` 검증 통과

---

## S3. 인증(H6)·승인 검토·작업 수락(H7, accept)

**목표:** I3로 인증·대상을 확인하고, review digest를 만들어 최종 승인과 작업 수락을 원자적으로 처리한다.

**파일:** `coordinator.py`(인증·시작), `store/atomic.py`(accept), `test_s3_auth_start.py`

### S3-1 H6 authenticate(owner_ref, id, AuthCommand) -> AuthResponse

| action | 허용 상태 | 처리 |
|---|---|---|
| `open` | auth `none`/`closed`, supported+ready | I3 호출 → `human` + grant(응답에만, 저장은 generation과 만료만) |
| `finish` | `human`, 현재 generation | I3 → verified면 `target`(TrustedTarget)·`connection`(ConnectionBinding)을 **내부 저장**, View엔 `account_label`·TargetView만 |
| `close` | 시작 전, 현재 generation | binding·review 무효화, `closed` |
| `refresh` | `human`, 현재 generation | grant 교체, 이전 grant 무효 |

- 공통 선행 검사: 소유 → `job_state is null` → `expected_revision` 일치 → generation 일치(`STALE_REVISION`/`INVALID_PHASE`)
- I3가 계정 불일치·연결 불일치를 보고하면 `ACCOUNT_MISMATCH`/`CONNECTION_MISMATCH`, timeout·런타임 오류는 503 `RUNTIME_ERROR` 후 안전한 상태로 재조회 가능하게 저장
- viewer 연결 끊김은 close가 아니다(상태 변경 없음)

### S3-2 review 생성

조건: `ready=true` + auth `verified` + target `status=="new"` + support `supported`. 이때 `ReviewView{values, assets, profile_ref, target, procedure, goal, notice}`를 만들고 `digest = sha256(canonical({review: ReviewView에서 digest 제외, revision, auth_generation, connection_ref}))`. revision·인증 연결을 digest에 묶어(View에는 노출 안 함) 내용이 같아도 재인증·이후 revision에 이전 승인을 재사용할 수 없게 한다. 조건이 깨지면 review를 지운다. target이 `existing`/`ambiguous`면 review 없음.

### S3-3 H7 start(owner_ref, id, StartInput) -> (status, RegistrationView)

순서가 중요하다(계약 H7):
1. owner 인증 후 **먼저** `(owner_ref, request_key)` 조회
   - 같은 key + 같은 request_digest → 저장된 View, **200**
   - 같은 key + 다른 payload → 409 `IDEMPOTENCY_CONFLICT`
2. 그 다음에 stale·phase 검사: revision(`STALE_REVISION`), `review_digest` 일치(`APPROVAL_INVALID`), ready·verified·supported·new(`INVALID_PHASE`/`AUTH_REQUIRED`/`TARGET_AMBIGUOUS`)
3. 이미 job이 있는 등록에 다른 key → 409 `IDEMPOTENCY_CONFLICT`
4. 같은 effect_key 대상(다른 등록 포함)에 미해결·확정·모호 효과가 있으면 409 `DUPLICATE_RISK`
5. `store.accept(...)` 한 트랜잭션: AcceptedScope(불변) + key + digest + `job_state=active` 저장
6. 커밋 후에 실행 디스패치(S4) → **202**

- `request_digest` = canonical(`{"path_id": id, **StartInput}`) SHA-256
- 수락 이후 실행 오류는 HTTP 오류가 아니라 저장된 결과로만 나타난다

### S3-4 store.accept

```python
accept(conn, owner_ref, registration_id, start_input, scope: dict, request_digest) -> "accepted" | "replayed"
```
트랜잭션 안에서 위 1~4를 다시 확인한다(검사와 쓰기 사이 경쟁 차단). `UNIQUE(owner_ref, request_key)` 위반은 replay/conflict로 해석한다.

**시험(test_s3_auth_start.py)** — T5-01
- open→finish 정상: View에 connection_ref·account_ref 없음, grant는 open/refresh 응답에만
- 오래된 generation finish → 거부, refresh 후 이전 grant 무효
- 계정 불일치 → `ACCOUNT_MISMATCH`, review 없음
- target existing/ambiguous → review 없음, start → `TARGET_AMBIGUOUS`/`DUPLICATE_RISK`
- review digest 위조·오래됨 → `APPROVAL_INVALID`, 효과 0
- 정상 start 202 → 같은 key 재전송 200(같은 View), 다른 payload 409, 다른 key 409
- **경쟁:** 두 스레드가 같은 등록에 서로 다른 key로 동시에 start → 정확히 1개만 202
- start 후 H5/H6 → `INVALID_PHASE`

**완료:** T5-01 시나리오 전부 pass, 경쟁 시험 100회 반복 시 수락 1건 유지

---

## S4. 실행 연결·admit/observe/fence/finalize·응답 유실

**목표:** 수락된 작업을 I4로 실행하고, 효과 예약·관측·오류 정지를 원자적으로 처리한다.

**파일:** `store/atomic.py`(admit/observe/fence/finalize), `coordinator.py`(run_job, recover), `test_s4_atomic.py`

### S4-1 STORE 연산 (common-integration-v1 `storage.operations`)

```python
admit(conn, ctx, operation: dict) -> permit_id            # S-ADMIT
observe(conn, ctx, observation: dict, evidence: list[dict]) -> None   # S-OBSERVE
fence(conn, registration_id, error: dict) -> None         # S-FENCE: active -> stopping
finalize(conn, registration_id, result: dict) -> None     # stopping/active -> stopped|done
```

| 연산 | 트랜잭션 안 검사 | 결과 |
|---|---|---|
| admit | job `active`, worker lease 현재값, operation이 accepted scope의 등록 operation이고 `binding_digest` 일치, fence 없음, effect_key 미예약 | effects에 `reserved` 1행. 이미 confirmed/reserved/unknown이면 거부 |
| observe | admit된 operation·lease·registration·target 일치 | observation·evidence 저장(같은 ID는 dedupe), effect 상태 갱신. stopped 이후에도 근거 추가 가능, 상태는 그대로 |
| fence | job `active` | `stopping`. 이후 admit 전부 거부. 증명되지 않은 `reserved` 효과는 `unknown` |
| finalize | `stopping` 또는 (done 조건 충족한) `active` | `done`은 goal confirmed + 미해결 효과 없음일 때만. 그 외 `stopped`. 종료 상태는 다시 열지 않음 |

- `effect_key = (environment, platform, external_account_ref, object_kind, slot_ref, logical_operation_id)` 를 canonical 문자열로 만들어 PK로 쓴다. 요청 key·버전·worker가 바뀌어도 같은 효과는 같은 key. **logical_operation_id = 프로필 `step_id`** — runtime이 `operation_id`만 바꿔 같은 효과를 다시 예약하지 못하게 한다.
- read 단계(`effect_class=read`)는 effect를 예약하지 않고 permit만 준다. fence 이후(stopping)에도 read는 허용(늦은 확인 조회).
- `binding_digest = sha256(canonical({step_id, bound: 승인 values 중 step.bindings, asset_digests(main_images 단계), target, profile_digest}))` — gateway.`operations(ctx)`가 계산해 runtime에 준다(R05와 합의 필요).
- 판정은 runtime 보고서가 아니라 **STORE에 기록된** observation·evidence만으로 한다. goal_observation은 같은 내용의 goal EvidenceRecord가 STORE에 있을 때만 신뢰.
- 한 번도 admit되지 않고 끝난 작업은(모든 변경은 admit이 먼저이므로) 효과가 없었다고 보고 `not_reached`.
- fence와 admit은 같은 job 행 잠금(`BEGIN IMMEDIATE`)으로 직렬화된다.
- R05 remote가 admit/observe/fence를 호출해야 하므로, `StoreGateway` 객체(ctx를 받아 위 함수 호출)로 노출한다. 실제 노출 형식은 R05·R01과 합의(PLAN §7).

### S4-2 run_job(registration_id)

1. `ExecPort.execute({"accepted": AcceptedScope})` 호출(트랜잭션 밖)
2. 반환 `ExecutionReport` 검증. `error`가 있으면 `fence` → 결과 판정(S5) → `finalize`
3. 정상 보고면 결과 판정(S5) → confirmed면 `finalize(done)`, 아니면 fence 후 `finalize(stopped)`
4. 포트 예외(응답 유실·crash) → `fence`, 진행 중 효과는 unknown, `finalize(stopped)`. **자동 재실행하지 않음**

### S4-3 recover() — 재시작 시

`state=active`인데 현재 worker가 없고 관측 안 된 admission이 있는 job → `fence` + unknown 보존 + `stopped`. 자동 재개하지 않는다.

**시험(test_s4_atomic.py)** — T5-12, DV-01
- 미등록 action·binding_digest 불일치·오래된 lease → admit 거부, effects 0행
- 같은 operation 두 번 admit → 두 번째 거부
- **fence 경쟁:** admit과 fence를 동시에 반복 → fence 이후 admit 0건
- 효과 전 응답 유실(admit 전 예외) → absent, stopped
- 효과 후 응답 유실(admit 후 observe 없이 예외) → unknown 보존, stopped, 재실행 없음
- worker crash 후 `recover()` → stopped, unknown 유지
- 같은 key 재전송/다른 payload/다른 key 같은 의도(DV-01) → 새 효과 0
- stopped 이후 observe로 근거 추가 → 상태는 stopped 유지

**완료:** T5-12·DV-01 시나리오 pass, 경쟁 시험 반복 안정

---

## S5. 결과 판정(I5)·조회(H8, H9)

**목표:** 증거만으로 결과를 판정하고, 저장된 상태를 조회한다.

**파일:** `result.py`, `coordinator.py`(조회), `test_s5_result.py`

### S5-1 evaluate(EvaluateInput) -> Result (순수 함수, I/O 없음)

판정 규칙(profile `goal` 기준):
1. `report.goal_observation`이 없으면 → `unknown`(`EVIDENCE_INSUFFICIENT`)
2. `method`가 `profile.goal.methods`에 없으면 → `unknown`
3. `target`이 accepted scope의 target identity와 다르면 → `not_reached` 또는 `unknown`(오류 기록)
4. `payload_digest`가 accepted scope 값으로 계산한 digest와 다르면 → `not_reached`(성공 금지)
5. `requires_asset_digests`이면 `asset_digests`가 scope assets의 digest 집합과 같아야 함
6. `observed_state == goal.observed_state` 이고 미해결(`unknown`/`reserved`) 효과가 없을 때만 → `confirmed`
7. 판정기 내부 오류 → `unknown`(fail closed)

- `next_action`은 사람이 읽을 안내(예: "플랫폼에서 직접 등록 여부를 확인하세요. 자동 재제출하지 않습니다.")
- 크몽·숨고 mock 모두 `independent_readback` 증거가 있어야 confirmed
- replay `I5`(confirmed)·`I5-unknown`과 같은 입력이면 같은 출력을 내야 한다

### S5-2 조회

- H8 `get_registration(owner_ref, id)` — 저장된 View만. 외부 readback·상태 변경 없음. 타 owner → `NOT_FOUND`
- H9 `list_registrations(owner_ref, query)` — S1 cursor 규칙, 생성순 + registration_id
- View의 `progress`는 effects·observations에서 계산(참고용), `result`는 종료 시 필수

**시험(test_s5_result.py)** — AC3, T5-05
- replay I5 → confirmed, I5-unknown → unknown
- goal 증거 없음·method 불일치·가격 digest 불일치·이미지 digest 누락 → confirmed 아님
- 미해결 효과가 남으면 goal이 맞아도 done 아님
- 비소유자 H8 → 404, H8 반복 호출해도 DB 변경 0(행 수·updated_at 비교)
- DB 재연결 후 active/stopped job 조회 유지(UI 재접속)

**완료:** 시험 통과. 이 시점에 **크몽 정상 경로 MVP 핵심**(S0~S5) 완료

---

## S6. 첨부 검증 강화

**목표:** T6-01 시나리오 전체를 만족하도록 H1 첨부 검증을 확장한다.

**파일:** `coordinator.py`(H1), `ids.py`(이미지 헤더 파서), `test_s6_assets.py`

- PNG: 시그니처 + IHDR에서 가로·세로, JPEG: SOI + SOF0/SOF2에서 가로·세로
- 허용 MIME `image/png`, `image/jpeg`만. 선언 MIME과 바이트 판정이 다르면 거부
- 크기 상한은 프로필 규칙 확인 후 상수로 둔다(기본 5MB, 근거 미확인 표시)
- 외부 URL 참조·다른 owner asset 재사용 → 거부
- multipart part 누락·추가·중복 → `INVALID_REQUEST`
- 저장 digest = 바이트 SHA-256. `fixtures/shared/mock-image.png`(652×488)로 정상 경로 확인
- 거부된 요청은 sources·assets 저장 0건

**완료:** T6-01 시나리오 pass

---

## S7. 한 원본·두 플랫폼 독립성

**목표:** 같은 원본으로 만든 크몽·숨고 등록이 서로 영향을 주지 않음을 보장한다.

**파일:** `test_s7_multi_platform.py`(구현 변경은 필요할 때만)

- 같은 source_id로 kmong·soomgo 등록 생성 → 값·target·review·job·result 독립
- 한쪽 H5 수정은 다른 쪽 revision·values 불변
- 원본 사실 수정은 새 Source로만, 기존 등록이 참조하는 과거 원본 불변
- 두 등록의 effect_key는 플랫폼이 달라 서로 막지 않음. 같은 플랫폼·같은 slot의 두 번째 등록은 `DUPLICATE_RISK`

**완료:** T5-06 시나리오 pass

---

## S8. HTTP 계층·통합 연결

**목표:** CO 유스케이스를 H1~H9 HTTP로 노출하고 R02·R04·R05 모듈과 연결한다.

**착수 조건:** R01이 HTTP 프레임워크를 결정(FastAPI 제안, PLAN §7)하고 제품 `pyproject.toml`·`uv.lock`에 반영

**파일:** `http/` (프레임워크 어댑터), `service.py`, `test_s8_http.py`

- 라우트는 common-integration-v1 `routes` 그대로(`/v1` 9개). 핸들러는 입력 파싱 → CO 호출 → View 직렬화만
- 오류는 `AppError.to_view()` + §0.4 status
- owner는 인증 컨텍스트에서만(개발 모드는 테스트용 헤더, 운영 인증 방식은 R01·R04와 합의)
- H1 multipart: manifest part(`SourceInput` JSON) + `new_assets[].part_name` 파일 part
- H7 수락 후 실행은 백그라운드 worker로 `run_job` 호출. 서버 시작 시 `recover()` 실행
- 포트 0, 127.0.0.1만. DB 경로는 `.local/` 또는 테스트 임시 경로

**시험(test_s8_http.py)**
- replay `http` 목록(H1~H9, H6-open/finish)의 요청을 실제 서버에 보내 status·응답 형식 검증(값은 id·시각 제외 비교)
- 오류 status 매핑 표 전수
- 실제 R02 PREP·R05 remote 구현이 나오면 fake 대신 주입해 같은 시험 반복

**완료:** H1~H9 HTTP 시험 pass, R04 UI가 replay 서버 대신 이 서버로 동작

---

## 9. 단계별 완료 표

| 단계 | 산출 | 수용 조건 | 제품 시험 | MVP(12/8) 전 필수 |
|---|---|---|---|---|
| S0 | 계약 로드·검증기·포트 | — | — | ✅ |
| S1 | STORE·H1~H3 | AC1 | T5-11 일부 | ✅ |
| S2 | KNOW·H4·H5 | AC1 | — | ✅ |
| S3 | H6·H7·accept | AC1·AC2 | T5-01 | ✅ |
| S4 | admit/observe/fence/finalize | AC2·AC3 | T5-12, DV-01 | ✅ |
| S5 | RESULT·H8·H9 | AC3 | T5-05 | ✅ |
| S6 | 첨부 검증 | AC1 | T6-01 | MVP 이후 가능 |
| S7 | 두 플랫폼 독립성 | AC1 | T5-06 | MVP 이후 가능 |
| S8 | HTTP·통합 | AC1 | 통합 smoke | 프레임워크 결정 즉시 |

각 단계가 끝나면 PLAN §5.3 규칙대로 명령·commit·입력·기대·관측·pass/fail/incomplete를 기록한다. bootstrap replay 통과는 제품 통과가 아니다.

### 9.1 요구사항 연결 (TASK-050 `product_requirement_refs`)

요구사항 정의는 `implementation-v0.4.json`의 REQ-01~11 수용 기준을 따른다. 같은 요구사항이라도 r03-app이 맡는 부분만 적고, 나머지 담당은 오른쪽 열에 남긴다. 결과를 기록할 때는 아래 "검증" 열의 시험 이름과 REQ ID를 함께 적는다.

| REQ | 요구사항(수용 기준 요약) | r03-app이 맡는 부분 | 단계 | 검증 | r03-app 밖 |
|---|---|---|---|---|---|
| REQ-01 | 원본·필수 정보·자료 준비: 사용자 확인 사실·이미지와 출처·버전, 누락/충돌 질문, 합성 가격 값을 바꾸지 않음 | 불변 Source 버전·첨부 바이트 hash 저장, PREP 이슈를 View로 노출, H5에서 질문→field→ResolvedAnswer 정규화, 원본 사실 수정은 새 Source로만 | S1, S2, S6 | test_s1_source(버전·불변), test_s2_prepare(I2-missing ready=false·가격 미생성, 답변 정규화), test_s6_assets | 사실 추출·질문 생성(R02 PREP) |
| REQ-02 | 등록 대상 식별: 지원 대상 registry 연결, 미지원·잘못된 대상 차단, 임의 URL 요청 금지 | KNOW(I1) 로컬 registry 조회, unsupported/blocked를 정상 View로 저장하고 외부 접근 0, 형식 오류 selector 거부 | S2 | test_s2_prepare(unsupported selector → PREP 호출 0, 형식 오류 → INVALID_REQUEST) | URL 입력 해석(WBS W10, TASK-050 범위 밖) |
| REQ-03 | 플랫폼별 변환·검토: 사실/단위 유지, LLM 제안과 확인값 구분, 필수 규칙·권리 검사, 확인 필요 항목 노출 | Preparation(values·facts·provenance·issues)을 검증 후 그대로 저장·노출, 승인 범위를 ReviewView+digest로 고정, rights_confirmed=false 첨부 거부 | S2, S3, S6 | test_s2_prepare(Preparation 검증·blocking issue 유지), test_s3_auth_start(review digest), test_s6_assets(권리 없음 거부) | 변환·LLM 제안 생성(R02), 화면 표시(R04) |
| REQ-05 | 실행 대상·승인·권한: 계정·대상·버전·동작·환경 승인, 가드 미충족이면 동작 0, 동일 효과 차단 | H7 선행 검사(revision·review digest·verified·target new·profile), accept 원자 기록, admit의 등록 operation·binding_digest·lease 검사, effect_key 유일성, environment=mock만 허용 | S3, S4 | test_s3_auth_start(T5-01: 위조·오래된 digest 효과 0, 경쟁 시 1건만 수락), test_s4_atomic(T5-12: 미등록 action·old lease 거부, 같은 효과 재예약 거부) | 실제 인증·runtime 실행(R05) |
| REQ-06 | 크몽 최초 등록: 필드·이미지·가격 입력, 모의 심사 접수 후 독립 receipt 재조회 일치 | 크몽 프로필로 전 흐름 연결, RESULT가 independent_readback·payload digest·이미지 digest가 승인 범위와 같을 때만 confirmed | S2~S5 | test_s5_result(I5 confirmed, 가격·이미지 digest 불일치 → confirmed 아님), kmong replay 기반 흐름 시험 | 크몽 adapter·mock 페이지(R05 r05-kmong) |
| REQ-07 | 숨고 최초 등록 확장: 서비스 카테고리·문항 설정 저장 후 재조회 일치 | 숨고 프로필로 같은 흐름 지원, 같은 원본의 크몽·숨고 등록 독립성 | S2~S5, S7 | soomgo replay 기반 흐름 시험, test_s7_multi_platform(T5-06) | 숨고 adapter·mock 페이지(R04 r04-soomgo) |
| REQ-08 | 결과·부분 효과·실패: 완료/실패/차단/확인 필요/미확인 표시, 증거·다음 조치, 응답 유실 후 중복 없음, 접수와 공개 분리 | GoalVerdict(confirmed/not_reached/unknown)와 EffectSummary·next_action 저장, 응답 유실 시 unknown 보존·자동 재실행 0, recover()의 fence+stopped, H8/H9 무변경 조회 | S4, S5 | test_s4_atomic(DV-01: 효과 전·후 응답 유실, crash 복구), test_s5_result(증거 부족 → unknown, H8 GET 무변경) | 결과 화면(R04) |
| REQ-10 | 격리·개인정보·안전한 운영: owner 격리, mock/live 차단, 로그인 입력·비밀 미기록, 승인 자료만, 세션 만료·폐기 | 모든 조회·변경에 owner 검사(타 owner 404), owner를 클라이언트 입력에서 받지 않음, View에 connection_ref·account_ref·자격증명 미노출, environment≠mock 거부, cursor owner 바인딩 | S1~S5, S8 | test_s1_source(타 owner·변조 cursor), test_s3_auth_start(View에 내부 binding 없음), test_s5_result(T5-05 비소유자 404), test_s0_contract(environment=live 거부) | 세션 폐기·브라우저 격리(R05), 배포 보안(R01) |

TASK-050 대상이 아닌 요구사항: REQ-04(원격 직접 인증, R05), REQ-09(플랫폼 확장 구조, W10), REQ-11(재현성·가치 평가, R01 통합). r03-app은 이들의 계약을 지키지만 완료 근거를 따로 만들지 않는다.

**계약 우선순위 주의:** REQ-08 수용 기준에 "읽기 재확인 + 명시 재개"가 있지만, 더 최신인 공통 설계 V1(CS-05)은 수락 후 사용자 취소·재개·rollback을 두지 않는다. 이 문서는 CS-05를 따른다. 즉 stopped 이후 읽기 전용 근거 추가만 허용하고 작업을 다시 열지 않는다(§10).

## 10. 미결정·가정

| 항목 | 이 문서의 가정 | 확인 대상 |
|---|---|---|
| 종료 연산 이름 | 계약 storage `S-FENCE`의 `finalize` 사용 | R01 (PLAN §7의 `terminal` 표기는 이것으로 통일) |
| 포트 호출 방식 | 동기 함수 | R02·R05 |
| STORE 노출 | `StoreGateway` 객체 주입 | R05·R01 |
| HTTP 프레임워크 | S8 전까지 없음 | R01 |
| 첨부 크기 상한 | 5MB(근거 미확인) | 프로필 규칙 |
| 이미지 구조 검사 | PNG: 모든 chunk CRC, IHDR 첫 chunk, IEND에서 정확히 끝남(뒤에 붙은 바이트 거부). JPEG: 세그먼트 구조·SOF0/1/2·EOI 끝. 가로·세로 1~20000(임시 상한) | 프로필 규칙 |
| 선언 MIME | multipart part의 Content-Type을 `(bytes, content_type)`로 받아 바이트 판정과 다르면 거부(파라미터·대소문자 무시) | S8 HTTP 계층 |
| 개발용 owner 인증 | 테스트 헤더 | R01·R04 |
| 준비·인증 시간 제한 | 수치 미정(계약: 구현 실험 후) | 측정 후 |
| 공유 사실 판정 | CO는 의미를 판단하지 않음. replay의 모든 field가 `direct` 출처라 CO가 판정하면 수정이 불가능해짐 → PREP의 `conflict` 이슈로만 `FACT_CONFLICT` | R02 (PREP이 conflict 이슈를 내는 기준) |
| PREP 실패 | 포트 예외 → `model_unavailable` blocking 이슈로 정상 저장(201), 형식 위반 출력 → 503 `RUNTIME_ERROR`·저장 안 함 | R02 |
| profile digest | 고정 profile 항목 전체(value_schema 포함)의 canonical SHA-256. replay의 `aaaa…`는 자리표시값 | R01 |
| H9 정렬 | 계약 "creation then registration_id"를 H2와 같은 최신순(`created_at DESC, registration_id DESC`)으로 해석. cursor는 종류(sources/registrations)·owner에 묶임 | R04 (UI 목록 순서) |
| progress 계산 | 단계 상태 = effect 상태(쓰기 단계) 또는 관측 verdict(read 단계), 없으면 pending. step_index = 앞에서부터 연속 confirmed 수. 멈춘 작업의 pending 현재 단계는 `error`, 멈춘 작업의 reserved는 `unknown` | R04 |
| replay I5 비교 | goal_verdict·effects·error만 비교. evidence 목록·next_action 문구는 replay와 다름(replay는 goal 증거만 표시) | R01 |
| StoreGateway API | 공통 `GatewayStore`에 맞춤: `admit(context, op)→Permit`, `record_observation(context, obs, evidence[])`, `fence(registration_id, error)`. 추가 helper: `acquire_context(rid)→WorkerContext`(lease를 STORE에 등록, runtime이 RT-01 안에서 호출해 불투명하게 보관), `expected_operations(context)`. goal 증거는 마지막 read 단계 observation과 함께 `record_observation`으로 기록 | R05 (lease 등록 방식·helper 2개) |
| 스키마 검증기 | 앱 내장 검증기 유지(제품 의존성 0). IB-02 표준과 어긋나지 않음을 `test_contract_alignment`가 jsonschema 4.25.1과 같은 판정인지 비교(설치 시 실행) | R01 (제품 의존성에 jsonschema 추가 여부) |
| payload_digest | 승인 `scope.values`의 canonical SHA-256. replay의 `bbbb…`는 자리표시값이라 그대로는 confirmed가 안 됨 | R05 |
| binding_digest | §S4-1 규칙 | R05 |
| 실행 중 revision | fence·finalize마다 revision +1 (UI가 오래된 응답 무시) | R04 |
| H6 revision | open·finish·close·refresh 모두 revision +1 (replay H6-open/finish와 같음). 인증 실패·timeout은 `closed`로 저장 후 오류 반환 | R04 (UI 재조회) |
| target_label | TrustedTarget에 없어 `"{platform} 신규 {object_kind}"`로 생성 | R05 (runtime이 label 제공 여부) |
| 시작 후 review | 시작 후 View에서 review 생략(replay H7과 같음), AcceptedScope에 보존 | — |
| REQ-08 "명시 재개" | 공통 설계 V1 CS-05(재개 없음)를 따름. stopped 이후는 읽기 근거 추가만 | R01 (요구사항 문구 갱신 여부) |
