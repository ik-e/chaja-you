# V0.3 · 설계 검토 및 결정 현황

> [구조화 검토](review-v0.3.json) · [핵심 계약](CONTRACTS-V0.3.md) · [검증 결과](validation-v0.3.json). V0.2 대비 13개 결함을 재검토. 계약 개선은 실제 제품 채택/안전성 입증이 아니다.

## 결함 보완

| ID | 문제 | 상태 | 보완 계약 | 잔여 검증 |
| --- | --- | --- | --- | --- |
| ISSUE-01 | 승인·외부 계정 | 계약 보완 | V3-R01, V3-R10 | 실제 식별 수단·원격 인증 |
| ISSUE-02 | 동일 의도·중복 | 계약 보완 | V3-R02, V3-R03, V3-R06 | 실제 저장소 유일성·동시성 |
| ISSUE-03 | 부작용 분류 | 계약 보완 | V3-R04 | 실제 화면별 효과 조사 |
| ISSUE-04 | 철회 경쟁 상태 | 계약 보완 | V3-R03, V3-R05, V3-R06 | 강제 게이트웨이·race 시험 |
| ISSUE-05 | 상태 전이 | 계약 보완 | V3-R06, V3-R07 | worker/저장 구현 |
| ISSUE-06 | 완료 증거 | 부분 보완 | V3-R07 | 실제 플랫폼 완료 증거 |
| ISSUE-07 | 사실과 파생값 | 계약 보완 | V3-R08 | 변환 정확성 |
| ISSUE-08 | 플랫폼 규칙 | 부분 보완 | V3-R09 | 필수/옵션/VAT/효과 확인 |
| ISSUE-09 | API 타입·오류 | 논리 계약 보완 | V3-R10 | wire schema·HTTP/DB 구현 |
| ISSUE-10 | 격리·보안 | 부분 보완 | V3-R05, V3-R11 | 실제 강제·TTL·보존 |
| ISSUE-11 | AI 역할 | 계약 보완 | V3-R12 | 엔진·모델 비교 |
| ISSUE-12 | 가치 비교 | 부분 보완 | V3-R13 | 실측·합격선 |
| ISSUE-13 | 정합성 검증 | 부분 보완 | V3-R14 | 전체 의미·제품 검증 |


## 시험 계획 및 실행 구분

| ID | 시험 | 대상 문제 | 기대 결과 | 제품 시험 |
| --- | --- | --- | --- | --- |
| V3-T01 | wrong account·재인증 | ISSUE-01 | 불일치 시 admission 0 | not_run |
| V3-T02 | 새 ID·제목으로 중복 우회 | ISSUE-02 | 미확인 대상 차단 | not_run |
| V3-T03 | 동시 요청·철회 race | ISSUE-02, ISSUE-04 | 철회 이후 새 admission 0 | not_run |
| V3-T04 | 자동저장·첨부·공개 | ISSUE-03, ISSUE-08 | 미확인 효과 차단, 부분 효과 보존 | not_run |
| V3-T05 | 낡은 lease·게이트웨이 우회 | ISSUE-04, ISSUE-10 | 명령 차단, pending 효과 unknown | not_run |
| V3-T06 | 취소·인증 만료·crash | ISSUE-05 | stopping/unknown 등 올바른 전이 | not_run |
| V3-T07 | 접수·반려·상충 증거 | ISSUE-05, ISSUE-06 | 목표 완료와 후속 관측 분리 | not_run |
| V3-T08 | 사실·파생값·가격 충돌 | ISSUE-07, ISSUE-08, ISSUE-11 | 임의 사실/반올림 없음 | not_run |
| V3-T09 | API 소유권·버전·타입 | ISSUE-09 | 타 사용자/오래된 버전 차단 | not_run |
| V3-T10 | 합성 원격 인증·인계·격리·폐기 | ISSUE-01, ISSUE-10 | 동일 context 및 상호배타 제어 | not_run |
| V3-T11 | AI 예상 외 화면/외부 지시 | ISSUE-11 | 중단 후 제안, 무승인 조작 0 | not_run |
| V3-T12 | 동일 업무 A/B/C | ISSUE-12 | 활동·대기·비용·오류 분리 실측 | not_run |
| V3-T13 | 정적/추상 설계 검증 | ISSUE-13 | 참조·전이·가드·결정 DAG 검사 | not_run |


정적 검사 13/13, 추상 사례 54/54 통과. [재현 스크립트](validate-v0.3.mjs): 이 디렉터리에서 `node validate-v0.3.mjs` 실행. Boolean guard, declared transitions and evidence predicates only; no actual concurrency, browser, database, platform, API or user value execution. Prior design semantics not exhaustively proven.

