# r03-app 상세 설계 및 구현 계획 — TASK-050 (R03)

- 작성일: 2026-11-25 · 작성: R03
- TASK: [TASK-050](../../../../../docs/artifacts/tasks/TASK-050.json) "공통 앱·API·저장·결과 판정 구현" · 상태: R01 배정, 착수 준비
- Phase: [PHASE-20261125-01](../../../../../docs/human/phase-intents/PHASE-20261125-01.md) 공통 계약 기반 mock 제품 개발
- 패키지: `r03-app` · 브랜치: `r03/product-app` · 기준 commit: `98b446c` (bootstrap), 배정 `65aed37`, **공통 기준 `c4742a1`** (main 병합, `check-changes --base`)
- 담당 경로: `src/lesson_registration/app/`, `tests/modules/app/`
- 근거 설계: CS-01·02·03·05·06 ([공통 설계 V1](../../../../../docs/artifacts/design/lesson-registration-20261124/COMMON-INTEGRATION-V1.md), common-integration-v1.json, data-schema-v4.1.json, platform-profiles-v2.json)

> 이 문서의 결정은 r03-app 내부의 국소 결정이다. 공통 계약·의존성·다른 담당 영역에 영향을 주는 항목은 §7에 따로 모아 R01에게 제안한다.

## 1. 목적과 범위

공통 서버(H1~H9)와 CO·KNOW·STORE·RESULT를 구현한다. PREP(I2, R02)와 인증·실행 facade(I3/I4, R05)는 주입받아 크몽·숨고 모의 등록이 원본 입력부터 결과 판정까지 일관되게 처리되게 한다.

| 포함 | 제외 |
|---|---|
| H1~H9 API, 오류 코드·status 통일, 소유권·revision 검사 | 브라우저 runtime·viewer (R05) |
| CO: 흐름 조정·업무 상태 전이 단독 소유 | PREP/AI 내부 (R02) |
| KNOW: I1 프로필 registry 직접 구현 | 플랫폼 adapter operation (R04 숨고, R05 크몽) |
| STORE: 영속 저장, 원자 accept/admit/observe/fence | UI (R04) |
| RESULT: I5 증거 기반 판정 직접 구현 | 공통 계약·stub·fixture·composition (R01) |

**관련 요구사항(TASK-050):** REQ-01·02·03·05·06·07·08·10
**mock-only:** 실제 플랫폼 접속·계정·자격증명 취급 금지

## 2. 지킬 규칙 (공통 계약에서)

1. 원본 사실은 불변이다. 변경되면 새 Source 버전, 플랫폼별 선택은 등록 요청에만 저장한다(CS-02).
2. 서버가 현재 질문 → field → answer_id를 확정해 PREP에 전달하고 다시 검사한다. 강사가 확인하지 않은 가격·조건은 생성하지 않는다.
3. 원본·준비·인증은 요청 안에서 끝내거나 명시적 오류/준비 이슈로 반환한다. H7만 durable accept 직후 202를 반환한다(CS-03).
4. 승인 스냅샷과 실제 operation이 일치해야 하고, runtime gateway에 등록된 operation만 admission한다(CS-05).
5. 같은 key는 기존 작업을 재조회하고, 다른 key로 같은 효과를 재발급하는 것은 차단한다. unknown은 자동 재제출하지 않는다.
6. 오류에만 `stopping → stopped`로 전이하고 이후 새 admission을 금지한다. 사용자 취소·재개·rollback은 없다.
7. 관측 근거가 없으면 성공 판정을 금지한다. 실행기 완료와 등록 성공은 다르다(CS-06).

## 3. 상세 설계 결정

### 3.1 모듈 구성

```
src/lesson_registration/app/
  api/          H1~H9 라우팅·입력 검증·오류 매핑·소유자 식별
  coordinator/  CO: 유스케이스(create_source, create_registration, edit, authenticate, start, get, list)
  knowledge/    KNOW: 버전 고정 profile registry, profile hash
  store/        STORE: 스키마·트랜잭션·원자 연산
  result/       RESULT: 판정 규칙
  ports.py      공통 contracts/interfaces.py 타입 재노출 + 앱 전용 Clock (Protocol 복제 없음)
```

