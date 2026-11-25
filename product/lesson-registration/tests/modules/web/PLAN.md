# r04-web 상세 설계 및 구현 계획 — TASK-051 (R04)

- 작성일: 2026-11-25 · 작성: R04 (원민, 웹 UI / 사용자 흐름)
- TASK: [TASK-051](../../../../../docs/artifacts/tasks/TASK-051.json) "등록 지원 웹 UI 구현" · 상태: 진행 중 (R04 수신 및 착수)
- Phase: [PHASE-20261125-01](../../../../../docs/human/phase-intents/PHASE-20261125-01.md) 공통 계약 기반 mock 제품 개발
- 패키지: `r04-web` · 브랜치: `r04/product-web` (로컬 통합: `akaraywon`) · 배정: HRESP-20261125-01
- 담당 경로: `web/`, `tests/modules/web/`
- 근거 설계: CS-02, CS-03, CS-04, CS-06 ([공통 설계 V1](../../../../../docs/artifacts/design/lesson-registration-20261124/COMMON-INTEGRATION-V1.md), data-schema-v4.1.json, common-integration-v1.json)

---

## 1. 목적 및 작업 범위

H1~H9 공통 API를 소비하는 등록 지원 웹 UI 및 사용자 흐름을 구현한다. 원본 입력(Source)부터 AI 구조화/보완(Prepare), 인증 및 원격 뷰어(Auth), 승인 및 멱등 제출(Review), 진행 및 최종 결과 판정(Progress/Result)까지의 5대 화면 흐름을 제공한다.

| 영역 | 포함 항목 | 제외 항목 |
|---|---|---|
| **소비자 흐름** | H1~H9 REST API 비동기 클라이언트, 화면 상태 전이(State Machine) | 서버 구현(R03), AI 모델 추론 엔진(R02) |
| **5대 화면** | Source, Prepare, Auth(Viewer mount), Review, Progress/Result | 원격 브라우저 컨테이너/실행기 runtime(R05) |
| **상태 통제** | 승인 전 수정/stale revision 복구, 승인 후 변경/취소/재개 차단 | 플랫폼 실제 자격증명/실서비스 접속 (mock-only) |
| **뷰어 연동** | AuthGrant 기반 Viewer 컨테이너 mount/dispose 수명주기 | 공통 DB 영속화/저장소 트랜잭션(R03) |

- **관련 요구사항**: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-08
- **품질/시험 참조**: AT-02, T5-05, T6-02, DV-05

---

## 2. 공통 설계 준수 규칙

### 2.1 팀장 추가 지시사항 (2026-11-25 R03 API 연결 기준)
1. **공통 /v1 라우트 사용:** H1~H9 경로는 공통 `/v1/*` 규격을 그대로 사용한다.
2. **H7 202/200 응답 분기:** H7(Start) 최초 등록 응답은 `202 Accepted`, 동일 `request_key` 재전송 시는 `200 OK`를 정상 수신 처리한다.
3. **실행 중 상태 조회:** 실행 진행 중에는 H8을 통해 `job_state`와 `progress`를 주기적으로 폴링 조회한다.
4. **종료 후 결과 표출:** 작업 종료 후에는 STORE에 영속화된 최종 `result`를 사용자에게 표시한다.
5. **unknown 결과 통제:** 결과가 `unknown`일 경우 절대 자동 재실행(재제출)하지 않으며, 강사에게 상황 고지 및 수동 확인 등 다음 조치를 안내한다.
6. **Owner 식별자 전달:** `owner`는 오직 인증 Context(`X-Mock-Owner` 헤더 등)로만 전달하며, 요청 body의 owner 필드는 일절 사용하지 않는다.
7. **AuthGrant 격리:** H6의 `AuthGrant`는 인증 뷰어 화면에만 일시 전달하며, 로컬 스토리지/DB에 저장하거나 로그에 남기지 않는다.
8. **캐시 금지:** 모든 요청 및 응답에 `Cache-Control: no-store` 정책을 준수한다.

### 2.2 공통 아키텍처 원칙
1. **원본 불변 원칙 (CS-02)**: 강사의 원본 사실은 불변이다. 수정 시 새로운 불변 Source 버전을 생성하며, 플랫폼별 세부 선택은 Registration 요청에만 격리한다.
2. **단방향 비가역 상태 전이 (CS-03)**:
   - Prepare 완료(`ready: true`) 전에는 Start(H7) 진입을 차단한다.
   - Review 단계에서 승인(Start) 후에는 사용자 임의의 수정, 취소, 롤백, 재개를 원천 금지한다.