## 남은 결정

| ID | 결정 | 상태 | 최종 채택 선행 결정 | 필요 근거 |
| --- | --- | --- | --- | --- |
| DEC-01 | MVP 지원 플랫폼 | open | DEC-02, DEC-04 | 공통 mock, 실제 목표·권한·가치 |
| DEC-02 | 플랫폼별 완료 범위 | partial | 없음 | 실제 등록 객체와 증거 |
| DEC-03 | 실행 구조 | open | DEC-04, DEC-05 | 원격 합성 PoC 및 로컬/혼합 비교 |
| DEC-04 | 운영사 허용 | external_unverified | 없음 | 공식 정책·운영사 허용 |
| DEC-05 | 계정·승인 결합 | contract_proposed | 없음 | 합성 wrong-account/중복/철회 검증 |
| DEC-06 | AI/코드 역할 | contract_proposed | 없음 | 정확성·예외·비용 시험 |
| DEC-07 | 실행 엔진 | open | DEC-03, DEC-06 | 동일 fixture로 엔진 비교 |
| DEC-08 | 세션 TTL·재인증 | open | DEC-03, DEC-05 | 격리·수명·폐기·비용 |
| DEC-09 | 순차/동시 등록 | open | DEC-01 | 사용자 요구·운영 자원 |
| DEC-10 | 물리 실행 단위 | open | DEC-03, DEC-06, DEC-09, DEC-15 | 게이트웨이 강제·복구·공수 |
| DEC-11 | DB·파일 저장 | deferred | DEC-10, DEC-14 | 원자성·유일성·보존 |
| DEC-12 | 스택·배포·물리 API | deferred | DEC-10, DEC-11 | 공수·환경·보안 |
| DEC-13 | 성능·비용·직접 시간 | open | 없음 | 동일 목표 A/B/C 실측 |
| DEC-14 | 개인정보·로그·보존 | open | DEC-03, DEC-08 | 처리 위치·법·삭제 검증 |
| DEC-15 | 장애 복구·통지 | partial | DEC-03, DEC-05 | crash·lease·중단 검증 |
| DEC-16 | PoC 재사용 | open | DEC-06, DEC-07, DEC-10 | 공통 harness·코드 검토 |
| DEC-17 | 이행·환불 | deferred | DEC-01, DEC-02, DEC-04, DEC-13 | 허용 범위·가치·원가 |


기존 LR-D01~06의 세분화 검토 후보. 최종 채택 의존성이지 조사/PoC 진행 순서 강제 아님. TASK-043~045 변경 없음, TASK-046 제안 미등록.

## 설계 준비도

| 영역 | 상태 | 다음 확인 |
| --- | --- | --- |
| L0/L1 기획·문제 | 기존 V1.1 유지 | 시장·사용자 가치 실증 |
| L2 요구사항 | 논리 수용 조건 상세화 | 성능·비용 및 MVP 목표 |
| L3 도메인 | 계정·승인·의도·효과·결과 계약 보완 | 실제 객체/효과/식별 증거 |
| L4 실행 구조 | 역할/게이트웨이 후보 상세화 | 원격 인증·격리·엔진·물리 단위 |
| L5 상세 설계 | 데이터·API·상태·사용자 흐름 논리 계약 | DB/HTTP/UI 물리 구현·보안 |
| L6 검증 | 정적 및 추상 모델 검사 완료 | 공통 mock·실행·장애·가치 검증 |
| L7 WBS | 대기 | R01 채택 판단 이후 구현 배정 |

## 사용자 가치 검증

비교군: direct, general_ai, dedicated. 통제: source, media, platform, goal, initial_state, permission, quality. 관측: active_user_seconds, system_seconds, review_wait_seconds, interventions, rework, fact_errors, unauthorized_mutations, duplicate_effects, goal_verdict, cost, willingness_to_pay. R02의 3채널 20~30분은 희망 목표; 아직 실측되지 않음.

## 다음 단계

1. R03~05의 공통 모의 계약 검증(11/26 목표) 및 원격 브라우저 합성 PoC 제안(미배정).
2. 실제 플랫폼별 객체/효과/증거·운영사 허용의 근거 확인. 실제 계정/로그인/등록 금지 유지.
3. 11/27 R01 기술·범위 채택 판단. 이후 물리 API/DB/배포·본 구현 WBS. 팀원 TASK 및 main 미변경.
