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

실행: `uv sync --locked --python 3.12 --group remote` → `uv run --locked --group remote python -m playwright install chromium`
→ `uv run --locked --group remote python dev.py test r05-remote`. Chromium을 받을 수 없는 환경은 `LR_BROWSER_CHANNEL=chrome`.
설계·시험 기록: [`tests/modules/remote/PLAN.md`](../../../../tests/modules/remote/PLAN.md)
