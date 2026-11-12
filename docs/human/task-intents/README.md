# TASK별 R01 작업 의도

이 디렉터리는 각 TASK를 수행할 때 R01이 중요하게 보는 목적·우선순위·범위 경계를 보존합니다.

문장은 AI가 구조화할 수 있지만 `authority: R01`인 문서의 의미에 대한 최종 권한은 R01에게 있습니다. `drafted_by: AI`는 작성 주체를, `status`는 R01 확인 상태를 나타냅니다.

## 사용 규칙

- TASK에 `intent_ref`가 있으면 작업 시작 전에 해당 파일을 읽습니다.
- Task Intent는 작업 목적·우선순위·범위 경계의 권위 입력입니다.
- Task Intent는 외부 사실이나 조사 결과를 미리 정하는 정답이 아닙니다.
- 근거가 의도의 가정과 충돌하면 결과를 의도에 맞추지 말고 충돌과 근거를 TASK result에 기록합니다.
- Task Intent와 다른 결론을 제안할 수 있으며, 중요한 차이는 `decision_requests`로 R01에게 돌립니다.
- Task Intent 자체를 ADR·current·spec의 확정 결정으로 자동 승격하지 않습니다.
- 최종 프로젝트 기준으로 채택할 내용은 R01 검토 후 ADR·state·spec 등에 별도로 반영합니다.

## 현재 의도

- [TASK-003 · R04 사용자 문제·결과 화면](TASK-003.md)
- [TASK-004 · R02 데이터·이용 조건·운영 제약](TASK-004.md)
- [TASK-005 · R03 동적 구성 MVP·평가](TASK-005.md)
