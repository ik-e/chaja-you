# R01 통합 후보 인수·수용 검증 · TASK-048

[공통 기준](../contracts/CURRENT-BASELINE.md) · [22개 수용 시험 준비 목록](product-gate-readiness-20261125.json) · [실행기](PRODUCT-GATE.md) · [팀 최신 근거](team-integration-checkpoint-20261125.json) · [독립 조합 CI](https://github.com/ik-e/chaja-you/actions/runs/45568163241/job/139047965594).

R03가 실제 App/STORE 조립을 주도한다. R01은 중복 제품 구현 대신 제출된 고정 후보의 독립 검증과 전체 수용 시험을 담당한다. R02/R04/R05는 본인 코드와 시험을 관리한다. 공통 변경이 필요한 경우 실제 서명·예제·정상/실패/unknown 시험 및 영향만 반환한다.

## 인수 조건

- 최신 main 및 담당별 고정 SHA, 변경 경로, 동일 lock, 명시 provider factory와 실행 명령, loopback mock 원본/이미지/계정, 종료/폐기, 정상·실패·미실행 범위를 기록한다.
- 실제 서비스에서 HTTP/WS 동일 owner, H6 /authentication 및 revision, same-origin module/canvas, 합성 성공 fallback 제거, verified-before-review, H6부터 stable lineage slot, 현재 lease 승인 asset reader, exact binding manifest, permit consume 및 fence/dispatch, 별도 read authority를 확인한다.
- 크몽 정상: 실제 접수 1회, 승인값·이미지·target·independent receipt 대조. 오류: 응답 유실/307·308/재실행/old lease/다른 owner/target/asset 변조 및 실제 mutation count. 이후 실제 PREP, UI/Viewer, 숨고 actual persisted state/readback 및 양 플랫폼 교차. 첫 수직 동작을 전체 완료로 판정하지 않는다.
- 후보 SHA/tree, 명령, fixture/profile digest, 예상/실제 응답과 상태, mutation/dispatch 수, 독립 근거/명시적 부재, 종료·비밀 비노출, pass/fail/incomplete/not_run을 기록한다.

## 전체 gate 등록 준비

| 묶음 | 시험 | 선행 구현 |
| --- | --- | --- |
| 원본/준비 | AT-01, T5-08, T5-11, T6-01, T6-02 | 실제 I2/H1~H5, 별도 승인 모델, revision·답변 보존 |
| 인증/승인/경계 | AT-02, AT-03, T5-01, T5-02, T5-12, T5-03, T5-07 | 실제 HTTP/Viewer/STORE/Runtime/registry |
| 플랫폼 정상/독립성 | AT-04, AT-05, T5-06, T5-13 | 양 플랫폼 실제 adapter 및 mock 저장/독립 조회 |
| 재접속·장애 | T5-05, DV-01~05 | 실제 UI/HTTP/WS·job·effect와 오류 주입 |

준비 목록은 채택 gate의 기대를 실제 구현에 대응한 점검 목록이며 신규 계약이 아니다. 전체 실행 함수 PRODUCT_CASES 등록은 정확한 assertion과 관측 근거를 연결하여 R01이 검토한다. 현재 0/22. T5-08은 현재 실행기가 실제 모델 자동 호출을 차단한다. R02의 실험 설계/비용 검토 후 동일 후보의 승인된 실제 모델 시험 실행 및 release 판정 연결 방법이 필요하다. 기본 CI에는 유료 모델 호출 없음. 기존 preflight 및 Runtime/크몽 조합 30/37 통과는 supporting evidence만이다.

## 작업 브랜치

r01/product-integration은 WORKSPACE와 TASK-048의 활성 지정 경로이므로 유지하고 최신 main으로 fast-forward한다. r01/product-prep-20261125는 main ancestor이며 고유 변경 0, bootstrap SHA 이력 참조 유지; 정리 후보로 기록하되 삭제 도구/권한 확인 전 보존한다. 다른 담당 브랜치를 수정하지 않는다.
