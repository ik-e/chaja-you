# 통합 구조·작업 공간·책임 후보

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## common-integration-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · blob `9df34e576f8a7c63c7ee84d01893a77631ce0360`

### integration

- **ID** (`id`): INTEGRATION
- **layout** (`layout`): contracts/ common schema/profile/test fixtures and typed examples (R01 baseline) · app/ CO/HTTP/store/result · preparation/ PREP · remote/ EXEC auth/runtime/viewer gateway · platforms/ registered profile/adapters · web/ UI · tests/ contract and integrated tests
- **root&#95;proposal** (`root_proposal`): product/lesson-registration/ (logical proposal, no actual file creation or root dependency changes)
- **dependencies** (`dependencies`)
  - UI · CO
  - UI · VIEWER
  - CO · KNOW
  - CO · PREP
  - CO · EXEC
  - CO · RESULT
  - CO · STORE
  - PREP · KNOW
  - EXEC · KNOW
  - EXEC · RUNTIME
  - VIEWER · RUNTIME
  - RUNTIME · KNOW
  - RUNTIME · STORE
- **calls** (`calls`)
  - **[0] I1**
    - **ID** (`id`): I1
    - **consumer** (`consumer`): CO
    - **provider** (`provider`): KNOW
  - **[1] I2**
    - **ID** (`id`): I2
    - **consumer** (`consumer`): CO
    - **provider** (`provider`): PREP
  - **[2] I3**
    - **ID** (`id`): I3
    - **consumer** (`consumer`): CO
    - **provider** (`provider`): EXEC
  - **[3] I4**
    - **ID** (`id`): I4
    - **consumer** (`consumer`): CO
    - **provider** (`provider`): EXEC
  - **[4] I5**
    - **ID** (`id`): I5
    - **consumer** (`consumer`): CO
    - **provider** (`provider`): RESULT
  - **[5] HTTP**
    - **ID** (`id`): HTTP
    - **consumer** (`consumer`): UI
    - **provider** (`provider`): CO
  - **[6] VIEWER**
    - **ID** (`id`): VIEWER
    - **consumer** (`consumer`): UI
    - **provider** (`provider`): VIEWER
  - **[7] AUTH-RUNTIME**
    - **ID** (`id`): AUTH-RUNTIME
    - **consumer** (`consumer`): EXEC
    - **provider** (`provider`): RUNTIME
  - **[8] VIEWER-RUNTIME**
    - **ID** (`id`): VIEWER-RUNTIME
    - **consumer** (`consumer`): VIEWER
    - **provider** (`provider`): RUNTIME
  - **[9] ATOMIC**
    - **ID** (`id`): ATOMIC
    - **consumer** (`consumer`): RUNTIME
    - **provider** (`provider`): STORE
- **node&#95;note** (`node_note`): Provider graph = logical use dependencies, not imports/processes. Platform adapters inside EXEC and registry rules inside KNOW; runtime-provided gateway scopes operations; STORE has no callback to CO/EXEC. RESULT receives immutable input and no state/driver access.
- **handoff** (`handoff`): freeze schema/ports/API examples and mock-only guard · per-boundary fake provider and typed examples; each module tests against fake others · shared run command and real adapter/runtime conformance after shared stack selection · first integrated Kmong path then Soomgo extension; regress failures and unknown; use same build+contract+fixture identities
- **pending** (`pending`): 11/27 R01 independent R03/R04/R05 evidence review: common language/framework/DB/runtime transport/actual paths and commands, dependency lock, shared fixture/adapter manifest, minimal product skeleton smoke, single owners and WBS actual effort · runtime operation registry exact action definitions, stable target resolution and physical atomic tests · actual platform permission/goal/fields remain separate live gate
- **work&#95;packages&#95;proposed** (`work_packages_proposed`)
  - R01 · common contract/trace/acceptance + integration decision · W01 W07 W09 · confirmed contract/stub and end-to-end evidence
  - R02 · source truth/AI preparation + fixture handoff · W02 W19 · PREP I2, fixture/questions exact; capability/availability confirm before assigning AI implementation, 12/4 handoff
  - R03 · common server, registry, store/result, harness · W03 W10 · I1 I5 HTTP/storage/gate; scope and effort after independent evidence
  - R04 · web UI + Soomgo adapter · W05 W08 · UI/H6 viewer and profile conformance; sequence by workload
  - R05 · remote runtime &amp; Kmong independent adapter reuse · W04 W06 · I3 I4 gateway; final Kmong owner R01/R05 based on workload/results, one owner before product task
- **task&#95;status** (`task_status`): proposal only, no assignment; existing independent tasks remain and 11/27 gate unchanged

### closure

- **logical&#95;contract** (`logical_contract`): decided&#95;with&#95;explicit&#95;deltas
- **상태** (`status`): design&#95;candidate&#95;ready&#95;for&#95;static&#95;review
- **pending** (`pending`): shared stack/workspace/skeleton/launch command and actual adapter registry decisions after independent evidence · real product integrated tests 22 not run; standards JSON Schema engine, digest implementation, real model, permission/DB concurrency and remote isolation not proven · prior R03/R04/R05 independent tasks unchanged, no new WBS assignment · live only separate R01 phase and permission evidence
- **no&#95;claim** (`no_claim`): No runtime product completion, no live support claim. No new general design framework.

