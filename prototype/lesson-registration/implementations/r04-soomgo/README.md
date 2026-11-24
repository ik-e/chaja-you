> **이전 배정 공간 — 신규 실행 지시 아님.** TASK-044는 2026-11-24 실제 작업으로 개정되었다. [실제 작업 공간](https://github.com/ik-e/chaja-you/tree/926b5de767/docs/members/R04/workspace) · [이전 원문](https://github.com/ik-e/chaja-you/blob/b46200de40f0290bc1ab2c06ab8a5f9a62c73a2e/prototype/lesson-registration/implementations/r04-soomgo/README.md). 기존 미충족 범위는 정본 TASK의 개정 이력에서 확인한다. 파일·브랜치는 삭제하지 않았다.

# R04 · 숨고 독립 등록 기능 PoC (TASK-044)

**최초 조사 질문:** 숨고 고수 프로필, 서비스 등록, 포트폴리오, 견적 중 현재 '신규 등록'에 해당하는 실제 객체와 업무 완료의 의미는 무엇인가? 크몽 상품 등록의 복제라는 가정은 금지.

1. **design.md 작성:** 조사된 공식 등록 경로와 관측일/근거, 선행 가입·인증, 입력 항목/이미지, 사람 승인/허용 경계, 완료/실패/미확인, 도구 선택 근거.
2. **독립 실행 코드:** 선정한 최소 객체 한 건을 가상 정보로 준비→승인→R03 mock에서 필드/이미지 처리→모의 상태 표시.
3. **검증:** 정상·필수 누락·미승인·unknown 4종, 실행 명령/실제 로그.
4. **결과 제출:** 구현 가능/미검증/정책 보류를 구분하고 크몽 작업 공간을 수정하지 않는다.

**제외:** 크몽 코드 재사용을 전제로 설계, 실제 숨고 계정 로그인·자동 등록·견적 전송, 비밀번호/OTP/세션 수집.

[공통 모의 환경](../../test-harness/README.md) · [TASK-044](../../../../docs/artifacts/tasks/TASK-044.json). **현재 코드 미구현.**

## 작업 시작 및 격리

- 전용 브랜치: `r04/task-044-soomgo-registration`
- 담당 디렉터리: `prototype/lesson-registration/implementations/r04-soomgo/`
- [공통 작업 공간](../../README.md)의 실행 환경·제품 승격 기준을 따른다. 새 의존성/lock은 이 디렉터리 안에서만 관리한다.
- [공통 모의 계약](../../test-harness/CONTRACT.md)을 읽고 R03이 공유한 고정 commit의 mock을 별도 worktree에서 사용한다. 독립 착수 가능, 공통 검증 전 통과 주장 금지.
