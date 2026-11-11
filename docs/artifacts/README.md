# AI 산출물 원본

AI가 작성·수정하는 구조화 데이터의 기준 공간이다. 새 산출물은 JSON으로 저장하고 안정적인 ID, 종류, 상태, 담당, 입력·출력, 근거와 검증을 담는다. 도구 출력·표본 데이터는 필요한 범위에서 원래 형식을 함께 보존한다.

| 공간 | 내용 |
|---|---|
| [planning](planning/README.md) | 기획서 원본·기획 제안 |
| [research](research/README.md) | 조사 결과·이전 기술 제안 |
| [specs](specs/README.md) | 현재 요구사항과 평가 사례 |
| [state](state/README.md) | 현재 우선순위·결정 요청·제출 상태 |
| [tasks](tasks/README.md) | 작업 입력과 실행 결과 |
| [runs](runs/README.md) | 상세 실행·근거 데이터 |
| [evaluations](evaluations/README.md) | 사례별 실제 평가 기록 |

이관한 문서는 원래 담당·상태·출처와 본문을 JSON의 메타데이터와 섹션으로 보존했다. `kind: document`는 조사·제안 자료이고, 현재 목표는 [PROJECT](../../PROJECT.md), 현재 계약은 [EVAL](../../EVAL.md)에서 찾는다. 원본·생성 문서 관계와 갱신 방법은 [문서 관리 규칙](../문서_관리_규칙.md)을 따른다. 작업 담당자가 산출물과 관련 상태를 갱신한다.
