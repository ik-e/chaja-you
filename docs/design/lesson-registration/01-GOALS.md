# 목표·요구사항·상위 결정

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## direction-v0.4.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/direction-v0.4.json) · blob `54beb7c357e580b087442bb8f00e40ab2a3567af`

### id

- LESSON-DIRECTION-20261124

### version

- 0.4-direction

### date

- 2026-11-24

### authority

- R01

### status

- direction&#95;decided&#95;detail&#95;pending

### source

- **kind** (`kind`): R01&#95;direct&#95;instruction
- **quote** (`quote`): 원격 브라우저 방식을 채택하되 원격 브라우저 세부 기술은 나중에 구현자가 결정할 수 있도록 하는 게 좋을 것 같고 mvp의 범위는 크몽 우선 그리고 숨고 확장, 핵심 기능은 최초 등록이 정상적으로 동작되는 것까지 ↵ 1/4까지는 최종 목표는 필요한 정보와 인증이 되면 원하는 url에 등록이 될 수 있는 것까지
- **interpretation&#95;boundary** (`interpretation_boundary`): 방향·우선순위·목표 확정. 세부 수용 시험, 지원 한계, 물리 설계와 일정/WBS는 다음 설계에서 제안한다. 실제 서비스 이용 허용을 부여하는 지시가 아님.
- **clarifications** (`clarifications`)
  - **[0] **
    - **kind** (`kind`): R01&#95;direct&#95;instruction
    - **quote** (`quote`): 원하는 url 등록이 결국 등록 가능한 플랫폼에 등록하도록 하는 거야
    - **meaning** (`meaning`): URL은 사용자가 원하는 등록 대상 플랫폼 또는 등록 경로를 전달하는 입력이다. 등록 가능한 플랫폼의 최초 등록 업무 수행이 목표이며, 임의 URL에 대한 범용 자동 적응을 필수 조건으로 해석하지 않는다.

### baseline

- **design&#95;commit** (`design_commit`): 07a40412ace0e434ce919ab979e8af8b77833435
- **main&#95;commit** (`main_commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
- **phase&#95;ref** (`phase_ref`): docs/human/phase-intents/PHASE-20261124-02.md
- **previous&#95;decisions** (`previous_decisions`): review-v0.3.json
- **precedence** (`precedence`): 현재 결정은 V0.3의 해당 상위 방향·범위 상태를 갱신한다. 기존 V0.3 논리 계약 및 현재 단계 mock-only 제한은 보존. 이전 설계 및 실행 기록은 수정하지 않는다.

### evidence

#### EV-R05-REMOTE-20261124

- **ID** (`id`): EV-R05-REMOTE-20261124
- **commit** (`commit`): fc59a4b8f5e8adea3c4dc3b2264df2907131c018
- **path** (`path`): docs/members/R05/workspace/remote-browser-poc/README.md
- **result&#95;path** (`result_path`): docs/members/R05/workspace/remote-browser-poc/evidence/results.json
- **test&#95;log&#95;path** (`test_log_path`): docs/members/R05/workspace/remote-browser-poc/evidence/pytest&#95;output.txt
- **observed** (`observed`): R05 보고: 합성 웹 뷰어 원격 로그인·동일 인증 세션 실행·뷰어 종료 후 서버 작업·텍스트/이미지/저장·제어권 반환·논리적 세션 격리/폐기. pytest 10개, 3회 연속 통과 보고. R01 측 독립 재실행 아님.
- **limits** (`limits`): 로컬 합성 환경, Chrome 프로세스 공유 BrowserContext, 실제 플랫폼·Docker/운영 격리·HTTPS/WSS 외부 접속·부하·IME 미검증.
- **use** (`use`): 원격 브라우저 구조의 채택 근거 및 구현 재사용 후보. CDP·Playwright·FastAPI 등 세부 기술 채택으로 해석 금지.

### decisions

#### DIR-01

