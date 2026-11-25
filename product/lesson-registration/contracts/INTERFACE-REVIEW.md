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
