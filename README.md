# chaja-you

**2026-11-23 현재 R02 음악 레슨 강사용 등록 지원 서비스의 12항목 기획을 구체화하고 있습니다.** 기획 방향은 정했으나 실제 사용자 Pain의 우선순위·MVP·기술 구현 방식·수익 모델은 아직 검증/확정되지 않았습니다. UI/DB/API 상세 설계 및 PoC·구현은 보류 중입니다. 아래 찾아you 앱 리서치 설명은 **이전 제품안 및 교육기관 잠정 제출 기준**으로만 유지합니다.

[현재 단계 의도](docs/human/phase-intents/PHASE-20261123-01.md) · [현재 실행 상태](CURRENT.md) · [레슨 등록 기획·담당별 산출물](docs/artifacts/planning/lesson-registration-20261123/README.md)

기존 찾아you 방향: 사용자 요청에 따라 조사 워크플로와 에이전트 팀을 동적으로 구성하고, 결과에 근거와 출처를 연결하는 리서치 시스템 (현재 실제 구현 보류).

사람은 [사람 작업 공간](docs/human/README.md)에서 AI 결과의 프로젝션을 확인하고 의도·승인·수정·보류를 남깁니다. AI는 [PROJECT](PROJECT.md), [CURRENT](CURRENT.md), [EVAL](EVAL.md), [TASK](TASK.md)와 해당 작업의 [구조화 산출물](docs/artifacts/README.md)을 사용합니다. 중요한 선택은 [ADR](docs/adr/README.md)에 근거·결정 권한·재검토 조건을 남깁니다.

- [전체 문서 안내](docs/README.md) · [AI 작업 지침](AGENTS.md)
- [팀 헌장](docs/charter/팀_헌장.md) · [공개 저장소 운영 안내](docs/public/공개_저장소_운영_안내.md)
- [Discord 읽기·검색 도구](docs/discord/Discord_읽기_검색_도구.md)

## Step 1 제출 문서

- [기획서·요구사항](docs/step1/기획서.md) · [WBS·담당·주차별 계획과 실적](docs/step1/WBS.md)
- [양식·작성·열람 안내](docs/step1/README.md) · [제출 준비·실제 제출 상태](docs/submissions/README.md)

기획서는 서비스 정의·기능 요구사항·비기능 요구사항을 기본으로 작성합니다. 구조·스택·미정 기술의 결정 담당/시점과 검증 계획을 포함합니다. WBS는 공식 산출물의 작성·검토·제출을 개발과 구분합니다. 문서 생성이나 링크 준비만으로 제출 완료가 되지 않습니다.

## 프로젝션 생성

AI 산출물 원본을 바꾸고 다음 명령으로 CURRENT·EVAL·검토 화면·제출물 인덱스와 Step별 제출 프로젝션을 생성합니다.

```powershell
uv run --no-project python tools/project_docs.py
uv run --no-project python tools/project_docs.py --check
```

이 저장소는 공개 팀 공동 작업 공간입니다. 비밀값·개인 연락처·비공개 URL은 기록하지 않으며, 외부 원본은 이용 권한과 공개 범위를 확인합니다.
