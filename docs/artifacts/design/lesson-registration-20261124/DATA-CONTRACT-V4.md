# 상세 데이터 계약 V4 · 조사 근거 기반 설계 기준선

- 2026-11-25 / R01 위임 결정 및 검토 근거
- 상위 계약 LD-01~08 유지; 공통 상세 계약 및 두 플랫폼 모의 프로필 결정. 실제 플랫폼 규칙·운영 허용·제품 통합 완료의 승인 아님.
- 정본: [공통 데이터 계약 V4](data-contract-v4.json), [공통 스키마 V4](data-schema-v4.json), [플랫폼별 프로필 V2](platform-profiles-v2.json).

## 설계 결정과 근거

| ID | 결정 | 근거 | 대안 | 채택 이유 및 제한 |
|---|---|---|---|---|
| DC1 | 원본의 불변 원문·자료, 등록 요청 내 fact/근거 | R02 최신 조건과 공개 공고 버전 차이, AI의 실제 비용/통보기한 오류(S03) | 원본을 매번 재작성하거나 모든 플랫폼 필드 원본화 | 원문 보존·fact+source/answer locator·필드 매핑; 확인은 최종 승인에 통합. 가격/회차/분/기간/VAT 독립. |
| DC2 | 프로필에 실제 입력값 스키마·제약·절차·완료 조건 | 크몽과 숨고 입력 목적/형식 차이(S04,S09,S10) | 공통 enum과 공통 판매 상품 필드로 통일 | 공통 ID 개방, 등록된 profile로 지원·타입 검증. 구체적인 mock 옵션은 가설. 신규 플랫폼 등록으로 확장. |
| DC3 | 크몽 패키지의 누락 화면 항목 및 모집 형태·지역·이미지 목록 | S04 401~426, S10 24~37 | V3 시간·금액만, 단일 이미지·자유 지역 | 필수 화면 항목을 계약에 포함. 정확 옵션·단일 mode는 별도 확인. 실제 사용자 가격을 fixture로 덮지 않음. |
| DC4 | 숨고 서비스 설정과 고수 프로필/견적 분리 | S08,S09 130~157,S10 93~123 | 숨고를 크몽 상품 등록과 같은 데이터로 강제 | MIDI 선택형 프로필 후보, 가격/사진 강제 없음. 신규 고수 등록/실제 목표 미확정 보존. |
| DC5 | 인증 결과의 내부 연결 바인딩을 승인 범위에 포함 | LD-06, V3 P1 결함, S11 세션 안전성 | 외부 계정 ID만 비교 또는 별도 인증 관리 서비스 | 연결 참조+확인 세대+account. 실제 세션 비밀은 EXEC 내부. 승인 검증/worker lease 분리. |
| DC6 | 관측 대상·방법·근거 연결과 프로필별 완료 조건 | S04 L26~28,S07,S09,S11, V3 P2 | 클릭 완료=성공 또는 모든 프로필 독립 재조회 강제 | 두 mock은 독립 readback; 확장 profile은 신뢰 가능한 응답도 가능. 제출/저장/게시 구분. |
| DC7 | 준비 완료는 검증의 계산값, 검사 책임 명시 | LD-05/08,S03 사실 충돌,V3 P4 | ready 임의 저장 또는 JSON shape만 검증 | 필수/규칙/근거/원본값 체크, blocking issue. UI에는 계산한 ready 반환. 관계/실행 검사 별도 업무 코드. |
| DC8 | 기존 API 경계 유지, 세부 기술·미확인 항목만 보류 | 독립 T1~T6 계약 S12, phase | 팀원 작업 변경 및 전면 구현 기술 확정 | 공통 상세 의미와 mock contract 현재 결정; 통합/실제 규칙 근거에 따라 profile만 조정. |

## 원문 출처

