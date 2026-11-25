# r05-remote tests — R05 · TASK-053

`uv run --locked --group remote python dev.py test r05-remote` (Chromium 미설치 환경: `LR_BROWSER_CHANNEL=chrome`)

- `test_auth_viewer.py`: I3·뷰어 (직접 로그인, grant 회전, 격리, origin 고정, 시간 초과)
- `test_execution.py`: R03 Coordinator·StoreGateway와 연결한 I4 (같은 연결 인계, 응답 유실, 거부 시 외부 변경 0건)
- `neutral_site.py`, `support.py`: 중립 mock 사이트, 시험용 driver, 뷰어 클라이언트 대역

계획과 실행 기록: [PLAN.md](PLAN.md)
