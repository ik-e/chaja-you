# 사람 작업 공간

이 디렉터리는 사람이 프로젝트의 방향을 정하고 AI 결과에 의도·판단·피드백을 남기는 권위 입력 공간입니다.

## 사람이 읽는 화면

- [프로젝트 검토 화면](../review/README.md): AI 작업 결과, 검증, 불확실성, 결정 요청을 압축해서 봅니다.
- [필수 제출물](../submissions/README.md): 기획서·WBS·발표 등 사람에게 전달할 프로젝션을 확인합니다.
- [현재 상태](../../CURRENT.md): 현재 범위·우선순위·열린 결정을 빠르게 확인합니다.

## 사람이 쓰는 입력

- [INTENT](INTENT.md): 장기간 유지할 목표·운영 원칙·제약을 사람이 직접 관리합니다.
- [responses](responses/README.md): 특정 OPEN/TASK/ADR에 승인·수정·보류·거절·추가 지시를 남깁니다.

생성된 `review/`, `submissions/`, `PROJECT.md`, `CURRENT.md`, `EVAL.md`는 직접 수정하지 않습니다. 사람이 방향을 바꾸려면 `INTENT.md` 또는 `responses/`에 남기고, AI가 그 입력을 ADR·state·spec·task 원본에 반영한 뒤 프로젝션을 재생성합니다.

```text
AI canonical artifacts
        ↓
generated review / submission
        ↓
human intent / response
        ↓
ADR / state / spec / task update
        ↓
next AI work
```

AI는 사람이 명시적으로 요청하지 않는 한 이 디렉터리의 사람 입력 파일을 대신 수정하지 않습니다.
