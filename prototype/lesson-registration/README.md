# 레슨 등록 플랫폼별 독립 실험 작업 공간

**적용 단계:** [PHASE-20261124-02](../../docs/human/phase-intents/PHASE-20261124-02.md) · [작업 계약](../../docs/artifacts/design/lesson-registration-20261124/PLATFORM-INDEPENDENT-WORK.md)

- R03 [공통 테스트 하네스](test-harness/README.md): 크몽·숨고 모의 양식/오류/합성 입력과 테스트 재현.
- R04 [숨고 독립 구현](implementations/r04-soomgo/README.md): 숨고 등록 객체 조사 후 최소 실행 코드.
- R05 [크몽 독립 구현](implementations/r05-kmong/README.md): 크몽 레슨 상품 등록 최소 실행 코드.

세 공간은 서로의 구현 구조를 강제하지 않는다. **실제 플랫폼에서 계정 로그인/제출/등록 테스트는 허용 검증 전까지 수행하지 않는다.** 현재는 공간 및 TASK 배정만 완료, 코드/테스트 실행 결과는 없다. 
