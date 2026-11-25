# V0.7 설계 검증 보강 및 독립 검토

- 검토 기준: `5a01ec3845415200e0383546e18bfb8a6a78a2e9` (V0.1–V0.6 설계 원본 변경 없음).
- 실행 증거: [validation-constraints-v0.7.json](validation-constraints-v0.7.json). GitHub에서 고정 SHA의 8개 원본 JSON을 읽어 저장한 동일 순수 JavaScript 검증 함수를 직접 실행했다. 원본 blob SHA를 기록했다.
- 재실행: 저장소 루트에서 `node docs/artifacts/design/lesson-registration-20261124/run-constraints-v0.7.mjs` (Node, 외부 의존성 없음).
- 제품 실행·실제 플랫폼 인증·등록 없음. 기존 TASK/단계 허용/설계 채택/일정 변경 없음.

## 자동 검증

| 검증 | 결과 | 보장 범위 |
|---|---|---|
| STATE-01~04 | 4/4 | 실제 job 상태·전이·이벤트 유효성, 그래프상 도달/종료 경로, reserved 격리, 실행 가드 13개, unknown/stopping/목표 완료의 명시 가드 |
| EFFECT-01 | 1/1 | 개별 attempt 전이 및 증거 이벤트, 같은 시도 재-admission 금지 |
| WIRE-01~03 | 3/3 | V0.3 계승+V0.5 보정 스키마 참조, 29개 effective routes/12개 ports의 타입 이름, UI 내부 route 노출 차단 |
| ARCH-01 | 1/1 | 선언된 컴포넌트 의존성 DAG |
| TRACE-01 | 1/1 | 수용시험 원본 requirement_refs 보존, 시험 ID 중복 금지 |
| 결함 주입 | 21/21 | 의도적 결함 20건의 hard check 탐지 및 호출/의존 관계 불일치 1건 탐지. 정상 기준선에서 해당 검사가 통과한 경우에만 결함 탐지로 계산 |

Hard check 10/10과 별개로 ARCH-R01 호출/의존성 불일치 11건이 발견되었다. 11건은 서로 다른 계약의 불일치 사례이며 11개의 독립 결함이라는 의미가 아니다. `depends_on`이 호출 의존성인지 정적 모듈 의존성인지 확정되지 않아 자동으로 순환 또는 결함이라 단정하거나 간선을 추가하지 않는다.

| 호출 관계 | 계약 | 검토 이유 |
|---|---|---|
| C4-02 → C4-09 | HTTP-11/12/17/25 | 결과/재확인 제공자로 가는 의존 경로 부재 |
| C4-05 → C4-07 | HTTP-19, PORT5-06/09 | 역방향 C4-07 → C4-05 이미 존재. 무조건 정적 간선을 추가하면 순환 |
| C4-05 → C4-06 | PORT5-03/10 | 세션/재연결·runtime 호출 경계 누락 |
| C4-05 → C4-08 | PORT5-04 | adapter 계획 생성 호출 경계 누락 |
| C4-09 → C4-07 | PORT5-08 | read-only 재확인 경계 누락 |

추가 미검증: HTTP-02 multipart와 HTTP-17 after_revision은 typed input 미정; job의 11개 추가 조건 이름은 선언되어 있으나 truth/update 의미가 형식화되지 않음. 그래프 도달성은 조건을 무시한 구조상 가능성이지 실행 가능성, 교착 부재, 종료 보장이 아니다. Boolean conjunction의 누락 반례도 조건 이름을 독립 변수로 놓은 제한된 검증이다.

## 독립 AI 설계 검토 (자동 결과와 구분)

검토 자료: [V0.3 core](core-contract-v0.3.json), [V0.4 구현](implementation-v0.4.json), [V0.4 physical](physical-v0.4.json), [V0.5 계약](contract-v0.5.json), [V0.5 WBS](wbs-v0.5.json), [V0.6 trace](trace-index-v0.6.json), V0.3 data API, V0.4 direction, 상위 기획 plan.json. 아래는 설계 내용에 대한 별도 근거 검토이지 제품 실행 관측이 아니다.

