# 레슨 등록 지원 서비스 · 현행 설계 기준

> 기존 정본에서 생성한 현재 적용 인덱스. 별도 설계 정본·승인·업무 배정이 아니다.

[AI용 현행 인덱스](CURRENT-DESIGN.json) · [운영 상태](../../../CURRENT.md) · [채택 전 고정 검토 스냅샷](README.md) · [전체 이력](12-HISTORY.md)

## 1. 현행 적용 우선순위

- [PHASE-20261125-01](../../human/phase-intents/PHASE-20261125-01.md) · [논리 설계 채택](../../artifacts/design/lesson-registration-20261124/adoption-20261125.json) · [IB-01~05 승인](../../human/responses/HRESP-20261125-02_common-implementation-binding.md)
- 고정 논리 기준선 `197987047ea9a305072bba3fdff816c5c37b0157`: 원본 98개, 기존 결정 88개 보존. IB 결정 5개는 그 후속 구현 방향이다.
- 실행 후 사용자 중단/변경/재개/rollback 없음; 오류 시에만 중단 후 결과 반환. 이전 재개/취소/rollback 조항보다 우선.
- 현재 mock-only. 실제 서비스 허용, 제품 성공, 팀원 수신·착수, 물리 스택/일정 확정을 추정하지 않는다.

## 2. 설계 계층