- S03 [R02 강사 요구·최신 조건](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R02/workspace/2026-11-23_lesson-pain-priority.md) · blob `c1aba280833039a5787b4460d948de231b44e135` · 사용자 진술·회상·최신 확인값, 실측 없음
- S04 [R03 개인 PoC 명세](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/SPEC.md) · blob `7ef82683df7826330ec00a1348b56c7b48973c0f` · 크몽형 모의 실험, 고정 fixture
- S07 [R03 검증 기록](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/verification.json) · blob `5a343dd028889970e2cd64dbf0f2bab4e27a5fb9` · 19 pass 자기 보고, 모의 Skyvern 입력·첨부·영수증; 독립 재실행 아님
- S08 [R04 숨고 업무 흐름](https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24_%EC%88%A8%EA%B3%A0_%EA%B3%A0%EC%88%98%EB%93%B1%EB%A1%9D_%EA%B5%90%EC%9C%A1%EC%8B%A0%EC%B2%AD_%EC%82%AC%EC%9A%A9%EC%9E%90%ED%9D%90%EB%A6%84_%EC%84%9C%EB%B9%84%EC%8A%A4%EC%A0%88%EC%B0%A8_%EC%84%A4%EA%B3%84%EB%B6%84%EC%84%9D%EB%B3%B4%EA%B3%A0%EC%84%9C.md) · blob `0de56aa480c4d207a09f4f9f560d707f8004a979` · 기존 고수 계정 관측 및 제안, 신규 가입·공개 추론 분리
- S09 [R04 화면 보고서](https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24_%EC%88%A8%EA%B3%A0_%EA%B3%A0%EC%88%98%EC%A0%84%ED%99%98_%EB%B0%8F_%EB%93%B1%EB%A1%9D%EC%A0%88%EC%B0%A8_%ED%99%94%EB%A9%B4%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7_%EC%83%81%EC%84%B8%EB%B3%B4%EA%B3%A0%EC%84%9C.md) · blob `4062a83b314fd6db11d4572edfefc8873a367287` · STEP 06~12, 15, 16 보고서 관측; 스크린샷 원본 개별 검증 안 함
- S10 [R05 입력 뼈대](https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-24_platform-input-skeleton.md) · blob `ba0a1f1d6243876929efd4b8aad6cd602570d47a` · 수동 작성 화면·임시저장 보고, 플랫폼별 제약 후보; 실제 자동화 아님
- S11 [R05 기술·권한 조사](https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-23_lesson-technical-feasibility.md) · blob `48428cf787b919f44245d584729ffdc62b6a1857` · 공식/관찰/추정 구분, 운영사 허용 미확인
- S12 [R03 공통 시험 계약](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/prototype/lesson-registration/test-harness/CONTRACT.md) · blob `f93daf71aebc1a4272739956c7753968e7655d5b` · T1~T6, 변경하지 않음; release 미확인

## 데이터와 책임

| 구조 | 식별 | 내용 | 책임 |
|---|---|---|---|
| Source | source_id | SourceInput/SourceView; immutable source, raw_text, asset_refs, previous_source_id?, created_at | PREP creates; CO owner-scoped reuse; no independent confirmation endpoint |
| Profile | profile ref | Profile + registry value_schema/value_defs + rule/step/goal content | KNOW creates versioned profiles; PREP/EXEC/RESULT same immutable content |
| Registration | registration_id | Preparation, AuthOutput/ConnectionBinding, Scope/AcceptedScope, progress, ExecutionReport, Result | CO owns lifecycle; PREP prepares, EXEC verifies/runs, RESULT evaluates; no new entity count |

| ID | 경계 | 전달 타입 | 검증 및 책임 |
|---|---|---|---|
| B01 | KNOW→CO/PREP/EXEC/RESULT | ProfileRef / Profile | resolve registered profile incl value contract, evidence and goal; pin profile; unregistered/mismatched/unknown live deny |
| B02 | CO→PREP→CO | PrepareInput → Preparation | facts with source/answer evidence; validate platform values, blocking issues and exact commercial values; ready computed |
| B03 | CO→EXEC→CO | AuthInput → AuthOutput | verified branch must include target+ConnectionBinding, same account and generation; keep internal only |
| B04 | CO→EXEC | ExecuteInput(AcceptedScope) | immutable scope incl connection, profile, values, provenance, source/target and approval digest; runtime resolves pinned verified connection and acquires exclusive worker lease; lease generation is separate from verified auth generation |
| B05 | EXEC→RESULT | ExecutionReport + trusted EvidenceRecord[] | each observation/evidence binds registration, target, method, operation; goal fields observed not copied from approved input; profile requires proof |
| B06 | RESULT→CO | Result | goal verdict, effects/evidence, error, next_action; CO controls job terminal state, result does not reopen job |

