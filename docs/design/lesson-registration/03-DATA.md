# 상위 데이터와 상세 공통 계약

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## logical-data-contract-decision-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-data-contract-decision-v1.json) · blob `7141bcc48dabc36e42736035f4a6fcc2b8526f34`

> remaining/closure는 결정 당시 상태. 현재 해결 여부는 후속 V4/공통 V1에서 확인.

### id

- LR-LOGICAL-DATA-01

### version

- `1`

### date

- 2026-11-25

### status

- agreed&#95;frozen&#95;upper&#95;logical&#95;contract

### authority

- **actor** (`actor`): R01
- **approval&#95;quote** (`approval_quote`): 문제 없어 보여 그럼 상위 수준에서 논리적 데이터 계약 설계는 완료된 건가
- **record&#95;instruction** (`record_instruction`): 그럼 깃허브에 반영해
- **scope** (`scope`): 직전 제안의 상위 논리적 데이터 계약과 설계 원칙에 대한 합의. 상세 필드/스키마/API/물리 설계 또는 제품 구현·운영·TASK 변경의 승인 아님.

### basis

- **candidate&#95;commit** (`candidate_commit`): a7de5d76ad4946f29c9c61f23f5c2e03946f9e11
- **refs** (`refs`): top-design-v1.json · top-design-amendment-v1.json · detail-decisions-v2.json · detail-contract-v2.json · logical-behavior-v5.json · interface-review-evidence-v3.json
- **precedence** (`precedence`): 상위 목적·범위·안전 불변식과 오류 시 중단 원칙 유지. 이 결정은 데이터 계약의 상위 원칙을 확정하며 V2/V3 상세 후보의 상충 부분보다 우선한다. 상세 후보와 과거 검증 근거는 보존한다.

### principles

#### LD-01

- **ID** (`id`): LD-01
- **결정** (`decision`): 공통 업무에서 사용하는 정보의 의미와 전달만 공통 계약으로 정의하고 플랫폼별 항목·타입·필수/조건부 제약·절차·완료 조건은 플랫폼 프로필이 정의한다.
- **이유** (`rationale`): 등록 업무의 공통 구조를 유지하면서 지원 플랫폼마다 달라지는 필드를 보존한다. 지원 플랫폼 추가 시 공통 계약 수정이 원칙적으로 불필요해야 한다.

#### LD-02

- **ID** (`id`): LD-02
- **결정** (`decision`): 원본(Source), 플랫폼 프로필(Profile), 등록 요청(Registration)의 3개 핵심 논리 구조를 유지한다. 준비·인증·승인 범위·진행·결과는 등록 요청에 속하는 정보이며 독립 업무 자원을 강제하지 않는다.
- **이유** (`rationale`): 원본은 여러 등록에서, 프로필은 여러 사용자에게 재사용되고 등록 요청은 독립적으로 수행된다. 분리는 수명주기와 재사용 여부에 근거한다.

#### LD-03

- **ID** (`id`): LD-03
- **결정** (`decision`): 동일 의미의 정보는 동일 타입을 사용하며 데이터의 생성·수신·변경·검증 책임을 명시한다.
- **이유** (`rationale`): 컴포넌트마다 다른 의미로 해석하거나 책임이 누락되지 않도록 한다.

#### LD-04

- **ID** (`id`): LD-04
- **결정** (`decision`): 등록값은 해당 프로필의 계약으로 검사한다. 공통 식별자는 특정 플랫폼 열거형에 묶지 않고 서버의 지원 프로필 조회 및 유효성 검사로 제한한다.
- **이유** (`rationale`): 모든 필드의 공통화와 무검증 자유형 JSON의 단점을 피한다. 미지원/미확인 실제 플랫폼에 대한 실행 허용을 뜻하지 않는다.

#### LD-05

- **ID** (`id`): LD-05
- **결정** (`decision`): 준비 결과는 등록값·정보 근거·문제를 전달한다. 준비 완료 여부는 필수 조건 충족 및 해결되지 않은 차단 문제 여부에서 도출하며 별도 독립 상태로 관리하지 않는다.
- **이유** (`rationale`): 완료 표시와 실제 검사 결과 간 불일치를 방지하고 사용자에게 필요한 정보만 질문한다.

