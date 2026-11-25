# 제품 작업 지침 (사람/AI 공통)
상위 AGENTS.md와 CURRENT, 활성 Phase, 본인 TASK를 먼저 확인한다. WORKSPACE.json에서 package ID·owner·paths·acceptance를 읽고 고정 설계 원본을 확인한다. 후보 상태는 배정이 아니다.
작업 시작: 승인된 기준 커밋에서 자기 브랜치 checkout; python dev.py doctor; python dev.py test <package>. 자신의 PLAN.md에 목적, 세부 설계, 대안/근거, 작은 구현 순서·검증·완료 조건을 기록한다. 국소 결정은 담당자 자율. 공통 계약/의존성/다른 영역 변경은 영향과 대안을 R01에게 제시한다.
R01은 계약·통합만 담당, 플랫폼 구현 금지. 실제 플랫폼 로그인/등록·자격증명 금지. 합성 replay 결과는 실제 구현 통과가 아니다. 결과에는 명령, commit, 입력, 기대/관측, pass/fail/incomplete를 기록. AI는 미배정 TASK를 활성화하지 않는다.