## 플랫폼별 필드와 절차

### kmong.service_listing.mock.v2

| 필드 | 의미 | 필수성 | 규칙 | 근거 |
|---|---|---|---|---|
| title | 서비스 제목 | required | 10~30자, 실제 카운트/허용 문자 재확인 | S04, S10 |
| category_path | 카테고리 | required | 현재 화면의 경로 선택값, 단계 수 가변; 실제 목록/ID 재확인 | S04, S10 |
| description | 서비스 설명 | required | 100~20000자 보고, 금칙문자·공개 정보 제한 | S03, S04, S10 |
| recruitment | 모집 형태 | required | 개인레슨/그룹교육/기업강의 | S04, S10 |
| delivery | 제공 방식 | required | 온라인/오프라인 선택; 복합 조합은 실제 규칙 확인 | S04, S10 |
| region | 지역·상세지역·상세주소 | conditional | 오프라인 시 선택 목록+주소. 공개 범위 확인; mock에서 합성 주소만 | S04, S10 |
| main_images | 메인 이미지 | required | PNG/JPG, 1~4장, 652×488 표기; 정확 규격은 mock 가정 | S04, S10 |
| process | 서비스 제공 절차 | required | 50~20000자 보고; 실제 운영 과정 보존 | S03, S04, S10 |
| preparation | 의뢰인 준비사항 | required | 50~20000자 보고; 필수 준비물 없음 유지 | S03, S04, S10 |
| packages | 가격 정보 | required | 선택한 패키지마다 등급, 제목≤20, 설명≤60, VAT 포함 금액, 작업 기간(일), 수정 횟수, 회당 분, 횟수; 단일/다중 모드 실제 재확인 | S03, S04, S10 |

| 단계 | 업무 | 효과 분류 | 완료 관측 |
|---|---|---|---|
| K1 | 신규 등록 화면 진입 | potential_effect | 계정/신규 대상 일치; 진입 시 draft 생성 여부 미확인 |
| K2 | 기본·상세·지역·절차 입력 | potential_effect | 입력값 대조 |
| K3 | 메인 이미지 첨부 | potential_effect | 첨부 자료 digest 일치 |
| K4 | 패키지 입력 | potential_effect | 등급별 값·단위 대조 |
| K5 | 제출 전 전체 값 대조 | read | 승인된 모든 값 및 첨부 일치 |
| K6 | 모의 심사 접수 1회 | potential_effect | 접수 응답 관측; 응답 단독 성공 판정 금지 |
| K7 | 독립 접수 조회 | read | 동일 대상 receipt ID·payload·asset digest 일치 |

모의 완료 목표: `mock_listing_receipt`; independent_readback. 실제 목표 후보: 심사 접수(상품 식별자+접수 근거); 공개/반려/심사 추적은 별도.

- 합성 가정: only deterministic synthetic option sets; NOT verified live menu values; triple mode from R03 separate regression; R02 reports single STANDARD possible, R05 toggle unknown; single/dual variants require distinct verified profile, do not fabricate extra packages for actual user
- 이번 범위 제외: 상세 이미지/동영상, 선택 체크박스·추가 가격·FAQ/키워드, 커리큘럼 추가정보
- 실제 미확인: 단일 모드/선택 등급, 실제 category/지역/드롭다운 값·허용 글자수/이미지 검증, VAT 포함 여부 및 작업기간/수정횟수 사용자 결정, 접수와 심사 상태 증거·운영사 허용

### soomgo.service_configuration.mock.v2