#### LD-06

- **ID** (`id`): LD-06
- **결정** (`decision`): 실행 범위는 승인된 등록값·원본/프로필 버전·인증된 계정 및 대상·확인된 연결을 결합하여 고정한다. 승인 참조는 등록 요청 내 고정 범위를 식별하며 별도 계획 생성이나 승인 관리 자원을 추가하지 않는다.
- **이유** (`rationale`): 사전 확보 절차로 수행 가능한 업무이며 승인 내용과 실제 실행을 일치시키기 위함이다. 원격 연결 참조는 서버 내부에서만 전달하고 세션/자격증명 자체는 공통 업무 데이터에 넣지 않는다.

#### LD-07

- **ID** (`id`): LD-07
- **결정** (`decision`): 등록 결과는 목표 판정·확인된 수행/효과·관측 대상과 방식이 포함된 근거·오류를 제공한다. 목표 달성은 해당 프로필의 완료 조건으로 판정한다.
- **이유** (`rationale`): 제출 응답과 독립 재조회 등 관측 방식을 구분하고 신뢰할 수 있는 근거가 충분하면 불필요한 조회를 강제하지 않는다. 오류 중단 및 미확인 효과 보존 원칙 유지.

#### LD-08

- **ID** (`id`): LD-08
- **결정** (`decision`): 공통 타입·플랫폼 규칙·업무 관계·실행 조건·결과 검사를 각 책임 경계에서 수행한다. 논리 계약과 물리적 저장 및 코드 구조를 구분한다.
- **이유** (`rationale`): 타입이 맞는 것만으로 업무 유효성을 보장할 수 없으며, 검증 책임 구분은 별도 검증 서비스 5개를 의미하지 않는다.

### ownership

- 플랫폼 프로필 · KNOW · CO/PREP/EXEC/RESULT · 동일 고정 프로필의 정보 및 규칙
- 준비 결과 · PREP · CO · 등록값, 근거, 문제; 프로필과 원본 관계 검사
- 인증·대상 확인 · EXEC · CO · 신뢰할 수 있는 계정/대상과 서버 내부 연결 참조
- 승인된 실행 범위 · CO · EXEC · 승인된 값과 대상·프로필·연결 고정; 실행 전 조건 검증
- 실행 관측 · EXEC · RESULT · 수행 결과·대상·관측 방식·근거·오류
- 등록 결과 · RESULT · CO · 프로필 완료 조건에 따른 판정 및 근거; CO가 저장/제공

### acceptance

- 동일 원본으로 서로 독립된 크몽/숨고 등록 요청을 처리할 수 있다.
- 새로운 지원 플랫폼을 추가할 때 공통 업무 구조와 계약의 수정이 원칙적으로 필요하지 않다. 플랫폼별 등록 계약 및 검증·실행 구현은 추가한다.
- 필수 정보 누락·충돌·제약 위반이 있을 때 필요한 사항만 확인하고 임의의 값으로 실행하지 않는다.
- 승인된 값과 실제 확인된 계정·대상·연결로만 실행한다.
- 정상 완료와 오류 중단, 확인된 결과와 미확인 결과를 구분하고 근거를 제공한다.

### closure

- **upper&#95;logical&#95;data&#95;contract** (`upper_logical_data_contract`): agreed&#95;complete
- **detail&#95;data&#95;contract** (`detail_data_contract`): candidate&#95;needs&#95;refinement&#95;and&#95;verification
- **interface&#95;api** (`interface_api`): candidate&#95;needs&#95;alignment
- **physical&#95;integration** (`physical_integration`): deferred&#95;pending&#95;independent&#95;evidence
- **implementation** (`implementation`): not&#95;authorized&#95;by&#95;this&#95;decision
- **live** (`live`): not&#95;authorized&#95;mock&#95;only

### remaining

#### P1

- **ID** (`id`): P1
- **issue** (`issue`): 인증 출력→실행 입력의 내부 연결 참조 및 동일 연결 바인딩 계약
- **상태** (`status`): open

#### P2