| 결정 | 선택 | 대안 | 근거 |
|---|---|---|---|
| D1 계층 | HTTP 계층과 CO 유스케이스 분리. 테스트는 CO를 직접 호출 | API 핸들러에 로직 작성 | 프레임워크가 미정이어도 핵심 로직·시험 진행 가능. R04는 replay 서버로 선행 |
| D2 저장소 | 표준 라이브러리 `sqlite3`, `BEGIN IMMEDIATE` 트랜잭션, 파일은 테스트 임시 경로/`.local/` | 인메모리 dict, ORM | 신규 의존성 없이 원자성·영속성 시험 가능. 공통 DB가 바뀌면 store 모듈만 교체 |
| D3 원자 연산 | 각 연산을 단일 트랜잭션 + 조건부 UPDATE(기대 상태·revision 일치 시만)로 구현 | 앱 레벨 lock | 프로세스 재시작·다중 worker에서도 중복 방지 유지 |
| D4 멱등성 | `(owner, registration_id, request_key)` 유일 제약. 같은 key+같은 payload digest는 기존 작업 반환, 다른 payload는 409 | key만 비교 | DV-01 "same key/conflicting payload" 요구 |
| D5 효과 중복 차단 | CS-05 stable logical effect key `(environment, platform, external_account_ref, object_kind, slot_ref, logical_operation_id=step_id)`를 효과 유일성 기준으로 사용. 요청 멱등 key·승인 digest는 별도 가드(H7) | `(registration, operation, approval_digest)` (R01 검토: 새 등록·승인 변경 시 같은 외부 효과를 못 막음) | 새 등록·다른 key·revision/worker 변경·unknown 모두 같은 효과 재예약 차단 (test_s3 DUPLICATE_RISK, test_s4 DuplicateIntent·AdmissionGuards) |
| D6 포트 주입 | 공통 `contracts/interfaces.py`의 Providers/Protocol을 그대로 사용, `Coordinator(providers=...)` 명시 주입(IB-05) | 로컬 Protocol 정본 | R01 검토: 별도 Protocol 정본 복제 금지 |
| D7 HTTP 프레임워크 | FastAPI 0.128.2 (R01 채택·공통 `app` 그룹 반영 완료) | 표준 `http.server` | multipart·검증·OpenAPI 필요 |
| D8 검증·digest | 공통 `contracts.validation.SchemaCatalog`(jsonschema 4.25.1)와 `contracts/canonical.py` 사용. review digest = 내부 Scope digest, profile digest = 자기 digest 제외 Profile, payload = values, asset = 업로드 순서 목록 | 앱 내장 검사기·자체 digest | R01 권고: 검증 기준 이원화 방지, data-contract-v4 canonical 규칙 |

### 3.2 데이터

| 엔터티 | 주요 필드 | 규칙 |
|---|---|---|
| Source | id, owner, version, content, assets(바이트 hash·MIME·크기) | 불변, 수정 시 새 버전 |
| Profile | platform, version, profile_hash, 필드·절차·목표 정의 | 버전 고정 조회만 |
| Registration | id, owner, source_ref(버전 고정), profile_hash, preparation, answers, revision | 승인 전 H5로만 변경, revision 증가 |
| AuthGrant | registration, binding(내부), 공개 표시 정보 | binding은 응답에 노출하지 않음(CS-04) |
| Approval | registration, revision, snapshot_digest | H7 시점의 정확한 범위만 |
| Job | registration, request_key, payload_digest, state | `null → active → done` / `active → stopping → stopped` |
| Effect | job, operation, admission 시각, outcome(absent/confirmed/unknown) | unknown 보존 |
| Evidence | job, 관측값·readback·digest | EXEC가 기록, RESULT가 판정 |

