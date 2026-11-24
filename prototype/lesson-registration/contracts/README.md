# 모의 환경 계약 공간 · TASK-039 (R03)

오늘은 실제 F1/F2/F3 제품 스키마가 아닌 **테스트 환경용** 필드·오류·결과 의미를 정한다.

- 합성 fixture `source_id`, `facts`, 이미지 권리 상태
- 검수·승인 상태와 승인 전 실행 금지
- `MOCK_SUCCESS`, `MOCK_FAILURE`, `MOCK_UNKNOWN`, `NEEDS_CONFIRMATION` 등 시험 상태(이름은 R03/R04/R05 협의 후 확정)
- 어떤 데이터/조작으로 각 상태를 발생시키고 관측할지 정답/오류 케이스
- `mock`과 `live`의 상태를 절대 같은 '접수 완료'로 표시하지 않음

제출해야 할 것은 `mock-contract-v0.1.json`과 같은 입력·기대값·검증 파일이며, **현재는 아직 담당자의 실행 산출물이 없음**. 실제 기술 API 이름·DB 스키마는 결정하지 않는다.

참조: [오늘 배정](../../../docs/artifacts/design/lesson-registration-20261123/TEST-ENV-WORK-20261124.md).
