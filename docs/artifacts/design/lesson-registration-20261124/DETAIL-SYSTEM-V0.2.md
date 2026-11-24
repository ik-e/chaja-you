# L4/L5 · 시스템 책임·사용자 흐름·인터페이스·인증

> 2026-11-24 · R01 V0.2 상세 설계 검토 초안. 최종 채택 및 실서비스 실행 승인 아님. [구조화 정본 후보](detail-design-v0.2.json) · [근거·검토 안내](README.md)

V0.1 논리 책임 6개 유지. 지금 확정하는 것은 입력/출력·가드·책임 경계의 제안이며, 프로세스/서비스 수, DB, 프레임워크, 실행 엔진은 미채택. 원격 브라우저는 C 후보의 구체화로 합성 로그인에만 적용한다.

## S-A. 논리 모듈 상세

| ID | 책임/부모 | 입력 → 출력 | 금지·실패 경계 |
| --- | --- | --- | --- |
| C01a | LR-C-01 원본/자료 | 원문·확인값·이미지 → source_version, facts, issues | AI 사실 후보만; 권리/충돌 확인 |
| C02a | LR-C-02 규칙/변환 | source+platform rule → draft_version, field mappings, questions | 플랫폼별 매퍼 분리; 엔진으로 사실 생성 금지 |
| C03a | LR-C-03 승인/권한/의도 가드 | approval+permission+intent+job+lease → allow/deny(reason) | 동작 직전 검사, unknown/중복/철회/live 차단 |
| C04a | LR-C-04 실행 오케스트레이션/adapter | 승인된 step+opaque session handle → attempt/observations | 실행기는 정책·성공 단독 확정 금지; mock origin 고정 |
| C04b | LR-C-04 세션/제어권 경계 (후보) | connection/lease → human view or worker capability | 로그인 중 AI 접근 없음; 합성 전용; 동시 제어 금지 |
| C05a | LR-C-05 결과/복구 | attempt+관측+goal → result_revision, next_action | 외부 효과 불명확 unknown, 부작용 없는 재확인 |
| C06a | LR-C-06 웹 UI/API | 사용자 명시 입력·결정 → 위 논리 호출; 상태/증거 표시 | 외부 자격증명을 우리 서비스 폼에 넣지 않음 |
| C07a | 공통 저장/감사 포트 (물리 미정) | immutable snapshot/attempt/result; owner-scoped 조회 | 실행 중 상태 손실 대비; 민감정보 기록 금지; 삭제 정책 미정 |

## S-B. 우리 서비스 사용자 흐름 (TO-BE, 화면 후보)

| ID | 화면/행동 | 표시 및 요청 | 이동·예외 |
| --- | --- | --- | --- |
| U01 | 원본 입력 | 기존 원고, 확인된 레슨 조건, 사진·권리, 공개 범위 | 구조화 → U02; 빈 값/상충은 질문; 로그인 요구 전 정보 준비 가능 |
| U02 | 대상 및 목표 선택 | 크몽 상품 / 숨고 서비스 설정 후보; 탈잉 연구 표시 | 객체·선행조건·지원 범위 표시. current mock only; 각 대상 독립 |
| U03 | 플랫폼별 초안 검토 | 원본 대비 변환값, 가격/단위, 이미지 preview, 필수 누락, 규칙 출처 | 사용자 수정 → 새 version; 전용 추가 질문 → U01/U03 |
| U04 | 승인/실행 준비 | 대상 객체/목표·환경·승인 동작, 변경 시 재승인 안내 | 권한·승인 확인, live 불가. 원격 인증 후보 U05; 승인과 인증 별개 |
| U05 | 계정 연결/원격 화면 (후보) | 합성 로그인 전용 화면; 로그인·추가 인증은 사용자; 화면 기록 OFF | 사용자가 완료 → 인증 상태 최소 관측 → 제어권 반환/인계. 만료/취소는 needs_action |
| U06 | 실행/중단/사용자 개입 | 현재 step, 마지막 확인 시점, 사람 개입 사유, 중단 | 비동기 서버 작업 후보; 모의 실행만. 추가 결정 시 정지, 승인 영향 재확인 |
| U07 | 결과/증거 | 대상별 목표/환경, 입력·저장/접수·심사·공개 구분, 근거/오류 | unknown → U08; 독립 결과 유지. 실제 게시 상태를 모의 결과로 표시하지 않음 |
| U08 | 재확인 및 재개 | 기존 효과 조회, 가능한 다음 조치, 재승인 요구 | 이미 성공은 상태만 수정, 불명확은 차단, 안전한 다음 단계+현재 승인 확인 후 별도 시도 |

## S-C. 논리 API → HTTP 후보 (구현 지시 아님)

