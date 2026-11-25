# WBS 및 통합 일정 이력

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## wbs-v0.5.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/wbs-v0.5.json) · blob `5203828cc220187ec53d1602579b9e12ab1cf5d0`

> 이전 WBS 후보. A2 및 현재 공통 계약 우선. 일정/담당 배정 전.

### id

- WBS-LESSON-V0.5

### status

- proposal&#95;not&#95;assigned

### date

- 2026-11-24

### availability

- **R02** (`R02`)
  - **unavailable&#95;from** (`unavailable_from`): 2026-12-06
  - **unavailable&#95;through** (`unavailable_through`): 2026-12-22
  - **handoff&#95;by** (`handoff_by`): 2026-12-04
  - **return&#95;from** (`return_from`): 2026-12-23
  - **during&#95;period** (`during_period`): no tasks, review gates or on-call dependency
  - **backup** (`backup`): R01 uses frozen domain fixture and decision notes; unresolved substantive changes remain needs&#95;action.
  - **planned&#95;handoff** (`planned_handoff`): 2026-12-03

### tasks

#### W01

- **ID** (`id`): W01
- **title** (`title`): V0.5 공통 계약·최소 제품 skeleton·수용 기준 동결
- **owner** (`owner`): R01
- **start** (`start`): 2026-11-25
- **end** (`end`): 2026-11-27
- **depends&#95;on** (`depends_on`): `[]`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-09
- **output** (`output`): 타입/오류/fixture, provider stub, 공통 실행 명령·mock guard, 통합 체크포인트, 플랫폼별 완료 조건
- **done** (`done`): 11/26 독립 PoC 근거 대조; 11/27 공통 계약·stub·smoke 재현 및 R01 착수 판단. AI/숨고 범위와 공수 확인; live 허용 문의는 지연 위험으로 착수 단계에 시작할 수 있으나 별도 공식 승인. V0.8 typed HTTP-02/17, action spec, resume 및 MVP gate fixture/port 합의; 착수 시 공수·가용성 확인.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-25 · 2026-11-26 · 2026-11-27
- **workdays** (`workdays`): `3`

#### W02

- **ID** (`id`): W02
- **title** (`title`): 도메인 fixture·검수 기준 1차 인계
- **owner** (`owner`): R02
- **start** (`start`): 2026-11-25
- **end** (`end`): 2026-11-27
- **depends&#95;on** (`depends_on`): `[]`
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-06 · REQ-07 · REQ-11
- **output** (`output`): 합성 원본·이미지·필드·누락 질문·정답 및 확인 불가 목록
- **done** (`done`): 11/27까지 초기 합성 원본/필드·질문·정답·미확인 조건 공유. 개인 자료 금지. 12/3 W19에서 최종 동결.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-25 · 2026-11-26 · 2026-11-27
- **workdays** (`workdays`): `3`

#### W19

- **ID** (`id`): W19
- **title** (`title`): AI 정보 구조화·플랫폼별 매핑·질문 및 최종 인계
- **owner** (`owner`): R02
- **start** (`start`): 2026-11-30
- **end** (`end`): 2026-12-03
- **depends&#95;on** (`depends_on`): W01 · W02
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-11
- **output** (`output`): AI provider + deterministic validation contract, raw source fixture/예상 질문, 12/3 코드·실행법·미완료 항목 인계
- **done** (`done`): T5-08 원문→후보 사실→누락 질문→확인→초안 검증. 모델 미사용 fixture는 별도 기술 시험. 실제 구현 가용성은 W01에서 확인; 불가 시 R01이 AI 범위를 축소/재배정하고 다른 업무 조정, 무조건 추가 업무 부과 금지. 12/3 인계 후 R03이 공통 모듈 유지보수. IC05에서 R02→R03 순으로 provider 계약·fixture·실행법 인계 후 연결/시험. stub 경로 유지, 지연 시 R01에게 범위/일정 영향만 보고.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-30 · 2026-12-01 · 2026-12-02 · 2026-12-03
- **workdays** (`workdays`): `4`

#### W03

- **ID** (`id`): W03
- **title** (`title`): 공통 앱·저장·승인/작업·상태 및 AI port 연결
- **owner** (`owner`): R03
- **start** (`start`): 2026-11-30
- **end** (`end`): 2026-12-03
- **depends&#95;on** (`depends_on`): W01 · W02
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-05 · REQ-08 · REQ-10
- **output** (`output`): 공통 API·versioned store·가드/attempt·결과, AI provider stub 연결, owner-scoped list
- **done** (`done`): W01 contract 기준 11/30 stub smoke, 12/1 API+store 연결, 12/3 실제 provider/AI 연결·기본 안전 시험. AI 모델 내부는 W19; 보안/unknown 기본 가드 생략 금지.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-30 · 2026-12-01 · 2026-12-02 · 2026-12-03
- **workdays** (`workdays`): `4`

