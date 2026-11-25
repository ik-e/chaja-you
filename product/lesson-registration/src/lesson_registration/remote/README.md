# r05-remote — R05 · TASK-053

원격 브라우저 runtime (mock 전용). EXEC provider로 I3 `authenticate`, I4 `execute`를 제공합니다.

| 파일 | 역할 |
|---|---|
| `runtime.py` | `RemoteRuntime`: 세션(등록별 BrowserContext), grant·세대, I3/I4, 뷰어 attach, 유휴 정리 |
| `gateway.py` | RT-01~04 `ExecutionGateway`(STORE admit → driver → record_observation, 오류 시 fence), driver용 `BoundGateway` |
| `page.py` | `BrowserScopedPage`: 고정 origin의 상대 경로만, goto·fill·attach·submit·view |
| `viewer.py` | CDP screencast 프레임 전송, 사람 입력 수신(전송 중립), 감사 기록에 입력 내용 없음 |
| `browser.py` | Playwright를 전용 이벤트 루프 스레드에서 실행하는 동기 브리지 |
| `bindings.py` | 플랫폼 binding(계정 확인, 대상 확인, driver, context 생성) |

실행: `uv sync --locked --python 3.12 --all-groups` → `uv run --locked --all-groups python -m playwright install chromium`
→ `uv run --locked --all-groups python dev.py test r05-remote`. Chromium을 받을 수 없는 환경은 `LR_BROWSER_CHANNEL=chrome`.
설계·시험 기록: [`tests/modules/remote/PLAN.md`](../../../../tests/modules/remote/PLAN.md)

## Viewer 연결 초안 · 2026-11-25

`transport.viewer_router`는 R03 앱에 주입할 FastAPI APIRouter를 반환한다. 서버의 실제 서비스 세션으로 owner를 확인하는 async callback과 신뢰된 서비스 origin을 R03이 제공한다. app 영역의 실제 연결은 R03 담당이다.

```python
from lesson_registration.remote.transport import viewer_router

# resolve_owner(ws)는 인증된 서비스 세션의 owner 또는 None을 반환한다.
app.include_router(viewer_router(runtime, allowed_origin=service_origin,
                                 resolve_owner=resolve_owner))
```

제안 경로는 `/remote/viewer.js`와 `/remote/viewer/ws`이다. GET으로 JS를 제공하고, 인증된 same-origin WebSocket의 첫 메시지로 `{t: "attach", grant: AuthGrant}`를 받는다. query와 다른 Origin을 거부한다. Grant는 owner와 현재 세대·만료에 연결되며 원자적으로 한 번만 attach할 수 있다. 재접속은 H6 refresh로 새 Grant를 받는다. `viewer.py`의 frame/input 형식을 사용한다. 메시지는 4096자, 입력은 초당 120개, 대기 입력은 32개, 전송 큐는 8개를 상한 후보로 두었다. 운영 수치는 측정 후 협의한다.

R04 호출 예시는 다음과 같다. container에는 Viewer 전용 요소를 전달한다.

```javascript
import { mount } from '/remote/viewer.js';

const handle = mount(container, authResponse.grant, event => {
  // event는 ready, error, disconnected 중 하나다.
  updateViewerStatus(event);
});
// 화면 이탈이나 재마운트 시 호출한다.
handle.dispose();
```

`ready`는 연결 준비 상태다. 인증 완료는 H6 finish의 서버 응답으로 표시한다. dispose는 UI 연결과 이벤트만 정리한다. 인증 완료 시 runtime이 입력 gate를 닫고 입력 lock의 barrier를 통과하며, 대기 입력은 실행 시점에 다시 검사해 폐기한다. 진행 중 입력의 종료 이후 계정을 확인한다.

`slot_resolver(registration_id, owner_ref, profile_id)` 주입점을 추가했다. R03이 소유권을 검증한 Source 계보 기반 slot을 제공해야 한다. 기존 registration 기반 기본값은 기존 호출 호환용이며 D01 채택 완료 근거로 사용하지 않는다.

Fence 이후 readback은 `late_read_authorizer(store_context)`의 별도 허가가 있을 때만 수행한다. 기본은 미허가다. 허가 범위와 STORE의 Permit consume/dispatch 원자 경계는 R03과 협의 중이다.

현재 브라우저 시험에는 승인된 app/remote/verification 그룹을 함께 설치한다.

```powershell
uv sync --locked --python 3.12 --all-groups
uv run --locked --all-groups python dev.py test r05-remote
```

시험은 main의 R04 원본 UI를 테스트 서버로 제공하고 실제 `viewer-container`에 mount를 직접 호출한다. R04의 실제 버튼/H6 바인딩과 R03 API 조립부에 대한 전체 연결은 담당자 반영 후 추가 확인한다.
