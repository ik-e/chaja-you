# AI 작업 계약

AI는 [장기 의도](docs/human/INTENT.md)와 [현재 단계 의도](docs/human/phase-intents/README.md)를 확인하고 [CURRENT](CURRENT.md)의 적용 범위·보류 상태를 읽는다. [PROJECT](PROJECT.md)와 [EVAL](EVAL.md)는 단계에 따라 과거 기획·제출용 잠정안일 수 있으므로 실제 구현 지시로 자동 적용하지 않는다. 해당 TASK의 검증 기준만 선택적으로 연결한다. 담당자는 [JSON 템플릿](docs/artifacts/tasks/template.json)을 복사해 [작업 공간](docs/artifacts/tasks/README.md)에 저장한다. `kind`를 `task`로 바꾸고 고유 ID, 담당·기한과 아래 항목을 채운다. 담당·기한이 정해지지 않았으면 `null`로 둔다.

| 필드 | 작업에 담을 내용 |
|---|---|
| question · goal | 답할 질문과 이 답으로 내릴 결정 |
| inputs · references | 필요한 기준·선행 결과의 저장소 경로 |
| scope | 이번 작업의 범위와 제약 |
| outputs | 구조화 산출물 형식과 저장 경로 |
| acceptance · verification | 완료 조건과 실제 확인 방법 |
| phase_intent_ref | CURRENT의 active_phase_intent_ref와 연결하는 현 단계 실행 목적·보류 경계. 모든 활성 TASK에서 일치 여부 확인 |
| traceability | 관련 `intent_refs`·`design_refs`·`requirement_refs`·`evaluation_refs`. 존재하는 ID만 연결하고 불필요한 문서 생성을 위한 참조는 만들지 않음 |
| validation_plan | 구현과 함께 설계할 검증 질문·baseline·관측값·성공/미확인 조건. 단순 작업에는 `null` 가능 |
| depends_on | 완료 전에 반영할 선행 TASK ID. 초안 작성은 기존 자료로 병행 가능 |
| suggested_owner · due | 담당 제안과 내부 목표일. owner가 null이면 실제 배정은 미확정 |
| submission_ids · required_for_submission | 연결할 제출물 ID와 제출 준비에 필요한 작업인지 여부 |
| result | summary, claims, evidence, verification, uncertainties, decision_requests |

canonical TASK 원본은 한 시점에 한 명의 책임자만 직접 수정한다. 기본 책임자는 `owner`이며, 다른 팀원은 근거·차이·수정 제안을 자신의 작업 기록에 남기고 owner가 정본에 반영한다. 다른 TASK가 전제로 사용할 의미·인터페이스·상태·완료 조건만 담당자 간 합의 대상으로 두고, 제품 범위·필수 요구사항·완료 기준을 바꾸는 충돌은 R01 결정으로 올린다. 세부 기준은 [문서와 산출물 관리 규칙](docs/문서_관리_규칙.md#협의정본-수정커밋-규칙)을 따른다.

새 TASK는 가능한 범위에서 `traceability`로 상위 Intent·Design Hypothesis·Requirement·Evaluation을 연결한다. 모든 참조를 반드시 채우는 것이 목적이 아니라, **왜 이 작업이 존재하고 어떤 가설·요구사항을 검증하는지 실제로 추적할 가치가 있는 관계만 기록**한다. 기존 TASK 전체를 소급 마이그레이션하지 않는다.

`validation_plan`은 구현 범위를 정할 때 같이 작성한다. 최소 항목은 검증 질문, 기대 관측값, 성공/실패/미확인 경계이며 비교가 필요한 경우 baseline과 동일 조건을 추가한다. 실제 실행 근거가 없으면 정량 합격선을 임의로 확정하지 않는다. 단순 문서 정리·기계적 변환처럼 별도 실험이 불필요한 작업은 `null`로 둘 수 있다.

상태는 `할 일`, `진행 중`, `검토 중`, `완료`, `막힘`을 사용한다. `result`는 실행 전 `null`이고, 완료 시 실제 검증과 근거를 포함한다. 제안과 관찰 결과를 구분하고, 출처나 실행 기록으로 뒷받침하지 못한 항목은 불확실성으로 남긴다.

결과 형식은 [기계용 결과 템플릿](docs/artifacts/tasks/result_template.json)을 따른다. 각 주장은 `id`, `text`, `status`, `evidence_ids`를 갖는다. 근거는 고유 `id`와 저장소 기준 `path` 또는 공개 `url`을 갖고, 검증은 `criterion`, `verdict`, `evidence_ids`를 갖는다. 실행 전 예시값은 실제 결과로 사용하지 않는다.

상세 실행 기록과 평가 결과도 JSON으로 저장한다. 실행은 `id`, `kind: run`, `status`, `case_id`, `input`, `plan`, `steps`, `claims`, `evidence`를 갖고, 각 작업의 역할·선행 관계·실행 순서와 실제 상태를 남긴다. 평가 결과는 `kind: evaluation`, `task_ref`, `case_id`, `run_path`, `checks`, `verdict`를 갖고, 필요한 경우 TASK와 동일한 `traceability` 참조를 이어받는다. 각 검사에는 `criterion`, `verdict`, `evidence`를 기록한다. 판정은 `pass`, `fail`, `inconclusive` 중 하나다.

사람은 [검토 화면](docs/review/README.md)에서 결론·검증·남은 불확실성·결정 요청을 확인하고, 중요한 결정은 [ADR](docs/adr/README.md)의 원본에 기록한다.

원본 변경 후 `uv run --no-project python tools/project_docs.py`로 프로젝션을 생성한다. `uv run --no-project python tools/project_docs.py --check`로 원본 형식과 프로젝션 최신 여부를 확인한다.

## 현재 레슨 등록 PoC의 요구사항과 실행 기록

이전 `focus_apps.json`의 요구사항/사례 ID와 레슨 등록 기획 V1.1의 FR ID는 같은 의미가 아니다. TASK-043~045는 `traceability.product_spec_ref`와 `product_requirement_refs`로 레슨 요구사항을 별도 연결한다. 기존 검증기의 `requirement_refs`는 기존 focus_apps 기준이므로 혼용하지 않는다. PoC 실행 증거는 우선 담당 작업 디렉터리에 두고 TASK result의 근거로 연결한다. 새로운 제품 평가 사례가 정본에 채택되기 전에는 이전 focus_apps의 case ID로 새 run/evaluation을 등록하지 않는다.

## 종료·미채택 TASK 조회

- [TASK-001~021 기존 정산 원장](docs/artifacts/state/legacy_task_closeout_20261118.json)
- [TASK-022~042 정산 및 사유](docs/artifacts/state/TASK-CLOSEOUT-20261124.md) · [구조화 정산 원본](docs/artifacts/state/task_closeout_20261124.json)

원본 상태와 운영상 비활성·보류·대체·미채택을 구분하며, 미채택 번호를 다시 사용하지 않는다. 재개는 현재 단계와 R01 결정에 따른 별도 TASK로 기록한다.

TASK 종료 또는 대체 시 [브랜치 수명 주기와 종료](docs/development/GitHub_코드_관리_협업_규칙.md#브랜치-수명-주기와-종료)에 따라 검증·정본 반영/정산·근거 보존을 확인하고 불필요한 작업 브랜치를 정리한다. TASK의 원본 상태·결과 및 미해결 의무는 브랜치 삭제와 별개로 유지한다.
