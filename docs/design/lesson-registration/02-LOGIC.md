# 논리 설계 및 상태 모델

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## detail-decisions-v2.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-decisions-v2.json) · blob `3c04b85cb9ee45d8aa21b9cfdea0713fe8dc3014`

### id

- LR-DETAIL-DECISIONS-02

### authority

- **actor** (`actor`): R01
- **date** (`date`): 2026-11-24
- **quote** (`quote`): 크게 문제 없어 설계 진행하면 될 것 같아
- **scope** (`scope`): 직전 D1~D5 합의와 합리적 하위 결정 위임. 제품 범위·핵심 사용자 경험 변경, 실제 구현·운영 및 TASK 변경 승인 아님.

### basis

- **[0] **
  - **path** (`path`): top-design-v1.json
  - **blob** (`blob`): 1ed54afd5b541fa3a9d4030267ba65c54729ff2b
- **[1] **
  - **path** (`path`): top-design-amendment-v1.json
  - **blob** (`blob`): ad4f09689896206163dfce72d972281b10075891
- **[2] **
  - **path** (`path`): logical-behavior-v4.json
  - **blob** (`blob`): 80bcaca22e8915f4f8def196e5c829a20ea98c4e
- **[3] **
  - **path** (`path`): detail-contract-v1.json
  - **blob** (`blob`): cdfce1fcfbd443da1d3e16ea030d844132df5cc3
- **[4] **
  - **path** (`path`): platform-profiles-v1.json
  - **blob** (`blob`): 829a9b793b8f8039dc280dfc251f9f9cd8ea786b
- **[5] **
  - **path** (`path`): detail-gate-v1.json
  - **blob** (`blob`): 55c66d285183fb4a8a12041b883c12e7775d12f7

### rules

- 상위 정합성, 제거 시 요구 미충족, 단순 대안 비교, 현재 결정 필요성과 근거 수준. 확정된 D1~D5 아래에서 논리적 의미만 확정; 물리 구조·일정·기술은 필요에 따라 위임.

### decisions

#### D1

- **ID** (`id`): D1
- **결정** (`decision`): 하나의 고정 플랫폼 프로필 버전을 준비/실행/판정이 함께 참조
- **need** (`need`): FR-02/04/05; 서로 다른 규칙으로 준비와 실행이 불일치하면 등록 오류
- **대안** (`alternative`): 각 모듈 규칙 복제 또는 LLM 절차 재생성
- **근거** (`why`): 중복/불일치와 불확실성 감소. 사전 절차 확보 전제에 직접 부합
- **now** (`now`): 컴포넌트 I/O를 고정하는 데 필요
- **상태** (`status`): R01&#95;agreed

#### D2

- **ID** (`id`): D2
- **결정** (`decision`): 원본과 플랫폼 조건을 내부 검사, 불확실한 정보만 질문, 인증 후 한 번 최종 등록 정보 확인 및 실행 승인
- **need** (`need`): FR-01~03; 값과 계정/대상에 대한 명시 승인
- **대안** (`alternative`): 원본·초안·계획별 필수 승인 세 번
- **근거** (`why`): 중복 검수 제거; 원본에 명시된 사실과 사용자 답변/승인으로 근거 유지
- **now** (`now`): 사용자 흐름·요청 경계에 필요
- **상태** (`status`): R01&#95;agreed

#### D3

- **ID** (`id`): D3
- **결정** (`decision`): 준비부터 결과까지 하나의 등록 요청 식별자, 수락 시 불변 실행 범위를 내부 snapshot으로 고정
- **need** (`need`): I1/I2/I5; 승인 범위 고정과 대상별 독립 결과
- **대안** (`alternative`): 원본 외에 별도 Draft/Plan/Approval/Job 관리 API 및 저장소
- **근거** (`why`): 독립적으로 수정·재사용할 계획 업무가 없음; 논리 구분만 유지
- **now** (`now`): API와 저장 계약의 단순한 기준
- **상태** (`status`): R01&#95;agreed&#95;refinement

