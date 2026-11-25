# 제품 작업 지침 (사람/AI 공통)
상위 AGENTS.md와 CURRENT, 활성 Phase, 본인 TASK를 먼저 확인한다. [현행 AI 설계 인덱스](../../docs/design/lesson-registration/CURRENT-DESIGN.json)에서 적용 계층/결정/근거를 확인한 뒤 WORKSPACE.json에서 package ID·owner·paths·acceptance를 읽고 고정 설계 원본을 확인한다. 현재 배정 TASK와 활성 Phase를 확인한다. 담당자 확인 전 실행 결과를 주장하지 않는다.
작업 시작: 활성화 기준 커밋에서 TASK의 자기 브랜치 checkout; python dev.py doctor; python dev.py test <package>. 자신의 PLAN.md에 목적, 세부 설계, 대안/근거, 작은 구현 순서·검증·완료 조건을 기록한다. 국소 결정은 담당자 자율. 공통 계약/의존성/다른 영역 변경은 영향과 대안을 R01에게 제시한다.
R01은 계약·통합만 담당, 플랫폼 구현 금지. 실제 플랫폼 로그인/등록·자격증명 금지. 합성 replay 결과는 실제 구현 통과가 아니다. 결과에는 명령, commit, 입력, 기대/관측, pass/fail/incomplete를 기록. AI는 미배정 TASK를 활성화하지 않는다.

TASK 결과 정본은 담당자가 별도 문서 갱신으로 관리하며 제품 전용 branch의 check-changes 검사에는 포함하지 않는다.

## 승인된 공통 구현 경계

[공통 구현 계약](contracts/README.md), [구조화 결정](contracts/IMPLEMENTATION-BINDING.json), [검증 근거](evidence/common-contract-ci-20261125.json)를 확인한다. IB-01~05 방향은 R01 승인, 세부 provider/transport/launch/stack은 담당자 확인 후 공통 변경으로 조정. main의 승인된 공통 변경을 자기 브랜치에 병합하고 해당 공통 기준 SHA를 기록하여 `check-changes --base`에 사용한다. 타 담당 영역 변경 및 무단 shared dependency 추가 금지. 10개 공통 시험/72개 합성 payload는 실제 제품 통과가 아니다.

현행 설계 적용 범위와 독립 검증은 [기준선 정책](../../docs/design/lesson-registration/BASELINE-POLICY.md), [검증 안내](../../docs/design/lesson-registration/VALIDATION.md) 참조. 과거 설계는 이력 전용이다.

## 공통 물리 방향 및 갱신
[PD-01~08](contracts/PHYSICAL-BINDING.json)과 [README의 기준선 갱신 절차](README.md#공통-기준선-갱신-확인-2026-11-25)를 확인한다. 방향 채택과 정확한 lock/세부 계약/제품 검증은 구분한다. owner 합의 전 기존 Protocol과 pinned schema를 유지하며 독립 fake로 진행. 적용한 main SHA 및 자신의 검증 결과를 PLAN에 기록한다.
