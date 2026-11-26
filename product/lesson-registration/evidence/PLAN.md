# TASK-048 · R01 공통 설계·통합 작업 계획 및 검토

기준: [현재 TASK](../../../docs/artifacts/tasks/TASK-048.json), [Phase](../../../docs/human/phase-intents/PHASE-20261125-01.md), [논리 계약](../../../docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json), [현재 배정](../WORKSPACE.json). 2026-11-25. R01만 공통 경계·통합; 팀원 구현/실서비스 실행 금지.

## 순서와 완료 조건

| 단계 | 산출물 | 상태/판정 기준 |
| --- | --- | --- |
| 1. 정합성 | 전용 설계 JSON 라우팅, 채택/고정 원본 일치, 기존 문서 재생성 | 재생성/검증 CI 통과; 과거 원본 보존 |
| 2. 코드 경계 | [binding](../contracts/IMPLEMENTATION-BINDING.json), [Python Protocol](../contracts/interfaces.py), [viewer](../contracts/viewer.d.ts) | R01 방향 승인; 초기 공유 계약, 담당자 세부 확인 |
| 3. 공통 검증 | [표준 스키마 검사](../contracts/validation.py), [시험](../tests/contract/standard_schema/test_contracts.py) | Python 3.12 CI 10/10·72 payload 통과; replay/결함 주입만 |
| 4. 조립 구조 | [wiring](../src/lesson_registration/composition/wiring.py), [replay provider](../stubs/replay_ports.py) | 기본 명시 주입 및 synthetic wiring 시험 통과; 실제 연결은 팀원 결과 뒤 |
| 5. 실행 환경 | 공통 dependency lock, provider/launch config, 격리·오류 처리 | 선택 근거와 공수 확인 후 R01 결정 |
| 6. 점진 통합 | R03 app + I2/I3/I4 fake → 실제 provider → 크몽 → 숨고 | 같은 후보 버전의 실제 관측; 22개 수용 시험은 별도 |
| 7. 수용 | 공통 V1 gate의 전체 22개 ID | T5-08 실제 모델 포함. 실행 전 not_run, 실패/누락 구분 |

## 승인된 방향과 담당자 추가 검토