- **ID** (`id`): DIR-01
- **updates** (`updates`): DEC-03
- **state** (`state`): decided
- **title** (`title`): 목표 실행 구조
- **결정** (`decision`): 서버 원격 브라우저. 사용자가 일반 웹 브라우저에서 원격 화면을 보고 직접 인증하고, 승인된 등록 작업을 서버에서 동일 인증 맥락으로 수행한다. 사용자 웹 접속 종료 후에도 작업 수명주기 독립.
- **이유** (`reason`): 설치 부담을 줄이고 인증 이후 무인 실행을 제공하는 사용자 가치. R05 합성 PoC로 핵심 가설의 실행 근거 확보.

#### DIR-02

- **ID** (`id`): DIR-02
- **updates** (`updates`): DEC-07 · DEC-08 · DEC-10 · DEC-12 · DEC-16
- **state** (`state`): delegated&#95;with&#95;constraints
- **title** (`title`): 원격 브라우저 세부 구현
- **결정** (`decision`): 원격 화면 전송·브라우저 제어 엔진·브라우저 종류·격리/배포의 구체 기술은 구현자가 요구와 공통 계약을 충족하는 범위에서 선정한다. R05 방식 재사용 우선 검토, CDP/Playwright/noVNC 등 강제하지 않음.
- **guardrails** (`guardrails`): 사용자 직접 인증, 동일 인증 맥락, 사용자/자동화 제어권 상호배타, 뷰어 종료 후 작업 지속, 승인·계정·대상·권한 결합, 중복/unknown 차단, 인증정보 비저장·최소 처리, 사용자별 격리·폐기, 재현 가능한 증거 · 기술 선택 근거·대안·변경 조건·공통 인터페이스 영향 기록. 공통 의존성/인터페이스 변경은 합의 필요. · 위임은 구현 기술 선택이지 현재 권한 제한·보안 조건을 완화하는 권한 아님. 최종 운영 격리·보존 정책 및 검증은 별도.

#### DIR-03

- **ID** (`id`): DIR-03
- **updates** (`updates`): DEC-01 · DEC-02
- **state** (`state`): scope&#95;decided&#95;target&#95;detail&#95;pending
- **title** (`title`): 2026-12-08 MVP
- **결정** (`decision`): 크몽 우선 구현, 숨고 확장. 핵심 업무는 최초 등록 정상 동작까지. 최초 등록의 원본/필수 정보 준비 → 플랫폼 변환 → 검토 → 직접 인증/계정·대상 확인 → 실행 승인 → 입력·필요한 첨부·저장/제출 → 결과 확인을 수직 연결.
- **이유** (`reason`): 첫 플랫폼 완결 후 다른 등록 객체로 확장하여 공통 구조 검증. 숨고 확장의 구체 완료 객체 및 일정 배치는 추가 명세.
- **milestone** (`milestone`): 2026-12-08

#### DIR-04

- **ID** (`id`): DIR-04
- **updates** (`updates`): DEC-01 · DEC-02 · DEC-06
- **state** (`state`): goal&#95;decided&#95;acceptance&#95;pending
- **title** (`title`): 2027-01-04 최종 목표
- **결정** (`decision`): 사용자가 원하는 URL을 제시하면 해당 URL이 가리키는 등록 가능한 플랫폼에서, 필요한 정보·자료 및 사용자 인증이 갖춰진 경우 최초 등록 업무를 수행하고 결과를 확인할 수 있는 서비스.
- **이유** (`reason`): 사용자가 등록하고자 하는 플랫폼을 URL로 지정하여 최초 등록 업무를 맡길 수 있도록 MVP의 공통 계약과 등록 경로를 확장한다.
- **milestone** (`milestone`): 2027-01-04
- **interpretation** (`interpretation`): URL은 등록 대상 플랫폼 또는 등록 경로의 지정 수단이다. URL 자체가 새로운 범용 웹 에이전트 구축 요구는 아니다. 등록 가능 여부(지원 경로, 필요한 정보, 인증, 사용자 승인, 운영사 허용, 실행/완료 증거)를 확인한다. 플랫폼별 어댑터, 공통 실행기, 동적 분석 등은 구현 선택지이며, 미지원 신규 사이트의 무설정 자동 적응이나 임의 인터넷 URL의 성공은 필수 수용 조건이 아니다. 최종 지원 플랫폼 목록과 확장 방식은 이후 설계에서 구체화한다.

### proposed_acceptance

