# V0.6 구체 대상 유형 및 항목 규격

기획안 기준 검토 초안. 상위 분류는 직접 동작 대상이 아니다. 아래 각 구체 유형은 V0.5의 생성/동일성/변경/종료 규칙을 상속하며 세부 식별 기준을 추가한다. 실제 저장소 구조와 UI는 결정하지 않는다.

[기계 판독용 정본](../../artifacts/planning/lesson-registration-20261126/integrated/typed-domain-v0.6/domain.json)

## 1. 구체 유형 전체

| 상위 | 구체 유형 ID | 명칭 | 식별 기준 | 정의 | 필수 의미 인자 |
|---|---|---|---|---|---|
| ACCOUNT | ACCOUNT.SERVICE | 찾아you 계정 | 계정 ID | 서비스 인증 상태와 소유 정보의 귀속 기준. 외부 계정이나 자연인과 동일시하지 않는다. | account_id, account_status |
| SESSION | SESSION.SERVICE | 찾아you 로그인 세션 | 서비스 세션 ID | 서비스 계정에 대한 로그인 접근을 유지한다. | account_id, session_id, expires_at |
| AUTH_ATTEMPT | AUTH.SERVICE_LOGIN | 서비스 로그인 인증 시도 | 시도 ID | 기존 서비스 계정의 본인 인증을 한 번 시작한 사건. | attempt_id, account_candidate, result |
| AUTH_ATTEMPT | AUTH.SERVICE_SIGNUP | 서비스 가입 인증 시도 | 시도 ID | 신규 서비스 계정 가입에 필요한 인증 시도. | attempt_id, signup_request_id, result |
| AUTH_ATTEMPT | AUTH.SERVICE_RECOVERY | 서비스 계정 복구 인증 시도 | 시도 ID | 기존 계정의 접근 복구를 위한 신원 확인 시도. | attempt_id, account_candidate, result |
| AUTH_ATTEMPT | AUTH.EXTERNAL_LOGIN | 외부 로그인 인증 시도 | 시도 ID 및 플랫폼 | 업무 목적의 공식 외부 계정 인증을 한 번 시작한 사건. | attempt_id, platform_id, task_id, account_candidate, result |
| LESSON | LESSON.SAVED | 저장 레슨 정보 | lesson_id | 강사가 새 정보로 저장한 하나의 재사용 정보 집합. 같은 ID는 수정 후에도 동일하고, 내용이 같은 새 저장은 다른 ID. | lesson_id, owner_account_id, version, field_values, material_uses |
| EDIT | EDIT.NEW_LESSON | 신규 레슨 편집 내용 | edit_id | 아직 저장 레슨 정보 ID가 확정되지 않은 신규 작성값. 최초 저장 전에는 LESSON.SAVED가 아님. | edit_id, owner_account_id, field_values, material_uses |
| EDIT | EDIT.EXISTING_LESSON | 기존 레슨 편집 내용 | edit_id, lesson_id | 기존 레슨 정보의 지정 기준 버전에 대해 저장 전인 수정값. | edit_id, lesson_id, base_version, field_changes, material_changes |
| EDIT | EDIT.TASK_INPUT | 업무 입력안 편집 내용 | edit_id, task_id, input_version | 한 업무의 아직 반영되지 않은 입력안 수정값. 레슨 기본값 수정과 구별. | edit_id, task_id, input_version, field_changes |
| FIELD_DEF | FIELD.SPEC | 정보 항목 규격 | field_id, spec_version | 소속 대상·항목 의미·형식·단위·적용 범위가 명시된 정의. 필드 규격 목록에서만 유효. | field_id, owner_type, meaning, value_type, unit, spec_version |
| FIELD_VALUE | VALUE.LESSON | 저장 레슨 항목값 | lesson_id, field_id, item_key(필요한 항목만) | 현재 LESSON.SAVED 안의 특정 항목값. 편집값·플랫폼 적용값과 다름. | lesson_id, field_id, value, origin, review, version |
| FIELD_VALUE | VALUE.LESSON_EDIT | 레슨 편집 항목값 | edit_id, field_id, item_key | EDIT.NEW_LESSON 또는 EDIT.EXISTING_LESSON에 제공된 값. 저장 효과 없음. | edit_id, field_id, value, origin, review |
| FIELD_VALUE | VALUE.TASK_INPUT | 외부 입력안 항목값 | task_id, input_version, field_id, item_key | 특정 외부 대상에 입력할 예정값. 정확 플랫폼 필드 규격이 필요. | task_id, input_version, field_id, value, origin, review |
| FIELD_VALUE | VALUE.TASK_EDIT | 외부 입력안 편집 항목값 | edit_id, field_id, item_key | EDIT.TASK_INPUT의 미반영 변경값. | edit_id, field_id, value |
| FIELD_VALUE | VALUE.EXTERNAL_OBSERVED | 외부 조회 항목값 | observation_id, field_id, item_key | 특정 읽기에서 확보된 외부 저장값·공개값·상태값 중 위치가 명시된 값. | observation_id, external_ref, field_id, location, value, evidence |
| MATERIAL | MATERIAL.TEXT | 제공 텍스트 | material_id | 강사가 붙여넣거나 제공한 설명 텍스트 자체. | material_id, text, origin |
| MATERIAL | MATERIAL.IMAGE | 제공 이미지 | material_id | 이미지 자료 자체. 대표/본문/프로필은 사용 관계의 용도. | material_id, content_ref, media_type |
| MATERIAL | MATERIAL.VIDEO | 제공 영상 | material_id | 동영상 자료 자체. | material_id, content_ref, media_type |
| MATERIAL | MATERIAL.AUDIO | 제공 음원 | material_id | 음원 자료 자체. | material_id, content_ref, media_type |
| MATERIAL | MATERIAL.DOCUMENT | 제공 문서 | material_id | 설명 자료 파일. 인증 비밀·공식 신분 증빙 수집 대상 아님. | material_id, content_ref, media_type |
| MATERIAL | MATERIAL.URL | 제공 링크 | material_id | 강사가 제공한 URL 자체. 링크 대상의 내용이나 권리를 보장하지 않음. | material_id, url, origin |
| MATERIAL_USE | USE.LESSON_EDIT | 레슨 편집 자료 사용 관계 | edit_id, material_id, purpose_code | 신규 또는 기존 레슨 편집 내용에서 특정 용도의 자료 사용. | edit_id, material_id, purpose_code |
| MATERIAL_USE | USE.LESSON_SAVED | 저장 레슨 자료 사용 관계 | lesson_id, material_id, purpose_code | 저장 레슨 정보에서 특정 용도의 자료 사용. | lesson_id, material_id, purpose_code |
| MATERIAL_USE | USE.INPUT_SET | 입력안 자료 사용 관계 | task_id, input_version, field_id, material_id | 정확 외부 첨부 입력 항목에 자료를 사용할 예정인 관계. | task_id, input_version, field_id, material_id |
| RIGHTS | RIGHTS.USE | 자료 사용 권한 진술 | material_id, purpose_code, decision_id | 정확 자료·용도에 대한 사용 권한의 사용자 진술. 권리 존재를 자동 확정하지 않음. | material_id, purpose_code, statement, evidence |
| RIGHTS | RIGHTS.DISCLOSURE | 자료 공개 범위 결정 | material_id, purpose_code, decision_id | 정확 자료·용도에서 공개할 대상 범위에 대한 결정. | material_id, purpose_code, audience, decision_id |
| PLATFORM | PLATFORM.REGISTERED | 조사 대상 플랫폼 | platform_id | 7개 조사 플랫폼 중 정확 하나의 참조. | platform_id, name, source |
| EXT_ACCOUNT | ACCOUNT.EXTERNAL | 외부 계정 참조 | platform_id, verified_account_key | 공식 외부 인증 등으로 식별된 외부 계정. 미식별 후보와 다름. | platform_id, account_key_evidence |
| EXT_TYPE | EXT.TYPE_SPEC | 외부 대상 유형 규격 | native_type_id, spec_version | 정확 플랫폼의 대상 식별 규칙과 관계/항목 규격. 원문 보고와 실재 검증 구분. | native_type_id, identity_rule, field_specs, evidence_refs |
| LESSON_LINK | LINK.LESSON_TARGET | 레슨-외부 모집 대상 연결 | lesson_id, native_target_ref | 저장 레슨 정보와 정확 모집 대상 간 내부 관계. 공유 프로필/게시판만을 모집 단위로 연결하지 않는다. | lesson_id, native_target_ref, identity_evidence |
| ACCOUNT_LINK | LINK.ACCOUNT_EXTERNAL | 서비스-외부 계정 연결 | account_id, external_account_ref | 확인된 외부 계정의 내부 관리 관계. 지속 관리 제품 채택 별도. | account_id, external_account_ref |
| OVERRIDE | OVERRIDE.TASK_FIELD | 이번 업무 적용값 | task_id, field_id, target_path | 현재 TASK에만 적용하는 사용자 지정 항목값. | task_id, field_id, value, decision_id |
| OVERRIDE | OVERRIDE.REUSABLE_FIELD | 재사용 플랫폼 적용값 | lesson_id, platform_id, field_id, account_or_target_scope | 이후 요청에 재사용할 항목값. 별도 제품 채택 및 재사용 조건 확인. | lesson_id, platform_id, field_id, scope, value |
| INPUT_SET | INPUT.CREATE | 신규 외부 객체 생성 입력안 | task_id, input_version | 정확 신규 객체 유형을 생성할 예정값. | task_id, native_type_id, fields, material_uses |
| INPUT_SET | INPUT.ADD_RELATION | 외부 모집 관계 추가 입력안 | task_id, input_version | 정확 공유 상위 객체에 추가할 모집 분야/서비스 관계 값. | task_id, parent_ref, relation_type, fields |
| INPUT_SET | INPUT.UPDATE | 외부 항목 수정 입력안 | task_id, input_version | 정확 기존 대상의 변경할 항목과 예정값. 변경 대상 아닌 항목은 보존. | task_id, native_target_ref, changed_fields |
| INPUT_SET | INPUT.RENEW | 외부 동일 공고 갱신 입력안 | task_id, input_version | 구체 갱신 효과 종류와 필요 인자만 포함. 내용 수정값과 구분. | task_id, post_ref, effect_code, parameters |
| INPUT_SET | INPUT.REVIEW_SUBMISSION | 외부 심사 제출 입력안 | task_id, input_version | 최초 또는 변경안 심사 제출할 정확 내용 버전. | task_id, review_kind, target_ref, content_version |
| QUESTION | QUESTION.MISSING_FIELD | 누락 항목 보완 질문 | question_id, field_id, target_ref | 값이 필요한 특정 항목과 누락 사유를 전달하기 위한 질문. | question_id, target_ref, field_id, reason |
| QUESTION | QUESTION.UNCERTAIN_FIELD | 불확실 항목 보완 질문 | question_id, field_id, target_ref | 추출값/사용자 제공값의 의미·단위·출처가 불명인 질문. | question_id, target_ref, field_id, uncertainty |
| QUESTION | QUESTION.CONSTRAINT_CONFLICT | 제약 충돌 선택 질문 | question_id, conflict_ref | 실제 제공값과 플랫폼 제약이 충돌해 대안 결정을 요청하는 질문. | question_id, conflict_ref, option_refs |
| OPTION | OPTION.CONSTRAINT_VALUE | 제약 충돌 대체값 | question_id, option_id | 사용자가 실제 제공 가능한지 판단할 대체 항목값. | question_id, field_id, proposed_value, scope |
| OPTION | OPTION.FOLLOWUP | 후속 업무 선택지 | issue_id, option_id | 정확 오류에 대해 별도 조회·보완·보류·새 준비 중 허용되는 행동 후보. | issue_id, operation_ref, precondition |
| DECISION | DECISION.FIELD_USE | 항목값 사용 결정 | decision_id, field_slot, value_version | 정확 추출값/입력값을 해당 범위에서 사용할지에 대한 결정. | decision_id, actor, field_slot, value_version, outcome |
| DECISION | DECISION.CONSTRAINT | 제약 충돌 대안 결정 | decision_id, question_id | 정확 대안 선택 또는 전체 대안 거절. | decision_id, question_id, option_id_or_reject |
| DECISION | DECISION.TASK_SCOPE | 업무 대상 선택 결정 | decision_id, request_id | 정확 레슨/플랫폼/업무 종류/외부 대상 범위 선택. 실행 승인 아님. | decision_id, request_id, chosen_refs |
| DECISION | DECISION.INFO_APPROVAL | 외부 적용 정보 승인 | decision_id, task_id, input_version | 정확 외부 입력안 버전 및 적용 자료에 대한 승인/거절. | decision_id, task_id, input_version, outcome |
| DECISION | DECISION.EXEC_APPROVAL | 외부 실행 범위 승인 | decision_id, task_id, goal_refs | 정확 플랫폼·계정·대상·효과 및 읽기 범위 승인/거절. | decision_id, task_id, goals, scope, outcome |
| DECISION | DECISION.RETENTION_APPROVAL | 조건부 인증 유지 승인 | decision_id, monitor_id, setting_version | 특정 자동 조회의 세션 유지 기간·접근 범위에 대한 별도 승인. | decision_id, monitor_id, setting_version, expires_at, outcome |
| DECISION | DECISION.DISCARD_EDIT | 미저장 편집 폐기 결정 | decision_id, edit_id | 저장되지 않은 정확 편집 내용의 폐기 여부. | decision_id, edit_id, outcome |
| DECISION | DECISION.SERVICE_TERMS | 서비스 이용 조건 결정 | decision_id, terms_version | 찾아you 이용 조건에 대한 강사의 결정. | decision_id, account_or_signup_ref, terms_version, outcome |
| DECISION | DECISION.EXTERNAL_TERMS | 외부 약관 결정 | external_evidence, terms_version | 외부 공식 화면에서 본인이 직접 한 동의/거절. 서비스 승인과 다름. | platform_id, account_ref, terms_version, observation_ref |
| EXT_SESSION | SESSION.EXTERNAL_TASK | 일회 업무용 외부 세션 | session_id, external_account_ref, purpose | 기본 실행/조회에 필요한 기간만 사용하는 외부 인증 세션. | session_id, account_ref, task_or_read_scope, expires_at |
| EXT_SESSION | SESSION.EXTERNAL_MONITOR | 조건부 자동 조회 외부 세션 | session_id, monitor_id, external_account_ref | 별도 승인과 조건에 따라 자동 읽기만 수행하는 세션. | session_id, monitor_id, account_ref, scope, expires_at |
| PERMISSION | PERMISSION.INTERNAL | 내부 정보 접근 권한 근거 | account_id, target_ref, action_code, evidence | 서비스 자체 데이터 접근 권한 판정 근거. | account_id, target_ref, action_code, evidence |
| PERMISSION | PERMISSION.EXTERNAL | 외부 계정 업무 권한 근거 | external_account_ref, native_target_ref, effect_code, evidence | 외부 계정이 정확 대상에 해당 업무를 수행할 권한 근거. | external_account_ref, native_target_ref, effect_code, evidence |
| ATTEMPT | ATTEMPT.EXTERNAL_WRITE | 외부 쓰기 시도 | attempt_id, goal_id | 정확 승인된 외부 변화 동작을 시도한 사건. 실제 반영과 구분. | attempt_id, goal_id, request_ref, timestamp |
| OBSERVATION | OBS.CONTENT | 외부 내용 조회 | observation_id, target_ref, field_ids | 특정 대상의 저장/공개 내용값을 읽는 시도 및 결과. | observation_id, target_ref, field_ids, result, timestamp |
| OBSERVATION | OBS.STATUS | 외부 상태 조회 | observation_id, target_ref, status_field_ids | 정확 심사/공개/모집 등의 상태 축 읽기. | observation_id, target_ref, status_field_ids, result, timestamp |
| OBSERVATION | OBS.IDENTITY | 외부 식별 조회 | observation_id, platform_id, account_scope | 정확 기존 외부 대상 후보와 식별 근거 조회. | observation_id, platform_id, account_scope, native_type_id, result |
| OBSERVATION | OBS.EFFECT | 외부 효과 확인 조회 | observation_id, goal_id | 정확 목표 효과의 실제 발생 판정에 필요한 근거 확보 시도. | observation_id, goal_id, result, evidence |
| EFFECT_RESULT | RESULT.EXTERNAL_EFFECT | 개별 외부 효과 판정 | goal_id, judgment_id | 목표 효과의 미시도/발생/미발생/불명 판정. 조회 결과나 실행 시도 자체가 아님. | goal_id, judgment_id, outcome, evidence |
| REVIEW | REVIEW.FIRST | 외부 최초 심사 참조 | platform_id, target_ref, external_review_evidence | 특정 최초 심사 사건. 외부 식별 규칙 검증 필요. | target_ref, submission_version, observation_refs |
| REVIEW | REVIEW.REVISION | 외부 변경안 심사 참조 | platform_id, target_ref, external_review_evidence | 특정 변경안 심사 사건. 기존 최초 심사와 동일시 금지. | target_ref, revision_version, observation_refs |
| VERSION | VERSION.LESSON | 레슨 정보 버전 참조 | lesson_id, version_id | 업무에 적용한 레슨 저장값의 식별 근거. | lesson_id, version_id, applied_ref |
| VERSION | VERSION.OVERRIDE | 플랫폼 적용값 버전 참조 | override_slot, version_id | 사용한 정확 플랫폼 적용값의 기준. | override_slot, version_id |
| VERSION | VERSION.INPUT | 입력안 버전 참조 | task_id, version_id | 승인·실행에 적용한 입력안 버전. | task_id, version_id |
| VERSION | VERSION.RULE | 규칙 버전 참조 | rule_id, version_id | 적용한 플랫폼/제품/보안 규칙 버전. | rule_id, version_id |
| RIGHT_REQUEST | RIGHT.DATA_READ | 개인정보 열람 요청 | right_request_id | 정보주체의 정확 데이터 범위 열람 요청. | subject_ref, scope, request_id |
| RIGHT_REQUEST | RIGHT.DATA_CORRECT | 개인정보 정정 요청 | right_request_id | 정확 개인정보 항목의 정정 요청. | subject_ref, scope, corrected_value, request_id |
| RIGHT_REQUEST | RIGHT.DATA_DELETE | 개인정보 삭제 요청 | right_request_id | 정확 개인정보 범위 삭제 요청. | subject_ref, scope, request_id |
| OPS_CASE | OPS.INCIDENT | 서비스 장애 사건 | ops_case_id | 서비스 자체 장애 및 영향 범위. 외부 반려와 구분. | ops_case_id, impact, evidence |
| OPS_CASE | OPS.QUALITY_BREACH | 운영 기준 미달 사건 | ops_case_id, rule_id | 측정된 품질 값의 기준 미달 사건. | ops_case_id, rule_id, measurement, evidence |
| MONITOR | MONITOR.PUBLIC | 공개 정보 자동 조회 설정 | monitor_id, setting_version | 허용된 공개 정보 읽기 조건과 알림 규칙. 인증 세션 불필요. | monitor_id, target_refs, read_fields, schedule, alert_rule |
| MONITOR | MONITOR.AUTHENTICATED | 인증 기반 자동 조회 설정 | monitor_id, setting_version | 별도 승인된 인증 세션을 이용한 읽기 조건과 알림 규칙. | monitor_id, target_refs, read_fields, schedule, alert_rule, retention_approval |
| REQUEST | REQ.SIGNUP | 가입 요청 | request_id | 정확 가입 요청 의도. 가입에 필요한 최소 정보 및 동의 참조. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.RECOVER_ACCOUNT | 계정 복구 요청 | request_id | 정확 계정 복구 요청 의도. 계정 후보 및 복구 인증 참조. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.LOGOUT | 서비스 로그아웃 요청 | request_id | 정확 서비스 로그아웃 요청 의도. 현재 세션 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.CREATE_LESSON | 신규 레슨 저장 요청 | request_id | 정확 신규 레슨 저장 요청 의도. 편집 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.SAVE_LESSON | 기존 레슨 변경 저장 요청 | request_id | 정확 기존 레슨 변경 저장 요청 의도. 레슨 ID, 기준 버전, 편집 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.DELETE_LESSON | 저장 레슨 삭제 요청 | request_id | 정확 저장 레슨 삭제 요청 의도. 레슨 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_LESSON | 저장 레슨 조회 요청 | request_id | 정확 저장 레슨 조회 요청 의도. 정확 레슨 ID 또는 본인 목록 조건. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.DISCARD_LESSON_EDIT | 미저장 레슨 편집 폐기 요청 | request_id | 정확 미저장 레슨 편집 폐기 요청 의도. 편집 ID, 미저장 여부. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.DISCARD_INPUT_EDIT | 미저장 입력안 편집 폐기 요청 | request_id | 정확 미저장 입력안 편집 폐기 요청 의도. 편집 ID, 미반영 여부. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_CREATE | 신규 등록 준비 요청 | request_id | 정확 신규 등록 준비 요청 의도. 레슨 ID, 플랫폼, 정확 신규 대상 유형. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_ADD_RELATION | 모집 관계 추가 준비 요청 | request_id | 정확 모집 관계 추가 준비 요청 의도. 레슨 ID, 플랫폼, 상위 외부 대상, 관계 유형. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_UPDATE | 기존 외부 내용 수정 준비 요청 | request_id | 정확 기존 외부 내용 수정 준비 요청 의도. 레슨 ID, 정확 기존 대상, 변경 항목. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_BUMP | 동일 공고 노출 최신화 준비 요청 | request_id | 정확 동일 공고 노출 최신화 준비 요청 의도. 정확 기존 공고, 효과 코드. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_EXTEND | 동일 공고 기간 연장 준비 요청 | request_id | 정확 동일 공고 기간 연장 준비 요청 의도. 정확 기존 공고, 목표 기간. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.PREPARE_REVIEW | 외부 심사 제출 준비 요청 | request_id | 정확 외부 심사 제출 준비 요청 의도. 정확 외부 객체, 내용 버전, 심사 종류. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.EXECUTE_TASK | 승인 외부 업무 실행 요청 | request_id | 정확 승인 외부 업무 실행 요청 의도. 업무 ID, 정확 목표 효과, 정보/범위 승인. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_EXTERNAL_IDENTITY | 기존 외부 대상 식별 조회 요청 | request_id | 정확 기존 외부 대상 식별 조회 요청 의도. 플랫폼, 외부 계정, 대상 유형, 검색 조건. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_EXTERNAL_CONTENT | 외부 내용 조회 요청 | request_id | 정확 외부 내용 조회 요청 의도. 정확 대상, 항목, 읽기 범위. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_EXTERNAL_STATUS | 외부 상태 조회 요청 | request_id | 정확 외부 상태 조회 요청 의도. 정확 대상, 상태 축, 읽기 범위. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_EXTERNAL_EFFECT | 기존 효과 확인 조회 요청 | request_id | 정확 기존 효과 확인 조회 요청 의도. 정확 목표 효과 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.ADD_LESSON_LINK | 레슨-외부 대상 연결 추가 요청 | request_id | 정확 레슨-외부 대상 연결 추가 요청 의도. 레슨 ID, 정확 외부 모집 대상. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.REMOVE_LESSON_LINK | 레슨-외부 대상 연결 제거 요청 | request_id | 정확 레슨-외부 대상 연결 제거 요청 의도. 정확 관계 ID 또는 양쪽 참조. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.ADD_ACCOUNT_LINK | 외부 계정 연결 추가 요청 | request_id | 정확 외부 계정 연결 추가 요청 의도. 서비스 계정 및 검증 외부 계정. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.REMOVE_ACCOUNT_LINK | 외부 계정 연결 제거 요청 | request_id | 정확 외부 계정 연결 제거 요청 의도. 정확 관계 참조. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.HOLD_TASK | 업무 보류 요청 | request_id | 정확 업무 보류 요청 의도. 업무 ID, 미실행 효과 범위. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.EXCLUDE_TASK | 업무 제외 요청 | request_id | 정확 업무 제외 요청 의도. 수락 전 업무 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.RECONSIDER_TASK | 업무 조건 재검토 요청 | request_id | 정확 업무 조건 재검토 요청 의도. 업무 ID, 변경 조건. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.REPREPARE_REMAINDER | 미발생 효과 새 준비 요청 | request_id | 정확 미발생 효과 새 준비 요청 의도. 미발생 판정 및 지연 실행 방지 근거. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.REVOKE_EXT_ACCESS | 외부 접근 철회 요청 | request_id | 정확 외부 접근 철회 요청 의도. 세션/계정, 목적 범위. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.START_MONITOR | 자동 조회 시작 요청 | request_id | 정확 자동 조회 시작 요청 의도. 설정 버전, 필요 승인. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.CHANGE_MONITOR | 자동 조회 조건 변경 요청 | request_id | 정확 자동 조회 조건 변경 요청 의도. 설정 ID, 변경값, 재승인 조건. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.STOP_MONITOR | 자동 조회 종료 요청 | request_id | 정확 자동 조회 종료 요청 의도. 정확 설정 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.CANCEL_AUTH | 외부 인증 시도 취소 요청 | request_id | 정확 외부 인증 시도 취소 요청 의도. 정확 인증 시도 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.START_AUTH | 외부 인증 시도 시작 요청 | request_id | 정확 외부 인증 시도 시작 요청 의도. 플랫폼, 목적 업무. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.REBUILD_INPUT | 입력안 재구성 요청 | request_id | 정확 입력안 재구성 요청 의도. 업무 ID, 현재 입력/규칙 기준. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_REQUEST | 기존 요청 기록 조회 요청 | request_id | 정확 기존 요청 기록 조회 요청 의도. 동일 요청 ID. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_HISTORY | 업무 이력 조회 요청 | request_id | 정확 업무 이력 조회 요청 의도. 본인 요청 ID 및 기록 종류. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.READ_DRAFT | 외부 미제출 정보 조회 요청 | request_id | 정확 외부 미제출 정보 조회 요청 의도. 정확 외부 미제출 대상 식별; 별도 검토. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.SAVE_DRAFT | 외부 미제출 정보 저장 요청 | request_id | 정확 외부 미제출 정보 저장 요청 의도. 정확 외부 임시저장 종류, 대상/예정값. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.SET_FIRST_SCHEDULE | 외부 최초 모집 일정 지정 요청 | request_id | 정확 외부 최초 모집 일정 지정 요청 의도. 클래스 ID, 일정값. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.SET_REPRESENTATIVE | 외부 대표 서비스 지정 요청 | request_id | 정확 외부 대표 서비스 지정 요청 의도. 고수 프로필과 정확 제공 서비스. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.EXPORT_HISTORY | 업무 이력 다운로드 요청 | request_id | 정확 업무 이력 다운로드 요청 의도. 본인 기록 범위; 채택 미정. | request_id, owner_account_id, target_ref, typed_arguments |
| REQUEST | REQ.INQUIRE_OPS | 운영 장애 상태 확인 요청 | request_id | 정확 운영 장애 상태 확인 요청 의도. 본인 업무와 관련된 사건 참조; 채택 미정. | request_id, owner_account_id, target_ref, typed_arguments |
| TASK | TASK.CREATE | 신규 객체 생성 업무 | task_id, request_id | 정확 플랫폼·신규 대상 유형·생성 입력안. 허용 효과 CREATE_OBJECT. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.ADD_RELATION | 모집 관계 추가 업무 | task_id, request_id | 정확 기존 상위 객체·모집 관계 유형·추가값. 허용 효과 ADD_RELATION. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.UPDATE | 외부 항목값 수정 업무 | task_id, request_id | 정확 기존 외부 대상·변경 필드와 값. 허용 효과 CHANGE_FIELD. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.BUMP | 동일 공고 노출 최신화 업무 | task_id, request_id | 정확 공고·플랫폼 최신화 기능. 허용 효과 BUMP_EXISTING. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.EXTEND | 동일 공고 기간 연장 업무 | task_id, request_id | 정확 공고·기간 목표. 허용 효과 EXTEND_EXISTING. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.REVIEW | 외부 심사 제출 업무 | task_id, request_id | 정확 외부 객체·제출 내용 버전·심사 종류. 허용 효과 SUBMIT_FIRST_REVIEW/SUBMIT_REVISION_REVIEW. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.READ_CONTENT | 외부 내용 읽기 업무 | task_id, request_id | 정확 외부 대상·필드 범위. 허용 효과 READ_CONTENT. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.READ_STATUS | 외부 상태 읽기 업무 | task_id, request_id | 정확 외부 대상·상태 축. 허용 효과 READ_STATUS. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.DRAFT | 외부 임시저장 업무 | task_id, request_id | 외부 임시저장 유형/대상·내용. 허용 효과 SAVE_DRAFT. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.FIRST_SCHEDULE | 외부 최초 모집 일정 업무 | task_id, request_id | 클래스·일정값. 허용 효과 SET_FIRST_SCHEDULE. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| TASK | TASK.REPRESENTATIVE | 외부 대표 서비스 지정 업무 | task_id, request_id | 공유 프로필·서비스 관계. 허용 효과 SET_REPRESENTATIVE. | task_id, request_id, platform_id, external_account_ref_or_unresolved, native_type_or_target_ref, goal_refs |
| GOAL | GOAL.WRITE | 외부 변경 목표 | task_id, goal_id | 정확 외부 변경 효과 코드·대상·변경값과 판정 규칙. 쓰기 효과 코드만 허용. | task_id, goal_id, write_effect_code, target_or_type, expected_change, rule_ref |
| GOAL | GOAL.READ | 외부 읽기 목표 | task_id, goal_id | 정확 외부 읽기 항목 및 관측 결과 확보 목적. 외부 변화 목표가 아니다. | task_id, goal_id, read_effect_code, target_ref, field_ids |
| CHECK | CHECK.INPUT_REQUIRED | 입력 필수값 검사 | check_id, exact_target_ref, rule_version | 정확 입력안 필수 항목의 존재 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.INPUT_FORMAT | 입력 형식 검사 | check_id, exact_target_ref, rule_version | 정확 항목 규격의 값 형식·단위·범위 일치 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.INPUT_SOURCE | 입력값 출처 일치 검사 | check_id, exact_target_ref, rule_version | 사용자 지정 정보 및 적용값과 변환값의 일치 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.INPUT_CONFLICT | 플랫폼 제약 충돌 검사 | check_id, exact_target_ref, rule_version | 실제 제공 조건과 플랫폼 허용 조건의 충돌 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.INTERNAL_ACCESS | 내부 접근 권한 검사 | check_id, exact_target_ref, rule_version | 서비스 계정의 정확 내부 대상 읽기·쓰기 권한. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.EXTERNAL_IDENTITY | 외부 식별 동일성 검사 | check_id, exact_target_ref, rule_version | 정확 플랫폼 계정/객체/관계의 동일성. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.EXTERNAL_PERMISSION | 외부 업무 권한 검사 | check_id, exact_target_ref, rule_version | 외부 계정의 지정 효과에 대한 권한. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.POLICY | 대행 허용 근거 검사 | check_id, exact_target_ref, rule_version | 정확 플랫폼·접근 방식·업무의 허용 근거. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.PRODUCT_SCOPE | 제품 제공 범위 검사 | check_id, exact_target_ref, rule_version | 업무·효과의 채택/단계. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.PROJECT_PERMISSION | 프로젝트 실행 허가 검사 | check_id, exact_target_ref, rule_version | 환경·업무·효과별 허가 범위. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.IMPLEMENTATION | 구현 검증 검사 | check_id, exact_target_ref, rule_version | 정확 구현 버전·업무·효과의 검증 수준. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.APPROVAL_VALID | 사용자 승인 유효성 검사 | check_id, exact_target_ref, rule_version | 현재 대상/값/규칙과 정확 승인 기록 일치 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.DUPLICATE | 중복 실행 위험 검사 | check_id, exact_target_ref, rule_version | 이전 요청 및 기존 외부 효과의 중복 위험. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.DELAY_FENCE | 지연 실행 위험 검사 | check_id, exact_target_ref, rule_version | 이전 동작이 나중에 실행될 가능성 제거 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.EXECUTION | 개별 실행 조건 종합 검사 | check_id, exact_target_ref, rule_version | 정확 목표 효과에 필요한 모든 필수 검사 충족 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.MATERIAL_RIGHT | 자료 사용 권한 검사 | check_id, exact_target_ref, rule_version | 자료·용도에 대한 사용 권한 근거. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.MATERIAL_DISCLOSURE | 자료 공개 범위 검사 | check_id, exact_target_ref, rule_version | 자료·용도에 대한 공개 범위 근거. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.AUTH_RESULT | 인증 결과 검사 | check_id, exact_target_ref, rule_version | 정확 시도 및 공식 인증 결과 일치 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.PREREQUISITE | 외부 선행 요건 검사 | check_id, exact_target_ref, rule_version | 가입·자격·약관·정산 중 지정 요건 충족 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.ACCESS_BLOCKED | 접근 차단 검사 | check_id, exact_target_ref, rule_version | 정확 외부 세션 범위의 이후 접근 차단 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.SESSION_DISCARDED | 세션 폐기 검사 | check_id, exact_target_ref, rule_version | 정확 서비스 관리 외부 세션 재사용 불가 여부. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.INTERNAL_MUTATION | 내부 변경 반영 검사 | check_id, exact_target_ref, rule_version | 동일 요청의 정확 내부 대상에 대한 반영/미반영/불명. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.OBS_CHANGE | 외부 관측값 비교 | check_id, exact_target_ref, rule_version | 동일 외부 대상·항목의 유효한 두 관측의 차이. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.QUALITY | 운영 품질 기준 검사 | check_id, exact_target_ref, rule_version | 정확 운영 측정값과 기준의 비교. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.RIGHT_REQUEST | 개인정보 권리 처리 검사 | check_id, exact_target_ref, rule_version | 정확 권리 요청의 허용 범위 및 처리 결과. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| CHECK | CHECK.RETENTION | 조건부 인증 유지 조건 검사 | check_id, exact_target_ref, rule_version | 정확 설정, 승인, 만료, 허용 읽기 조건. | check_id, target_ref, rule_ref, outcome, evidence, timestamp |
| RULE | RULE.FIELD | 필드 입력 규칙 | rule_id, version | 정확 필드 입력 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.WORKFLOW | 외부 업무 절차 규칙 | rule_id, version | 정확 외부 업무 절차 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.EFFECT_EVIDENCE | 외부 효과 판정 규칙 | rule_id, version | 정확 외부 효과 판정 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.DELEGATION_POLICY | 플랫폼 대행 허용 규칙 | rule_id, version | 정확 플랫폼 대행 허용 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.PRODUCT_SCOPE | 제품 제공 범위 규칙 | rule_id, version | 정확 제품 제공 범위 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.PROJECT_PERMISSION | 프로젝트 실행 허가 규칙 | rule_id, version | 정확 프로젝트 실행 허가 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.PRIVACY | 개인정보 처리 규칙 | rule_id, version | 정확 개인정보 처리 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.QUALITY | 운영 품질 기준 | rule_id, version | 정확 운영 품질 기준의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.SESSION | 인증 세션 사용 규칙 | rule_id, version | 정확 인증 세션 사용 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.IDENTITY | 외부 대상 동일성 규칙 | rule_id, version | 정확 외부 대상 동일성 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| RULE | RULE.DUPLICATE | 중복/재실행 방지 규칙 | rule_id, version | 정확 중복/재실행 방지 규칙의 적용 대상과 판정 조건. 다른 종류의 규칙으로 대체할 수 없음. | rule_id, version, scope, predicate, source_ref |
| EVIDENCE | EVIDENCE.FEATURE_REPORT | 플랫폼 기능 조사 근거 | evidence_id, source, exact_subject, timestamp | 정확 플랫폼 기능 조사 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.FEATURE_TEST | 플랫폼 기능 실재 검증 근거 | evidence_id, source, exact_subject, timestamp | 정확 플랫폼 기능 실재 검증 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.POLICY | 대행 허용 정책 근거 | evidence_id, source, exact_subject, timestamp | 정확 대행 허용 정책 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.PROJECT | 프로젝트 실행 허가 근거 | evidence_id, source, exact_subject, timestamp | 정확 프로젝트 실행 허가 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.IMPLEMENTATION | 구현 검증 근거 | evidence_id, source, exact_subject, timestamp | 정확 구현 검증 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.IDENTITY | 외부 대상 식별 근거 | evidence_id, source, exact_subject, timestamp | 정확 외부 대상 식별 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.PERMISSION | 접근 권한 근거 | evidence_id, source, exact_subject, timestamp | 정확 접근 권한 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.USER_INPUT | 사용자 제공 정보 출처 | evidence_id, source, exact_subject, timestamp | 정확 사용자 제공 정보 출처에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.EXTRACTION | 자료 추출 근거 | evidence_id, source, exact_subject, timestamp | 정확 자료 추출 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.OBSERVATION | 외부 조회 근거 | evidence_id, source, exact_subject, timestamp | 정확 외부 조회 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.EFFECT | 외부 효과 독립 판정 근거 | evidence_id, source, exact_subject, timestamp | 정확 외부 효과 독립 판정 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.SESSION | 인증 및 세션 정리 근거 | evidence_id, source, exact_subject, timestamp | 정확 인증 및 세션 정리 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.MATERIAL_RIGHT | 자료 사용 권리 근거 | evidence_id, source, exact_subject, timestamp | 정확 자료 사용 권리 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVIDENCE | EVIDENCE.OPS | 운영 장애 및 측정 근거 | evidence_id, source, exact_subject, timestamp | 정확 운영 장애 및 측정 근거에만 사용하는 출처 및 확인 방법. 근거의 존재와 주장 확인은 별개. | evidence_id, subject_ref, source_ref, observed_at, method |
| EVENT | EVENT.REQUEST_RECEIVED | 요청 수신 사건 기록 | event_id, exact_subject | 요청 수신 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.REQUEST_ACCEPTED | 요청 수락 사건 기록 | event_id, exact_subject | 요청 수락 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.INTERNAL_APPLIED | 내부 변경 반영 사건 기록 | event_id, exact_subject | 내부 변경 반영 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.INTERNAL_UNKNOWN | 내부 변경 결과 미확인 사건 기록 | event_id, exact_subject | 내부 변경 결과 미확인 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.DECISION_RECORDED | 사용자 결정 기록 사건 기록 | event_id, exact_subject | 사용자 결정 기록 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.DECISION_WITHDRAWN | 사용자 결정 철회 사건 기록 | event_id, exact_subject | 사용자 결정 철회 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.APPROVAL_INVALID | 기존 승인 적용 불가 사건 기록 | event_id, exact_subject | 기존 승인 적용 불가 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.TASK_HELD | 대상별 업무 보류 사건 기록 | event_id, exact_subject | 대상별 업무 보류 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.TASK_EXCLUDED | 대상별 업무 제외 사건 기록 | event_id, exact_subject | 대상별 업무 제외 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.EXTERNAL_ATTEMPT | 외부 쓰기 시도 사건 기록 | event_id, exact_subject | 외부 쓰기 시도 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.OBSERVATION | 외부 조회 결과 사건 기록 | event_id, exact_subject | 외부 조회 결과 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.EFFECT_JUDGMENT | 외부 효과 판정 사건 기록 | event_id, exact_subject | 외부 효과 판정 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.VERSION_CHANGED | 적용 버전 변경 사건 기록 | event_id, exact_subject | 적용 버전 변경 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.TASK_ENDED | 업무 처리 종료 사건 기록 | event_id, exact_subject | 업무 처리 종료 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.NOTICE_DELIVERY | 정보 전달 시도 및 결과 사건 기록 | event_id, exact_subject | 정보 전달 시도 및 결과 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.SESSION_BLOCKED | 외부 접근 차단 사건 기록 | event_id, exact_subject | 외부 접근 차단 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.SESSION_DISCARDED | 외부 인증 세션 폐기 사건 기록 | event_id, exact_subject | 외부 인증 세션 폐기 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.DIRECT_REPORT | 사용자 직접 수행 보고 사건 기록 | event_id, exact_subject | 사용자 직접 수행 보고 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.MONITOR_STARTED | 자동 조회 시작 사건 기록 | event_id, exact_subject | 자동 조회 시작 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.MONITOR_ENDED | 자동 조회 종료 사건 기록 | event_id, exact_subject | 자동 조회 종료 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| EVENT | EVENT.OPS_RESPONSE | 운영 대응 사건 기록 | event_id, exact_subject | 운영 대응 사건의 주체·대상·시점·결과 참조. 다른 사건 유형과 교환 불가. | event_id, subject_ref, actor_ref, timestamp, result_ref |
| NOTICE | NOTICE.LESSON_LIST | 저장 레슨 목록 | notice_id, recipient_scope, content_version | 정확 저장 레슨 목록을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.LESSON_DETAIL | 저장 레슨 상세 | notice_id, recipient_scope, content_version | 정확 저장 레슨 상세을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.FEATURE_SCOPE | 플랫폼별 업무 제공 범위 및 제약 | notice_id, recipient_scope, content_version | 정확 플랫폼별 업무 제공 범위 및 제약을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.INPUT_PREVIEW | 외부 입력안 | notice_id, recipient_scope, content_version | 정확 외부 입력안을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.INPUT_CHECK | 입력안 검사 결과 | notice_id, recipient_scope, content_version | 정확 입력안 검사 결과을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.QUESTION | 보완 질문 전달 내용 | notice_id, recipient_scope, content_version | 정확 보완 질문 전달 내용을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.OPTIONS | 제약 충돌 대안 | notice_id, recipient_scope, content_version | 정확 제약 충돌 대안을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.AUTH | 직접 인증 안내 | notice_id, recipient_scope, content_version | 정확 직접 인증 안내을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.PREREQUISITE | 외부 직접 선행 절차 안내 | notice_id, recipient_scope, content_version | 정확 외부 직접 선행 절차 안내을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.IDENTITY | 외부 대상 후보 및 식별 근거 | notice_id, recipient_scope, content_version | 정확 외부 대상 후보 및 식별 근거을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.DIFF | 변경 차이 및 영향 | notice_id, recipient_scope, content_version | 정확 변경 차이 및 영향을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.INFO_APPROVAL | 정보 승인 요구 내용 | notice_id, recipient_scope, content_version | 정확 정보 승인 요구 내용을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.EXEC_APPROVAL | 실행 승인 요구 내용 | notice_id, recipient_scope, content_version | 정확 실행 승인 요구 내용을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.INTERNAL_RESULT | 내부 변경 결과 | notice_id, recipient_scope, content_version | 정확 내부 변경 결과을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.TASK_PROGRESS | 업무 준비·수락·시도 상태 | notice_id, recipient_scope, content_version | 정확 업무 준비·수락·시도 상태을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.EFFECT_RESULT | 대상별 외부 효과 판정 | notice_id, recipient_scope, content_version | 정확 대상별 외부 효과 판정을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.HISTORY | 업무 이력 | notice_id, recipient_scope, content_version | 정확 업무 이력을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.LAST_OBSERVATION | 마지막 유효 외부 조회 정보 | notice_id, recipient_scope, content_version | 정확 마지막 유효 외부 조회 정보을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.NEW_OBSERVATION | 새 외부 조회 결과 | notice_id, recipient_scope, content_version | 정확 새 외부 조회 결과을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.ISSUE | 문제 및 후속 조치 | notice_id, recipient_scope, content_version | 정확 문제 및 후속 조치을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.SESSION_RESULT | 외부 접근 차단 및 폐기 결과 | notice_id, recipient_scope, content_version | 정확 외부 접근 차단 및 폐기 결과을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.RIGHT_RESULT | 정보 권리 처리 결과 | notice_id, recipient_scope, content_version | 정확 정보 권리 처리 결과을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.MONITOR_RISK | 인증 유지 위험 안내 | notice_id, recipient_scope, content_version | 정확 인증 유지 위험 안내을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.MONITOR_CHANGE | 조건부 상태 변화 통지 | notice_id, recipient_scope, content_version | 정확 조건부 상태 변화 통지을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| NOTICE | NOTICE.OPS | 운영 사건 정보 | notice_id, recipient_scope, content_version | 정확 운영 사건 정보을 제공하기 위한 정보 집합. 전달 시도/열람/결정과 구분. | notice_id, recipient_ref, subject_ref, content_refs, version |
| ISSUE | ISSUE.INPUT_MISSING | 입력 항목 누락 | issue_id, target_ref, related_event | 정확 입력 항목 누락에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.INPUT_UNCERTAIN | 입력 의미/값 불확실 | issue_id, target_ref, related_event | 정확 입력 의미/값 불확실에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.INPUT_CONFLICT | 입력 제약 충돌 | issue_id, target_ref, related_event | 정확 입력 제약 충돌에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.INPUT_FORMAT | 입력 규격 위반 | issue_id, target_ref, related_event | 정확 입력 규격 위반에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.AUTH | 인증 실패/만료 | issue_id, target_ref, related_event | 정확 인증 실패/만료에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.ACCOUNT_MISMATCH | 외부 계정 불일치 | issue_id, target_ref, related_event | 정확 외부 계정 불일치에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.PERMISSION | 업무 권한 제한 | issue_id, target_ref, related_event | 정확 업무 권한 제한에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.POLICY | 대행 허용 미확인/금지 | issue_id, target_ref, related_event | 정확 대행 허용 미확인/금지에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.IDENTITY | 외부 대상 식별 불명 | issue_id, target_ref, related_event | 정확 외부 대상 식별 불명에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.APPROVAL | 승인 변경/불일치 | issue_id, target_ref, related_event | 정확 승인 변경/불일치에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.DUPLICATE | 중복/지연 실행 위험 | issue_id, target_ref, related_event | 정확 중복/지연 실행 위험에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.INTERNAL_UNKNOWN | 내부 처리 결과 불명 | issue_id, target_ref, related_event | 정확 내부 처리 결과 불명에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.EXTERNAL_NOT_OCCURRED | 외부 효과 미발생 확인 | issue_id, target_ref, related_event | 정확 외부 효과 미발생 확인에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.EXTERNAL_UNKNOWN | 외부 효과 발생 여부 불명 | issue_id, target_ref, related_event | 정확 외부 효과 발생 여부 불명에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.REVIEW_REJECTION | 외부 심사 반려 | issue_id, target_ref, related_event | 정확 외부 심사 반려에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.READ_UNAVAILABLE | 외부 조회 불가/상충 | issue_id, target_ref, related_event | 정확 외부 조회 불가/상충에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.SESSION_UNKNOWN | 접근 차단 또는 폐기 불명 | issue_id, target_ref, related_event | 정확 접근 차단 또는 폐기 불명에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |
| ISSUE | ISSUE.OPERATIONS | 서비스 운영 장애 | issue_id, target_ref, related_event | 정확 서비스 운영 장애에 대한 영향·사유·근거와 후속 조건. 다른 문제 유형으로 일괄 대체 금지. | issue_id, target_ref, stage, evidence, impact, followup_refs |