| 계층 | 현행 상태 | 정본 | 읽기 뷰 / 주의 |
| --- | --- | --- | --- |
| 상위 의도·목표 | 현재 적용 | [INTENT.md](../../human/INTENT.md) · [PHASE-20261125-01.md](../../human/phase-intents/PHASE-20261125-01.md) · [direction-v0.4.json](../../artifacts/design/lesson-registration-20261124/direction-v0.4.json) · [top-design-v1.json](../../artifacts/design/lesson-registration-20261124/top-design-v1.json) · [top-design-amendment-v1.json](../../artifacts/design/lesson-registration-20261124/top-design-amendment-v1.json) | [01-GOALS.md](01-GOALS.md) — 현재 Phase 우선, A2 오류 전용 중단·mock-only |
| 제품 요구사항 | 명시 보존 | [implementation-v0.4.json](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements` · [trace-index-v0.9.json](../../artifacts/design/lesson-registration-20261124/trace-index-v0.9.json) `/requirements` | [01-GOALS.md](01-GOALS.md) — REQ-08 재개 문구는 A2 및 CS-05/06으로 대체. 구 컴포넌트/물리 설계는 이력 |
| 논리·상태·업무 경계 | 채택 | [detail-decisions-v2.json](../../artifacts/design/lesson-registration-20261124/detail-decisions-v2.json) · [logical-behavior-v5.json](../../artifacts/design/lesson-registration-20261124/logical-behavior-v5.json) · [common-integration-v1.json](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [adoption-20261125.json](../../artifacts/design/lesson-registration-20261124/adoption-20261125.json) | [02-LOGIC.md](02-LOGIC.md) · [06-API-PORTS.md](06-API-PORTS.md) · [07-EXECUTION.md](07-EXECUTION.md) — CS-01~09 원본 당시 상태 유지, 현행 채택은 승인 기록 |
| 데이터·프로필 | 동결/채택·mock | [logical-data-contract-decision-v1.json](../../artifacts/design/lesson-registration-20261124/logical-data-contract-decision-v1.json) · [data-contract-v4.json](../../artifacts/design/lesson-registration-20261124/data-contract-v4.json) · [data-schema-v4.1.json](../../artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · [platform-profiles-v2.json](../../artifacts/design/lesson-registration-20261124/platform-profiles-v2.json) | [03-DATA.md](03-DATA.md) · [04-SCHEMA.md](04-SCHEMA.md) · [05-PLATFORMS.md](05-PLATFORMS.md) — V4.1 명시 델타·공통 V1 우선. 실제 운영사 규칙 미검증 |
| 공통 구현 계약 | 방향 승인·초기 공유 | [IMPLEMENTATION-BINDING.json](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) · [HRESP-20261125-02_common-implementation-binding.md](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · [interfaces.py](../../../product/lesson-registration/contracts/interfaces.py) · [validation.py](../../../product/lesson-registration/contracts/validation.py) · [viewer.d.ts](../../../product/lesson-registration/contracts/viewer.d.ts) · [wiring.py](../../../product/lesson-registration/src/lesson_registration/composition/wiring.py) | [README.md](../../../product/lesson-registration/contracts/README.md) — IB-01~05, 세부 provider/제품 스택 미확정 |
| 공통 물리 설계·실행환경 | PD-01~08 방향 채택·세부 검증 | [PHYSICAL-BINDING.json](../../../product/lesson-registration/contracts/PHYSICAL-BINDING.json) · [HRESP-20261125-03_common-physical-direction.md](../../../docs/human/responses/HRESP-20261125-03_common-physical-direction.md) · [WORKSPACE.json](../../../product/lesson-registration/WORKSPACE.json) · [pyproject.toml](../../../product/lesson-registration/pyproject.toml) · [uv.lock](../../../product/lesson-registration/uv.lock) · [bootstrap-ci-20261125.json](../../../product/lesson-registration/evidence/bootstrap-ci-20261125.json) · [pyproject.toml](../../../product/lesson-registration/evidence/physical-env/pyproject.toml) · [lesson-physical-probe.yml](../../../.github/workflows/lesson-physical-probe.yml) | [README.md](../../../product/lesson-registration/README.md) · [PLAN.md](../../../product/lesson-registration/evidence/PLAN.md) — 정확한 lock 및 기술 시험은 PD 정본의 environment 상태로 판정; 제품 보안/동작은 별도 |
| 담당별 상세 설계·작업 | TASK 배정 | [current.json](../../artifacts/state/current.json) · [WORKSPACE.json](../../../product/lesson-registration/WORKSPACE.json) · [TASK-048.json](../../artifacts/tasks/TASK-048.json) · [TASK-049.json](../../artifacts/tasks/TASK-049.json) · [TASK-050.json](../../artifacts/tasks/TASK-050.json) · [TASK-051.json](../../artifacts/tasks/TASK-051.json) · [TASK-052.json](../../artifacts/tasks/TASK-052.json) · [TASK-053.json](../../artifacts/tasks/TASK-053.json) · [TASK-054.json](../../artifacts/tasks/TASK-054.json) | [CURRENT.md](../../../CURRENT.md) · [WORK-PACKAGES.md](../../../product/lesson-registration/WORK-PACKAGES.md) — 담당자 PLAN/수신/착수 및 일정 별도 확인 |
| 검증·수용 시험 | 설계/합성 검증 | [common-integration-v1.json](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/gate` · [common-integration-validation-v1.json](../../artifacts/design/lesson-registration-20261124/common-integration-validation-v1.json) · [common-contract-ci-20261125.json](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json) · [TASK-048.json](../../artifacts/tasks/TASK-048.json) | [09-TESTS.md](09-TESTS.md) · [README.md](../../review/README.md) — 제품 22개 시험 실제 결과는 TASK/고정 실행 근거로 판정 |
| 현행 WBS 후보 | 미확정 | [wbs-v0.6-candidate.json](../../../docs/artifacts/planning/lesson-registration-20261123/wbs-v0.6-candidate.json) | [PLAN.md](../../../product/lesson-registration/evidence/PLAN.md) — R05 7근무일 추정·R02 12/4 인계; 전체 owner PLAN 후 확정 |
| 과거 설계·WBS | 이력/선별 참조 | [MANIFEST.json](MANIFEST.json) · [trace-index-v0.9.json](../../artifacts/design/lesson-registration-20261124/trace-index-v0.9.json) · [wbs-v0.5.json](../../artifacts/design/lesson-registration-20261124/wbs-v0.5.json) | [10-DECISIONS.md](10-DECISIONS.md) · [11-WBS.md](11-WBS.md) · [12-HISTORY.md](12-HISTORY.md) · [TARGET-DESIGN.md](../TARGET-DESIGN.md) — 고정 98개 원본·88개 추적 보존, 이전 찾아you 및 WBS는 현행 배정 아님 |

## 3. 요구사항 추적

원본 보존. TASK 연결은 공통 논리 결정을 통한 탐색 관계이며 직접 배정 또는 충족 여부가 아니다. 정확한 배정 요구사항은 각 TASK 원본을 확인한다.

| 요구사항 | 논리 결정 | 관련 TASK | 계획 시험 |
| --- | --- | --- | --- |
| [REQ-01](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/0` 원본·필수 정보·자료 준비 | CS-02, CS-03, CS-07, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) | AT-01, T5-08, T5-11, T6-01, T5-06 |
| [REQ-02](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/1` 등록 대상 식별 | CS-01, CS-02, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | T5-07 |
| [REQ-03](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/2` 플랫폼별 변환·검토 | CS-01, CS-02, CS-03, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | AT-01, T5-08, T5-11, T6-02, T5-03, T5-07, DV-04 |
| [REQ-04](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/3` 원격 직접 인증·제어권 인계 | CS-03, CS-04, CS-07, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) | AT-02, T5-02, T5-03, DV-02, DV-05 |
| [REQ-05](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/4` 실행 대상·승인·권한 | CS-02, CS-03, CS-04, CS-05, CS-07, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | T6-02, AT-03, T5-01, T5-02, T5-12, T5-07, DV-01, DV-02, DV-04 |
| [REQ-06](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/5` 크몽 최초 등록 | CS-01, CS-06, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | AT-04, T5-06, T5-13, DV-03 |
| [REQ-07](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/6` 숨고 최초 등록 확장 | CS-01, CS-06, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | AT-05, T5-06, T5-13, DV-03 |
| [REQ-08](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/7` 결과·부분 효과·실패 (재개 조항 대체) | CS-02, CS-03, CS-05, CS-06, CS-07, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | AT-04, AT-05, T5-05, DV-01, DV-03, DV-05 |
| [REQ-09](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/8` 플랫폼 확장 | CS-01, CS-07, CS-08, CS-09 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | T5-03, AT-05, T5-06, T5-13, DV-04 |
| [REQ-10](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/9` 격리·개인정보·안전한 운영 | CS-04, CS-05, CS-06, CS-07, CS-08 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) | T6-01, AT-02, AT-03, T5-12, T5-05, DV-01, DV-02, DV-03, DV-05 |
| [REQ-11](../../artifacts/design/lesson-registration-20261124/implementation-v0.4.json) `/requirements/10` 재현성과 서비스 가치 | CS-07, CS-08, CS-09 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) | T5-08, T5-03 |

## 4. 결정 추적

과거 CS 원본 상태는 보존하고 채택 기록으로 현행 적용을 판정한다. IB 영향 관계는 기존 계약 탐색용이며 신규 업무·수용 기준·검증 승격이 아니다.

| 논리 결정 | 현행 적용 | 선행 결정 | 관련 IB | 관련 TASK |
| --- | --- | --- | --- | --- |
| [CS-01](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/0` | 채택 | D1, LD-01, LD-04, DC2 | IB-01 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) |
| [CS-02](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/1` | 채택 | D2, D3, D6, D7, LD-02, LD-05, DC1, DC7 | IB-02 | [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) |
| [CS-03](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/2` | 채택 | D2, D3, C03, LD-06, DC7 | — | [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) |
| [CS-04](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/3` | 채택 | DIR-01, DIR-02, A4, D3, LD-06, DC5 | IB-03, IB-04 | [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) |
| [CS-05](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/4` | 채택 | A2, A3, D3, D5, LD-06, DC5, C04, C05 | IB-03 | [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) |
| [CS-06](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/5` | 채택 | A2, D4, D5, LD-07, DC6 | IB-03 | [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) |
| [CS-07](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/6` | 채택 | DIR-02, D8, LD-08, C06, DC8, B4-02, R5-10 | IB-01, IB-04, IB-05 | [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) |
| [CS-08](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/7` | 채택 | A2, A4, LD-08, DC8, D8, R5-09, R5-11 | IB-02, IB-05 | [TASK-048](../../artifacts/tasks/TASK-048.json) |
| [CS-09](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/decisions/8` | 채택 | D8, LD-08, DC8 | — | [TASK-048](../../artifacts/tasks/TASK-048.json) |

### IB-01 · 공통 호출 규약

**선택:** Python 3.12 Protocol + JSON object at in-process service boundary; provider bridges may use async or other internal transport; I4 only called by accepted worker

**근거:** Current isolated Python bootstrap passed, common types are JSON and physical separation not required. Minimal provider contracts avoid mandatory framework or distributed infrastructure.

**대안:** Separate microservice/RPC for each provider / Async-only port signatures / Framework model types as shared canonical schema

- [결정 원본](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) `/decisions/0` · [승인 근거](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · 선행: CS-01, CS-07, LD-03
- 영향 검토: [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) · 관련 계획 제품 시험: T5-03
- 확인된 근거: `test_port_wiring_and_missing_unknown`, `test_provider_error_and_invalid_output` · [검증 기록](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json)
- 검증 한계: 실제 provider timeout/동시성/worker·IPC 미검증
- 남은 검토: R02/R03/R05 confirm concrete provider signatures/transport; change only by shared review.
- 재검토 조건: Provider requires process isolation, streaming or latency constraints.

### IB-02 · 공통 스키마 검사

**선택:** Use pinned named Draft 2020-12 schema with explicit profile schema; jsonschema 4.25.1 isolated verification tool; no second type schema

**근거:** Standards-based validation avoids drift and tests all current shapes; production dependency/lock still separate.

**대안:** Custom schema checker / Pydantic as new source / Pre-generate model classes

- [결정 원본](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) `/decisions/1` · [승인 근거](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · 선행: CS-02, CS-08, LD-08
- 영향 검토: [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) · 관련 계획 제품 시험: T5-03, T5-13, DV-04
- 확인된 근거: `test_all_named_replay_shapes`, `test_http_named_shapes`, `test_platform_specific_values`, `test_datetime_and_digest_negative` · [검증 기록](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json)
- 검증 한계: 선정 합성 payload 검사. 프런트에 Python 엔진 강제 아님; 전체 제품 dependency lock 미확정
- 남은 검토: Standard validator direction accepted; product dependency group and full lock pending R03/shared review.
- 재검토 조건: Missing schema constraints, incompatible profile or performance need.

### IB-03 · Storage·Runtime·Adapter 권한 경계

**선택:** Split store coordinator/gateway capabilities; runtime owns opaque context/permit; adapter gets bound gateway only; no actual permit stub

**근거:** Retain logical owner/atomicity and deny bypass; actual registry/lease implementation remains provider responsibility.

**대안:** Expose raw driver to adapter / Shared unrestricted storage object

- [결정 원본](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) `/decisions/2` · [승인 근거](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · 선행: CS-04, CS-05, CS-06
- 영향 검토: [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) · 관련 계획 제품 시험: AT-03, T5-12, DV-01, DV-02, DV-04
- 확인된 근거: `test_input_guards_before_provider`, `test_mismatched_auth_generation_rejected` · [검증 기록](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json)
- 검증 한계: 입력 및 인증 관계 일부만 검증. 실제 원자성·permit·lease·권한 검증 아님
- 남은 검토: R03/R05 confirm storage transaction signatures, fence/finalize return, adapter registry and operation binding.
- 재검토 조건: Real implementation cannot enforce atomic guard or adapter needs additional typed operation.

### IB-04 · 프레임워크 독립 Viewer

**선택:** Framework-neutral viewer mount/dispose with AuthGrant and event callback; transport/client package remains open

**근거:** UI can design independent of remote stack, grant and detach semantics retained.

**대안:** Direct remote URL or browser control from UI / Choose framework-specific viewer now

- [결정 원본](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) `/decisions/3` · [승인 근거](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · 선행: CS-04, CS-07
- 영향 검토: [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · 관련 계획 제품 시험: AT-02, T5-02, DV-05
- 확인된 근거: 런타임 시험 없음 · [검증 기록](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json)
- 검증 한계: 타입 선언만. transport·브라우저·grant 보안 미검증
- 남은 검토: R04/R05 jointly decide transport and owner/generation/origin binding.
- 재검토 조건: Viewer PoC demonstrates unsupported lifecycle/transport.

### IB-05 · 명시적 provider 조립

**선택:** Explicit provider injection and exact synthetic replay; no automatic replay fallback in product, no fake workflow

**근거:** Validate edges early while avoiding competing CO implementation. Actual stateful flow needs R03 app and genuine providers.

**대안:** Build replacement full mock app / Wait for all implementations

- [결정 원본](../../../product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json) `/decisions/4` · [승인 근거](../../human/responses/HRESP-20261125-02_common-implementation-binding.md) · 선행: CS-07, CS-08
- 영향 검토: [TASK-048](../../artifacts/tasks/TASK-048.json) · [TASK-049](../../artifacts/tasks/TASK-049.json) · [TASK-050](../../artifacts/tasks/TASK-050.json) · [TASK-051](../../artifacts/tasks/TASK-051.json) · [TASK-052](../../artifacts/tasks/TASK-052.json) · [TASK-053](../../artifacts/tasks/TASK-053.json) · [TASK-054](../../artifacts/tasks/TASK-054.json) · 관련 계획 제품 시험: T5-03
- 확인된 근거: `test_port_wiring_and_missing_unknown`, `test_separate_instances_and_no_implicit_provider` · [검증 기록](../../../product/lesson-registration/evidence/common-contract-ci-20261125.json)
- 검증 한계: 합성 주입/독립성만. 실제 CO·모듈 연결 및 launch 미검증
- 남은 검토: Owner factory signatures, shared launch configuration and module-level testing strategy before actual assembly.
- 재검토 조건: First real provider ready.

### PD-01~08 · 공통 물리 방향

[PHYSICAL-BINDING.json](../../../product/lesson-registration/contracts/PHYSICAL-BINDING.json) · [HRESP-20261125-03_common-physical-direction.md](../../../docs/human/responses/HRESP-20261125-03_common-physical-direction.md) · [wbs-v0.6-candidate.json](../../../docs/artifacts/planning/lesson-registration-20261123/wbs-v0.6-candidate.json)

| ID | 채택 방향 | 담당자 확인 |
| --- | --- | --- |
| PD-01 시스템 구조 | 모듈형 모놀리스 + 격리 browser runtime; 프로세스 분리 필요성은 근거 후 판단 | R03/R05: lifecycle, shutdown, process isolation 조건 |
| PD-02 실행 기술 | Python 3.12, FastAPI/ASGI, SQLite, Playwright/Chromium; UI/AI 내부 기술은 owner 제안 | R01/R03/R05: product regression and owner OS/local install confirmation; R02/R04 additional needs |
| PD-03 공통 데이터 | 기존 named JSON Schema/profile; 서버 권위 UTF-8 sorted-key JSON·safe integer·Unicode 보존·SHA256, 배열 순서·asset raw bytes; 기존 data contract 범위 | R02/R03/R04/R05: supplied server byte helper/golden vectors; exact digest target scope, slot mapping, error/time/ID semantics |
| PD-04 Worker/저장 | CO 단일 상태 소유, accepted worker는 request/viewer와 수명 분리, SQLite 원자 accept/admit/observe/fence/finalize; runtime exclusive lease | R03/R05: transaction/timeout, permit/lease generation, crash/fence race |
| PD-05 모듈 호출 | 기존 Python Protocol/JSON 및 BoundGateway; runtime owns permit/context; adapter 등록 operation만; event loop에서 blocking 금지 | R03/R05 STORE 호출, R04/R05 operation manifest와 fake gateway, R02/R03 I2 timeout |
| PD-06 Viewer | CDP screencast + WebSocket 방향 수용; R05 viewer mount/dispose, R03 서버 경계, R04 UI 소비 | R03/R04/R05 endpoint/message schema, grant owner/generation/expiry/origin, input cutoff, disconnect detach, WSS 검증 |
| PD-07 Composition | 명시 provider 주입·설정·수명 관리, fake는 개발·검증에 명시 선택; 자동 replay fallback 없음 | 각 owner factory signature, config/launch, port, shutdown |
| PD-08 통합 검증 | 독립 기술 검사 → 공유 계약 → 실제 provider → 크몽/숨고 통합 → 22개 동일 후보 gate | R01: shared product-lock regression, owner PLAN and actual provider/product gate; R02 handoff 12/4 |

## 5. 현재 담당별 작업

| TASK | 담당 | 패키지 | 관련 IB | PLAN 작성 위치 |
| --- | --- | --- | --- | --- |
| [TASK-048](../../artifacts/tasks/TASK-048.json) | R01 | common | IB-01, IB-02, IB-03, IB-04, IB-05 | `product/lesson-registration/evidence/PLAN.md` |
| [TASK-049](../../artifacts/tasks/TASK-049.json) | R02 | r02-preparation | IB-01, IB-02, IB-05 | `product/lesson-registration/tests/modules/preparation/PLAN.md` |
| [TASK-050](../../artifacts/tasks/TASK-050.json) | R03 | r03-app | IB-01, IB-02, IB-03, IB-05 | `product/lesson-registration/tests/modules/app/PLAN.md` |
| [TASK-051](../../artifacts/tasks/TASK-051.json) | R04 | r04-web | IB-02, IB-04, IB-05 | `product/lesson-registration/tests/modules/web/PLAN.md` |
| [TASK-052](../../artifacts/tasks/TASK-052.json) | R04 | r04-soomgo | IB-01, IB-02, IB-03, IB-05 | `product/lesson-registration/tests/modules/soomgo/PLAN.md` |
| [TASK-053](../../artifacts/tasks/TASK-053.json) | R05 | r05-remote | IB-01, IB-02, IB-03, IB-04, IB-05 | `product/lesson-registration/tests/modules/remote/PLAN.md` |
| [TASK-054](../../artifacts/tasks/TASK-054.json) | R05 | r05-kmong | IB-01, IB-02, IB-03, IB-05 | `product/lesson-registration/tests/modules/kmong/PLAN.md` |

담당자별 PLAN은 작성 위치이며 존재·수신·착수·완료 여부를 주장하지 않는다. 이전 WBS는 [이력](11-WBS.md)으로만 사용한다.

## 6. 검증 및 남은 설계

- [공통 CI](https://github.com/ik-e/chaja-you/actions/runs/45527624382) · 계약 10개, 합성 포트 36개, HTTP 36개, 회귀 9개, 문서 27개. 고정 후보에 대한 검사다.
- 제품 gate 22개: [수용 기준](../../artifacts/design/lesson-registration-20261124/common-integration-v1.json) `/gate` · [실제 결과 원본](../../artifacts/tasks/TASK-048.json). 합성/제품 시험 구분, T5-08 실제 모델 필수.

- Owner-specific environment confirmation, remaining UI/AI dependencies and product provider transport/async choices
- R03/R05 STORE, R04/R05 gateway, R03/R04/R05 viewer, R02/R03 I2, each owner factory/config: contracts/INTERFACE-REVIEW.md
- Canonical helper and golden vectors supplied; actual scope/slot/profile readback mapping and provider integration require owner confirmation
- Other owner PLAN/availability and WBS confirmation; actual product tests not run

## 7. 갱신

```sh
node tools/generate_lesson_current_design.mjs
node tools/generate_lesson_current_design.mjs --check
```

기존 정본을 먼저 변경하고 생성기를 실행한다. 현재 Phase·TASK·승인·설계 ID·요구사항·시험 참조 및 경로/JSON Pointer를 확인한다. 고정 스냅샷은 기존 생성기로 관리하며 과거 원본을 수정하지 않는다.
