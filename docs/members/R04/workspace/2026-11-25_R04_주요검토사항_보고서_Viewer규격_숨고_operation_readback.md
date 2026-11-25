# [기술 검토 보고서] Viewer 연결 및 메시지 규격 · 숨고 Operation 및 Readback 설계

- **작성일:** 2026-11-25
- **작성자:** R04 (원민, 웹 UI / 숨고 Adapter 담당)
- **대상 과업:** [TASK-051](../../../artifacts/tasks/TASK-051.json) (등록 지원 웹 UI), [TASK-052](../../../artifacts/tasks/TASK-052.json) (숨고 Adapter 및 독립 mock)
- **참조 문서:** 
  - [공통 설계 V1 (COMMON-INTEGRATION-V1.md)](../../../artifacts/design/lesson-registration-20261124/COMMON-INTEGRATION-V1.md)
  - [플랫폼 프로필 V2 (platform-profiles-v2.json)](../../../artifacts/design/lesson-registration-20261124/platform-profiles-v2.json)
  - [공통 통합 정의 (common-integration-v1.json)](../../../artifacts/design/lesson-registration-20261124/common-integration-v1.json)
  - [web/PLAN.md](../../../../product/lesson-registration/tests/modules/web/PLAN.md) / [soomgo/PLAN.md](../../../../product/lesson-registration/tests/modules/soomgo/PLAN.md)

---

## 1. 개요

본 보고서는 R01 팀장의 공통 설계 완료 및 개발 작업 배정에 따라, 본격적인 코드 구현 착수 전 R04 소관 핵심 영역인 **(1) Web UI와 원격 브라우저 간 Viewer 연결 및 메시지 규격**, **(2) 숨고(Soomgo) 어댑터의 S1~S6 단계별 Operation 정의 및 독립 Readback 검증 로직**에 대한 상세 기술 검토 결과를 보고하기 위해 작성되었습니다.

공통 아키텍처 원칙(CS-01~06)과 격리 원칙(mock-only, 서버/런타임과 UI의 디커플링)을 엄격히 준수하면서 타 담당자(R03 App, R05 Remote)와의 인터페이스 정합성을 보장하는 기술 사양을 제시합니다.

---

## 2. Viewer 연결 및 메시지 규격 검토 (TASK-051 Web UI)

### 2.1 아키텍처 및 수명주기 (Lifecycle)

Web UI는 H6 API(인증 단계)에서 발급된 단기 인증 토큰(`AuthGrant`)을 바탕으로 원격 브라우저 뷰어를 마운트하고 해제하는 **소비자(Consumer)** 역할을 수행합니다.

```
[ Web UI (R04) ]                     [ Server H6 (R03) ]             [ Remote Viewer (R05) ]
       |                                      |                                   |
       |--- 1. POST /auth (open) ------------>|                                   |
       |<-- 2. AuthGrant (grant, expiry) -----|                                   |
       |                                                                          |
       |--- 3. mount(container, grant) ------------------------------------------>|
       |<-- 4. VIEWER_READY (마운트 및 스트림 준비 완료) ---------------------------|
       |                                                                          |
       |   [ 사용자: 뷰어 화면에서 수동 로그인/인증 수행 ]                           |
       |                                                                          |
       |--- 5. POST /auth (finish) ---------->|                                   |
       |<-- 6. 200 OK (verified account) -----|                                   |
       |                                                                          |
       |--- 7. dispose() (입력 즉시 차단 및 UI 화면 분리) ------------------------>|
       |<-- 8. VIEWER_DISPOSED ---------------------------------------------------|
```

### 2.2 클라이언트 마운트/디스포즈 계약

공통 설계 명세(`common-integration-v1.json`의 `runtime.viewer`)에 정의된 클라이언트 계약을 준수합니다.

```typescript
interface ViewerClient {
  /**
   * DOM 컨테이너에 뷰어를 마운트하고 세션을 초기화함.
   * stale/expired/foreign grant일 경우 거절하고 에러 발생.
   */
  mount(container: HTMLElement, grant: AuthGrant): ViewerInstance;
}

interface ViewerInstance {
  /** 뷰어 화면을 언마운트하고 원격 세션과의 UI 연결을 안전하게 분리 */
  dispose(): void;
  
  /** 뷰어 이벤트 리스너 등록 */
  on(event: ViewerEvent, handler: (payload: any) => void): void;
}
```

- **입력 (`AuthGrant`):**
  - `generation`: 세대 번호 (0부터 단조 증가, refresh 시 갱신)
  - `grant`: 단기 불투명 티켓 (URL 파라미터 노출 금지, Service Identity 바인딩)
  - `expiry`: 유효 시각 (만료 시 자동 차단)
- **중요 원칙:**
  - `dispose()`는 **UI detach(화면 분리)**일 뿐이며, 백그라운드 작업 취소가 아님.
  - UI는 브라우저 raw 드라이버나 계정 비밀번호/자격증명에 절대 직접 접근하지 않음.

### 2.3 통신 프로토콜 및 메시지 인터페이스 규격 (`postMessage`)

