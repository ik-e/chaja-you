# 강사님 FinalProject 원본 전체 보존

> 기준: 2026-11-18 R01이 **강사로부터 GitHub 보존을 구두로 허락받았다고 확인**. 이는 사용자 제공 허락 사실의 기록이며, 모든 제3자에게 자유로운 재배포를 허가하는 라이선스 표시는 아닙니다.

## 보존 범위와 원칙

- 출처: [교육기관 Gitea `Lecture/FinalProject`](https://gt.isitsoft.kr/publicproj/aio-01d4-stu/src/branch/main/Lecture/FinalProject)
- 범위: 해당 **전체 폴더와 하위 파일**, 문서·샘플·가이드·지원 자료 및 해당 폴더에 포함된 기존 파일 전부
- 시점: GitHub Action이 Gitea `main`을 읽은 **그 시점**의 원본 commit SHA를 manifest에 기록
- 출력: `snapshots/<원본 커밋 40자리>/Lecture/FinalProject/`에 모든 파일을 **원본 바이트 그대로** 저장
- 변경 통제: 과거 스냅샷을 덮어쓰지 않고 새 커밋이 생기면 **새 디렉터리** 생성. 파일 변환·요약본은 이 폴더 밖에서 관리
- 무결성: 파일별 SHA-256, 크기, 원본 경로/commit, 총 파일수/총 바이트를 자동 생성·검증
- 공개 범위: 현재 `ik-e/chaja-you`는 public GitHub 저장소. 내부 팀 보존에 대한 구두 허락으로 기록하고, 원본의 재사용/재배포는 강사의 안내 범위에서만

## 실행

`python tools/archive_full_finalproject.py --archive` 는 네트워크를 통해 Gitea **지정 공개 저장소**의 해당 폴더만 다운로드하여 원본 스냅샷을 작성합니다. `--verify` 는 이미 저장된 스냅샷의 누락·초과·변형·해시 오류를 검출합니다.

GitHub Action [archive-full-instructor-finalproject.yml](../../../.github/workflows/archive-full-instructor-finalproject.yml)은 전용 작업 브랜치에서 실행하며 **기존 TASK/WBS/Phase/프로젝션 산출물/대시보드를 수정하지 않습니다.**

**보존과 채택을 구분합니다.** 원본 자료의 목차/가이드가 새로 배포되더라도 기존 기획·기술 선택이 자동 변경되는 것은 아닙니다.

## 스냅샷 내 파일

실제 업로드된 각 버전의 `manifest.json`에서 파일 목록과 링크를 확인합니다. 가이드 개정 시 `snapshot commit`을 갱신하지 않고 새 스냅샷을 만듭니다.
