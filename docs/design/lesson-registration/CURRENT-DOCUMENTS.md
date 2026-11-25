# 현행 설계와 공식 제출 문서 연결 · 2026-11-25

기준 main `4992959c08a12ad81a983ea4a89fed0837c0f1f8` (논리·물리 원본은 f5e6857 기준). [현행 설계](CURRENT-DESIGN.md) · [시스템 구조 요약](SYSTEM-OVERVIEW.md) · [구조화 매핑](../../deliverables/lesson-registration-20261125.json). 별도 설계 정본을 생성하지 않으며 현행 원본→읽기용/제출용 문서의 연결만 정리한다.

| 산출물 | 현재 경로 | 원본 | 상태 |
| --- | --- | --- | --- |
| DLV-01 기획 | [Step1](../../step1/기획서_제출본.md) | V1.1, REQ-01~11, adoption, CS/IB/PD | 채택 mock 범위 반영 |
| DLV-02 WBS | [Step1](../../step1/WBS_제출본.md) | V0.6 후보, TASK/WORKSPACE | 잔여 공수/일정 미확정 |
| DLV-03 API | [Step2](../../step2/API_설계_문서.md) | H1~H9/I1~I5, V4.1 | S8 main 반영, 실제 연동 미확인 |
| DLV-04 DB | [Step2](../../step2/데이터베이스_스키마_설계서.md) | V4.1, SQLite, R03 main 고정 SQL | 현재 DDL 확인, 최종 연동 미확인 |
| DLV-05 상태 전이 | [Step3](../../step3/단일에이전트_상태전이그래프_설계서.md) | I2/TASK-049, 내부 graph 후보 | R02 확인 필요 |
| DLV-06 자기 성찰 | [Step3](../../step3/자기성찰_테스트결과서.md) | graph 후보, T5-08, 실제 run | 계획, not_run |
| DLV-07/08 | 협업 아키텍처/보안 | 현행 구조 및 PR #44 보안 후보 | 후속 제출용 갱신 |
| DLV-09~16 | 결과/릴리스/발표 | 실제 run/배포/발표 증거 | 후속 |

[11/24 강사 원본 가이드](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/README.md) · [OUTPUT-GUIDE](https://github.com/ik-e/chaja-you/blob/f5e685716a5ed4fb36159d215b3cc861ef3d5e79/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/OUTPUT-GUIDE.md) · [제출 상태](../../submissions/README.md). 제공 목차 우선. 실제 제출 형식·렌더·열람·대시보드·접수는 별도. 이전 찾아you 생성 문서와 11/23 후보는 Git 이력, [고정 설계 뷰](README.md)는 당시 스냅샷으로 유지.

PR #44 검토 중인 세부 계약을 채택 원본으로 승격하지 않는다. 병합 및 실제 구현 차이 확인 후 영향받는 문서만 갱신. 현재 제출 후보의 목적은 중복 작성 없이 현행 정본을 이해하고 평가할 수 있도록 하는 것이다.

**운영 방향:** [R01 11/25 핵심 Pain 우선·일일 조정](../../human/responses/HRESP-20261125-06_pain-first-rolling-plan.md). 교육 기술은 제품 가치와 연결, 부족한 요구는 추가 기능 후보로 충족. 실질 설계·구현 초기의 변화를 수용하며 일일 근거·가용성에 따라 WBS를 갱신한다. 새로운 배정·일정/기술 확정은 아니다.
