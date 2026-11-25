# V0.8 설계 보완 및 상태 보고

검토/변경 기준: V0.7 독립 검토(3d0ebdf2a19e48ea00533566ddbb209232f8e6fa). R01의 위임에 따라 기존 목표·방향·단계·WBS 날짜/담당·정식 TASK를 변경하지 않고 상세 설계 및 검증 계획을 보완했다. 이 보고는 구현 착수 승인 또는 실서비스 허가가 아니다.

## 자율 처리 및 종료 기준
- 기존 의도/요구/결정으로 해소 가능한 구조·계약·추적·시험 누락은 AI가 수정하고 근거 및 재검증을 기록한다.
- 목표/범위/핵심 방향/팀원 업무·일정의 중대한 변경, 실제 플랫폼 허용과 위험 수용은 R01 판단으로 남긴다.
- 현재 단계의 필수 계약 충돌이 해소되고 검증 통과, 미확인 위험의 후속 작업 및 판정 조건이 연결되면 종료한다. 개별 수정의 사용자 승인을 반복 요구하지 않는다.
- 검증 불가능한 조건이나 실행되지 않은 시험은 pass로 기록하지 않는다. 발견된 모든 미래 위험을 설계 단계에서 해결하려고 무한 반복하지 않는다.

## 변경과 증거
| V0.7 발견 | V0.8 조치 | 상태 |
|---|---|---|
| IR-01 호출/의존성 | C4-02→09, C4-05→06/07/08, C4-09→07 반영. C4-07→05 제거. 게이트웨이가 C4-10 원자 저장 경계에서 검증하고 결과 반환; coordinator callback 금지. | 11→0 불일치, DAG 통과 |
| IR-02 재개 조건 | V3-J03 최초 planned만, V3-J20 needs_action/blocked의 HTTP-13 explicit_resume_current + safe_next_step_proven. unknown 안전 재확인 전 조회만. | 구조/가드 검증 통과; 실제 CAS·경쟁 검증 별도 |
| IR-03 입력 계약 | HTTP-02 typed multipart file+AssetUploadMetadata, 서버 파생 식별자/지문. HTTP-17 typed ReadRequest path/query, no body, revision 순. | 2→0 미정의 입력. 구현 serializer/fixture 검증 별도 |
| IR-04 제어권 | 기존 mock-only, 권한/lease/격리 및 우회 차단 원칙 유지. | W04/W11 구현 실증, 실제 인증/운영 승인 전 live 차단 |
| IR-05 MVP gate | MVP-GATE-01 20 필수 시험, 동일 build/contract/fixture/environment 근거, AI 실제 모델 실행, 누락/불일치 incomplete. W09 추적 보완. | 설계 및 판정기 시험 통과; 제품 미실행 |
| IR-06 상세 실행 명세 | ActionDefinition/ActionArgumentSpec, 버전별 registry, 인자 binding 및 사전/사후/증거 ref 미해결 시 deny. AI-01~03 합성 원문/기대값/충돌/실패 기준. | 공통 계약 보완; 실제 플랫폼별 action 정의·검증기는 W01/W06/W08 |
| IR-07 외부 의존 | GAP-01/02/05 유지, 실측·플랫폼 허용·공수 별도. | 미검증 |
| IR-08 인계 위험 | IC05 R02 인계→R03 연결·실제 시험 순서 명시. | 일정/담당 불변, 실제 가용성 확인 W01 |

정본은 기존 경로의 구조화 JSON(각 revision *-v08)이며 변경 전 버전은 Git 이력에 보존한다. 기존 V0.3~0.5 읽기 문서의 해당 절은 최신 정본 및 이 보고와 함께 읽는다. 상세 동기화는 후속 산출물 projection의 일부이며 기존 버전 문구를 현재 계약으로 오인하지 않는다.

## 재검증 결과
2026-11-24, 원격 GitHub의 고정 commit/blob을 읽고 실제 저장소의 JavaScript 검증 함수를 직접 실행했다(파일시스템 CLI, GitHub Actions 재실행과 구분).
| 검사 | 통과 |
|---|---|
| V0.5 정적 | 25/25 |
| V0.5 추상 | 31/31 |
| V0.6 추적 인덱스 | 29/29 |
| V0.6 정보 그래프 | 8/8 |
| V0.6 회귀 | 25/25 |
| V0.7 원본 제약 | 10/10 |
| V0.7 결함 주입 | 21/21 |
| V0.8 보완 제약 | 8/8 |
| V0.8 결함 주입 | 8/8 |
| V0.8 MVP 판정기 합성 | 12/12 |

18개 인덱스 원본 blob SHA 일치. 정보 그래프 239 records, 1324 edges, warnings 0. V0.7 review 0; typed input 미검증 0. V0.8 결과 JSON에 실제 대상 blob과 시험별 판정 기록. 전체 상태의 의미론/교착/동시성/외부 동작은 증명하지 않았다. MVP-GATE-01 실제 결과 incomplete(product_execution not_run). 정적 검사 성공을 제품 성공으로 승격하지 않는다.

재현 명령:
- node docs/artifacts/design/lesson-registration-20261124/run-constraints-v0.7.mjs
- node docs/artifacts/design/lesson-registration-20261124/run-closure-v0.8.mjs
- 기존 selective trace/contract 검증 실행 경로 유지.

## 단계 판정
- 설계 정합성: 보완된 명시 계약 기준 통과. 구현 준비 기준선 후보로 적합.
- W01(11/25~27): 공통 타입/fixture/실행 명령·stub 및 실제 개발 가용성 동결, 원격 합성 PoC 독립 확인. 현재 동결/제품 구현 완료는 아님.
- 12/8 mock MVP, 1/4 최종 목표 유지. 실제 등록/외부 플랫폼 허용/운영 보안은 후속 단계 승인 필요.
- 현재 사용자에게 요청할 새 개별 설계 결정 없음. 실증 실패 또는 기존 목표/범위 변경 필요 시에만 결정 요청.