- **상태** (`status`): draft&#95;not&#95;approved
- **mvp** (`mvp`)
  - **[0] MVP-A01**
    - **ID** (`id`): MVP-A01
    - **target** (`target`): kmong.service&#95;listing
    - **required** (`required`): 크몽형 합성 최초 상품 1건의 전 구간을 제품 UI에서 연결; 승인 데이터/이미지·대상 일치, 모의 접수 결과 독립 조회. 실제 서비스의 목표 완료는 심사 접수 확인이며 공개와 별개. 허용 전 실제 실행 금지.
  - **[1] MVP-A02**
    - **ID** (`id`): MVP-A02
    - **target** (`target`): soomgo
    - **required** (`required`): 크몽 경로 완성 후 숨고의 확인된 등록 객체로 동일 공통 계약을 확장. 서비스 설정 저장 후보, 신규 가입·프로필·공개·견적 분리. 실제 완료 객체와 수용 범위는 R04 근거 및 R01 결정.
  - **[2] MVP-A03**
    - **ID** (`id`): MVP-A03
    - **target** (`target`): common
    - **required** (`required`): 사용자 직접 합성 인증/동일 세션 인계, 미승인/계정 불일치/필수 누락 차단, 실패와 미확인 구분·중복 방지. 최초 등록 정상 경로가 핵심이며 예외 최소 안전 조건은 유지.
- **final** (`final`)
  - **[0] FINAL-A01**
    - **ID** (`id`): FINAL-A01
    - **required** (`required`): 사용자 지정 URL + 등록 목적/필요 정보·자료 → 대상 플랫폼 및 등록 가능 경로 확인 → 필요한 정보 충족 → 직접 인증 및 실행 승인 → 최초 등록 실행 → 결과 증거. URL은 플랫폼 홈페이지 또는 지원되는 등록 경로일 수 있으며, 정확한 지원 형태는 상세 설계에서 정의.
  - **[1] FINAL-A02**
    - **ID** (`id`): FINAL-A02
    - **required** (`required`): MVP의 크몽 우선·숨고 확장을 기반으로 등록 가능한 플랫폼의 지원 범위를 확장하고, 사용자 URL로 해당 등록 경로를 선택·실행한다. 최종 지원 플랫폼 목록, 평가 대상 수, 수용 기준은 상세 설계에서 제안. 미지원 신규 사이트 자동 분석/무설정 등록 시험을 필수화하지 않음.
  - **[2] FINAL-A03**
    - **ID** (`id`): FINAL-A03
    - **required** (`required`): 미지원 경로, 정보 누락, 인증 불가, 권한 미확인, 결과 미확인 등은 질문·차단·상태 안내로 구분. URL 검증 및 허용된 접근 경계 적용. 실제 등록은 운영사 허용·사용자 동의·보안·단계 승인 충족 시에만.

### next_design

- URL을 대상 플랫폼/등록 경로로 연결하고, 등록 가능 여부 및 필요 정보·인증·권한을 판정하는 계약과 플랫폼 확장 방식 정의 (범용 미지원 URL 자동 적응 강제 아님)
- MVP와 최종 목표의 수용 조건·포함/제외 범위·평가 시나리오 구체화
- V0.3 계약을 기준으로 공통 물리 API·DB·UI·모듈 인터페이스 및 원격 브라우저 기술 중립 포트 설계
- R03~R05 코드/조사 재사용 범위 및 통합 순서 결정, 구현자별 기술 선택 책임
- 12/8 MVP와 1/4 최종 마일스톤 역산 WBS·의존성·담당·완료 조건 수립

### unchanged

- 현재 PHASE mock-only, TASK-043~045, T1~T6 공통 계약, 실제 플랫폼 접근/제출 승인 없음
- main 및 팀원 브랜치 변경 없음. 기존 V0.1~V0.3 원본 보존.
- 원격 브라우저 상세 기술·전체 제품 기술 스택, 실제 운영 권한·보안, 실제 성능/가치 미확정. 신규 TASK 할당 없음.

## top-design-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/top-design-v1.json) · blob `1ed54afd5b541fa3a9d4030267ba65c54729ff2b`

### id

- LR-TOP-20261124

### status

- approved&#95;top&#95;level&#95;only