#### W04

- **ID** (`id`): W04
- **title** (`title`): 원격 브라우저 runtime 및 port
- **owner** (`owner`): R05
- **start** (`start`): 2026-11-30
- **end** (`end`): 2026-12-02
- **depends&#95;on** (`depends_on`): W01
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
- **output** (`output`): R05 PoC 재사용 검토, 구현자 기술 선정, session/lease/operation gateway
- **done** (`done`): 직접 합성 로그인·동일 맥락·disconnect 지속·격리·폐기; no bypass; port 시험; 11/30 fake runtime, 12/1 인증/인계 연결, 12/2 실제 mock session 및 gateway 연동
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-30 · 2026-12-01 · 2026-12-02
- **workdays** (`workdays`): `3`

#### W05

- **ID** (`id`): W05
- **title** (`title`): 웹 화면·API 연결
- **owner** (`owner`): R04
- **start** (`start`): 2026-11-30
- **end** (`end`): 2026-12-03
- **depends&#95;on** (`depends_on`): W01
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-08
- **output** (`output`): UI-01~07 기본 화면 및 stub 연동
- **done** (`done`): 원본/대상/검토/인증/승인/결과 흐름; 확인 필요/unknown 표시; 11/30 stub UI, 12/1 원본/검토 API, 12/2 auth/plan 화면, 12/3 실제 API/작업 목록 연동
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-30 · 2026-12-01 · 2026-12-02 · 2026-12-03
- **workdays** (`workdays`): `4`

#### W06

- **ID** (`id`): W06
- **title** (`title`): 크몽 adapter 및 모의 실행
- **owner** (`owner`): R01
- **start** (`start`): 2026-11-30
- **end** (`end`): 2026-12-03
- **depends&#95;on** (`depends_on`): W01
- **요구 참조** (`requirement_refs`): REQ-06 · REQ-09
- **output** (`output`): 크몽 규칙·operation·readback/receipt adapter, R03/R05 자료 재사용
- **done** (`done`): 합성 필드·이미지·접수/재조회 성공; 필수 오류·효과 미확인 구분; stub port 사용 가능; 11/30 skeleton smoke 주관, 12/1 adapter plan 및 fake gateway, 12/2 runtime 연동, 12/3 receipt+AI/공통 연결 회귀
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-11-30 · 2026-12-01 · 2026-12-02 · 2026-12-03
- **workdays** (`workdays`): `4`

#### W07

- **ID** (`id`): W07
- **title** (`title`): 크몽 수직 통합·수용 시험
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-04
- **end** (`end`): 2026-12-04
- **depends&#95;on** (`depends_on`): W02 · W03 · W04 · W05 · W06 · W19
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-08 · REQ-10
- **output** (`output`): 첫 통합 release/시험 로그, R02 추가 의존 없는 fixture
- **done** (`done`): 12/4은 첫 통합 착수일이 아니라 기존 일별 smoke 기반 전체 크몽 수직 경로 수용 시험. 원본 AI 변환/계정/승인/이미지/receipt, 재접속, 실패 및 중복 차단 검증.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-04
- **workdays** (`workdays`): `1`

#### W08

- **ID** (`id`): W08
- **title** (`title`): 숨고 adapter·독립 fixture
- **owner** (`owner`): R04
- **start** (`start`): 2026-12-04
- **end** (`end`): 2026-12-07
- **depends&#95;on** (`depends_on`): W01 · W05
- **요구 참조** (`requirement_refs`): REQ-07 · REQ-09
- **output** (`output`): 숨고 대상/질문지·저장/readback 모의 adapter
- **done** (`done`): 확인된 합성 서비스 설정 목표 증거; 신규 가입/공개 효과 분리; R02 검토 필수 아님; 11/27 공통 contract와 fixture에서 Soomgo 전용 증거/이미지 차이 확인. UI 구현 기간에는 stub interface 합의, 본 adapter는 12/4·7.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-04 · 2026-12-07
- **workdays** (`workdays`): `2`

#### W18

- **ID** (`id`): W18
- **title** (`title`): MVP 직전 통합 보완·결함 수정 여유
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-07
- **end** (`end`): 2026-12-07
- **depends&#95;on** (`depends_on`): W07
- **요구 참조** (`requirement_refs`): REQ-05 · REQ-06 · REQ-08 · REQ-10
- **output** (`output`): 크몽 통합 회귀 결과·남은 결함/차단 목록, 숨고 연결 준비
- **done** (`done`): 12/4 크몽 수직 통합 결과 재검토 및 필요한 수정. 숨고 독립 구현 W08과 병렬 진행하며 W08 완료 후 W09에서 연결. 핵심 미충족 시 R01 범위/일정 재판단.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-07
- **workdays** (`workdays`): `1`

