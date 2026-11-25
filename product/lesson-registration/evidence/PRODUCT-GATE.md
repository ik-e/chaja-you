# 제품 수용 시험 실행기 · R01 TASK-048

정본은 [채택 common-integration V1 gate](../../../docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json)의 22개 ID이다. [실행기](product_gate.py)는 WORKSPACE pin의 git blob/commit과 ID 순서를 확인하고 동일 commit의 결과를 기록한다. 기존 gate/요구사항을 변경하지 않는다.

```sh
cd product/lesson-registration
uv sync --locked --all-groups --python 3.12
uv run --locked --all-groups --python 3.12 python evidence/product_gate.py --mode inventory
uv run --locked --all-groups --python 3.12 python evidence/product_gate.py --mode probe --output .local/product-gate.json
uv run --locked --all-groups --python 3.12 python evidence/product_gate.py --mode acceptance --require-complete
```

- inventory: pin 및 22개 실제 시나리오/기대/대상 확인. 실행은 하지 않는다.
- probe: R03의 실제 loopback HTTP/SQLite 합성 provider 시험과 실제 CLI 실행기 검증을 실행한다. 지원 근거의 명령/commit/코드 hash/시험 수/판정은 별도 기록하며, **부분 근거가 통과해도 product gate는 not_run**이다. `--gate <ID>`로 관련 probe만 선택 가능.
- acceptance: 전체 시나리오를 구현하고 R01이 검토한 case만 `PRODUCT_CASES`에 등록한다. 현재 등록된 완전한 case는 0개이다. 등록 시 명시 assertion ID/실제 관측(input+candidate, 응답/상태/외부 효과 수, 독립 증거 또는 부재)을 반환한다. 실행기가 불충족/누락을 구별한다. 수동 verdict 문자열·replay·단순 테스트 수로 통과시키지 않는다. 등록 코드가 pinned 기대를 완전히 검사하는지는 R01의 코드·시험 리뷰 책임이다. 기록만으로 진실성을 자동 증명하지 않는다.
- T5-08은 실제 모델 필수이므로 자동 CI에서 호출하지 않는다. R02가 승인된 별도 합성 실험과 통합 시험을 설계한 후 동일 후보의 전체 기준을 확인한다. 미실행은 통과가 아니다. `--require-complete`는 22개 모두 pass일 때만 0 반환.
- 실행 모드는 clean checkout, mock-only. 보고서 경로는 .local/ 또는 checkout 밖. 고정 합성 자료만 사용하고 credentials 및 proxy 변수를 제거한다. 실제 플랫폼/유료 API 호출을 구성하지 않는다. 실패 시 각 명령을 로컬에서 직접 재현. GitHub Actions [preflight](../../../.github/workflows/lesson-product-gate-preflight.yml)는 보고서를 artifact로 보존한다.

## 점진 통합 순서

1. R03 Mock API + 합성 PREP/Runtime으로 HTTP/UI 계약 확인. 실제 UI 소비는 R04 책임.
2. R02 PREP 및 R03 중첩/timeout 보존; R05 Runtime/Viewer/STORE 실제 실행 경계 및 R04 UI 연결.
3. 실제 크몽 Adapter와 Runtime, 실제 숨고 Adapter와 Runtime을 각 모의 사이트에 연결. 승인된 원본/target/operation/실제 저장·독립 재조회 확인.
4. 동일 후보에서 각 gate의 전체 시나리오를 구현·실행. 오류/응답 유실/경합/외부 효과·UI 및 두 플랫폼 교차 시험을 포함. 기존 22개 모두 충족 전 완료 금지.

공통 실행기는 업무 배분이나 제품 스펙을 변경하지 않는다.
