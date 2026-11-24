# 레슨 등록 설계 — R01 재설계 기준선

2026-11-25: 상위 논리적 데이터 계약 합의 완료. 팀원 조사 원문을 기반으로 상세 공통 계약 V4 및 플랫폼별 모의 프로필 V2를 결정하고 선정된 설계 검증을 수행했다. **실제 플랫폼 실행·제품 통합·구현 기술 확정은 별도.**

## 현재 기준선

| 구분 | 문서 | 상태 |
|---|---|---|
| 최상위 설계 | [최상위 합의](top-design-v1.json), [상위 보완](top-design-amendment-v1.json) | 합의 |
| 논리 및 상세 결정 | [D1~D8](detail-decisions-v2.json), [논리 모델 V5](logical-behavior-v5.json) | 상위 방향 합의, 논리 모델 검증 |
| 상위 논리적 데이터 계약 | [결정 정본](logical-data-contract-decision-v1.json), [설계 보고 V2](DETAIL-DESIGN-V2.md) | 합의 완료·동결 |
| 상세 공통 계약 | [계약 V4](data-contract-v4.json), [스키마 V4](data-schema-v4.json), [설계 보고 V4](DATA-CONTRACT-V4.md) | 위임 결정·선정된 설계 사례 검증 |
| 플랫폼별 계약 | [프로필 V2](platform-profiles-v2.json) | 모의 기준선; 실제 규칙 및 허용 미확인 |
| 인터페이스/API | V4 계약의 wire_compatibility; [V3 후보](interface-contract-v3.json) | 기존 경계 유지, V4 우선, 구현 연계 검증 필요 |
| 검증 근거 | [V4 검증](data-contract-validation-v4.json), [실행 코드](validate-data-contract-v4.mjs), [이전 V3 결함](interface-review-evidence-v3.json) | 합성 31/31; 실제 통합 미검증 |
| 구현/통합 | 기존 독립 TASK 및 phase 유지 | 후속 결정, mock-only |

V4와 상충하는 V2/V3 상세 후보 및 플랫폼 프로필 V1은 역사적 자료다. [V2 상세 후보](detail-contract-v2.json), [V3 스키마](interface-schema-v3.json), [V1 상세 이력](DETAIL-DESIGN-V1.md), [V4 논리 이력](logical-behavior-v4.json). 기존 팀원 작업 및 공통 하네스 계약 변경 없음.

---

# 레슨 등록 설계 · V0.8 보완 기준선 후보

> 2026-11-24 · R01. V0.1은 보존, V0.2는 팀원 조사·모의 실험 근거를 연결한 추가 상세 설계 후보. 최종 채택/본 구현/실서비스 실행/신규 TASK 승인 아님. 현 PHASE 및 R03~R05 공통 시험 계약 변경 없음.

## 최신 V0.8 (V0.7 검토 결함 보완)

- [설계 상태·보완·위임·종료 기준](DESIGN-STATUS-V0.8.md)
- [추가 검증 코드](validate-closure-v0.8.mjs) · [실행 코드](run-closure-v0.8.mjs) · [실행 증거](validation-closure-v0.8.json)
- 기존 JSON 원본 경로에서 revision *-v08을 사용하며, 이전 내용은 Git 이력에 보존. 이하 V0.3~0.5 Markdown은 당시 버전 설명; 충돌 시 최신 JSON과 V0.8 상태 보고가 우선한다.
- 제품 실행/정식 TASK 변경/실제 플랫폼 접근 승인 없음.

## 이전 V0.5 (V0.4 결함 10개 보완)

- [공통 계약·데이터·API·포트·UI·검토 보완](CONTRACT-V0.5.md) · [구조화 원본](contract-v0.5.json)
- [점진 통합 및 AI 책임 WBS](WBS-V0.5.md) · [구조화 원본](wbs-v0.5.json)
- [정적 25/25 및 추상 31/31 검사](validation-v0.5.json) · [재현 코드](validate-v0.5.mjs)

V0.5는 명시적으로 교정한 계약만 대체하고 V0.3/V0.4와 기존 방향을 보존. 상위 방향 확정, 세부 설계/일정/담당 검토 후보. 구현 및 실제 운영 승인 아님. 주말/공휴일과 R02 가용 제외 유지, R02 AI 책임 제안과 11/30부터 단계별 통합. 기존 TASK/PHASE/main 변경 없음. 정적/추상 검증과 제품 시험은 별개.

## V0.4 상위 방향 결정 (2026-11-24)

[결정 내용 및 목표](DIRECTION-V0.4.md) · [구조화 원본](direction-v0.4.json)