- **ID** (`id`): P2
- **issue** (`issue`): 완료 근거의 관측 방식 및 대상과 증거 연결 계약
- **상태** (`status`): open

#### P3

- **ID** (`id`): P3
- **issue** (`issue`): 플랫폼 ID/종류/목표의 공통 스키마 고정 열거형을 지원 프로필 기반 계약으로 정리
- **상태** (`status`): open

#### P4

- **ID** (`id`): P4
- **issue** (`issue`): 의미적 검사 규칙의 책임·실행 가능한 검증과 정상/비정상/확장 예시
- **상태** (`status`): open

#### P5

- **ID** (`id`): P5
- **issue** (`issue`): 상세 데이터 타입·필수/조건부 필드·참조·제약과 인터페이스/API의 정합성; 구현자 통합 가능 수준 검증
- **상태** (`status`): open

### non_changes

- 제품 범위, 승인·오류 시 중단 원칙, 기존 4개 작업 상태, 기존 독립 TASK-043~045 및 phase, main, 실제 플랫폼 실행 허용 여부 변경 없음.
- 정확한 필드명, 물리 테이블, 프레임워크, DB/원격 브라우저 기술 선택은 본 합의에서 확정하지 않음.

## data-contract-v4.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-contract-v4.json) · blob `edd84980d5df53c8df0800dd28f7878396ad4397`

### id

- LR-DATA-04

### date

- 2026-11-25

### status

- delegated&#95;detailed&#95;contract&#95;mock&#95;baseline&#95;design&#95;checked

### authority

- R01: 그러면 기존 조사 자료를 근거로 상세 계약을 결정하고 권장대로 진행해 단 나를 설득할 수 있어야 해

### basis

- **commit** (`commit`): b5317a5a3ca8081117b512a394831c112a1c1d15
- **refs** (`refs`)
  - **[0] **
    - **path** (`path`): interface-schema-v3.json
    - **blob** (`blob`): ea45fc389d1c9159bfd2e53f6a0d16aa4734eb89
  - **[1] **
    - **path** (`path`): interface-contract-v3.json
    - **blob** (`blob`): e6b73da91c0856e815601739301a53adcc321e70
  - **[2] **
    - **path** (`path`): logical-data-contract-decision-v1.json
    - **blob** (`blob`): 7141bcc48dabc36e42736035f4a6fcc2b8526f34
  - **[3] **
    - **path** (`path`): detail-design-v0.2.json
    - **blob** (`blob`): ee0490e7bad742cb4e9cf3f593da1bc1421c16c2
  - **[4] **
    - **path** (`path`): detail-gate-v1.json
    - **blob** (`blob`): 55c66d285183fb4a8a12041b883c12e7775d12f7
- **approved** (`approved`): LR-LOGICAL-DATA-01

### precedence

- V4 common and profile contract supersedes conflicting V2/V3 detailed schema/ports/profile fields only. Upper purpose/LD-01~08, existing error-only stop, mock-only, team T1~T6 and phase unchanged. V3 wire paths candidate, retain nine, not implementation authorization.

### source_evidence

#### S03

- **ID** (`id`): S03
- **title** (`title`): R02 강사 요구·최신 조건
- **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
- **path** (`path`): docs/members/R02/workspace/2026-11-23&#95;lesson-pain-priority.md
- **limit** (`limit`): 사용자 진술·회상·최신 확인값, 실측 없음
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R02/workspace/2026-11-23&#95;lesson-pain-priority.md
- **blob** (`blob`): c1aba280833039a5787b4460d948de231b44e135

#### S04

- **ID** (`id`): S04
- **title** (`title`): R03 개인 PoC 명세
- **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
- **path** (`path`): docs/members/R03/workspace/test/SPEC.md
- **limit** (`limit`): 크몽형 모의 실험, 고정 fixture
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/SPEC.md
- **blob** (`blob`): 7ef82683df7826330ec00a1348b56c7b48973c0f

#### S07

- **ID** (`id`): S07
- **title** (`title`): R03 검증 기록
- **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
- **path** (`path`): docs/members/R03/workspace/test/verification.json
- **limit** (`limit`): 19 pass 자기 보고, 모의 Skyvern 입력·첨부·영수증; 독립 재실행 아님
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/verification.json
- **blob** (`blob`): 5a343dd028889970e2cd64dbf0f2bab4e27a5fb9

