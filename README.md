# chaja-you

사용자 요청에 따라 조사 워크플로와 에이전트 팀을 동적으로 구성하고, 결과에 근거와 출처를 연결하는 리서치 시스템입니다.

사람은 [사람 작업 공간](docs/human/README.md)에서 AI 결과의 프로젝션을 확인하고 의도·승인·수정·보류를 남깁니다. AI는 [PROJECT](PROJECT.md), [CURRENT](CURRENT.md), [EVAL](EVAL.md), [TASK](TASK.md)와 해당 작업의 [구조화 산출물](docs/artifacts/README.md)을 사용합니다. 중요한 선택은 [ADR](docs/adr/README.md)에 근거·결정 권한·재검토 조건을 남깁니다.

- [전체 문서 안내](docs/README.md) · [AI 작업 지침](AGENTS.md)
- [팀 헌장](docs/charter/팀_헌장.md) · [공개 저장소 운영 안내](docs/public/공개_저장소_운영_안내.md)
- [Discord 읽기·검색 도구](docs/discord/Discord_읽기_검색_도구.md)

## 프로젝션 생성

AI 산출물 원본을 바꾸고 다음 명령으로 CURRENT·EVAL·검토 화면·제출물 인덱스와 Step별 제출 프로젝션을 생성합니다.

```powershell
uv run --no-project python tools/project_docs.py
uv run --no-project python tools/project_docs.py --check
```

이 저장소는 공개 팀 공동 작업 공간입니다. 비밀값·개인 연락처·비공개 URL은 기록하지 않으며, 외부 원본은 이용 권한과 공개 범위를 확인합니다.
