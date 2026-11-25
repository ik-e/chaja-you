# 이전 R01 설계 브랜치 검토 · 2026-11-25

비교 기준 main: `ffc5477c03f9955b8a899d9613c86dba17f13122`. 열린 PR의 head/base 대조, commit compare 및 분기 고유 변경 파일의 blob 비교를 수행. 브랜치 삭제는 이 기록만으로 수행되었다고 간주하지 않는다.

| 브랜치 | 확인한 HEAD | main에 없는 커밋 | 판단 / 근거 |
| --- | --- | ---: | --- |
| r01/lesson-design-baseline-20261124 | [37e85eb](https://github.com/ik-e/chaja-you/commit/37e85eb616ead67afc75def7c2ec5bcff76b41ae) | 0 | 삭제 후보: HEAD가 main 조상, V0.8 및 검증 근거가 이력에 보존 |
| r01/lesson-redesign-20261124 | [d68406b](https://github.com/ik-e/chaja-you/commit/d68406b895b344819eb7ed6c3524167789bfdb84) | 0 | 삭제 후보: HEAD가 main 조상, 채택 기록의 고정 ref와 원본/프로젝션 보존 |
| r01/product-prep-20261125 | [98b446c](https://github.com/ik-e/chaja-you/commit/98b446cb70eeaf95d02d69f36821b04d4d583913) | 0 | 삭제 후보: HEAD가 main 조상, bootstrap 및 제품 공간 증거 보존 |
| r01/lesson-design-kickoff-20261123 | [dba2f5d](https://github.com/ik-e/chaja-you/commit/dba2f5dc97a4c8a61d523831a51f6f30b1936efb) | 7 | 보존: 분기 고유 파일 6개, ADR-004·design-intake·milestone 등; MVP 분기의 조상이지만 main 조상 아님 |
| r01/lesson-mvp-workspace-20261124 | [aa9a909](https://github.com/ik-e/chaja-you/commit/aa9a9092da5e0c8a6ed9565e8836b060e313f094) | 44 | 보존: 분기 변경 25개 중 24개 main과 다름/부재, 과거 TASK-038~042·환경/설계 자료. 현재 제품 기준에 무조건 병합하지 않음 |
| r01/planning-design-information-model-20261119 | [d582a84](https://github.com/ik-e/chaja-you/commit/d582a84e4f8c22ff3ca36acd6381d2d9132c4230) | 69 | 보존: 변경 16개 중 12개 동일, 4개 설계 문서/정보 모델의 blob 차이. 설계 체계의 변화와 고유 커밋 정산 필요 |
| r01/validation-requests | [4ea55d6](https://github.com/ik-e/chaja-you/commit/4ea55d6e1ac05ce42b2351262c9ecef97ba7b8a2) | 4 | 보존: selective-design-validation.yml, run_validation.mjs, validation-request.json 모두 main 부재. 독립 검증 도구 재사용 여부 별도 판단 |
| r01/product-integration | [ffc5477](https://github.com/ik-e/chaja-you/commit/ffc5477c03f9955b8a899d9613c86dba17f13122) | 0 (검토 시점) | 유지: 활성 TASK-048 작업 브랜치 |

해당 후보에 연결된 열린 PR 없음(검토 시점). 팀원 브랜치 및 R01의 다른 운영·실험 브랜치는 이번 범위 밖이다.

## 실행 상태

브랜치 정리 후보만 확정. 연결된 GitHub 도구에는 remote ref 삭제 작업이 제공되지 않아 삭제는 미실행. 삭제 직전 HEAD/조상 여부/열린 PR/활성 참조를 재확인하고 확인한 HEAD가 달라졌으면 중단한다. 분기 고유 기록이 있는 브랜치는 승인 없이 병합하거나 삭제하지 않는다.

이전 설계 파일 자체를 삭제하거나 이동하지 않는다. [현행 설계 기준](CURRENT-DESIGN.md)과 [고정 이력](12-HISTORY.md)으로 조회한다.