## 2. 플랫폼별 고유 대상 전체

| 유형 ID | 대상 | 역할 | 정의 | 식별 기준·미확인 | 근거 |
|---|---|---|---|---|---|
| EXT.KMONG.PRODUCT | 크몽 서비스 상품 | 모집 대상 | 독립 상품 후보; 가격 패키지와 구분 | 상품 관리 경로 및 상품 ID 후보. 영구성·계정 권한 검증 전 쓰기 금지 | R02-PL01-OBJ1·R04-PL01-OBJ1·R05-PL01-O1 |
| EXT.KMONG.PACKAGE | 크몽 가격 패키지 | 종속 구성 | 상품의 가격 구성 단위. 독립 객체인지 값 묶음인지 미확인 | 정확 상품과 패키지 구분값 필요; 구분값 검증 전 변경 금지 | R04-PL01-OBJ2 |
| EXT.KMONG.OPTION | 크몽 가격 옵션 | 종속 구성 | 상품 또는 패키지에 포함되는 추가 선택 항목. 소속 범위 미확인 | 정확 소속 대상 및 옵션 구분값 필요; 독립 ID 미확인 | R05-PL01-O2 |
| EXT.KMONG.EXPERT_PROFILE | 크몽 전문가 소개 프로필 | 공유 후보 | 전문가 소개·기술·경력·포트폴리오의 소속 대상 후보. 별개 외부 실체인지 미확인 | 상품 소개와 구별 가능한 공식 관리 경로 및 식별 근거 필요 | R02-PL01-OBJ1 |
| EXT.TALING.CLASS | 탈잉 클래스 | 모집 대상 | 수강료·회차·커리큘럼을 포함하는 클래스 심사 단위 후보 | 정확 클래스 식별 및 튜터 계정 필요; 클래스명만으로 식별 금지 | R02-PL02-OBJ1·R04-PL02-OBJ1·R05-PL02-O1 |
| EXT.TALING.TUTOR_PROFILE | 탈잉 튜터 프로필 | 공유 후보 | 튜터명·튜터 소개·프로필 사진 등의 소속 대상. 클래스와 구분 | 튜터 프로필 독립 식별·클래스 공유 영향 확인 필요 | R02-PL02-OBJ1 |
| EXT.TALING.CURRICULUM_SESSION | 탈잉 커리큘럼 회차 | 종속 구성 | 클래스 내 회차별 제목·내용 후보. 일정과 구분 | 클래스 및 회차 구분 방식 확인 필요 | R04-PL02-OBJ2 |
| EXT.TALING.SCHEDULE | 탈잉 클래스 일정 | 종속 구성 | 모집 신청을 받기 위한 날짜/협의 일정. 회차별 내용과 구분 | 정확 클래스와 일정 구분 방식 확인 필요 | R05-PL02-O2 |
| EXT.SOOMGO.PROFILE | 숨고 고수 프로필 | 공유 대상 | 활동명·소개·대표 서비스가 속할 수 있는 고수 프로필 | 본인 프로필 관리 경로 및 계정 식별 근거 필요; 표시명만으로 식별 금지 | R02-PL03-OBJ1·R04-PL03-OBJ1·R05-PL03-O1 |
| EXT.SOOMGO.SERVICE_REL | 숨고 제공 서비스 관계 | 모집 관계 후보 | 정확 프로필에 속한 제공 서비스 분야 및 서비스별 세부 항목. 독립 객체 여부 미확인 | 프로필과 제공 서비스 구분 근거 및 관계 유일성 확인 필요 | R04-PL03-OBJ2·R05-PL03-O2 |
| EXT.PROMPIE.PROFILE | 프람피 전문가 프로필 | 공유 대상 | 전문가 활동명·소개·주소 등 프로필 대상 | 본인 프로필 및 계정별 정확 식별 규칙 필요 | R02-PL04-OBJ1·R04-PL04-OBJ1·R05-PL04-O1 |
| EXT.PROMPIE.FIELD_REL | 프람피 제공 레슨 분야 관계 | 모집 관계 후보 | 프로필에 연결된 레슨 분야와 분야별 소개 | 프로필 및 정확 분야 구분 근거 필요 | R02-PL04-OBJ2·R04-PL04-OBJ2·R05-PL04-O2 |
| EXT.PROMPIE.CURRICULUM | 프람피 커리큘럼 | 종속 구성 | 레슨 계획 및 설명의 구성 단위 후보 | 소속 분야 및 커리큘럼 구분 근거 필요 | R02-PL04-OBJ3 |
| EXT.PROMPIE.PRICE_ENTRY | 프람피 시간별 비용 항목 | 종속 값 묶음 후보 | 1회 수업 시간과 1회 레슨 비용의 조합. 독립 객체 아님을 가정하지 않음 | 소속 커리큘럼 및 가격 행 구분 규칙 확인 필요 | R02-PL04-OBJ4 |
| EXT.PROMPIE.PORTFOLIO_ITEM | 프람피 포트폴리오 항목 | 종속 구성 | 이미지/영상 및 영상 설명의 소속 항목 후보 | 프로필 및 포트폴리오 항목 구분 근거 필요 | R02-PL04-OBJ5 |
| EXT.PROMPIE.FAQ_ANSWER | 프람피 FAQ 답변 | 종속 구성 | 정확 질문에 대한 답변 항목 후보 | 프로필 및 질문 식별 근거 필요 | R02-PL04-OBJ6 |
| EXT.PROMPIE.EDUCATION_ENTRY | 프람피 학력 항목 | 종속 구성 후보 | 대학교 학력 항목. 교육 이수·경력과 구분 | 프로필 및 학력 행 구분 방식 미확인 | R02-PL04-OBJ7 |
| EXT.PROMPIE.TRAINING_ENTRY | 프람피 교육 이수 항목 | 종속 구성 후보 | 교육 이수 이력 항목. 학력·경력과 구분 | 프로필 및 교육 행 구분 방식 미확인 | R02-PL04-OBJ7 |
| EXT.PROMPIE.CAREER_ENTRY | 프람피 경력 항목 | 종속 구성 후보 | 경력 이력 항목. 학력·교육 이수와 구분 | 프로필 및 경력 행 구분 방식 미확인 | R02-PL04-OBJ7 |
| EXT.MULE.POST | 뮬 개인레슨 게시글 | 모집 대상 | 개인레슨 게시판에 속한 개별 모집 게시글 | 게시글 idx 및 URL 관측 보고 있음; 소유/영구성/갱신 동일성 검증 필요 | R02-PL05-OBJ1·R04-PL05-OBJ1·R05-PL05-O1 |
| EXT.MULE.BOARD | 뮬 개인레슨 게시판 | 게시 위치 | 개별 글이 속한 게시판. 강사의 글과 구분 | 게시판 경로 식별; 게시글 수정/갱신 대상 금지 | R05-PL05-O2 |
| EXT.HIPHOPPLAYA.POST | 힙합플레이야 홍보 게시글 | 모집 대상 | 홍보 게시판의 개별 레슨 글 | 게시판 경로와 글 식별값 관측; 소유권·유일성 검증 필요 | R02-PL06-OBJ1·R04-PL06-OBJ1·R05-PL06-O1 |
| EXT.HIPHOPPLAYA.BOARD | 힙합플레이야 홍보 게시판 | 게시 위치 | 홍보 글이 속한 게시판 | 정확 게시판 분류 경로; 글 수정/갱신 대상 금지 | R05-PL06-O2 |
| EXT.HIPHOPLE.POST | 힙합LE 레슨 장터 게시글 | 모집 대상 | 장터에 표시되는 개별 레슨 모집 글 | 공개 상세 경로 식별값 관측; 소유권·영구성 검증 필요 | R02-PL07-OBJ1·R04-PL07-OBJ1·R05-PL07-O1 |
| EXT.HIPHOPLE.CATEGORY | 힙합LE 레슨 분류 | 분류 값/참조 후보 | 장터 레슨 분류. 개별 글과 구분 | 분류 링크 관측; 외부 객체인지 값인지 확인 필요 | R05-PL07-O2 |

