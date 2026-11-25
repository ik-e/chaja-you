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
| IB-02 | 표준 JSON Schema 엔진, 원본 schema 유지 | 자체 checker·새 타입 정본의 드리프트 방지 | 검증 도구는 고정 버전, 제품 dependency/lock 별도 |
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

마지막 명령은 표준 스키마 도구의 독립 검증용이다(직접 버전 고정, 전이 의존성 전체 lock 미고정). 아직 제품 pyproject/uv.lock 변경 없음. 명령은 POSIX runner 기준. Windows에서는 PYTHONPATH에 제품 root와 src를 설정하고 동일 명령 실행. 모든 replay 값·digest는 합성 예시이며 실제 인증, 원격 권한, 입출력 출처 또는 product proof가 아니다.

## 구현자가 반환할 공통 검토 사항

- R02: I2 실제 모델 호출의 동기 bridge/timeout 및 불확실성 표현; 인계.
- R03: registry/profile 조회, store accept/admit/observe/fence/finalize 원자 책임, HTTP launch/provider factory.
- R04: UI H1~H9 및 viewer mount, 숨고 adapter operation 등록.
- R05: runtime/adapter 분리, registry manifest/target/digest/lease, viewer transport와 크몽 작업량.
- R01: 공유 스택/락, 공통 물리 경계 확정 및 실제 provider 연결. 구체적 기술 선택은 각 담당자 근거 우선.

## 2026-11-25 공통 물리 방향 및 팀 공유

[승인](../../../docs/human/responses/HRESP-20261125-03_common-physical-direction.md) · [PD-01~08](../contracts/PHYSICAL-BINDING.json) · [잠정 WBS](../../../docs/artifacts/planning/lesson-registration-20261123/wbs-v0.6-candidate.json).

1. PD 방향 및 R05 수신/공수 기록을 현행 인덱스에 연결.
2. [독립 후보 환경](physical-env/pyproject.toml)과 [기술 probe](probe_physical.py)에서 Python 3.12 lock, ASGI HTTP/WS, thread bridge, SQLite 경쟁, schema, Chromium loopback/CDP 검증. 통과 및 owner 검토 전 제품 pyproject/lock 유지.
3. R03/R05 STORE, R04/R05 operation manifest, R03/R04/R05 viewer, R02/R03 I2, 각 owner factory/config 및 서버 canonical digest golden vector를 기존 계약 기준으로 합의. 독립 구현은 대기하지 않는다.
4. 승인 lock/기술 probe 반영 후 공통 테스트·CI 회귀, 기준선 SHA와 README 절차 공유. 팀원 PLAN/가용성 취합 후 WBS 확정.
5. 실제 provider 도착 순서로 연결; 합성/기술 probe와 22개 제품 시험 분리.

R05: 053·054 수신 및 7근무일 추정, 11/27 인터페이스 협의 후보, 12/3 통합 후보. runtime 계약 우선. 실제 PLAN/착수 여부 미확인.

첫 후보 CI: [45534634454](https://github.com/ik-e/chaja-you/actions/runs/45534634454)에서 Python 3.12 의존성 해석/설치 통과, Ubuntu 26.04의 Chromium 미지원으로 브라우저 설치 실패·기술 probe 미실행. 지원 runner Ubuntu 24.04를 지정하여 재검증한다. 이전 로컬 관측 서술은 재현 근거 미확보로 검증에 사용하지 않는다.

담당자 공통 세부 합의는 [INTERFACE-REVIEW](../contracts/INTERFACE-REVIEW.md)를 사용한다. 서버 canonical byte primitive와 golden vectors/negative test 추가; 실제 digest 대상 선택·slot·profile readback과 팀원 동의는 별도. 독립 검증 명령: `uv run --locked --python 3.12 python dev.py test common`.