#### W09

- **ID** (`id`): W09
- **title** (`title`): 숨고 연결 및 MVP 시연
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-08
- **end** (`end`): 2026-12-08
- **depends&#95;on** (`depends_on`): W18 · W08
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **output** (`output`): 크몽 먼저 완료, 숨고 확장 시연 및 상태표
- **done** (`done`): 크몽 정상 경로/AI/재접속/기본 가드와 숨고 확장 검증. 각 수용 항목 상태 표시. 미충족 시 R01의 명시 범위/일정 재판정, 성공 위장 금지. MVP-GATE-01 필수 시험의 동일 후보 근거 확인 및 변경 후 회귀. gate 불완전이면 완료 주장 금지.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-08
- **workdays** (`workdays`): `1`

#### W10

- **ID** (`id`): W10
- **title** (`title`): URL 대상 registry·확장 계약
- **owner** (`owner`): R03
- **start** (`start`): 2026-12-09
- **end** (`end`): 2026-12-15
- **depends&#95;on** (`depends_on`): W09
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-09 · REQ-10
- **output** (`output`): URL resolver, registry version, supported/unsupported/blocked 판정
- **done** (`done`): 홈/지원 등록 URL, 미지원/잘못된/내부망 URL 차단; adapter 등록 시험; 기존 MVP registry/URL resolver를 교체하지 않고 홈/등록 경로·지원 목록·새 플랫폼 플러그인 계약 강화
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-09 · 2026-12-10 · 2026-12-11 · 2026-12-14 · 2026-12-15
- **workdays** (`workdays`): `5`

#### W11

- **ID** (`id`): W11
- **title** (`title`): runtime 안전·장애·격리 강화
- **owner** (`owner`): R05
- **start** (`start`): 2026-12-09
- **end** (`end`): 2026-12-18
- **depends&#95;on** (`depends_on`): W09
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-08 · REQ-10
- **output** (`output`): 실행 가드·lease fencing·crash recovery·운영 격리 PoC
- **done** (`done`): 취소/철회 race, old lease, 세션 폐기, 비밀 비노출; 실제 외부 실행 금지 유지
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-09 · 2026-12-10 · 2026-12-11 · 2026-12-14 · 2026-12-15 · 2026-12-16 · 2026-12-17 · 2026-12-18
- **workdays** (`workdays`): `8`

#### W12

- **ID** (`id`): W12
- **title** (`title`): 플랫폼 확장·UI 보완
- **owner** (`owner`): R04
- **start** (`start`): 2026-12-09
- **end** (`end`): 2026-12-18
- **depends&#95;on** (`depends_on`): W09
- **요구 참조** (`requirement_refs`): REQ-07 · REQ-09 · REQ-08
- **output** (`output`): 숨고 안정화 및 추가 등록 가능 후보 명세/adapter 계획
- **done** (`done`): 확인된 지원 대상만, 탈잉 등은 필수 아님; 공통 계약 유지
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-09 · 2026-12-10 · 2026-12-11 · 2026-12-14 · 2026-12-15 · 2026-12-16 · 2026-12-17 · 2026-12-18
- **workdays** (`workdays`): `8`

#### W13

- **ID** (`id`): W13
- **title** (`title`): 운영사 허용·최종 지원 범위 판단
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-09
- **end** (`end`): 2026-12-18
- **depends&#95;on** (`depends_on`): W09
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-09 · REQ-10
- **output** (`output`): 플랫폼별 지원·권한·실환경 gate, 보안 및 운영 확인표
- **done** (`done`): 12/18 기준 허용 근거 및 지원 범위 판단, 허용 근거 없으면 live blocked. 외부 회신 대기는 공수 제외; 이후 회신은 12/22 게이트 또는 별도 R01 승인에서 재검토. 실제 범위 승인 별도; mock 성과를 실등록으로 표기 금지.; live gate 조건 충족 여부와 승인 책임/실환경 시험 계획 명시. 별도 phase 승인 이전 실제 계정/사이트 실행 금지.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-09 · 2026-12-10 · 2026-12-11 · 2026-12-14 · 2026-12-15 · 2026-12-16 · 2026-12-17 · 2026-12-18
- **workdays** (`workdays`): `8`

#### W14