3. **stale revision 회복**:
   - 모든 수정 요청은 현재 `revision`을 동반하며, 409 Conflict 발생 시 최신 상태(H8)를 재조회하여 사용자에게 변경 사실을 알리고 갱신한다.
4. **멱등 제출 및 Key 보존**:
   - 네트워크 재시도 시에도 동일한 `request_key`를 유지하여 중복 실행을 방지한다.
5. **원격 뷰어 수명주기 (CS-04)**:
   - H6을 통해 전달된 AuthGrant 정보로 Viewer를 마운트하며, 인증 완료(`finish`) 또는 취소(`close`) 시 즉시 Viewer를 해제(dispose)하고 입력을 차단한다.
6. **증거 기반 결과 표시 (CS-06)**:
   - UI는 성공 여부를 자체 추측하지 않으며, 서버의 판정 결과(`confirmed`, `failed`, `unknown`)를 그대로 표시하고 관측 근거를 제시한다.

---

## 3. 상세 설계 결정

### 3.1 화면 및 컴포넌트 아키텍처

```
product/lesson-registration/web/
  ├── api/              # H1~H9 API HTTP 클라이언트 (typed fetch wrapper, error handling)
  ├── state/            # 프론트엔드 상태 머신 (workflow transition, revision tracking)
  ├── components/       # UI 컴포넌트
  │     ├── source/     # 원본 레슨 텍스트/자료 입력 및 버전 선택
  │     ├── prepare/    # AI 질문/필수 확인 항목 폼, 충돌/이슈 표시
  │     ├── auth/       # 플랫폼 인증 상태, Viewer mount 컨테이너
  │     ├── review/     # 등록 확정 전 최종 요약, 변경불가 고지, 단일 승인 버튼
  │     └── result/     # 실행 상태 폴링, 관측 근거(Evidence), 최종 판정 뷰
  └── index.html        # 통합 엔트리포인트 (경량/독립 SPA 환경)
```

| 결정 ID | 항목 | 선택 | 근거 |
|---|---|---|---|
| **D1** | UI 스택 | 표준 모던 웹 컴포넌트 (Vanilla TS/JS 또는 경량 선언적 컴포넌트) | 외부 대형 프레임워크 의존성 없이 표준 브라우저 환경에서 즉시 동작 가능 |
| **D2** | API 연동 | `fetch` 기반의 Typed API Client + 에러 코드 매핑 | R03의 FastAPI H1~H9 표준 REST 규약 완벽 정합 |
| **D3** | 상태 관리 | 유한 상태 머신 (FSM: `DRAFT` → `PREPARED` → `AUTHENTICATED` → `SUBMITTED` → `DONE/STOPPED`) | 잘못된 화면 전환 및 승인 후 불법 조작 방지 |
| **D4** | Viewer 연동 | `<iframe>` 또는 Canvas/WebSocket 연동 래퍼 (AuthGrant 수명주기 동기화) | R05의 원격 브라우저 뷰어 규격과 독립적 디커플링 |

---

## 4. WBS 및 구현 계획

| 단계 | 작업 내용 | 예상 소요 | 산출물 |
|---|---|---|---|
| **W1** | H1~H9 API 클라이언트 및 에러 처리 모듈 구현 | 1.0 MD | `web/api/client.py` 또는 `web/api/client.js` |
| **W2** | 5대 화면 컴포넌트 및 FSM 상태 관리 구현 | 1.5 MD | `web/components/`, `web/state/` |
| **W3** | 원격 Viewer mount/dispose 연동 및 이벤트 처리 | 0.5 MD | `web/components/auth/viewer.js` |
| **W4** | 독립 mock API 기반 통합 테스트 (정상/충돌/unknown) | 1.0 MD | `tests/modules/web/test_ui_workflow.py` |

- **총 예상 소요 시간**: 4.0 MD (12/8 mock MVP 일정 내 완료)

---

## 5. 수용 조건 검증 계획

- **r04-web-AC1 (사용자 흐름 및 Viewer 연동)**:
  - Source 생성 → 질문 답변 → Auth 뷰어 마운트 → 인증 완료 → 승인 → 결과 조회 시나리오 검증.
- **r04-web-AC2 (정보 확인/수정 및 변경 불가 통제)**:
  - 승인 전 정보 수정 시 revision 증가 검증, 409 Conflict 발생 시 최신 데이터 재조회 검증, 승인(Start) 후 수정/취소 버튼 비활성화 검증.
- **r04-web-AC3 (독립 Mock API 시험)**:
  - Mock 서버 환경에서 confirmed, failed, unknown 판정이 올바르게 분기되어 표시되는지 테스트.