### authority

- **actor** (`actor`): R01
- **date** (`date`): 2026-11-24
- **quote** (`quote`): 큰 문제 없어보여 이대로 설계를 구체화하면 될 것 같은데
- **scope** (`scope`): 직전 제시한 최상위 목적·원본/계획/작업 분리·다섯 책임·사용자 흐름 및 상태/불변식. 하위 논리 설계 검토, 실제 구현·운영 승인 아님.

### sources

- **[0] **
  - **path** (`path`): docs/artifacts/planning/lesson-registration-20261123/proposal-v1.1.json
  - **blob** (`blob`): a81b521898cc516cd88b8b53ec39dbf008b164eb
  - **refs** (`refs`): P1 · P2 · P3 · F1 · F2 · F3 · FR-01~06 · sections 8,9,12
- **[1] **
  - **path** (`path`): docs/artifacts/design/lesson-registration-20261124/direction-v0.4.json
  - **blob** (`blob`): 54beb7c357e580b087442bb8f00e40ab2a3567af
  - **refs** (`refs`): DIR-01 · DIR-02 · DIR-03 · DIR-04
- **[2] **
  - **path** (`path`): docs/human/phase-intents/PHASE-20261124-02.md
  - **blob** (`blob`): 6b790bf85ed6295cb096e56560ddc86d34031087
  - **refs** (`refs`): mock-only · TASK-043~045 unchanged

### goal

- 확인된 원본과 사용자 인증/승인을 기반으로 등록 가능한 플랫폼에 최초 등록을 수행하고 근거와 다음 행동을 제공하여 강사의 직접 재가공·조작·재확인 부담을 줄인다. 가치 실측 전.

### objects

- 재사용 가능한 사용자 확인 원본
- 플랫폼별 등록 계획(계정·대상·범위·버전 결합)
- 독립 등록 작업(시도·효과·결과 기록)

### roles

- CO · 등록 업무 조정 · 목표·승인·진행 상태
- PREP · 등록 준비 · 사실·변환·검증
- KNOW · 플랫폼 지식 · 지원·규칙·절차·완료 조건
- EXEC · 등록 실행 · 원격 인증·제어권·외부 조작
- RESULT · 결과 확인 · 관측·판정·복구

### shared

- 공통 영속 기록; 논리 책임 구분이며 물리 배치 강제 아님.

### flow

- 등록 대상/원본 지정(순서 자유)
- 등록 정보 준비
- 누락·충돌 확인
- 사용자 직접 인증
- 계정·대상·등록 계획 확정
- 명시 실행 승인
- 제어권 획득 후 실행
- 증거와 결과/후속 행동

### invariants

- I1 · 확인되지 않거나 승인되지 않은 사실/판매 조건 변경 금지
- I2 · 현재 인증·승인·권한·제어권 없이 외부 등록 동작 시작 금지
- I3 · 효과 진행/미확인/이미 확인 상태에서 동일 효과 재발급 금지
- I4 · 목표 증거 없이 성공 금지; 모의/실제 및 외부 객체 상태 구분
- I5 · 원본과 플랫폼별 계획/작업/결과 독립; 다른 플랫폼 실패·후속 심사가 기존 접수 성공을 덮어쓰지 않음

### milestones

- **mvp** (`mvp`): 2026-12-08 크몽 우선, 숨고 확장
- **final** (`final`): 2027-01-04 사용자 URL로 등록 가능한 플랫폼 최초 등록 및 결과 확인
- **scope** (`scope`): 실제 플랫폼 허용·보안·단계 승인 전 모의만; 숨고 실제 등록 객체 미확정; 무지원 임의 URL 자동 적응 불요

## top-design-amendment-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/top-design-amendment-v1.json) · blob `ad4f09689896206163dfce72d972281b10075891`

### id

- LR-TOP-AMEND-01

### base

- LR-TOP-20261124

### authority