- **ID** (`id`): W14
- **title** (`title`): URL 기반 통합·회귀 시험
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-21
- **end** (`end`): 2026-12-22
- **depends&#95;on** (`depends_on`): W10 · W11 · W12 · W13
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-04 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10
- **output** (`output`): 지원 URL→등록 E2E, 실패/격리 회귀 결과
- **done** (`done`): 크몽/숨고 지원 경로, 미지원 차단, 원격 실행·증거; R02 참여 불필요; 외부 gate가 승인된 경우 별도 phase에서만 승인된 실제 경로 시험 가능, 그렇지 않으면 mock 검증 및 live 미달 기록.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-21 · 2026-12-22
- **workdays** (`workdays`): `2`

#### W15

- **ID** (`id`): W15
- **title** (`title`): 사용자 수용·가치 검수
- **owner** (`owner`): R02
- **start** (`start`): 2026-12-23
- **end** (`end`): 2026-12-28
- **depends&#95;on** (`depends_on`): W14
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-08 · REQ-11
- **output** (`output`): 동일 fixture 직접/AI/전용 비교, 누락·업무 시간 관측
- **done** (`done`): 실패 포함, 실제 심사 대기 구분, R02 참여 불가시 R01 대체 합성 검수 및 가치 미실측 표시; R02 복귀 후 이전 AI/도메인 인계 결과 검수, 직접/범용 AI/전용 서비스의 동일 조건 비교.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-23 · 2026-12-24 · 2026-12-28
- **workdays** (`workdays`): `3`

#### W16

- **ID** (`id`): W16
- **title** (`title`): 최종 결함 수정·배포/운영 검증
- **owner** (`owner`): R03
- **start** (`start`): 2026-12-23
- **end** (`end`): 2026-12-30
- **depends&#95;on** (`depends_on`): W14
- **요구 참조** (`requirement_refs`): REQ-05 · REQ-08 · REQ-10 · REQ-11
- **output** (`output`): 통합 release 후보, 설치/재현, 보안·회귀 기록
- **done** (`done`): R04/R05 각 모듈 수정 협력; 승인된 환경만, live 금지 기본값
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-23 · 2026-12-24 · 2026-12-28 · 2026-12-29 · 2026-12-30
- **workdays** (`workdays`): `5`

#### W17

- **ID** (`id`): W17
- **title** (`title`): 최종 지원 URL 수용 시험·제출 준비
- **owner** (`owner`): R01
- **start** (`start`): 2026-12-31
- **end** (`end`): 2027-01-04
- **depends&#95;on** (`depends_on`): W13 · W15 · W16
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-02 · REQ-03 · REQ-04 · REQ-05 · REQ-06 · REQ-07 · REQ-08 · REQ-09 · REQ-10 · REQ-11
- **output** (`output`): 최종 산출물, 지원 목록, 증거, 미충족·제약, 제출 기록
- **done** (`done`): 2027-01-04 목표: 등록 가능한 지원 플랫폼 URL+필요 정보/인증→등록 결과; live 조건 미충족은 mock만 보고; 실제 제출은 별도 확인; live gate 불충족 시 실제 서비스 목표 미달/미검증 명시. 실제 제출 증거 별도.
- **상태** (`status`): proposed
- **work&#95;dates** (`work_dates`): 2026-12-31 · 2027-01-04
- **workdays** (`workdays`): `2`

### milestones

#### M01

- **ID** (`id`): M01
- **date** (`date`): 2026-11-27
- **gate** (`gate`): 공통 계약 및 착수 판단
- **refs** (`refs`): W01

#### M02

- **ID** (`id`): M02
- **date** (`date`): 2026-12-03
- **gate** (`gate`): R02 인계 완료 목표 (최종 기한 12/4)
- **refs** (`refs`): W19

#### M03

- **ID** (`id`): M03
- **date** (`date`): 2026-12-04
- **gate** (`gate`): 크몽 수직 통합
- **refs** (`refs`): W07

#### M04

- **ID** (`id`): M04
- **date** (`date`): 2026-12-08
- **gate** (`gate`): MVP
- **refs** (`refs`): W09

#### M05

- **ID** (`id`): M05
- **date** (`date`): 2026-12-22
- **gate** (`gate`): URL 확장 및 운영 gate 검토
- **refs** (`refs`): W13 · W14

#### M06

- **ID** (`id`): M06
- **date** (`date`): 2027-01-04
- **gate** (`gate`): 최종 수용
- **refs** (`refs`): W17

### tests

#### AT-01

- **ID** (`id`): AT-01
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03
- **scenario** (`scenario`): 합성 원본 및 충돌/VAT 미확인
- **기대값** (`expected`): 원본 값 유지, 누락 질문, 임의 변환 0
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-02

