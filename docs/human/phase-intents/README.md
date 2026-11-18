# 현재 단계 의도 (Phase Intent)

장기 의도와 개별 TASK 의도 사이에서 **지금 적용되는 실행 전략·보류 범위·의사결정 시점**을 명시하는 R01 권위 입력입니다.

- [현재 단계: PHASE-20261118-01 · 투 트랙](PHASE-20261118-01.md)
- 적용 중인 Phase의 단일 포인터는 [current.json](../../artifacts/state/current.json)의 `active_phase_intent_ref`입니다.
- 각 활성 TASK는 `phase_intent_ref`와 `traceability.intent_refs`로 현재 단계 의도를 참조합니다.
- 현재 단계 의도는 장기 [INTENT](../INTENT.md)를 바꾸지 않고, 과거 제품 제안·WBS를 현재 실행 결정으로 자동 승인하지 않습니다.
- 단계 전환은 사용자/팀의 실제 결정이 나온 후 새 파일과 포인터를 만들어 기록합니다. 과거 문서는 이력으로 남깁니다.
