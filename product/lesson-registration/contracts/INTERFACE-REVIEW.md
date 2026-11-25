# 담당자 공통 경계 확인 · TASK-048

현행 [IB](IMPLEMENTATION-BINDING.json)·[PD](PHYSICAL-BINDING.json)·[공통 논리 원본](../../../docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json)이 기준이다. 아래는 **담당자 협의 항목 및 반환 기준**이며 추가 업무 배정/상태 전이/승인 또는 합의 완료가 아니다. 기존 `interfaces.py`, `viewer.d.ts`, pinned schema를 유지하고 fake로 독립 구현 가능하다. 차이가 필요한 때만 R01 공통 변경 검토로 올린다.

| 대상 | 협의 담당 | 이미 고정된 계약 | 반환할 세부 사항 |
| --- | --- | --- | --- |
| STORE (S-ACCEPT/ADMIT/OBSERVE/FENCE) | R03·R05 | CoordinatorStore/GatewayStore, CO 단일 상태 소유, durable admission 전 dispatch 금지, stable logical effect key, unknown 중복 차단 | 기존 Protocol 서명 유지 가능 여부, scoped context/permit 연동, transaction·timeout·fence 경쟁/응답 유실·관측 및 오류 예제, 별도 fake/실DB 시험 |
| Runtime Gateway (RT-01~04) | R05·R04, R03 registry | 동일 verified binding 및 exclusive lease, adapter에는 BoundGateway만, Operation schema의 ID/step/action/effect_class/binding_digest만, 승인된 immutable values로 인자 resolve | 크몽·숨고 manifest entry 예제, stable logical operation/slot 참조, registry 조회, 읽기/잠재 효과 구분 및 미등록/변조/중복 차단 시험; profile 별 규칙은 owner 경로 |
| Viewer | R03·R04·R05 | framework-neutral mount/dispose, CDP screencast+WS 방향, current AuthGrant, R05 viewer/R03 연결/R04 UI, dispose detach only | endpoint/message·frame/input/event 타입 및 상호 검증, grant owner/generation/expiry/origin, finish 후 입력 차단, stale/foreign/reconnect 시험, WSS 운영 경계. 원시 CDP/세션 비밀·URL/query/log grant 노출 금지 |
| I2 | R02·R03 | PrepareInput→Preparation, source facts/units 보존, blocking Issue 및 ready=false | 호출 동기 bridge·timeout, MODEL_UNAVAILABLE·누락/충돌 예제, 실제 모델 환경/의존성/인계 |
| Digest / slot | R03·R04·R05·R02(입력) | 기존 data-contract-v4 canonical, profile/scope/payload/asset 각각 정해진 대상, readback actual normalized values | [서버 byte helper](canonical.py) 및 [golden vectors](../fixtures/shared/canonical-vectors.json)로 일치 확인; profile digest self 제외, scope exact internal Scope, payload exact values, asset raw bytes/upload 순서. profile normalization 및 slot은 실제 담당자 합의 |
| Composition/launch | R01·각 담당 | explicit Providers injection; fake 명시 선택, implicit fallback 금지 | factory import/signature, config/timeout, worker/lifespan, mock launch 및 teardown, 추가 dependency 필요 여부 |

공통 byte helper는 JSON object를 정렬·직렬화하는 작은 primitive만 제공한다. compact separators, UTF-8 strict, Unicode codepoint key order(서버 Python), no normalization, 배열 순서 보존, safe integer, SHA-256; non-integer number/비JSON 타입 거절. 입력 객체는 선행 named/profile schema validation을 거쳐야 한다. duplicate raw JSON keys 검출, exact digest 대상/slot 결정 및 승인/증거 확인은 별도 provider 책임이다. replay fixture의 합성 digest를 실제 생성값으로 취급하지 않는다.

## 반환 및 변경 처리

- 각자의 기존 PLAN에 **공통 기준 SHA / 상대 담당자 / 유지 또는 변경이 필요한 서명·예제 / 이유 / 정상·실패·unknown 시험 / 남은 확인**만 기록한다. 공유 lock/계약 변경은 R01이 반영. 다른 담당의 코드를 수정할 필요 없다.
- 11/27은 공통 접점 협의의 잠정 목표이며 새 마감일이 아니다. 독립 구현은 가능한 부분부터 지속한다. R02 인계 12/4, R05 7일 추정 및 다른 공수는 [WBS 후보](../../../docs/artifacts/planning/lesson-registration-20261123/wbs-v0.6-candidate.json)에 연결.
- 실제 구현 및 담당자 확인 전에는 합의/제품 시험 통과로 표시하지 않는다. mock-only 유지. 실제 로그인·계정·비밀·등록 금지.

