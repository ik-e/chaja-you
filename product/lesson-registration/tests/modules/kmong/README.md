# r05-kmong tests — R05 · TASK-054

`uv run --locked --python 3.12 python dev.py test r05-kmong`

- `test_profile_contract.py`: pin된 profile·data schema와의 정합성
- `test_adapter.py`: 합성 mock + fake gateway 주입 시험 (정상, 오류, unknown, 중복 차단, 재조회)
- `support.py`: 시험 전용 HTML 폼 클라이언트(ScopedPage 구현), fake gateway/STORE, 최소 schema 검사기

계획과 실행 기록: [PLAN.md](PLAN.md)