### 3.3 STORE 원자 연산

| 연산 | 전제 조건(트랜잭션 안 검사) | 결과 |
|---|---|---|
| `accept` | 현재 revision·승인 digest 일치, 인증 grant 유효, 같은 등록에 활성 job 없음 | Job `active` 생성 또는 같은 key 기존 job 반환 |
| `admit` | Job `active`, operation이 승인 범위·등록 목록에 있음, 같은 효과 미예약, fence 없음 | Effect 예약 |
| `observe` | 예약된 Effect | 관측·증거 기록(`stopped` 이후도 근거 추가 가능, 상태 불변) |
| `fence` | Job `active` | `stopping`, 이후 admit 거부 |
| `finalize` | 진행 중 효과 정리 | `done` 또는 `stopped` 확정 |

R05 remote가 admission·fence를 호출하므로, 이 연산을 노출하는 인터페이스 형식은 R05·R01과 맞춘다(§7).

### 3.4 결과 판정(RESULT, I5)

- EvidenceRecord를 승인 스냅샷과 대조한다: profile goal·method·target·payload·asset digest
- 크몽·숨고 mock은 독립 readback(접수 ID·저장값 재조회)이 있어야 confirmed
- 판정: pinned GoalVerdict `confirmed / not_reached / unknown`. 확실한 미도달(대상·값·첨부 불일치)은 not_reached, 증거 부족·결과 미확인은 unknown이며 어느 쪽도 성공으로 표시하지 않는다.

## 4. 구현 순서

각 단계마다 시험을 먼저 쓰고 `dev.py test r03-app`로 확인한다.

| 단계 | 내용 | 완료 확인 |
|---|---|---|
| S0 | 계약 타입·replay 사례(I1, I2, I2-missing, I3, I4, I5) 정독, ports.py | replay 대체 구현으로 포트 호출 통과 |
| S1 | STORE 스키마, Source/Registration 저장, 소유권 | T5-11 일부 |
| S2 | KNOW(I1)·CO 준비 흐름(H1~H5), revision 검사 | H1~H5 정상·누락 |
| S3 | 인증(H6)·승인·accept(H7) | T5-01 |
| S4 | admit/observe/fence/finalize, 중복·경쟁·응답 유실 | T5-12, DV-01 |
| S5 | RESULT(I5), H8/H9 조회 | AC3, T5-05 |
| S6 | 첨부 검증(MIME·크기·hash·multipart) | T6-01 |
| S7 | 한 원본·두 플랫폼 독립성 | T5-06 |
| S8 | HTTP 계층 연결(프레임워크 결정 후), R04·R05·R02 통합 지원 | replay 대신 실제 API로 smoke |

## 5. 시험과 완료 조건

### 5.1 수용 조건

| ID | 기대 결과 | 확인 시험 |
|---|---|---|
| r03-app-AC1 | H1~H9, I1/I5 구현, I2/I3/I4 주입, 소유권·revision 검사 | T5-01, T5-05, T5-11 |
| r03-app-AC2 | 영속 저장 원자 accept/admit/fence, 중복·경쟁·응답 유실 | T5-12, DV-01 |
| r03-app-AC3 | 관측 근거 없으면 성공 금지, 오류 중단 및 조회 복구 | DV-01, T5-05 |

### 5.2 제품 시험(통합 수용 계약)

| 시험 | 시나리오 | 기대 결과 |
|---|---|---|
| T5-01 | 누락·오래된·위조 digest/profile | 현재 검토 범위만 1회 수락, 나머지 효과 0 |
| T5-05 | UI 재접속, 소유자/비소유자 조회, active/terminal | 작업 유지, 비소유자 404, GET 무변경 |
| T5-06 | 한 원본 → 두 플랫폼, 플랫폼별 수정·새 원본 버전 | 값·대상·승인·결과 독립, 과거 원본 불변 |
| T5-11 | 원본 생성/재사용, path/body 주입, 타 소유자 | 식별 보존, 서버 측 검토만, 무효·타인 거부 |
| T5-12 | 중복 operation, 잘못된 binding, 미등록 action, old lease, fence 경쟁 | 등록된 bound action만, 원자 admission, stale·postfence 거부, unknown 보존 |
| T6-01 | 이미지 권리·MIME/크기 불일치, 외부 참조, multipart 누락/추가 | 유효 첨부만 저장, hash 일치, 거부 시 효과 없음 |
| DV-01 | 첨부 실패, 효과 전후 응답 유실, worker crash, 같은 key/다른 payload/다른 key 같은 의도 | 오류에만 정지, 이후 효과 없음, absent/confirmed/unknown 구분 |