- **ID** (`id`): AT-02
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-10
- **scenario** (`scenario`): 원격 사용자 인증→인계→viewer 종료
- **기대값** (`expected`): 동일 세션 작업 완료, 타 세션/낡은 lease 차단, 폐기
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-03

- **ID** (`id`): AT-03
- **요구 참조** (`requirement_refs`): REQ-05
- **scenario** (`scenario`): 잘못된 계정/승인 stale/미허용 동작
- **기대값** (`expected`): mutation 0
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-04

- **ID** (`id`): AT-04
- **요구 참조** (`requirement_refs`): REQ-06
- **scenario** (`scenario`): 크몽형 정상 등록
- **기대값** (`expected`): 필드/이미지/receipt 독립 재조회 일치
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-05

- **ID** (`id`): AT-05
- **요구 참조** (`requirement_refs`): REQ-07 · REQ-09
- **scenario** (`scenario`): 숨고형 정상 설정
- **기대값** (`expected`): category/문항 독립 재조회 일치, 공개와 분리
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-06

- **ID** (`id`): AT-06
- **요구 참조** (`requirement_refs`): REQ-08 · REQ-05
- **scenario** (`scenario`): 응답 유실/첨부 오류/중복/취소
- **기대값** (`expected`): unknown/failed/cancelled 분리, 추가 mutation 0
- **stage** (`stage`): MVP
- **실행** (`execution`): not&#95;run

#### AT-07

- **ID** (`id`): AT-07
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-09 · REQ-10
- **scenario** (`scenario`): 지원 홈/등록 URL, 미지원/내부망/redirect
- **기대값** (`expected`): registry match, 무단 fetch 0, 적합 adapter
- **stage** (`stage`): FINAL
- **실행** (`execution`): not&#95;run

#### AT-08

- **ID** (`id`): AT-08
- **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-08 · REQ-10
- **scenario** (`scenario`): crash/철회 race/동시 제어/격리
- **기대값** (`expected`): 새 admission 차단, durable unknown, 격리/삭제 검증
- **stage** (`stage`): FINAL
- **실행** (`execution`): not&#95;run

#### AT-09

- **ID** (`id`): AT-09
- **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-11
- **scenario** (`scenario`): A/B/C 동일 목표 업무 비교
- **기대값** (`expected`): 활동 시간·오류·개입·비용/대기 분리, 실패 포함
- **stage** (`stage`): FINAL
- **실행** (`execution`): not&#95;run

#### AT-10

- **ID** (`id`): AT-10
- **요구 참조** (`requirement_refs`): REQ-02 · REQ-06 · REQ-07 · REQ-08 · REQ-09
- **scenario** (`scenario`): 지원 URL 입력→최초 등록→결과
- **기대값** (`expected`): 각 지원 플랫폼 목표/증거 일치; 미지원 차단; actual 권한 없으면 mock only
- **stage** (`stage`): FINAL
- **실행** (`execution`): not&#95;run

### assumptions

- 일정은 목표일 기준 초안. 토·일과 한국 공휴일(12/25, 1/1)을 제외한 실제 근무일만 배정. workdays는 일정 창 내 근무일 수이지 확정 인일이 아니며 팀원 실제 가용시간·공수는 배정 전 검토.
- R01 크몽 adapter 담당은 R05 원격 runtime과 병렬화하기 위한 제안. 실제 배정은 R01 검토. R03~05 기존 TASK와 새 WBS 중복 시 기존 결과를 재사용, 신규 canonical TASK는 승인 후.
- 실제 사이트 허용/보안은 독립 gate; 검증 미충족이면 목표 미충족 또는 제한된 mock 시연으로 기록.
- W17 최종 통합 수용은 W16 종료 후 12/31 시작, 실제 작업일은 12/31·1/4 두 날. 제출 문서 초안 준비는 앞 단계와 병렬 가능. 선행 작업은 다음 근무일 착수 전에 완료.
- W13 권한·범위 판단 작업 창을 12/18까지로 조정해 R01의 12/21~22 통합 시험과 중복 배정을 피한다. 외부 회신 지연은 별도 게이트/미확인으로 관리.
- R02 11/27 domain fixture 초기 공유, 11/30~12/3 AI 구현 및 최종 인계 제안. 개인 사유 기록 없음. 12/6~22 작업/리뷰/호출 없음. R03은 인계된 provider 유지보수; 범위 변경은 R01 판단.
- 일별 checkpoint는 기존 작업 창에 포함, 별도 전일 작업이 아님. R03/R05/R04의 결함 지원 공수는 W01에서 확인. R01의 주책임 일정 20근무일 이상에 팀 관리·리뷰 부담 추가: 가용성 확인 후 W06/W19 등 조정, 주말 작업 금지.
- MVP의 핵심 경로에 최소 AI, source 재사용, plan/승인, job 재접속, 재연결 및 안전한 unknown 처리 포함. UI 정교화/추가 플랫폼/대규모 인프라는 후속, 가드·권한·효과 증거는 축소 금지. 실제 소요 추정 없음.
- 12/8까지 크몽 1개 완결과 숨고 확장 목표; 12/4·7 숨고 실제 구현 창 2근무일, 기존 조사/PoC 활용. W01에서 부족하면 R01이 명시적으로 범위/우선순위를 재결정.