#### S08

- **ID** (`id`): S08
- **title** (`title`): R04 숨고 업무 흐름
- **commit** (`commit`): 926b5de7678f8984be035409d386c6347d749f56
- **path** (`path`): docs/members/R04/workspace/2026-11-24&#95;숨고&#95;고수등록&#95;교육신청&#95;사용자흐름&#95;서비스절차&#95;설계분석보고서.md
- **limit** (`limit`): 기존 고수 계정 관측 및 제안, 신규 가입·공개 추론 분리
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24&#95;%EC%88%A8%EA%B3%A0&#95;%EA%B3%A0%EC%88%98%EB%93%B1%EB%A1%9D&#95;%EA%B5%90%EC%9C%A1%EC%8B%A0%EC%B2%AD&#95;%EC%82%AC%EC%9A%A9%EC%9E%90%ED%9D%90%EB%A6%84&#95;%EC%84%9C%EB%B9%84%EC%8A%A4%EC%A0%88%EC%B0%A8&#95;%EC%84%A4%EA%B3%84%EB%B6%84%EC%84%9D%EB%B3%B4%EA%B3%A0%EC%84%9C.md
- **blob** (`blob`): 0de56aa480c4d207a09f4f9f560d707f8004a979

#### S09

- **ID** (`id`): S09
- **title** (`title`): R04 화면 보고서
- **commit** (`commit`): 926b5de7678f8984be035409d386c6347d749f56
- **path** (`path`): docs/members/R04/workspace/2026-11-24&#95;숨고&#95;고수전환&#95;및&#95;등록절차&#95;화면스크린샷&#95;상세보고서.md
- **limit** (`limit`): STEP 06~12, 15, 16 보고서 관측; 스크린샷 원본 개별 검증 안 함
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24&#95;%EC%88%A8%EA%B3%A0&#95;%EA%B3%A0%EC%88%98%EC%A0%84%ED%99%98&#95;%EB%B0%8F&#95;%EB%93%B1%EB%A1%9D%EC%A0%88%EC%B0%A8&#95;%ED%99%94%EB%A9%B4%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7&#95;%EC%83%81%EC%84%B8%EB%B3%B4%EA%B3%A0%EC%84%9C.md
- **blob** (`blob`): 4062a83b314fd6db11d4572edfefc8873a367287

#### S10

- **ID** (`id`): S10
- **title** (`title`): R05 입력 뼈대
- **commit** (`commit`): c5cef60dceb98390b008e7345fc5c0492695e8e3
- **path** (`path`): docs/members/R05/workspace/2026-11-24&#95;platform-input-skeleton.md
- **limit** (`limit`): 수동 작성 화면·임시저장 보고, 플랫폼별 제약 후보; 실제 자동화 아님
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-24&#95;platform-input-skeleton.md
- **blob** (`blob`): ba0a1f1d6243876929efd4b8aad6cd602570d47a

#### S11

- **ID** (`id`): S11
- **title** (`title`): R05 기술·권한 조사
- **commit** (`commit`): c5cef60dceb98390b008e7345fc5c0492695e8e3
- **path** (`path`): docs/members/R05/workspace/2026-11-23&#95;lesson-technical-feasibility.md
- **limit** (`limit`): 공식/관찰/추정 구분, 운영사 허용 미확인
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-23&#95;lesson-technical-feasibility.md
- **blob** (`blob`): 48428cf787b919f44245d584729ffdc62b6a1857

#### S12

- **ID** (`id`): S12
- **title** (`title`): R03 공통 시험 계약
- **commit** (`commit`): b220a6e6777928ab81c8a0852608b83f3838ff47
- **path** (`path`): prototype/lesson-registration/test-harness/CONTRACT.md
- **limit** (`limit`): T1~T6, 변경하지 않음; release 미확인
- **url** (`url`): https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/prototype/lesson-registration/test-harness/CONTRACT.md
- **blob** (`blob`): f93daf71aebc1a4272739956c7753968e7655d5b

### decisions