### 5.3 기록과 완료 판정

- 결과마다 명령·commit·입력·기대·관측·pass/fail/incomplete를 기록한다.
- bootstrap replay 통과는 제품 통과가 아니다. 미실행·실패·unknown은 완료가 아니다.
- 22개 제품 수용 시험은 R01이 같은 후보·계약·fixture·환경에서 판정한다.

## 6. 공수 추정과 일정 (검토용)

R03 작성자 추정이며, 가용시간 확인 후 R01과 확정한다.

| 항목 | 추정(인일) |
|---|---:|
| 설계 정독·PLAN·포트 정의 (S0) | 1 |
| STORE·원자 연산·멱등성 (S1, S4) | 2.5 |
| KNOW·CO·상태 전이 (S2, S3) | 1.5 |
| RESULT·조회 (S5) | 1 |
| H1~H9 HTTP·오류 매핑·첨부 검증 (S6, S8) | 2 |
| 제품 시험 작성(경쟁·응답 유실 포함) | 2 |
| 통합 연결 지원(R02·R04·R05) | 1 |
| **합계** | **약 11** |

- 목표: 12/8 mock MVP, 1/4 최종(일정은 미확정).
- 위험: 11/26~12/8은 9근무일이라 MVP 전 전체 완료가 빠듯하다. 12/8 전에는 크몽 정상 경로 + 원자 수락/중복 방지 + readback 판정(S0~S5, T5-01·T5-12·DV-01)을 우선하고, T5-06·T6-01 세부와 H2/H9 목록 기능은 MVP 이후로 미루는 순서를 제안한다.
- WBS V0.5 기준으로 이후 W10(URL registry)·W16(최종 결함 수정)과 R02 PREP 인계 후 유지보수가 추가될 수 있다. TASK-050 범위 밖이므로 별도 배정 시 다시 산정한다.
- R01 검토(11/25): 위 우선순위는 WBS 후보에 반영됐지만 H2/H9·T5-06·T6-01 등 필수 계약·시험의 연기를 승인한 것은 아니다. 22개 gate 미충족이면 MVP 미완료/부분 시연으로 보고한다. (H2/H9·T5-06·T6-01은 이미 구현·시험 완료)

### 6.1 진행 현황과 잔여 공수 (2026-11-25 갱신)

| 구분 | 상태 | 잔여 추정(인일) |
|---|---|---:|
| S0~S7 (STORE·KNOW·H1~H7 유스케이스·H8/H9·원자 연산·RESULT·첨부·두 플랫폼) | 완료, `dev.py test r03-app` 177 통과 | 0 |
| 공통 계약 정렬 (IB-01~05, 공통 validator·canonical digest) | 완료 | 0 |
| S8 FastAPI HTTP 계층 (multipart, 오류 매핑, worker·lifespan·recover) | 서버 구현·독립 HTTP 시험 14개 통과, 실제 UI 연결 미확인 | 0 |
| R05 STORE·lease·operation 연동 (R05 착수 후) | 임시안 구현, 협의 대기 | 1 |
| R04 API·viewer 연결 | 미착수 | 0.5 |
| R02 I2 실제 bridge·timeout | 미착수 | 0.5 |
| 22개 gate 대비 결함 수정·통합 지원 | — | 1 |
| **잔여 합계** | 통합에서 발견되는 결함에 따라 재산정 | **약 3** |