[사용자 승인](../../../docs/human/responses/HRESP-20261125-02_common-implementation-binding.md) · [검증 실행](https://github.com/ik-e/chaja-you/actions/runs/45527624382)

| ID | 권장 | 대안/판단 근거 | 남은 검토 |
| --- | --- | --- | --- |
| IB-01 | Python 3.12 동기 호출 Protocol, async/IPC bridge 내부 위임 | 기존 bootstrap 및 5개 포트; 서비스마다 RPC 강제하지 않음 | R02/R03/R05 호출 서명/worker 실행 방식 |
| IB-02 | 표준 JSON Schema 엔진, 원본 schema 유지 | 자체 checker·새 타입 정본의 드리프트 방지 | 제품 lock 반영 완료; 공통 서버 SchemaCatalog 재사용 기본, 실제 provider 연동 확인 |
| IB-03 | CO/Gateway store 권한 분리, Adapter에는 bound gateway | raw driver/store 노출은 계약 위반 위험 | R03/R05 트랜잭션/lease/operation manifest/target/digest |
| IB-04 | framework-neutral viewer contract | UI의 runtime 기술 결합 최소화 | R04/R05 transport·grant TTL/origin·owner 결합 |
| IB-05 | composition provider 명시 주입 | 완전한 가짜 app 작성하지 않음 | 실제 provider factory/공통 실행 명령 |

결정별 근거·선행 CS·대안·재검토 조건은 [구조화 결정](../contracts/IMPLEMENTATION-BINDING.json)에 기록. 초기 공통 인터페이스를 전달하고 정확한 통합 커밋과 채택 상태를 명시한다. 국소 구현은 담당자 자율. 기존 TASK, 논리 정본, 제품 범위 변경 없음.

## 실행

```sh
cd product/lesson-registration
uv run --locked --python 3.12 python dev.py doctor
uv run --locked --python 3.12 python dev.py test all
PYTHONPATH=.:src uv run --no-project --python 3.12 --with jsonschema==4.25.1 python -m unittest discover -s tests/contract/standard_schema -v
```

마지막 명령은 표준 스키마 도구의 독립 검증용이다(직접 버전 고정, 전이 의존성 전체 lock 미고정). 초기 공통 제품 pyproject/uv.lock은 후속 물리 CI를 근거로 반영(아래 갱신 기록). 명령은 POSIX runner 기준. Windows에서는 PYTHONPATH에 제품 root와 src를 설정하고 동일 명령 실행. 모든 replay 값·digest는 합성 예시이며 실제 인증, 원격 권한, 입출력 출처 또는 product proof가 아니다.

## 구현자가 반환할 공통 검토 사항

- R02: I2 실제 모델 호출의 동기 bridge/timeout 및 불확실성 표현; 인계.
- R03: registry/profile 조회, store accept/admit/observe/fence/finalize 원자 책임, HTTP launch/provider factory.
- R04: UI H1~H9 및 viewer mount, 숨고 adapter operation 등록.
- R05: runtime/adapter 분리, registry manifest/target/digest/lease, viewer transport와 크몽 작업량.
- R01: 공유 스택/락, 공통 물리 경계 확정 및 실제 provider 연결. 구체적 기술 선택은 각 담당자 근거 우선.

## 2026-11-25 공통 물리 방향 및 팀 공유

[승인](../../../docs/human/responses/HRESP-20261125-03_common-physical-direction.md) · [PD-01~08](../contracts/PHYSICAL-BINDING.json) · [잠정 WBS](../../../docs/artifacts/planning/lesson-registration-20261123/wbs-v0.6-candidate.json).

1. PD 방향 및 R05 수신/공수 기록을 현행 인덱스에 연결.
2. [독립 후보 환경](physical-env/pyproject.toml)과 [기술 probe](probe_physical.py)에서 Python 3.12 lock, ASGI HTTP/WS, thread bridge, SQLite 경쟁, schema, Chromium loopback/CDP 검증. 통과한 후보의 정확한 lock을 제품 경로에 반영하고 별도 회귀 검증.
3. R03/R05 STORE, R04/R05 operation manifest, R03/R04/R05 viewer, R02/R03 I2, 각 owner factory/config 및 서버 canonical digest golden vector를 기존 계약 기준으로 합의. 독립 구현은 대기하지 않는다.
4. 승인 lock/기술 probe 반영 후 공통 테스트·CI 회귀, 기준선 SHA와 README 절차 공유. 팀원 PLAN/가용성 취합 후 WBS 확정.
5. 실제 provider 도착 순서로 연결; 합성/기술 probe와 22개 제품 시험 분리.

R05: 053·054 수신 및 7근무일 추정, 11/27 인터페이스 협의 후보, 12/3 통합 후보. runtime 계약 우선. 실제 PLAN/착수 여부 미확인.

첫 후보 CI: [45534634454](https://github.com/ik-e/chaja-you/actions/runs/45534634454)에서 Python 3.12 의존성 해석/설치 통과, Ubuntu 26.04의 Chromium 미지원으로 브라우저 설치 실패·기술 probe 미실행. 지원 runner Ubuntu 24.04를 지정하여 재검증한다. 이전 로컬 관측 서술은 재현 근거 미확보로 검증에 사용하지 않는다.

담당자 공통 세부 합의는 [INTERFACE-REVIEW](../contracts/INTERFACE-REVIEW.md)를 사용한다. 서버 canonical byte primitive와 golden vectors/negative test 추가; 실제 digest 대상 선택·slot·profile readback과 팀원 동의는 별도. 독립 검증 명령: `uv run --locked --python 3.12 python dev.py test common`.

후속 검증: [물리 CI](https://github.com/ik-e/chaja-you/actions/runs/45534844447) 성공 (Python 3.12.3, 26 packages, Chromium build v1200, 4/4 기술 probe). [근거](physical-ci-20261125.json). 성공 로그의 정확한 lock과 동일 dependency spec을 제품 pyproject.toml/uv.lock에 반영. Linux 기술 검증과 owner 환경/실제 제품 안전 검증은 별도. 이전 후보 환경은 이력이며 제품 실행은 제품 lock 사용. 제품 lock 표준 스키마 검사는 `uv run --locked --python 3.12 python -m unittest discover -s tests/contract/standard_schema -v` (제품 root와 src를 PYTHONPATH에 추가). 실제 제품 22개 미실행.

R03 PLAN 확인: [고정 snapshot](https://github.com/ik-e/chaja-you/blob/e29fb6939f1ec49d9b4a89fbe2874bb6331498cf/product/lesson-registration/tests/modules/app/PLAN.md), 11인일 추정/12월 8일 일정 위험. [공통 접점 및 기존 계약 정합성 피드백](../contracts/INTERFACE-REVIEW.md#r03-plan-검토-2026-11-25), WBS 후보에 반영. R02/R04 PLAN 및 R05 실제 PLAN은 확인되지 않았으므로 일정 확정 금지.

R03 후속: [R01 결정](../../../docs/human/responses/HRESP-20261125-04_r03-app-followup.md) · [진행 근거](r03-progress-20261125.json) · [공동 반환 기준](../contracts/INTERFACE-REVIEW.md#r03-진행-보고-후속-2026-11-25). S8 착수 가능, 회귀 미확인. R03/R05 digest·operation·STORE/lease 예제 합의 → R01 공통 fixture 계산값 및 실패 벡터 갱신 → 통합 회귀. Viewer/I2/factory는 담당자 반환 후 결정. 잔여 공수·전체 PLAN/가용성 확인 후 WBS 확정, 추가 TASK 자동 배정 없음.

## D01~D06 세부 방향 및 보안 후보

[승인](../../../docs/human/responses/HRESP-20261125-05_common-detail-direction.md) · [후보](../contracts/DETAIL-CANDIDATE.json) · [인증 세션 보안](../contracts/SESSION-SECURITY.md). 기존 R03/R05 협의 대기 대신 R01이 reference와 실패 시험을 먼저 제공. 명령: `uv run --locked --python 3.12 python -m unittest discover -s tests/contract -p test_detail_candidate.py -v` (PYTHONPATH=.:src), 제품 lock의 all-groups 환경에서 `python evidence/probe_physical.py`. 실행 결과는 정확한 commit CI로 확인; 이전 채팅 13/13은 재현 근거 부재로 검증값 사용 금지. 기존 replay sentinel 유지, 계산값은 후보 test에서 실제 생성. 독립 모델·loopback probe와 실제 제품 22개/운영 보안은 분리. 담당자 차이 확인 후 현행 interfaces.py·manifest/slot/fixture 변경 여부를 확정.

후속: [공동 개발 기준](../contracts/CURRENT-BASELINE.md) 및 [R01 전달](../../../docs/human/responses/HRESP-20261125-08_common-baseline-release.md). 81ade0f 후보의 4개 CI 통과; R04 추가 구현이 반영된 최신 main과 함께 다시 검증. 실제 owner conformance 및 22개 gate 미확인. [OpenAI 실험 환경](OPENAI-EXPERIMENT.md)은 기관 Member 접근/예산/정책 확인 전 실제 호출 금지.

## 11/25 팀 후속 및 점진 통합 준비

[팀 고정 검토](team-checkpoint-20261125.json) · [제품 gate 실행 체계](PRODUCT-GATE.md). R02 실험 설계/수행 자율, R01 검토만; 실제 모델 오류 및 후속 비용 계획 확인. R03 합성 API 실행기 main 반영, R04 실제 UI/숨고 결과 검토 및 WBS 갱신, R05 고정 CI 15/32 통과. `evidence/product_gate.py`는 22 gate pin과 결과를 구분하고 합성 HTTP/CLI preflight를 수행한다. 완전한 gate case는 아직 0개. 관련 provider/보안/상태가 실제 연결된 이후 검증 case를 등록. 기본 CI에 실제 모델/플랫폼 호출 없음. R02/R04 잔여 공수, R05 갱신 공수·가용성 확인 전 일정 확정 금지.

## 11/25 최신 통합 인수

[팀 최신 체크포인트](team-integration-checkpoint-20261125.json) · [통합 인수 기준](INTEGRATION-INTAKE.md) · [22개 준비 목록](product-gate-readiness-20261125.json). Runtime 30/30·크몽 37/37 동일 고정 조합 독립 CI 통과(skip 0), 전체 제품 0/22. R03 실제 조립, R01 독립 검증·공통 변경 검토·수용 시험 등록 및 판정. R02 실제 실험 설계/비용 검토, R04 실제 UI/숨고 동작 보완. 모든 잔여 공수/가용성 갱신과 공식 제출 확인은 별도.