웹 UI 컨테이너와 뷰어 구현체(`<iframe>` 기반 격리 환경) 간의 안전한 양방향 통신을 위해 `postMessage` 표준 메시지 프로토콜을 정의합니다.

#### Host(Web UI) → Viewer 메시지

| 메시지 타입 | 페이로드 | 목적 및 동작 |
|---|---|---|
| `VIEWER_INIT` | `{ grant: string, generation: number, targetUrl: string }` | 뷰어 초기화 및 원격 세션 연결 요청 |
| `VIEWER_LOCK_INPUT` | `{ reason: string }` | 인증 확인 중 사용자 마우스/키보드 입력 잠금 |
| `VIEWER_DISPOSE` | `{}` | UI 연결 해제, 스트림 중단 및 리소스 정리 |

#### Viewer → Host(Web UI) 메시지

| 메시지 타입 | 페이로드 | 목적 및 동작 |
|---|---|---|
| `VIEWER_READY` | `{ sessionId: string, timestamp: number }` | 뷰어 렌더링 및 인터랙션 가능 상태 통지 |
| `VIEWER_ERROR` | `{ code: string, message: string, fatal: boolean }` | 인증 만료(`EXPIRED_GRANT`), 연결 실패 등 에러 통지 |
| `VIEWER_DISCONNECTED`| `{ code: number, reason: string }` | WebSocket/WebRTC 연결 종료 알림 |
| `VIEWER_AUTH_DETECTED`| `{ detectedAt: number }` | (선택적) 플랫폼 로그인 완료 패턴 감지 알림 |

### 2.4 보안 및 안전성 통제 정책

1. **토큰 보호 (Grant Safety):**
   - `AuthGrant`는 DOM 속성에 노출되지 않으며 브라우저 히스토리나 URL 쿼리스트링에 싣지 않습니다.
   - Origin 검증: `window.addEventListener("message", ...)` 수신 시 `event.origin`을 화이트리스트로 검증하여 제3자 스크립트 도청을 원천 차단합니다.
2. **입력 즉각 차단 (Fail-Safe Lock):**
   - 사용자가 UI의 [인증 완료(Finish)]를 누르는 즉시 `VIEWER_LOCK_INPUT`을 발송하고 오버레이 스피너를 띄워 추가적인 임의 조작을 방지합니다.
   - H6 `finish` 응답이 오면 즉각 `dispose()`를 실행하여 뷰어 요소를 DOM에서 완전히 제거합니다.

---

## 3. 숨고 Operation 및 Readback 검증 설계 (TASK-052 Soomgo Adapter)

### 3.1 S1~S6 단계별 Operation 상세 정의

숨고 레슨 서비스 설정(`soomgo.service_configuration.mock.v2`)은 다음 6단계의 순차적 오퍼레이션으로 실행됩니다.

```
[S1: Read]       기존 고수 서비스/카테고리 확인 (MIDI 서비스 존재 여부 조회)
     ↓
[S2: Potential]  신규 서비스 추가 및 카테고리 진입 (category="midi_mock")
     ↓
[S3: Potential]  질문지 7대 항목 폼 설정 (daw, goals, keyboard, ages, genders, format, location_mode)
     ↓
[S4: Read]       저장 전 폼 필드 입력값과 승인된 스냅샷 전수 대조
     ↓
[S5: Potential]  모의 서비스 설정 저장 1회 (저장 버튼 1회 단독 실행)
     ↓
[S6: Read]       서비스 목록/설정 독립 조회 (독립 Readback을 통한 증거 캡처)
```

| 단계 | 오퍼레이션 명칭 | Effect Class | 바인딩 대상 필드 | 기대 관측 증거 (Success Evidence) |
|---|---|---|---|---|
| **S1** | `check_category` | `read` | - | 계정 활성 상태 및 기존 등록 서비스 목록 확인 |
| **S2** | `select_category` | `potential_effect` | `category` | 신규 레슨 등록 슬롯 진입 및 질문지 화면 렌더링 확인 |
| **S3** | `configure_questions` | `potential_effect` | `daw`, `goals`, `keyboard`, `ages`, `genders`, `format`, `location_mode` | 각 체크박스/라디오/셀렉트 폼에 바인딩 값 반영 확인 |
| **S4** | `verify_form_before_save`| `read` | 8개 필드 전체 | DOM에 체크된 값과 승인된 value schema 간 100% 일치 확인 |
| **S5** | `execute_single_save` | `potential_effect` | - | 저장 버튼 1회 클릭 및 네트워크 200 OK / 리다이렉션 관측 |
| **S6** | `independent_readback`| `read` | - | 저장 완료 화면에서 실제 영속화된 값 재추출 및 일치 확인 |

### 3.2 8개 필수 필드 바인딩 규격

`platform-profiles-v2.json`의 스키마에 정의된 정확한 바인딩 타입과 규칙을 따릅니다.