## R03 PLAN 검토 (2026-11-25)

근거: [R03 TASK-050 PLAN 고정 snapshot](https://github.com/ik-e/chaja-you/blob/e29fb6939f1ec49d9b4a89fbe2874bb6331498cf/product/lesson-registration/tests/modules/app/PLAN.md). FastAPI 및 SQLite/BEGIN IMMEDIATE 방향은 PD-02/04와 일치한다. 공통 pyproject/uv.lock의 app/verification 그룹으로 작업 가능. multipart 처리에서 추가 라이브러리가 필요하면 R03가 정확한 요구를 PLAN에 제시하고 공통 lock 변경은 R01이 검증한다. 아래는 새로운 설계 요구가 아니라 기존 채택 계약에 대한 정합성 피드백이다.

| PLAN 지점 | 확인 사항 |
| --- | --- |
| D5 효과 중복 차단 | `(registration, operation, approval_digest)`만으로는 새 등록 ID/승인 digest 변경 시 같은 외부 효과를 차단하지 못함. 기존 CS-05의 stable logical effect key: `(environment, platform, external_account_ref, object_kind, stable slot_ref, stable logical_operation_id)`를 효과 유일성 기준으로 사용. 요청 멱등 키/승인 digest는 별도 가드. 새 등록·다른 key·revision/worker 변경·unknown에 대한 실패 시험 추가. |
| §3.4 결과 | pinned GoalVerdict는 `confirmed / not_reached / unknown` (failed는 wire enum 아님). 확실한 미도달과 증거 부족을 구분. |
| §3.3 accept | H7은 현재 verified ConnectionBinding/target/profile/scope/permission 및 revision/review를 원자 확인. Viewer AuthGrant는 human 인증 연결용이며 승인/worker 권위가 아님. finish 이후 viewer 입력 차단 유지. |
| ports.py / STORE | shared `contracts/interfaces.py`를 사용. 로컬 bridge는 가능하나 별도 Protocol 정본 복제 금지. S-ACCEPT와 GatewayStore admit/record_observation/fence 및 coordinator finalize 서명·lease/permit은 R05와 대조. |
| 일정 | 11인일 추정 및 12/8 전 vertical/safety 우선 순서는 WBS 후보에 반영. H2/H9, T5-06/T6-01 등 필수 계약/시험을 삭제·연기 승인한 것은 아님. 22개 gate 미충족이면 MVP 미완료/부분 시연으로 보고하고 R01에게 일정/범위 조정 근거 반환. |

R03의 PLAN 원문과 담당 브랜치는 수정하지 않는다. R03은 위 사항을 자기 PLAN에 반영/이견 기록하고 관련 담당과 기존 계약을 맞춘다. 11인일/7근무일은 보고값이지 완료 또는 확정 일정이 아니다.

## R03 진행 보고 후속 (2026-11-25)

[고정 구현](https://github.com/ik-e/chaja-you/commit/e29fb6939f1ec49d9b4a89fbe2874bb6331498cf) · [보고/검토 근거](../evidence/r03-progress-20261125.json) · [R01 후속 결정](../../../docs/human/responses/HRESP-20261125-04_r03-app-followup.md). S0~S7 및 174/10/2 통과는 보고값이며 최신 기준 독립 재현 및 제품 gate 미확인. 이미 구현한 사항 유지, 남은 차이만 검토.

| 항목 | 적용/반환 기준 |
| --- | --- |
| S8 | main app/verification 그룹으로 HTTP 구현 착수. multipart 추가 dependency가 필요하면 버전·필요성·시험 제안. |
| Schema | 공통 SchemaCatalog/jsonschema 4.25.1 사용 기본. replay 일치만으로 동등성 주장 금지. 시간대 없는 timestamp, numeric edge, profile values/unknown field 및 오류 매핑 확인. |
| REQ-08 / finalize | 현행 CS-05/06 및 A2 우선, 과거 원본 보존. stopped 이후 읽기 근거 추가만, 재개/재실행 없음. 기존 CoordinatorStore.finalize 사용. |
| Digest/fixture | 공통 canonical helper·golden vectors 사용; actual normalized readback에서 payload digest 계산. binding의 step/registered operation/asset/target/profile·첨부 순서·slot 공동 예제 확정 후 R01이 계산값 기반 fixture 및 회귀 갱신. 기존 replay placeholder는 합성 전용. |
| STORE/lease | acquire_context/expected_operations는 기존 Protocol에 미채택. R05와 verified binding, lease 등록·폐기, permit, 등록 operation ID/action_key/effect_class/binding, 관측-admission/evidence 연결, stale/foreign lease, worker/fence 경쟁·응답 유실 예제 및 시험 확인. 종료 후 읽기 근거 추가에 임의 관측 주입 금지. |
| Viewer/I2/launch | R03·R04·R05 viewer endpoint/messages, finish 입력 차단, detach; R02·R03 I2 timeout/오류; owner factory/lifespan/worker/launch 확인. |
| WBS | TASK-050 유지. W10/W16/PREP 추가 배정 미확정; 초기 11인일 대비 잔여 공수·readiness 반환. 22개 gate 유지. |

합의·제품 회귀 전 세부 계약 채택 또는 제품 완료로 기록하지 않는다. R01은 공통 변경/fixture 담당이며 R03 브랜치와 구현 파일을 직접 수정하지 않는다.

## D01~D06 공통 세부 기준 후보

R01이 [구체안](DETAIL-CANDIDATE.json)과 [세션 보안](SESSION-SECURITY.md), [reference 시험](../tests/contract/test_detail_candidate.py)을 먼저 제시한다. 담당자는 전체 재설계 대신 기존 PLAN에 기준 SHA, 실제 구현과의 차이, 반례/시험, 필요한 서명 변경만 반환. R02 D05, R03 D01/02/03/05/06, R04 D01/03/04, R05 D01/02/03/04/06. R01 공통 변경·fixture/통합 담당. 실제 provider 서명, 플랫폼 정규화·slot, actual dispatch fence, WS/격리·폐기, 설정 수치 및 제품 gate는 미확정/미검증. 현재 합성 reference는 제품 구현 아님. 실제 계정 사용 금지.

## 11/25 R01 공동 개발 기준 전달

[공동 개발 기준선](CURRENT-BASELINE.md)을 먼저 적용. R04가 전달한 H8 Progress/H6 Viewer/Polling A안 중 이름 변경은 기존 schema 사용으로 교정, grant URL/log 노출 금지, polling 주기는 자율이며 조회 제한과 goal_verdict 분리. R01이 Discord에 전달했다고 확인. 상대 담당의 합의/실제 반영은 별도. D01~D06 검증 reference 기준으로 필요한 차이만 반환하며 기존 logical pin/Protocol/gate 변경 없음. R05는 이미 Playwright와 Chromium/WS 방향이 채택되어 별도 승인 불필요.

## R05 구현 보고 및 공통 접점 후속 (2026-11-25)

[R01 전달/처리](../../../docs/human/responses/HRESP-20261125-09_r05-progress-followup.md) · [고정 진행 근거](../evidence/r05-progress-20261125.json). remote 8e506e1 / kmong ae582bf; 담당자 보고 15/32, 잔여 합계 3~3.5근무일. R03의 현행 step digest와 정렬된 사실은 확인하되 D01~04 전체 정합성 승인으로 보지 않는다.

| 접점 | 확인된 구현 차이 | 기준 및 반환 |
| --- | --- | --- |
| D01 R03/R05/R04 | 현행 단계별 bound digest는 K6/S5 등 빈 binding에서 전체 승인값 변경을 직접 반영하지 않음 | 기존 logical Scope/manifest pin과 D01 binding.v1 reference 비교. R03/R05가 동일 scope/manifest/operation 벡터(빈 binding 포함)와 tampered 승인값/target/profile/asset 반례 반환. 별도 wire 변경 없이 구현 가능성 우선. R01은 최종 공유 helper·golden vector 반영, 독자식 혼용 금지. |
| D01 slot | 기본 slot_for(registration_id)로 새 등록 시 중복 방지 우회 | R03이 소유권 검증된 Source의 previous_source_id chain root와 플랫폼/object/계정에 대한 안정적 server slot을 제공하는 방향 우선 검토. 동일 계보 재등록/새 버전/새 request key에도 같은 slot; 별개 계보의 모호한 동일 대상은 신규 효과 차단. 내부 resolver 주입으로 AuthInput wire 변경 없이 가능한지 R03/R05 확인. 기존 slot 임의 변경·승인 범위 확대 금지. |
| D02 | admit 반환 Permit 무시, acquire_context/expected_operations 임시안, 실제 dispatch fence 경합 미증명 | CO durable claim, STORE one-shot reserve/consume 및 runtime fence/enqueue 직렬화. 발급 후 fence·중복 소비·timeout/late command·orphan 및 실제 mutation count 시험. expected_operations 없는 driver fallback 금지. R03/R05 실제 내부 서명 확인 후 공통 Protocol 변경 필요 시만 반환. |
| D03 | fence 후 observe_goal 직접 호출 및 target/evidence의 입력값 재사용 가능성 | 별도 허가된 read-only 경계, admission-linked actual observed target/asset/payload evidence; 미확인 target은 confirmed 불가. terminal 재개 금지. K6 직전 exact approved values 재확인; readback mismatch/absence/unknown 구별. |
| D04 | attach_viewer 동일 grant 재사용 가능, receive에서 enqueue 전 검사만 | atomic single-use attach + owner/registration/generation/expiry/origin, 단일 입력 권한; finish 시 큐 폐기/실행 시점 재검증 및 drain/barrier, 이후 입력 0건. 실제 WS 경계 검증. TTL 600/900은 담당자 후보, 확정 아님. |
| 첨부 및 page | 실제 runtime/adapter AssetSource 미연결 | R03이 승인 scope 내 asset ID/digest로만 bytes 제공하는 내부 제한 provider; R05 raw byte digest 재계산·순서 확인·권한 오류 처리, DB/전체 파일 경로/credential 노출 금지. ScopedPage는 runtime 제한 내부 helper이며 공통 BoundGateway 유지. R03/R05/R04 실제 호출 예제 후 공통 타입 변경 여부 검토. |
| Chromium 회귀 | 응답 유실 시 POST 재전송 관측, route.fetch(max_redirects=0,max_retries=0) 변경 | R01 고정 commit 독립 Chromium 시험으로 단일 접수·재dispatch 없음·unknown 유지 확인. redirect/retry 경로(307/308 등), context/service worker 및 actual dispatch 경합 추가 검증 필요; route fetch만으로 exactly-once 주장 금지. |

기존 논리 pin, 22 gate, 업무 분담 유지. 사용자 확인한 전달 이후 실제 담당 합의·수정·CI는 별도 기록한다. R01은 담당 브랜치/구현을 직접 수정하지 않는다.

## R02·R04 후속 통합 검토 (2026-11-25)

[팀 고정 근거](../evidence/team-checkpoint-20261125.json) · [R04 검토](../evidence/r04-progress-20261125.json). R02의 PR51/52 draft는 별도 리뷰, 실제 모델 가격 충돌 오류·실험 설계/비용/인계는 R02 책임 및 R01 검토. [R03 합성 API 실행기](../tests/modules/app/README.md)는 31fe0c5 main에 반영되어 실제 Viewer를 기다리지 않고 H1~H9 연동 가능(합성 provider). 실제 모델/Viewer/플랫폼은 별도.

| 접점 | 확인 사항 및 반환 기준 |
| --- | --- |
| D05 R02/R03 | 부모 /packages 삭제 후 leaf만 전달하면 이전 값 유실. PR51은 부모와 leaf 동시 입력에서 형제 보존. 실제 H5에서 부모/형제 보존 및 provenance, 현재 revision/CAS, 지원 불가 시 기존 상태 보존/거부; timeout/late 결과 적용 금지. 기존 계약 내 해결 우선, 실제 사례 시험. |
| R04 UI | 9개 CI는 Python API·마크업 검사. 실제 버튼 H1~H9 연결 및 revision/approve 상태 통제, H7 StartInput·H8 Progress/goal_verdict 적용. 고정 1.5초 간격을 지수 백오프로 주장 금지, 조회 timeout은 실제 결과 아님. 시안 예시 데이터와 실제 성공 표시 분리. |
| R04 Viewer | grant URL 금지, exact origin+source+generation 및 one-shot input 권한은 선택 사항 아님. H6 server verified 전 성공 표시 금지, detach와 cancel 구분. 기존 CURRENT-BASELINE/D04 유지. |
| R04 숨고 | S5 unknown을 confirmed로 기록하지 않음. 실제 저장 상태를 별도 조회하고 승인값/고정 HTML에서 성공 근거를 합성하지 않음. S4 exact approved values 비교, BoundGateway/permit, 공통 canonical, observed target와 I5 최종 판정, 잘못된 대상/유실/중복 회귀. |

담당자는 기존 TASK 및 소유 경로에서 수정/시험하며 R01은 공통 경계와 통합만 변경. 12/4 및 12/8 후보와 22개 gate 유지.