## 3. 공통 레슨 항목 규격 후보

| 항목 ID | 의미 | 값 형식 | 단위 | 구체 정의 |
|---|---|---|---|---|
| FIELD.LESSON.TITLE | 레슨 제목 | text | 없음 | 강사가 저장 레슨 정보에 부여한 모집용 제목 |
| FIELD.LESSON.INSTRUCTOR_DISPLAY_NAME | 강사 활동명 | text | 없음 | 수강생에게 공개할 강사 활동명. 서비스 계정 로그인 이름과 별개 |
| FIELD.LESSON.SUBJECT | 레슨 분야 | category_ref | 분야 코드 | 수업에서 가르치는 분야. 플랫폼 카테고리값과 별개 |
| FIELD.LESSON.DESCRIPTION | 레슨 상세 소개 | text | 없음 | 레슨 제공 내용의 설명 |
| FIELD.LESSON.SUMMARY | 레슨 요약 | text | 없음 | 레슨 자체의 짧은 요약. 강사 프로필 한 줄 소개와 별개 |
| FIELD.LESSON.INSTRUCTOR_BIO | 강사 소개 | text | 없음 | 레슨 제공자인 강사의 소개 |
| FIELD.LESSON.DELIVERY_MODE | 수업 진행 방식 | enum_candidate | 없음 | 대면/비대면 등 수업 제공 방식. 모집 형태와 별개 |
| FIELD.LESSON.GROUP_MODE | 모집 형태 | enum_candidate | 없음 | 개인/그룹 등 모집 단위 형태 |
| FIELD.LESSON.PARTICIPANT_COUNT | 수강 인원 | positive_integer | 명 | 해당 수업의 참여 수강생 수. 최소/최대/정원 구분 추가 확인 |
| FIELD.LESSON.AUDIENCE_DESCRIPTION | 대상 수강생 설명 | text | 없음 | 레슨을 모집하려는 수강생의 설명 |
| FIELD.LESSON.REGION | 수업 가능 지역 | region_ref | 지역 코드 | 강사가 수업 가능한 지리 영역 |
| FIELD.LESSON.VENUE_NAME | 수업 장소명 | text | 없음 | 실제 수업 장소의 명칭 |
| FIELD.LESSON.VENUE_ADDRESS | 수업 장소 주소 | address_text | 없음 | 실제 수업 장소의 주소 |
| FIELD.LESSON.VENUE_NEGOTIABLE | 수업 장소 협의 가능 여부 | boolean | 없음 | 수강생과 수업 장소 협의가 가능한지 여부 |
| FIELD.LESSON.PRICE_AMOUNT | 레슨 가격 금액 | nonnegative_decimal | PRICE_CURRENCY | 정확 가격 적용 단위와 결합한 레슨 제공 금액. 금액만으로 변환 불가 |
| FIELD.LESSON.PRICE_BASIS | 레슨 가격 적용 단위 | enum | PER_SESSION/PER_HOUR/PER_COURSE | PRICE_AMOUNT가 적용되는 과금 기준. 실제 필요 단위 추가 확인 |
| FIELD.LESSON.PRICE_CURRENCY | 레슨 가격 통화 | currency_code | 통화 코드 | 가격 금액의 통화. 국내 서비스에서 통화 선택 UI 채택 미정 |
| FIELD.LESSON.SESSION_DURATION | 회당 수업 시간 | positive_integer | 분/회 | 한 회 수업에 제공하는 시간 |
| FIELD.LESSON.SESSION_COUNT | 총 수업 횟수 | positive_integer | 회/과정 | 전체 수업 과정에 포함되는 회차 수 |
| FIELD.LESSON.CURRICULUM_SESSION_TEXT | 회차별 커리큘럼 설명 | text | 없음 | 지정 회차에서 진행할 수업 내용. 회차 번호 필수 |
| FIELD.LESSON.DELIVERY_PROCEDURE | 레슨 제공 절차 설명 | text | 없음 | 레슨을 제공하기까지의 절차 안내. 실제 플랫폼 입력 의미 검증 필요 |
| FIELD.LESSON.STUDENT_PREPARATION | 수강생 준비사항 | text | 없음 | 수강생이 수업 전 준비할 사항 |
| FIELD.LESSON.AVAILABILITY | 수업 제공 가능 시간 | time_range_candidate | 시간대 | 강사가 수업을 제공할 수 있는 시간 범위. 외부 최초 일정과 별개 |
| FIELD.LESSON.CONTACT_AVAILABILITY | 연락 가능 시간 | time_range_candidate | 시간대 | 문의 연락을 받을 수 있는 시간 범위 |
| FIELD.LESSON.CONTACT_PHONE | 모집 연락용 전화번호 | phone_text | 없음 | 강사가 모집 정보에 제공할 전화번호. 로그인/인증 번호와 별개 |
| FIELD.LESSON.CONTACT_PUBLIC | 연락처 공개 여부 | boolean | 없음 | 해당 모집 연락처를 공개할지의 결정. 실제 플랫폼 허용 별도 |
| FIELD.LESSON.WEBSITE_URL | 공개 소개 웹사이트 링크 | url | 없음 | 강사/레슨을 소개하기 위해 공개할 웹사이트 URL |
| FIELD.LESSON.SEARCH_KEYWORD | 검색 키워드 | text_list | 없음 | 검색용 키워드 목록. 플랫폼 태그와 자동 동일시하지 않음 |
| FIELD.LESSON.TAG | 레슨 태그 | text_list | 없음 | 모집 정보에 부여할 태그 후보 목록 |
| FIELD.LESSON.FAQ_QUESTION | FAQ 질문 | text | 없음 | 강사가 제공하는 자주 묻는 질문 하나의 문구. 답변과 구분 |
| FIELD.LESSON.FAQ_ANSWER | FAQ 답변 | text | 없음 | 정확 질문 항목에 대응하는 답변 문구 |
| FIELD.LESSON.BEFORE_LESSON_REQUEST | 수강 전 요청사항 | text | 없음 | 수업 시작 전에 수강생에게 요구할 사항 |
| FIELD.LESSON.EDUCATION_TEXT | 강사 학력 소개 | text | 없음 | 공개 소개용 학력 내용. 인증 증빙 자체와 별개 |
| FIELD.LESSON.CAREER_TEXT | 강사 경력 소개 | text | 없음 | 공개 소개용 경력 내용. 학력/자격과 별개 |
| FIELD.LESSON.PORTFOLIO_VIDEO_DESCRIPTION | 포트폴리오 영상 설명 | text | 없음 | 지정 포트폴리오 영상에 대한 설명 |
| FIELD.LESSON.INCLUDED_ITEMS | 레슨 기본 포함 항목 | text_list | 없음 | 기본 레슨 가격에 포함된 제공 항목 |
| FIELD.LESSON.PRICE_NOTE | 가격 참고 설명 | text | 없음 | 가격의 적용 조건에 관한 설명. 금액/단위와 별개 |
| FIELD.LESSON.SKILL_TEXT | 강사 보유 기술 소개 | text | 없음 | 강사가 공개할 기술 설명. 레슨 분야와 별개 |
| FIELD.LESSON.QUALIFICATION_TEXT | 강사 자격 소개 | text | 없음 | 공개할 자격에 관한 설명. 공식 증빙 제출과 별개 |
| FIELD.LESSON.TRAINING_TEXT | 강사 교육 이수 소개 | text | 없음 | 공개할 교육 이수 내용. 학력/경력과 별개 |