## 7. R01 결정 반영 (2026-11-25 회신)

| 항목 | R01 결정 | 반영 |
|---|---|---|
| HTTP 프레임워크 | FastAPI 채택, 공통 의존성(app 그룹) 반영 | S8 진행. 추가 의존성 필요 시 이 PLAN에 요구를 적고 R01이 lock 반영 |
| jsonschema | 제품 의존성 반영, 공통 표준 검증기 사용 권장 | 앱 내장 검사기 제거, `contracts.validation.SchemaCatalog` 사용 (D8) |
| REQ-08 | 최신 CS-05/06 적용. 중단 후 읽기 근거 추가만, 재개 없음 | 구현 그대로 (SPEC §10) |
| 종료 연산 | `finalize` | 그대로 |
| digest | 공통 `contracts/canonical.py`·`fixtures/shared/canonical-vectors.json` 반영. binding 대상·operation 규칙은 R05와 협의, 공통 replay 변경은 R01 | canonical 적용·golden vector 시험 추가 (D8). binding은 §7.1 |
| 범위 | TASK-050 집중. W10·W16·PREP 유지보수는 확정 배정 아님 | §6 잔여 공수에서 제외 |

### 7.1 공통 접점 협의 (INTERFACE-REVIEW 반환 형식)

2026-11-25 후속: main `094e4d2` / R03 `4a240ee` 위에서 구현한
[runtime 연결 결정 및 사용 예제](RUNTIME-INTEGRATION.md)를 적용한다.
Source 계보 slot, 승인 바이트 reader, 로컬 HTTP/WS 세션 조립, opt-in D01 binding.v1,
durable Permit consume을 추가했다. R05 context 전달/consume 호출 및 실제 dispatch-fence
직렬화 wrapper를 R03에서 구현했다. R05 실제 dispatch 연결과 R04 UI 조립은 후속이며
기존 3인일 추정은 공동 E2E 후 재산정한다. 앱 201개 전체 통과(75.271초), doctor,
check-changes(base 094e4d2), diff 검사 통과. 상세 근거: runtime-integration-evidence.json.

공통 기준 SHA: `c4742a1`. 아래 "임시안"은 r03 독립 구현이며 상대 담당과 합의 완료가 아니다.