1. `category` (문자열): `"midi_mock"` (const)
2. `daw` (배열): `["consult", "logic", "cubase", "ableton", "fl", "garageband"]` 중 다중 선택
3. `goals` (배열): `["hobby", "entrance", "practical"]` 중 다중 선택
4. `keyboard` (단일값): `"available" | "chords_only" | "unavailable"`
5. `ages` (배열): `["teens", "twenties", "thirties", "forties", "fifties_plus"]`
6. `genders` (배열): `["male", "female"]`
7. `format` (배열): `["individual", "group", "online", "academy"]`
8. `location_mode` (배열): `["flexible", "studio", "visit", "online"]`

### 3.3 1회 저장 원칙 (Single Write Constraint)

- **오퍼레이션 격리:** 양식 저장은 오직 **S5 단계에서 정확히 1회**만 호출됩니다.
- **다중 클릭 방지:** 어댑터 내부에서 `is_saving` 플래그 및 원자적 실행 잠금을 두어 중복 호출을 차단합니다.
- **오류 발생 시:** 저장 응답 실패 시 임의로 저장을 재시도(Retry)하지 않으며, 상태를 즉시 `failed`로 기록하고 게이트웨이에 보고합니다.

### 3.4 독립 Readback 및 EvidenceRecord 캡처 메커니즘

CS-06(증거 기반 판정) 원칙에 따라, 어댑터의 실행 완료와 실제 플랫폼 반영 성공은 분리되어 검증되어야 합니다.

```
[ 어댑터 S5 저장 완료 ] ──> [ S6 독립 Readback 세션/페이지 이동 ] ──> [ DOM 추출 ] 
                                                                         ↓
[ EvidenceRecord 생성 ] <── [ Sha256(추출값) vs Sha256(승인값) 대조 ] <────┘
```

1. **독립 조회 (Readback):**
   - 저장이 성공한 후, 저장 완료 응답에만 의존하지 않고 고수 프로필의 **서비스 관리 상세 페이지**로 이동하여 실제로 저장된 폼 값을 다시 읽어옵니다.
2. **`EvidenceRecord` 구성:**
   ```json
   {
     "id": "EV-SOOMGO-READBACK-001",
     "kind": "readback_observation",
     "step_id": "S6",
     "timestamp": 1732512000,
     "observed_payload": {
       "category": "midi_mock",
       "daw": ["logic", "ableton"],
       "goals": ["hobby"],
       "keyboard": "available",
       "ages": ["twenties", "thirties"],
       "genders": ["male", "female"],
       "format": ["individual"],
       "location_mode": ["studio"]
     },
     "payload_digest": "sha256:d8e8fca...",
     "target_verified": true,
     "verdict": "confirmed"
   }
   ```
3. **판정 로직:**
   - 추출된 `payload_digest`가 S4 단계의 승인 스냅샷 해시와 일치할 때만 `confirmed` 판정을 내립니다.
   - 네트워크 단절 등으로 조회가 불가능할 경우 `failed`가 아닌 `unknown`으로 분류하여 자동 재제출이나 중복 저장을 방지합니다 (DV-04).

### 3.5 합성 Fixture 및 Gateway 주입 아키텍처

- `product/lesson-registration/fixtures/platforms/soomgo/`:
  - `service_config.html`: 실제 숨고 고수 서비스 설정 화면의 DOM 트리(폼 라벨, input name, select option 구조)를 재현한 가상 HTML 페이지.
  - `mock_responses.json`: 저장 시 응답하는 REST/JSON 규격.
- 외부 라이브 브라우저 없이도 경량 DOM 파서(BeautifulSoup / Playwright mock page)를 통해 `python dev.py test r04-soomgo` 환경에서 즉각적이고 결정론적인 회귀 검증이 가능하도록 구성합니다.

---

## 4. 종합 제안 및 타 담당자 협의 사항

1. **R03 (App/API 담당)과의 협의:**
   - H6(인증) API의 반환 모델에 `AuthGrant`의 만료 시간(`expiry_seconds`) 및 뷰어 힌트(`viewer_type: "iframe" | "canvas"`)를 명시적으로 포함해줄 것을 제안합니다.
   - S8 HTTP loopback 시험 결과와 R04 Web UI 클라이언트 간 통합 엔드포인트 규약을 고정합니다.
2. **R05 (Remote/크몽 담당)과의 협의:**
   - 뷰어 내부에서 전달할 `VIEWER_READY`, `VIEWER_DISPOSE` postMessage 이벤트 스펙을 상호 확정합니다.
   - 크몽과 숨고 간 공통 어댑터 인터페이스(PlatformPort)의 반환 시그니처(`execute(step) -> StepResult`) 일관성을 확인합니다.

---

## 5. 결론 및 향후 계획

본 검토를 통해 **Viewer 연동 수명주기/메시지 규격**과 **숨고 S1~S6 오퍼레이션 및 독립 Readback 절차**가 공통 통합 아키텍처 V1 및 플랫폼 프로필 V2에 완벽히 정합함을 확인했습니다.

팀장 및 팀원의 검토 의견을 수렴한 후, 계획된 W1 일정에 맞춰:
1. `product/lesson-registration/web/api/client.py` (H1~H9 클라이언트 모듈)
2. `product/lesson-registration/fixtures/platforms/soomgo/` (합성 HTML fixture)
구현에 착수하겠습니다.
