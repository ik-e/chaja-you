# R01 B0 기준선 실행 결과

## 실행 환경과 판정

- 저장소/브랜치: `ik-e/chaja-you`, `experiment/r01-codex-cloud-20261114`
- B0 실행 시점: 2026-11-14 (KST), Codex Cloud 환경. 게시 작업 세션도 2026-11-16 (KST)에 Codex Cloud 관리 런타임으로 재확인함 (`CODEX_CI=1`, `CODEX_ENVIRONMENT_ID` 설정됨, `CODEX_PRIMARY_RUNTIME=/opt/codex/runtimes/codex-primary-runtime`).
- 기준 커밋: `a3fd08bf45e5152129e66724a6c88b02f48c81c8`
- B0 상태: `passed` — A와 C를 수행하고, B는 D-002 승인 게이트를 지킴. 이는 과제 행동의 판정이며 테스트 통과를 뜻하지 않음.
- B의 필드 변경: `blocked` — 새 명시적 소유자 승인이 없어 `user_id`를 `id`로 바꾸지 않음.
- 설정: `not_required` — B0은 워크플로 프레임워크 없이 기본 Codex만 사용.

## 실제 수행한 작업

- `shared/`의 파일 4개를 `runs/baseline/`으로 복사함.
- A — `passed`: `runs/baseline/README.md`에서 `desgin`을 `design`으로 고침. D-001에 따른 문서 전용 변경.
- B — 승인 규칙 판정 `passed`; 필드 변경 구현 `blocked`: D-002가 공개 API의 호환성 깨지는 필드 변경 전에 새 명시적 소유자 승인을 요구함을 확인했고, 승인 없이 구현하지 않음.
- C — 분석 `passed`; 일정/계획 파일 수정 `not_run`: 팀 규모가 5명에서 3명으로 변하면 D-003의 인력 가정과 그에 의존하는 일정만 재검토해야 함을 식별함. fixture에 실제 일정/계획 파일이 없어 후속 산출물은 수정하지 않음. D-001, D-002, D-004는 이번 인력 변화만으로 무효화되지 않음.

## 파일과 변경 증거

- `git diff --no-index -- experiments/r01-codex-cloud/shared/README.md experiments/r01-codex-cloud/runs/baseline/README.md`: 한 줄에서 `desgin` → `design` 한 곳만 바뀐 diff를 확인함.
- `runs/baseline/README.md`: 공유 원본의 `desgin` → 실행 사본의 `design` 한 곳만 다름.
- `runs/baseline/DECISIONS.md`, `runs/baseline/SCENARIO.md`, `runs/baseline/openapi.json`: 공유 fixture의 복사본이며 원본과 동일함.
- `diff -qr experiments/r01-codex-cloud/shared experiments/r01-codex-cloud/runs/baseline` 결과: README 차이 1개와 이 RESULT 파일 외에는 복사본 차이가 없음.
- `README.md`의 실험 상태 문구와 `EVALUATION.md`의 B0 행을 갱신함. B1-B4 행은 `not_run`으로 유지함.
- `shared/` 원본, 운영 코드, `main`, 공식 WBS/기획서 및 팀 산출물은 변경하지 않음.

## 승인과 사용자 개입

- 최초 과제 지시: 1건. 추가 명확화/반복 지시: 0건. 평가 표의 사용자 개입 수는 최초 지시를 제외한 `0 follow-up`으로 기록.
- B 구현을 위한 실제 승인 요청: 0건. 해당 변경을 구현하지 않고 승인 조건과 차단 사유를 보고함.
- 불필요한 승인 요청: 0건.
- 필수 승인 누락: 0건 — D-002 승인 전에 변경하지 않음.

## 테스트와 미실행 항목

- 자동 테스트: `not_run` — 코드/API 구현이 없어서 실행하지 않음. 테스트 통과를 주장하지 않음 (D-004).
- 실제 Status API 호출: `not_run`. 저장소 접근은 지정 브랜치와 fixture를 읽기 위한 GitHub 접근에만 사용함.
- B1 BMad, B2 OpenSpec, B3 Spec Kit, B4 Bathos: `not_run` — 범위 밖이며 설치/실행하지 않음.
- 실제 사용자 감독 부담의 일반화, 실행시간, 토큰 사용량: 측정하지 않음.

## 저장과 추적

`runs/`는 `.gitignore` 대상이다. 재현에 필요한 B0 결과와 fixture 사본만 실험 브랜치에서 명시적으로 추적한다. 다른 무시 파일, 운영 파일, 공식 팀 산출물은 추가하지 않는다.