## 4. 자료 사용 목적과 허용 자료

| 목적 ID | 명칭 | 허용 자료 유형 |
|---|---|---|
| COVER_IMAGE | 대표 모집 이미지 | MATERIAL.IMAGE |
| PROFILE_IMAGE | 강사 프로필 이미지 | MATERIAL.IMAGE |
| BODY_IMAGE | 본문 삽입 이미지 | MATERIAL.IMAGE |
| LESSON_VIDEO | 레슨 소개 영상 | MATERIAL.VIDEO·MATERIAL.URL |
| LESSON_AUDIO | 레슨 소개 음원 | MATERIAL.AUDIO·MATERIAL.URL |
| PORTFOLIO | 강사 포트폴리오 자료 | MATERIAL.IMAGE·MATERIAL.VIDEO·MATERIAL.AUDIO·MATERIAL.DOCUMENT·MATERIAL.URL |
| CURRICULUM | 회차별 커리큘럼 자료 | MATERIAL.TEXT·MATERIAL.DOCUMENT·MATERIAL.IMAGE·MATERIAL.VIDEO |
| REFERENCE | 정보 추출 참고 자료 | MATERIAL.TEXT·MATERIAL.IMAGE·MATERIAL.DOCUMENT·MATERIAL.URL |

## 5. 팀원 조사 필드 주장 전체