### calendar

- **timezone** (`timezone`): Asia/Seoul
- **period&#95;start** (`period_start`): 2026-11-25
- **period&#95;end** (`period_end`): 2027-01-04
- **working&#95;weekdays** (`working_weekdays`): Mon · Tue · Wed · Thu · Fri
- **weekend&#95;days&#95;utc** (`weekend_days_utc`): `0` · `6`
- **holidays** (`holidays`)
  - **[0] **
    - **date** (`date`): 2026-12-25
    - **name** (`name`): 기독탄신일
    - **source** (`source`): https://www.kasa.go.kr/prog/plcyBrf/brief/kor/sub01&#95;01&#95;04/view.do?plcyBrfNo=202
  - **[1] **
    - **date** (`date`): 2027-01-01
    - **name** (`name`): 신정
    - **source** (`source`): https://www.kasa.go.kr/prog/bbsArticle/BBSMSTR&#95;000000000018/view.do?bbsId=BBSMSTR&#95;000000000018&amp;nttId=B000000003234Li6nD2
- **rule** (`rule`): 주말과 공휴일은 작업일·공수 산정 및 작업/검토/마일스톤 배정에서 제외. 날짜 범위 안의 work&#95;dates만 작업일이며, 날짜 단위 기간은 확정 공수(인일) 아님. 추가 임시공휴일 지정 시 재계산.
- **total&#95;workdays** (`total_workdays`): `27`
- **mvp&#95;workdays** (`mvp_workdays`): `10`
- **post&#95;mvp&#95;workdays** (`post_mvp_workdays`): `17`
- **r02&#95;unavailable&#95;workdays** (`r02_unavailable_workdays`): `12`

### schedule_revision

- v0.5-progressive-integration

### change_log

- **[0] **
  - **date** (`date`): 2026-11-24
  - **이유** (`reason`): R01 지시: 주말·공휴일 작업 시간 제외
  - **before&#95;commit** (`before_commit`): 977404b9386678137842cc489ca29a0ad35c2c43
  - **changes** (`changes`)
    - **[0] W02**
      - **ID** (`id`): W02
      - **before** (`before`)
        - **start** (`start`): 2026-11-25
        - **end** (`end`): 2026-12-04
        - **depends&#95;on** (`depends_on`): `[]`
      - **after** (`after`)
        - **start** (`start`): 2026-11-25
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): `[]`
        - **workdays** (`workdays`): `7`
    - **[1] W03**
      - **ID** (`id`): W03
      - **before** (`before`)
        - **start** (`start`): 2026-11-28
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
      - **after** (`after`)
        - **start** (`start`): 2026-11-30
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
        - **workdays** (`workdays`): `4`
    - **[2] W04**
      - **ID** (`id`): W04
      - **before** (`before`)
        - **start** (`start`): 2026-11-28
        - **end** (`end`): 2026-12-02
        - **depends&#95;on** (`depends_on`): W01
      - **after** (`after`)
        - **start** (`start`): 2026-11-30
        - **end** (`end`): 2026-12-02
        - **depends&#95;on** (`depends_on`): W01
        - **workdays** (`workdays`): `3`
    - **[3] W05**
      - **ID** (`id`): W05
      - **before** (`before`)
        - **start** (`start`): 2026-11-28
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
      - **after** (`after`)
        - **start** (`start`): 2026-11-30
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
        - **workdays** (`workdays`): `4`
    - **[4] W06**
      - **ID** (`id`): W06
      - **before** (`before`)
        - **start** (`start`): 2026-11-28
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
      - **after** (`after`)
        - **start** (`start`): 2026-11-30
        - **end** (`end`): 2026-12-03
        - **depends&#95;on** (`depends_on`): W01
        - **workdays** (`workdays`): `4`
    - **[5] W07**
      - **ID** (`id`): W07
      - **before** (`before`)
        - **start** (`start`): 2026-12-04
        - **end** (`end`): 2026-12-05
        - **depends&#95;on** (`depends_on`): W02 · W03 · W04 · W05 · W06
      - **after** (`after`)
        - **start** (`start`): 2026-12-04
        - **end** (`end`): 2026-12-04
        - **depends&#95;on** (`depends_on`): W02 · W03 · W04 · W05 · W06
        - **workdays** (`workdays`): `1`
    - **[6] W18**
      - **ID** (`id`): W18
      - **before** (`before`): `null`
      - **after** (`after`)
        - **start** (`start`): 2026-12-07
        - **end** (`end`): 2026-12-07
        - **depends&#95;on** (`depends_on`): W07
        - **workdays** (`workdays`): `1`
    - **[7] W09**
      - **ID** (`id`): W09
      - **before** (`before`)
        - **start** (`start`): 2026-12-08
        - **end** (`end`): 2026-12-08
        - **depends&#95;on** (`depends_on`): W07 · W08
      - **after** (`after`)
        - **start** (`start`): 2026-12-08
        - **end** (`end`): 2026-12-08
        - **depends&#95;on** (`depends_on`): W18 · W08
        - **workdays** (`workdays`): `1`
    - **[8] W13**
      - **ID** (`id`): W13
      - **before** (`before`)
        - **start** (`start`): 2026-12-09
        - **end** (`end`): 2026-12-22
        - **depends&#95;on** (`depends_on`): W09
      - **after** (`after`)
        - **start** (`start`): 2026-12-09
        - **end** (`end`): 2026-12-18
        - **depends&#95;on** (`depends_on`): W09
        - **workdays** (`workdays`): `8`
    - **[9] W14**
      - **ID** (`id`): W14
      - **before** (`before`)
        - **start** (`start`): 2026-12-19
        - **end** (`end`): 2026-12-22
        - **depends&#95;on** (`depends_on`): W10 · W11 · W12
      - **after** (`after`)
        - **start** (`start`): 2026-12-21
        - **end** (`end`): 2026-12-22
        - **depends&#95;on** (`depends_on`): W10 · W11 · W12
        - **workdays** (`workdays`): `2`
  - **milestones** (`milestones`)
    - **[0] M02**
      - **ID** (`id`): M02
      - **before** (`before`): 2026-12-04
      - **after** (`after`): 2026-12-03
    - **[1] M03**
      - **ID** (`id`): M03
      - **before** (`before`): 2026-12-05
      - **after** (`after`): 2026-12-04