| ID | 우선순위·판정 | 근거/문제 및 보완 |
|---|---|---|
| IR-01 | P0 구조 정합성 검토 필요 | C4-02 API의 depends_on에 C4-09 없음에도 HTTP-11/12/17/25를 C4-09에 매핑. C4-05↔C4-07 호출/의존 방향도 불명확. 자동 ARCH-R01과 일치. 런타임 호출, 정적 port 의존, 소유 책임을 분리해 공통 경계를 동결(W01). |
| IR-02 | P0 명시 재개 조건의 형식화 누락 | V3-J03의 from은 planned/needs_action/blocked, meaning은 '재개 시 명시 요청 추가 확인'이나 conditions에는 명시 재개 이벤트/조건 없음. V3-R03/R06 및 R5-04, Resume5Request.explicit_resume과 의미상 정책은 존재. 신규 작업과 복구 경로를 구별하는 상태 변수/guard를 정의하고 경로 검증 필요. 현재 검증기는 통과, 실제 우회 가능성은 구현/조건 의미 없이 확정 불가. |
| IR-03 | P0 공통 wire 계약 미동결 | HTTP-02 multipart/HTTP-17 after_revision 입력은 typed 미정(자동과 일치). V0.5 Plan.digest는 full scope를 요구하지만 canonical serialization, multipart/key/error/version 규격 및 fixture 미동결(GAP-03). W01에서 합의 후 provider conformance를 실행해야 함. |
| IR-04 | P0 안전 경계의 구현 실증 필요 | R5-03 및 ViewerInputEnvelope.payload/json, BrowserCommand.arguments/json은 정책을 명시하지만 사람이 원격 화면을 직접 조작하는 동안 등록/공개 등 외부 효과의 범위를 실제로 강제할 수 있는지는 미확인. R05 합성 PoC는 원격 구조의 근거이지 실제 인증/브라우저 격리 및 강제 수단 증명 아님. W04/W11에서 승인·제어권·중단 race 및 우회 경로 실험; 실환경 gate 유지. |
| IR-05 | P1 MVP 수용 gate 연결 보완 | R5-09는 AI T5-08, 크몽, 숨고 및 기본 안전 포함; W09.done에는 AI/재접속/기본 가드가 있으나 trace의 W09 연결은 T5-06/09/13, V3-T07, AT-04/05 6건뿐. W07 등 선행 시험 결과 재사용 가능하나 W18 수정 이후 유효한 결과인지 판정하는 명시 gate/required test list 필요. 기존 coverage는 연결 존재만 확인. |
| IR-06 | P1 검증 실효성 보완 | StepSpec.before_spec/after_spec/evidence_spec 및 BrowserCommand.arguments 타입은 ID/json으로 선언. 규칙/동작별 구체 조건과 argument schema/정답 fixture가 동결돼야 구체 값/승인 범위/사후 효과 판정 가능. T5-08도 원문 fixture·기대 추출값·누락 질문·금지 추론 및 모델 실행 판정 기준 필요. W01/W19에서 정의. |
| IR-07 | 외부 의존/이미 관리 중 | 기획 가치 실측, 실서비스 허용, 실제 숨고 대상 객체, 기술 공수/운영 보안은 GAP-01~05와 W13/W15/W17에 이미 명시. mock 설계/실증 통과와 실제 서비스 목적 달성 구분 유지. 새 결함으로 중복 등록하지 않음. |
| IR-08 | 일정 위험/이미 부분 완화 | W19 최종 AI 인계와 W03 실제 AI 연결은 모두 12/3 종료. W07은 두 작업을 의존하고 IC05가 같은 날 인계를 명시해 논리 위반은 아님. IC02~04 stub 계약, IC05 시간 순서/실패 시 범위 재판단을 명시해 병목 완화. |

## 비교 및 결론

- 자동과 독립 검토 공통: 아키텍처 호출/의존 관계(11 계약, 5 관계) 및 계승된 typed 입력 2개 미정.
- 독립 검토 추가: 복구 경로의 명시 재개 조건, 통합 MVP gate의 필수 시험/변경 후 유효성, argument/fixture 및 기술 강제 경계, 일정 인계 리스크.
- 자동 검증은 실제 원본과 직접 연결된 판정 가능한 속성 및 오류 주입에 집중한다. 현재의 자연어 조건을 그대로 두고 전체 상태 안전성이나 설계 완전성을 증명했다고 기록하지 않는다.
- V0.7은 보완한 설계 검증기이지 설계 원본 수정 또는 제품 승인 아님. W01 착수/공통 계약 동결 전에 IR-01~03에 대한 보완 또는 명시적 보류 판단이 필요하다. 기존 GAP과 중복된 항목은 새 TASK 배정하지 않는다.
