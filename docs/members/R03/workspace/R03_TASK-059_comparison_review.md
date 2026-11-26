# TASK-059 | R03 독립 사용자 스토리 비교·누락 검토 (2차 초안)

**2026-11-26 · V1.2 · R01 승인 전 · 외부 실행 및 GitHub 수정 없음**

독립 기준: `R03_TASK-059_F01-E05_user-stories_draft.json` (SHA-256 `602bbbaddb6dca379afcbadeaf88d93914f33527bb565b6873c6be05dd17c32c`), 98개 사용자 행동 / 48개 시스템 이벤트. 기존 ID/원본 명세/피처 커버리지를 그대로 보존하였다.

## 1. 비교 근거와 기준

|담당|스토리 수|원본 commit / blob|상태|
|---|---:|---|---|
|R02|32|[원본](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json) · `3f4924c5fc11` / `e14d4f802b60`|진행 중 · 크몽 상세 보완, 나머지 플랫폼 조사 계속|
|R04|39|[원본](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json) · `3f4924c5fc11` / `b7f4cb3e0ca3`|재검증 보완 · 미확인 및 계약 잔여사항 명시|
|R05|47|[원본](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json) · `3f4924c5fc11` / `98271e64f02a`|독립 조사 작성 · 통합 검토 대기|
|R01|63|[원본](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json) · `3f4924c5fc11` / `62e92b26a95d`|통합 초안 · 승인 전 · R04/추가 근거 대기|

R05 조사 브랜치 `codex/r05-task-057-research`의 commit `8e2820a0ef64aa361cc6cc0b6f0811bf54a728ec`와 main 파일의 blob이 동일하다. R01 통합 브랜치 `b5bd2221f882b7eccf9b9e13e9811c46c25c2b6a`도 main의 통합 파일과 동일하다. 통합 파일은 R02/R05의 이전 원본 및 R04 미제출 당시 원본을 참조하므로 최신 개별 원본을 별도로 대조하였다.

M = 의미 일치, S = 단일 행동 분리 대응, P = 부분 대응(조건·분기·범위 차이), G = 별도 행동 누락 후보. G에 붙인 R03 ID는 관련 문맥이며 대응으로 집계하지 않는다. 동일 후보가 여러 원본에 있을 수 있어 G 개수를 신규 기능 수로 볼 수 없다. 원본 action 기준의 의미 대조이며 실제 플랫폼·상태·필드 전수 검증이나 전체 분기 완전성 판정은 아니다.

|원본|M|S|P|G|합계|
|---|---:|---:|---:|---:|---:|
|R02|17|6|5|4|32|
|R04|20|7|11|1|39|
|R05|18|6|15|8|47|
|R01|27|6|15|15|63|
|합계|82|25|46|28|181|

## 2. 주요 발견 및 R01 결정 요청

### R03-C01 · 원본 보관·목록 조회 (높음)