- **date** (`date`): 2026-11-24
- **R01** (`R01`): 사람이 플랫폼에서 하는 일을 대신 해주는 거고 추가적으로 한다면 등록 전 원본 정보 검사와 플랫폼에 대한 정보를 알아서 등록하는데에 피하거나 필수적인 사항들을 고려한다는 거야 · 그리고 미리 플랫폼 절차도 알고 있으니 어려울게 없지 · 그럼 수정하고 세부 설계 진행하면 될 것 같은데
- **scope** (`scope`): 승인된 목적/논리 구조를 유지하고 사전 확보 플랫폼 정보 기반 등록 대행으로 명시. 상세 설계 진행 허용. 제품 구현 착수/실서비스/기존 TASK 변경은 아님.

### decisions

- A1 · 사전 확보 플랫폼 지식에 따라 사람의 최초 등록 업무를 대행; 원본과 플랫폼 요구 사항 사전 검사
- A2 · 실행 후 사용자 중단/변경/재개/rollback 없음; 오류 시에만 중단 후 결과 반환
- A3 · 멱등성은 키/논리 효과 식별을 기본 원칙으로 두고 물리 구현은 세부 설계
- A4 · 서버 원격 브라우저 구조 및 크몽 우선·숨고 확장 유지; 기술 위임, mock-only phase 유지

### unchanged

- 원본/계획/작업 독립, 다섯 논리 책임, 사용자 확인 및 직접 인증, 운영 허용과 사용자 승인, 증거 없는 성공 금지, 지원 URL만, 12/8·1/4 목표. 실제 업무 조사 불확실성/실서비스 권한 유지.

## implementation-v0.4.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/implementation-v0.4.json) · blob `f7b49262a4d470f6a2764e0fd2c559e6358cc416`

### requirements

#### REQ-01

- **ID** (`id`): REQ-01
- **title** (`title`): 원본·필수 정보·자료 준비
- **prior&#95;refs** (`prior_refs`): FR-01 · V3-R08
- **mvp** (`mvp`): required
- **final** (`final`): required
- **acceptance** (`acceptance`): 사용자 확인된 사실/이미지와 출처·버전, 누락/충돌 질문. 합성 90/180/270분 월4회 25/40/50만원을 변경하지 않음.
- **출처** (`source_refs`): SRC-05 · SRC-08

#### REQ-02

- **ID** (`id`): REQ-02
- **title** (`title`): 등록 대상 식별
- **prior&#95;refs** (`prior_refs`): DIR-04 · V3-R02 · V3-R09
- **mvp** (`mvp`): 지원 플랫폼 선택 및 등록 경로 결정
- **final** (`final`): URL로 지원 플랫폼/경로 선택
- **acceptance** (`acceptance`): 등록 가능한 대상 registry에 연결, 미지원/잘못된/권한 미확인 URL은 차단/안내, 임의 URL 요청 수행 금지.
- **출처** (`source_refs`): SRC-01 · SRC-04

#### REQ-03

- **ID** (`id`): REQ-03
- **title** (`title`): 플랫폼별 변환·검토
- **prior&#95;refs** (`prior_refs`): FR-02 · V3-R08 · V3-R09 · V3-R12
- **mvp** (`mvp`): required
- **final** (`final`): required
- **acceptance** (`acceptance`): 사실/단위 유지, LLM 제안과 확인값 구분, 필수 규칙/조건/권리 검사 및 확인 필요 항목 노출. AI 또는 확인된 대체 입력으로 모의 경로 가능; AI 기능 시연 별도.
- **출처** (`source_refs`): SRC-05 · SRC-06 · SRC-08

#### REQ-04

- **ID** (`id`): REQ-04
- **title** (`title`): 원격 직접 인증·제어권 인계
- **prior&#95;refs** (`prior_refs`): DIR-01 · DIR-02 · V3-R01 · V3-R05 · V3-R11
- **mvp** (`mvp`): required
- **final** (`final`): required
- **acceptance** (`acceptance`): 일반 브라우저에서 합성 인증, 동일 세션 서버 인계, 사용자/worker 상호배타, 뷰어 종료 후 계속. 세션 폐기·타 계정 거부. 기술 내부는 위임.
- **출처** (`source_refs`): SRC-09

#### REQ-05

