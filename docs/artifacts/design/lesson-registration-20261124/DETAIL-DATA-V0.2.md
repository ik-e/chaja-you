# L2/L3/L5 · 공통 도메인·데이터 상세 설계

> 2026-11-24 · R01 V0.2 상세 설계 검토 초안. 최종 채택 및 실서비스 실행 승인 아님. [구조화 정본 후보](detail-design-v0.2.json) · [근거·검토 안내](README.md)

V0.1의 FR-01~06, I-01~09, 13개 엔터티를 유지하며 필드·단위·권리·변환의 상세 계약을 제안한다. 실제 DBMS나 ORM, 개인의 실제 계정 및 자료 사용은 채택하지 않는다. 새로운 사실을 만들지 않고 원본/확인된 값/파생값/플랫폼별 추가 결정/합성 fixture를 구분한다.

## D-A. 요구에서 상세 계약으로

| ID | V0.1 연결 | 설계 상세 | 근거 |
| --- | --- | --- | --- |
| DD-01 | FR-01; I-01 | 원본 입력 → 필드별 Fact 후보 → 사용자가 확인하거나 충돌/누락 표기 → 원본 버전 고정. AI 추출은 확인이 아님. 공통 사실과 플랫폼 전용 입력을 분리. | S03,S04,S13 |
| DD-02 | FR-02; I-01,I-09 | 대상·객체별 RuleSnapshot과 매핑을 버전화. 같은 원본이라도 크몽 상품/숨고 서비스 설정/탈잉 클래스는 다른 객체·단위. 미확인 규칙은 실행 불가 또는 가설 표시. | S08,S09,S10 |
| DD-03 | FR-03,FR-04; I-02,I-03 | 자료·원본·규칙·초안·대상·동작·환경·허용을 각각 참조. 새 승인 없이 값 변경/추가 제출 금지. | S03,S05,S11 |
| DD-04 | FR-05,FR-06; I-04~I-08 | 실행 시도, 관측, 결과 판정, 재개 의도를 분리; 모의 접수≠실제 접수≠공개. | S05,S07,S12 |

## D-B. 공통 사실 사전

| ID | 경로 | 논리 타입·단위 | 확인 및 제약 | 근거 |
| --- | --- | --- | --- | --- |
| F01 | source_text | string | 원문 보존, 빈 값 불가. AI 문구는 별도 초안. 개인정보는 필요한 범위만. | S03,S04 |
| F02 | instructor.public_name | string\|null | 공개 활동명. 실제 실명/외부 계정 표시명과 동일하다고 추정 금지. | S08,S10 |
| F03 | lesson.subjects | list<category_intent> | 음악 분야, 제공 대상, 목적; 플랫폼 카테고리 ID로 직접 변환하지 않고 선택 확인. | S03,S09,S10 |
| F04 | lesson.description / teaching_scope | string/list<string> | 수업 내용·제공 범위, 경력·학력 등 사실은 근거와 분리. 임의 성과·경력 생성 금지. | S03,S08 |
| F05 | lesson.audience / goals / skill / age / gender | 각 optional fact | 대상자 문구와 숨고 연령/성별/건반 필터는 다른 의미. 명시 확인 없으면 null, 전체 선택으로 추정 금지. | S09,S10 |
| F06 | lesson.delivery_mode / group_size | enum + integer\|null | in_person/online/hybrid; individual/group 별도. 현재 기준 대면 1:1; 다른 방식은 미확인. | S03,S09 |
| F07 | lesson.location / travel_policy | public_region, private_address_ref?, travel_radius_km? | 공개 지역·주소·출장반경 구분, 상세주소 공개 범위 승인 필요. 대면 작업실 ≠ 출장. | S03,S09,S10 |
| F08 | packages[] | id, minutes_per_session:int>0, sessions_per_period:int>0, period:month/one_off/other, total_price_krw:int>=0 | 각 요금제를 독립 저장. 90/180/270분 월4회 25/40/50만원은 현재 확인값; 세 패키지 동일 금액 강제 금지. VAT 포함 여부 별도 확인. | S03,S04,S10 |
| F09 | included_services / additional_fees | list<fact>, pricing_mode | 수업 내 녹음·기본 믹싱/마스터링 포함; 별도 음원 제작·발매 비용 상담. 무료 포함으로 변환 금지. | S03 |
| F10 | reschedule / cancel_no_show | structured policy + free_text | 고정 사전통보기한 없음; 당일 취소·무단 불참 회차 사용. 임의 2일 전 규정 금지. | S03 |
| F11 | first_visit / preparation | structured fact + list<string> | 무료 상담·테스트 녹음, 준비물 필수 없음·참고곡 등 선택. 유료 체험 상품으로 생성 금지. | S03 |
| F12 | curriculum / service_process | list<item>, text | 수준·목표별 맞춤; 회차별 사실이 없으면 강사에게 질문. 4회 고정 커리큘럼 창작 금지. | S03,S10 |
| F13 | daw_tools / qualification / availability / contact_window | optional list/structured facts | 도구·자격·근무시간 미확인 시 null. 연락 가능 시간은 공개 연락처와 별도. | S09,S10 |
| F14 | media_refs[] | asset_ref+version | 원본 이미지, 공개 허용·권리, MIME·크기·해상도·digest, 변환 파생 관계. 외부 URL/연락처·제3자 정보 확인. | S03,S10,S11 |
| F15 | platform_specific_inputs | platform+object_kind+field_key -> fact_ref/value | 크몽 작업기간·수정횟수·패키지명, 숨고 질문 선택, 탈잉 회차 등 별도 확인. 회차를 작업일로 임의 변환 금지. | S04,S09,S10 |

