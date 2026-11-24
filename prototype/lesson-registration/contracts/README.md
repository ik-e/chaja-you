# 공유 인터페이스 계약 공간 — R03 업무 의미 / R05 기술 인터페이스

상태: **협의 전 설계 초안**. 현재 확정된 API/Schema가 없으므로 임의로 서버의 REST 경로·데이터베이스 컬럼·프레임워크를 고정하지 않는다.

- I-01: source_id, source_version, facts(가격/시간/횟수/비용/조건), media_refs, evidence_refs → F1
- I-02: draft_id, draft_version, platform, mapped_fields, unresolved, provenance → R04 승인 화면
- I-03: approval_id, approved_draft_version, actions, environment(mock/live), approved_at → F2
- I-04: job_id, environment, event, evidence_refs, result_state, retry_blocked → F3/UI

합의 시 결정: 필수 타입·enum·누락/충돌 오류·버전 규칙·mock/live 경계·증거 의미·중복 실행 가드. 작성한 계약은 R03/R04/R05가 같은 예제로 검토하고 R01은 Must/Done 충돌만 판단.

**불변식:** 승인하지 않은 사실 생성 금지, 승인 버전 불일치 시 F2 거부, mock 성공을 live 접수라고 주장 금지, unknown 이후 자동 재제출 금지.

근거: [최소 설계](../../../docs/artifacts/design/lesson-registration-20261123/MVP-MINIMUM-DESIGN-V0.1.md)