- DC1 · 원본의 불변 원문·자료, 등록 요청 내 fact/근거 · R02 최신 조건과 공개 공고 버전 차이, AI의 실제 비용/통보기한 오류(S03) · 원본을 매번 재작성하거나 모든 플랫폼 필드 원본화 · 원문 보존·fact+source/answer locator·필드 매핑; 확인은 최종 승인에 통합. 가격/회차/분/기간/VAT 독립.
- DC2 · 프로필에 실제 입력값 스키마·제약·절차·완료 조건 · 크몽과 숨고 입력 목적/형식 차이(S04,S09,S10) · 공통 enum과 공통 판매 상품 필드로 통일 · 공통 ID 개방, 등록된 profile로 지원·타입 검증. 구체적인 mock 옵션은 가설. 신규 플랫폼 등록으로 확장.
- DC3 · 크몽 패키지의 누락 화면 항목 및 모집 형태·지역·이미지 목록 · S04 401~426, S10 24~37 · V3 시간·금액만, 단일 이미지·자유 지역 · 필수 화면 항목을 계약에 포함. 정확 옵션·단일 mode는 별도 확인. 실제 사용자 가격을 fixture로 덮지 않음.
- DC4 · 숨고 서비스 설정과 고수 프로필/견적 분리 · S08,S09 130~157,S10 93~123 · 숨고를 크몽 상품 등록과 같은 데이터로 강제 · MIDI 선택형 프로필 후보, 가격/사진 강제 없음. 신규 고수 등록/실제 목표 미확정 보존.
- DC5 · 인증 결과의 내부 연결 바인딩을 승인 범위에 포함 · LD-06, V3 P1 결함, S11 세션 안전성 · 외부 계정 ID만 비교 또는 별도 인증 관리 서비스 · 연결 참조+확인 세대+account. 실제 세션 비밀은 EXEC 내부. 승인 검증/worker lease 분리.
- DC6 · 관측 대상·방법·근거 연결과 프로필별 완료 조건 · S04 L26~28,S07,S09,S11, V3 P2 · 클릭 완료=성공 또는 모든 프로필 독립 재조회 강제 · 두 mock은 독립 readback; 확장 profile은 신뢰 가능한 응답도 가능. 제출/저장/게시 구분.
- DC7 · 준비 완료는 검증의 계산값, 검사 책임 명시 · LD-05/08,S03 사실 충돌,V3 P4 · ready 임의 저장 또는 JSON shape만 검증 · 필수/규칙/근거/원본값 체크, blocking issue. UI에는 계산한 ready 반환. 관계/실행 검사 별도 업무 코드.
- DC8 · 기존 API 경계 유지, 세부 기술·미확인 항목만 보류 · 독립 T1~T6 계약 S12, phase · 팀원 작업 변경 및 전면 구현 기술 확정 · 공통 상세 의미와 mock contract 현재 결정; 통합/실제 규칙 근거에 따라 profile만 조정.

### logical_records

- Source · source&#95;id · SourceInput/SourceView; immutable source, raw&#95;text, asset&#95;refs, previous&#95;source&#95;id?, created&#95;at · PREP creates; CO owner-scoped reuse; no independent confirmation endpoint
- Profile · profile ref · Profile + registry value&#95;schema/value&#95;defs + rule/step/goal content · KNOW creates versioned profiles; PREP/EXEC/RESULT same immutable content
- Registration · registration&#95;id · Preparation, AuthOutput/ConnectionBinding, Scope/AcceptedScope, progress, ExecutionReport, Result · CO owns lifecycle; PREP prepares, EXEC verifies/runs, RESULT evaluates; no new entity count

### fact_paths

