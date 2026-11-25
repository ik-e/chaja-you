# OpenAI API PREP 실험 환경 · TASK-049 / TASK-048

[사용자 방향](../../../docs/human/responses/HRESP-20261125-07_openai-model-experiment-direction.md) · [담당 PLAN](../tests/modules/preparation/PLAN.md).

상태: 공급자 방향 확정, API 계정·결제·키·비용 한도 미설정, 실제 유료 호출 미실행. R01 제안: 별도 API project `chaja-you-prep-exp`, 초기 USD 10 (승인 전).

1. 조직 Owner가 https://platform.openai.com/settings/organization/projects 에서 전용 프로젝트 생성. R02를 Organization Reader + 프로젝트 Member로 초대; Default project/Owner 권한 부여 금지. R02 개인별 제한 API key 발급, 팀장 키 공유 금지.
2. 예산 승인 뒤 Limits에서 spend enforcement 및 50/80/100% 알림, 허용 모델/요청 한도 설정. 집계 지연으로 소폭 초과 가능; 실행기 호출·출력·재시도 제한 병행. 공식 도움말 https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform .
3. R02는 로컬 OS 보안 저장소/환경변수 OPENAI_API_KEY로 주입. 키를 Git/Discord/chat/log/fixture/CI artifact에 기록하지 않는다. 필요한 SDK 버전, timeout/retry 및 최소 테스트는 R02 제안 후 R01 공통 lock 검증. 현재 SDK 추가/lock 변경 없음. 기본 CI는 키 없이 fake; 실제 호출은 별도 명시적 local opt-in.
4. Extractor 주입 경계 유지. 합성 사례, 최대 호출 수, 입출력 토큰·재시도 상한, 단가 근거와 비용 추정 기록. 저비용 후보부터 시험; 허용 범위 초과 시 중단. 실제 모델/버전은 접근 가능성과 시험 결과로 선정.
5. 동일 입력에서 원문·근거 일치, 가격·단위·VAT·충돌 보존, 필수 프로필/스키마, 정상 완료, 오류/timeout 평가. 근거 충분한 값의 일괄 최종 검토와 불확실 항목만 질문하는 대안을 비교. AT-01/T5-08/T6-02 및 실제 모델 시험은 fake 결과와 구분.
6. 모델 snapshot, 입력/프롬프트 버전, case ID, usage input/output/cached tokens(가능한 경우), 단가·비용, 호출/재시도/timeout, latency, 품질 pass/fail, 성공 처리 1건당 총 비용 기록. 동일 품질 조건 통과 후보 중 비용 최소화. 재현 명령/설정 예시(키 없음)와 근거 인계.
7. R02/R03 중첩 필드 보존 및 deadline/revision 협의 지속. 12/4 인계는 목표 후보. 운영용 API 프로젝트/service account는 배포 단계 별도.

이 문서는 유료 호출이나 실제 플랫폼 및 사용자 정보 전송을 승인하지 않는다.
