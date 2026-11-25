# 원격 인증 세션 보안 경계 · TASK-048 / D04

상태: R01 수용 방향의 검증 후보. Mock-only. 실제 계정, 사이트, 자격증명 처리 승인 아님.

## 보호 대상과 위협

인증된 원격 브라우저 자체가 자격증명에 준하는 capability이다. 직접 로그인도 서버가 일시적으로 키 입력·화면·쿠키·스토리지에 접근할 수 있으므로 "비밀번호 저장 안 함"은 충분한 보안 근거가 아니다. 서버/브라우저 침해, 세션 탈취, cross-owner/CSRF/WS hijack, 악성 navigation/SSRF, 프레임/입력/trace 유출, 세션 잔존을 고려한다.

| 경계 | 필수 후보 통제 | 검증 |
| --- | --- | --- |
| 서비스 identity | 서버 세션에서 owner 도출; H1~H9 및 WS owner/registration 확인; test header는 독립 test 전용. HTTPS/WSS, secure HttpOnly SameSite cookie 및 CSRF/Origin 검증 | 타 owner, origin, 만료·변조·재사용 거절 |
| Viewer | random opaque single-use attach grant; digest만 저장; owner/registration/generation/expiry 결합, 인증된 동일 origin WS 첫 메시지, grant를 URL/로그에 두지 않음. attach 전에 어떤 frame/input도 없음. refresh/재접속은 H6으로 grant 교체, 기존 연결 입력 즉시 차단. 제한된 pointer/key/text/scroll만, 크기/빈도/queue 제한, 임의 CDP/스크립트/clipboard export 금지 | 동일 grant 2회, stale/foreign, wrong origin, finish와 대기 입력 경합 |
| H6 finish / H7 start | finish가 input gate를 먼저 닫고 대기 입력 폐기·진행 입력 종료 후 trusted identity/target 확인. Viewer grant와 verified binding 별도. H7에서 current binding·scope 검증, worker 독점 claim/lease 및 operation permit; 임의 URL/동작 금지 | same account other connection, worker/observer 위조, fence race |
| 세션 격리 | mock은 등록별 BrowserContext, 별도 page/CDP/queue, service worker 차단 및 synthetic origin allowlist. BrowserContext는 OS/프로세스 보안 경계 아님. 실제 운영 후보는 사용자별 격리 process/container, 최소 권한, browser sandbox, 임시 profile/메모리·자원 제한; CDP 로컬 비공개; 네트워크 egress allowlist, redirect/subresource/WebSocket/DNS/사설 주소/metadata 접근 통제 | 합성 context 쿠키/storage 분리, 비허용 loopback 차단; 실제 OS/egress/침해 시험은 별도 |
| 데이터 최소화 | 로그인/인증 화면 recording/screenshot/trace/video 금지, input 원문/쿠키/token/authorization/query/비밀/프레임 저장 및 로그 금지. 로그인 이후도 민감 정보 마스킹·최소 결과 증거만. 세션 state export/download/storage_state 파일·재사용 금지. 임시 자원 접근 최소화. 감사는 이벤트 종류, 시간, opaque registration/owner, 성공·실패 code만; payload/exception dump 금지 | synthetic log inspection; actual logging/telemetry/crash dump retention audit pending |
| 수명/폐기 | grant TTL은 인증 session 수명과 독립; detach는 UI 연결만 해제. prestart idle/absolute timeout, finish/close/refresh 규칙, accepted job bounded runtime; 상태 손실·세션 만료 시 fence/unknown, 재로그인/재bind/자동재실행 금지. terminal/timeout/shutdown에서 page/CDP/context/queue/temp data 폐기; 재시작 시 orphan fence. 실제 계정 로그아웃/서버 토큰 만료는 플랫폼 지원에 따라 별도 검증; context.close가 원격 토큰 무효화라고 주장하지 않음 | teardown 후 old context 불가, 새 context empty; real shutdown/session revoke tests pending |

## 운영 출시 전 별도 gate (현재 mock 수용 gate 22개 변경 없음)

실사용은 명시적 사용자 동의(어떤 플랫폼·동작·수명·위험인지), 운영사 허용 및 필요한 법적/개인정보 검토, 실제 HTTPS/WSS/서비스 인증·격리·egress·감사·삭제·사고 대응, 부하/장애/침투 검증이 모두 별도로 필요하다. OAuth/공식 API 및 최소 scope 위임이 제공되면 실제 브라우저 로그인 세션 위임보다 우선 검토한다. 기본은 사용자 직접 로그인·MFA, 자동 비밀번호 수집/저장·CAPTCHA 우회 금지. 실제 서비스의 권한은 본 mock 단계에서 취득하지 않는다. 사고시 해당 세션/권한 폐기, 플랫폼 logout/revoke 가능성 확인, 영향 평가 및 필요한 통지. 권한 유지 시간·용량·동시 세션·보존 기간은 측정 및 정책 근거로 결정한다.

## 반환

R03: service identity, H6/H7 상태·권한 검사, STORE/worker 및 secret 없는 오류. R04: owner-bound UI, grant 메모리만, detach와 finish 분리. R05: browser/transport/isolated context/allowlist, input gate, session cleanup 및 로그. R01: cross-boundary tests, exact candidate/CI evidence and rollout gate. 책임은 기존 TASK 내. 실제 provider 연동 및 보안 적합 판정 전 운영 금지.
