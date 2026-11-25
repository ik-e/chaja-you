# 공통 모의 검증 계약 v0.1 (착수 기준)

정본 책임 R03 / TASK-043. R04·R05는 독립 구현을 시작하고 공유 항목의 변경만 상호 확인한다. 이 계약은 시험을 연결하기 위한 최소 어휘이며 제품 API, DB, 언어, 실제 플랫폼 양식의 필드 정의가 아니다. 실제 외부 서비스는 호출하지 않는다.

## 전달 단위

- R03은 크몽 레슨 상품과 숨고에서 R04가 근거를 확인한 등록 객체의 mock을 제공한다. 미확인 필드/객체는 가설로 표시한다.
- 시험 입력: `contract_version`, `fixture_id`, `case_id`(T1~T6), `platform`(kmong/soomgo), `environment`(mock), `source_version`, `approved_draft_version`, `actions`, 합성 입력/이미지 참조. 승인 없음·값 누락·버전 충돌은 구분한다.
- 결과: `case_id`, `platform`, `environment`, `result_state`(mock_success/failed/unknown/needs_confirmation/blocked), `retry_blocked`, 관측값, 오류 사유, `evidence_refs`. 정확한 타입/필수성은 R03이 R04/R05와 협의해 버전화한다.
- 검증은 실제 모의 폼/상태 관측을 근거로 한다. mock_success는 실제 게시/심사 접수가 아니다. 승인 없는 동작·live·unknown 재제출은 차단한다.

## 실행과 고정 버전

R03은 README 또는 release manifest에 mock 시작/종료 명령, 로컬 접속 주소, fixture·case 목록, 계약/fixture 버전을 적는다. 하네스는 loopback(127.0.0.1)에서만 제공하고 실서비스 네트워크·자격증명·데이터 없이 재현한다. release commit SHA는 커밋 이후 TASK 결과/전달 기록에 명시한다.

다른 구현자는 하네스 branch 전체를 병합하지 않고 별도 checkout을 사용한다.

```bash
git fetch origin r03/task-043-dual-platform-harness
git worktree add --detach ../chaja-you-test-harness <R03-release-commit-SHA>
```

별도 checkout의 `prototype/lesson-registration/test-harness/README.md`에 적힌 명령으로 mock을 시작하고, 자신의 작업 디렉터리에서 PoC를 실행한다. 위 SHA는 R03이 실제 배포한 값으로 교체한다. mock URL이나 파일 경로를 입력으로 전달할 수 있게 하되 내부 구현/CLI는 각 담당이 정한다. 단순 데이터 검증은 fixture 파일을 읽는 방식도 가능하다.

**공통 기록:** 구현 commit, 하네스 commit, 계약/fixture 버전, 실행 환경/명령, case별 기대·관측값, pass/fail/inconclusive, 증거 경로. 하네스 미완성 시 초기 자체 실행은 가능하지만 공통 검증 통과로 표시하지 않는다. 현재 하네스 release와 시험 실행은 미완료다.

[작업 계약 및 T1~T6](../../../docs/artifacts/design/lesson-registration-20261124/PLATFORM-INDEPENDENT-WORK.md) · [R03 작업](../../../docs/artifacts/tasks/TASK-043.json).
