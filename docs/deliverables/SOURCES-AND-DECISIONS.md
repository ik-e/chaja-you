# 조사 근거와 결정 적용 기준

**확인 기준일: 2026-11-18.** 이번 체계는 공식 강사 자료의 제출 요구와 소프트웨어·AI 문서화 표준을 서로 다른 **권위 계층**으로 사용합니다. 아래 웹 링크는 공개된 초록/문서 수준의 관찰입니다. 유료 표준 본문 전체를 열람하거나 팀이 인증받았다는 의미는 아닙니다.

## 1. 적용 우선순위

1. 강사/매니저의 **최신 실제 산출물 양식·제출 규칙** (불확실하면 확인 과제로 남김)
2. 강사 대시보드의 현재 산출물·마감·제출/접수 상태 (비공개 URL을 공개 저장소에 복제하지 않음)
3. 교육용 예시의 목차·표·다이어그램 (샘플의 가상 구현·시험 내용은 필수 사항 아님)
4. ISO/IEEE·OWASP·NIST·OpenAPI·JSON Schema 등 **목적별 외부 품질 근거** (강사 필수 형식을 대체하지 않음)
5. 팀 자체 운영 기본값과 생성 규칙 (변경 가능)

## 2. 확인한 핵심 자료

| 자료 | 직접 확인된 적용 가능한 사실 | 적용하면 안 되는 해석 |
| --- | --- | --- |
| [OUTPUT-GUIDE.md](https://gt.isitsoft.kr/publicproj/aio-01d4-stu/src/branch/main/Lecture/FinalProject/OUTPUT-GUIDE.md) · [팀 적용 확인](../guidelines/2026-11-16_OUTPUT-GUIDE_적용확인.md) | 제공된 목차 준수, 열람권한, 대시보드 등록, 미구현·미결정 구분 | 임의 목차가 곧 공식 목차 |
| 강사 대시보드 '1팀' 산출물 25~41행, 11/18 확인 | DLV-01~16 이름·기한·당시 상태가 존재 | 이후 일정/결과가 불변 |
| 강사 공유 Google Docs `최종프로젝트_주요산출물(예시)`, 11/18 확인 | DLV-01~12의 교육용 예시 구조와 가상 시험·구현 사례 | 특정 FR/기술/가상 통과값의 채택 |
| [ISO/IEC/IEEE 15289:2019](https://www.iso.org/standard/74909.html) | 소프트웨어 생명주기 정보 항목의 목적과 내용·문서 유형에 초점 | 16개 목차를 그대로 지정 |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | 요구사항 활동과 산출 정보 항목·형식 가이드 | 우리 FR/NFR 수와 기술 선택 의무화 |
| [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) | 아키텍처 기술의 구조·관점·표현 | 모든 제품에서 동일한 다이어그램 필수 |
| [ISO/IEC/IEEE 29119-3:2021](https://www.iso.org/standard/79429.html) | 테스트 문서 템플릿과 테스트 프로세스 산출물 구분 | 수행되지 않은 시험 결과 채우기 |
| [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | 소프트웨어 품질 특성의 참조 모델 | 모든 품질 특성을 8주 내 전수 시험 |
| [arc42 문서화 접근](https://arc42.org/documentation/) | 역할·목적에 맞게 유지 가능한 아키텍처 지식 구조 | arc42의 모든 장을 작성 의무화 |
| [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html) / [JSON Schema 2020-12](https://json-schema.org/specification) | HTTP API/구조화 데이터의 기계 검사 가능한 계약 | HTTP API 또는 JSON 방식의 채택 지시 |
| [NIST GAI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) / [OWASP LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | 생성형 AI 위험 및 과도한 도구 권한 통제 위험 | 모든 보안 요구가 확인·구현되었다는 주장 |
| [OpenAI Eval 권고](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | 실제 과제·데이터·실행·평가 피드백을 연결하는 방식 | 단일 모델 점수를 사용자 가치 근거로 사용 |
| [OpenAI Harness Engineering 사례](https://openai.com/index/harness-engineering/) | AI 실행을 위한 저장소의 명료성·검사·피드백 루프 실무 사례 | 동일 구현 인력·속도·결과를 보장 |

### 근거 주장별 강도

- **높음:** 대시보드에 16개 제출 항목이 있다는 것(2026-11-18 관측). ISO 표준 제목·공식 초록의 명시 범위. 공유 예시 문서에 실제로 적힌 제목들.
- **중간:** 8주 프로젝트에서 작업 정본과 제출 프로젝션을 분리하는 것이 효율적이라는 설계 판단. 위 근거에 부합하지만 팀의 시간 절감이 아직 계량되지 않음.
- **미확인:** 16개 전부의 공식 필수 목차·별도 WBS 제출 방식·실제 강사 합격 판정, 향후 선정 제품의 기술 스택/성능.

**정보 불확실성의 파급 범위:** 예시만 확보한 항목에 `official_outline_status = not_yet_verified`를 설정합니다. 임의 목차를 최종으로 승격하지 않고, 공식 양식 확보와 [공식 목차 대조](official-outline-template.json) 후 단계별 문서 템플릿을 확정합니다.

## 3. R01/AI 운영 결정의 상태

- 현재 본 설계는 **팀장에게 제안된 작업용 정보 체계**이며, 실제 프로젝트 제품 주제나 구현 기술을 확정하는 새로운 ADR은 아닙니다.
- 작업용 정보 모델을 채택하는 경우에도 기존 [Phase Intent](../human/phase-intents/PHASE-20261118-01.md)와 기존 TASK 정본을 변경하지 않습니다.
- 내용·예시·출처가 바뀌면 기준 출처/버전/검증 결과를 기록하고 결정은 별도 사람 판단으로 승격합니다.
