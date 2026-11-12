# 팀 아이디어 Inbox

이 공간은 R01~R05와 AI가 프로젝트 진행 중 떠오른 **아이디어·가설·대안·개선 제안의 원형을 부담 없이 남기는 공유 입력 공간**입니다.

여기에 기록된 내용은 현재 프로젝트 기준, 승인된 설계, 요구사항, 일정 또는 구현 지시가 아닙니다. 팀원 제안은 제안자의 관찰과 아이디어를 보존하는 입력이며, 필요하면 이후 AI/R01 검토를 거쳐 [Candidate 공간](../artifacts/candidates/README.md)의 구조화 후보로 정리합니다.

## 사용 원칙

- 누구의 아이디어인지 `proposed_by`를 남깁니다.
- 완성된 기획서처럼 만들 필요는 없습니다. 문제, 아이디어, 기대 가치, 우려 정도만 있으면 충분합니다.
- 같은 아이디어가 이미 있어도 덮어쓰지 말고 관련 문서를 연결합니다. 이후 Candidate 정리 단계에서 병합합니다.
- 팀원이 제안했다는 사실만으로 TASK나 설계에 적용하지 않습니다.
- 현재 구현에 즉시 필요한 변경은 Idea가 아니라 해당 TASK/협의/결정 절차를 사용합니다.
- 중요한 장기 의도나 권한 있는 결정은 이 공간이 아니라 `docs/human/`과 ADR에 남깁니다.
- AI는 일반 작업 시작 시 Idea Inbox 전체를 기본 컨텍스트로 읽지 않습니다. 아이데이션·후보 정리·관련 TASK에서 필요할 때만 확인합니다.

## 권장 파일명

`IDEA-YYYYMMDD-Rxx-NN_짧은제목.md`

예: `IDEA-20261113-R03-01_동적역할생성.md`

## 최소 형식

[템플릿](TEMPLATE.md)을 사용합니다.

```text
title
proposed_by
date
context
idea
expected_value
concerns
related_refs
```

## 흐름

```text
Team idea / AI suggestion
        ↓
docs/ideas/  (raw inbox)
        ↓ 필요성·중복·위험 검토
docs/artifacts/candidates/  (curated candidate)
        ↓ 조사·실험·평가
Human decision
        ↓
Design / Spec / ADR / Task / State
```

아이디어가 Candidate로 정리된 뒤에도 원제안은 provenance를 위해 남겨둘 수 있습니다.