- **[1] **
  - **date** (`date`): 2026-11-24
  - **이유** (`reason`): V0.5 P08/P10 AI 책임 및 점진 통합
  - **before&#95;commit** (`before_commit`): d3e550b2bb24ae684b97b79e799c654124808f44
  - **changes** (`changes`): W02 11/27 초기 인계로 분리 · W19 R02 11/30~12/3 AI·최종 인계 · W03/04/05/06 일별 연결, W07 최초 전체 수용 · W14 운영 gate 선행; 외부 gate 미달은 mock · 휴일·R02 부재·12/8/1/4 유지

### base

- wbs-v0.4.json

### integration_checkpoints

#### IC01

- **ID** (`id`): IC01
- **date** (`date`): 2026-11-27
- **owner** (`owner`): R01
- **participants** (`participants`): R02 · R03 · R04 · R05
- **기대값** (`expected`): 공통 타입·fixture·fake provider·launch/smoke 계약, 최소 환경 합의; 기존 TASK-043~045 결과 검토
- **within&#95;tasks** (`within_tasks`): W01 · W02

#### IC02

- **ID** (`id`): IC02
- **date** (`date`): 2026-11-30
- **owner** (`owner`): R01
- **participants** (`participants`): R02 · R03 · R04 · R05
- **기대값** (`expected`): fake provider로 UI→API→plan/approve→job→result 연결, 통합 실행 명령; mock only
- **within&#95;tasks** (`within_tasks`): W19 · W03 · W04 · W05 · W06

#### IC03

- **ID** (`id`): IC03
- **date** (`date`): 2026-12-01
- **owner** (`owner`): R01
- **participants** (`participants`): R02 · R03 · R04 · R05
- **기대값** (`expected`): 실제 원본/DB·plan + 원격 인증 stub/실제 경계, 계약 검증·실패 목록
- **within&#95;tasks** (`within_tasks`): W19 · W03 · W04 · W05 · W06

#### IC04

- **ID** (`id`): IC04
- **date** (`date`): 2026-12-02
- **owner** (`owner`): R01
- **participants** (`participants`): R02 · R03 · R04 · R05
- **기대값** (`expected`): 원격 실제 mock auth/lease + UI 검토/승인 + adapter 연결, no bypass
- **within&#95;tasks** (`within_tasks`): W19 · W03 · W04 · W05 · W06

#### IC05