- lesson.package · SourcePackage · S03 107~115 · one fact per actual package; VAT basis unknown until explicit confirmation
- lesson.subjects · string&#91;&#93; · S03/S04/S09 · source category intent, not platform option ID
- lesson.description · string · S03 · lesson scope not invented
- lesson.included · string&#91;&#93; · S03 116 · in-session recording/basic mix/mastering
- lesson.additional&#95;fees · string · S03 117 · separate production/release consultation; no free assumption
- lesson.reschedule · string · S03 118 · no fixed notice period
- lesson.cancel&#95;no&#95;show · string · S03 119 · same-day cancellation/no-show counts
- lesson.first&#95;visit · string · S03 120 · free consultation/test recording, not priced trial
- lesson.delivery · string · S03 121 · studio face-to-face, no travel/online inference
- lesson.group&#95;size · integer positive · S03 121 · one-to-one
- lesson.location · string or structured region · S03/S04/S09 · explicit public region/address approval
- lesson.preparation · string · S03 122 · no mandatory materials; optional reference
- lesson.curriculum · string · S03 115 · tailored not invented 4-class schedule
- lesson.media · asset ref or refs · S04/S10 · rights + exact bytes/digest
- lesson.package&#95;options · object · S04 421~426 · platform-specific package title/description/work days/revision count user choice or source
- lesson.daw&#95;tools · string&#91;&#93; · S09 · user-authorized support filters
- lesson.goals · string&#91;&#93; · S09 · user-authorized support filters
- lesson.skill · string · S09 · user-authorized support filter
- lesson.age · string&#91;&#93; · S09 · user-authorized support filters
- lesson.gender · string&#91;&#93; · S09 · user-authorized support filters

### boundaries

- B01 · KNOW→CO/PREP/EXEC/RESULT · ProfileRef / Profile · resolve registered profile incl value contract, evidence and goal; pin profile; unregistered/mismatched/unknown live deny
- B02 · CO→PREP→CO · PrepareInput → Preparation · facts with source/answer evidence; validate platform values, blocking issues and exact commercial values; ready computed
- B03 · CO→EXEC→CO · AuthInput → AuthOutput · verified branch must include target+ConnectionBinding, same account and generation; keep internal only
- B04 · CO→EXEC · ExecuteInput(AcceptedScope) · immutable scope incl connection, profile, values, provenance, source/target and approval digest; runtime resolves pinned verified connection and acquires exclusive worker lease; lease generation is separate from verified auth generation
- B05 · EXEC→RESULT · ExecutionReport + trusted EvidenceRecord&#91;&#93; · each observation/evidence binds registration, target, method, operation; goal fields observed not copied from approved input; profile requires proof
- B06 · RESULT→CO · Result · goal verdict, effects/evidence, error, next&#95;action; CO controls job terminal state, result does not reopen job

### semantic_checks

- V01 · CO/PREP · validate source raw or asset; owner; source immutability, rights flagged; no unsupported type/secret. Each current Fact origin kind=source locates immutable source or answer locates accepted answer; references checked by PREP. Source text interpretation not fully machine-provable.
- V02 · KNOW · match exact profile identity including platform/object/version/digest/environment; registry selector allowlist; compose profile value schema, check fields/bindings/goal references, duplicate IDs. Unknown profile deny; no arbitrary URL fetch.
- V03 · PREP · profile-specific values validation. Mock K conditional region and approved disclosure, category/path and dropdown fixture membership; exact tiers and distinct options, image rights/metadata/approved assets; no foreign fields; S no image/price, allowed options only.
- V04 · PREP · all values map to existing fact refs via JSON Pointer paths, all fact origins verified; unresolved required issues or invalid rule =&gt; ready false. Required missing/unknown/conflict never guessed; free text semantics checked from source and final review, cannot prove meaning using a schema. User answers only current issue scope; optional unsupported values omitted.
- V05 · PREP · for each Kmong /packages/i, linked SourcePackage with vat&#95;basis=included must match minutes, sessions, period and total amount (direct or explicitly user-decided VAT-inclusive replacement fact); preserve original fact and decision; unknown VAT blocks. Work&#95;days/revision&#95;count/title/description require explicit source/answer option facts; do not infer from number of sessions. User-selected tier must map actual package. R03 equal 300k fixture is independent synthetic regression only.
- V06 · CO/EXEC · review/start checks current revision, pinned scope and exact connection&#95;ref/verified&#95;generation/account+target, profile, permission, stable effect key. Start atomic immutable accept/idempotency ledger. EXEC checks current authorized connection and exclusive worker lease; same account alone insufficient. No public runtime handle/token. Worker lease generation may change independently of verified auth binding.
- V07 · EXEC · each potentially mutating operation uses stable logical operation ID+target tuple+binding, admitted durably before dispatch; no duplicate/unknown retry. Read step is scoped. Any unexpected error/condition loss after start =&gt; stopping→stopped, pending becomes unknown if absence not proven; no user cancel/resume/rollback.
- V08 · RESULT · goal observation must match trusted evidence record and exact approved target/profile goal/method/state, observed canonical payload digest (from actual readback, not approved-input copy), asset digests if required; all required steps and effects verified; no unknown effect for done. If insufficient evidence =&gt; unknown, not&#95;reached only known no goal-capable effect or authoritative absence. Preserve error/unknown and late proof, not reopen.
- V09 · CO · state and response invariants: prestart ready is derived, unsupported/blocked never ready; review only ready+verified+new; terminal result required and done confirmed; stopped never resumes. Owner-only data/public evidence redaction. GET no external mutation.

