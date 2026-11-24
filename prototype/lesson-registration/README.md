# 레슨 등록 MVP 코드·테스트 작업 공간 (초안)

**상태:** 2026-11-24 R01 준비 브랜치. **코드 구현·실행·업무 배정 미착수.** 현재 Phase Intent의 설계·PoC 보류를 해제하는 R01 공식 결정 이전에는 코드 실행을 승인된 제품 작업으로 간주하지 않는다.

- 제품 기준: [기획안 V1.1](../../docs/artifacts/planning/lesson-registration-20261123/proposal-v1.1.md)
- 필수 선행: [MVP 최소 설계 V0.1](../../docs/artifacts/design/lesson-registration-20261123/MVP-MINIMUM-DESIGN-V0.1.md)
- 팀 작업 계약 초안: [MVP-WORK-PACKAGES](../../docs/artifacts/design/lesson-registration-20261123/MVP-WORK-PACKAGES-20261124.md)
- 현재 적용 단계: [PHASE-20261123-01](../../docs/human/phase-intents/PHASE-20261123-01.md)
- 기존 설계 방법: [L0~L7](../../docs/deliverables/PLANNING-DESIGN-INFO-MODEL.md)

## 이 공간에서 만들 것

실제 크몽 계정 없이 **합성 레슨 1건을 입력→사실 검증→사용자 승인→모의 입력·이미지 첨부→결과 상태 확인**하는 수직 MVP. 모의 폼은 확인 가능한 최소 필드·업로드·오류만 구현하며 실제 크몽 페이지를 복제하거나 자동 접수하지 않는다.

| 공간 | 제안 책임 | 실제 코드가 들어갈 내용 | 다른 담당자에게 제공할 것 |
| --- | --- | --- | --- |
| [fixtures](fixtures/synthetic-lesson-001.json) | R02 | 합성 입력/정답/오류 데이터 | R03/R05 동일 시험 입력 |
| [contracts](contracts/README.md) | R03(업무 의미)+R05(API) | 합의된 JSON Schema·예제·오류/버전 | UI/Core/Adapter 공통 인터페이스 |
| [core](core/README.md) | R03 | F1 사실 매핑·검증 + F3 상태/재시도 규칙 | 독립 실행 함수·테스트 |
| [ui](ui/README.md) | R04 | 원본 입력, 내용/승인 검토, 실행/결과 표시 | 실제 클릭 시연 |
| [adapters/mock-kmong](adapters/mock-kmong/README.md) | R05 | 모의 폼/업로드/결과 이벤트, 백엔드 연결 | mock 실행 로그·증거 |
| [tests](tests/README.md) | R03/R05, R01 인수 | 정상·누락·버전충돌·업로드 실패·unknown | 재현 명령·PASS/FAIL 증거 |

## 개발 순서와 공통 약속

1. **먼저:** R01의 범위/착수 승인 → R03·R05의 공유 데이터·상태 계약 V0.1 → R04 화면 입력/결과 확인.
2. **그다음:** 각 담당 폴더에서 최소 구현, 합성 fixture로 단위·계약 시험. 기술 스택은 R05 근거 검토 후 선택, 현재 Python/React/Playwright 의존성은 새로 추가하지 않는다.
3. **통합:** mock에서 C01~C07을 재현, 결과·에러·증거 참조를 별도로 남긴다. 실제 사이트에서 로그인/제출/자동 게시하지 않는다.
4. **작업 방식:** 담당별 TASK 브랜치에서 코드·테스트 작성, 연관 담당 검토 후 통합 브랜치/PR, 이후 main 통합 여부 결정. 같은 공통 계약 파일을 여러 명이 동시에 직접 수정하지 않는다.
5. **기록:** GitHub에는 코드/불변식/재현 가능한 test fixture·명령만; 비밀번호·쿠키·실제 개인자료·임시 세션은 넣지 않는다. 수행하지 않은 테스트를 완료로 표시하지 않는다.

이 README는 공간과 경계를 안내한다. **제품 채택/실행 승인 문서가 아니며**, 실제 설계·코드 생성 후 현재 상태와 어긋나면 함께 갱신한다.
