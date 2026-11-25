# R03 runtime 연결 결정 · 2026-11-25

TASK-050/REQ-05·08·10: 승인 범위·실행 권한 연결. 기준 main 094e4d2,
R03 4a240ee, R05 remote a7af111/kmong a3718a9. 공통 Protocol 변경 없음.

## 주입 예제

```python
from lesson_registration.app.runtime_support import RuntimeSupport
support = RuntimeSupport(store, knowledge)
# RemoteRuntime(..., slot_resolver=support.slot_resolver)
slot = support.slot_resolver(registration_id, owner_ref, profile_id)
raw = support.read_approved_asset(worker_context, asset_id)
```

slot = 'slot-' + canonical SHA256({kind: source-slot.v1, owner, root_source_id,
platform, object_kind}). owner를 확인하며 previous_source_id를 따라 최초 Source까지
조회한다. 새 버전/등록은 같은 slot, 독립 Source는 별개다. R05가 인증 target을
만들 때 호출하므로 기존 Scope.target.slot_ref에 들어가며 승인 뒤 바꾸지 않는다.

reader는 매 호출 active job·현재 lease·등록 owner·승인 목록/권리·digest·크기를
검증한다. fenced/terminal이면 거부한다. caller는 scope.assets 순서로 읽는다.
R05 a3718a9의 approved_reader_for_scope(accepted)는 context 인자가 없으므로
내부 make_context 연결에 store_context를 전달하여 다음 reader를 주입해야 한다.

```python
read = lambda asset_id: support.read_approved_asset(store_context, asset_id)
```

accepted만으로 DB에서 현재 lease를 찾아 권한을 만들어 주는 우회는 제공하지 않는다.

## Viewer

```python
from lesson_registration.app.http.viewer_composition import create_viewer_app
from lesson_registration.remote.transport import viewer_router
app = create_viewer_app(coordinator, runtime, viewer_router,
    service_origin='http://127.0.0.1:8011', mock_owner='demo-a')
```

UI/API/WS는 동일 origin 또는 개발 proxy로 묶는다. UI는 Origin을 포함한
same-origin POST /_mock/session 호출 후 HttpOnly/SameSite=Strict cookie를 사용한다.
owner는 서버 설정값이며 client body/query/header로 선택하지 않는다. HTTP와 WS는
같은 세션을 확인한다. TTL 1800초/최대 128개는 로컬 기본값. 재시작 시 폐기한다.
운영 인증이 아니다. R05 grant/입력 barrier 시험을 이 조립부 시험으로 대체하지 않는다.
기존 mock_server는 synthetic HTTP 리허설용이며 이 factory로 자동 변경되지 않는다.

## Digest와 Permit

StoreGateway(..., binding_version='binding.v1')는 전체 Scope digest와 단계 manifest를
묶는다. 공통 reference binding.v1과 동일하며 logical_operation_id/action_key=step_id,
operation_id=registration_id:step_id. R05 adapter가 아직 legacy 식이므로 default는
legacy 유지. 양쪽을 같은 버전으로 동시에 조립해야 한다. 자동 fallback/혼용 없음.
공유 helper/golden vector 반영은 R01 반환 대상이다.

R05는 consume을 별도로 호출하지 않고 다음 dispatch wrapper를 사용한다.

```python
permit = store.admit(ctx.store_ctx, operation)
outcome = store.dispatch(ctx.store_ctx, permit, operation,
    lambda: driver.perform(ctx.driver_ctx, operation))
# 반환된 observation/evidence는 기존 record_observation 경로로 기록한다.
```

dispatch 내부에서 등록별 잠금 → consume DB commit → 동기 callback 완료 → 잠금 해제.
SQLite 트랜잭션은 callback 전에 닫힌다. Gateway fence, Coordinator fence/finalize 및
이를 경유하는 recover가 같은 잠금을 쓴다. DB 절대 경로와 registration_id가 키이므로
별도 Store/Gateway 인스턴스도 같은 잠금을 사용한다. 대기자가 없어지면 잠금 항목을 제거한다.

fence가 먼저 commit하면 callback은 0회. dispatch가 잠금을 먼저 획득하면 그 작업 완료까지
fence가 대기하며 그 뒤 새 dispatch는 거부한다. 따라서 요청 도착과 fence 완료 시점은 다르다.
이미 진행 중인 네트워크 요청을 취소했다고 주장하지 않는다. callback 오류는 잠금 안에서
fence하여 reserved 효과를 unknown으로 보존하고 재실행하지 않는다.

consume만 단독 호출하면 dispatch 간격 보호가 없다. callback은 브라우저 작업을 큐에
넣고 반환하거나 awaitable을 반환하면 안 되며 실제 동기 I/O가 끝나야 한다. 다른 스레드가
fence 완료를 기다리게 한 뒤 callback에서 그 스레드를 join하는 것도 금지(교착).
R05의 제한된 I/O timeout이 필요하며 멈춘 callback을 강제로 종료하지 않는다.
현행 DB당 single-app-process 범위의 잠금이다. 다른 프로세스/DB 직접 변경을 보호하지 않는다.
R05 runtime이 wrapper를 적용한 실제 브라우저 경쟁 시험 전에는 제품 D02 완료가 아니다.

종료 후 읽기 허가 callback은 기본 미주입(거부) 유지. 별도 허가 및 admission-linked
관측 저장 경계가 확인되기 전 terminal 관측 권한을 확장하지 않는다.

## 검증 범위

test_runtime_support: 실제 SQLite 계보, owner/profile 거부, 이미지/lease/fence/변조,
Permit 재사용/operation 변조/fence 거부, 빈 binding 단계의 전체 승인값 변조.
test_viewer_composition: cookie 기반 HTTP/WS owner, 무세션/타 origin 거부.
R05 실제 router/browser, R04 UI 버튼/H6, 실제 dispatch 경쟁과 22 gate는 후속 통합 대상.

test_dispatch_gate: fence 먼저 callback 0회, consume 직후 경쟁 fence 대기, callback 중
별도 SQLite 쓰기 성공, callback 오류 unknown 보존, 새 Gateway에서도 Permit 재사용 차단.
R05 c3fa0b1의 307/308 회귀는 원격 브랜치 검증 보고이며 여기서 재실행하지 않았다.
통합 시 접수 전 0건/접수 후 1건·후속 POST 0·unknown 보존을 검증한다.