| ID | 동작/후보 경로 | 요청 핵심 | 응답 핵심 | 가드/오류 |
| --- | --- | --- | --- | --- |
| A01 | prepare_source POST /v1/sources | source_text, facts[], media_versions[], prior_version? | source_ref/version, facts[], issues[] | owner, rights; 422 missing/conflict, 수정은 새 버전 |
| A02 | prepare_draft POST /v1/drafts | source_ref/version, platform, object_kind, rule_version, target_goal | draft_ref/version, field_mappings[], issues[], digest | rule/object unknown, unsupported value; 422/409 |
| A03 | 수정 PATCH /v1/drafts/{ref} | expected_version, explicit field edits | new draft_version, digest, issues | 409 stale; 확인되지 않은 사실은 원본 수정/재검토 |
| A04 | record_approval POST /v1/approvals | source/draft/rule/media versions, target, environment, actions, digest, explicit consent | approval_ref, scope_digest, status | 409 stale, 422 unresolved, 403 scope; 철회 endpoint 별도 |
| A05 | plan_and_check_execution POST /v1/jobs | intent_ref/target_slot, approval_ref, requested environment/actions, idempotency_key | job_ref, state, retry_blocked, reasons | 서버가 permission 평가; 동일 intent/operation 키 및 기존 효과 검사; 403 live,409 duplicate |
| A06 | execute_approved_action 내부 worker command | job_ref, step_id, operation_id, expected_revision, lease_generation? | attempt_ref, observations[], error_code | 직전 원자 가드, 기록 후 단일 동작; 외부에서 직접 호출 불가 |
| A07 | read_result GET /v1/jobs/{ref} | owner context, after_revision? | state, target_goal, observed_stage, result_revision, evidence_refs, next_action, retry_blocked | 소유자 검사; 증거 조회 읽기 전용 |
| A08 | reconcile POST /v1/jobs/{ref}/reconcile | expected_revision, evidence_refs/user observation | updated result, safe_next_step?, retry_blocked | 재확인만, 증거 부족이면 unknown |
| A09 | resume POST /v1/jobs/{ref}/resume | expected_revision, explicit_resume, current approval_ref | state, safe_step, reasons | 현재 승인·permission·인증 재검사; unknown 중 효과 반복 금지 |
| A10 | cancel / revoke POST /v1/jobs/{ref}/cancel, /v1/approvals/{ref}/revoke | expected_revision, reason | state, lease_revoked, pending_effect? | 새 동작 차단. 이미 시도된 효과 불명확하면 unknown |
| A11 | connection/lease 후보 POST /v1/connections, /{ref}/handoff, /{ref}/close | platform, mock, owner, expected_generation, action | opaque connection_ref, auth_state, controller, expiry | 접속 URL/토큰은 짧은 수명·권한 범위, 일반 로그 미포함; live 차단 |

## S-D. 작업/관측/오류 상태 계약 보완

| ID | 조건 | 표현/효과 | 다음 행동 |
| --- | --- | --- | --- |
| ST01 | 필수값/권리/규칙/선행조건 미해결 | draft needs_confirmation / job needs_action; reason_code, field_key | 사용자 확인·새 버전·재승인 |
| ST02 | 현재 mock 권한 없음 / live 요청 / 타 사용자 | blocked 또는 접근 거부; 실행 0 | 권한 재검토, 현재 live 해제 금지 |
| ST03 | 실행 중 세션 만료/추가 인증, 효과 미발생 확인 | needs_action, auth_required, checkpoint | 사용자 재인증 후 가드·승인 재검사 |
| ST04 | 입력/업로드 실패 및 해당 동작 효과 없음 입증 | failed 또는 needs_action; last_verified_step | 수정 후 명시 재개, 승인 변경 시 재승인 |
| ST05 | 제출/저장 직후 응답 유실, 프로세스 중단 또는 충돌 | unknown, retry_blocked=true; attempt/evidence refs | 읽기 전용 재확인; 실패/취소로 강등해 재시도 금지 |
| ST06 | 목표 mock receipt 또는 설정 재조회 일치 | mock_completed, observed_stage platform_specific/receipt_confirmed | 실제 target_confirmed 금지; 결과 revision 기록 |
| ST07 | 사용자 중단 또는 권한 철회 | 추가 부작용 0, 진행 중 효과 불명확 unknown; 효과 없음 확인 시 cancelled | 제어권 제거, 재확인만 |
| ST08 | 타 플랫폼 job 상태 변경 | 해당 job/result만 업데이트 | 다른 대상은 그대로; 복수 동시 실행 미채택 |

## S-E. 원격 브라우저 후보 세션·제어권 수명주기

