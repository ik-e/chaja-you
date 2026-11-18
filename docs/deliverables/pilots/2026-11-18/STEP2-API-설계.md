# 찾아you API 설계 — 잠정 계약 검증본

> **설계 가설 · 미구현 · 미승인 · 미제출** · 적용 기준: 2026-11-18 · 문서 ID: `DLV-03`
>
 >
> 이 문서는 기존 찾아you 기획의 **트랙 B 제출 대응용 잠정 시연본**입니다. 프로젝트 주제·기능·기술 채택 및 실제 구현·제출을 의미하지 않습니다.

- **기준:** 이전 APP-A 요청→조사 작업→근거·판정→결과 조회 하나를 문서상 연결
- **목차 근거:** 교육 예시의 인증 방식/API 상세/Pydantic 검증/Tool 호출/API 목록을 현재 흐름에 맞게 재구성; 최신 공식 수정본 대조 대기
- **생성 입력:** [파일럿 정본](model.json) · 기준 커밋 `53b73584069042225298c97c6c5688f8b429f56b`
- **Phase:** [PHASE-20261118-01](../../../human/phase-intents/PHASE-20261118-01.md)

## 문서·근거 경계

기존 기획/설계 원본을 변경하지 않고 동일 기준 데이터에서 생성한 **검토용 Markdown**입니다. 해당 커밋이 당시 참고 자료이며, 현재 제품의 승인/개발/제출 상태는 아닙니다.

| 기준 원본 | 원본 고정 커밋 |
| --- | --- |
| [`docs/artifacts/planning/기획서_초안.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/planning/%EA%B8%B0%ED%9A%8D%EC%84%9C_%EC%B4%88%EC%95%88.json) | `53b735840690` |
| [`docs/artifacts/tasks/TASK-006.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/tasks/TASK-006.json) | `53b735840690` |
| [`docs/artifacts/specs/focus_apps.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/specs/focus_apps.json) | `53b735840690` |
| [`docs/artifacts/planning/WBS.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/planning/WBS.json) | `53b735840690` |

## 1. 목적·경계·인증 방식

### 계약의 상태

이 API는 **검증용 가상 계약**입니다. HTTP API·FastAPI·구체 엔드포인트·키 발급·테이블은 현재 구현하거나 최종 채택하지 않았습니다. Python/FastAPI는 기존 기술 후보일 뿐이며 사용자에게 이미 동작한다고 표시하지 않습니다.