- 서버 원격 브라우저 채택, 세부 기술은 구현자 선택. R05 PoC는 근거이며 특정 스택 강제 없음.
- 2026-12-08 MVP: 크몽 우선, 숨고 확장, 최초 등록 정상 동작.
- 2027-01-04 최종 목표: 사용자가 URL로 지정한 등록 가능한 플랫폼에서 필요한 정보와 인증이 갖춰지면 최초 등록 수행 및 결과 확인. 임의 신규 사이트 자동 적응을 필수화하지 않음.
- V0.3 논리 계약 유지. 상위 방향은 결정되었으며 상세 수용 기준·물리 설계·WBS는 아래 기준선 후보, 실제 실행 허용은 별도. 현 단계 mock-only 유지.

## V0.4 본 구현 기준선 후보

- [구현 기준·요구사항·컴포넌트·포트](IMPLEMENTATION-V0.4.md) · [구조화 원본](implementation-v0.4.json)
- [물리 데이터·HTTP·UI·통합](PHYSICAL-V0.4.md) · [구조화 원본](physical-v0.4.json)
- [WBS·일정·수용 시험](WBS-V0.4.md) · [구조화 원본](wbs-v0.4.json)
- [정적 검증 26/26](validation-v0.4.json) · [재현 코드](validate-v0.4.mjs)

주말 및 2026-12-25·2027-01-01 공휴일 제외. 전체 27근무일, MVP까지 10근무일. R02 12/6~22 가용 제외 및 12/3 인계 목표(12/4 최종 기한) 반영. 일정·역할은 검토 제안이며 TASK 배정 전. V0.3 논리 계약 유지, 원격 기술 선택 위임. 실제 실행 금지 단계 유지. 설계 정적 검증과 제품 시험은 별개.

## V0.3 논리 계약 (검토 후보)

| 문서 | 구조화 원본 |
| --- | --- |
| [정합성 개선 계약](CONTRACTS-V0.3.md) | [core-contract-v0.3.json](core-contract-v0.3.json) |
| [논리 데이터·API](DATA-API-V0.3.md) | [data-api-v0.3.json](data-api-v0.3.json) |
| [결함·검증·결정](REVIEW-DECISIONS-V0.3.md) | [review-v0.3.json](review-v0.3.json) |

정적 검사 13/13, 추상 모델 54/54 통과: [결과](validation-v0.3.json) · [재현](validate-v0.3.mjs). 실제 제품 실행 검증 없음. 상위 기획/PHASE 제한을 우선하며, V0.3이 명시적으로 교정한 계약에 한해 이전 세부 설계를 대체. 나머지 V0.1/V0.2 보존. 팀원 TASK/공통 계약/main 변경 없음.

## 이전 V0.1/V0.2 읽는 순서

| 범위 | V0.1 기준선 | V0.2 상세화 |
| --- | --- | --- |
| L2 사용자·FR/NFR | [요구사항](REQUIREMENTS-V0.1.md) | [사용자 흐름·시스템](DETAIL-SYSTEM-V0.2.md) |
| L3/L5 도메인·데이터 | [도메인·흐름](DOMAIN-WORKFLOW-V0.1.md) | [공통 데이터](DETAIL-DATA-V0.2.md) · [플랫폼 흐름](DETAIL-PLATFORM-FLOWS-V0.2.md) |
| L4/L5 실행·인터페이스 | [시스템 계약](SYSTEM-CONTRACTS-V0.1.md) | [책임·UI·API·인증 후보](DETAIL-SYSTEM-V0.2.md) |
| L6 검증·결정 | [검증·결정](VERIFICATION-DECISIONS-V0.1.md) | [근거·시험·게이트](DETAIL-VERIFICATION-V0.2.md) |

V0.1 구조화 원본: [요구](requirements-v0.1.json) · [도메인](domain-workflow-v0.1.json) · [시스템](system-contracts-v0.1.json) · [검증](verification-decisions-v0.1.json). V0.2 [구조화 정본 후보](detail-design-v0.2.json)는 이를 대체하지 않는 overlay이며 4개 Markdown은 동일 데이터에서 생성한 검토 뷰다. 기존 project_docs.py 변경 없음. 불변식/ID 유지; V0.2 후보가 충돌하면 R01 결정 전 기존 제약 우선.

기준: [기획 V1.1](../../planning/lesson-registration-20261123/proposal-v1.1.md) · [설계 순서](../../../deliverables/PROGRESSIVE-DESIGN-ORDER.md) · [현재 단계](../../../human/phase-intents/PHASE-20261124-02.md) · [독립 작업 계약](PLATFORM-INDEPENDENT-WORK.md).

## 근거 스냅샷 (변경 가능한 브랜치 대신 커밋 고정)

