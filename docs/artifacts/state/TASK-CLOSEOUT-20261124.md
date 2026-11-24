# TASK-022~042 정산 및 인계 (2026-11-24)

[정산 원본 JSON](task_closeout_20261124.json) · [기존 TASK-001~021 정산 원본](legacy_task_closeout_20261118.json) · [현재 단계 의도](../../human/phase-intents/PHASE-20261124-02.md)

**원본 TASK의 상태·결과와 운영상 종료 분류를 구분한다.** 기존 TASK는 원본을 보존하고, 정식 배정되지 않은 번호는 다시 사용하지 않는다. 미완료 의무는 명시하되 신규 작업으로 자동 배정하지 않는다.

- 022~032: main의 이전 TASK 11개.
- 033~037: 설계 제안 5개(정식 TASK 파일 없음).
- 038~042: 닫힌 PR #41의 미병합 배정안 5개.
- 현재 활성: TASK-043~045. R01이 Discord 전달을 보고했으며, 팀원 개별 수신·착수·실행은 미확인.

## TASK별 사유 및 인계

| TASK / 이전 담당(제안 포함) | 원본 상태 | 처리 | 사유 | 후속 TASK·미해결 의무 |
| --- | --- | --- | --- | --- |
| [TASK-022](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-022.json) · R02 | 할 일 | 탐색 단계 종료·후속 채택 | 11/21 후보 비교를 위한 탐색 과제였다. 11/23 음악 레슨 등록 지원 방향을 선택했으므로 후보 탐색 자체를 반복하지 않는다. TASK-022 결과 미기록은 수행 실패 판정이 아니다. | TASK-028, TASK-032 — 기존 후보의 증거는 보존; 실제 사용자 가치와 지불 의향 검증은 후속 판단. |
| [TASK-023](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-023.json) · R03 | 할 일 | 탐색 단계 종료·비활성 | 레슨 등록 방향이 선택되어 기존 중고거래 관련 후보 탐색을 현 단계 구현 업무로 이어가지 않는다. 개별 후보의 기술적 실패를 의미하지 않는다. | TASK-031, TASK-043 — 기존 후보 기록 보존; 현재 검증은 레슨 등록의 모의 시험. |
| [TASK-024](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-024.json) · R04 | 할 일 | 탐색 단계 종료·비활성 | 제품 방향 결정 이후 기존 토지대장·지적도 등 독립 후보 심화는 현 단계 범위가 아니다. | TASK-029, TASK-044 — 후보 조사 기록 보존. 숨고 등록 객체 검증은 별도 목적의 후속 과제. |
| [TASK-025](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-025.json) · R05 | 할 일 | 탐색 단계 종료·비활성 | 제품 방향 결정 이후 테이블오더 등 후보 탐색은 현 단계 실행 과제가 아니다. | TASK-030, TASK-045 — 후보 기술 평가 기록 보존. 크몽 등록 PoC는 새 제품의 별도 업무. |
| [TASK-026](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-026.json) · R01 | 진행 중 | 기존 결과 보존·단계 종료 | 11/19 후보 검토 결과는 보존한다. 11/23 제품 방향 선택 이후 11/21 회의 준비를 신규 수행하지 않는다. TASK 완료 여부나 회의의 모든 결론을 소급 확정하지 않는다. | TASK-032 — 멘토 피드백·후보 선택 당시의 근거 및 미확인 사항은 필요시 재검토. |
| [TASK-027](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-027.json) · R01 | 진행 중 | 이전 설계 보류·제출 의무 유지 | 기존 제품 기준 잠정 제출 문서는 현재 본 구현 설계가 아니다. 기획 방향이 바뀌어 실제 설계는 검증 후 재수립한다. | 별도 판단 — 공식 제출·접수 확인 및 최신 기획에 따른 제출본 갱신은 R01 별도 의무. 제출 완료로 표시하지 않는다. |
| [TASK-028](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-028.json) · R02 | 완료 | 기존 완료·근거 재사용 | 기획 V1.1에 사용자·판매 조건 근거가 반영되어 기존 조사 반복은 불필요하다. | TASK-043, TASK-044, TASK-045 — 가상 fixture와 실사용 근거 구분; 실제 시간 실측·결제 및 플랫폼 허용 미검증. |
| [TASK-029](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-029.json) · R04 | 검토 중 | 기존 결과 보존·추가 조사 보류 | 5개 대안 조사 결과를 기획 V1.1에 반영했다. 현재는 숨고 PoC를 우선하며 기존 시장 조사를 전체 재수행하지 않는다. | TASK-044 — 실제 비용·도구 비교 성과·지불 의향은 추후 사용자 가치/BM 검증; 기존 추정치를 실측으로 승격하지 않는다. |
| [TASK-030](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-030.json) · R05 | 할 일 | 부분 조사 인계·전체 범위 보류 | 1차 당근·크몽 조사 문서가 별도 브랜치에 존재하지만 TASK result는 미기록이다. 3개 플랫폼 8개 영역의 전체 검증 완료 전이며 현 단계는 숨고/크몽 독립 PoC로 전환했다. | TASK-044, TASK-045 — 플랫폼별 공식 허용·등록 객체·인증·사진·실행/결과 복구·구조/비용을 해당 범위에 재사용. 탈잉 조사 및 실제 허용 검증은 보류, 실등록 승인 아님. |
| [TASK-031](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-031.json) · R03 | 할 일 | 부분 산출물 인계·전체 범위 대체 | 크몽·탈잉 비교 요구사항 초안이 존재하지만 TASK result는 미기록이다. 현재 R03 책임은 두 플랫폼 공통 모의 검증이며 제품 F1/F3 단독 구현은 미채택이다. | TASK-043, TASK-044, TASK-045 — 공통 요구사항과 오류/승인/미확인 규칙을 재사용; 숨고 객체와 플랫폼별 차이는 재검증. |
| [TASK-032](https://github.com/ik-e/chaja-you/blob/3b456f34765391bd230cf604e72cdaef84651539/docs/artifacts/tasks/TASK-032.json) · R01 | 검토 중 | 기준선 보존·후속 판단 대기 | 기획 V1.1을 독립 PoC 입력으로 사용한다. 본 구현 스택·실제 등록 허용·BM 최종 검증은 미결정이므로 원본을 완료로 변경하지 않는다. | TASK-043, TASK-044, TASK-045 — 11/27 PoC 근거 기반 채택·설계·MVP 범위 판단, 이후 제출본 갱신. |
| [TASK-033](https://github.com/ik-e/chaja-you/blob/dba2f5dc97a4c8a61d523831a51f6f30b1936efb/docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md) · R01 | 정식 파일 없음 | 미채택 제안·방향 대체 | 단일 크몽 E2E와 기능별 분업 전제의 설계 제안이다. 플랫폼별 독립 검증으로 변경되어 기존 제안을 배정하지 않았다. | TASK-043, TASK-044, TASK-045 — R01 공통 성공 기준은 현행 Phase 및 공통 시험 계약으로 이어짐. |
| [TASK-034](https://github.com/ik-e/chaja-you/blob/dba2f5dc97a4c8a61d523831a51f6f30b1936efb/docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md) · R02 | 정식 파일 없음 | 미채택 제안 | 실사용 자료를 테스트용으로 준비하는 별도 업무 대신 합성 fixture와 권한이 확인된 기존 근거 재사용을 택했다. | TASK-043, TASK-045 — R02에게 신규 실사용 자료 제출이나 별도 TASK를 요구하지 않는다. 실제 정보/이미지 권리 검증은 필요 시 별도 확인. |
| [TASK-035](https://github.com/ik-e/chaja-you/blob/dba2f5dc97a4c8a61d523831a51f6f30b1936efb/docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md) · R03 | 정식 파일 없음 | 미채택 제안·역할 변경 | R03이 제품 F1/F3 모듈을 소유하는 대신 독립 공통 테스트 환경을 담당한다. | TASK-043 — 제품 F1/F3 공통 구조 선택은 독립 PoC 후 보류. |
| [TASK-036](https://github.com/ik-e/chaja-you/blob/dba2f5dc97a4c8a61d523831a51f6f30b1936efb/docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md) · R04 | 정식 파일 없음 | 미채택 제안·역할 변경 | 단일 크몽 UI 개발 분업을 채택하지 않고 숨고 등록 핵심 기능을 독립 검증하도록 전환했다. | TASK-044 — 본 제품 UI 프레임워크와 공통 화면은 아직 미선정. |
| [TASK-037](https://github.com/ik-e/chaja-you/blob/dba2f5dc97a4c8a61d523831a51f6f30b1936efb/docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md) · R05 | 정식 파일 없음 | 미채택 제안·역할 변경 | 공통 API/이벤트 저장 등 사전 통합 구조를 확정하지 않고 크몽 등록 핵심 PoC로 전환했다. | TASK-045 — 공통 API·DB·배포 구조는 검증 후 선택. |
| [TASK-038](https://github.com/ik-e/chaja-you/blob/aa9a9092da5e0c8a6ed9565e8836b060e313f094/docs/artifacts/tasks/TASK-038.json) · R01 | 할 일 | 미병합 배정안·대체 | 테스트 환경만 만드는 기존 분업안을 취소하고 독립 PoC와 공통 검증의 범위로 변경했다. PR #41은 미병합 종료. | TASK-043, TASK-044, TASK-045 — R01 인수·채택 판단은 현재 단계 의도에서 유지. |
| [TASK-039](https://github.com/ik-e/chaja-you/blob/aa9a9092da5e0c8a6ed9565e8836b060e313f094/docs/artifacts/tasks/TASK-039.json) · R03 | 할 일 | 미병합 배정안·통합 대체 | 별도 계약/시험 작업을 R03이 전체 모의 하네스를 소유하는 TASK-043으로 통합했다. | TASK-043 — 크몽·숨고 양쪽 mock 및 버전 공유까지 포함. |
| [TASK-040](https://github.com/ik-e/chaja-you/blob/aa9a9092da5e0c8a6ed9565e8836b060e313f094/docs/artifacts/tasks/TASK-040.json) · R04 | 할 일 | 미병합 배정안·역할 대체 | 모의 페이지 책임을 R03에게 넘기고 R04는 숨고 독립 구현을 담당하게 변경했다. | TASK-043, TASK-044 — 숨고 실제 등록 객체는 확인 후 mock에 반영. |
| [TASK-041](https://github.com/ik-e/chaja-you/blob/aa9a9092da5e0c8a6ed9565e8836b060e313f094/docs/artifacts/tasks/TASK-041.json) · R05 | 할 일 | 미병합 배정안·역할 대체 | R05를 크몽 핵심 PoC에 집중시키고 공통 루트 환경 정리는 R01 기준선 관리, 하네스 재현성은 R03, 실험별 의존성은 각 담당이 관리하도록 변경했다. | TASK-043, TASK-045 — 공통 환경은 main에 반영됐으나 실제 설치·CI 결과를 별도 검증해야 함. |
| [TASK-042](https://github.com/ik-e/chaja-you/blob/aa9a9092da5e0c8a6ed9565e8836b060e313f094/docs/artifacts/tasks/TASK-042.json) · R02 | 할 일 | 미병합 배정안·미채택 | 별도 R02 업무 대신 R03이 합성 fixture를 준비하고 확인된 기존 R02 근거를 필요한 범위에서 재사용하도록 변경했다. | TASK-043 — 가상 사진·데이터와 실제 사용자/권리 정보를 구분. 권리가 불분명한 실자료 사용 금지. |

## 재사용·재개 기준

- 001~021은 11/18 원장과 불변 스냅샷을 변경하지 않는다.
- 022~032는 이전 당시 상태·결과 및 근거를 보존한다. 정산은 제출·실행 완료를 인증하지 않는다.
- 033~042는 신규 TASK로 다시 생성하지 않고 위 원본 커밋 링크로 추적한다.
- 보류 사항은 R01의 다음 결정 및 명시적 후속 TASK를 통해 재개한다. 기존 번호 재사용 금지.
- 027의 실제 제출·접수 확인, 029~032의 미검증 사용자 가치·플랫폼 허용·설계 결정 등은 취소된 의무로 간주하지 않는다.
