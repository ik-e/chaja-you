# 2026-11-18 Step1·Step2 독립 프로젝션 파일럿

> **개발/제출 정본을 교체하지 않은 격리된 검증본**입니다. 2026-11-18 기준 기존 찾아you 기획을 공식 제출 대응의 **잠정 기준**으로 사용합니다. 실제 제품 선정 목표는 11/21입니다.

## 파일럿 4개 결과

| 산출물 | 생성 파일 | 직접 출처 |
| --- | --- | --- |
| STEP1 기획서 및 FR/NFR | [기획서](STEP1-%EA%B8%B0%ED%9A%8D%EC%84%9C.md) | [model.json](model.json) DLV-01 |
| STEP1 WBS(기존 계획/두 트랙) | [WBS](STEP1-WBS.md) | DLV-02 |
| STEP2 API 계약 초안 | [API 설계](STEP2-API-%EC%84%A4%EA%B3%84.md) | DLV-03 |
| STEP2 DB 스키마/ERD | [DB 설계](STEP2-DB-%EC%8A%A4%ED%82%A4%EB%A7%88.md) | DLV-04 |

## 생성·검증

```bash
python tools/pilot_step1_step2.py --check
python tools/pilot_step1_step2.py
```

원본 [model.json](model.json)을 수정한 경우에만 위 생성기로 **이 파일럿 디렉터리 안의 4개 파일**을 다시 생성합니다. 다른 TASK/기획서·WBS 원본과 대시보드를 수정하지 않습니다.

[검토/한계 보고서](REVIEW.md) · [프로젝션 기준](../../PROJECTION-CONTRACT.md) · [품질 게이트](../../QUALITY-GATES.md)

## 확인된 불변 경계

- 유지: `docs/step1/기획서.md`, `docs/step1/WBS.md`, `docs/artifacts/planning/*.json`, `docs/artifacts/tasks/TASK-*.json`, `docs/human/phase-intents/`, 대시보드 제출 상태
- 별도 추가: 이 디렉터리의 Markdown 초안과 정합성 검사 도구
- 미실행: 제품 기능/API/DB 구현, 실제 사용자/앱/모델 통합 테스트, 공식 제출·접수
- 공식 [OUTPUT-GUIDE](https://gt.isitsoft.kr/publicproj/aio-01d4-stu/src/branch/main/Lecture/FinalProject/OUTPUT-GUIDE.md)에는 제공 목차의 항목 누락 금지 규칙이 있습니다. **강사 수정본의 정확한 목차/별도 WBS 제출 방법을 아직 대조하지 못했으므로 현재 파일은 공식 제출완료판이 아닙니다.**

## 변경 후 재검토

11/21 실제 주제 선정 후에는 새 Phase/의도와 새 사용자 문제·요구사항을 기준으로 내용을 다시 작성합니다. 이 파일럿은 과거 기준/재사용 가능한 형식의 테스트 이력으로 보존하며, 새로운 기획 정본으로 자동 승격하지 않습니다.