| 접점 | 상대 | 유지/변경 서명·예제 | 이유 | 정상·실패·unknown 시험 | 남은 확인 |
|---|---|---|---|---|---|
| CoordinatorStore | (R03 내부) | `accept(owner, registration_id, start, scope) -> RegistrationView`, `fence(registration_id, error)`, `finalize(registration_id, result) -> "done"\|"stopped"` 유지. 내부적으로 `accept_with_status`로 202/200 구분 | 공통 Protocol 그대로 | test_s3 Start·StartRace, test_s4 | 없음 |
| GatewayStore | R05 | `admit(context, operation) -> Permit`, `record_observation(context, observation, evidence[]) -> Observation`, `fence(registration_id, error)` 유지. **추가 helper 제안**: `acquire_context(registration_id) -> WorkerContext{registration_id, lease}`(RT-01 안에서 호출해 lease를 STORE에 등록), `expected_operations(context) -> Operation[]` | STORE가 현재 worker를 알아야 admission에서 old lease를 거부할 수 있음 (CS-05). context/permit은 runtime이 불투명하게 보관 (IB-03) | 정상: test_s4 HappyPath. 실패: forged lease·미등록 step·binding 변조·효과 class 위조·중복 효과. unknown: 효과 후 응답 유실, worker crash→recover | R05: lease 등록 방식 수용 여부, helper 2개 유지 여부, timeout 수치 |
| Operation·binding digest | R05 | 임시안: `binding_digest = json_digest({step_id, bound: step.bindings의 승인 values, asset_digests(첨부 단계, 업로드 순서), target, profile_digest})`, logical_operation_id = step_id | 공통은 "exact immutable bound values"만 고정, 계산 대상은 R05와 협의 (R01 회신) | AdmissionGuards binding 변조 거부 | R05 manifest·slot 규칙과 대조 |
| goal readback 증거 | R05 | goal EvidenceRecord를 마지막 read 단계 observation과 함께 `record_observation`으로 기록, payload = `json_digest(scope.values)`, asset = 업로드 순서 목록 | GatewayStore에 별도 goal 메서드 없음, data-contract-v4 canonical | test_s5 EvaluateRules, test_s4 LostResponses | R05 normalize 매핑 |
| H1~H9 API | R04 | 공통 routes 9개 그대로, 오류 status는 http.status_codes, H6 open/finish/close/refresh 모두 revision +1, 시작 후 review 생략, H9 최신순 | 공통 계약·replay와 동일 | S8 실제 loopback HTTP 시험 14개 통과 | R04 UI 재조회·목록 순서 확인 |
| Viewer | R04·R05 | R03은 H6 응답에 AuthGrant(open/refresh)만 전달, grant는 저장하지 않음, finish 이후 human 입력 차단은 runtime 책임 | IB-04, CS-04 | test_s3 grant 비저장·세대 교체 | endpoint/message 타입은 R04·R05 결정 후 S8에 연결 |
| I2 | R02 | `PreparationPort.prepare` 동기 호출, PortFailure `MODEL_UNAVAILABLE`→저장되는 준비 이슈, 기타 허용 코드만 전달, ready=true면 profile value schema 통과 필수, 방금 수정한 field의 blocking conflict → FACT_CONFLICT | 계약 H4/H5, 단일 검증 기준 | test_s2, test_contract_alignment | R02 timeout·실제 모델 bridge, conflict 이슈 기준 |

## 8. 로컬 환경 확인

2026-11-25 실행 기록:

```sh
cd product/lesson-registration
uv sync --locked --python 3.12
uv run --locked --python 3.12 python dev.py doctor          # passed: source pins, ownership, synthetic image
uv run --locked --python 3.12 python dev.py test r03-app    # independent bootstrap replay passed
```

이 결과는 경로·fixture 연결만 확인한 것이며 기능 검증이 아니다. 변경 범위 검사: `python dev.py check-changes r03-app --base c4742a1` (공통 기준 갱신 시 이 SHA도 갱신)

### S8 독립 검증 (2026-11-25)

- 기준: `fa40128df3e652efc93948cc87a23d52b5662f2c` 위 미커밋 작업 트리. 공통 기준 `c4742a1`, 기존 공통 정렬 수정 보존.
- `uv run --locked --group app --group verification python dev.py test r03-app`: 191개 통과(기존 177 + HTTP 14), 49.350초. 실제 127.0.0.1 임시 포트·SQLite와 명시 주입한 SchemaPrep/GatewayRuntime 사용.
- `doctor`, common 5개, standard_schema 10개, integration 2개 통과. 제품 통합 성공을 의미하지 않는다.
- `check-changes --base c4742a1`는 기존 daily 두 파일 때문에 실패했다. TASK 결과/프로젝션은 별도 문서 갱신이며 패키지 소유 경로 검사 밖이다. 공유 lock·다른 담당 코드 수정 없음.
- [구조화 검증 정본](../../../../../docs/artifacts/runs/TASK-050-s8-http-20261125.json): 입력·기대/관측·명령·코드 SHA256·미확인 범위. [TASK 결과](../../../../../docs/artifacts/tasks/TASK-050.json)는 진행 중이며 완료로 표시하지 않는다.
- 진입점: `lesson_registration.app.http.create_app(coordinator, ...)`, `lesson_registration.app.service.serve(coordinator, ...)`. 세부 인증·multipart·수명/종료 제한은 SPEC S8 참조.
- [FastAPI lifespan 문서](https://fastapi.tiangolo.com/advanced/events/)의 시작/종료 수명 모델을 적용했다. UI/viewer·실제 provider·22개 gate는 후속 통합에서 확인한다.