| 필드 | 의미 | 필수성 | 규칙 | 근거 |
|---|---|---|---|---|
| category | 제공 서비스 | required | 대상 MIDI 서비스의 실제 선택 식별자 재확인 | S08, S09 |
| daw | DAW 요청 필터 | required | 관찰된 선택 목록; cardinality는 mock 가정 | S09 |
| goals | 레슨 목적 | required | 취미/입시/작업 준비 | S09 |
| keyboard | 건반 가능 범위 | required | 가능/코드만/불가; 단일 선택은 mock 가정 | S09 |
| ages | 레슨생 연령대 | required | 관찰된 연령 선택 목록; 추측/전체 자동 선택 금지 | S09 |
| genders | 레슨생 성별 | required | 관찰된 선택 목록; 임의 선택 금지 | S09 |
| format | 레슨 형태 | required | 개인/그룹/온라인/학원 | S03, S09 |
| location_mode | 진행 방식 | required | 무관/강사 작업실/출장/온라인 | S03, S09 |

| 단계 | 업무 | 효과 분류 | 완료 관측 |
|---|---|---|---|
| S1 | 기존 고수의 제공 서비스/신규 category 확인 | read | provider account 및 기존/신규 category 확인 |
| S2 | 서비스 추가·질문지 진입 | potential_effect | category 및 신규 슬롯 일치; 추가 시 저장 효과 여부 미확인 |
| S3 | MIDI 질문지 설정 | potential_effect | 선택값 일치 |
| S4 | 저장 전 대조 | read | 승인된 설정값 일치 |
| S5 | 모의 서비스 설정 저장 1회 | potential_effect | 저장 응답 관측 |
| S6 | 서비스 목록/설정 독립 조회 | read | 동일 category·설정 ID·payload 일치 |

모의 완료 목표: `mock_service_configuration_saved`; independent_readback. 실제 목표 후보: 서비스 추가 및 설정 저장 후보; 공개·검색 노출·견적 수신과 별개.

- 합성 가정: 기존 고수 계정, MIDI 선택지 및 필수/선택 cardinality는 synthetic. 신규 고수 전환·다른 카테고리의 문항·필수성/옵션은 확인 전. 가격/이미지 요구하지 않음.
- 이번 범위 제외: 고수 프로필 자체 편집·포트폴리오, 견적·스마트견적·캐시·정산·결제
- 실제 미확인: 최초 등록 객체 및 신규 고수 선행 조건, 실제 선택 cardinality/필수성, 신규 서비스 추가의 외부 효과·저장/조회·정책 허용


## 검증

[실행 코드](validate-data-contract-v4.mjs), [검증 근거](data-contract-validation-v4.json). 검증 대상은 이전 후보 커밋에 고정되어 있다. 이번 기록은 결과와 상태만 갱신하며 타입/프로필 내용은 변경하지 않는다.

- 공통 정의 참조 217/217, 참조 누락 0; 각 프로필 결합 참조 검사 통과.
- 선택된 합성 정상/비정상/확장 사례 31/31 통과.
- 논리 모델 N=4,5,6,7 탐색 합계 260 상태/584 전이; 선정 불변식 위반 0.
- V3 문제 P1~P4에 대한 상세 계약 변경 및 선택 사례 확인. P5(실제 구현자 연결·통합 가능성)는 실행 근거 필요.

### 검증 한계
- Subset JS shape checker, not standard JSON Schema engine.
- Semantic sample checks use synthetic fixtures, trusted origin/evidence lists and expected payload digest supplied by test. Not actual extraction/provenance proof, digest generation, registry selection, database concurrency, runtime permission/session enforcement or real browser execution.
- Third platform synthetic sample demonstrates shape/profile extension only, not actual adapter support.
- Logical model remains abstract, N=6/7 also examined; actual runtime tests not run.

## 후속 확인 및 위임

- actual Kmong dropdown/category/region IDs, single package toggle, live policies/receipt
- Soomgo real initial object, new account workflow, category-requiredness/cardinality and save proof
- actual independent T1~T6 release/adapter implementation, runtime DB/HTTP/concurrency/permission/lease enforcement
- actual user efficiency, physical stack and final integration

기존 9개 업무 API 후보와 5개 업무 포트 유지. 독립 TASK-043~045 및 T1~T6 하네스 계약 변경 없음. 실제 연동 시 공통 계약과 독립 하네스의 변환 경계를 확인한다. 물리적 저장·프레임워크·실행 기술은 구현 근거를 바탕으로 결정한다.