원본: [R05-US-005](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-005](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [R04-US-002](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json)

R03: R03-US-009, R03-US-010, R03-US-014, R03-US-015

원본 선택/저장 결과/재요청은 있으나 최초 보관 요청과 목록 조회는 별도 행동으로 없음.

**행동/수정 후보:** 강사는 레슨 원본의 보관을 요청한다. / 강사는 저장된 레슨 원본 목록을 조회한다.

**범위/결정:** F02·F05; 명시 저장 방식과 목록 필요성 미결정(D04).

### R03-C02 · 외부 판매글 임시 저장·재열기 (높음)

원본: [R02-US-027](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R02-US-028](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json)

R03: R03-US-009, R03-US-014, R03-US-015

크몽에서 작성 중 판매글을 임시 저장하고 다시 여는 후보. 우리 서비스의 원본 저장과 외부 플랫폼의 초안 저장은 다른 객체·외부 효과. R02 근거 R02-EV-KMONG-USER-20261126(사용자 조사 기록); 실행·권한은 미확인.

**행동/수정 후보:** 강사는 외부 판매글의 임시 저장을 요청한다. / 강사는 외부 임시 판매글의 열람을 요청한다.

**범위/결정:** undecided. F05/F02는 관련 근거일 뿐 외부 저장을 기본 피처로 확정하지 않음. D04/D10.

### R03-C03 · 중단된 기본 작업의 재개 (높음)

원본: [R02-US-026](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [IS-050](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-068, R03-US-070, R03-US-071

R03은 실패 재처리·중단·보류를 구분했으나 실패하지 않은 중단 업무의 재개 요청은 별도로 없음.

**행동/수정 후보:** 강사는 중단된 업무의 재개를 요청한다.

**범위/결정:** undecided. 원본·대상·권한·승인·미확인 효과 재확인; 기존 승인 무조건 재사용 금지. D06/D08.

### R03-C04 · 심사 접수 취소와 재심사 (높음)

원본: [R02-US-029](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R02-US-030](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R05-US-036](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-036](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-025, R03-US-027, R03-US-048, R03-US-051, R03-US-066, R03-US-068, R03-US-070

내부 취소와 이미 접수된 외부 심사 취소는 다름. 반려 보완과 재심사도 무조건 같은 요청의 재시도는 아님. R05 공식 안내 참조 R05-EV-05, R02 사용자 기록; 실제 실행 허용 미확인.

**행동/수정 후보:** 강사는 외부 심사 접수 취소를 요청한다. / 강사는 보완한 판매글의 재심사를 요청한다.

**범위/결정:** 취소는 undecided, 재심사는 F20/F29 분기 후보; 외부 상태 확인·새 승인 선행. D06/D08/D10.

### R03-C05 · 업무 선택·승인·실행 요청의 관계 (높음)

원본: [R05-US-020](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-021](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-022](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-020](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-021](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-022](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [R04-US-036](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json)

R03: R03-US-009, R03-US-018, R03-US-019, R03-US-020, R03-US-021, R03-US-048, R03-US-051

R03은 업무 선택과 실행 승인만 기록. R05/R01은 승인 후 신규 등록·수정·갱신 요청을 별도 행동으로 작성. 실행 승인이 곧 요청인지 별도 요청이 필요한지 미정.

**행동/수정 후보:** 강사는 승인된 신규 등록을 요청한다. / 강사는 승인된 게시물 수정을 요청한다. / 강사는 승인된 공고 갱신을 요청한다.

**범위/결정:** F19~21 연결 후보. 별도 버튼/승인 뒤 추가 클릭 필수화 금지; 논리 분리 또는 승인에 병합 결정(D11).

### R03-C06 · 부분 성공 시 미완료 대상 선택 (높음)

원본: [R05-US-029](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-029](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-046](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [R04-US-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json)

R03: R03-US-022, R03-US-055, R03-US-062, R03-US-068, R03-US-069

플랫폼별 결과 확인은 있으나 이후 미완료 대상 선택 및 인증 실패 플랫폼만 건너뛰는 분기가 뚜렷하지 않음.

**행동/수정 후보:** 강사는 미완료 업무 대상을 선택한다. / 강사는 인증에 실패한 플랫폼의 업무를 제외한다.

**범위/결정:** F07/F24/F29. 성공 대상 재실행 금지; 실패/미확인 분리, 미확인 효과 조회 우선. D08/D10.

### R03-C07 · 준비 작업 실패 후 재준비 (높음)

원본: [IS-057](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-024, R03-US-027, R03-US-050, R03-US-068

외부 실행 전 변환·검증 작업의 실패/시간 초과와 실행 후 실패는 의미가 다름. R01의 강사 의견 A3에서 유래한 후보.

**행동/수정 후보:** 강사는 실패한 입력안 준비 작업의 재수행을 요청한다.

**범위/결정:** F08~F10; 이전 초안·원본 버전 유지, 늦은 응답 덮어쓰기 방지. 신규 실행 재처리와 분리.

### R03-C08 · 서비스 자체 계정·작업 공간 (높음)

원본: [R05-US-042](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-042](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-051](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-052](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-053](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-062](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-063](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-001, R03-US-002, R03-US-072, R03-US-075

R03 로그인·로그아웃은 있으나 계정 등록, 자체 인증 실패 확인, 계정 삭제, 본인 작업 공간 선택은 별도 행동 없음. 외부 플랫폼 계정 가입과 혼동 금지.

**행동/수정 후보:** 강사는 서비스 계정 등록을 요청한다. / 강사는 서비스 계정 인증 실패 사유를 확인한다. / 강사는 서비스 계정 삭제를 요청한다. / 강사는 본인의 작업 공간을 선택한다.

**범위/결정:** undecided, 서비스 자체 계정 필요성·복구·소유권 검토(D01/D05/D09).

### R03-C09 · 대행 불가 시 직접 작성용 자료 (높음)

원본: [IS-059](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [R05-US-039](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json)

R03: R03-US-016, R03-US-017, R03-US-023

지원 범위 확인/입력안 검토는 있으나 대행 불가 시 강사가 직접 작성할 자료를 받는 대안 경로는 별도 없음. R05-DEC-2에서 도출된 후보.

**행동/수정 후보:** 강사는 직접 작성용 레슨 자료를 확인한다.

**범위/결정:** undecided; 대행 성공으로 표시하지 않음, 사용자 가치 검증. D10/D11.

### R03-C10 · 심사 승인과 실제 모집 가능 구분 (높음)

원본: [R05-US-041](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-041](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-058](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-055, R03-US-057, R03-US-067

탈잉 승인 후 최초 모집 일정 준비 여부를 별도 확인한다는 후보. R05-EV-05/06(공식 안내 참조); 실제 대행 가능 여부 미확인.

**행동/수정 후보:** 강사는 심사 승인 후 남은 모집 준비를 확인한다. / 강사는 최초 모집 일정 설정을 요청한다.

**범위/결정:** 확인 행동 F24/F29 분기, 일정 설정은 undecided. 전체 수업 일정 관리는 제외 유지(D10).

### R03-C11 · 삭제·연결 해제 범위 수정 권고 (높음)

원본: [R04-US-025](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-039](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-034](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-035](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-034](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-035](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-072, R03-US-073

V1.2 §9.5는 내부 원본 삭제 및 외부 게시물 관리 연결 해제 요청을 명시한다. R03의 요청 자체 undecided 분류는 과도하게 보수적. R04의 F05 직접 연결은 저장과 삭제 혼동 가능.

**행동/수정 후보:** 기존 072·073의 action 유지, base 후보로 변경 검토. 처리 정책만 미결정으로 유지.

**범위/결정:** 외부 게시물 삭제 아님. 데이터 보존·진행 중 업무·권한 해제는 D09에서 결정.

### R03-C12 · 미확인 결과의 확인 요청과 안전한 재처리 (높음)

원본: [R04-US-026](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-026](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-026](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-063, R03-US-068, R03-US-069

R03은 사용자 별도 확인 요청을 undecided, 다른 팀은 base로 분류. V1.2 §5.8·§9.3 기존 외부 효과 확인 필수, 사용자 별도 요청 방식은 미정.

**행동/수정 후보:** 069를 F26 상태 갱신 요청의 특수 분기 또는 독립 행동으로 정리.

**범위/결정:** 시스템 확인 의무는 기본, UI·요청 단계만 결정. 계속 미확인 시 재실행 금지(D08).

### R03-C13 · 플랫폼 특화 정보·객체·정책 (중간)

원본: [R02-US-031](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R02-US-032](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R05-US-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-039](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-040](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-043](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-044](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-045](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-046](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-047](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-039](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-040](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-016, R03-US-017, R03-US-023, R03-US-024, R03-US-025, R03-US-026, R03-US-028, R03-US-029, R03-US-040, R03-US-041, R03-US-042, R03-US-047, R03-US-048

크몽 가격 검증·장소 협의·패키지, 탈잉 회차/수강료, 숨고 대표 서비스 및 매칭 조건, 프람피 단계, 뮬 검색·식별, 게시판 과정별 가격은 공통 행동의 구체 조건이거나 신규 지원 후보. R05 상세 근거 및 R02 사용자 기록을 참고; 필수값·실제 결과·권한 검증 아님.

**행동/수정 후보:** 공통 스토리의 입력·검증·분기 구체화. 강사는 대표 서비스 후보를 지정한다. (별도 범위 검토)

**범위/결정:** 대표 서비스·검색 방식·연락처 공개 범위는 undecided. 구체 규격·환산·공개 연락처 자동 변환 확정 금지(D10).

### R03-C14 · 검토와 승인·거절의 분리 (중간)

원본: [R02-US-014](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R02-US-015](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R04-US-011](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-012](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-023](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-031](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-032](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-037](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-018](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-018](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-023, R03-US-034, R03-US-042, R03-US-047, R03-US-048, R03-US-049, R03-US-050, R03-US-051, R03-US-052, R03-US-053

R03은 정보 승인·실행 승인 및 각 거절을 분리. R02는 복합 행동, R04는 검토/승인을 별도 명시하되 검토 inputs에 승인 클릭 포함. 기존 승인 철회와 최초 거절도 분리 필요.

**행동/수정 후보:** 강사는 최종 등록 정보를 검토한다. / 강사는 실행 범위를 검토한다.

**범위/결정:** 승인은 논리적으로 구분, 한 승인 과정 허용. 검토를 별도 강제 단계로 확정하지 않음(D11).

### R03-C15 · 모니터링 설정 항목의 차이 (중간)

원본: [R04-US-018](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R02-US-021](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R02/independent-result.json), [R05-US-030](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-030](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-077, R03-US-078, R03-US-079, R03-US-080, R03-US-081, R03-US-082, R03-US-083, R03-US-084

R03은 대상·범위·기간·알림 조건을 별도 행동으로 기록. R04는 조회 주기·알림 채널까지 제안. V1.2는 사용자 지정 주기/채널을 확정하지 않음.

**행동/수정 후보:** 강사는 자동 조회 주기를 설정한다. / 강사는 알림 수신 채널을 선택한다.

**범위/결정:** 조건부 미결정, 플랫폼 제한·비용 및 기본값 검토. 임의 6시간·횟수 정책 확정 금지(D12/D13/D15).

### R03-C16 · 자동 조회·알림·종료 경계 (높음)

원본: [R04-US-019](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-034](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-035](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-032](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [R05-US-033](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-031](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-032](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-033](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-061](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-086, R03-US-087, R03-US-088, R03-US-089, R03-US-090, R03-US-091, R03-US-092, R03-US-093, R03-US-094, R03-US-095, R03-US-096, R03-US-097, R03-US-098

R03은 위험 확인·승인·거절·철회·종료/해제 결과와 종료 미확인을 세분화. R04의 세션 파기 요청을 구현하려면 철회·종료와 별도 기능인지 검토. R05의 알림 근거는 E04 사용자 행동, E03 자동 조회는 시스템 이벤트.

**행동/수정 후보:** 기존 후보 유지; 승인 만료·권한 철회 시 접근 차단 및 관련 세션 폐기, 종료 미확인 표시.

**범위/결정:** 조건부. 조회 전용 권한, 기본 업무 종료 후 세션 유지 금지. D14~D17.

### R03-C17 · R03 자체 의미 중복·분기 정리 (중간)

원본: [R04-US-022](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-028](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-007](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-007](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-024](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json), [IS-027](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-009, R03-US-010, R03-US-018, R03-US-019, R03-US-020, R03-US-021, R03-US-023, R03-US-040, R03-US-041, R03-US-042, R03-US-048, R03-US-051, R03-US-055, R03-US-056, R03-US-058, R03-US-059, R03-US-060, R03-US-062, R03-US-063, R03-US-064, R03-US-065, R03-US-066, R03-US-067, R03-US-068, R03-US-069

원본 목록/선택, 대상 확인/지정, 결과/근거, 마지막 관측/이력, 조회 요청/미확인 확인, 대응 안내/사유, 실패 재처리/재개를 비교. 의미가 같으면 한 ID 재사용하고 trigger/입력·분기를 보완.

**행동/수정 후보:** 기존 ID 유지하고 통합 시 중복 후보를 R01에 제시.

**범위/결정:** 같은 표현 수량 검사와 의미 완전성은 다름. UI 버튼 수/강제 절차 증가 방지.

### R03-C18 · 권한·검증 근거의 강도 및 제안 충돌 (높음)

원본: [R04-US-012](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-018](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-036](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R04-US-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R04/independent-result.json), [R05-US-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/R05/independent-result.json), [IS-038](https://github.com/ik-e/chaja-you/blob/3f4924c5fc1153a641987eaf1b5e2bdc937b569f/docs/artifacts/planning/lesson-registration-20261126/integrated/user-stories.json)

R03: R03-US-017, R03-US-022, R03-US-029, R03-US-033, R03-US-035, R03-US-045, R03-US-053, R03-US-074, R03-US-081, R03-US-087, R03-US-095

R04 승인 취소 후 세션 유지 대기, 인증 3회 제한, 플랫폼 단위 기등록 차단, 모니터링 주기 자동 보정은 미채택 제안. V1.2 기본 작업 종료·철회 시 세션 폐기, 동일 레슨/계정/외부 객체와 다중 객체 관계 고려. R05 대표 서비스 base와 R01 undecided 차이.

**행동/수정 후보:** 허용 범위와 상태/대상/종료를 명확히 재검토.

**범위/결정:** 안 A 연락처·가격 분리 방향도 최종 DB/변환 규칙 승인 아님. 실제 외부 실행/정책 추정 금지.

## 3. 원본별 전수 명시 행동 대조 (181행)

### R02 · 32개

|원본 ID|구분|R03 대응 또는 관련 문맥|검토 메모|
|---|---|---|---|
|R02-US-001|S|US-003, US-004, US-006|원본+사진 제공 분리|
|R02-US-002|M|US-009|저장 원본 선택|
|R02-US-003|M|US-013|원본 수정|
|R02-US-004|S|US-016, US-017|지원 업무와 제약 확인|
|R02-US-005|S|US-018, US-019, US-020, US-021|대상과 업무 선택 분리|
|R02-US-006|M|US-025|누락 정보 제공|
|R02-US-007|M|US-026|불확실 정보 확인|
|R02-US-008|M|US-029|제약 대안 선택|
|R02-US-009|P|US-030, US-070, US-022|대안 없음의 명시적 업무 종료와 거절·제외 구분|
|R02-US-010|M|US-031|외부 로그인|
|R02-US-011|M|US-034|계정 확인|
|R02-US-012|M|US-041|관리 게시물 선택|
|R02-US-013|M|US-046|변경 전후 확인|
|R02-US-014|S|US-048, US-051|정보 승인과 실행 승인|
|R02-US-015|S|US-049, US-052|두 승인 거절 분리|
|R02-US-016|M|US-055|플랫폼별 결과|
|R02-US-017|M|US-059|마지막 확인 상태|
|R02-US-018|M|US-063|상태 갱신 요청|
|R02-US-019|M|US-064|상태 변화와 결과|
|R02-US-020|P|US-057, US-066|대응 안내와 원인 검토, 안내의 목적을 명확히|
|R02-US-021|S|US-077, US-078, US-079, US-080|모니터링 대상·조건 분리|
|R02-US-022|M|US-087|인증 유지 승인|
|R02-US-023|M|US-092|알림 확인|
|R02-US-024|M|US-094|모니터링 종료 요청|
|R02-US-025|M|US-070|작업 취소/중단 요청; 실제 취소 가능 시점 미정|
|R02-US-026|G|관련 문맥: US-068, US-071|중단된 기본 작업의 재개 요청(실패 재처리와 별개)|
|R02-US-027|G|관련 문맥: US-014, US-015|외부 판매글 임시 저장(내부 원본 저장과 별개)|
|R02-US-028|G|관련 문맥: US-009, US-010|외부 임시 판매글 재열기|
|R02-US-029|G|관련 문맥: US-070|외부 심사 제출 취소(내부 작업 취소와 별개)|
|R02-US-030|P|US-025, US-027, US-048, US-051, US-068|반려/판매글 수정 후 재심사 접수 요청의 분리 검토|
|R02-US-031|P|US-024|가격 상한·패키지 검증 오류는 기존 행동의 구체 분기|
|R02-US-032|P|US-028, US-029|오프라인 장소 협의 가능 여부는 구체 선택값; 실제 조건 필요|

### R04 · 39개

|원본 ID|구분|R03 대응 또는 관련 문맥|검토 메모|
|---|---|---|---|
|R04-US-001|S|US-003, US-006|원본 텍스트·수업 조건|
|R04-US-002|G|관련 문맥: US-009, US-010|저장 원본 목록 조회(원본 선택 전)|
|R04-US-003|M|US-013|원본 필드 수정|
|R04-US-004|S|US-016, US-017|지원 및 제약 열람; 화면 종속 제거|
|R04-US-005|M|US-018|플랫폼 선택|
|R04-US-006|M|US-025|누락 보완|
|R04-US-007|M|US-029|대안 선택|
|R04-US-008|M|US-031|직접 로그인|
|R04-US-009|M|US-040|기존 객체 후보 확인|
|R04-US-010|M|US-046|변경 전후 비교|
|R04-US-011|P|US-023, US-048|최종 입력안 검토와 승인 구분; 초안 확인과 최종 확인도 구분 필요|
|R04-US-012|P|US-034, US-042, US-047, US-051|실행 범위 전체 검토와 승인 구분 필요|
|R04-US-013|S|US-055, US-056|결과와 증빙 확인 분리|
|R04-US-014|S|US-059, US-060|마지막 상태와 시점 분리|
|R04-US-015|S|US-062, US-063|대상 선택·수동 갱신 요청|
|R04-US-016|M|US-064|갱신 결과·변화 확인|
|R04-US-017|M|US-066|반려 사유 확인|
|R04-US-018|P|US-077, US-078, US-079, US-080|주기 및 알림 채널은 별도 후보, 최소 주기 수치 미채택|
|R04-US-019|M|US-086|세션 유지 위험 확인|
|R04-US-020|M|US-092|중요 변화 알림|
|R04-US-021|M|US-094|중단 요청|
|R04-US-022|M|US-009|추가 등록 시 원본 선택 재사용|
|R04-US-023|S|US-049, US-052|작업 승인 거절의 유형 구분|
|R04-US-024|M|US-033|인증 재시도|
|R04-US-025|P|US-072|삭제 요청 명시; 기본/미결정 분류 차이, F05 직접 연결보다 지원 근거 적합|
|R04-US-026|P|US-069|미확인 효과 조회 요청 동일; base/undecided 분류 차이|
|R04-US-027|M|US-004|이미지 첨부|
|R04-US-028|M|US-009|작업 원본 선택|
|R04-US-029|S|US-019, US-020, US-021|업무 종류 선택|
|R04-US-030|M|US-041|외부 객체 지정|
|R04-US-031|M|US-048|최종 입력안 승인|
|R04-US-032|M|US-051|실행 범위 승인|
|R04-US-033|P|US-057, US-067|반려 수정 제안 검토와 대응안 선택 구분|
|R04-US-034|M|US-087|인증 유지 승인|
|R04-US-035|P|US-094, US-095, US-097|세션 파기 자체는 시스템; 독립 요청 필요 여부 결정|
|R04-US-036|P|US-009, US-018, US-019, US-051|추가 등록 요청과 선택·승인 관계 검토|
|R04-US-037|P|US-053, US-049, US-052|승인 철회와 최초 거절 구분, 철회 범위 미결정|
|R04-US-038|P|US-022, US-033, US-070|인증 실패 대상만 건너뛰고 나머지 계속하는 명시 분기|
|R04-US-039|P|US-073|관리 연결 해제 명시; base/undecided 및 F05 연결 차이|

### R05 · 47개

|원본 ID|구분|R03 대응 또는 관련 문맥|검토 메모|
|---|---|---|---|
|R05-US-001|S|US-003, US-004, US-006|원본 자료 제출|
|R05-US-002|M|US-009|저장 원본 선택|
|R05-US-003|P|US-011, US-012|구조화 결과 대조·정정; base/undecided 차이|
|R05-US-004|M|US-013|원본 수업 조건 수정|
|R05-US-005|G|관련 문맥: US-014, US-015|원본 보관 요청(최초 명시 저장)과 저장 결과/재요청 구분|
|R05-US-006|M|US-016|플랫폼 지원 확인|
|R05-US-007|S|US-018, US-019, US-020, US-021|플랫폼·업무 선택 분리|
|R05-US-008|M|US-023|플랫폼 입력안 검토|
|R05-US-009|M|US-025|누락 보완|
|R05-US-010|M|US-029|대체 조건 선택|
|R05-US-011|S|US-031, US-032|직접 로그인/본인인증|
|R05-US-012|M|US-033|세션 재인증|
|R05-US-013|M|US-034|본인 계정 확인|
|R05-US-014|M|US-041|관리 대상 지정|
|R05-US-015|M|US-046|전후 비교|
|R05-US-016|M|US-048|최종 정보 승인|
|R05-US-017|M|US-051|외부 실행 승인|
|R05-US-018|S|US-049, US-052|승인 거절 분리|
|R05-US-019|M|US-054|변경 실행 조건 재검토|
|R05-US-020|G|관련 문맥: US-019, US-048, US-051|신규 등록 요청(승인 후 별도 명시 행동 필요성)|
|R05-US-021|G|관련 문맥: US-020, US-047, US-051|조건 변경 요청(승인 후 별도 명시 행동 필요성)|
|R05-US-022|G|관련 문맥: US-021, US-041, US-051|갱신 요청(승인 후 별도 명시 행동 필요성)|
|R05-US-023|M|US-056|접수 근거 확인|
|R05-US-024|P|US-058, US-059, US-060|마지막 확인 이력과 과거 실행 이력 구분; 범위 차이|
|R05-US-025|S|US-062, US-063|채널 상태 갱신 요청|
|R05-US-026|P|US-069, US-063|응답 유실 후 접수 조회, base/undecided 차이|
|R05-US-027|M|US-060|조회 실패 후 마지막 확인 시점|
|R05-US-028|P|US-025, US-027, US-050, US-067|반려 보완안 제출의 대상/후속 승인 분기 구체화|
|R05-US-029|G|관련 문맥: US-055, US-062, US-068, US-069|미완료 대상 선택(실패와 미확인 구분)|
|R05-US-030|S|US-077, US-079|대상·기간 설정|
|R05-US-031|M|US-087|지속 조회 인증 승인|
|R05-US-032|P|US-093, US-092|알림 근거는 E04 사용자 행동; E03 자동 조회 자체는 시스템|
|R05-US-033|M|US-095|지속 조회 권한 철회|
|R05-US-034|P|US-072|원본 삭제 요청 명시; 세부 정책만 미결정|
|R05-US-035|P|US-073|관리 연결 해제 요청 명시; 세부 정책만 미결정|
|R05-US-036|G|관련 문맥: US-070|심사 접수 취소(외부 효과)|
|R05-US-037|M|US-022|처리 불가 플랫폼 제외|
|R05-US-038|P|US-028, US-041, US-047|대표 서비스 지정은 플랫폼 특화 후보; 범위 미결정|
|R05-US-039|P|US-016, US-017|프로필 등록과 유료 제안 구분; 제안 제외|
|R05-US-040|P|US-023, US-024, US-026|과정별 요금·단위 확인/별도 가격란 충돌|
|R05-US-041|G|관련 문맥: US-055, US-057, US-067|승인 후 남은 모집 준비 확인(승인≠모집 가능)|
|R05-US-042|G|관련 문맥: US-001, US-002, US-009|본인 작업 공간 선택, 다계정/소유권 정책 미결정|
|R05-US-043|P|US-023, US-028, US-029|크몽 오프라인·패키지별 입력 검토 분기|
|R05-US-044|P|US-023, US-024, US-046, US-048|탈잉 회차·계산된 수강료 확인 및 변경 제한 분기|
|R05-US-045|P|US-023, US-028, US-047|숨고 제공 서비스 매칭 요청 조건 검토; 저장 미확인|
|R05-US-046|P|US-016, US-025|프람피 등록 단계·다음 필요 정보 확인|
|R05-US-047|P|US-040, US-041, US-042|뮬 검색·동명이인 식별; 검색 입력 방식은 미정|

### R01 · 63개

|원본 ID|구분|R03 대응 또는 관련 문맥|검토 메모|
|---|---|---|---|
|IS-001|S|US-003, US-004, US-006|원본 제출|
|IS-002|M|US-009|저장 원본 선택|
|IS-003|P|US-011, US-012|원본·추출 대조; base/undecided|
|IS-004|M|US-013|원본 수정|
|IS-005|G|관련 문맥: US-014, US-015|명시적 원본 보관 요청|
|IS-006|M|US-016|지원 업무 확인|
|IS-007|S|US-018, US-019, US-020, US-021|플랫폼·업무 조합 분리|
|IS-008|M|US-023|입력안 검토|
|IS-009|M|US-025|누락 보완|
|IS-010|M|US-029|대체 조건 선택|
|IS-011|S|US-031, US-032|직접 인증|
|IS-012|M|US-033|세션 재인증|
|IS-013|M|US-034|본인 계정 확인|
|IS-014|M|US-041|기존 게시물 지정|
|IS-015|M|US-046|변경 전후 비교|
|IS-016|M|US-048|최종 정보 승인|
|IS-017|M|US-051|실행 승인|
|IS-018|S|US-049, US-052|거절 유형 구분|
|IS-019|M|US-054|변경 조건 재검토|
|IS-020|G|관련 문맥: US-019, US-048, US-051|신규 등록 요청과 승인 분리 후보|
|IS-021|G|관련 문맥: US-020, US-047, US-051|조건 변경 요청과 승인 분리 후보|
|IS-022|G|관련 문맥: US-021, US-041, US-051|갱신 요청과 승인 분리 후보|
|IS-023|M|US-056|접수 근거|
|IS-024|P|US-058, US-059, US-060|마지막 확인/전체 과거 이력 구분|
|IS-025|S|US-062, US-063|상태 갱신 요청|
|IS-026|P|US-069, US-063|접수 여부 확인; 범위 차이|
|IS-027|M|US-060|마지막 확인 시점|
|IS-028|P|US-025, US-027, US-050, US-067|반려 보완안 제출 구체 분기|
|IS-029|G|관련 문맥: US-055, US-062, US-068, US-069|부분 성공의 미완료 대상 선택|
|IS-030|S|US-077, US-079|대상·기간|
|IS-031|M|US-087|지속 조회 인증 승인|
|IS-032|P|US-092, US-093|알림 근거 검토; E03 내부 기능|
|IS-033|M|US-095|지속 조회 권한 철회|
|IS-034|P|US-072|원본 삭제 요청 명시; 처리 정책만 미결정|
|IS-035|P|US-073|연결 해제 요청 명시; 처리 정책만 미결정|
|IS-036|G|관련 문맥: US-070|외부 심사 취소|
|IS-037|M|US-022|수행 불가 플랫폼 제외|
|IS-038|P|US-028, US-041, US-047|숨고 대표 서비스 지정; undecided 유지|
|IS-039|P|US-016, US-017|프로필/유료 제안서 차이 확인|
|IS-040|P|US-023, US-024, US-026|과정별 가격 확인|
|IS-041|G|관련 문맥: US-055, US-057, US-067|심사 승인 후 남은 모집 준비 확인|
|IS-042|G|관련 문맥: US-001, US-002, US-009|본인 작업 공간 선택|
|IS-043|M|US-026|불확실 정보 확인|
|IS-044|P|US-030, US-070, US-022|대안 없음으로 대상 업무 종료 분기|
|IS-045|M|US-055|실패 결과 확인은 결과 확인의 조건|
|IS-046|M|US-055|부분 성공 결과 확인은 결과 확인의 조건|
|IS-047|M|US-064|상태 변화와 갱신 결과|
|IS-048|P|US-057, US-066|대응 안내 확인 및 사유 확인|
|IS-049|M|US-070|진행 중 취소 요청; 외부 복구 보장 없음|
|IS-050|G|관련 문맥: US-068, US-071|중단 작업 재개 요청|
|IS-051|M|US-002|서비스 계정 로그인/인증 후보|
|IS-052|G|관련 문맥: US-002|서비스 자체 인증 실패 안내 확인|
|IS-053|M|US-075|서비스 세션 종료 후보|
|IS-054|P|US-028, US-050|플랫폼별 적용 조건 변경은 최초 지정과 반복 구분|
|IS-055|M|US-005|첨부 사용 권한|
|IS-056|P|US-046, US-054|외부에서 직접 변경된 사실과 기존 승인 비교|
|IS-057|G|관련 문맥: US-024, US-027, US-050, US-068|외부 실행 전 준비 작업 실패 후 재준비 요청|
|IS-058|G|관련 문맥: US-057, US-067|탈잉 최초 모집 일정 설정 요청; 별도 범위 검토|
|IS-059|G|관련 문맥: US-016, US-017, US-023|자동 대행 불가 업무의 직접 작성용 자료 확인|
|IS-060|P|US-022, US-033, US-035, US-070|인증 실패·권한 부족 시 명시적 종료/건너뛰기 분기|
|IS-061|M|US-088|인증 유지 승인 거절|
|IS-062|G|관련 문맥: US-001, US-002|서비스 자체 계정 등록 요청|
|IS-063|G|관련 문맥: US-002, US-072, US-075|서비스 계정 삭제 요청(원본 삭제와 구분)|

## 4. R03 역방향 대조 (98행)

명시적 대응 없음: 28개. 독립 후보의 고유성 또는 누락 확정이 아니라 타 원본 action의 직접 대응 미발견 상태이다. 분기나 내부 이벤트에 포함되어 있을 수 있다.

|R03 ID|단일 행동|R02|R04|R05|R01|
|---|---|---|---|---|---|
|R03-US-001|강사는 서비스에 진입한다.|—|—|—|—|
|R03-US-002|강사는 서비스 계정으로 인증한다.|—|—|—|IS-051|
|R03-US-003|강사는 기존 레슨 소개글을 제공한다.|R02-US-001|R04-US-001|R05-US-001|IS-001|
|R03-US-004|강사는 레슨 사진을 첨부한다.|R02-US-001|R04-US-027|R05-US-001|IS-001|
|R03-US-005|강사는 첨부 자료의 사용 권한을 확인한다.|—|—|—|IS-055|
|R03-US-006|강사는 기본 레슨 조건을 입력한다.|R02-US-001|R04-US-001|R05-US-001|IS-001|
|R03-US-007|강사는 사용할 수 없는 첨부 자료를 교체한다.|—|—|—|—|
|R03-US-008|강사는 원본의 불필요한 첨부 자료를 제거한다.|—|—|—|—|
|R03-US-009|강사는 저장된 원본 레슨 정보를 선택한다.|R02-US-002|R04-US-022, R04-US-028, R04-US-036|R05-US-002|IS-002|
|R03-US-010|강사는 불러온 원본 레슨 정보를 확인한다.|—|—|—|—|
|R03-US-011|강사는 구조화된 레슨 사실을 확인한다.|—|—|R05-US-003|IS-003|
|R03-US-012|강사는 잘못 추출된 레슨 사실을 정정한다.|—|—|R05-US-003|IS-003|
|R03-US-013|강사는 기존 원본 레슨 정보를 수정한다.|R02-US-003|R04-US-003|R05-US-004|IS-004|
|R03-US-014|강사는 원본 저장 결과를 확인한다.|—|—|—|—|
|R03-US-015|강사는 원본 저장을 재요청한다.|—|—|—|—|
|R03-US-016|강사는 플랫폼별 지원 업무를 확인한다.|R02-US-004|R04-US-004|R05-US-006, R05-US-039, R05-US-046|IS-006, IS-039|
|R03-US-017|강사는 플랫폼별 업무 제약을 확인한다.|R02-US-004|R04-US-004|R05-US-039|IS-039|
|R03-US-018|강사는 작업 대상 플랫폼을 선택한다.|R02-US-005|R04-US-005, R04-US-036|R05-US-007|IS-007|
|R03-US-019|강사는 신규 등록 업무를 선택한다.|R02-US-005|R04-US-029, R04-US-036|R05-US-007|IS-007|
|R03-US-020|강사는 기존 게시 정보 수정 업무를 선택한다.|R02-US-005|R04-US-029|R05-US-007|IS-007|
|R03-US-021|강사는 공고 갱신 업무를 선택한다.|R02-US-005|R04-US-029|R05-US-007|IS-007|
|R03-US-022|강사는 작업 대상에서 수행 불가 플랫폼을 제외한다.|R02-US-009|R04-US-038|R05-US-037|IS-037, IS-044, IS-060|
|R03-US-023|강사는 플랫폼별 변환 정보를 확인한다.|—|R04-US-011|R05-US-008, R05-US-040, R05-US-043, R05-US-044, R05-US-045|IS-008, IS-040|
|R03-US-024|강사는 입력 정보의 검증 문제를 확인한다.|R02-US-031|—|R05-US-040, R05-US-044|IS-040|
|R03-US-025|강사는 누락된 레슨 정보를 제공한다.|R02-US-006, R02-US-030|R04-US-006|R05-US-009, R05-US-028, R05-US-046|IS-009, IS-028|
|R03-US-026|강사는 불확실한 레슨 사실을 확인한다.|R02-US-007|—|R05-US-040|IS-040, IS-043|
|R03-US-027|강사는 유효하지 않은 입력 정보를 정정한다.|R02-US-030|—|R05-US-028|IS-028|
|R03-US-028|강사는 플랫폼별 적용 조건을 지정한다.|R02-US-032|—|R05-US-038, R05-US-043, R05-US-045|IS-038, IS-054|
|R03-US-029|강사는 실제로 제공할 수 있는 대체 조건을 선택한다.|R02-US-008, R02-US-032|R04-US-007|R05-US-010, R05-US-043|IS-010|
|R03-US-030|강사는 제시된 대체 조건을 거절한다.|R02-US-009|—|—|IS-044|
|R03-US-031|강사는 대상 외부 플랫폼에 직접 로그인한다.|R02-US-010|R04-US-008|R05-US-011|IS-011|
|R03-US-032|강사는 외부 플랫폼의 본인인증을 수행한다.|—|—|R05-US-011|IS-011|
|R03-US-033|강사는 대상 외부 플랫폼에 재인증한다.|—|R04-US-024, R04-US-038|R05-US-012|IS-012, IS-060|
|R03-US-034|강사는 인증된 외부 계정을 확인한다.|R02-US-011|R04-US-012|R05-US-013|IS-013|
|R03-US-035|강사는 접근 권한 제한 사유를 확인한다.|—|—|—|IS-060|
|R03-US-036|강사는 외부 플랫폼 계정을 생성한다.|—|—|—|—|
|R03-US-037|강사는 외부 플랫폼의 전문가 인증을 수행한다.|—|—|—|—|
|R03-US-038|강사는 외부 플랫폼의 약관에 동의한다.|—|—|—|—|
|R03-US-039|강사는 외부 플랫폼의 정산 계좌를 설정한다.|—|—|—|—|
|R03-US-040|강사는 기존 게시물 후보를 확인한다.|—|R04-US-009|R05-US-047|—|
|R03-US-041|강사는 관리할 기존 게시물을 선택한다.|R02-US-012|R04-US-030|R05-US-014, R05-US-038, R05-US-047|IS-014, IS-038|
|R03-US-042|강사는 선택된 게시물의 작업 대상을 확인한다.|—|R04-US-012|R05-US-047|—|
|R03-US-043|강사는 직접 등록했던 기존 게시물의 관리 연결을 요청한다.|—|—|—|—|
|R03-US-044|강사는 잘못 식별된 작업 대상을 거절한다.|—|—|—|—|
|R03-US-045|강사는 기존 등록 여부의 확인 결과를 검토한다.|—|—|—|—|
|R03-US-046|강사는 변경 전후 레슨 정보를 비교한다.|R02-US-013|R04-US-010|R05-US-015, R05-US-044|IS-015, IS-056|
|R03-US-047|강사는 기존 게시물의 변경 범위를 선택한다.|—|R04-US-012|R05-US-038, R05-US-045|IS-038|
|R03-US-048|강사는 최종 등록·변경 정보를 승인한다.|R02-US-014, R02-US-030|R04-US-011, R04-US-031|R05-US-016, R05-US-044|IS-016|
|R03-US-049|강사는 최종 등록·변경 정보의 승인을 거절한다.|R02-US-015|R04-US-023, R04-US-037|R05-US-018|IS-018|
|R03-US-050|강사는 최종 정보의 수정을 요청한다.|—|—|R05-US-028|IS-028, IS-054|
|R03-US-051|강사는 업무 실행 범위를 승인한다.|R02-US-014, R02-US-030|R04-US-012, R04-US-032, R04-US-036|R05-US-017|IS-017|
|R03-US-052|강사는 업무 실행 범위의 승인을 거절한다.|R02-US-015|R04-US-023, R04-US-037|R05-US-018|IS-018|
|R03-US-053|강사는 실행 전에 업무 승인을 철회한다.|—|R04-US-037|—|—|
|R03-US-054|강사는 변경된 실행 조건을 확인한다.|—|—|R05-US-019|IS-019, IS-056|
|R03-US-055|강사는 플랫폼별 업무 결과를 확인한다.|R02-US-016|R04-US-013|—|IS-045, IS-046|
|R03-US-056|강사는 업무 결과의 확인 근거를 검토한다.|—|R04-US-013|R05-US-023|IS-023|
|R03-US-057|강사는 결과에 따른 후속 조치를 확인한다.|R02-US-020|R04-US-033|—|IS-048|
|R03-US-058|강사는 과거 업무 실행 이력을 조회한다.|—|—|R05-US-024|IS-024|
|R03-US-059|강사는 플랫폼별 마지막 확인 정보와 상태를 조회한다.|R02-US-017|R04-US-014|R05-US-024|IS-024|
|R03-US-060|강사는 상태의 마지막 확인 시점을 확인한다.|—|R04-US-014|R05-US-024, R05-US-027|IS-024, IS-027|
|R03-US-061|강사는 외부 게시물 링크를 연다.|—|—|—|—|
|R03-US-062|강사는 상태 갱신 대상을 선택한다.|—|R04-US-015|R05-US-025|IS-025|
|R03-US-063|강사는 현재 상태의 갱신을 요청한다.|R02-US-018|R04-US-015|R05-US-025, R05-US-026|IS-025, IS-026|
|R03-US-064|강사는 상태 갱신 결과를 확인한다.|R02-US-019|R04-US-016|—|IS-047|
|R03-US-065|강사는 상태 조회 실패 사유를 확인한다.|—|—|—|—|
|R03-US-066|강사는 업무 실패·반려·정보 불일치의 확인된 사유를 검토한다.|R02-US-020|R04-US-017|—|IS-048|
|R03-US-067|강사는 필요한 후속 대응 방안을 선택한다.|—|R04-US-033|R05-US-028|IS-028|
|R03-US-068|강사는 실패한 업무의 재처리를 요청한다.|R02-US-030|—|—|—|
|R03-US-069|강사는 미확인 업무의 기존 외부 효과 확인을 요청한다.|—|R04-US-026|R05-US-026|IS-026|
|R03-US-070|강사는 해당 업무의 중단을 요청한다.|R02-US-009, R02-US-025|R04-US-038|—|IS-044, IS-049, IS-060|
|R03-US-071|강사는 해당 업무의 진행을 보류한다.|—|—|—|—|
|R03-US-072|강사는 보관된 원본 정보의 삭제를 요청한다.|—|R04-US-025|R05-US-034|IS-034|
|R03-US-073|강사는 외부 게시물의 관리 연결 해제를 요청한다.|—|R04-US-039|R05-US-035|IS-035|
|R03-US-074|강사는 업무용 외부 접근 권한을 철회한다.|—|—|—|—|
|R03-US-075|강사는 서비스 계정에서 로그아웃한다.|—|—|—|IS-053|
|R03-US-076|강사는 작업 대상의 소유권 확인 자료를 제공한다.|—|—|—|—|
|R03-US-077|강사는 자동 모니터링 대상을 선택한다.|R02-US-021|R04-US-018|R05-US-030|IS-030|
|R03-US-078|강사는 자동 모니터링의 조회 범위를 지정한다.|R02-US-021|R04-US-018|—|—|
|R03-US-079|강사는 자동 모니터링 기간을 설정한다.|R02-US-021|R04-US-018|R05-US-030|IS-030|
|R03-US-080|강사는 상태 변화의 알림 조건을 설정한다.|R02-US-021|R04-US-018|—|—|
|R03-US-081|강사는 자동 모니터링의 조회 방식을 선택한다.|—|—|—|—|
|R03-US-082|강사는 자동 모니터링 설정 내용을 확인한다.|—|—|—|—|
|R03-US-083|강사는 자동 모니터링의 시작을 요청한다.|—|—|—|—|
|R03-US-084|강사는 자동 모니터링의 설정 변경을 요청한다.|—|—|—|—|
|R03-US-085|강사는 자동 모니터링 대상에서 지원 불가 대상을 제외한다.|—|—|—|—|
|R03-US-086|강사는 인증 유지 위험 안내를 확인한다.|—|R04-US-019|—|—|
|R03-US-087|강사는 인증 유지 조건을 승인한다.|R02-US-022|R04-US-034|R05-US-031|IS-031|
|R03-US-088|강사는 인증 유지 조건의 승인을 거절한다.|—|—|—|IS-061|
|R03-US-089|강사는 자동 모니터링의 운영 상태를 조회한다.|—|—|—|—|
|R03-US-090|강사는 자동 조회 실패 사유를 확인한다.|—|—|—|—|
|R03-US-091|강사는 자동 모니터링의 재개를 요청한다.|—|—|—|—|
|R03-US-092|강사는 자동 모니터링의 상태 변화 알림을 확인한다.|R02-US-023|R04-US-020|R05-US-032|IS-032|
|R03-US-093|강사는 상태 변화 알림의 관측 근거를 검토한다.|—|—|R05-US-032|IS-032|
|R03-US-094|강사는 자동 모니터링의 종료를 요청한다.|R02-US-024|R04-US-021, R04-US-035|—|—|
|R03-US-095|강사는 인증 유지 승인을 철회한다.|—|R04-US-035|R05-US-033|IS-033|
|R03-US-096|강사는 자동 모니터링 종료 결과를 확인한다.|—|—|—|—|
|R03-US-097|강사는 관련 작업용 인증 세션의 해제 결과를 확인한다.|—|R04-US-035|—|—|
|R03-US-098|강사는 자동 모니터링 종료 처리의 제한 사유를 확인한다.|—|—|—|—|

## 5. 자체 검토 / 인계 상태

|기준|현재 판정|근거·잔여사항|
|---|---|---|
|S1|inconclusive|F01~F29/E01~E05 독립 검토 유지, 최종 의미 완전성/범위 미확정|
|S2|inconclusive|98개 기존 명세·48개 이벤트 보존, 비교 발견 사항 신규 후보로만 기록|
|S3|inconclusive|181행 대조 및 역방향 98행 작성, 18개 발견. 의미상 최종 병합 및 전체 분기 검증 미완료|
|S4|inconclusive|로컬 비교 원장·대조 반영 초안 작성. 실제 저장소 반영·TASK result·CI 미수행|

### 다음 검토

- R01이 C01~C18의 신규 후보/기존 분기 재사용/제외/보류를 판정한다. 특히 C02~C12의 외부 효과 및 실패 후 흐름을 우선한다.
- 원본 스토리와 이벤트는 수정하지 않고 비교 원장을 전달한다. 채택된 변경만 이후 ID/피처 참조와 이벤트·분기를 갱신한다.
- 실제 플랫폼 권한·상태·제약·세션 관리·업무 완료 증거 검증 및 최종 통합/DB 설계는 R01 책임.
- 실제 로그인·등록·수정·갱신·자동화 및 구현은 수행하지 않았다.

### 검증 범위

원본별 예상 ID와 181개 행 일치, R03 참조 ID 존재, 98개 스토리/48개 이벤트/34개 피처 원본 보존, 18개 비교 발견의 근거 ID 연결을 로컬 검사하였다. 저장소 공식 검증 또는 의미상 완전성은 미수행.
