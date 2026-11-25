# r05-kmong fixtures — R05 · TASK-054

- `mock_kmong.py`: 합성 크몽형 등록 사이트 (127.0.0.1, 표준 라이브러리). 로그인 → 신규 등록(slot) → 기본·이미지·패키지 → 검토 → 심사 접수 → slot 기준 접수 조회.
  - 실제 크몽이 아니며 계정 비밀번호는 실행마다 무작위 생성.
  - 중복 접수를 스스로 막지 않고 횟수만 기록 (adapter·gateway의 중복 차단 검증용).
  - 장애 주입은 프로세스 내부 `faults`로만: `submit`=`drop_after_commit`/`fail_before_commit`/`reject_validation`, `readback`=`drop`, `tamper_readback`=`title`/`image`.
- 단독 실행: `uv run --locked --python 3.12 python fixtures/platforms/kmong/mock_kmong.py --port 0`
- 기준 입력은 공통 `fixtures/shared/replay.json`의 kmong `I4`를 읽기 전용으로 사용.
