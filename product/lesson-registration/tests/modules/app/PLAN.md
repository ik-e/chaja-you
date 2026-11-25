# r03-app 상세 설계 및 구현 계획 — TASK-050 (R03)

- 작성일: 2026-11-25 · 작성: R03
- TASK: [TASK-050](../../../../../docs/artifacts/tasks/TASK-050.json) "공통 앱·API·저장·결과 판정 구현" · 상태: R01 배정, 착수 준비
- Phase: [PHASE-20261125-01](../../../../../docs/human/phase-intents/PHASE-20261125-01.md) 공통 계약 기반 mock 제품 개발
- 패키지: `r03-app` · 브랜치: `r03/product-app` · 기준 commit: `98b446c` (bootstrap), 배정 `65aed37`
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
  ports.py      I2/I3/I4 Protocol 정의(공통 계약 타입 그대로) + 주입 지점
```

| 결정 | 선택 | 대안 | 근거 |
|---|---|---|---|
| D1 계층 | HTTP 계층과 CO 유스케이스 분리. 테스트는 CO를 직접 호출 | API 핸들러에 로직 작성 | 프레임워크가 미정이어도 핵심 로직·시험 진행 가능. R04는 replay 서버로 선행 |
| D2 저장소 | 표준 라이브러리 `sqlite3`, `BEGIN IMMEDIATE` 트랜잭션, 파일은 테스트 임시 경로/`.local/` | 인메모리 dict, ORM | 신규 의존성 없이 원자성·영속성 시험 가능. 공통 DB가 바뀌면 store 모듈만 교체 |
| D3 원자 연산 | 각 연산을 단일 트랜잭션 + 조건부 UPDATE(기대 상태·revision 일치 시만)로 구현 | 앱 레벨 lock | 프로세스 재시작·다중 worker에서도 중복 방지 유지 |
| D4 멱등성 | `(owner, registration_id, request_key)` 유일 제약. 같은 key+같은 payload digest는 기존 작업 반환, 다른 payload는 409 | key만 비교 | DV-01 "same key/conflicting payload" 요구 |
| D5 효과 중복 차단 | Effect를 `(registration, operation, approval_digest)`로 유일화. 다른 key로 같은 의도는 거부 | key별 효과 허용 | CS-05 "다른 key로 동일 효과 재발급 차단" |
| D6 포트 주입 | `typing.Protocol` 인터페이스, 생성자 주입. 테스트는 `dev.replay` 기반 대체 구현 | 전역 레지스트리 | 실제 R02/R05 구현으로 교체할 때 CO 수정 불필요 |
| D7 HTTP 프레임워크 | 미정. FastAPI 후보로 R01에게 제안(§7) | 표준 `http.server` | multipart·검증·OpenAPI가 필요. 제품 `pyproject.toml`은 R01 소유 |

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
- 판정: confirmed / failed / unknown. 근거가 부족하면 unknown이며 성공으로 표시하지 않는다.

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

## 7. R01에게 확인·제안할 사항

| 항목 | 내용 | 영향 |
|---|---|---|
| HTTP 프레임워크 | FastAPI(MIT, 버전 고정) 채택 제안. 제품 `pyproject.toml`·`uv.lock`은 R01 소유 | S8 착수 조건 |
| DB | 우선 표준 `sqlite3`로 구현. 공통 DB가 정해지면 store 모듈만 교체 | 없음(국소) |
| STORE 인터페이스 | R05 remote가 호출할 admit/observe/fence 형식과 호출 경로(직접 import vs 포트) | R05와 공동 결정 |
| I2/I3/I4 시그니처 | 실제 provider 주입 형식(동기/비동기, 타임아웃) | R02·R05와 공동 |
| 연산 이름 | 계약 storage `S-FENCE`의 `fence`/`finalize`를 사용(CS-05 본문의 `terminal`은 같은 의미로 해석). 다르면 알려 달라고 확인 | 문서·코드 이름 |
| replay 사례 | unknown·응답 유실·경쟁 replay가 공통 fixture에 없음. app 쪽 시험에서 자체 대체 구현으로 만들 예정 | 공통 fixture 확장 여부 |
| 범위 | W10·W16, PREP 유지보수의 배정 여부 | 공수 |
| PoC 재사용 | TASK-043 PoC(`docs/members/R03/workspace/test/`)에서 상태·중복 방지 아이디어만 참고, 코드는 그대로 옮기지 않음 | 없음 |

## 8. 로컬 환경 확인

2026-11-25 실행 기록:

```sh
cd product/lesson-registration
uv sync --locked --python 3.12
uv run --locked --python 3.12 python dev.py doctor          # passed: source pins, ownership, synthetic image
uv run --locked --python 3.12 python dev.py test r03-app    # independent bootstrap replay passed
```

이 결과는 경로·fixture 연결만 확인한 것이며 기능 검증이 아니다. 변경 범위 검사: `python dev.py check-changes r03-app --base 65aed37`
