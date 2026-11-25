# AI 보안 가드레일 설계 문서 · 레슨 등록 지원

> DLV-08 · 12/18 제출 예정 · 2026-11-25 현재 설계 초안. 현행 mock-only 가드와 [PR #44 보안 후보](https://github.com/ik-e/chaja-you/blob/24a1c3579e84ae6a8e76e4b78135288babc5f51b/product/lesson-registration/contracts/SESSION-SECURITY.md)를 구분한다. 실제 사용자 인증·운영 보안 승인 또는 적합 판정 아님.

[공통 V1](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [V4.1](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · [시스템 구조](../design/lesson-registration/SYSTEM-OVERVIEW.md) · [강사 AI 안전 가이드](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/CodingAgent/AI에이전트_절대하면안되는10가지.html) · [R01 운영 방향](../human/responses/HRESP-20261125-06_pain-first-rolling-plan.md).

## 1. 보호 대상 및 신뢰 경계

보호 대상은 사용자 원본·첨부·개인정보·승인 Scope·등록 대상·인증된 원격 브라우저·관측 근거. 사용자 입력/첨부/페이지/모델 출력은 신뢰되지 않는 데이터이며 권한 부여의 근거가 아니다. 서비스 owner 인증, human Viewer Grant, 내부 verified ConnectionBinding 및 worker/operation 실행 권한을 분리한다. 외부 플랫폼 인증 세션은 자격증명 수준으로 다룬다. mock은 합성 계정/사이트만.

## 2. 위협과 통제

| 위협 | 현행 가드 / 후보 보완 | 검증 |
| --- | --- | --- |
| 프롬프트 인젝션·허위 사실 | 원문/도구 결과와 지시 분리, profile/근거 검증, 누락은 질문. PREP에 실행 권한 없음 | 합성 악성 문구/누락/가격 충돌, T5-08 실제 모델 |
| 타 사용자 데이터/세션 | 서버 owner와 등록·대상 확인, 외부 계정 별도, opaque binding. grant owner/reg/generation/expiry 및 단일 사용은 D04 후보 | 타 owner 404, 다른 계정/세대 거절, WS 재사용/Origin 실제 시험 |
| 과도한 권한·승인 위조 | H7 정확한 review/revision/target/connection/permission, 등록 operation 및 durable 예약, 원시 브라우저 명령 금지. claim/permit 세부 D02 후보 | 위조·경쟁·중복·fence |
| 인증 쿠키·입력·화면 유출 | 비밀/로그인 입력/화면 기록·state export 금지, credential 외부 반환 금지. 로그 최소화와 폐기 정책 D04 후보 | 합성 secret 검사, 실제 WS/log/trace/temp 감사 미실행 |
| 네트워크/외부 수집 | mock registry 및 허용 목적지만, 임의 URL/실제 사이트 차단. 실운영 egress·redirect/DNS·사설주소 제어 별도 | loopback 격리 probe, 실제 OS/egress 검증 필요 |
| 오류 후 중복·결과 오판 | 원자 accept/admit/observe/fence/finalize, unknown 보존, 독립 readback·실제 evidence. 자동 재제출 금지 | lost response, stale, 증거 위조, terminal 불변 |
| 사용자 민감정보 출력·저장 | 필요한 최소값·권리 확인 첨부·안전 Error/Result, 내부 binding 비공개, 원본 보존/접근통제 | redaction, 형식·권리·owner 검사 |

## 3. 역할·권한 및 가드 위치

PREP 읽기/후보 생성만; CO 업무 상태/승인; STORE 원자적 권한 검사; EXEC 등록된 동작·관측만; RESULT 읽기/판정만. H6 human 입력 차단 후 인증 연결 확인, H7 승인 뒤에만 자동 실행. H8/H9 저장 조회만. [API](../step2/API_설계_문서.md). 합성 테스트 헤더는 제품 인증 아님. 모델 출력만으로 승인/실행 권한 발급 금지.

## 4. 세션 생명주기와 운영 조건

현재: 등록별 격리 BrowserContext 방향, 원격 직접 인증, 검증된 binding, 만료·종료·장애 시 폐기. D04 후보: same-origin authenticated WS, one-use attach grant 첫 메시지, refresh/finish 입력 권한 폐기, queue 정리, 화면/입력/비밀 로그 금지. R04 iframe/postMessage 제안은 담당 검토 중이며 WS transport와 host/viewer 경계의 구분 및 origin/source 검증 필요. BrowserContext는 OS/프로세스 보안 격리와 같지 않으며 context.close는 플랫폼 발급 token revoke와 다르다.

실제 운영 전 별도: 서비스 사용자 인증/CSRF/HTTPS/WSS, 사용자별 격리 process/container 및 브라우저 sandbox, egress, 접근통제·감사·보존·폐기/침해 대응, 플랫폼 허용/동의/공식 최소 권한 API 검토. 실제 사이트/계정 사용 승인 없음.

## 5. 검증 근거와 잔여 위험

[공통 계약/시험 안내](../design/lesson-registration/VALIDATION.md) · [R03 S8 run](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/artifacts/runs/TASK-050-s8-http-20261125.json) · [PR #44 checks](https://github.com/ik-e/chaja-you/pull/44/checks). R03 합성 HTTP 검증 191개(14 HTTP 포함) 보고는 제품 인증/보안 평가와 다르다. PR #44 CI 4개 통과는 후보 reference 및 합성 브라우저 격리/폐기 등 시험 범위에만 해당하며 main 채택/실제 provider 및 운영 보안 시험이 아니다. 실제 프롬프트 공격·WS·runtime 경계·로그/egress·장애/침투 시험과 제품 gate는 아직 완료되지 않았다. 수치/TTL/retention/실제 서비스 인증 방식은 담당자 검증·별도 정책 후 확정.

## 6. 변경 관리

실제 운영 권한 확대와 안전 조건 변경은 R01 별도 판단. 기술 적용은 핵심 Pain 해결 우선. PR #44와 담당자 피드백 채택 뒤 영향을 받는 항목만 갱신하고 실제 run과 함께 검증 결과를 기록한다. 제출·접수 미확인.
