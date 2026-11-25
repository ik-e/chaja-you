# 제품 작업 공간 · TASK 배정 완료

R01은 공통 계약·개발 환경·통합만 담당한다. 플랫폼별 실행기는 R04(숨고), R05(크몽) 담당으로 별도 TASK 배정. 담당자 수신·착수 및 가용성 확인 전이며 일정·세부 기술은 협의한다. [활성 단계](../../docs/human/phase-intents/PHASE-20261125-01.md) · [배정 근거](../../docs/human/responses/HRESP-20261125-01_product-task-assignment.md) · [bootstrap CI](https://github.com/ik-e/chaja-you/actions/runs/45525881756).

- [팀 설계 검토 홈](https://github.com/ik-e/chaja-you/blob/d68406b895b344819eb7ed6c3524167789bfdb84/docs/design/lesson-registration/README.md)
- [공통 계약](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [결정 추적](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/trace-index-v0.9.json)
- [작업 공간 정본 후보](WORKSPACE.json) · [replay 예시](fixtures/shared/replay.json). 원본 설계 파일을 복사해 별도 정본으로 만들지 않는다.

## 작업 공간 / 독립 검증

| 패키지 | 담당 후보 | 담당 경로 | 계약·시험 | 독립 시험 |
|---|---|---|---|---|
| common | R01 | `WORKSPACE.json`, `README.md`, `dev.py`, `pyproject.toml`, `uv.lock`, `.gitignore`, `contracts/`, `src/lesson_registration/__init__.py`, `src/lesson_registration/composition/`, `fixtures/shared/`, `tests/contract/`, `tests/integration/`, `stubs/`, `evidence/`, `src/lesson_registration/platforms/__init__.py` | 공통 계약 핀·공통 fixture/stub·composition·통합 시험; 플랫폼 실행기 구현 제외; CS-01, CS-07, CS-08, CS-09; T5-03, T5-13, DV-04 | `uv run --locked --python 3.12 python dev.py test common` |
| r02-preparation | R02 | `src/lesson_registration/preparation/`, `fixtures/source/`, `tests/modules/preparation/` | PrepareInput→Preparation; AI 후보·근거·누락/충돌 검사; 12/4 인계 후보, 실제 모델/역량 확인; CS-01, CS-02; AT-01, T5-08, T6-02 | `uv run --locked --python 3.12 python dev.py test r02-preparation` |
| r03-app | R03 | `src/lesson_registration/app/`, `tests/modules/app/` | H1~H9·CO·KNOW·STORE·RESULT; 원자 수락/admit/observe/fence와 API; 별도 브라우저·PREP 구현 제외; CS-01, CS-02, CS-03, CS-05, CS-06; T5-01, T5-05, T5-06, T5-11, T5-12, T6-01, DV-01 | `uv run --locked --python 3.12 python dev.py test r03-app` |
| r04-web | R04 | `web/`, `tests/modules/web/` | H1~H9 및 Viewer의 소비자; 화면·접속/승인/결과 UI; 서버·remote 구현 제외; CS-02, CS-03, CS-04, CS-06; AT-02, T5-05, T6-02, DV-05 | `uv run --locked --python 3.12 python dev.py test r04-web` |
| r04-soomgo | R04 | `src/lesson_registration/platforms/soomgo/`, `fixtures/platforms/soomgo/`, `tests/modules/soomgo/` | 숨고 adapter 및 합성 플랫폼 페이지/fixture; 서비스 설정 관측; 원격 runtime·공통 상태 변경 금지; CS-01, CS-05, CS-06; AT-05, T5-13, DV-03, DV-04 | `uv run --locked --python 3.12 python dev.py test r04-soomgo` |
| r05-remote | R05 | `src/lesson_registration/remote/`, `tests/modules/remote/` | I3/I4 facade·runtime gateway·viewer client·STORE 호출; 실제 플랫폼별 업무 규칙 제외; CS-04, CS-05, CS-07; AT-02, AT-03, T5-02, T5-12, DV-02, DV-05 | `uv run --locked --python 3.12 python dev.py test r05-remote` |
| r05-kmong | R05 | `src/lesson_registration/platforms/kmong/`, `fixtures/platforms/kmong/`, `tests/modules/kmong/` | 크몽 adapter 및 합성 플랫폼 페이지/fixture; 접수 readback; runtime·공통 상태 변경 금지; CS-01, CS-05, CS-06; AT-04, T5-13, DV-03, DV-04 | `uv run --locked --python 3.12 python dev.py test r05-kmong` |

공통 파일은 R01 소유; 플랫폼 상위 `__init__.py` 포함. 각 팀원은 자기 디렉터리만 수정. 공통 계약/의존성 변경은 R01에게 제안. 정식 TASK를 확인하고 자기 작업 브랜치에서 진행한다. 브랜치는 활성화 커밋을 기준으로 생성한다. R01에게 크몽 구현을 자동 인계하지 않는다.

## 로컬 실행

현재 준비 골격은 표준 라이브러리만 사용한다. 제품 FastAPI/DB/frontend/browser 의존성과 세부 기술은 별도 채택. 새 checkout마다 별도 .venv와 임시 실행 상태.

```sh
cd product/lesson-registration
uv sync --locked --python 3.12
uv run --locked --python 3.12 python dev.py doctor
uv run --locked --python 3.12 python dev.py smoke
uv run --locked --python 3.12 python dev.py test all
```

UI 팀: 별도 터미널에서 `uv run --locked --python 3.12 python dev.py serve api --platform soomgo --port 0` (또는 kmong). 출력한 loopback URL을 UI 개발 설정으로 전달. `/_dev/fixtures`에서 정확한 요청/응답 조회. H1~H9는 합성 replay이며 고정 입력 외에는 거절한다; multipart/임의 수정/상태 전이 구현 없음. 브라우저 UI 통합의 실제 CORS/동일 origin 구성은 R04/R03의 제품 개발에서 검증한다.

원격 팀: `uv run --locked --python 3.12 python dev.py serve mock --port 0` 출력 URL의 `/mock`에서 합성 sign-in, 합성 값 저장, 독립 receipt 확인. 실제 플랫폼 모의 페이지가 아니며 원격 실행기 보안도 입증하지 않는다. 플랫폼 담당자는 자기 플랫폼 mock 및 fixture를 직접 구체화한다. R02·R03·플랫폼 팀의 공통 의존성 대체는 `dev.replay(platform, case, value)`를 사용하고, 정상·누락·unknown의 실제 구현 시험을 추가한다.

`python dev.py check-changes <package> --base <승인된-제품-기준-commit>`는 해당 패키지 소유 경로만 변경했는지 검사한다. R04/R05는 패키지별 분리 브랜치가 기본 후보. R01은 통합 브랜치에서 각 모듈의 변경을 검토. TASK 배정 범위 내에서만 실행하며 결과는 구현 근거와 구별한다.

## 격리와 검증의 한계

- 포트 0, 127.0.0.1만 사용. DB·로그·브라우저 프로필은 각 테스트의 임시 경로 또는 .local/에 저장하고 커밋하지 않는다. 실제 credentials/외부 접속 금지.
- 제품의 실제 보안 경계·승인·중복 방지·DB 트랜잭션·LLM·브라우저 제어·실플랫폼 성공은 이 bootstrap으로 입증되지 않는다.
- 기존 22개 제품 수용 시험은 미실행. bootstrap 시험은 경로/fixture/replay의 연결 확인일 뿐. 실제 기능 담당자가 자신의 단위/계약 시험을 추가하고, R01은 독립 구현이 연결된 동일 후보로 통합 검증한다.
- 검토 결과 문제가 있으면 accepted schema/profile/ports를 수정하고 pin, fixture, 시험을 함께 갱신한다. 변경 대상 추적은 기존 IT-19 및 V0.9 인덱스 참조.

## 배정 현황

| TASK | 담당 | 패키지 | 브랜치 |
| --- | --- | --- | --- |
| [TASK-048](../../docs/artifacts/tasks/TASK-048.json) | R01 | common | r01/product-integration |
| [TASK-049](../../docs/artifacts/tasks/TASK-049.json) | R02 | r02-preparation | r02/product-preparation |
| [TASK-050](../../docs/artifacts/tasks/TASK-050.json) | R03 | r03-app | r03/product-app |
| [TASK-051](../../docs/artifacts/tasks/TASK-051.json) | R04 | r04-web | r04/product-web |
| [TASK-052](../../docs/artifacts/tasks/TASK-052.json) | R04 | r04-soomgo | r04/product-soomgo |
| [TASK-053](../../docs/artifacts/tasks/TASK-053.json) | R05 | r05-remote | r05/product-remote |
| [TASK-054](../../docs/artifacts/tasks/TASK-054.json) | R05 | r05-kmong | r05/product-kmong |

공통 bootstrap CI는 통과했다. 실제 담당자 수신·공수·스택 및 22개 제품 시험은 미확인/미실행. TASK 결과 갱신은 제품 경로 소유권 검사와 분리한 문서 갱신으로 처리한다.