각 행은 별도 주장 식별자이며 최종 필드 규격 ID가 아니다. 같은 라벨을 자동 통합하지 않고 실제 소속·의미·단위·읽기/쓰기 조건이 확정될 때만 필드 규격으로 채택한다.

| 근거 ID | 플랫폼 | 원문 | 대상 후보 | 원문 방향 | 상태 |
|---|---|---|---|---|---|
| R02-PL01-FIELD01 | 크몽 | 전문가 소개 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-FIELD02 | 크몽 | 보유 기술 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-FIELD03 | 크몽 | 경력·학력·자격 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-FIELD04 | 크몽 | 포트폴리오 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-01 | 크몽 | 제목 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-02 | 크몽 | 카테고리 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-03 | 크몽 | 서비스 설명 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-04 | 크몽 | 모집 형태 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-05 | 크몽 | 메인 이미지 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-06 | 크몽 | 상세 이미지 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-07 | 크몽 | 동영상 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-08 | 크몽 | 서비스 제공 절차 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-09 | 크몽 | 의뢰인 준비사항 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-10 | 크몽 | 지역 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-11 | 크몽 | 가격 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-12 | 크몽 | 작업 기간 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-13 | 크몽 | 수정 횟수 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-14 | 크몽 | 1회당 레슨시간 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-15 | 크몽 | 레슨 횟수 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-16 | 크몽 | 기본 포함 항목 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-17 | 크몽 | 검색 키워드 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-18 | 크몽 | 자주 묻는 질문 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-19 | 크몽 | 작업 전 요청사항 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-20 | 크몽 | 대상자 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-21 | 크몽 | 서비스 내용 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-22 | 크몽 | 준비물 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-23 | 크몽 | 커리큘럼 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-24 | 크몽 | 가능일 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-25 | 크몽 | 빠른 작업 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-26 | 크몽 | 추가 수정 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-27 | 크몽 | 레슨 시간 추가 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-28 | 크몽 | 레슨 횟수 추가 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-29 | 크몽 | 준비물 제공 비용 추가 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-30 | 크몽 | 강의실 제공 추가 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL01-CONF-31 | 크몽 | 맞춤 옵션 | EXT.KMONG.PRODUCT·EXT.KMONG.EXPERT_PROFILE | input | source_report |
| R02-PL02-FIELD01 | 탈잉 | 카테고리 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE | input | source_report |
| R02-PL02-FIELD02 | 탈잉 | 클래스명 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE | input | source_report |
| R02-PL02-FIELD03 | 탈잉 | 클래스 썸네일 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE | input | source_report |
| R02-PL02-FIELD04 | 탈잉 | 클래스 대상 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE | input | source_report |
| R02-PL02-CONF-01 | 탈잉 | 운영 방식 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-02 | 탈잉 | 카테고리 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-03 | 탈잉 | 클래스명 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-04 | 탈잉 | 클래스 썸네일 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-05 | 탈잉 | 클래스 대상 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-06 | 탈잉 | 클래스 요약 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-07 | 탈잉 | 클래스 상세 소개 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-08 | 탈잉 | 회차 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-09 | 탈잉 | 회차별 커리큘럼 소개 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-10 | 탈잉 | 참여인원 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-11 | 탈잉 | 수강료 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-12 | 탈잉 | 승인 메시지 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-13 | 탈잉 | 태그 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-14 | 탈잉 | 영상 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-15 | 탈잉 | 클래스 공지사항 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-16 | 탈잉 | 정산 설정 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-17 | 탈잉 | 튜터명 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-18 | 탈잉 | 튜터 소개 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-19 | 탈잉 | 프로필 이미지 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-20 | 탈잉 | 이력 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-21 | 탈잉 | 장소 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL02-CONF-22 | 탈잉 | 튜터 채널 | EXT.TALING.CLASS·EXT.TALING.TUTOR_PROFILE |  | source_report |
| R02-PL03-FIELD01 | 숨고 | 활동명 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD02 | 숨고 | 한줄소개 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD03 | 숨고 | 이벤트 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD04 | 숨고 | 프로필 사진 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD05 | 숨고 | 경력 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD06 | 숨고 | 학력 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD07 | 숨고 | 고수 서비스 상세설명 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD08 | 숨고 | 사진 및 동영상 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD09 | 숨고 | 질문답변 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL03-FIELD10 | 숨고 | 포트폴리오 | EXT.SOOMGO.PROFILE | input | source_report |
| R02-PL04-FIELD01 | 프람피 | 카테고리 선택 | EXT.PROMPIE.PROFILE | input | source_report |
| R02-PL04-CONF-01 | 프람피 | 프로필 제목 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-02 | 프람피 | 전문가 활동명(비즈니스명) | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-03 | 프람피 | 프로필 사진 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-04 | 프람피 | 주소·공개 표시 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-05 | 프람피 | 제안이력 가격 공개여부 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-06 | 프람피 | 본인인증 연령대 공개 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-07 | 프람피 | 진행방식 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-08 | 프람피 | 포트폴리오 목록 | EXT.PROMPIE.PORTFOLIO_ITEM | input·visible | source_report |
| R02-PL04-CONF-09 | 프람피 | 포트폴리오 이미지 | EXT.PROMPIE.PORTFOLIO_ITEM | input·visible | source_report |
| R02-PL04-CONF-10 | 프람피 | 포트폴리오 영상 | EXT.PROMPIE.PORTFOLIO_ITEM | input·visible | source_report |
| R02-PL04-CONF-11 | 프람피 | 포트폴리오 영상 설명 | EXT.PROMPIE.PORTFOLIO_ITEM | input·visible | source_report |
| R02-PL04-CONF-12 | 프람피 | 전문가 소개 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-13 | 프람피 | 이력 분류 | EXT.PROMPIE.EDUCATION_ENTRY·EXT.PROMPIE.TRAINING_ENTRY·EXT.PROMPIE.CAREER_ENTRY | input·visible | source_report |
| R02-PL04-CONF-14 | 프람피 | 대학교 학력 | EXT.PROMPIE.EDUCATION_ENTRY·EXT.PROMPIE.TRAINING_ENTRY·EXT.PROMPIE.CAREER_ENTRY | input·visible | source_report |
| R02-PL04-CONF-15 | 프람피 | 교육 이수 이력 | EXT.PROMPIE.EDUCATION_ENTRY·EXT.PROMPIE.TRAINING_ENTRY·EXT.PROMPIE.CAREER_ENTRY | input·visible | source_report |
| R02-PL04-CONF-16 | 프람피 | 제공 레슨 분야 | EXT.PROMPIE.FIELD_REL | input·visible | source_report |
| R02-PL04-CONF-17 | 프람피 | 분야별 서비스 소개 | EXT.PROMPIE.FIELD_REL | input·visible | source_report |
| R02-PL04-CONF-18 | 프람피 | 커리큘럼 기본정보 | EXT.PROMPIE.CURRICULUM | input·visible | source_report |
| R02-PL04-CONF-19 | 프람피 | 커리큘럼 모집 형태 | EXT.PROMPIE.CURRICULUM | input·visible | source_report |
| R02-PL04-CONF-20 | 프람피 | 1회당 수업시간 | EXT.PROMPIE.PRICE_ENTRY | input·visible | source_report |
| R02-PL04-CONF-21 | 프람피 | 1회당 레슨비용 | EXT.PROMPIE.PRICE_ENTRY | input·visible | source_report |
| R02-PL04-CONF-22 | 프람피 | 커리큘럼 레슨 설명 | EXT.PROMPIE.CURRICULUM | input·visible | source_report |
| R02-PL04-CONF-23 | 프람피 | 레슨 계획 단계 | EXT.PROMPIE.CURRICULUM | input·visible | source_report |
| R02-PL04-CONF-24 | 프람피 | 레슨 비용의 커리큘럼별 시간·가격 묶음 | EXT.PROMPIE.PRICE_ENTRY | input·visible | source_report |
| R02-PL04-CONF-25 | 프람피 | 레슨 비용 참고 사항 | EXT.PROMPIE.PRICE_ENTRY | input·visible | source_report |
| R02-PL04-CONF-26 | 프람피 | 웹사이트·외부 링크 | EXT.PROMPIE.PROFILE | input·visible | source_report |
| R02-PL04-CONF-27 | 프람피 | 리뷰 요청 주소 | EXT.PROMPIE.PROFILE | visible | source_report |
| R02-PL04-CONF-28 | 프람피 | FAQ | EXT.PROMPIE.FAQ_ANSWER | input·visible | source_report |
| R02-PL05-CONF-01 | 뮬 | 구분 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-02 | 뮬 | 지역 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-03 | 뮬 | 주소 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-04 | 뮬 | 홈페이지 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-05 | 뮬 | 전화번호 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-06 | 뮬 | 팩스 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-07 | 뮬 | 수강료 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-08 | 뮬 | 메인사진 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-09 | 뮬 | 사운드클라우드 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-10 | 뮬 | 제목 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-11 | 뮬 | 본문 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-12 | 뮬 | 본문 이미지 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-13 | 뮬 | 본문 동영상 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-14 | 뮬 | 약관동의 | EXT.MULE.POST | input·visible | source_report |
| R02-PL05-CONF-15 | 뮬 | 게시글 식별·시간·통계 | EXT.MULE.POST | visible | source_report |
| R02-PL05-CONF-16 | 뮬 | 최신글로 올리기·프리미엄 등록 | EXT.MULE.POST | visible | source_report |
| R02-PL05-CONF-17 | 뮬 | 수정·삭제 | EXT.MULE.POST | visible | source_report |
| R02-PL06-CONF-01 | 힙합플레이야 | 제목 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-02 | 힙합플레이야 | 본문 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-03 | 힙합플레이야 | 카테고리 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-04 | 힙합플레이야 | 첨부 미디어 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-05 | 힙합플레이야 | 외부 이미지·동영상 붙여넣기 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-06 | 힙합플레이야 | 임시저장·연습장 불러오기 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL06-CONF-07 | 힙합플레이야 | 글 등록 | EXT.HIPHOPPLAYA.POST | input·visible | source_report |
| R02-PL07-CONF-01 | 힙합LE | 레슨 분류 | EXT.HIPHOPLE.POST | visible | source_report |
| R02-PL07-CONF-02 | 힙합LE | 제목 | EXT.HIPHOPLE.POST | visible | source_report |
| R02-PL07-CONF-03 | 힙합LE | 썸네일 | EXT.HIPHOPLE.POST | visible | source_report |
| R02-PL07-CONF-04 | 힙합LE | 가격 | EXT.HIPHOPLE.POST | visible | source_report |
| R02-PL07-CONF-05 | 힙합LE | 작성자·게시일 | EXT.HIPHOPLE.POST | visible | source_report |
| R02-PL07-CONF-06 | 힙합LE | 본문 | EXT.HIPHOPLE.POST | visible | source_report |
| R04-PL01-F01 | 크몽 | 서비스 제목 | EXT.KMONG.PRODUCT | input·visible | unknown |
| R04-PL01-F02 | 크몽 | 카테고리 | EXT.KMONG.PRODUCT | input | unknown |
| R04-PL01-F03 | 크몽 | 패키지별 가격 | EXT.KMONG.PACKAGE | input·visible | unknown |
| R04-PL01-F09 | 크몽 | 패키지별 옵션 (작업 기간·수정 횟수 등) | EXT.KMONG.PACKAGE | input·visible | unknown |
| R04-PL01-F04 | 크몽 | 서비스 설명 | EXT.KMONG.PRODUCT | input·visible | unknown |
| R04-PL01-F05 | 크몽 | 메인 이미지 | EXT.KMONG.PRODUCT | input·visible | unknown |
| R04-PL01-F06 | 크몽 | 의뢰인 준비사항 | EXT.KMONG.PRODUCT | input | unknown |
| R04-PL01-F07 | 크몽 | 상품 고유 ID | EXT.KMONG.PRODUCT | return·visible | unknown |
| R04-PL01-F10 | 크몽 | 상품 상세 링크 | EXT.KMONG.PRODUCT | return·visible | unknown |
| R04-PL01-F08 | 크몽 | 심사 상태 | EXT.KMONG.PRODUCT | return·visible | unknown |
| R04-PL01-F11 | 크몽 | 판매 상태 | EXT.KMONG.PRODUCT | return·visible | unknown |
| R04-PL02-F01 | 탈잉 | 수업 제목 | EXT.TALING.CLASS | input·visible | unknown |
| R04-PL02-F02 | 탈잉 | 수업 형태 | EXT.TALING.CLASS | input | unknown |
| R04-PL02-F08 | 탈잉 | 수업 인원 | EXT.TALING.CLASS | input | unknown |
| R04-PL02-F03 | 탈잉 | 시간당 수업료 | EXT.TALING.CLASS | input·visible | unknown |
| R04-PL02-F09 | 탈잉 | 회차 | EXT.TALING.CLASS | input·visible | unknown |
| R04-PL02-F04 | 탈잉 | 단계별 커리큘럼 | EXT.TALING.CURRICULUM_SESSION | input·visible | unknown |
| R04-PL02-F05 | 탈잉 | 커버 사진 | EXT.TALING.CLASS | input·visible | unknown |
| R04-PL02-F10 | 탈잉 | 수업 사진 | EXT.TALING.CLASS | input·visible | unknown |
| R04-PL02-F06 | 탈잉 | 클래스 식별 번호 | EXT.TALING.CLASS | return·visible | unknown |
| R04-PL02-F11 | 탈잉 | 클래스 URL | EXT.TALING.CLASS | return·visible | unknown |
| R04-PL02-F07 | 탈잉 | 클래스 검수 상태 | EXT.TALING.CLASS | return·visible | unknown |
| R04-PL03-F01 | 숨고 | 한 줄 소개 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F02 | 숨고 | 제공 서비스 | EXT.SOOMGO.SERVICE_REL | input·visible | observed |
| R04-PL03-F03 | 숨고 | 서비스 세부 항목 (제공 가능 항목 선택) | EXT.SOOMGO.SERVICE_REL | input | observed |
| R04-PL03-F04 | 숨고 | 서비스 상세 설명 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F05 | 숨고 | 프로필 이미지 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F06 | 숨고 | 활동 지역 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F07 | 숨고 | 고수 프로필 URL | EXT.SOOMGO.PROFILE | return·visible | reported |
| R04-PL03-F08 | 숨고 | 프로필 공개 상태 | EXT.SOOMGO.PROFILE | return·visible | unknown |
| R04-PL03-F09 | 숨고 | 숨고 활동명 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F10 | 숨고 | 연락 가능 시간 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F11 | 숨고 | 직원수 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F12 | 숨고 | 외부 링크 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F13 | 숨고 | 대표 서비스 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F14 | 숨고 | 활동 가능 범위 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F15 | 숨고 | 프로필 완성도 | EXT.SOOMGO.PROFILE | visible | observed |
| R04-PL03-F16 | 숨고 | 서비스 세부 항목 설정 상태 | EXT.SOOMGO.SERVICE_REL | visible | observed |
| R04-PL03-F17 | 숨고 | 경력 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F18 | 숨고 | 학력 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F19 | 숨고 | 사진 및 동영상 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F20 | 숨고 | 포트폴리오 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F21 | 숨고 | 질문답변 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F22 | 숨고 | 본인인증 | EXT.SOOMGO.PROFILE | visible | observed |
| R04-PL03-F23 | 숨고 | 사업자등록증 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F24 | 숨고 | 공식 자격증 및 기타 서류 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F25 | 숨고 | 결제 수단 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F26 | 숨고 | 숨고페이 정산정보 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F27 | 숨고 | 세금 계산서 발행 | EXT.SOOMGO.PROFILE | input·visible | observed |
| R04-PL03-F28 | 숨고 | 리뷰 | EXT.SOOMGO.PROFILE | visible | observed |
| R04-PL04-F01 | 프람피 | 전문가명 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F07 | 프람피 | 한줄소개 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F02 | 프람피 | 전문 분야 (레슨) | EXT.PROMPIE.FIELD_REL | input·visible | unknown |
| R04-PL04-F03 | 프람피 | 소개글 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F08 | 프람피 | 경력사항 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F04 | 프람피 | 활동 지역 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F09 | 프람피 | 레슨 방식 | EXT.PROMPIE.PROFILE | input·visible | unknown |
| R04-PL04-F05 | 프람피 | 전문가 프로필 URL | EXT.PROMPIE.PROFILE | return·visible | unknown |
| R04-PL04-F06 | 프람피 | 전문가 활동 상태 | EXT.PROMPIE.PROFILE | return·visible | unknown |
| R04-PL05-F01 | 뮬 | 제목 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F02 | 뮬 | 과목 분류 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F08 | 뮬 | 지역 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F03 | 뮬 | 본문 내용 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F04 | 뮬 | 첨부 이미지 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F05 | 뮬 | 연락처 정보 | EXT.MULE.POST | input·visible | unknown |
| R04-PL05-F06 | 뮬 | 게시글 번호 | EXT.MULE.POST | return·visible | unknown |
| R04-PL05-F09 | 뮬 | 게시글 URL | EXT.MULE.POST | return·visible | unknown |
| R04-PL05-F07 | 뮬 | 게시 일시 | EXT.MULE.POST | return·visible | unknown |
| R04-PL05-F10 | 뮬 | 갱신 일시 | EXT.MULE.POST | return·visible | unknown |
| R04-PL05-F11 | 뮬 | 노출 상태 | EXT.MULE.POST | return·visible | unknown |
| R04-PL06-F01 | 힙합플레이야 | 제목 | EXT.HIPHOPPLAYA.POST | visible | observed |
| R04-PL06-F02 | 힙합플레이야 | 본문 내용 | EXT.HIPHOPPLAYA.POST | visible | observed |
| R04-PL06-F07 | 힙합플레이야 | 외부 미디어 링크 (사운드클라우드·유튜브) | EXT.HIPHOPPLAYA.POST | input·visible | unknown |
| R04-PL06-F03 | 힙합플레이야 | 포스터 이미지 첨부 | EXT.HIPHOPPLAYA.POST | input·visible | unknown |
| R04-PL06-F04 | 힙합플레이야 | 오픈채팅 링크 | EXT.HIPHOPPLAYA.POST | input·visible | unknown |
| R04-PL06-F08 | 힙합플레이야 | 연락처 | EXT.HIPHOPPLAYA.POST | input·visible | unknown |
| R04-PL06-F05 | 힙합플레이야 | 게시물 ID | EXT.HIPHOPPLAYA.POST | return·visible | unknown |
| R04-PL06-F09 | 힙합플레이야 | 게시물 URL | EXT.HIPHOPPLAYA.POST | return·visible | unknown |
| R04-PL06-F06 | 힙합플레이야 | 작성 일시 | EXT.HIPHOPPLAYA.POST | return·visible | unknown |
| R04-PL06-F10 | 힙합플레이야 | 게시 상태 | EXT.HIPHOPPLAYA.POST | return·visible | unknown |
| R04-PL07-F01 | 힙합LE | 제목 | EXT.HIPHOPLE.POST | visible | observed |
| R04-PL07-F08 | 힙합LE | 말머리 | EXT.HIPHOPLE.POST | input·visible | unknown |
| R04-PL07-F02 | 힙합LE | 본문 | EXT.HIPHOPLE.POST | visible | observed |
| R04-PL07-F03 | 힙합LE | 첨부 이미지 | EXT.HIPHOPLE.POST | input·visible | unknown |
| R04-PL07-F09 | 힙합LE | 미디어 링크 | EXT.HIPHOPLE.POST | input·visible | unknown |
| R04-PL07-F04 | 힙합LE | 연락처 | EXT.HIPHOPLE.POST | input·visible | unknown |
| R04-PL07-F10 | 힙합LE | 오픈채팅 링크 | EXT.HIPHOPLE.POST | input·visible | unknown |
| R04-PL07-F05 | 힙합LE | 게시물 ID | EXT.HIPHOPLE.POST | return·visible | unknown |
| R04-PL07-F11 | 힙합LE | 게시물 URL | EXT.HIPHOPLE.POST | return·visible | unknown |
| R04-PL07-F06 | 힙합LE | 등록 일시 | EXT.HIPHOPLE.POST | return·visible | unknown |
| R04-PL07-F12 | 힙합LE | 갱신 일시 | EXT.HIPHOPLE.POST | return·visible | unknown |
| R04-PL07-F13 | 힙합LE | 노출 상태 | EXT.HIPHOPLE.POST | return·visible | unknown |
| R04-PL07-F07 | 힙합LE | 가격 | EXT.HIPHOPLE.POST | visible | observed |
| R05-PL01-F1 | 크몽 | 제목 | EXT.KMONG.PRODUCT | input | documented |
| R05-PL01-F2 | 크몽 | 카테고리 | EXT.KMONG.PRODUCT | input | documented |
| R05-PL01-F3 | 크몽 | 서비스 설명 | EXT.KMONG.PRODUCT | input | documented |
| R05-PL01-F4 | 크몽 | 패키지 설정 | EXT.KMONG.OPTION | input | documented |
| R05-PL01-F5 | 크몽 | 반려 사유 | EXT.KMONG.PRODUCT | return | documented |
| R05-PL01-F6 | 크몽 | 기본 금액 | EXT.KMONG.PRODUCT | input | documented |
| R05-PL02-F1 | 탈잉 | 클래스명 | EXT.TALING.CLASS | input | documented |
| R05-PL02-F2 | 탈잉 | 클래스 썸네일 | EXT.TALING.CLASS | input | documented |
| R05-PL02-F3 | 탈잉 | 시간당 가격 | EXT.TALING.CLASS | input | documented |
| R05-PL02-F4 | 탈잉 | 1회당 클래스 시간 | EXT.TALING.CLASS | input | documented |
| R05-PL02-F5 | 탈잉 | 총 클래스 횟수 | EXT.TALING.CLASS | visible | documented |
| R05-PL02-F6 | 탈잉 | 반려 사유 | EXT.TALING.CLASS | return·visible | documented |
| R05-PL02-F7 | 탈잉 | 일정 | EXT.TALING.SCHEDULE | input | documented |
| R05-PL03-F1 | 숨고 | 한 줄 소개 | EXT.SOOMGO.PROFILE | input·visible | reported |
| R05-PL03-F2 | 숨고 | 숨고 활동명 | EXT.SOOMGO.PROFILE | input·visible | reported |
| R05-PL03-F3 | 숨고 | 제공 서비스 | EXT.SOOMGO.SERVICE_REL | input·visible | documented |
| R05-PL03-F4 | 숨고 | 대표 서비스 | EXT.SOOMGO.PROFILE | input·visible | documented |
| R05-PL03-F5 | 숨고 | 항목 미설정 | EXT.SOOMGO.SERVICE_REL | visible | reported |
| R05-PL04-F1 | 프람피 | 분야 | EXT.PROMPIE.FIELD_REL | input | documented |
| R05-PL04-F2 | 프람피 | 지역 | EXT.PROMPIE.PROFILE | input | documented |
| R05-PL05-F1 | 뮬 | 미확인(공고 본문) | EXT.MULE.POST | input | unknown |
| R05-PL06-F1 | 힙합플레이야 | 제목 영역(별도 라벨 없음) | EXT.HIPHOPPLAYA.POST | visible | observed |
| R05-PL06-F2 | 힙합플레이야 | 본문 영역(별도 라벨 없음) | EXT.HIPHOPPLAYA.POST | visible | observed |
| R05-PL06-F3 | 힙합플레이야 | 게시 시각(표시값) | EXT.HIPHOPPLAYA.POST | visible | observed |
| R05-PL07-F1 | 힙합LE | 가격 | EXT.HIPHOPLE.POST | visible | observed |
| R05-PL07-F2 | 힙합LE | 레슨 | EXT.HIPHOPLE.CATEGORY | visible | observed |
| R05-PL07-F3 | 힙합LE | 본문 영역(별도 라벨 없음) | EXT.HIPHOPLE.POST | visible | observed |

