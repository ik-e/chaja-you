# 2026-11-18 이전 TASK 종료 정산 · 원본 근거 보존

2026-11-18 R01의 투 트랙 전환 및 이전 TASK 정산을 위한 **당시 파일 원문 스냅샷**입니다. [manifest.json](manifest.json)이 모든 복제본의 원래 경로·기준 커밋·Git blob SHA를 보존합니다.

- **main 기준 커밋**: [`5f6a669718d6`](https://github.com/ik-e/chaja-you/commit/5f6a669718d6cc710b7f40d047cacab587991f84)
- **R05 개인 브랜치 기준 커밋**: [`a9db2e4dfa53`](https://github.com/ik-e/chaja-you/commit/a9db2e4dfa53f4525e5ac82ec71e88a02f321ca0)
- **정산 원본**: [이전 TASK 정산 JSON](../../artifacts/state/legacy_task_closeout_20261118.json) · [ADR-003](../../adr/ADR-003_이전_TASK_정산과_근거_보존.md)

## 보존 범위

- `snapshots/main/docs/artifacts/tasks/TASK-001.json` ~ `TASK-021.json`: 정산 당시 **21개 TASK의 원문**. 이후 owner가 변경해도 여기는 변경하지 않습니다.
- `snapshots/main/`: 11/17~18 회의 요약 원본, 당시 Phase Intent·R01 지시, 기존 선정 기준·제출 기록, 기획서·WBS 원본 등
- `snapshots/Imdahyeok/`: R05 개인 브랜치에서 작성된 다섯 안 평가 취합, R03/R05 멘토용 취합, 테이블오더 v5, TASK-014의 브랜치별 완료 결과. **main에 통합·승인된 사실로 간주하지 않습니다.**

각 스냅샷 파일은 **원본 Git blob SHA를 그대로 재사용**했으므로 manifest의 `blob_sha`와 사본의 Git blob SHA가 일치합니다. 정산 판단과 사본은 덮어쓰지 않고, 새로운 근거가 나오면 새 날짜/버전의 정산 기록과 결정 이력으로 변경합니다.

## 보존하지 않는 것과 검증 한계

비공개 Discord 기록, 인용된 외부 사이트의 과거 웹 페이지 전체, 교육기관 대시보드, 접근 권한이 불명확한 첨부 파일은 자동 복사하지 않습니다. 해당 자료는 접근 가능 범위·출처·확인 시점·미확인 상태로 기록합니다. 원본 파일의 존재와 내용 정확성은 별개입니다.
