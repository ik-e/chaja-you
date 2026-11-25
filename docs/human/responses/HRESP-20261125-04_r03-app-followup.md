# HRESP-20261125-04 · R03 TASK-050 진행 확인 및 공통 기준 적용

- 일자: 2026-11-25
- 권위: R01
- target: TASK-050, TASK-048, IB-02, PD-02~05, WBS V0.6 후보
- action: clarify
- 사용자 지시 원문: “디스코드 전달 했고 남은 사항 처리해줘”
- 이전 공통 방향: [HRESP-20261125-02](HRESP-20261125-02_common-implementation-binding.md) · [HRESP-20261125-03](HRESP-20261125-03_common-physical-direction.md)

R01은 R03에게 전달안을 전달했다고 보고하였다. Discord 원문/수신은 별도 검증하지 않았다. 앞서 전달한 결정의 정본 반영과 잔여 사항 정리를 진행한다.

- FastAPI 및 jsonschema 제품 lock은 main `c4742a1`에 이미 반영. S8 독립 구현 진행, multipart 등 추가 dependency는 담당자 제안 후 R01 검토.
- 서버 schema 판정의 단일 기준은 pinned named/profile Draft 2020-12 schema와 공통 jsonschema 4.25.1 검증기. 공통 구현 재사용을 기본으로 하며 오류 변환·업무 검증은 담당자 국소 책임. 별도 자체 schema 엔진을 제품 권위로 유지하려면 근거·차이 시험·R01 검토 필요. 프런트에 Python 구현을 강제하지 않는다.
- REQ-08 과거 원본 보존, 현행 CS-05/06 및 A2 적용. 오류 전용 중단, 읽기 근거 추가 허용, 재개/자동 재실행/rollback 금지. 종료 연산은 기존 `finalize`.
- canonical helper/golden vectors 사용. actual readback·operation manifest·binding 대상·slot 및 lease/helper 세부 계약은 담당자 확인 후 확정. 합성 replay 자리표시 digest를 성공 근거로 사용하지 않고 계산 대상 합의 후 R01이 공통 fixture 갱신.
- TASK-050 진행 중. R03 보고(S0~S7, 174/10/2 통과)는 [근거 기록](../../../product/lesson-registration/evidence/r03-progress-20261125.json)에 분리하고 독립 재검증/제품 완료로 표시하지 않는다. W10/W16/PREP 유지보수 추가 배정 미확정. 잔여 공수와 전체 담당자 계획 확인 후 WBS 조정. 22개 gate 및 mock-only 유지.
