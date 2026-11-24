> **2026-11-24 개정 이후 보존용 공간.** 최초 배정은 [고정 원문](https://github.com/ik-e/chaja-you/blob/b46200de40f0290bc1ab2c06ab8a5f9a62c73a2e/prototype/lesson-registration/README.md)에 보존했다. 현재 작업은 [개정 단계](../../docs/human/phase-intents/PHASE-20261124-03.md)와 아래 고정 작업 공간을 기준으로 검토한다. 기존 전용 브랜치/공간은 참조 확인 후 정리 후보이며 삭제 또는 신규 실행 지시가 아니다.
>
> - TASK-043: [R03 크몽형 모의 PoC](https://github.com/ik-e/chaja-you/tree/5f2e98e95b/docs/members/R03/workspace/test)
> - TASK-044: [R04 숨고 조사·설계](https://github.com/ik-e/chaja-you/tree/926b5de767/docs/members/R04/workspace)
> - TASK-045: [R05 원격 브라우저 PoC](https://github.com/ik-e/chaja-you/tree/fc59a4b8f5e8adea3c4dc3b2264df2907131c018/docs/members/R05/workspace/remote-browser-poc)

# 레슨 등록 플랫폼별 독립 PoC 작업 공간

**적용 단계:** [PHASE-20261124-02](../../docs/human/phase-intents/PHASE-20261124-02.md) · [작업 계약](../../docs/artifacts/design/lesson-registration-20261124/PLATFORM-INDEPENDENT-WORK.md)

## 작업 위치와 소유권

| 담당 / TASK | 전용 브랜치 | 코드·실행 환경 |
| --- | --- | --- |
| R03 / TASK-043 | `r03/task-043-dual-platform-harness` | [test-harness/](test-harness/README.md) |
| R04 / TASK-044 | `r04/task-044-soomgo-registration` | [implementations/r04-soomgo/](implementations/r04-soomgo/README.md) |
| R05 / TASK-045 | `r05/task-045-kmong-registration` | [implementations/r05-kmong/](implementations/r05-kmong/README.md) |

공통 기준선은 main에 있고, 팀원은 자기 브랜치·디렉터리만 수정한다. 각자의 TASK result·검증 증거를 담당자가 관리한다. R03의 공통 하네스는 R04/R05의 코드와 독립적으로 공유한다. 실제 플랫폼 로그인·등록·계정/세션 수집은 허용되지 않는다.

## 개발 환경

- 루트 Python 3.12와 `uv.lock`은 공통 검증 환경이다. 제품 런타임 패키지는 0개이며 개발용 pytest·ruff만 남긴다.
- 루트에서 `uv lock --check`, `uv sync --locked --group dev`, `uv run --locked pytest --version`, `uv run --locked ruff --version`으로 환경을 확인한다. 실제 설치·실행 증거는 CI 결과를 확인한다.
- 실험에 Python이 필요하면 **자기 디렉터리 안에만** 독립 `pyproject.toml` / `uv.lock`을 만든다. 해당 디렉터리에서 `uv sync --locked`, `uv run --locked ...`을 실행한다. Node 등을 택하면 자체 manifest/lock을 같은 디렉터리에 둔다. 루트에 workspace 멤버나 미채택 제품 프레임워크를 추가하지 않는다.
- 패키지 용도·버전·라이선스·실행/설치 명령은 해당 README/design.md에 기록한다. 비밀값, 실제 사용자 데이터, 세션, runtime 임시 파일은 커밋하지 않는다.

## 공통 시험 환경의 공유

[테스트 계약 v0.1](test-harness/CONTRACT.md)은 공통 I/O와 관측 항목만 정의한다. R03이 mock, fixture, 시험 명령, 계약/fixture 버전 및 배포한 commit SHA를 제공한다. R04/R05는 공개된 R03 commit을 별도 worktree에서 읽기 전용으로 실행하고 테스트 대상 URL/입력 파일을 자신의 실행기에 전달한다. 실행 로그에 **구현 commit + 하네스 commit + 계약/fixture 버전**을 기록한다. 전체 브랜치를 병합하거나 하네스를 복제하여 자기 버전으로 변경하지 않는다.

## 본 구현 승격 기준

1. 독립 PoC의 실제 동작·정상/실패/unknown 결과, 의존성·플랫폼 권한·미검증 상태를 확인한다.
2. R01이 검증된 코드/계약의 재사용·수정·폐기와 본 구현의 실행 구조·스택을 별도로 결정한다.
3. 선택된 코드·검증 데이터만 확정된 본 구현 경로에 이전하고, 의존성 및 계약을 다시 검증한다. 본 구현이 `prototype/`를 import하거나 이를 배포·빌드 입력으로 사용하지 않도록 한다.
4. R03 하네스 중 재사용할 시험은 본 제품의 평가 사례/계약과 연결하여 회귀 테스트로 승격한다. 전체 실험 브랜치의 무조건 병합은 하지 않는다.

**현재 상태:** 공간·공통 기준선 준비. 담당자의 실제 구현·실행은 TASK별로 증거를 남긴다. 본 구현 디렉터리와 기술 스택은 지금 확정하지 않는다.
