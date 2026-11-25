# 전체 원본 및 설계 이력

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## 우선순위

- Current phase/permission and human top decisions first; A2 overrides legacy cancel/resume/rollback
- V4.1 schema delta and common-integration-v1 wire/ports/constraints current; V4 remaining data and profile V2 current; old contracts historical except explicitly retained requirements
- V0.6 trace historical; original status preserved; current status is projection, not actual product verification
- 운영 단계는 main PHASE-20261124-03 우선. 기존 TASK/권한 변경 없음.

과거 취소/재개/rollback 계약은 A2 이후 현행 기능이 아니다. 과거 stage replay는 해당 당시 계약으로만 해석한다. 아래 원본은 모두 고정 커밋에서 열 수 있다.

| 원본 | 적용 | 읽기 뷰 |
| --- | --- | --- |
| [common-integration-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) | current_or_explicitly_retained | [06-API-PORTS.md](06-API-PORTS.md) · [07-EXECUTION.md](07-EXECUTION.md) · [08-INTEGRATION.md](08-INTEGRATION.md) · [09-TESTS.md](09-TESTS.md) · [10-DECISIONS.md](10-DECISIONS.md) |
| [COMMON-INTEGRATION-V1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/COMMON-INTEGRATION-V1.md) | history_or_supporting | 원본 직접 조회 |
| [common-integration-validation-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-validation-v1.json) | bounded_evidence | [09-TESTS.md](09-TESTS.md) |
| [contract-v0.5.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/contract-v0.5.json) | history_or_supporting | 원본 직접 조회 |
| [CONTRACT-V0.5.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/CONTRACT-V0.5.md) | history_or_supporting | 원본 직접 조회 |
| [CONTRACTS-V0.3.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/CONTRACTS-V0.3.md) | history_or_supporting | 원본 직접 조회 |
| [core-contract-v0.3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/core-contract-v0.3.json) | history_or_supporting | 원본 직접 조회 |
| [data-api-v0.3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-api-v0.3.json) | history_or_supporting | 원본 직접 조회 |
| [DATA-API-V0.3.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DATA-API-V0.3.md) | history_or_supporting | 원본 직접 조회 |
| [data-contract-v4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-contract-v4.json) | current_or_explicitly_retained | [03-DATA.md](03-DATA.md) |
| [DATA-CONTRACT-V4.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DATA-CONTRACT-V4.md) | history_or_supporting | 원본 직접 조회 |
| [data-contract-validation-v4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-contract-validation-v4.json) | bounded_evidence | [09-TESTS.md](09-TESTS.md) |
| [data-schema-v4.1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) | current_or_explicitly_retained | [04-SCHEMA.md](04-SCHEMA.md) |
| [data-schema-v4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.json) | history_or_supporting | 원본 직접 조회 |
| [DECISION-TRACE-V0.9.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DECISION-TRACE-V0.9.md) | history_or_supporting | 원본 직접 조회 |
| [DESIGN-STATUS-V0.8.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DESIGN-STATUS-V0.8.md) | history_or_supporting | 원본 직접 조회 |
| [detail-contract-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-contract-v1.json) | history_or_supporting | 원본 직접 조회 |
| [detail-contract-v2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-contract-v2.json) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-DATA-V0.2.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-DATA-V0.2.md) | history_or_supporting | 원본 직접 조회 |
| [detail-decisions-v2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-decisions-v2.json) | current_or_explicitly_retained | [02-LOGIC.md](02-LOGIC.md) |
| [detail-design-v0.2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-design-v0.2.json) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-DESIGN-V1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-DESIGN-V1.md) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-DESIGN-V2.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-DESIGN-V2.md) | history_or_supporting | 원본 직접 조회 |
| [detail-gate-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-gate-v1.json) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-PLATFORM-FLOWS-V0.2.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-PLATFORM-FLOWS-V0.2.md) | history_or_supporting | 원본 직접 조회 |
| [detail-review-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-review-v1.json) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-SYSTEM-V0.2.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-SYSTEM-V0.2.md) | history_or_supporting | 원본 직접 조회 |
| [detail-validation-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/detail-validation-v1.json) | history_or_supporting | 원본 직접 조회 |
| [DETAIL-VERIFICATION-V0.2.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DETAIL-VERIFICATION-V0.2.md) | history_or_supporting | 원본 직접 조회 |
| [direction-v0.4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/direction-v0.4.json) | current_or_explicitly_retained | [01-GOALS.md](01-GOALS.md) |
| [DIRECTION-V0.4.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DIRECTION-V0.4.md) | history_or_supporting | 원본 직접 조회 |
| [domain-workflow-v0.1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/domain-workflow-v0.1.json) | history_or_supporting | 원본 직접 조회 |
| [DOMAIN-WORKFLOW-V0.1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/DOMAIN-WORKFLOW-V0.1.md) | history_or_supporting | 원본 직접 조회 |
| [implementation-v0.4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/implementation-v0.4.json) | requirements_retained_other_sections_historical | [01-GOALS.md](01-GOALS.md) |
| [IMPLEMENTATION-V0.4.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/IMPLEMENTATION-V0.4.md) | history_or_supporting | 원본 직접 조회 |
| [interface-contract-v3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/interface-contract-v3.json) | history_or_supporting | 원본 직접 조회 |
| [interface-review-evidence-v3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/interface-review-evidence-v3.json) | history_or_supporting | 원본 직접 조회 |
| [interface-schema-v3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/interface-schema-v3.json) | history_or_supporting | 원본 직접 조회 |
| [logical-behavior-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v1.json) | history_or_supporting | 원본 직접 조회 |
| [logical-behavior-v2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v2.json) | history_or_supporting | 원본 직접 조회 |
| [logical-behavior-v3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v3.json) | history_or_supporting | 원본 직접 조회 |
| [logical-behavior-v4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v4.json) | history_or_supporting | 원본 직접 조회 |
| [logical-behavior-v5.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-behavior-v5.json) | current_or_explicitly_retained | [02-LOGIC.md](02-LOGIC.md) |
| [logical-data-contract-decision-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-data-contract-decision-v1.json) | current_or_explicitly_retained | [03-DATA.md](03-DATA.md) |
| [LOGICAL-DESIGN-V3.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/LOGICAL-DESIGN-V3.md) | history_or_supporting | 원본 직접 조회 |
| [logical-validation-v2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-validation-v2.json) | history_or_supporting | 원본 직접 조회 |
| [logical-validation-v3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-validation-v3.json) | history_or_supporting | 원본 직접 조회 |
| [logical-validation-v5.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-validation-v5.json) | bounded_evidence | [09-TESTS.md](09-TESTS.md) |
| [physical-v0.4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/physical-v0.4.json) | history_or_supporting | 원본 직접 조회 |
| [PHYSICAL-V0.4.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/PHYSICAL-V0.4.md) | history_or_supporting | 원본 직접 조회 |
| [PLATFORM-INDEPENDENT-WORK.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/PLATFORM-INDEPENDENT-WORK.md) | history_or_supporting | 원본 직접 조회 |
| [platform-profiles-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/platform-profiles-v1.json) | history_or_supporting | 원본 직접 조회 |
| [platform-profiles-v2.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/platform-profiles-v2.json) | current_or_explicitly_retained | [05-PLATFORMS.md](05-PLATFORMS.md) |
| [README.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/README.md) | history_or_supporting | 원본 직접 조회 |
| [requirements-v0.1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/requirements-v0.1.json) | history_or_supporting | 원본 직접 조회 |
| [REQUIREMENTS-V0.1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/REQUIREMENTS-V0.1.md) | history_or_supporting | 원본 직접 조회 |
| [REVIEW-DECISIONS-V0.3.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/REVIEW-DECISIONS-V0.3.md) | history_or_supporting | 원본 직접 조회 |
| [review-v0.3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/review-v0.3.json) | history_or_supporting | 원본 직접 조회 |
| [run-closure-v0.8.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/run-closure-v0.8.mjs) | history_or_supporting | 원본 직접 조회 |
| [run-constraints-v0.7.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/run-constraints-v0.7.mjs) | history_or_supporting | 원본 직접 조회 |
| [scope-lock-validation-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/scope-lock-validation-v1.json) | history_or_supporting | 원본 직접 조회 |
| [stage-verification-adapter.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/stage-verification-adapter.mjs) | history_or_supporting | 원본 직접 조회 |
| [stage-verification-manifest.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/stage-verification-manifest.json) | history_or_supporting | 원본 직접 조회 |
| [stage-verification-replay.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/stage-verification-replay.json) | history_or_supporting | 원본 직접 조회 |
| [stop-validation-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/stop-validation-v1.json) | history_or_supporting | 원본 직접 조회 |
| [system-contracts-v0.1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/system-contracts-v0.1.json) | history_or_supporting | 원본 직접 조회 |
| [SYSTEM-CONTRACTS-V0.1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/SYSTEM-CONTRACTS-V0.1.md) | history_or_supporting | 원본 직접 조회 |
| [top-design-amendment-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/top-design-amendment-v1.json) | current_or_explicitly_retained | [01-GOALS.md](01-GOALS.md) |
| [top-design-v1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/top-design-v1.json) | current_or_explicitly_retained | [01-GOALS.md](01-GOALS.md) |
| [trace-index-v0.6.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/trace-index-v0.6.json) | history_or_supporting | 원본 직접 조회 |
| [trace-index-v0.9.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/trace-index-v0.9.json) | current_or_explicitly_retained | [10-DECISIONS.md](10-DECISIONS.md) |
| [validate-closure-v0.8.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-closure-v0.8.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-common-integration-v1.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-common-integration-v1.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-constraints-v0.7.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-constraints-v0.7.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-data-contract-v4.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-data-contract-v4.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-detail-v1.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-detail-v1.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-interface-review-v3.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-interface-review-v3.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-logical-v2.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-logical-v2.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-logical-v3.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-logical-v3.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-logical-v5.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-logical-v5.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-scope-lock-v1.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-scope-lock-v1.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-stop-v1.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-stop-v1.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-trace-v0.6.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-trace-v0.6.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-v0.3.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-v0.3.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-v0.4.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-v0.4.mjs) | history_or_supporting | 원본 직접 조회 |
| [validate-v0.5.mjs](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validate-v0.5.mjs) | history_or_supporting | 원본 직접 조회 |
| [validation-closure-v0.8.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validation-closure-v0.8.json) | history_or_supporting | 원본 직접 조회 |
| [validation-constraints-v0.7.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validation-constraints-v0.7.json) | history_or_supporting | 원본 직접 조회 |
| [validation-v0.3.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validation-v0.3.json) | history_or_supporting | 원본 직접 조회 |
| [validation-v0.4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validation-v0.4.json) | history_or_supporting | 원본 직접 조회 |
| [validation-v0.5.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/validation-v0.5.json) | history_or_supporting | 원본 직접 조회 |
| [verification-decisions-v0.1.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/verification-decisions-v0.1.json) | history_or_supporting | 원본 직접 조회 |
| [VERIFICATION-DECISIONS-V0.1.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/VERIFICATION-DECISIONS-V0.1.md) | history_or_supporting | 원본 직접 조회 |
| [VERIFICATION-REVIEW-V0.7.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/VERIFICATION-REVIEW-V0.7.md) | history_or_supporting | 원본 직접 조회 |
| [wbs-v0.4.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/wbs-v0.4.json) | history_or_supporting | 원본 직접 조회 |
| [WBS-V0.4.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/WBS-V0.4.md) | history_or_supporting | 원본 직접 조회 |
| [wbs-v0.5.json](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/wbs-v0.5.json) | historical_candidate | [11-WBS.md](11-WBS.md) |
| [WBS-V0.5.md](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/WBS-V0.5.md) | history_or_supporting | 원본 직접 조회 |

## 운영 정본

- [docs/human/phase-intents/PHASE-20261124-03.md](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/human/phase-intents/PHASE-20261124-03.md)
- [docs/review/README.md](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/review/README.md)
- [docs/artifacts/tasks/TASK-043.json](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/artifacts/tasks/TASK-043.json)
- [docs/artifacts/tasks/TASK-044.json](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/artifacts/tasks/TASK-044.json)
- [docs/artifacts/tasks/TASK-045.json](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/artifacts/tasks/TASK-045.json)
- [docs/artifacts/tasks/TASK-046.json](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/artifacts/tasks/TASK-046.json)
- [docs/artifacts/tasks/TASK-047.json](https://github.com/ik-e/chaja-you/blob/9b6ff0463722372d577747e89cb853e773c78591/docs/artifacts/tasks/TASK-047.json)