- **대표 사용자 흐름:** 지정 Android 앱 2개를 오프라인 타이머(필수) 및 무계정(선호) 기준으로 비교 요청 → 요청 검증 → 비동기 조사 작업 준비 → 상태 및 판정 결과 조회.
- **계정·인증:** 로컬 단일 사용자 데모를 가정하더라도 실제 외부 공개 배포 시에는 인증·소유권 확인이 필요합니다. 예시 \`Authorization: Bearer <REDACTED>\`는 실제 토큰이 아닙니다.
- **권한:** 생성 요청은 해당 사용자에게 귀속, 조회는 요청 소유자만 허용. 인증 불가 401, 소유하지 않은 요청은 403/404 선택 검토.
- **비밀키:** 외부 조회/LLM 키는 클라이언트에 전달하지 않는 설계 가정. 실제 구현 전 검증 필요.
- **상태 어휘:** \`queued\`, \`running\`, \`completed\`, \`partial\`, \`failed\`, \`cancelled\` (제안). \`partial\`은 실패와 별도이며 \`unknown\` 조건을 참조할 수 있습니다.

## 2. API 목록과 사용자 흐름

| API ID | Method | Path(제안) | 입력 | 반환 / 상태 | 연결 요구 |
| --- | --- | --- | --- | --- | --- |
| API-01 | POST | /api/v1/research-requests | targets, criteria, discovery_rule | 202, request_id, status | FR-01/02 |
| API-02 | GET | /api/v1/research-requests/{request_id} | request_id | 200, request & task summary | FR-03 |
| API-03 | GET | /api/v1/research-requests/{request_id}/results | request_id | 200, claims/verdicts/sources/unknowns | FR-04 |
| API-04 | GET | /api/v1/research-requests/{request_id}/tasks | request_id | 200, task_id/attempts/status | FR-02/03 |

**인계 흐름:** API-01 검증→request_id 발급→작업 후보 제안(R03 논리)→task_id 확정 및 관계 저장(R05 영역)→실행별 attempt_id 기록→source/evidence/verdict 연결→API-03 조회. 이는 TASK-006의 **설계 순서를 예시 계약으로 투영**한 것이며 실제 호출·저장·팀 승인 확인은 없었습니다.

### 예시 요청(JSON, 실제 전송 아님)

\`\`\`json
{
  "domain": "focus_apps",
  "targets": ["PomoToki", "Focus To-Do"],
  "criteria": [
    {"id":"C-OFFLINE","name":"offline_timer","importance":"must"},
    {"id":"C-ACCOUNT","name":"no_account","importance":"prefer"}
  ],
  "discovery_rule": "specified_candidates_only"
}
\`\`\`

### 예시 202 응답

\`\`\`json
{
  "request_id": "req_example_001",
  "status": "queued",
  "result_url": "/api/v1/research-requests/req_example_001/results"
}
\`\`\`

API-03 조회 시, 조건을 충족한다고 단정하는 대신 각 판정이 \`fulfilled\`/\`not_fulfilled\`/\`unknown\` 중 무엇인지와 source_id/evidence_id를 보여줍니다. 실제 앱 기능은 응답에 임의로 확정값으로 삽입하지 않습니다.

## 3. 상세 계약·오류·검증

### 필드·검증 명세

| 계약/필드 | 유형·제약(제안) | 오류 |
| --- | --- | --- |
| domain | 허용된 도메인 코드 | 422 unsupported_domain |
| targets | APP-A는 2개 비공백 문자열 | 422 invalid_targets |
| criteria[].id | 요청 내 중복 불가 | 422 duplicate_criterion |
| criteria[].importance | must/prefer | 422 invalid_importance |
| discovery_rule | specified_candidates_only / conditional_discovery | 422 invalid_rule |
| request_id | API가 발급하는 문자열 ID | 404 unknown_request |
| task.status | 대기/실행/완료/부분/실패/취소 | 409 invalid_transition |
| verdict.status | fulfilled/not_fulfilled/unknown | 근거 없을 때 fulfilled 금지 |

### 오류 응답 예시

\`\`\`json
{
  "error": {
    "code": "invalid_targets",
    "message": "The specified-candidate scenario needs two candidates.",
    "request_id": null,
    "retryable": false
  }
}
\`\`\`

| 상태 | 의미 | 공개 여부 |
| --- | --- | --- |
| 400 | 파싱/형식 오류 | 안전한 메시지만 노출 |
| 401 | 인증 누락 | 비밀 정보 노출 금지 |
| 403/404 | 소유권·조회 정책 | 선택 사항 미결정 |
| 409 | 상태 전이/중복 문제 | 클라이언트 재시도 조건 확인 |
| 422 | 도메인 입력 의미 검증 실패 | 필드별 사유 |
| 429 | 요청/호출 예산 초과 | 자동 무한 재시도 금지 |
| 500/503 | 내부·외부 도구 실패 | 부분 결과 가능성 검토 |

**예시 구현 언어에 따른 Pydantic 검사**는 선택 사항입니다. API 입력·출력 JSON Schema 또는 다른 언어의 DTO 검증도 가능하므로 특정 라이브러리를 채택하지 않았습니다.

## 4. Tool 호출·실패 정책과 미결정

| 단계 | 담당 역할 가설 | 입력 | 출력 | 실패·중단 |
| --- | --- | --- | --- | --- |
| 계획 | R03 영역 | request_id, criteria, targets | task 제안 및 depends_on | 필수 조건 누락 시 보류 |
| 저장·상태 | R05 영역 | 계획 제안 | task_id, queued→running 등 상태 | 계약 오류 시 실행 불가 |
| 자료 조회 | R02 제약 + R03 도구 | 허용된 source/검색 요청 | source_id, retrieved_at, access_status | 접근 실패를 evidence로 만들지 않음 |
| 근거 판정 | R03 기준 | source + criterion | verdict + evidence refs | 근거 불충분이면 unknown |
| 반환 | R05 API + R04 화면 | request/result refs | 결과와 실패·미확인 목록 | partial과 failed 구분 |

- 실제 외부 웹 자동 수집은 금지된 비허용 경로를 사용하지 않습니다.
- timeout/calls/retry budget의 숫자는 **미확정**입니다. 유한 상한의 존재와 실패 종료만 명세했습니다.
- 현재 APP-C의 조건부 발굴은 실제 오프라인 앱 조회 완료를 의미하지 않습니다. 추후 실제 주제 선정에서 API 자체가 폐기될 수 있습니다.
- 남은 검토: 인증/호스팅, API 형태, 필드/상태 이름, DB 관계, R02/R03/R04/R05 경계, 공식 가이드에서 요구하는 Tool 설명 범위.

**원본:** TASK-006의 data_contracts/components 및 기획서 JSON. 다음 DB 설계 문서와 관계를 검증하되 실제 구현 계약으로 채택하지 않습니다.

---

**검토 상태:** 공식 수정본 필수 목차 직접 대조(G0) 미완료 · 기술/구현 승인 미완료 · 제출·접수 미완료
