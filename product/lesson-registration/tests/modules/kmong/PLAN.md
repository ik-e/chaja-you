# r05-kmong PLAN · TASK-054 크몽 등록 adapter 및 독립 mock

- 담당: R05 (임다혁) · 브랜치: `r05/product-kmong` · 기준 커밋: `65aed37` (활성화 커밋)
- 독립 실행: `uv run --locked --python 3.12 python dev.py test r05-kmong`
- 고정 설계: `platform-profiles-v2.json`의 `kmong.service_listing.mock.v2`, `data-schema-v4.1.json`, `common-integration-v1.json` (WORKSPACE.json pins)
- 상태: 착수. 아래 "미정 사항"은 R01 회신 대기.

## 1. 목적

승인·수락된 범위(AcceptedScope)의 값만으로 크몽형 **합성** 등록 페이지에서 K1~K7을 수행하는 adapter를 만든다.
접수는 1회만 하고, 접수 응답과 분리된 독립 재조회로 receipt·값·이미지 digest를 대조한다.
실제 크몽 접속·계정·제출은 하지 않는다.

## 2. 범위

| 포함 | 제외 (다른 담당) |
|---|---|
| K1~K7 operation 정의(registry)와 binding digest | 원격 브라우저 실행·세션·lease (r05-remote) |
| 값 사전 검증 (profile value_schema + 조건부 지역) | STORE admission/fence 실제 구현 (r03-app) |
| 단계별 실행, 관측(Observation), 증거(EvidenceRecord) 생성 | job 상태 전이, 결과 판정 (CO·RESULT) |
| 독립 재조회(GoalObservation) | 실제 크몽 화면·계정 |
| 합성 크몽 mock 사이트와 fixture | 공통 계약·dev.py·공통 fixture 변경 |

## 3. 세부 결정과 근거

| ID | 결정 | 근거 / 대안 |
|---|---|---|
| K-D01 | adapter는 raw driver 대신 **좁은 페이지 인터페이스**(`ScopedPage`: goto·fill·attach·submit·view)만 받는다. 실제 구현은 r05-remote가 브라우저로, 시험은 stdlib HTML 폼 클라이언트로 제공 | RT-01 "no raw driver or credential to adapter". 대안(Playwright Page 직접 전달)은 계약 위반 |
| K-D02 | 이동 경로는 adapter registry의 고정 경로만 사용, origin은 runtime이 고정 | prohibitions "arbitrary origin/navigation" |
| K-D03 | operation_id = 대상(slot)·단계·action의 안정 해시, binding_digest = 단계가 묶는 값의 정규 JSON sha256 | RT-02 "stable logical operations", effect key가 버전·요청이 바뀌어도 같아야 함 |
| K-D04 | `perform`은 실행 전 operation이 registry와 일치하는지, binding_digest가 scope에서 다시 계산한 값과 같은지 확인. 다르면 실행하지 않고 오류 | RT-03 "never caller free arguments" |
| K-D05 | 시작 전 값 검증을 K1 이전에 수행. 오프라인이면 지역 필수, 온라인이면 지역 없어야 함 | 효과 발생 전에 실패해야 중복·잔여 draft 위험이 없음 |
| K-D06 | 이미지는 runtime의 자산 저장소에서 바이트를 받아 **digest를 재계산**한 뒤 첨부 | 첨부 자료 digest 일치(K3) |
| K-D07 | K6 응답 유실·시간 초과는 `unknown` + `EFFECT_UNKNOWN`. 응답만으로 성공 판정하지 않음 | profile K6 "응답 단독 성공 판정 금지" |
| K-D08 | K6 직전에 같은 slot의 기존 receipt를 읽기로 확인하고 있으면 `DUPLICATE_RISK`로 중단 | gateway admission과 별도의 adapter 방어선 |
| K-D09 | K7은 receipt ID가 아닌 **slot 기준 경로**로 조회 | K6 응답이 유실돼도 독립 확인 가능해야 함 |
| K-D10 | payload_digest는 재조회한 값을 정규화해 계산하고, scope 값의 digest와 비교 | RT-04 "actual normalized readback, no copy from input" |
| K-D11 | mock 사이트는 중복 접수를 스스로 막지 **않는다**(접수 횟수만 기록) | 중복 차단이 adapter·gateway에서 실제로 동작하는지 검증하기 위함 |
| K-D12 | mock 사이트·fixture는 표준 라이브러리만 사용 | 공통 환경 `dependencies = []`, 의존성 변경은 R01 승인 필요 |

## 4. 구현 순서

1. registry·값 검증 (`profile.py`, `operations.py`) + profile 정합성 시험 (고정 설계와 단계·binding·schema 일치)
2. 합성 mock 사이트 (`fixtures/platforms/kmong/mock_kmong.py`) + 시험용 HTML 폼 클라이언트
3. adapter `perform` K1~K6, `observe_goal` K7
4. fake gateway 주입 시험: 정상, 필수 오류, 응답 유실(unknown), 중복 차단, 변조 operation 거부
5. 산출 객체(Observation·GoalObservation·ExecutionReport·EvidenceRecord)를 고정 schema로 검증
6. 결과 기록 (§6), r05-remote 연동은 runtime 구현 후

