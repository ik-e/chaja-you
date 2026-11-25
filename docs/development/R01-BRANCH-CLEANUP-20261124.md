# R01 작업 브랜치 정리 기록 (2026-11-24)

- 담당: R01
- 적용 범위: `r01/` 접두사인 원격 브랜치 6개만. main, R02~R05, 개인, docs/·ops/·review/·task/·experiment/ 등 다른 이름의 브랜치는 정리 대상에서 제외.
- 결정 근거: R01의 현재 대화 요청 및 [브랜치 수명 주기](GitHub_코드_관리_협업_규칙.md#브랜치-수명-주기와-종료), [2026-11-24 TASK 정산](../artifacts/state/TASK-CLOSEOUT-20261124.md).
- 비교 기준: main [9200941e](https://github.com/ik-e/chaja-you/commit/9200941eca7cc33d23fe1152973c1e563c883581)
- **실행 상태:** 삭제 판단 및 실행 절차 준비 완료. 현재 GitHub 연결은 원격 브랜치 삭제·태그 생성 작업을 지원하지 않아 태그 생성 및 실제 브랜치 삭제는 미실행이다. 삭제되었다고 기록하지 않는다.

## A. 통합 완료 — 즉시 정리 후보 4개

각 브랜치의 최신 HEAD와 병합 당시 PR HEAD가 정확히 일치하고, PR 병합 커밋을 위 main과 비교한 결과 ahead_by=0, status=behind였다. 이후 브랜치 단독 작업이 남았다는 증거가 없고 활성 TASK 또는 열린 PR의 head/base가 아니다. 별도 아카이브 태그가 필요하지 않다.

| 브랜치 | 확인 HEAD | 병합 PR / main에 포함된 커밋 | 사유 |
|---|---|---|---|
| `r01/correct-ops-context-20261119` | [7795d89c](https://github.com/ik-e/chaja-you/commit/7795d89ca5e4e3c2ea986f462fba88bbee39ca40) | [#26](https://github.com/ik-e/chaja-you/pull/26) · [559dd2ce](https://github.com/ik-e/chaja-you/commit/559dd2ce3a2935eadab6d0e4561af7ba34de1e1d) · 2026-11-19T08:55:25Z | 팀장 관리 문서의 운영 맥락 정정이 PR #26으로 반영되었고, 현재 단계의 지시 및 상태 원본은 이후 결정에 따라 main에서 관리한다. 추가 HEAD 변경 없음. |
| `r01/ops-sync-20261119` | [dc2b55d4](https://github.com/ik-e/chaja-you/commit/dc2b55d477a5a2a8b6c4cc0af23694cd33a0b2e1) | [#24](https://github.com/ik-e/chaja-you/pull/24) · [dd514492](https://github.com/ik-e/chaja-you/commit/dd514492e17a091192a697fc9469cdbaee1b3b49) · 2026-11-19T08:48:18Z | R01 관리 정본·프로젝션 동기화가 PR #24로 반영되었으며 후속 상태·TASK 정산은 main에 존재한다. 당시 동기화 작업 브랜치를 재사용할 이유 없음. |
| `r01/planning-design-information-model-20261119` | [d582a84e](https://github.com/ik-e/chaja-you/commit/d582a84e4f8c22ff3ca36acd6381d2d9132c4230) | [#21](https://github.com/ik-e/chaja-you/pull/21) · [97bb9486](https://github.com/ik-e/chaja-you/commit/97bb948653010b649bb0929c8868d5c8921cd98c) · 2026-11-19T05:44:03Z | 기획·설계 정보 모델과 검증 계획이 PR #21로 병합되었으며 main의 docs/deliverables/PLANNING-DESIGN-INFO-MODEL.md 등에서 재사용할 수 있다. 실험 브랜치를 유지할 필요 없음. |
| `r01/step1-step2-submission-drafts-20261119` | [161e75aa](https://github.com/ik-e/chaja-you/commit/161e75aa59d2511c297a7912b7f5ec1a13fa0e63) | [#23](https://github.com/ik-e/chaja-you/pull/23) · [0c2c7b4f](https://github.com/ik-e/chaja-you/commit/0c2c7b4faa42e759c79fa2a1ba91159f0bd2c77c) · 2026-11-19T06:39:10Z | Step1·Step2 잠정 제출 문서 배치가 PR #23으로 병합되었다. main에 당시 제출 체크리스트가 존재하며 이후 개정은 main에서 관리한다. 실제 제출·접수 확인 의무는 남아 있지만 이 브랜치를 유지할 필요는 없음. |

## B. 미채택·대체 — 보존 후 정리 후보 2개

| 브랜치 | 확인 HEAD / main 대비 별도 커밋·비교 파일 | 정리 사유 | 보존 예정 태그 |
|---|---|---|---|
| `r01/lesson-design-kickoff-20261123` | [dba2f5dc](https://github.com/ik-e/chaja-you/commit/dba2f5dc97a4c8a61d523831a51f6f30b1936efb) · 7개 커밋 / 6개 변경 파일 | 단일 크몽 중심 기능별 분업 제안(TASK-033~037)이 플랫폼별 독립 PoC로 대체되어 정식 배정되지 않았다. ADR-004 제안, design-intake, milestone-plan, 작업 계약 원본은 main에 모두 병합되지 않았다. 원본 HEAD를 태그로 고정한 뒤 브랜치 삭제 가능. | `archive/r01-lesson-design-kickoff-20261123` |
| `r01/lesson-mvp-workspace-20261124` | [aa9a9092](https://github.com/ik-e/chaja-you/commit/aa9a9092da5e0c8a6ed9565e8836b060e313f094) · 44개 커밋 / 26개 변경 파일 | PR #41은 R01 지시로 미병합 종료되었다. TASK-038~042의 테스트 환경 분업은 TASK-043~045로 대체했고 공통 환경 설정은 별도로 main에 반영했다. 이전 최소 설계, fixture·시험 코드·TASK 원본 등 고유 자료가 남아 있으므로 원본 HEAD를 태그로 고정하기 전에는 삭제하지 않는다. | `archive/r01-lesson-mvp-workspace-20261124` |

설계 착수 브랜치 HEAD는 MVP 작업 공간 브랜치 HEAD의 조상이다(비교: ahead 37, behind 0). 다만 TASK-033~037의 원본과 TASK-038~042의 원본을 구분하기 위해 두 시점의 태그를 각각 고정하는 것이 명확하다. 기존 정산 원장은 이미 두 commit SHA에 연결되어 있다. 태그를 생성하지 않은 상태에서 SHA 링크만으로 영구 보존을 가정하지 않는다.

현재 구현은 [활성 단계](../human/phase-intents/PHASE-20261124-02.md)와 [현재 작업 공간](../../prototype/lesson-registration/README.md)을 사용한다. 과거 설계 및 미채택 TASK를 다시 활성화하거나 main에 일괄 병합하지 않는다.

## C. 삭제 전 검증 및 실행

- 현재 열린 PR은 #5이며 대상 R01 브랜치를 head/base로 사용하지 않는다.
- GitHub 기본 브랜치 코드 검색에 각 브랜치 전체 이름을 질의했을 때 결과 0건이었다. 검색 결과는 모든 문서/비공개 링크의 전수 확인을 의미하지 않는다. 실제 삭제 직전에 main 및 작업 중 문서의 브랜치명 참조를 다시 점검하고 필요 시 main 또는 보존된 commit 링크로 수정한다.
- 해당 브랜치를 로컬에서 작업 중인 사람이 없고 미커밋 파일이 없음을 확인한다. 로컬 브랜치는 본 실행의 삭제 대상이 아니다.
- 원격 최신 HEAD가 기록과 다르면 재검토하고 삭제하지 않는다. 아래 명령은 원격 삭제에 SHA 조건을 붙인다.
- B의 태그는 필요한 원본 보존을 위해 먼저 원격에 생성하고 HEAD 일치를 확인한 후 삭제한다. 태그 이미 존재 시 재지정/강제 푸시하지 않는다.

### 실행 명령 (인증된 로컬 Git, origin이 ik-e/chaja-you인지 확인 후)

```powershell
git remote get-url origin
git fetch origin --prune
# A: 병합 완료 브랜치만 정리
git push --force-with-lease=refs/heads/r01/correct-ops-context-20261119:7795d89ca5e4e3c2ea986f462fba88bbee39ca40 origin :refs/heads/r01/correct-ops-context-20261119
git push --force-with-lease=refs/heads/r01/ops-sync-20261119:dc2b55d477a5a2a8b6c4cc0af23694cd33a0b2e1 origin :refs/heads/r01/ops-sync-20261119
git push --force-with-lease=refs/heads/r01/planning-design-information-model-20261119:d582a84e4f8c22ff3ca36acd6381d2d9132c4230 origin :refs/heads/r01/planning-design-information-model-20261119
git push --force-with-lease=refs/heads/r01/step1-step2-submission-drafts-20261119:161e75aa59d2511c297a7912b7f5ec1a13fa0e63 origin :refs/heads/r01/step1-step2-submission-drafts-20261119
```

B는 아래 원격 태그 생성·검증에 성공한 경우에만 별도 삭제 명령을 실행한다.

```powershell
git tag archive/r01-lesson-design-kickoff-20261123 dba2f5dc97a4c8a61d523831a51f6f30b1936efb
git push origin refs/tags/archive/r01-lesson-design-kickoff-20261123
git ls-remote origin refs/tags/archive/r01-lesson-design-kickoff-20261123
git tag archive/r01-lesson-mvp-workspace-20261124 aa9a9092da5e0c8a6ed9565e8836b060e313f094
git push origin refs/tags/archive/r01-lesson-mvp-workspace-20261124
git ls-remote origin refs/tags/archive/r01-lesson-mvp-workspace-20261124
```

```powershell
# 위 원격 태그 SHA가 각 기록 HEAD와 일치할 때만 실행
git push --force-with-lease=refs/heads/r01/lesson-design-kickoff-20261123:dba2f5dc97a4c8a61d523831a51f6f30b1936efb origin :refs/heads/r01/lesson-design-kickoff-20261123
git push --force-with-lease=refs/heads/r01/lesson-mvp-workspace-20261124:aa9a9092da5e0c8a6ed9565e8836b060e313f094 origin :refs/heads/r01/lesson-mvp-workspace-20261124
```

삭제 후 `git ls-remote --heads origin "refs/heads/r01/*"` 및 GitHub 브랜치 목록으로 확인하고 결과를 이 기록에 남긴다. 태그 생성 또는 삭제 실패는 미실행/실패로 구분한다. 다른 브랜치를 변경하지 않는다.
