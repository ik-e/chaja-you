# MVP 개발 환경 · uv 실행 계약 (2026-11-24 제안)

상태: 개발 작업 공간의 기본 환경 설정. **F1~F3 제품 기능 구현이나 실행 검증 완료가 아님**. R01의 모의 PoC 착수 승인 및 기술 스택 선택은 별도 필요.

## 무엇이 이미 정해져 있는가

- 프로젝트 루트 `.python-version`: Python 3.12
- 루트 `pyproject.toml`과 `uv.lock`: 기존 의존성 유지. `[tool.uv] package=false`는 설치 가능한 배포 패키지 구조를 고정하지 않는 선택이다.
- 테스트 탐색: `prototype/lesson-registration/tests` — **신규 MVP 테스트만**. 기존 `tools/project_docs.py`와 Step별 도구를 변경하지 않는다.
- 기존 환경 관리 도구: `pytest`, `ruff`; 실제 웹/API/브라우저 기능 프레임워크는 미선정.

## 개발자가 루트에서 실행할 명령

```bash
uv sync --locked --group dev
uv run --locked pytest prototype/lesson-registration/tests -q
uv run --locked ruff check prototype/lesson-registration/tests
python tools/project_docs.py --check
```

- `--locked`: 의존성 변경 없이 잠금 일관성을 확인한다. 팀원 간 동일한 잠금 버전을 사용한다. 온라인에서 필요한 패키지를 처음 내려받는 과정은 별도로 발생할 수 있다.
- `pytest` 현재 검증 대상은 **합성 fixture의 형태·mock 구분·민감정보 비포함**뿐이다. F1 검증, 화면 조작, 크몽 모의 입력, E2E 통과로 해석하지 않는다.
- 문서 도구는 기존 CI처럼 Python 표준 라이브러리로 동작한다. 이미 사용 중인 `uv run --no-project python tools/project_docs.py --check`도 그대로 유지한다.

## 의존성 추가 절차

1. R05가 기술 구조/실행 위치/브라우저·API 요구를 조사하여 하나의 권장안과 대안을 제시한다.
2. R03(업무 스키마), R04(UI)와 `contracts` 의미·호출 경계를 맞춘다.
3. Python 패키지가 필요한 경우 R05 책임으로 변경 제안한다. 예: `uv add <approved-dependency>` 및 `uv lock`; 패키지의 용도·필요 버전·라이선스·잠금 diff를 기록한다.
4. 테스트/린트/프로젝션 기존 검사와 새 MVP CI를 확인한 뒤 TASK 브랜치→PR로 반영한다.
5. React/Node UI를 채택한다면 Node의 별도 패키지 매니저/잠금 파일을 사용한다. Node를 억지로 `uv.lock`으로 관리하지 않는다.

## 외부 의존·기록 제약

- 실서비스 크몽에 자동 제출하지 않는다. 비밀번호·OTP·실 세션/개인 사진을 공개 저장소에 커밋하지 않는다.
- 모의 환경의 입력·결과는 **반드시 mock**으로 구분한다.
- 새 패키지를 추가하기 전에는 필요한 기능·공급망 위험·버전 잠금 및 기존 `uv.lock` 영향부터 검토한다.
