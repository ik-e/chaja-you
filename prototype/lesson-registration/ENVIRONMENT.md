# MVP 테스트 환경 uv 실행 계약 · 2026-11-24

현재 상태: **작업 브랜치 설정 준비 / 실제 `uv sync`·CI 통과 미확인.** [오늘 작업 TASK-038~042](../../docs/artifacts/design/lesson-registration-20261123/TEST-ENV-WORK-20261124.md) 기준.

## 채택한 최소 도구

- Python `.python-version=3.12`; `requires-python >=3.12`
- 런타임 dependencies = **[]**. 아직 채택하지 않은 `pydantic`, `pydantic-settings`, `python-dotenv`, `requests` 제거.
- `[dependency-groups].dev`: `pytest`, `ruff`. 실제 테스트·코드 검증에 필요한 도구이므로 유지.
- `[tool.uv] package=false`: 아직 배포 패키지 구조를 선정하지 않음.
- `uv.lock`: 위 dev 도구와 필수 전이 의존성만 남김(이력은 `UV-AUDIT-20261124.md`).

## 루트에서 실행

```bash
uv lock --check
uv sync --locked --group dev
uv pip check --python .venv/bin/python
uv run --locked pytest prototype/lesson-registration/tests -q
uv run --locked ruff check prototype/lesson-registration/tests
python tools/project_docs.py --check
```

Windows PowerShell의 검사 경로는 `uv pip check --python .venv/Scripts/python.exe`이다. CI는 Linux 기준이다.

**현재 실행 결과:** GitHub에 정적 파일/검사 명령을 준비했으나 설치·테스트 실실행 결과를 기록하지 않았다. R05/TASK-041이 직접 실행 후 명령·환경·결과·오류를 제출해야 완료 가능.

## 향후 의존성 변경은 별도 결정

- R05가 서버/브라우저/API/저장소를 설계·비교하기 전 FastAPI, Playwright, SQLAlchemy 등은 추가하지 않는다.
- R04가 React/Node를 선택하기 전 Node 패키지 매니저·잠금 파일을 만들어 확정하지 않는다.
- 실제 기능 코드에서 필요성이 확인되면 R05가 영향 및 대안을 검토해 의존성 추가 TASK/PR로 올린다. 잠금 갱신과 테스트를 함께 수행한다.
- 기존 문서 관리 도구는 `python tools/project_docs.py` 경로를 그대로 사용한다.