#### D4

- **ID** (`id`): D4
- **결정** (`decision`): 결과 판정 책임 분리, 신뢰할 수 있는 증거가 충분한 경우 추가 조회 없음; 프로필이 요구할 때만 readback
- **need** (`need`): I4; 클릭 성공과 등록 목표 구분
- **대안** (`alternative`): 모든 플랫폼에 독립 재조회 강제 또는 클릭 성공=완료
- **근거** (`why`): 필요한 증거만 확보. 기존 크몽/숨고 모의 계약은 독립 재조회가 완료 조건이므로 유지
- **now** (`now`): 플랫폼별 완료 계약 정의에 필요
- **상태** (`status`): R01&#95;agreed

#### D5

- **ID** (`id`): D5
- **결정** (`decision`): 업무상 의미 있는 단계와 외부 효과의 실행 전 기록/관측/결과만 보존, 기본 키 관리
- **need** (`need`): I3/FR-05/06; 오류 후 미확인 효과 중복 방지
- **대안** (`alternative`): 모든 클릭/화면 이벤트 로깅 또는 아무 기록 없이 최종 결과만
- **근거** (`why`): 전자는 과다·민감정보 위험, 후자는 응답 유실 시 안전한 판단 불가
- **now** (`now`): 실행 및 결과 최소 계약
- **상태** (`status`): R01&#95;agreed

#### D6

- **ID** (`id`): D6
- **결정** (`decision`): 원본 버전은 독립 재사용, 개별 플랫폼 답변/변환은 그 요청에만 적용; 공통 사실 변경은 명시적인 새 원본 버전
- **need** (`need`): I1/I5; 한 플랫폼의 응답이 다른 등록 내용을 변경하지 않아야 함
- **대안** (`alternative`): 최신 원본 in-place 수정, 모든 플랫폼 자동 반영
- **근거** (`why`): 기존 승인 및 다른 작업 보존. 원본을 선택·수정할 최소 기능만 필요
- **now** (`now`): 동시/순차 재사용 경계
- **상태** (`status`): delegated&#95;design

#### D7

- **ID** (`id`): D7
- **결정** (`decision`): 사용자 HTTP는 원본과 등록 요청 두 업무 자원; 인증 명령은 등록 요청의 하위 동작; 내부 단계/승인/효과 관리 API 없음
- **need** (`need`): FR-01~06; 실제 사용자 상호작용 및 조회만
- **대안** (`alternative`): 15개 개별 자원/기능 API 또는 단일 거대 command API
- **근거** (`why`): 업무 자원 중심으로 수명주기를 단순화하고 인증/시작 권한 경계는 명시
- **now** (`now`): UI/서버 병렬 구현을 위한 계약 필요; 경로명은 변경 가능
- **상태** (`status`): delegated&#95;design&#95;candidate

#### D8

- **ID** (`id`): D8
- **결정** (`decision`): 구체적 DB 테이블/프레임워크/브라우저/배포 선택 미확정
- **need** (`need`): 기능/공통 계약 충족 여부가 우선, 팀 독립 실험 근거 아직 평가 전
- **대안** (`alternative`): 현재 특정 스택과 14개 테이블 강제
- **근거** (`why`): 근거 부족하고 되돌림 비용/담당 자율성 고려; 지금 고정할 이유 없음
- **now** (`now`): 11/27 통합 판단 및 구현자가 계약에 맞춰 선택
- **상태** (`status`): deferred

## logical-behavior-v5.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v5.json) · blob `2c13b86a44b10f7877678509819e97d1d1b72c17`

### id

- LR-LOGICAL-05

### authority

- LR-DETAIL-DECISIONS-02

### scope

- Single registration, fixed profile length parameter; logical state only. User answers only before acceptance. Confirming source separately not required. Actual permission, identity, error and evidence are trusted event preconditions.

### initial