## D-C. 논리 엔터티 필드와 무결성

| ID | 엔터티 / 키 | 필수 논리 속성 | 무결성·소유 |
| --- | --- | --- | --- |
| E01 | Instructor / instructor_ref | owner_principal_ref, public_profile_ref, created_at | 우리 서비스 소유자; 외부 로그인 비밀번호나 쿠키 없음. |
| E02 | LessonSourceVersion / source_ref+source_version | instructor_ref, source_text_ref, confirmed_at?, status, previous_version?, fact_refs, media_refs | immutable 버전, 수정은 새 버전; 최신 값 참조와 이전 근거 보존. |
| E03 | Fact / fact_ref | source_version, path, value, unit?, provenance_ref, confirmation_state, observed_at?, conflict_refs[] | confirmed/proposed/missing/conflicting/derived; confirmed 사용자 확인; 파생 계산은 입력 fact와 식 기록; null≠0≠빈 문자열. |
| E04 | MediaAssetVersion / asset_ref+asset_version | owner, storage_ref, digest, mime, bytes, width?, height?, rights_state, permitted_use, parent_ref? | 권리 unknown이면 외부 첨부 차단; 합성 fixture와 실제 분리; 변환하면 새 digest·버전. |
| E05 | PlatformRuleSnapshot / platform+object_kind+rule_version | field_rules[], flow_version, outcome_spec, source_refs, checked_at, confidence, scope | reported_observation/official/assumption/unverified 구분; 권한은 별도. 규칙 변경 시 승인 무효. |
| E06 | ExecutionPermission / permission_ref+revision | environment, platform, object_kind, action_set, policy_evidence_ref, status, expires_at? | mock만 현재 허용; live는 default deny; 사용자 승인으로 생성하지 않음. |
| E07 | RegistrationDraftVersion / draft_ref+draft_version | source_version, rule_version, media_versions, target, field_mappings[], issues[], state, content_digest | 각 mapping: field_key,value,unit,fact_refs,transform_id,confirmation_state; 미해결 필수/권리 차단. |
| E08 | Approval / approval_ref | actor, scope_snapshot, digest, approved_at, revoked_at? | source/draft/rule/media/target/environment/actions 버전 및 지문 고정; 동일 버전도 권한 철회 시 차단. |
| E09 | RegistrationIntent / intent_ref | owner, platform, object_kind, target_slot_ref, goal, source_ref, active_job_ref? | 대상 슬롯은 신규 상품 의도 또는 기존 객체 식별자. 내용 수정해도 동일 효과 의도 유지. 사용자 간 독립. |
| E10 | RegistrationJob / job_ref | intent_ref, approval_ref, permission_ref, environment, state, checkpoint, retry_blocked, revision | 한 의도에 진행/unknown 작업이 있으면 신규 부작용 차단. 전이 CAS 또는 동등한 원자적 가드 후보. |
| E11 | ExecutionAttempt / attempt_ref | job_ref, operation_id, step_id, action_digest, approval_scope, permission_revision, status, started_at, completed_at?, error_code? | 부작용 직전 durable 기록; 같은 operation_id 재사용은 이전 시도 조회만; 프로세스 중단 후 in-flight는 unknown. |
| E12 | ObservationEvidence / evidence_ref | job_ref, attempt_ref?, platform, environment, observed_at, kind, observed_fields, redacted_ref?, confidence | 영수증/재조회/폼 값/사용자 확인 구분. 외부 세션, 주민번호, 인증코드, 전체 화면 무조건 저장 금지. |
| E13 | RegistrationResult / job_ref+result_revision | goal, observed_stage, verdict, evidence_refs[], reason_code?, next_action, retry_blocked | append-only 판정 이력. 근거가 부족하면 unknown, 클릭 성공만으로 완료 금지. |
| E14 | PlatformConnection / connection_ref (후보) | owner, platform, environment, session_handle_ref, auth_state, expires_at?, revision | 우리 서비스 로그인과 외부 로그인 분리. 지금은 합성 세션만; 원문 자격증명·토큰 저장 금지. |
| E15 | BrowserLease / lease_ref (후보) | connection_ref, instance_ref, controller, generation, lease_expires_at, state | human/automation/none 상호배타; 임대 재발급 세대 확인. 세션은 데이터 레코드와 분리된 격리 실행 환경. |

