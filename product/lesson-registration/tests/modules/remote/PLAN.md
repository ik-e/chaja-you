# r05-remote PLAN · TASK-053 원격 브라우저 runtime·인증·뷰어

- 담당: R05 (임다혁) · 브랜치: `r05/product-remote` · 기준 커밋: `65aed37` (활성화 커밋)
- 독립 실행: `uv run --locked --python 3.12 python dev.py test r05-remote`
- 고정 설계: `common-integration-v1.json` (state, storage S-ACCEPT~S-FENCE, runtime RT-01~04, VIEWER), `data-schema-v4.1.json` (AuthInput/AuthOutput/AuthGrant, ExecuteInput/ExecutionReport, Operation/Observation), 06-API-PORTS I3·I4·H6
- 상태: 착수. §7 미정 사항은 R01·R03·R04 회신 대기. 브라우저 의존 부분은 의존성 승인 후 진행.

## 1. 목적

사용자가 뷰어로 합성 mock 사이트에 **직접** 로그인한 같은 브라우저 연결을 서버가 이어받아 실행하게 한다.
이를 위해 I3(인증 열기·갱신·완료·닫기)와 I4(실행) facade를 제공한다.
플랫폼 adapter에는 raw driver 대신 좁은 페이지 인터페이스만 주고, 효과가 생길 수 있는 명령은 모두 STORE admission 뒤에만 실행한다.

## 2. 범위

| 포함 | 제외 (다른 담당) |
|---|---|
| I3/I4 facade, RT-01~04 gateway | job 상태 전이, H6/H7 HTTP 핸들러 (r03-app) |
| 세션·연결·grant 세대·worker lease 관리, 세션 격리·폐기 | STORE 실제 저장소·트랜잭션 (r03-app) |
| VIEWER client 계약 `mount(container, grant) -> dispose()`와 전송 | 화면 배치·디자인 (r04-web) |
| STORE 호출(S-ADMIT/S-OBSERVE/S-FENCE) 연결 | 플랫폼별 업무 규칙 (r05-kmong, r04-soomgo) |
| 중립 mock 기준 실제 브라우저 제어·뷰어 분리·응답 유실 시험 | 실제 플랫폼·계정 |

## 3. 세부 결정과 근거

| ID | 결정 | 근거 / 대안 |
|---|---|---|
| R-D01 | 11/24 R05 PoC(`docs/members/R05/workspace/remote-browser-poc/`, Imdahyeok fc59a4b)의 검증된 부분을 **재설계해 이전**: 세션별 BrowserContext, CDP screencast 프레임 중계, 입력 재생, 접속 끊김 후 작업 유지, 키 입력 비기록 감사 로그, 유휴 TTL 정리 | WBS W04 "R05 PoC 재사용 검토". prototype 의존 금지 규칙에 따라 코드 복사가 아니라 계약에 맞춰 다시 작성 |
| R-D02 | adapter에는 `ScopedPage`(goto·fill·attach·submit·view)만 전달. origin은 profile route로 고정, 다른 origin·임의 스크립트·쿠키 접근 없음 | RT-01 "no raw driver or credential to adapter", r05-kmong K-D01과 같은 인터페이스 |
| R-D03 | RT-03 `perform`: registry operation과 정확히 일치 + binding_digest 재계산 일치 → S-ADMIT 영속 → adapter 실행 → S-OBSERVE. unknown 효과 등급은 potential_effect로 취급 | common-integration RT-03 |
| R-D04 | 예기치 않은 오류·unknown 관측이면 S-FENCE 요청, 이후 admission 없음. 자동 재개·재시도 없음 | state invariants "no auto-resume" |
| R-D05 | 인증 연결: `open`은 human 세대 n과 짧은 수명 grant 발급, `refresh`는 grant 회전(이전 grant 무효), `finish`는 human 입력 차단 후 계정·대상·연결 확인, `close`·timeout은 binding 폐기 | H6 request_and_effect |
| R-D06 | 뷰어 `dispose`는 화면 분리일 뿐 작업 취소가 아님. 끊긴 뒤에도 작업 계속 | VIEWER client_contract, AT-02 |
| R-D07 | grant는 URL·로그에 남기지 않음 (첫 메시지 인증, 주소창에서 제거). 키 입력 내용은 감사 로그 제외 | VIEWER "not logged/URL leaked", PoC T11 |
| R-D08 | 세션·계정·lease 격리: 세션마다 별도 BrowserContext, worker lease는 연결당 1개, 다른 소유자·이전 세대 grant 거부 | AC2, AT-02 |
| R-D09 | STORE와 브라우저가 없는 단계부터 시작: 계약대로 동작하는 fake STORE + fake page로 facade·gateway를 먼저 시험 | 의존성 승인 전에도 진행 가능, 이후 실제 구현 교체 |

## 4. 구현 순서

1. (지금 가능) 포트 타입과 facade 골격: `AuthService`(I3), `ExecutionService`(I4), `RuntimeGateway`(RT-01~04), `StorePort` 인터페이스
2. (지금 가능) fake STORE·fake page 기반 시험: 등록 operation만 실행, admission 순서, fence 후 차단, 응답 유실→unknown, 이전 세대 grant 거부, lease 중복 거부
3. (의존성 승인 후) 브라우저 runtime: 세션 생성·폐기, `ScopedPage` 구현, 뷰어 전송
4. (R04 합의 후) VIEWER client `mount/dispose`와 이벤트(ready/error/disconnected)
5. (R03 합의 후) 실제 STORE 연결, r05-kmong adapter와 통합 시험
6. 결과 기록 (§6)

## 5. 시험·완료 조건

| 수용 기준 | 시험 | 기대 |
|---|---|---|
| AC1 I3/I4 facade, RT-01~04, viewer, 같은 인증 연결 인계 | 직접 mock 로그인 → finish → 같은 연결로 실행 | 연결 재생성·재로그인 없이 실행, verified 출력에 connection 포함 |
| AC2 세션·계정·lease 격리, STORE admission·fence, raw driver 비노출 | 다른 세션·이전 세대 grant·잘못된 계정·이중 lease·fence 후 요청 | 모두 거부, 외부 변경 0건, adapter 인터페이스에 driver·쿠키 없음 |
| AC3 중립 mock에서 실제 브라우저 제어·뷰어 분리·응답 유실 | 브라우저 실행 중 뷰어 dispose, 응답 유실 주입 | 작업 계속, 유실은 unknown으로 보존, 재제출 없음 |

완료 판정: 독립 실행 명령으로 통과하고 명령·commit·관측을 §6에 기록. 제품 시험 AT-02, AT-03, T5-02, T5-12, DV-02, DV-05는 R01 통합 단계에서 판정.

## 6. 실행 기록

(구현 후 작성)

## 7. 미정 사항 (확인 중)

- Q1 (R01) 제품 의존성 추가: Playwright + Chromium, product `pyproject.toml`·`uv.lock`·CI 변경 승인. 승인 전에는 §4의 1~2만 진행
- Q2 (R01·R03·R04) 뷰어 전송 방식: CDP screencast + WebSocket 제안 (PoC 근거). endpoint 위치, 동일 origin, TTL·timeout 수치 — 설계상 11/27 결정
- Q3 (R03) STORE 호출 형태: `admit(ctx, op) -> permit`, `observe(ctx, observation, evidence)`, `fence(registration_id, error)`의 함수 시그니처와 예외 형태
- Q4 (R01) 일정: runtime 우선 시 크몽 adapter 마감 조정 여부
