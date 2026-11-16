# R01 discovery 작업 상태 — 2026-11-16

## 실행 환경·범위

- 저장소: ik-e/chaja-you
- 브랜치: experiment/r01-codex-cloud-20261114
- 기준점: 2026-11-16 계획 반영 커밋 d099960
- 환경 확인: Codex 관리 runtime 상태 도구에서 provider=cloud, observed_phase=running, connectivity=connected를 확인. 로컬 환경에도 CODEX_CI=1, CODEX_ENVIRONMENT_ID 설정, CODEX_PRIMARY_RUNTIME 경로가 확인됨.
- 허용 범위: experiments/r01-codex-cloud/discovery/ 신규 산출물만.
- 보호 범위: main, 운영 코드/API, 공식 팀 문서, B0 결과는 수정하지 않음.

## 파일별 상태

| 파일 | 상태 | 실제 수행 / 미수행 |
|---|---|---|
| 01-hypotheses.md | passed | R01의 이전 가설과 A/B 타겟 후보 및 U1~U4 근거 수준·반증 조건을 정리. 시장 문제 입증은 not_run. |
| 02-user-incidents.md | passed | 공개 이슈 사건 7건과 해결/반례 2건, 독립 계정 중복 주의, 피해/비용 unknown을 기록. 독립 재현·인터뷰는 not_run. |
| 03-existing-alternatives.md | passed | BATHOS, BMad, OpenSpec, 강한 Codex/ChatGPT 프로젝트 지침·기억과 수동 checklist를 대조. 대안별 실제 효능 측정은 not_run. |
| 04-shortlist-and-decision.md | passed | 근거가 제한된 타겟-문제 후보를 2개로 제한하고 점수·반증·인터뷰 질문·최소 시험을 작성. 후보 채택 결정은 R01 pending. |
| 05-next-experiment.md | passed | 강한 Codex 기준선 중심의 후속 시험을 설계. fixture 제작·실험 실행·사용자 인터뷰·BMad/OpenSpec 설치/실행은 모두 not_run. |
| STATUS.md | passed | 본 파일. 01~05 산출물 기준 커밋 SHA와 수행 경계를 기록. |

## 실제 수행 및 미실행 구분

- 수행: 지정 문서(HANDOFF, README, TASK_PROMPTS, shared scenario/decisions, 2026-11-16 plan), R01 R4 및 경쟁 조사 자료 읽기.
- 수행: OpenSpec/BMad/Codex/BATHOS 공개 GitHub issue와 공개 제품 문서를 읽기 전용으로 확인하고 근거 링크·게시 시점·보고자 주장을 정리.
- 수행: 사용자 사례 7건, 긍정적/해결된 반례 2건 및 issue 참여 계정 중복 주의를 기록.
- 수행: 각 incident의 계획 필수 필드 구조 점검, git diff --cached --check.
- not_run: 외부 사용자에게 연락 또는 인터뷰 요청 발송, 사용자 인터뷰.
- not_run: BMad/OpenSpec 설치·실행, 제품/업무 코드 개발, 실제 API 호출, fixture 제작·실험 실행, 자동 테스트/성능 측정.
- not_run: 유료 서비스 이용, 크레딧 구매, 외부 repo 쓰기.
- GitHub 공개 source의 읽기 전용 조회만 했다. issue/comment를 생성하거나 수정하지 않았다.
- 별도 승인 요청: 0건. 외부 인터뷰는 지시대로 발송하지 않았다. 추가 사용자 개입/후속 지시도 없었다.
- 실패: 조사 산출물 작성/구조 점검에서 실패한 항목 없음. 이슈에 기재된 사용자의 실패 보고는 독립적으로 재현한 결과가 아니다.

## 커밋

- 01~05 산출물 커밋 SHA: 5b6fce1643b1a855d49000f4268dd8b32695c894
- 이 SHA는 01~05 파일의 변경을 포함한다. STATUS.md 자체는 뒤이은 상태 기록 커밋에 포함되며, 최종 브랜치 HEAD SHA는 완료 보고에서 별도로 제시한다.

## 근거 부족

- 실제 사용자 인터뷰·관찰이 없어 타겟 A(소규모 팀 실무 책임자)와 B(숙련 개인 개발자)의 역할·팀 규모·반복률이 검증되지 않았다.
- 보고된 비용 중 상당수의 인시·금액은 unknown. 공개 issue 표본은 선택 편향이 있으며 발생률·시장 규모·지불 의사를 추정할 수 없다.
- OpenSpec/BMad/BATHOS의 현행 버전에서 각 보고가 해결됐는지 직접 실행하지 않았다. 이슈 상태만으로 현재 제품 결함을 단정하지 않는다.
- 보고자 본인의 설명이므로 사건의 독립 재현, 실제 결과 손실 여부, 조직 간 독립성은 일부 unknown.
- Codex MCP 반복 승인의 최신 버전 재현 조건과 총 감독 시간은 미확인.
- B0 결과는 기존 모의 Status API 기준선이며 실제 사용자 고통의 증거가 아니다.

## R01 판단 필요

1. 후보 1(다중 저장소 변경/상태 검증)과 후보 2(Codex/MCP 반복 승인) 중 어떤 타겟을 먼저 사용자 검증할지 선택.
2. 실제 연락 가능한 사용자가 있는지, 인터뷰 대상 선정·접촉·기록 동의를 승인할지 판단. 이번 작업에서는 외부 연락하지 않음.
3. 인터뷰에서 반복 사건과 피해가 확인될 경우, 격리된 mock fixture로 강한 Codex 기준선을 먼저 실행할지 결정.
4. 강한 Codex 기준선 이후에도 잔여 문제가 관측될 때 OpenSpec을 별도 대조 조건으로 투입할지 결정.
5. 어느 가설도 공식 제품 도메인이나 팀 MVP로 채택하지 않음. 공식 팀 문서·main·B0 산출물은 변경하지 않음.
