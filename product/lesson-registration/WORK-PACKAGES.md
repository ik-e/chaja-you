# 작업 패키지 (배정 완료 · 수신/착수 미확인)

## common — R01 · [TASK-048](../../docs/artifacts/tasks/TASK-048.json)

공통 계약 핀·공통 fixture/stub·composition·통합 시험; 플랫폼 실행기 구현 제외

경로: `WORKSPACE.json`, `README.md`, `dev.py`, `pyproject.toml`, `uv.lock`, `.gitignore`, `contracts/`, `src/lesson_registration/__init__.py`, `src/lesson_registration/composition/`, `fixtures/shared/`, `tests/contract/`, `tests/integration/`, `stubs/`, `evidence/`, `src/lesson_registration/platforms/__init__.py`, `AGENTS.md`, `WORK-PACKAGES.md`

계획: `evidence/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test common`

- common-AC1: 공통 계약 pin 및 경로 소유권 검증
- common-AC2: 모든 패키지 독립 smoke·fixture 검증
- common-AC3: 실제 제품 수용 시험은 별도로 판정

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r02-preparation — R02 · [TASK-049](../../docs/artifacts/tasks/TASK-049.json)

PrepareInput→Preparation; AI 후보·근거·누락/충돌 검사; 12/4 인계 후보, 실제 모델/역량 확인

경로: `src/lesson_registration/preparation/`, `fixtures/source/`, `tests/modules/preparation/`

계획: `tests/modules/preparation/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r02-preparation`

- r02-preparation-AC1: I2 구현: 실제 모델로 사실·근거·질문 생성, 양 플랫폼 프로필 검증
- r02-preparation-AC2: 가격/단위/VAT 누락·충돌 보존, 임의 값 생성 금지
- r02-preparation-AC3: 12/4까지 재현 명령과 합성 데이터·유지보수 인계

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r03-app — R03 · [TASK-050](../../docs/artifacts/tasks/TASK-050.json)

H1~H9·CO·KNOW·STORE·RESULT; 원자 수락/admit/observe/fence와 API; 별도 브라우저·PREP 구현 제외

경로: `src/lesson_registration/app/`, `tests/modules/app/`

계획: `tests/modules/app/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r03-app`

- r03-app-AC1: H1~H9, I1/I5 구현 및 I2/I3/I4 주입; 소유권·revision 검사
- r03-app-AC2: 영속 저장 원자 accept/admit/fence, 중복·경쟁·응답 유실 테스트
- r03-app-AC3: 실제 관측 근거 없으면 성공 금지; 오류 중단 및 조회 복구

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r04-web — R04 · [TASK-051](../../docs/artifacts/tasks/TASK-051.json)

H1~H9 및 Viewer의 소비자; 화면·접속/승인/결과 UI; 서버·remote 구현 제외

경로: `web/`, `tests/modules/web/`

계획: `tests/modules/web/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r04-web`

- r04-web-AC1: H1~H9 사용자 흐름과 viewer mount/dispose 연동
- r04-web-AC2: 승인 전 정보 확인·수정, stale revision 처리, 승인 후 변경·취소·재개 금지
- r04-web-AC3: 독립 mock API 기반 UI 시험, unknown과 confirmed 구분

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r04-soomgo — R04 · [TASK-052](../../docs/artifacts/tasks/TASK-052.json)

숨고 adapter 및 합성 플랫폼 페이지/fixture; 서비스 설정 관측; 원격 runtime·공통 상태 변경 금지

경로: `src/lesson_registration/platforms/soomgo/`, `fixtures/platforms/soomgo/`, `tests/modules/soomgo/`

계획: `tests/modules/soomgo/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r04-soomgo`

- r04-soomgo-AC1: S1~S6 등록된 operation 및 승인된 설정값 사용
- r04-soomgo-AC2: 저장 1회와 독립 readback 확인, 잘못된 대상·응답 유실 실패 검사
- r04-soomgo-AC3: 자체 mock 페이지/fixture 및 gateway 주입 시험; 실제 서비스 금지

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r05-remote — R05 · [TASK-053](../../docs/artifacts/tasks/TASK-053.json)

I3/I4 facade·runtime gateway·viewer client·STORE 호출; 실제 플랫폼별 업무 규칙 제외

경로: `src/lesson_registration/remote/`, `tests/modules/remote/`

계획: `tests/modules/remote/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r05-remote`

- r05-remote-AC1: I3/I4 facade와 RT-01~04, viewer 제공; 같은 인증 연결 인계
- r05-remote-AC2: 세션·계정·lease 격리, STORE admission 및 fence 연결; raw driver 노출 금지
- r05-remote-AC3: 중립 mock에서 실제 브라우저 제어·뷰어 분리·응답 유실 시험

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항

## r05-kmong — R05 · [TASK-054](../../docs/artifacts/tasks/TASK-054.json)

크몽 adapter 및 합성 플랫폼 페이지/fixture; 접수 readback; runtime·공통 상태 변경 금지

경로: `src/lesson_registration/platforms/kmong/`, `fixtures/platforms/kmong/`, `tests/modules/kmong/`

계획: `tests/modules/kmong/PLAN.md` · 실행: `uv run --locked --python 3.12 python dev.py test r05-kmong`

- r05-kmong-AC1: K1~K7 승인값·이미지·조건부 필드 일치, 등록된 operation만
- r05-kmong-AC2: 제출 1회와 독립 receipt/이미지 digest 대조, 오류·unknown 중복 차단
- r05-kmong-AC3: 자체 mock 페이지 및 gateway 주입 시험; 실제 제출 금지

산출물: 담당 경로의 상세 설계 및 구현 계획; 담당 구현 코드·독립 테스트·실행 방법; 수용 조건별 실행 결과와 미확인 사항