- **source** (`source`): `false`
- **profile** (`profile`): unset
- **prep** (`prep`): missing
- **auth** (`auth`): none
- **target** (`target`): unset
- **review** (`review`): `false`
- **job** (`job`): none
- **effect** (`effect`): clear
- **step** (`step`): `0`

### domains

- **source** (`source`): `false` · `true`
- **profile** (`profile`): unset · supported · unsupported · blocked
- **prep** (`prep`): missing · issues · ready
- **auth** (`auth`): none · human · read · verified · worker
- **target** (`target`): unset · new · existing · ambiguous
- **review** (`review`): `false` · `true`
- **job** (`job`): none · active · stopping · done · stopped
- **effect** (`effect`): clear · pending · unknown · absent
- **step** (`step`): 0..N

### rules

#### source&#95;select

- **ID** (`id`): source&#95;select
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
- **set** (`set`)
  - **source** (`source`): `true`
  - **prep** (`prep`): missing
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): provide immutable source or select existing

#### select&#95;supported

- **ID** (`id`): select&#95;supported
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
- **set** (`set`)
  - **profile** (`profile`): supported
  - **prep** (`prep`): missing
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): registry resolution; unsupported/blocked no execution

#### select&#95;unsupported

- **ID** (`id`): select&#95;unsupported
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
- **set** (`set`)
  - **profile** (`profile`): unsupported
  - **prep** (`prep`): missing
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): registry resolution; unsupported/blocked no execution

#### select&#95;blocked

- **ID** (`id`): select&#95;blocked
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
- **set** (`set`)
  - **profile** (`profile`): blocked
  - **prep** (`prep`): missing
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): registry resolution; unsupported/blocked no execution

#### prepare&#95;issues

- **ID** (`id`): prepare&#95;issues
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
  - **source** (`source`): `true`
  - **profile** (`profile`): supported
- **set** (`set`)
  - **prep** (`prep`): issues
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): unresolved required fields or validation issues

#### prepare&#95;ready

- **ID** (`id`): prepare&#95;ready
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
  - **source** (`source`): `true`
  - **profile** (`profile`): supported
- **set** (`set`)
  - **prep** (`prep`): ready
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): confirmed by source or explicit answers, valid under profile; AI proposal not proof

#### answer&#95;or&#95;edit

- **ID** (`id`): answer&#95;or&#95;edit
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): none · verified
  - **source** (`source`): `true`
  - **profile** (`profile`): supported
- **set** (`set`)
  - **prep** (`prep`): missing
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): revalidate after answer/edit, invalidate old review

#### auth&#95;open

- **ID** (`id`): auth&#95;open
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
  - **auth** (`auth`): none
- **set** (`set`)
  - **auth** (`auth`): human
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): direct authentication only

#### auth&#95;finish

- **ID** (`id`): auth&#95;finish
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): human
- **set** (`set`)
  - **auth** (`auth`): read
- **근거** (`why`): fence human input

#### auth&#95;close

- **ID** (`id`): auth&#95;close
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): human · read · verified
- **set** (`set`)
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): prestart abandon only

#### auth&#95;invalid

- **ID** (`id`): auth&#95;invalid
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): human · read · verified
- **set** (`set`)
  - **auth** (`auth`): none
  - **target** (`target`): unset
  - **review** (`review`): `false`
- **근거** (`why`): unverified or expired; no stale review

#### target&#95;new

- **ID** (`id`): target&#95;new
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): read
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
- **set** (`set`)
  - **auth** (`auth`): verified
  - **target** (`target`): new
  - **review** (`review`): `false`
- **근거** (`why`): stable identity and registered target evidence

#### target&#95;existing

- **ID** (`id`): target&#95;existing
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): read
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
- **set** (`set`)
  - **auth** (`auth`): verified
  - **target** (`target`): existing
  - **review** (`review`): `false`
- **근거** (`why`): stable identity and registered target evidence

#### target&#95;ambiguous

- **ID** (`id`): target&#95;ambiguous
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): none
  - **auth** (`auth`): read
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
- **set** (`set`)
  - **auth** (`auth`): verified
  - **target** (`target`): ambiguous
  - **review** (`review`): `false`
