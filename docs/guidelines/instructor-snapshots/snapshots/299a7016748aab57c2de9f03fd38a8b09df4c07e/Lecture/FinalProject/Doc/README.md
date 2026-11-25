# 최종 프로젝트 공통·단계별 작성 가이드

문서의 주된 사용 단계로 분류했습니다. 다른 단계에서도 필요하면 참고할 수 있으며, 표의 단계가 기술 도입을 그때까지 미루라는 뜻은 아닙니다. PDF와 같은 이름의 HTML을 함께 보관합니다.

| 단계 | PDF | HTML | 주요 내용 |
|---|---|---|---|
| 공통 | [AIO_1기_최종프로젝트_가이드](AIO_1기_최종프로젝트_가이드.pdf) | [열기](AIO_1기_최종프로젝트_가이드.html) | 일정·산출물·평가·팀 운영 |
| 공통 · CodingAgent | [agent-skills-final-project](CodingAgent/agent-skills-final-project.pdf) | [열기](CodingAgent/agent-skills-final-project.html) | 모든 단계의 AI 코딩 계획·검증·리뷰 |
| 공통 · CodingAgent | [AI 에이전트에게 절대 하면 안 되는 10가지](CodingAgent/AI에이전트_절대하면안되는10가지.pdf) | [열기](CodingAgent/AI에이전트_절대하면안되는10가지.html) | 최소 권한·외부 입력·키·승인·격리·검증·모니터링 |
| STEP1 | [AIO_1기_1주차_킥오프](Step1/AIO_1기_1주차_킥오프.pdf) | [열기](Step1/AIO_1기_1주차_킥오프.html) | 팀 구성·주제 선정·기획 시작 |
| STEP1 | [기획서_잘_쓰는_법](Step1/기획서_잘_쓰는_법.pdf) | [열기](Step1/기획서_잘_쓰는_법.html) | 사용자 문제·범위·요구사항·검증 |
| STEP1 | [WBS_잘_쓰는_법](Step1/WBS_잘_쓰는_법.pdf) | [열기](Step1/WBS_잘_쓰는_법.html) | 작업 분해·완료 기준·일정·담당 |
| STEP2 | [API설계문서_작성법](Step2/API설계문서_작성법.pdf) | [열기](Step2/API설계문서_작성법.html) | API·Tool 계약·검증·권한·실패 처리 |
| STEP2 | [DB스키마설계서_작성법](Step2/DB스키마설계서_작성법.pdf) | [열기](Step2/DB스키마설계서_작성법.html) | 관계·컬럼·권한·저장 규칙 |
| STEP2 → STEP3 | [최종프로젝트_API서버_백그라운드워커_구조](Step2/최종프로젝트_API서버_백그라운드워커_구조.pdf) | [열기](Step2/최종프로젝트_API서버_백그라운드워커_구조.html) | 웹·작업 처리의 책임·Job·진행 상태 |
| STEP2 → STEP3 | [설계서 한 줄을 실제 동작으로 연결하기](Step2/DESIGN-TO-WORKING-FLOW.pdf) | [열기](Step2/DESIGN-TO-WORKING-FLOW.html) | 계약·모의 연결·상태·실제 연동·작업 인계·증빙 |
| STEP3 (STEP2·STEP4도 참고) | [모델·도구·서비스 평가와 증빙 남기기](Step3/MODEL-TOOL-SERVICE-EVALUATION.pdf) | [열기](Step3/MODEL-TOOL-SERVICE-EVALUATION.html) | BFCL·자체 문항·여러 단계 실행·비용·평가 기록 |
| STEP3 | [단일 에이전트 상태 전이 그래프 설계서 작성 가이드](Step3/단일에이전트_상태전이그래프_설계서_가이드.pdf) | [열기](Step3/단일에이전트_상태전이그래프_설계서_가이드.html) | 아홉 칸 작성법·전이 완전성·종료 조건·팀 적용 |
| STEP3 | [자기 성찰 로직 테스트 결과서 작성 가이드](Step3/자기성찰_테스트결과서_가이드.pdf) | [열기](Step3/자기성찰_테스트결과서_가이드.html) | 여덟 칸 작성법·초기/탐지/보정/최종 비교·종료·비용·증빙 |
| STEP4 (STEP3 참고) | [멀티에이전트_AutoHealing_적용가이드](Step4/멀티에이전트_AutoHealing_적용가이드.pdf) | [열기](Step4/멀티에이전트_AutoHealing_적용가이드.html) | 협업·자기 성찰·복구 개념과 적용 |
| STEP5 (조기 배포 시 참고) | [최종프로젝트_CICD_따라가기](Step5/최종프로젝트_CICD_따라가기.pdf) | [열기](Step5/최종프로젝트_CICD_따라가기.html) | CI/CD 실행·배포·실패 복귀 |

## 분류 기준

- 전체 프로젝트 가이드는 이 폴더 바로 아래에 둡니다. 코딩 에이전트 활용·안전 자료는 단계 공통의 CodingAgent 폴더에 둡니다.
- 킥오프·기획서·WBS는 Step1, API·DB 및 API 서버·워커 기초 구조는 Step2에 둡니다.
- 멀티에이전트·Auto-Healing 적용 가이드는 주된 목적이 협업·복구이므로 Step4에 둡니다. 자기 성찰·단일 에이전트 개발을 하는 Step3에서도 관련 부분을 읽습니다.
- CI/CD 따라가기는 Step5에 둡니다. 팀이 일찍 배포를 시작한다면 그 시점부터 참고합니다.
- Step3에는 모델·도구·서비스 평가와 증빙 안내를 둡니다. 설계에서 동작으로 연결하는 Step2 실습 자료를 함께 활용합니다.
- Template은 단계별 강의 자료와 별개로 유지합니다.

가이드의 예시·권장 구성과 필수 제출 요구사항은 구분하고, 최신 매니저 안내와 팀의 채택 범위를 함께 확인해 주세요.
