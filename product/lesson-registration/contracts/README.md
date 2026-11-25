# 공통 구현 계약 · 방향 승인 / 초기 공동 개발 기준

- [검토용 결정 및 적용 범위](IMPLEMENTATION-BINDING.json)
- [Python 인터페이스](interfaces.py) · [표준 스키마 검사](validation.py) · [Viewer 프런트 계약](viewer.d.ts)
- [R01 계획/검토 요청](../evidence/PLAN.md)

논리 계약 및 스키마 원본은 [WORKSPACE.json](../WORKSPACE.json)의 고정 참조를 사용한다. R01이 IB-01~05 방향을 수용했다. 초기 구현 경계는 공동 개발 기준으로 사용하며, 담당자 확인 후 변경이 필요하면 공통 계약 변경으로 기록한다. [승인 기록](../../../docs/human/responses/HRESP-20261125-02_common-implementation-binding.md) · [실행 근거](../evidence/common-contract-ci-20261125.json) 기존 논리 데이터 또는 플랫폼 규칙을 복제하거나 수정하지 않는다. actual runtime/DB/provider/permission 구현은 담당자가 수행한다.