- **근거** (`why`): stable identity and registered target evidence

#### make&#95;review

- **ID** (`id`): make&#95;review
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): none
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
  - **auth** (`auth`): verified
  - **target** (`target`): new
- **set** (`set`)
  - **review** (`review`): `true`
- **근거** (`why`): stored exact values/target/profile/goal, no separate plan object

#### accept

- **ID** (`id`): accept
- **actor** (`actor`): USER
- **when** (`when`)
  - **job** (`job`): none
  - **prep** (`prep`): ready
  - **profile** (`profile`): supported
  - **auth** (`auth`): verified
  - **target** (`target`): new
  - **review** (`review`): `true`
  - **effect** (`effect`): clear
  - **step** (`step`): `0`
- **set** (`set`)
  - **job** (`job`): active
- **근거** (`why`): explicit start, revision/digest/key/target guard and immutable scope atomically

#### worker

- **ID** (`id`): worker
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): active
  - **auth** (`auth`): verified
  - **effect** (`effect`): clear
  - **step** (`step`): ltN
- **set** (`set`)
  - **auth** (`auth`): worker
- **근거** (`why`): exclusive authorized runtime control

#### admit

- **ID** (`id`): admit
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): active
  - **auth** (`auth`): worker
  - **effect** (`effect`): clear
  - **step** (`step`): ltN
- **set** (`set`)
  - **effect** (`effect`): pending
- **근거** (`why`): current guard plus durable stable operation key

#### operation&#95;proven

- **ID** (`id`): operation&#95;proven
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): active
  - **auth** (`auth`): worker
  - **effect** (`effect`): pending
  - **step** (`step`): ltN
- **set** (`set`)
  - **step** (`step`): inc
  - **effect** (`effect`): clear
- **근거** (`why`): accepted evidence; advance only once

#### goal&#95;proven

- **ID** (`id`): goal&#95;proven
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): active
  - **auth** (`auth`): worker
  - **effect** (`effect`): clear
  - **step** (`step`): eqN
- **set** (`set`)
  - **job** (`job`): done
  - **auth** (`auth`): none
- **근거** (`why`): profile-specific proof; extra readback only if required

#### error&#95;effect&#95;absent

- **ID** (`id`): error&#95;effect&#95;absent
- **actor** (`actor`): TRUSTED&#95;OBSERVATION
- **when** (`when`)
  - **job** (`job`): active
  - **effect** (`effect`): pending
- **set** (`set`)
  - **job** (`job`): stopping
  - **auth** (`auth`): none
  - **effect** (`effect`): absent
- **근거** (`why`): system error with effect absence evidence

#### error&#95;detected

- **ID** (`id`): error&#95;detected
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): active
- **set** (`set`)
  - **job** (`job`): stopping
  - **auth** (`auth`): none
- **근거** (`why`): actual error or loss of conditions, trusted system event only

#### finish&#95;stop&#95;pending

- **ID** (`id`): finish&#95;stop&#95;pending
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): stopping
  - **effect** (`effect`): pending
- **set** (`set`)
  - **job** (`job`): stopped
  - **effect** (`effect`): unknown
- **근거** (`why`): preserve uncertainty

#### finish&#95;stop&#95;other

- **ID** (`id`): finish&#95;stop&#95;other
- **actor** (`actor`): SYSTEM
- **when** (`when`)
  - **job** (`job`): stopping
  - **effect** (`effect`): clear · absent · unknown
- **set** (`set`)
  - **job** (`job`): stopped
- **근거** (`why`): preserve prior effects

### notes

- profile and source revisions are abstracted; every prestart edit invalidates auth/target/review
- review true represents server scope preview, not approval; accept atomically confirms and freezes scope
- N is profile procedure length; every step modeled conservatively as potentially mutating; read-only steps may use same guard without effect risk in implementation
- terminal states immutable; later evidence append independent of lifecycle
- external authorization/lease and actual error event trust are required at runtime, not proved by reachability

