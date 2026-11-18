# 찾아you DB 스키마 및 ERD — 잠정 관계 검증본

> **개념 설계 가설 · 미구현 · 미승인 · 미제출** · 적용 기준: 2026-11-18 · 문서 ID: `DLV-04`
>
 >
> 이 문서는 기존 찾아you 기획의 **트랙 B 제출 대응용 잠정 시연본**입니다. 프로젝트 주제·기능·기술 채택 및 실제 구현·제출을 의미하지 않습니다.

- **기준:** Step2 API 예시의 request/task/attempt/source/evidence/verdict 저장 관계를 정합적으로 시연
- **목차 근거:** 교육 예시의 ERD·엔터티 정의·권한 정책·데이터 수명·최적화를 현재 범위로 제한; 특정 pgvector/RLS/Redis 채택 아님
- **생성 입력:** [파일럿 정본](model.json) · 기준 커밋 `53b73584069042225298c97c6c5688f8b429f56b`
- **Phase:** [PHASE-20261118-01](../../../human/phase-intents/PHASE-20261118-01.md)

## 문서·근거 경계

기존 기획/설계 원본을 변경하지 않고 동일 기준 데이터에서 생성한 **검토용 Markdown**입니다. 해당 커밋이 당시 참고 자료이며, 현재 제품의 승인/개발/제출 상태는 아닙니다.