| ID | 출처 | 확인 범위 |
| --- | --- | --- |
| S01 | [R01 공통 V0.1](https://github.com/ik-e/chaja-you/blob/88251a3e26ecdf29b60b0737268f96d6e5100f6b/docs/artifacts/design/lesson-registration-20261124/README.md) | 불변식·기존 ID 유지; 설계 초안 |
| S02 | [R01 현재 단계](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/human/phase-intents/PHASE-20261124-02.md) | mock만 허용, 실서비스 금지 |
| S03 | [R02 강사 요구·최신 조건](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R02/workspace/2026-11-23_lesson-pain-priority.md) | 사용자 진술·회상·최신 확인값, 실측 없음 |
| S04 | [R03 개인 PoC 명세](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/SPEC.md) | 크몽형 모의 실험, 고정 fixture |
| S05 | [R03 코드](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/app.py) | FastAPI·SQLite·검증·승인·작업, 개인 코드 |
| S06 | [R03 실행기](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/runner.py) | Skyvern SDK 및 고정 DOM 필드 조작, 새 브라우저 생성 |
| S07 | [R03 검증 기록](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/members/R03/workspace/test/verification.json) | 19 pass 자기 보고, 모의 Skyvern 입력·첨부·영수증; 독립 재실행 아님 |
| S08 | [R04 숨고 업무 흐름](https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24_%EC%88%A8%EA%B3%A0_%EA%B3%A0%EC%88%98%EB%93%B1%EB%A1%9D_%EA%B5%90%EC%9C%A1%EC%8B%A0%EC%B2%AD_%EC%82%AC%EC%9A%A9%EC%9E%90%ED%9D%90%EB%A6%84_%EC%84%9C%EB%B9%84%EC%8A%A4%EC%A0%88%EC%B0%A8_%EC%84%A4%EA%B3%84%EB%B6%84%EC%84%9D%EB%B3%B4%EA%B3%A0%EC%84%9C.md) | 기존 고수 계정 관측 및 제안, 신규 가입·공개 추론 분리 |
| S09 | [R04 화면 보고서](https://github.com/ik-e/chaja-you/blob/926b5de7678f8984be035409d386c6347d749f56/docs/members/R04/workspace/2026-11-24_%EC%88%A8%EA%B3%A0_%EA%B3%A0%EC%88%98%EC%A0%84%ED%99%98_%EB%B0%8F_%EB%93%B1%EB%A1%9D%EC%A0%88%EC%B0%A8_%ED%99%94%EB%A9%B4%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7_%EC%83%81%EC%84%B8%EB%B3%B4%EA%B3%A0%EC%84%9C.md) | STEP 06~12, 15, 16 보고서 관측; 스크린샷 원본 개별 검증 안 함 |
| S10 | [R05 입력 뼈대](https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-24_platform-input-skeleton.md) | 수동 작성 화면·임시저장 보고, 플랫폼별 제약 후보; 실제 자동화 아님 |
| S11 | [R05 기술·권한 조사](https://github.com/ik-e/chaja-you/blob/c5cef60dceb98390b008e7345fc5c0492695e8e3/docs/members/R05/workspace/2026-11-23_lesson-technical-feasibility.md) | 공식/관찰/추정 구분, 운영사 허용 미확인 |
| S12 | [R03 공통 시험 계약](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/prototype/lesson-registration/test-harness/CONTRACT.md) | T1~T6, 변경하지 않음; release 미확인 |
| S13 | [R01 기획 V1.1](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/artifacts/planning/lesson-registration-20261123/proposal-v1.1.md) | 크몽 최초 상품 우선, 숨고 독립 검증 |
| S14 | [R01 작업 범위](https://github.com/ik-e/chaja-you/blob/b220a6e6777928ab81c8a0852608b83f3838ff47/docs/artifacts/design/lesson-registration-20261124/PLATFORM-INDEPENDENT-WORK.md) | R03 공통, R04 숨고, R05 크몽; 현재 분리 |

## 핵심 판단

- 크몽은 상품/심사 접수 후보, 숨고는 서비스 설정 저장 후보, 탈잉은 조사·확장 후보. 모의 결과는 실제 공개가 아니다.
- 최신 강사 확인 조건과 합성 fixture 분리. R03은 개인 PoC 19개 자동 테스트 통과를 보고했으나 공통 TASK-043 완료 증거가 아니다.
- 원격 브라우저 인증·제어권 인계는 합성 실험 후보. 실제 플랫폼 권한, 기술 스택, 물리 API/DB/배포, 운영 비용·보존 기간, 최종 MVP는 미결정.
- V0.2: 157개 상세 항목(표 20개). 생성 과정에서 표 폭·ID·출처·V0.1 명시 참조 검사. 전체 제품/PoC 실행 없음; 정식 스키마 검증/사용자 검토 전.

팀원의 TASK 결과·기획 V1.1·기존 코드·공통 의존성·main은 변경하지 않는다. 11/26 공통 모의 시험과 11/27 R01 결정의 입력으로 사용한다.