## D-D. 검증 및 변환 규칙

| ID | 판정/처리 | 예외 및 근거 |
| --- | --- | --- |
| M01 | confirmed Fact만 사실로 배치; AI 제안은 proposed; 누락은 missing, 충돌은 conflicting. | 미확인 필수 필드에는 사용자 질문. 선택 필드는 미입력 허용 여부 확인. S03 |
| M02 | 가격은 정수 KRW, 기간/회차/분 독립; 월 총액÷회차÷분×60은 파생 시급(유리수)으로만 표기. | 시간 단위/반올림/VAT 때문에 원본과 동등하지 않으면 승인 요청, 반올림으로 총액을 맞춘 척하지 않음. S03,S10 |
| M03 | platform field마다 transform_id와 fact_refs, 규칙 버전, 변환 전후 값 기록. | 글자수 축약은 의미 보존; 없던 경력/가격/정책 만들지 않음. S03,S04 |
| M04 | 이미지는 decode→MIME·바이트·픽셀·권리 검사→필요 시 파생 이미지→미리보기→새 승인. | 규격 출처/허용 오차 미확인 시 질문/가설. 4:3 또는 16:9로 변환해도 내용 잘림·연락처 노출 확인. S10,S11 |
| M05 | 플랫폼 규칙은 observed/official/unknown과 mock فرض(가설)를 별도 태그; 실환경 실행에는 별도 허용·검증. | UI 관측만으로 약관 허용이나 공개 여부 단정 금지. S08~S12 |
| M06 | 사용자 원본 기준 예시: 90/180/270분 × 월4회 250000/400000/500000 KRW. | R03 300000×세 tier는 synthetic_regression으로 분리. R04 예시 임의 수업료/이력 및 R05 예시 150000은 원본이 아님. S03,S04,S08,S10 |

## 적용 경계

저장 후보: 원본·규칙·초안·승인·작업·증거의 논리적 관계는 위 키를 사용한다. 구조화 DB 테이블/JSONB/파일 등의 물리 선택은 LR-D03/04 후. 필요 최소 보존 기간 및 개인정보 삭제/백업 정책은 LR-D06으로 남긴다. 실험 자료는 합성, 권리 확인 이미지와 고정 fixture만 사용한다.