## 6. R02 필수/선택 묶음 주장 전체

| 근거 ID | 플랫폼 | 분류 | 원문 |
|---|---|---|---|
| R02-G1-R1 | 크몽 | required | 제목 10\~30자 |
| R02-G1-R2 | 크몽 | required | 카테고리 |
| R02-G1-R3 | 크몽 | required | 서비스 설명 100\~20,000자 |
| R02-G1-R4 | 크몽 | required | 모집 형태 |
| R02-G1-R5 | 크몽 | required | 메인 이미지 1\~4장 |
| R02-G1-R6 | 크몽 | required | 서비스 제공 절차 |
| R02-G1-R7 | 크몽 | required | 의뢰인 준비사항 |
| R02-G1-R8 | 크몽 | required | 지역 |
| R02-G1-R9 | 크몽 | required | 판매 패키지 가격 |
| R02-G1-R10 | 크몽 | required | 작업 기간 |
| R02-G1-R11 | 크몽 | required | 수정 횟수 |
| R02-G1-R12 | 크몽 | required | 1회 레슨 시간 |
| R02-G1-R13 | 크몽 | required | 레슨 횟수 |
| R02-G1-O1 | 크몽 | optional | 상세 이미지·동영상 |
| R02-G1-O2 | 크몽 | optional | 검색 키워드 |
| R02-G1-O3 | 크몽 | optional | 자주 묻는 질문 |
| R02-G1-O4 | 크몽 | optional | 작업 전 요청사항 |
| R02-G1-O5 | 크몽 | optional | 대상자·서비스 내용·준비물 |
| R02-G1-O6 | 크몽 | optional | 커리큘럼 |
| R02-G1-O7 | 크몽 | optional | 수업 가능일 |
| R02-G2-R1 | 탈잉 | required | 카테고리 |
| R02-G2-R2 | 탈잉 | required | 클래스명 10\~30자 |
| R02-G2-R3 | 탈잉 | required | 대표 썸네일 1\~10장 |
| R02-G2-R4 | 탈잉 | required | 클래스 대상 50\~500자 |
| R02-G2-R5 | 탈잉 | required | 상세 소개 |
| R02-G2-R6 | 탈잉 | required | 회차와 회차별 커리큘럼 50\~500자 |
| R02-G2-R7 | 탈잉 | required | 참여 인원 |
| R02-G2-R8 | 탈잉 | required | 수강료 |
| R02-G2-R9 | 탈잉 | required | 튜터명 |
| R02-G2-R10 | 탈잉 | required | 튜터 소개 |
| R02-G2-R11 | 탈잉 | required | 프로필 사진 |
| R02-G2-R12 | 탈잉 | required | 수업 장소·상세 주소 |
| R02-G2-R13 | 탈잉 | required | 정산 정보 — 탈잉에서 본인 직접 입력 |
| R02-G2-R14 | 탈잉 | required | 사용자 확인 — 2026년 11월 27일 |
| R02-G2-O1 | 탈잉 | optional | 클래스 요약 |
| R02-G2-O2 | 탈잉 | optional | 승인 메시지 |
| R02-G2-O3 | 탈잉 | optional | 태그 |
| R02-G2-O4 | 탈잉 | optional | 유튜브 영상 |
| R02-G2-O5 | 탈잉 | optional | 클래스 공지사항 |
| R02-G2-O6 | 탈잉 | optional | 이력 |
| R02-G3-R1 | 숨고 | required | 활동명 |
| R02-G3-R2 | 숨고 | required | 한 줄 소개 |
| R02-G3-R3 | 숨고 | required | 서비스 상세 설명 |
| R02-G3-O1 | 숨고 | optional | 질문답변 5개 |
| R02-G3-O2 | 숨고 | optional | 제공 서비스 선택 |
| R02-G3-O3 | 숨고 | optional | 레슨 목적·대상 연령·성별·진행 방식 |
| R02-G3-O4 | 숨고 | optional | 사진·유튜브 영상 |
| R02-G3-O5 | 숨고 | optional | 연락 가능 시간·직원 수·외부 링크 |
| R02-G4-R1 | 프람피 | required | 프로필 제목 최대 30자 |
| R02-G4-R2 | 프람피 | required | 전문가 활동명 최대 20자 |
| R02-G4-R3 | 프람피 | required | 프로필 사진 |
| R02-G4-R4 | 프람피 | required | 주소 |
| R02-G4-R5 | 프람피 | required | 진행 방식 |
| R02-G4-R6 | 프람피 | required | 전문가 소개 |
| R02-G4-R7 | 프람피 | required | 분야별 소개 |
| R02-G4-R8 | 프람피 | required | 커리큘럼 |
| R02-G4-R9 | 프람피 | required | 비용 |
| R02-G4-O1 | 프람피 | optional | 학력 |
| R02-G4-O2 | 프람피 | optional | 경력 |
| R02-G4-O3 | 프람피 | optional | 포트폴리오 |
| R02-G4-O4 | 프람피 | optional | FAQ |
| R02-G4-O5 | 프람피 | optional | 포트폴리오 영상 설명 |
| R02-G5-R1 | 뮬 | required | 레슨 구분 |
| R02-G5-R2 | 뮬 | required | 제목 |
| R02-G5-R3 | 뮬 | required | 지역·주소 |
| R02-G5-R4 | 뮬 | required | 수강료 |
| R02-G5-R5 | 뮬 | required | 본문 |
| R02-G5-R6 | 뮬 | required | 전화번호 |
| R02-G5-R7 | 뮬 | required | 새 글 작성 시 약관 동의 |
| R02-G5-O1 | 뮬 | optional | 팩스 |
| R02-G5-O2 | 뮬 | optional | 메인 사진 |
| R02-G5-O3 | 뮬 | optional | 본문 이미지·동영상 |
| R02-G5-O4 | 뮬 | optional | 홈페이지 |
| R02-G5-O5 | 뮬 | optional | 사운드클라우드 링크 |
| R02-G6-R1 | 힙합플레이야 | required | 제목 |
| R02-G6-R2 | 힙합플레이야 | required | 본문 |
| R02-G6-R3 | 힙합플레이야 | required | 카테고리 |
| R02-G6-O1 | 힙합플레이야 | optional | 사진 |
| R02-G6-O2 | 힙합플레이야 | optional | 동영상 |
| R02-G6-O3 | 힙합플레이야 | optional | 오디오 첨부 |
| R02-G7-R1 | 힙합LE | required | 제목 |
| R02-G7-R2 | 힙합LE | required | 가격 |
| R02-G7-R3 | 힙합LE | required | 본문 |
| R02-G7-O1 | 힙합LE | optional | 레슨 분류 |
| R02-G7-O2 | 힙합LE | optional | 썸네일·사진 |
| R02-G7-O3 | 힙합LE | optional | 동영상·외부 링크 |

## 한계

- 상위 유형을 동작 대상으로 직접 허용하지 않음. 허용 목록에 구체 유형 ID가 있어야 하며 외부 항목 변경은 정확한 플랫폼 필드 규격과 편집 허용 근거 필요.
- 하위 유형은 논리적 태그/타입/값 종류이지 별도 DB 테이블을 강제하지 않는다. 일부 타입의 이름은 구체 의미 후보이며 필드값 범위(예: 수강 정원/최소/최대)는 추가 분리 필요.
- 38개 원문 객체 및 250개 직접 필드 주장, R02 묶음 주장 보존은 원문 참조 대조. 실제 동일성·필드 의미·권한 검증 아님. 추가 상세 필드 주장 374개는 별도 처리 필요.
- 모의 실행 제한 유지; 외부 25개 대상 의미 후보는 모두 실제 실행 금지. 상위 유형 및 외부 효과 정의만으로 제품 제공 범위 채택 금지.