- **ID** (`id`): IC05
- **date** (`date`): 2026-12-03
- **owner** (`owner`): R01
- **participants** (`participants`): R02 · R03 · R04
- **기대값** (`expected`): AI 원문 입력/질문→draft, 크몽 독립 readback, 최종 R02 인계; 원격 담당 완료 산출물 사용; R02 artifact/fixture 인계 먼저, 이후 R03 연결·실제 모델 수용 시험. 시간 초과 시 미완료 및 범위 판단.
- **within&#95;tasks** (`within_tasks`): W19 · W03 · W05 · W06

#### IC06

- **ID** (`id`): IC06
- **date** (`date`): 2026-12-04
- **owner** (`owner`): R01
- **participants** (`participants`): R03 · R04 · R05
- **기대값** (`expected`): 크몽 E2E 수용; 결함 수정 책임 명시, R02 참여 불필요
- **within&#95;tasks** (`within_tasks`): W07 · W08

#### IC07

- **ID** (`id`): IC07
- **date** (`date`): 2026-12-07
- **owner** (`owner`): R01
- **participants** (`participants`): R04
- **기대값** (`expected`): 크몽 회귀 보완, 숨고 adapter 독립 시험 및 통합 준비
- **within&#95;tasks** (`within_tasks`): W18 · W08

#### IC08

- **ID** (`id`): IC08
- **date** (`date`): 2026-12-08
- **owner** (`owner`): R01
- **participants** (`participants`): R03 · R04 · R05
- **기대값** (`expected`): MVP 수용표, 실제 통과/실패/미검증 구분; MVP-GATE-01 동일 후보 검증 결과, 미실행/실패/구버전 근거 분리.
- **within&#95;tasks** (`within_tasks`): W09

### mvp_gate

- **ID** (`id`): MVP-GATE-01
- **work&#95;ref** (`work_ref`): W09
- **milestone&#95;ref** (`milestone_ref`): M04
- **date** (`date`): 2026-12-08
- **scope** (`scope`): integrated&#95;mock&#95;product
- **groups** (`groups`)
  - **[0] source&#95;and&#95;ai**
    - **ID** (`id`): source&#95;and&#95;ai
    - **test&#95;refs** (`test_refs`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-03
  - **[1] remote&#95;auth&#95;and&#95;approval**
    - **ID** (`id`): remote&#95;auth&#95;and&#95;approval
    - **test&#95;refs** (`test_refs`): AT-02 · AT-03 · T5-01 · T5-02 · T5-04 · T5-12
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
  - **[2] target&#95;and&#95;contract**
    - **ID** (`id`): target&#95;and&#95;contract
    - **test&#95;refs** (`test_refs`): T5-03 · T5-07
    - **요구 참조** (`requirement_refs`): REQ-02 · REQ-09
  - **[3] platform&#95;goals**
    - **ID** (`id`): platform&#95;goals
    - **test&#95;refs** (`test_refs`): AT-04 · AT-05 · T5-06 · T5-09 · T5-13
    - **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-09
  - **[4] result&#95;and&#95;recovery**
    - **ID** (`id`): result&#95;and&#95;recovery
    - **test&#95;refs** (`test_refs`): AT-06 · T5-05
    - **요구 참조** (`requirement_refs`): REQ-08 · REQ-11
- **required&#95;test&#95;refs** (`required_test_refs`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · AT-02 · AT-03 · T5-01 · T5-02 · T5-04 · T5-12 · T5-03 · T5-07 · AT-04 · AT-05 · T5-06 · T5-09 · T5-13 · AT-06 · T5-05
- **actual&#95;model&#95;test&#95;refs** (`actual_model_test_refs`): T5-08
- **candidate&#95;fields** (`candidate_fields`): build&#95;sha · contract&#95;digest · fixture&#95;digest · environment
- **environment** (`environment`): mock
- **verdicts** (`verdicts`): pass · fail · incomplete
- **evidence&#95;required** (`evidence_required`): test&#95;ref · run&#95;ref · verdict · execution&#95;kind · candidate
- **execution&#95;kind** (`execution_kind`): integrated&#95;mock&#95;product
- **reuse** (`reuse`): 동일 build/contract/fixture/environment 식별자 근거만 재사용. W18 또는 통합 변경으로 식별자 변경 시 필수 자동 suite 재실행. 누락/unknown/not&#95;run/stale/수동 AI 대체는 incomplete. 정적/추상 설계 검증 제외.
- **completion** (`completion`): 모든 필수 시험 pass만 MVP mock 통과. 실패·미확인 시 기존 범위/일정 판단 규칙 유지; mock pass는 live/실서비스 목표 달성 아님.
- **execution&#95;status** (`execution_status`): not&#95;run

### revision

- 0.5.1-v08

