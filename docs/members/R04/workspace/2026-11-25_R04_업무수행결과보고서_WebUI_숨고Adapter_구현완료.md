# [R04 업무수행결과보고서] Web UI 및 숨고 Adapter 구현 완료

> **문서 지위 (2026-11-26 정정):** 이 문서는 **이전 설계 기준의 기록이며 참고 자료로 보존**한다. 현재 적용할 설계로 제안하는 문서가 아니다. 현재는 [기획안 V1.2](../../../artifacts/planning/lesson-registration-20261123/proposal-v1.2.md)를 기준으로 사용자 스토리·서비스 범위를 확정한 뒤 DB → API·프로토콜 → 상세 설계 순으로 진행한다([PHASE-20261126-01](../../../human/phase-intents/PHASE-20261126-01.md)). 새 설계 기준이 확정되기 전에는 이 문서의 API·UI·화면 흐름을 후속 설계의 기준으로 사용하지 않는다.

- **작성자:** R04 (원민, Web UI / 숨고 Adapter)
- **작성일자:** 2026-11-25
- **관련 TASK:** TASK-051 (Web UI), TASK-052 (숨고 Adapter)
- **대상 브랜치:** `akaraywon` (main 병합 완료)

---

## 핵심 요약
R04 배정 업무인 Web UI(TASK-051)와 숨고 Adapter(TASK-052)의 설계·구현·테스트 및 main 브랜치 동기화를 완료하였으며, 로컬 분할화면 브라우저를 통해 5대 화면 컴포넌트의 렌더링 및 FSM 워크플로우를 검증하였습니다.

---

### 1. **R04 Web UI(TASK-051) 구현 결과**

(1) **R03 API 비동기 클라이언트 및 워크플로우 제어기 구축**  
- 팀장 추가 지시 8대 기준(공통 `/v1/*` 라우트, H7 202/200 분기, H8 job_state/progress 관측, 종료 후 result 표출, unknown 자동 재실행 차단, `X-Mock-Owner` 헤더 전달, AuthGrant 비저장/비로깅, `Cache-Control: no-store`)을 완벽 준수하는 `WebApiClient`([client.py](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/api/client.py))와 `WorkflowController`([workflow.py](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/workflow.py))를 구현했습니다.

(2) **5대 화면 컴포넌트 및 통합 UI 진입점 제작**  
- `web/components/` 디렉터리에 5대 화면 컴포넌트 템플릿([source.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/components/source.html), [prepare.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/components/prepare.html), [auth.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/components/auth.html), [review.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/components/review.html), [result.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/components/result.html))을 구축하고, [index.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/index.html)에 인라인 조립했습니다.
- [app.js](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/app.js)를 통해 상태 머신 전환, 1.5초 지수 백오프 폴링 로직, R05 원격 Viewer와의 `postMessage` 규약(mount/ready/action/dispose) 핸들러를 구현했습니다.

---

### 2. **R04 숨고 Adapter(TASK-052) 구현 결과**

(1) **숨고 S1~S6 오퍼레이션 및 DOM Fixture 구축**  
- 합성 HTML DOM Fixture([service_config.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/fixtures/platforms/soomgo/service_config.html), [service_detail.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/fixtures/platforms/soomgo/service_detail.html)) 및 `mock_responses.json`을 제작했습니다.
- S1(탐색), S2(필드 입력), S3(미리보기), S4(저장 요청), S5(응답 검증), S6(독립 Readback)을 수행하는 `SoomgoAdapter`([adapter.py](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/src/lesson_registration/platforms/soomgo/adapter.py)) 및 `SoomgoOperations`([operations.py](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/src/lesson_registration/platforms/soomgo/operations.py))를 구현했습니다.

(2) **공통 StoreGateway 연동 및 독립 Readback 검증**  
- 공통 `StoreGateway` 및 `EvidenceStore`와 결합하는 `SoomgoGatewayRunner`([bridge.py](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/src/lesson_registration/platforms/soomgo/bridge.py))를 구현했습니다.
- S1~S4는 증거 없이 통과, S5에서 1회 저장 관측, S6에서 완전히 새로운 DOM 조회를 통한 독립 Readback 증거(`kind: goal`, `observed_state: mock_saved`)를 생성하여 정본 스키마 계약에 완벽히 부합하도록 검증했습니다.

---

### 3. **검증 및 화면 확인 안내**

(1) **자동화 테스트 검증 결과**  
- `dev.py test r04-web`: 9개 테스트 전수 통과 (API 클라이언트 7개 + 컴포넌트 마크업/FSM 2개)
- `dev.py test r04-soomgo`: 6개 테스트 전수 통과 (단위 테스트 3개 + Gateway 통합 테스트 3개)
- `project_docs.py --check`: 27개 문서 프로젝션 최신 상태 유지

(2) **로컬 및 원격 브라우저 확인 링크**  
- **로컬 웹 서버 접속 (즉시 열기):**  
  [http://localhost:8080](http://localhost:8080) (로컬 백그라운드 웹서버 구동 중)
- **로컬 파일 직접 열기:**  
  [product/lesson-registration/web/index.html](file:///Users/wonmin/orca/projects/Last%20Project/product/lesson-registration/web/index.html)
- **원격 GitHub 실시간 HTML 미리보기:**  
  [HTMLPreview로 index.html 바로 열기](https://htmlpreview.github.io/?https://github.com/ik-e/chaja-you/blob/main/product/lesson-registration/web/index.html)
- **터미널 실행 명령어:**
  ```bash
  # Google Chrome으로 UI 실행
  open -a "Google Chrome" "http://localhost:8080"
  ```
- 5대 화면 간 단계 이동, 구조화 필드 수정, 인증 상태 전환, 미확정(unknown) 상태 대응 팝업 등이 mock 데이터로 완전 동작합니다.

---

<details>
<summary>검증 근거·남은 일</summary>

**검증 근거:**
- `product/lesson-registration/tests/modules/web/test_api_client.py` & `test_ui_components.py` (9 passed)
- `product/lesson-registration/tests/modules/soomgo/test_soomgo_adapter.py` & `test_gateway_integration.py` (6 passed)
- `docs/artifacts/tasks/TASK-051.json` 및 `TASK-052.json` (상태: `진행 중`)
- 최신 Git 커밋: `bc2e2c8` (main 및 akaraywon 동기화 완료)

**남은 일:**
- R05의 원격 브라우저 실행 환경(TASK-053) 준비 시 실제 iframe postMessage 연동 테스트
- R03의 공통 백엔드 API 서버 가동 시 통합 E2E 테스트
</details>

---

### 추천 대안

- **안 A (추천):** 본 보고서를 개인 브랜치(`akaraywon`) 및 `main` 브랜치에 동기화하여 팀 전체가 열람할 수 있도록 하고, Discord 또는 공유 채널을 통해 R01(팀장) 및 R03, R05 담당자에게 R04 구현 완료 및 통합 대기 상태를 공지합니다.
- **안 B:** 브라우저 E2E 자동화 시나리오(Playwright 등)를 추가 구성하여 UI 상호작용 검증을 더욱 고도화합니다.
