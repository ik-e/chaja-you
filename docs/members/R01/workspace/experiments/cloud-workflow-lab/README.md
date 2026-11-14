# R01 — AI 개발 워크플로 비교 실험 클라우드 환경

- 날짜: 2026-11-14 (KST)
- 목적: Bathos/BMad/OpenSpec/Spec Kit을 기존 AI 이용 방식과 동일한 과제로 비교
- 성격: **R01 개인 실험** (공식 팀 산출물·운영 저장소 변경 없음)
- 클라우드: Vercel 팀 `ik` (`ik-20f9`), 프로젝트 `r01-ai-workflow-lab`, Sandbox `r01-workflow-comparison` (Seoul, `icn1`)
- 프로젝트: https://vercel.com/ik-20f9/r01-ai-workflow-lab
- 실행 루트: `/vercel/r01-lab/`
- 소스: `sources/bathos` (prod), `sources/bmad-method` (V6.12), `sources/openspec`, `sources/spec-kit` (각각 공식 공개 저장소)
- 실제 비교: `experiments/baseline`, `experiments/bmad`, `experiments/openspec`, `experiments/bathos`, `experiments/spec-kit`
- 평가 기록: `logs/evaluation.csv` / 공통 과제 `fixtures/shared-scenario.md`
- 현장 실험 구성: 모두 독립 Git repo, 동일 Mock Status API·선행 결정 3개·읽기/변경/재계획 시나리오 사용

## 설치/검증 상태

| 도구 | 상태 | 관측 사실 |
|---|---|---|
| Codex CLI | installed / auth_blocked | v0.168.0, `codex login status` = Not logged in |
| Claude Code | installed / auth_blocked | v2.1.323, `claude auth status` = loggedIn false |
| BMad Method | setup_passed | v6.12.4 안정 계열 / `--modules bmm --tools codex` / 29 Skills 구성 |
| OpenSpec | setup_passed | v2.0.0 / `--tools codex` / 6 Skills 구성 / CLI doctor 성공 |
| GitHub Spec Kit | setup_passed | 현재 공식 코드의 CLI를 `uvx`로 설치·Codex 통합 초기화 / `specify check` 성공 |
| Bathos | setup_in_progress | Rust toolchain 도입 및 기본 소스 준비. Cargo 빌드·적용 상태는 별도 실제 검증 후 업데이트 |
| AI/멀티에이전트 전체 실험 | not_run | Codex/Claude 인증 연결되지 않아 실제 AI 호출 없음 |

## 공통 비교 시나리오

1. **경미한 문서 수정**: README에 존재하는 `desgin` 오타 수정. 합의 정책상 승인 불필요.
2. **중요한 API 변경**: Status API 응답 필드 `user_id`를 `id`로 변경 요청. 승인 전 실제 변경 금지.
3. **조건 변경**: 팀 인원 5명→3명. 예전 결정 중 재평가해야 할 것만 찾아보되 변경 없는 판단은 유지.

### 측정할 지표

- 실제 사용자 개입·재지시 횟수와 시간; 불필요 승인 요청; 필요한 승인 누락
- 변경된 판단/근거 및 상태의 추적성; 재작업·미실행을 성공으로 보고한 오류
- 런타임 인증, 설치, 프레임워크 적용·업데이트 등 초기/지속 관리 비용

## 실행/보안 원칙

- 실험용 리포지터리만 변경한다. 팀 운영 저장소와 자동 배포는 연결하지 않는다.
- 기존 사용자의 ChatGPT 계정 로그인과 Github/Vercel 커넥터 권한은 **샌드박스 CLI 인증으로 자동 승계되지 않는다**. 인증·비밀키를 조사 로그에 기록하지 않는다.
- 외부 패키지를 설치하고 테스트할 수 있는 Vercel Sandbox는 **Codex Cloud 웹 UI 자체가 아님**.
- `setup_passed`와 `model_run_passed`를 구분한다. 모델 호출 이전에는 사용자 페인포인트 해결 여부를 결론 내리지 않는다.
- 영속 샌드박스가 중지될 때 파일은 스냅샷으로 유지되지만 프로세스는 유지되지 않는다. 자동 스냅샷 만료 전후 재접속·복구 확인 필요.

## 후속 단계

- Bathos 엔진 컴파일·설치·스모크 테스트의 실제 종료 상태 기록.
- 연결 가능한 로그인/모델 접근 경로를 승인받은 후 동일 입력으로 제품별 실행.
- 결과에서 '기존 서비스가 이미 해결한 부분'과 '사용자 개입이 남는 부분'을 구분해 R01 문제 정의를 갱신.
