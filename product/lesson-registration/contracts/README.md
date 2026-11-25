# 공통 구현 계약 · 방향 승인 / 초기 공동 개발 기준

- [검토용 결정 및 적용 범위](IMPLEMENTATION-BINDING.json)
- [Python 인터페이스](interfaces.py) · [표준 스키마 검사](validation.py) · [Viewer 프런트 계약](viewer.d.ts)
- [R01 계획/검토 요청](../evidence/PLAN.md)

논리 계약 및 스키마 원본은 [WORKSPACE.json](../WORKSPACE.json)의 고정 참조를 사용한다. R01이 IB-01~05 방향을 수용했다. 초기 구현 경계는 공동 개발 기준으로 사용하며, 담당자 확인 후 변경이 필요하면 공통 계약 변경으로 기록한다. [승인 기록](../../../docs/human/responses/HRESP-20261125-02_common-implementation-binding.md) · [실행 근거](../evidence/common-contract-ci-20261125.json) 기존 논리 데이터 또는 플랫폼 규칙을 복제하거나 수정하지 않는다. actual runtime/DB/provider/permission 구현은 담당자가 수행한다.

- [PD-01~08 공통 물리 방향](PHYSICAL-BINDING.json): R01 방향 수용; 초기 제품 lock은 [기술 CI 근거](../evidence/physical-ci-20261125.json) 기반; 세부 연동과 실제 제품 검증 별도. 기존 IB/논리 계약 변경 없음.

- [담당자 공통 경계 확인](INTERFACE-REVIEW.md): 기존 계약 기준의 협의·반환 항목. [서버 canonical byte helper](canonical.py) 및 [검증 벡터](../fixtures/shared/canonical-vectors.json), 실제 scope/slot/readback 담당자 확인 별도.

## 서버 스키마 검증 기준 (IB-02 후속)

[후속 결정](../../../docs/human/responses/HRESP-20261125-04_r03-app-followup.md)에 따라 서버의 pinned named/profile schema 단일 판정 기준은 `validation.py`의 `SchemaCatalog` 및 제품 lock의 jsonschema 4.25.1이다. 포트 경계에서 `CheckedPorts` 또는 동일 공통 catalog를 호출하는 bridge를 사용한다. 오류 매핑·업무 관계·권한 검사는 각 담당 모듈이 추가. 별도 schema 엔진을 제품 권위로 유지하려면 차이 시험 및 R01 검토 필요. 프런트 자체 UX 검사는 서버 판정을 대체하지 않는다. 의존성이 없으면 검사를 skip/fallback하지 않는다. pinned logical schema는 변경하지 않는다.

## D01~D06 세부 방향 후보 (R01 수용)

[구조화 후보](DETAIL-CANDIDATE.json) · [원격 인증 보안 경계](SESSION-SECURITY.md) · [후보 digest/manifest 함수](detail_candidate.py) · [독립 reference](../evidence/detail_reference.py) · [시험](../tests/contract/test_detail_candidate.py). 기존 인터페이스/논리 pin은 그대로이며 후보 코드를 제품 provider로 자동 사용하지 않는다. 독립 시험 및 담당자 차이 확인 후 공통 세부 서명을 확정한다. Mock-only; 실제 사용자 인증 세션 사용 금지.
