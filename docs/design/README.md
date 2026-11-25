# 설계 문서

- `architecture/`: 시스템 구성, 구성 요소, 데이터 흐름
- `api/`: API 계약, 요청·응답 예시, 오류 규칙
- `data/`: 데이터 모델, 스키마, 마이그레이션 기준
- [ADR](../adr/README.md): 주요 선택의 맥락·근거·재검토 조건

현재 설계 데이터는 [AI 산출물](../artifacts/README.md)에서 관리하고, 사람이 확인할 내용은 프로젝션으로 연결합니다. 담당자는 중요한 선택의 이유와 재검토 조건을 ADR에 남깁니다.

- [아키텍처](architecture/README.md) · [API](api/README.md) · [데이터](data/README.md) · [설계 결정](decisions/README.md)
- 프로젝트 팀 규칙: [팀 헌장](../charter/팀_헌장.md)
- 문서 연결·갱신 규칙: [문서 관리 규칙](../문서_관리_규칙.md)

## 현 프로젝트 설계 검토

- [레슨 등록 지원 서비스 — 사람용 검토 홈](lesson-registration/README.md) · [AI 조회 인덱스](lesson-registration/MANIFEST.json)
- 고정 설계 검토 스냅샷입니다. 현재 적용은 [논리 설계 채택 기록](../artifacts/design/lesson-registration-20261124/adoption-20261125.json), [CURRENT](../../CURRENT.md), [제품 작업 공간](../../product/lesson-registration/README.md)을 우선합니다. 실서비스 실행 승인은 아닙니다.