## 5. 시험·완료 조건

| 수용 기준 | 시험 | 기대 |
|---|---|---|
| AC1 승인값·이미지·조건부 필드 일치, 등록 operation만 | `test_profile_contract`, `test_adapter` 정상·온라인·이미지 여러 장, 변조 operation | 저장값 = scope 값, 미등록/변조 operation 실행 안 됨 |
| AC2 제출 1회, 독립 receipt·digest 대조, 오류·unknown 중복 차단 | 응답 유실, 재시도, 기존 receipt, 서버 거부 | 접수 횟수 1, unknown 후 재제출 없음, 재조회로 해소 |
| AC3 자체 mock 및 gateway 주입, 실제 제출 금지 | 전체 시험이 127.0.0.1 mock만 사용, `LR_ENVIRONMENT≠mock` 거부 | 외부 접속 없음 |

완료 판정: 위 시험이 독립 실행 명령으로 통과하고 명령·commit·관측을 §6에 기록. bootstrap replay 통과는 제품 통과가 아니다.
제품 시험 AT-04, T5-13, DV-03, DV-04는 R01 통합 단계에서 판정.

## 6. 실행 기록

### 2026-11-25 · 1차 (fake gateway 주입, runtime 미연동)

- 기준: `65aed37` 위 작업 트리 (커밋 전). Python 3.12.3 (uv), 표준 라이브러리만 사용
- 명령과 결과
  - `uv run --locked --python 3.12 python dev.py test r05-kmong` → **28 tests OK** (bootstrap replay 1 + 제품 시험 27)
  - `uv run --locked --python 3.12 python dev.py doctor` → passed
  - `uv run --locked --python 3.12 python dev.py check-changes r05-kmong --base 65aed37` → 소유 경로 밖 변경 없음
  - `python dev.py smoke` → bootstrap smoke passed (제품 검증 아님)
- 입력: 공통 replay `I4` AcceptedScope(오프라인, 이미지 1장 `fixtures/shared/mock-image.png`) + 시험 내 변형(온라인·이미지 3장, 값 오류, 다른 계정, mock 장애 주입)

| 수용 기준 | 시험 | 기대 | 관측 | 판정 |
|---|---|---|---|---|
| AC1 | `NormalPath` 2건 | K1~K7 confirmed, 플랫폼 저장값 = 승인값, 이미지 digest·순서 일치, 온라인은 지역 없음 | 일치 | pass |
| AC1 | `ProfileMirror`·`ValueValidation`·`OperationRegistry` | 단계·binding·필드·goal·fixture 규칙이 pin과 같음, 스키마 수준 변형 20종에서 고정 schema와 adapter 판정 일치 | 일치 | pass |
| AC1 | `OnlyRegisteredOperations` | 변조·미등록 operation 4종은 adapter·gateway 모두 거부, mock 요청 0건; 값 오류는 효과 전 중단 | 거부, 요청 0 | pass |
| AC2 | `test_offline_single_image_end_to_end` | 접수 1회, goal은 independent_readback, payload·asset digest 일치 | submissions=1 | pass |
| AC2 | `SubmitOnceAndUnknown` 5건 | 응답 유실→unknown·fence·재제출 거부(INVALID_PHASE/DUPLICATE_RISK)·재조회로 confirmed; 5xx→unknown 후 재조회 absent; 명시 거부→absent; gateway 없이도 adapter가 2차 제출 차단; 이미 접수된 slot은 K1에서 중단 | 모두 기대대로, submissions ≤ 1 | pass |
| AC2 | `IndependentReadback` 3건 | 재조회 값·이미지 변조→not_reached(mismatch), 재조회 무응답→unknown, receipt 2건→multiple_receipts | 일치 | pass |
| AC3 | 전체 + `MockOnly` | 127.0.0.1 mock만, 상대 경로만, `LR_ENVIRONMENT≠mock` 거부 | 일치 | pass |

- 회귀 민감도 확인: adapter의 안전 장치 5개(제출 전 재조회, registry 정확 일치, 응답만으로 성공 금지, 재조회 대조, unknown 보존)를 하나씩 제거하면 각각 시험이 실패함을 확인
- 미완료: r05-remote 실제 브라우저 runtime과의 연동 시험, R03 STORE 실제 admission/fence 연결, 제품 시험 AT-04·T5-13·DV-03·DV-04 (통합 단계)

## 7. 미정 사항 (R01 확인 중)

- Q1 ScopedPage 인터페이스를 r05-remote runtime이 그대로 구현하는 것으로 확정할지 (R05 내부 결정, R01 공유)
- Q2 profile_ref.digest 계산 방식(정규화 규칙). 지금은 platform·object_kind·version·environment만 확인
- Q3 일정: runtime 우선 시 크몽 adapter 마감 조정 여부