### wire_compatibility

- **routes** (`routes`)
  - **[0] H1**
    - **ID** (`id`): H1
    - **method** (`method`): POST
    - **path** (`path`): /v1/sources
    - **input** (`input`): SourceInput
    - **output** (`output`): SourceView
    - **flow** (`flow`): F1
    - **purpose** (`purpose`): create immutable snapshot/upload materials
    - **success** (`success`): `201`
  - **[1] H2**
    - **ID** (`id`): H2
    - **method** (`method`): GET
    - **path** (`path`): /v1/sources
    - **input** (`input`): ListQuery
    - **output** (`output`): SourceList
    - **flow** (`flow`): F1
    - **purpose** (`purpose`): reuse list
    - **success** (`success`): `200`
  - **[2] H3**
    - **ID** (`id`): H3
    - **method** (`method`): GET
    - **path** (`path`): /v1/sources/{id}
    - **input** (`input`): `null`
    - **output** (`output`): SourceView
    - **flow** (`flow`): F1
    - **purpose** (`purpose`): view chosen source
    - **success** (`success`): `200`
  - **[3] H4**
    - **ID** (`id`): H4
    - **method** (`method`): POST
    - **path** (`path`): /v1/registrations
    - **input** (`input`): RegistrationInput
    - **output** (`output`): RegistrationView
    - **flow** (`flow`): F1/F2
    - **purpose** (`purpose`): resolve and prepare; no separate draft resource
    - **success** (`success`): `201`
  - **[4] H5**
    - **ID** (`id`): H5
    - **method** (`method`): PATCH
    - **path** (`path`): /v1/registrations/{id}
    - **input** (`input`): PreparationEdit
    - **output** (`output`): RegistrationView
    - **flow** (`flow`): F2
    - **purpose** (`purpose`): answer necessary questions or revise before acceptance
    - **success** (`success`): `200`
  - **[5] H6**
    - **ID** (`id`): H6
    - **method** (`method`): POST
    - **path** (`path`): /v1/registrations/{id}/authentication
    - **input** (`input`): AuthCommand
    - **output** (`output`): AuthResponse
    - **flow** (`flow`): F3
    - **purpose** (`purpose`): auth lifecycle and target check; viewer transport not business API
    - **success** (`success`): `200`
  - **[6] H7**
    - **ID** (`id`): H7
    - **method** (`method`): POST
    - **path** (`path`): /v1/registrations/{id}/start
    - **input** (`input`): StartInput
    - **output** (`output`): RegistrationView
    - **flow** (`flow`): F4/F5
    - **purpose** (`purpose`): atomic approval/accept; returns tracked request/job, async execution is product behavior
    - **success** (`success`): `202` · `200`
  - **[7] H8**
    - **ID** (`id`): H8
    - **method** (`method`): GET
    - **path** (`path`): /v1/registrations/{id}
    - **input** (`input`): `null`
    - **output** (`output`): RegistrationView
    - **flow** (`flow`): F6
    - **purpose** (`purpose`): stored prep/progress/result; read-only
    - **success** (`success`): `200`
  - **[8] H9**
    - **ID** (`id`): H9
    - **method** (`method`): GET
    - **path** (`path`): /v1/registrations
    - **input** (`input`): ListQuery
    - **output** (`output`): RegistrationList
    - **flow** (`flow`): F6
    - **purpose** (`purpose`): return to existing request/result list
    - **success** (`success`): `200`
