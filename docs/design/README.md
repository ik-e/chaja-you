# 설계 문서

## 현재 레슨 등록 지원 서비스

- [현행 설계 기준 · 사람용](lesson-registration/CURRENT-DESIGN.md)
- [현행 설계 인덱스 · AI용](lesson-registration/CURRENT-DESIGN.json)

현재 Phase, 논리 설계 채택, 공통 구현 방향 IB-01~05, 작업 패키지와 검증 근거를 연결한다. 인덱스는 읽기용이며 새 정본/승인이 아니다.

| 찾을 내용 | 경로 |
| --- | --- |
| 논리 구성·책임·상태 | [아키텍처](architecture/README.md) |
| HTTP·업무 포트·실행 경계 | [API](api/README.md) |
| 데이터 의미·스키마·프로필 | [데이터](data/README.md) |
| 결정·선행 근거·TASK·시험 | [설계 결정](decisions/README.md) |
| 공통 구현·작업 공간 | [제품 계약](../../product/lesson-registration/contracts/README.md) · [작업 공간](../../product/lesson-registration/README.md) |
| 운영 상태 | [CURRENT](../../CURRENT.md) |
| 과거 설계·WBS·검토 | [고정 스냅샷](lesson-registration/README.md) · [전체 이력](lesson-registration/12-HISTORY.md) |
| 이전 설계 브랜치 정산 | [2026-11-25 브랜치 검토](lesson-registration/BRANCH-REVIEW-20261125.md) |

[AI 설계 정본 공간](../artifacts/design/README.md) · [ADR](../adr/README.md) · [문서 관리 규칙](../문서_관리_규칙.md) · [팀 헌장](../charter/팀_헌장.md)

현행 인덱스는 정본을 수정한 뒤 `node tools/generate_lesson_current_design.mjs`로 재생성하고 `--check`로 검사한다. 채택 전 스냅샷과 원본의 과거 상태는 보존한다. 실서비스 권한은 별도 승인이다.

- [현행 기준선 적용 규칙](lesson-registration/BASELINE-POLICY.md) · [독립 검증 실행](lesson-registration/VALIDATION.md)
