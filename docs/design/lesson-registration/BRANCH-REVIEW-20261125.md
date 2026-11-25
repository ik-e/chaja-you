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

## R01 후속 결정 · 이력 정산

사용자 지시(2026-11-25): 이전 설계는 계속 진행하지 않고 기록으로만 남기며 정확한 현행 기준선을 사용한다. [기준선 정책](BASELINE-POLICY.md).

- 단일 보관 브랜치 [archive/r01/design-history-20261125](https://github.com/ik-e/chaja-you/tree/archive/r01/design-history-20261125), 보관 커밋 `5e03e087213675bc8e8a0ba484318f6c68d5264a`. 트리는 당시 main과 동일하고, MVP(착수 포함), 설계 정보 모델, 이전 검증 실행기 HEAD를 추가 부모로 연결한다. **main에 병합하지 않는다.** 과거 내용의 채택이나 완료로 해석 금지.
- 정보 모델 변경 16개 중 12개 동일, 나머지 4개는 main에 실제 정제·합성·변경 검증 정책만 추가된 후속 버전. 재병합 불필요.
- 초기 착수·MVP 자료는 ADR-004 제안, 이전 로컬 가설, 이전 TASK/환경의 이력으로만 보존. 과거 설계 재개 없음.
- 이전 검증 실행기는 현행 V5/V4.1/공통 V1/추적·IB를 호출하는 [새 실행기](VALIDATION.md)로 기능 계승. 과거 요청·검증 정책은 재적용하지 않음.
- 원래 7개 브랜치 ref는 삭제 기능 부재로 남아 있음. 보관 조상 관계와 HEAD 재확인 후 로컬에서 삭제 가능. 활성 product-integration 및 팀원 브랜치 유지.