- **ports** (`ports`)
  - **[0] I1**
    - **ID** (`id`): I1
    - **caller** (`caller`): CO
    - **provider** (`provider`): KNOW
    - **input** (`input`): selector:string
    - **output** (`output`): ResolveOutput
    - **error** (`error`): unsupported/blocked is a value, not runtime error
  - **[1] I2**
    - **ID** (`id`): I2
    - **caller** (`caller`): CO
    - **provider** (`provider`): PREP
    - **input** (`input`): PrepareInput
    - **output** (`output`): Preparation
    - **error** (`error`): blocking issues or typed model/runtime error before accept; no fabricated fields
  - **[2] I3**
    - **ID** (`id`): I3
    - **caller** (`caller`): CO
    - **provider** (`provider`): EXEC
    - **input** (`input`): AuthInput
    - **output** (`output`): AuthOutput
    - **error** (`error`): prestart error only, revoke invalid viewer grant; no target proof on unknown account
  - **[3] I4**
    - **ID** (`id`): I4
    - **caller** (`caller`): CO
    - **provider** (`provider`): EXEC
    - **input** (`input`): ExecuteInput
    - **output** (`output`): ExecutionReport
    - **error** (`error`): error stop; durable checkpoints via shared infrastructure; report after operations and goal observation
    - **note** (`note`): accepted.scope.connection carries pinned connection; no independent execution connection argument
  - **[4] I5**
    - **ID** (`id`): I5
    - **caller** (`caller`): CO
    - **provider** (`provider`): RESULT
    - **input** (`input`): EvaluateInput
    - **output** (`output`): Result
    - **error** (`error`): missing required evidence not success; CO closes state; no browser mutation
    - **note** (`note`): trusted stored EvidenceRecord&#91;&#93; provided to evaluator; no client evidence
- **notes** (`notes`): Retain V3 candidate paths and input/output type names from common schema V4. CO maps AuthOutput to AuthResponse without internal connection/target identity or secret; viewer grant only auth open/refresh. Review digest binds internal scope, public ReviewView shows actual values and target label, no internal connection. Schema root must not be used as validation; select named definition. All existing semantic S01~S12 stay except V4 explicitly replaces field shapes, price/VAT meaning, platform enums, and connection/evidence boundaries.

### canonical

- **rule** (`rule`): Use server canonical UTF-8 sorted-key JSON, integer safe range, order arrays, preserve Unicode, SHA256. Profile content excludes self digest; scope digest exact internal Scope; payload digest exact platform values excluding transport-only source/approval/connection refs; when platform observations normalize to canonical values, profile defines same mapping; asset digest list in upload order. Test vectors and implementation must match; no client-supplied hash authority.

### verification_status

- **static** (`static`): subset&#95;reference&#95;shape&#95;checked
- **semantic** (`semantic`): 31&#95;of&#95;31&#95;selected&#95;synthetic&#95;contract&#95;cases&#95;pass
- **product** (`product`): not&#95;run
- **deferred** (`deferred`): actual Kmong dropdown/category/region IDs, single package toggle, live policies/receipt · Soomgo real initial object, new account workflow, category-requiredness/cardinality and save proof · actual independent T1~T6 release/adapter implementation, runtime DB/HTTP/concurrency/permission/lease enforcement · actual user efficiency, physical stack and final integration
- **evidence&#95;ref** (`evidence_ref`): data-contract-validation-v4.json
- **limits** (`limits`): Subset JS shape checker, not standard JSON Schema engine. · Semantic sample checks use synthetic fixtures, trusted origin/evidence lists and expected payload digest supplied by test. Not actual extraction/provenance proof, digest generation, registry selection, database concurrency, runtime permission/session enforcement or real browser execution. · Third platform synthetic sample demonstrates shape/profile extension only, not actual adapter support. · Logical model remains abstract, N=6/7 also examined; actual runtime tests not run.

### non_changes

- No new task, no main/PHASE changes, no live access. Mock rule set explicitly synthetic, exact adapter operations and transport delegated after independent results.