| ID | 상태/전이 | 가드·구현 요구 | 관측/실패 |
| --- | --- | --- | --- |
| RB01 | created → human_control | 사용자별 격리 브라우저 생성; 인증된 우리 서비스 사용자의 short-lived view grant; loopback synthetic only | 다른 사용자 접속 차단; worker/LLM 캡처·DOM 관측·trace·입력 기록 금지 during auth |
| RB02 | human_control → auth_check | 사용자가 직접 모의 계정 로그인하고 완료 요청; 원격 입력 lease 회수/세대 증가 | 인증 성공은 보호 페이지 또는 합성 auth marker 확인; 입력 내용/쿠키/비번 읽지 않음 |
| RB03 | auth_check → automation_control | 동일 instance/context, auth state verified; permission+approval+intent+lease generation 확인 | worker만 제어. 사람과 자동화 동시 입력 불가; 외부 실제 계정/토큰 없음 |
| RB04 | automation_control → running/disconnected viewer | 뷰어 연결 종료와 작업 생명주기 분리; 승인 범위 안에서만 worker 실행 | 사용자 웹 탭 닫혀도 모의 작업 완료 가능성 시험; 실제 계정은 미검증 |
| RB05 | automation_control → needs_human | 추가 인증/차단/결정/예상 외 화면; worker 중지·lease 회수 확인 후 사람에 인계 | 시도 중 외부 효과 불명확하면 job unknown; 인증과 재개는 별개 |
| RB06 | needs_human → auth_check → automation_control | 재인증/사용자 결정, 현재 버전·권한·기존 효과 확인 | 새 내용 승인 필요하면 U03/U04. 동일 의도 unknown이면 조회만 |
| RB07 | any → closing → closed | 중단/만료/철회; view grant, worker lease, 브라우저 프로세스 및 임시 프로필 폐기 | 폐기된 연결 접근 불가; 외부 플랫폼의 전역 로그아웃과는 별개. 폐기 실패 경고/격리 |
| RB08 | crash / heartbeat lost | lease 만료 후 이전 worker fencing; attempt 상태 durable; 복구 전 read-only 확인 | in-flight effect unknown; 자동 재제출 금지. 브라우저 상태 보존·장기 세션은 미채택 |

## S-F. 보안·배치 후보와 기술 판단

| ID | 항목 | 현 단계 / 채택 조건 |
| --- | --- | --- |
| SEC01 | 신뢰 경계 | 우리 서비스 인증/사용자 데이터/외부 인증/운영사 허용 분리. mock 사용자만. 플랫폼 사이트가 사용자 승인 대신 권한을 준다고 추정 금지. |
| SEC02 | 원격 접속 | noVNC+websockify+x11vnc+Xvfb+Chromium/Playwright 후보 또는 관리형 서비스. 실험 로컬/격리. VNC·CDP 포트 외부 직접 노출 금지; 서비스 공개 시 HTTPS/WSS·인증·세션별 ACL 필요. |
| SEC03 | 인증 정보 | 사용자 원격 입력 중 AI·스크린샷 기록·세션 덤프 차단. 서버가 인증 세션을 보유한다는 민감성 유지; 실제 로그인/쿠키 수집/재사용은 승인 전 금지. MFA/CAPTCHA/본인 인증 우회 금지. |
| SEC04 | 브라우저 권한 | 대상 origin 및 허용 경로·행위 제한; navigation/redirect 검증, 파일 업로드는 승인 asset만. 화면 표시만으로 접근 통제했다고 보지 않음. |
| SEC05 | 실행 방식 | 단일 앱+독립 worker/로컬 혼합/서버 브라우저/API/수동 보조 후보; durable job/queue는 책임만 정의. FastAPI, SQLite, Skyvern은 R03 실험의 증거이지 제품 채택 아님. |
| SEC06 | AI 경계 | LLM은 사실 추출·문안 변환 후보만. 가격/횟수/권리/승인/정책/결과는 결정적 검사 및 사람 확인. 브라우저의 외부 텍스트는 데이터, 시스템 지시 아님. |
| SEC07 | 저장·배포 | 개발: loopback, synthetic fixture, 독립 manifest/lock. 제품: 저장 위치, 암호화/키, worker 격리, 감사, 장애·삭제·백업·운영비는 LR-D03/04/06 이후. |
| SEC08 | 운영사·자료 | 공식 허용, 강사 동의, 플랫폼별 위임 범위와 본인인증, 외부 모델/호스팅의 처리 위탁 검토. 가격·비용·정산·메시지 자동화는 별도 결정. |

## 적용 경계

예시 호출 순서: A01 → A02 → A03(필요 시) → A04 → A05 → A11(합성 인증·인계) → A06 반복(동작별 가드) → A07; unknown이면 A08 후 A09는 안전한 다음 단계가 확인될 때만. 작업 생성은 외부 부작용이 아니다. 원격 브라우저 인증이 필수가 아닌 mock simulator에서는 A11을 생략하되 실제 인증 성공으로 표시하지 않는다. HTTP 경로·응답 코드는 구현 검토 후보이며 기존 R03 시험 계약을 대체하지 않는다.
