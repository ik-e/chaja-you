# AI 작업 계약

AI는 [PROJECT](PROJECT.md)와 [CURRENT](CURRENT.md)에서 목표와 우선순위를 확인하고, [EVAL](EVAL.md)의 적용 기준을 작업에 연결한다. 담당자는 [JSON 템플릿](docs/artifacts/tasks/template.json)을 복사해 [작업 공간](docs/artifacts/tasks/README.md)에 저장한다. `kind`를 `task`로 바꾸고 고유 ID, 담당·기한과 아래 항목을 채운다. 담당·기한이 정해지지 않았으면 `null`로 둔다.

| 필드 | 작업에 담을 내용 |
|---|---|
| question · goal | 답할 질문과 이 답으로 내릴 결정 |
| inputs · references | 필요한 기준·선행 결과의 저장소 경로 |
| scope | 이번 작업의 범위와 제약 |
| outputs | 구조화 산출물 형식과 저장 경로 |
| acceptance · verification | 완료 조건과 실제 확인 방법 |
| depends_on | 완료 전에 반영할 선행 TASK ID. 초안 작성은 기존 자료로 병행 가능 |
| suggested_owner · due | 담당 제안과 내부 목표일. owner가 null이면 실제 배정은 미확정 |
| submission_ids · required_for_submission | 연결할 제출물 ID와 제출 준비에 필요한 작업인지 여부 |
| result | summary, claims, evidence, verification, uncertainties, decision_requests |

canonical TASK 원본은 한 시점에 한 명의 책임자만 직접 수정한다. 기본 책임자는 `owner`이며, 다른 팀원은 근거·차이·수정 제안을 자신의 작업 기록에 남기고 owner가 정본에 반영한다. 다른 TASK가 전제로 사용할 의미·인터페이스·상태·완료 조건만 담당자 간 합의 대상으로 두고, 제품 범위·필수 요구사항·완료 기준을 바꾸는 충돌은 R01 결정으로 올린다. 세부 기준은 [문서와 산출물 관리 규칙](docs/문서_관리_규칙.md#협의정본-수정커밋-규칙)을 따른다.

상태는 `할 일`, `진행 중`, `검토 중`, `완료`, `막힘`을 사용한다. `result`는 실행 전 `null`이고, 완료 시 실제 검증과 근거를 포함한다. 제안과 관찰 결과를 구분하고, 출처나 실행 기록으로 뒷받침하지 못한 항목은 불확실성으로 남긴다.

결과 형식은 [기계용 결과 템플릿](docs/artifacts/tasks/result_template.json)을 따른다. 각 주장은 `id`, `text`, `status`, `evidence_ids`를 갖는다. 근거는 고유 `id`와 저장소 기준 `path` 또는 공개 `url`을 갖고, 검증은 `criterion`, `verdict`, `evidence_ids`를 갖는다. 실행 전 예시값은 실제 결과로 사용하지 않는다.

상세 실행 기록과 평가 결과도 JSON으로 저장한다. 실행은 `id`, `kind: run`, `status`, `case_id`, `input`, `plan`, `steps`, `claims`, `evidence`를 갖고, 각 작업의 역할·선행 관계·실행 순서와 실제 상태를 남긴다. 평가 결과는 `kind: evaluation`, `case_id`, `run_path`, `checks`, `verdict`를 갖는다. 각 검사에는 `criterion`, `verdict`, `evidence`를 기록한다. 판정은 `pass`, `fail`, `inconclusive` 중 하나다.

사람은 [검토 화면](docs/review/README.md)에서 결론·검증·남은 불확실성·결정 요청을 확인하고, 중요한 결정은 [ADR](docs/adr/README.md)의 원본에 기록한다.

원본 변경 후 `uv run --no-project python tools/project_docs.py`로 프로젝션을 생성한다. `uv run --no-project python tools/project_docs.py --check`로 원본 형식과 프로젝션 최신 여부를 확인한다.