- **ID** (`id`): REQ-05
- **title** (`title`): 실행 대상·승인·권한
- **prior&#95;refs** (`prior_refs`): FR-03 · V3-R01 · V3-R02 · V3-R03 · V3-R04 · V3-R05
- **mvp** (`mvp`): required
- **final** (`final`): required
- **acceptance** (`acceptance`): 계정/대상/버전/동작/환경 승인 및 운영 허용 별도, 가드 미충족이면 동작 0, 동일 효과 차단.
- **출처** (`source_refs`): SRC-02 · SRC-05

#### REQ-06

- **ID** (`id`): REQ-06
- **title** (`title`): 크몽 최초 등록
- **prior&#95;refs** (`prior_refs`): DIR-03 · FR-04 · V3-R07
- **mvp** (`mvp`): first&#95;required
- **final** (`final`): required&#95;if&#95;supported
- **acceptance** (`acceptance`): 크몽형 합성 상품 1건, 필드·이미지·가격 입력과 모의 심사 접수 후 독립 receipt 재조회 일치. 실제 심사 접수/공개 구별.
- **출처** (`source_refs`): SRC-06 · SRC-08

#### REQ-07

- **ID** (`id`): REQ-07
- **title** (`title`): 숨고 최초 등록 확장
- **prior&#95;refs** (`prior_refs`): DIR-03 · FR-04 · V3-R07
- **mvp** (`mvp`): second&#95;planned
- **final** (`final`): required&#95;if&#95;supported
- **acceptance** (`acceptance`): 숨고형 기존 합성 고수의 서비스 카테고리 및 문항 설정 저장 후 다시 조회 일치. 객체 후보이며 신규 고수·프로필·공개는 별도 결정; 12/8 통합 목표, 미충족시 R01 재계획.
- **출처** (`source_refs`): SRC-07 · SRC-08

#### REQ-08

- **ID** (`id`): REQ-08
- **title** (`title`): 결과·부분 효과·실패·재개
- **prior&#95;refs** (`prior_refs`): FR-05 · FR-06 · V3-R06 · V3-R07
- **mvp** (`mvp`): required
- **final** (`final`): required
- **acceptance** (`acceptance`): 대상별 모의 완료/실패/차단/확인 필요/미확인 표시, 증거·다음 조치. 응답 유실 후 중복 없음, 읽기 재확인+명시 재개. 접수와 공개 분리.
- **출처** (`source_refs`): SRC-02 · SRC-06

#### REQ-09

- **ID** (`id`): REQ-09
- **title** (`title`): 플랫폼 확장
- **prior&#95;refs** (`prior_refs`): DIR-04 · V3-R09
- **mvp** (`mvp`): registry+두 adapter 포트
- **final** (`final`): 지원 가능 플랫폼 확대 구조
- **acceptance** (`acceptance`): 지원 플랫폼/경로 추가는 registry·규칙·adapter·시험 단위. 공통 job/approval/DB/UI 계약 변경 최소화; 최종 지원 목록은 허용/일정/검증으로 확정. 신규 미지원 자동 적응 불필요.
- **출처** (`source_refs`): SRC-01 · SRC-04

#### REQ-10

- **ID** (`id`): REQ-10
- **title** (`title`): 격리·개인정보·안전한 운영
- **prior&#95;refs** (`prior_refs`): V3-R05 · V3-R11
- **mvp** (`mvp`): mock 최소 보안
- **final** (`final`): 운영 허용 시 강화 검증
- **acceptance** (`acceptance`): owner 격리, mock/live 서버 정책 차단, login 입력/비밀 미기록, 승인 자료만, 세션 만료·폐기, 실제 배포 보안과 권한 검증 전 live 불가.
- **출처** (`source_refs`): SRC-02 · SRC-09 · SRC-10

#### REQ-11

- **ID** (`id`): REQ-11
- **title** (`title`): 재현성과 서비스 가치
- **prior&#95;refs** (`prior_refs`): V3-R13 · V3-R14
- **mvp** (`mvp`): 재현 가능한 통합 시연
- **final** (`final`): 비교 평가·최종 증거
- **acceptance** (`acceptance`): 고정 fixture/버전/환경/실행 결과, 실패 포함. 능동 시간/시스템/심사대기·오류·비용 분리. 20~30분 희망치, 측정 전 성공 주장 금지.
- **출처** (`source_refs`): SRC-05 · SRC-11