| 기준 원본 | 원본 고정 커밋 |
| --- | --- |
| [`docs/artifacts/tasks/TASK-006.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/tasks/TASK-006.json) | `53b735840690` |
| [`docs/artifacts/planning/기획서_초안.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/planning/%EA%B8%B0%ED%9A%8D%EC%84%9C_%EC%B4%88%EC%95%88.json) | `53b735840690` |
| [`docs/artifacts/specs/focus_apps.json`](https://github.com/ik-e/chaja-you/blob/53b73584069042225298c97c6c5688f8b429f56b/docs/artifacts/specs/focus_apps.json) | `53b735840690` |

## 1. 설계 목표·범위와 ERD

이 스키마는 **기술 확정 이전의 개념 데이터 모델**입니다. DBMS·pgvector·Redis·RLS·마이그레이션 도구는 **미선정**이며 실제 데이터베이스를 생성한 기록이 아닙니다.

### 대표 사용자 흐름

사용자 요청 \`research_request\` → 작업 \`research_task\` → 시도 \`task_attempt\` → 조회한 출처 \`source\` → 근거 \`evidence\` → 조건별 판정 \`verdict\` → 근거 연결 \`verdict_evidence\` → 요청별 결과 조회.

### ERD (개념 모델)

\`\`\`mermaid
erDiagram
    RESEARCH_REQUEST ||--o{ RESEARCH_TASK : contains
    RESEARCH_REQUEST ||--o{ VERDICT : evaluates
    RESEARCH_TASK ||--o{ TASK_ATTEMPT : has
    RESEARCH_TASK ||--o{ SOURCE : retrieves
    SOURCE ||--o{ EVIDENCE : supports
    VERDICT ||--o{ VERDICT_EVIDENCE : uses
    EVIDENCE ||--o{ VERDICT_EVIDENCE : cited_by
    RESEARCH_REQUEST {
      string request_id PK
      string domain
      string status
      json targets
      json criteria
      string discovery_rule
      datetime created_at
    }
    RESEARCH_TASK {
      string task_id PK
      string request_id FK
      string role
      string status
      json depends_on
    }
    TASK_ATTEMPT {
      string attempt_id PK
      string task_id FK
      int attempt_no
      string status
      string error_code
    }
    SOURCE {
      string source_id PK
      string task_id FK
      string uri
      string access_status
      datetime retrieved_at
    }
    EVIDENCE {
      string evidence_id PK
      string source_id FK
      string finding
      string locator
    }
    VERDICT {
      string verdict_id PK
      string request_id FK
      string candidate_id
      string condition_id
      string status
    }
    VERDICT_EVIDENCE {
      string verdict_id FK
      string evidence_id FK
    }
\`\`\`

이는 도메인별 검색 결과·후속 발굴을 포함한 최종 물리 ERD가 아닙니다. 실제 제품에서는 충분히 간소화하거나 다른 관계를 채택할 수 있습니다.

## 2. 엔터티·관계 및 키 정의

| 테이블(제안) | PK | 핵심 컬럼 | 관계·제약 |
| --- | --- | --- | --- |
| research_request | request_id | domain, status, targets(JSON), criteria(JSON), discovery_rule, created_at | 요청의 상태·입력 계약. owner_id는 인증 선택 후 별도 검토 |
| research_task | task_id | request_id FK, goal, role, status, depends_on(JSON) | request 1:N task, 동일 request 범위 참조 |
| task_attempt | attempt_id | task_id FK, attempt_no, started_at, finished_at, status, error_code | task 1:N attempt, (task_id,attempt_no) 유일 |
| source | source_id | task_id FK, uri, retrieved_at, access_status | task 1:N source, 접근 실패를 실제 근거로 사용 금지 |
| evidence | evidence_id | source_id FK, locator, finding, checked_at | source 1:N evidence, source 참조 필수 |
| verdict | verdict_id | request_id FK, candidate_id, condition_id, status, checked_at | (request_id,candidate_id,condition_id) 단일 최종 판정 **가정**; 변경 이력 정책 미결정 |
| verdict_evidence | (verdict_id,evidence_id) | 두 FK | verdict:N evidence의 다대다 링크 |

### 주요 정합성 제약

- \`verdict.status\`는 \`fulfilled | not_fulfilled | unknown\` 중 하나. \`evidence\`를 참조하지 않는 fulfilled 판정이 없도록 **애플리케이션 검증 규칙(제안)**을 둡니다.
- source의 access_status가 \`unavailable\` 또는 \`failed\`이면 그 조회 자체가 기능 충족 근거가 되지 않습니다.
- 신규 task 재시도는 task_id 재사용, attempt_id 신규 발급. 실패한 attempt도 감사·재현을 위해 유지합니다.
- \`depends_on\`을 JSON 배열로 두는 예시를 사용했지만 그래프 조회 요구가 커지면 별도 \`task_dependency\` 테이블로 분리합니다.
- 엔터티 필드와 접근/보관 정책은 도메인·자료권한에 따라 재검토합니다.

## 3. API↔DB 데이터 계약과 대표 샘플

| Step2 API 항목 | DB 엔터티·컬럼 | 문서상 정합성 |
| --- | --- | --- |
| API-01 요청의 domain/targets/criteria/discovery_rule | research_request의 동명 컬럼 | 202 시 request_id 발급 |
| API-02 요청의 status | research_request.status / research_task.status | running/partial/failed 구분 |
| API-03 source/evidence/verdict 반환 | source→evidence→verdict_evidence→verdict | 조건별 출처 연결 |
| API-04 task/attempt 반환 | research_task→task_attempt | task_id 유지·attempt_id 변경 |

### 예시 데이터 (가상, 실측 아님)

\`\`\`json
{
  "research_request": {
    "request_id": "req_example_001",
    "domain": "focus_apps",
    "targets": ["PomoToki", "Focus To-Do"],
    "criteria": [
      {"id":"C-OFFLINE","name":"offline_timer","importance":"must"},
      {"id":"C-ACCOUNT","name":"no_account","importance":"prefer"}
    ],
    "discovery_rule": "specified_candidates_only",
    "status": "queued"
  },
  "research_task": {
    "task_id": "task_example_001",
    "request_id": "req_example_001",
    "role": "researcher",
    "status": "queued",
    "depends_on": []
  }
}
\`\`\`

확정 제품의 실제 사용 데이터가 아니라, API와 DB가 같은 필드를 공유하는지를 확인하기 위한 **문서용 테스트 픽스처**입니다.

## 4. 데이터 수명·권한·보안·미결정

### 접근 및 보존

- 사용자별 요청 소유권을 검증해야 하며 현재 단일-user/local 또는 다중-user 인증 경계가 결정되지 않았습니다. 따라서 **RLS 적용을 이미 구현했다거나 DB 권한 정책을 검증했다는 주장은 하지 않습니다.**
- 출처 데이터의 수집/복제/보관 여부는 이용조건·저작권·사이트 정책에 따르며 자동 크롤링을 승인하지 않습니다. 가능한 경우 원문 URL/확인 시점/locator/허가 범위만 보관합니다.
- API 키·외부 서비스 자격증명은 DB 내용/응답/일반 로그에 남기지 않는 것을 목표로 하며 실제 secret manager 선택은 미정입니다.
- 로그인·세션·JWT·Redis, pgvector, 인덱스/샤딩 등은 **교육 예시의 기능 설명 대상일 수 있지만 우리 제품 채택 확정 사항이 아닙니다.**

### 성능·조회

(1) \`research_task(request_id)\`, (2) \`source(task_id)\`, (3) \`verdict(request_id,candidate_id,condition_id)\`, (4) \`evidence(source_id)\` 인덱스를 물리 구현 시 후보로 검토합니다. 현재 쿼리 실행계획, 실제 인덱스 성능 수치는 없습니다.

### 남은 설계 질문

1. \`verdict\`의 최종 판단과 수정 이력(version) 유지 방식.
2. 외부 자료 삭제 요청, TTL, 보존 책임과 요청 데이터의 접근 주체.
3. task_dependency 정규화 필요성과 실패 attempt의 리텐션.
4. 구조화 JSON/SQL 스키마의 실제 자료형·관계 제약·마이그레이션.
5. 11/21 주제 선택에 따라 전체 엔터티 구조의 유지·폐기 판단.

**근거:** TASK-006의 \`data_contracts\`·담당 구성요소 및 기존 APP-A 기획. 이 문서는 실제 DB 생성·데이터 수집·승인을 뜻하지 않습니다.

---

**검토 상태:** 공식 수정본 필수 목차 직접 대조(G0) 미완료 · 기술/구현 승인 미완료 · 제출·접수 미완료
