# 현행 설계와 공식 제출 문서 연결 · 2026-11-25

기준 main `366cea92a497ff68176107766b1314ab75d5c59f` 및 R01 후속 검토. [현행 설계](CURRENT-DESIGN.md) · [시스템 구조 요약](SYSTEM-OVERVIEW.md) · [구조화 매핑](../../deliverables/lesson-registration-20261125.json) · [16개 공식 산출물 레지스트리](../../deliverables/registry.json). 별도 설계 정본이 아니라 현행 원본→제출용 뷰/실제 산출물의 연결. 문서별 원본·상태는 구조화 매핑에서 확인한다.

| 산출물 | 가이드 마감 | 현재 경로 | 준비 상태 |
| --- | --- | --- | --- |
| DLV-01 기획서(요구사항 명세 포함) | 2026-11-13 | [보기](../../step1/기획서_제출본.md) | 현행 mock 범위 반영 후보 |
| DLV-02 WBS | 2026-11-13 | [보기](../../step1/WBS_제출본.md) | 11/25 V0.6 후보 · R03 실제 조립 계획, R04 9/6 CI, R05 최신 30/37 독립 조합 CI; 갱신 잔여/일정·캡처 미확인 |
| DLV-03 API 설계 문서 | 2026-11-20 | [보기](../../step2/API_설계_문서.md) | 11/25 S8/launcher 독립 시험 통과 · R03 실제 WS/STORE/slot/asset 조립 계획, 전체 연동 미확인 |
| DLV-04 데이터베이스 스키마 설계서 | 2026-11-20 | [보기](../../step2/데이터베이스_스키마_설계서.md) | R03 SQLite DDL main; 실제 stable slot/asset/permit/lease 조립 대기 |
| DLV-05 단일 에이전트 상태 전이 그래프 설계서 | 2026-11-27 | [보기](../../step3/단일에이전트_상태전이그래프_설계서.md) | 11/25 9항목 현행 PREP 코드 대조 · 추가 보정 후보와 분리, R02 확인·공식 제출 미확인 |
| DLV-06 자기 성찰 로직 테스트 결과서 | 2026-12-04 | [보기](../../step3/자기성찰_테스트결과서.md) | 11/25 실제 모델 초기 비교 보고 연결 · 자기 성찰 A/B·보정 0건, 결과서 미완료 |
| DLV-07 멀티 에이전트 협업 아키텍처 설계서 | 2026-12-11 | [보기](../../step4/멀티에이전트_협업_아키텍처_설계서.md) | 현행 협업 구조 및 추가 AI 역할 후보; 실제 멀티 에이전트 미검증; 공식 양식 최종 대조 전 |
| DLV-08 AI 보안 가드레일 설계 문서 | 2026-12-18 | [보기](../../step4/AI_보안_가드레일_설계_문서.md) | 11/25 PR44 main 안전 기준 및 최신 Runtime/Viewer 회귀 · 실제 통합/운영 보안 미검증 |
| DLV-09 Auto-Healing 구현 결과서 | 2026-12-18 | [보기](../../step4/Auto-Healing_구현_결과서.md) | 시험 계획만, 실제 Auto-Healing 측정 not_run |
| DLV-10 대화형 AI 웹 애플리케이션 | 2026-12-24 | 미작성 | 11/25 R03 HTTP·R04 UI 9개 CI, Viewer 보완 main · 실제 H1~H9·WS/Runtime·배포 미확인 |
| DLV-11 통합 테스트 결과서 | 2026-12-31 | 미작성 | 22개 gate preflight 통과·최신 R05 독립 조합 30/37; 전체 gate 0/22, 실제 통합·배포 설계도 대기 |
| DLV-12 배포 아키텍처 설계도 | 2026-12-31 | 미작성 | 물리 방향 있음; 실제 배포 환경/네트워크/CI/CD·보안 확인 후 설계도 |
| DLV-13 중간 발표 PT 자료 | 2026-12-08 | 미작성 | 12/8 발표용 핵심 문제/설계 근거 준비; 실제 시연 범위·성과 및 PT 제작 대기 |
| DLV-14 최종 발표 PT 자료 | 2027-01-04 | 미작성 | 최종 평가/시연/발표 PT 대기 |
| DLV-15 프로젝트 개발 소스코드 | 2027-01-04 | 미작성 | 제품 소스 개발 중; 최종 제출 commit/재현/접근 확인 대기 |
| DLV-16 시연영상 | 2027-01-04 | 미작성 | 실제 통합 시연·영상 제작/열람 확인 대기 |

**공식 제출·접수:** 16개 모두 실제 대시보드 확인 전 미확인. [11/24 강사 원본 가이드](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/README.md) · [OUTPUT-GUIDE](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/OUTPUT-GUIDE.md) · [제출 상태](../../submissions/README.md). 제공 목차·별도 WBS 캡처·가독성/열람권한·대시보드·접수 확인은 별도. 이후 실제 실행 결과가 필요한 산출물은 근거가 생긴 뒤 작성한다.

**현행과 과거:** [Step1](../../step1/README.md) · [Step2](../../step2/README.md) · [Step3](../../step3/README.md) · [Step4](../../step4/README.md). 이전 찾아you 생성 문서/11/23 후보는 이력, [고정 설계 뷰](README.md)는 당시 스냅샷. PR #44는 main에 병합됐다. 세부 후보의 실제 구현 정합성 및 최종 서명은 별도 검토한다. 실제 통합/운영 보안·교육 기술 효과는 후보 시험과 구분한다.

**갱신 원칙:** [R01 핵심 Pain 우선·일일 조정](../../human/responses/HRESP-20261125-06_pain-first-rolling-plan.md). 제품 문제 해결 우선, 교육 요구를 가치에 기여하는 기술/추가 기능으로 충족. 매일 진행·잔여 공수·가용성·막힘 확인, 영향 문서만 동기화. 정본과 제출 준비 상태를 동시에 수정하되 과거 파일 보존. 제품 범위/공통 안전 계약/배정은 별도 판단 없이 변경하지 않는다.
