# r05-remote PLAN · TASK-053 원격 브라우저 runtime·인증·뷰어

## 2026-11-25 R03 main 089b8a4 실제 연결

R03 구현 `ab5f8b1`을 포함한 main `089b8a4`를 병합했다. 담당 경로에서 다음을 연결했다.

- `PlatformBinding.make_worker_context` 내부 factory에 실제 STORE worker context 전달. 기존 3인자 make_context는 기존 caller용으로 유지하며 adapter에는 제한된 결과 context만 전달한다.
- RT-03은 `admit` 반환 Permit을 `store.dispatch(context, permit, operation, invoke)`에 전달한다. consume은 별도로 호출하지 않는다. invoke는 동기 driver.perform과 BrowserHost.run의 완료 후 반환한다. dispatch가 callback 전에 거절하면 실행 관측을 생성하지 않고 fence한다.
- actual browser race 3개를 추가했다. admit 이후 Coordinator fence 완료 시 K6 driver 호출·접수 0건. consume 이후 Coordinator fence 경합 시 callback 종료까지 fence 대기, 실제 접수 1건. 응답 유실이면 unknown을 보존하고 K7·재실행을 차단한다.
- R03 create_viewer_app의 실제 HttpOnly cookie와 HTTP H6 및 Viewer router를 Chromium에서 연결했다. 무세션 HTTP 401, 세션 발급 후 H6 open, 실제 WS 프레임과 가상 로그인, H6 finish의 verified 응답을 확인했다. R04 버튼 자체의 바인딩은 별도다.

Windows / Python 3.12.7 / Chromium 143.0.7499.4에서 `uv run --locked --all-groups python dev.py test r05-remote` 34개 통과, 실패·skip 0개(71.481초). 이전 307·308 6개도 포함한다. 공통 시험은 Windows 기본 cp949에서 기존 파일 read_text 오류가 났고, 공통 파일을 수정하지 않고 `PYTHONUTF8=1`로 다시 실행해 24개 통과했다. doctor와 `check-changes r05-remote --base 089b8a4`, diff 검사도 통과했다.

별도 `r05-integration-check-089b8a4` 검증 작업 공간에서 두 R05 담당 디렉터리만 조합해 크몽 40개를 모두 실행했다. RuntimeSupport.slot_resolver와 실제 worker-bound 승인 이미지 reader, StoreGateway/Adapter 양쪽 binding.v1, 동기 dispatch 및 독립 재조회를 검증했다. 성공 실행의 Permit 7개가 모두 소비됨도 추가 확인했다. R03의 DB당 단일 서버 프로세스 보장 범위가 적용된다.

R04 실제 버튼부터 등록까지의 전체 UI E2E 및 새 변경의 커밋·push·GitHub CI는 후속이다. 종료 후 read 권한은 확장하지 않았다. R01의 공유 helper 승격과 전체 제품 gate 판정은 별도다.

## 2026-11-25 POST 307·308 재전송 회귀

기준 커밋은 `2baeb2b5d42432f8b0bd6218c02d9d6d6965b9f8`이다. NeutralSite에 접수 전/후 307·308과 후속 제출 endpoint를 추가했다. 중복 차단을 하지 않는 모의 사이트에서 요청 경로별 POST 횟수와 실제 접수 건수를 관측한다. 요청 본문·쿠키·Grant는 새 관측 목록에 저장하지 않는다.

변경 전 Chromium에서 접수를 저장한 원래 endpoint가 307을 반환하면 `route.fetch(max_redirects=0,max_retries=0)` 뒤 `route.fulfill(response=resp)`를 받은 브라우저가 이동 endpoint로 다시 POST했다. 최초 요청 1건과 이동 요청 1건으로 실제 접수 2건, K6 confirmed를 재현했다. 따라서 fetch 내부 redirect 제한만으로 브라우저의 후속 POST를 막을 수 없다.

R05 국소 보완으로 변경 요청의 응답이 307·308이면 브라우저에 전달하기 전에 abort한다. 리다이렉트가 원래 요청의 미처리를 보장하지 않으므로 접수 전/후 모두 unknown으로 보존한다. 첫 endpoint에서 실제 접수된 경우 1건, 접수 전 응답이면 0건이다. 자동 이동이나 재실행은 하지 않는다. 307·308을 요구하는 실제 사용자 인증/업무 흐름은 현재 이 정책으로 중단될 수 있으며, 지원 필요 시 새 승인·실행 경계와 함께 담당자 협의 대상이다.

추가한 `PostRedirects` 6개는 307/308 각각의 접수 전 이동·접수 후 이동·다른 origin 이동이다. 변경 후 최초 POST 1건, 후속 POST 0건, 다른 origin 요청 0건, K6와 최종 결과 unknown, 동일 job 재호출 시 접수 증가 없음, 안전한 redirect_blocked 감사 이벤트를 확인했다. 기존 303 후 GET 전환과 정상 등록·응답 유실 시험도 회귀에 포함했다.

Windows / Python 3.12.7 / Playwright 1.57.0 / 관리형 Chromium 143.0.7499.4에서 전체 `uv run --locked --all-groups python dev.py test r05-remote` 30개 통과, 실패·skip 0개(57.203초). 감사 이벤트 검증을 보강한 뒤 `python -m unittest -v test_execution.PostRedirects` 6개도 통과(19.291초)했다. lock·doctor·담당 경로·diff 검사도 통과했다. 이번 변경의 커밋·push 및 GitHub CI는 별도다.

## 2026-11-25 CI 확인 및 Viewer 예외 시험 보강

기존 push 커밋은 remote `a7af1114b43638e298d71d4fbcaf40bf4c0e09c7`, kmong `a3718a90c5179b5f72927347cf700283aa588992`이다. GitHub REST API에서 각 SHA의 Actions runs와 check-runs를 조회한 결과 모두 0건이었다. 제품 workflow의 push 대상은 main 및 R01 준비 브랜치이며 pull_request/workflow_dispatch도 지원한다. R05 브랜치 push만으로 실행되지 않는다. snapshot workflow는 과거 고정 커밋을 검증하므로 새 R05 커밋 검증과 구분한다. CI 설정은 수정하지 않았다.

확인 시점 최신 main `366cea92a497ff68176107766b1314ab75d5c59f`의 product bootstrap 실행 [45565527074](https://github.com/ik-e/chaja-you/actions/runs/45565527074)은 success다. 두 R05 push 커밋이 main의 ancestor가 아님을 확인했다. 해당 main 성공을 R05 커밋의 CI 통과로 기록하지 않는다.

`test_transport.py`에 다음 5개를 추가했다.

- 만료 Grant로 WS attach 시 화면/상태를 전달하지 않고 연결 거절
- attach 이후 Grant 만료 시 입력 거절과 입력 내용 비기록
- 두 동시 attach 경쟁에서 성공 1개·거절 1개, 활성 Viewer 1개
- WS detach는 브라우저 context를 유지하되 같은 Grant 재접속 거절, H6 refresh 후 새 generation으로 재접속
- Chromium에서 연결 중 즉시 dispose와 반복 dispose, 3회 refresh/mount/dispose 후 canvas·Viewer 잔존 0개 및 원래 context 유지

브라우저 시험용 서버 시작 코드를 재사용하도록 정리했다. 제품 코드 변경은 없다. 원래 R04 UI 버튼 바인딩을 자동 연결하는 시험으로 확대하지 않았다.

Windows / Python 3.12.7 / Playwright 1.57.0 / 관리형 Chromium 143.0.7499.4에서 `uv run --locked --all-groups python dev.py test r05-remote` 결과 24개 통과, 실패·skip 0개다. 이전 19개와 신규 5개를 함께 실행했다. lock/doctor/소유 경로 및 diff 검사도 통과했다. 새 시험 변경의 커밋·push 및 GitHub 실행은 별도다.

- 담당: R05 (임다혁) · 브랜치: `r05/product-remote` · 기준 커밋: `65aed37` (활성화 커밋)
- 독립 실행: `uv run --locked --python 3.12 python dev.py test r05-remote`
- 고정 설계: `common-integration-v1.json` (state, storage S-ACCEPT~S-FENCE, runtime RT-01~04, VIEWER), `data-schema-v4.1.json` (AuthInput/AuthOutput/AuthGrant, ExecuteInput/ExecutionReport, Operation/Observation), 06-API-PORTS I3·I4·H6
- 상태: 1차 구현 (2026-11-25). R01 회신으로 Playwright·CDP+WS 방향 확정, main `22cbb4f`(R03 StoreGateway 포함) 병합 후 진행. §7은 R03·R04 협의 대기.

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
| R-D10 | (구현 중 발견) GET/HEAD 외 요청은 브라우저가 아니라 Playwright `route.fetch(max_redirects=0, max_retries=0)`로 **한 번만** 보내고 응답을 그대로 돌려줌. 응답이 없으면 요청 실패로 끝내 unknown 유지 | 서버가 응답 없이 연결을 닫으면 Chromium이 같은 POST를 조용히 다시 보냄을 관측(클릭 1회에 접수 2건). 효과 중복 위험이라 runtime 단에서 차단 |
| R-D11 | runtime은 STORE의 `expected_operations`와 driver의 operation 목록이 정확히 같을 때만 실행, admit은 operation마다 브라우저 조작 전에 호출 | R03 StoreGateway 기준(11/25). 목록 불일치는 PROFILE_CHANGED로 fence |
| R-D12 | I3 finish는 사람 입력 차단 → 진행 중 이동이 끝날 때까지 대기 → 페이지에서 계정 읽기 → slot 기준 대상 상태 확인 순서. 계정은 사람이 입력한 값을 읽지 않고 플랫폼 화면이 보여준 계정 ID만 사용 | 자격증명 비보관, "trusted identity before target" (T5-02) |
| R-D13 | 뷰어는 전송 중립 API: `attach_viewer(grant, owner, sink)`와 `ViewerConnection.receive/dispose`. WebSocket endpoint는 R03 서버 경계에서 이 API에 연결 | R01: 세부 연결 규격은 R03·R04와 협의. 메시지 형식 제안은 `remote/viewer.py` 머리말 |

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

### 2026-11-25 · 1차 구현 (실제 브라우저 + R03 Coordinator/StoreGateway)

- 기준: main `22cbb4f` 병합 위 작업 트리(커밋 전). Python 3.12.3, Playwright 1.57.0 (remote 그룹 lock 그대로)
- 브라우저: 작업 환경에서 Playwright Chromium 다운로드가 차단되어 `LR_BROWSER_CHANNEL=chrome`(설치된 Google Chrome 153.0.8010.12)으로 실행. 2026-11-25 Windows에서 관리형 Chromium 143.0.7499.4 (Playwright 1.57.0, build v1200)로 재검증하여 15개 모두 통과. GitHub CI 실행은 별도 확인
- 명령: `LR_BROWSER_CHANNEL=chrome uv run --locked --group remote python dev.py test r05-remote` → **15 tests OK** (bootstrap 1 + 제품 14), 연속 4회 통과. `check-changes r05-remote --base 22cbb4f` 통과
- 입력: 중립 mock(`tests/modules/remote/neutral_site.py`), R03 `Coordinator`+`StoreGateway`(SQLite), 공통 replay I2 Preparation, `fixtures/shared/mock-image.png`. 시험용 driver는 pinned kmong 단계 K1~K7을 중립 mock에 대응

| 수용 기준 | 시험 | 기대 | 관측 | 판정 |
|---|---|---|---|---|
| AC1 같은 인증 연결 인계 | `test_same_connection_executes_and_goal_confirmed` | 사람이 뷰어 입력만으로 로그인 → CO finish → start → run_job이 같은 BrowserContext로 실행, 재로그인 없음 | 로그인 1회, 상태 `done`, 효과 K1~K7 모두 confirmed, mock 저장값 = 승인 values | pass |
| AC1 I3·viewer | `DirectAuth` 6건 | open→grant·화면 전송, finish→페이지 계정으로 verified, finish 뒤 입력 거부, refresh는 grant 회전·연결 유지, close는 연결 폐기·새 세대 | 일치 | pass |
| AC2 세션·계정 격리 | `Isolation` 3건 | 세션 간 쿠키 비공유, 다른 origin 요청 0건, 상대·외부 경로 거부, 유휴 시간 초과 시 닫힘 | 일치 | pass |
| AC2 STORE admission·fence, raw driver 비노출 | `Denials` 3건 | 위조 connection·미등록 operation → 외부 변경 0건·stopped, 이중 worker 거부, BoundGateway는 3개 메서드만, 변조 operation 뒤 fence | 일치 | pass |
| AC3 응답 유실 | `test_lost_submit_response_unknown_not_resent` | 접수 응답 유실 → 재전송 없음, 재실행 시 재dispatch 없음 | 접수 1건, K6 1회, 종료 상태 유지 | pass |
| AC3 뷰어 분리 | `test_same_connection...`(실행 전 dispose) | 뷰어 dispose 뒤에도 작업 진행 | `done` | pass |

- 회귀 민감도: POST 단일 전송(R-D10), admit 호출, 연결 일치 검사를 각각 제거하면 해당 시험이 실패함을 확인. registry 검사를 제거해도 R03 STORE가 미등록 단계를 거부해 zero mutation 유지(이중 방어 확인)
- 미완료/incomplete: 실제 WebSocket endpoint(R03·R04 협의), CI Chromium 실행 확인, r05-kmong adapter 실제 연결(브랜치 병합 후), 제품 시험 AT-02·AT-03·T5-02·T5-12·DV-02·DV-05는 R01 통합 단계

- 로컬 재검증 기준: main `bc2e2c8` 병합, `LR_BROWSER_CHANNEL` 미설정. `uv run --locked --group remote python dev.py test r05-remote` → **15 통과, 0 실패** (26.476초).
- `check-changes r05-remote --base 22cbb4f`는 개인 미추적 파일 64개와 이후 main에서 병합된 공통 경로 37개를 보고함. 실제 적용한 main `bc2e2c8`과 대조한 변경 14개는 모두 R05 원격 담당 경로에 있음.


## 7. 미정 사항 (확인 중)

- ~~Q1 의존성~~: R01 회신으로 해결(remote 그룹에 이미 반영)
- Q2 (R03·R04) 뷰어 endpoint 위치·인증·메시지 형식(제안: `remote/viewer.py`), grant TTL(현재 600초)·유휴 TTL(900초) 수치
- Q3 (R03) STORE: `acquire_context`·`expected_operations`를 R03 StoreGateway 그대로 사용 중. 작업 종료 시 lease 해제 함수 필요 여부
- Q4 (R01) 일정: runtime 우선 시 크몽 adapter 마감 조정 여부
- Q5 (R03) slot_ref 출처: 계약은 "server source lineage" 기준인데 AuthInput에는 registration_id만 있음. 현재 `slot-{registration_id}`. 같은 원본으로 두 번 등록하는 경우를 막으려면 CO가 source 기반 slot을 넘겨줘야 함
- Q6 (R03) 실행 중 첨부 바이트 제공 방법: driver가 이미지 bytes를 digest로 받을 AssetSource 필요(크몽 K3)
- Q7 (R01·R04) ScopedPage 인터페이스·예외 타입을 공통 계약으로 둘지: 현재 `remote/page.py`에 정의하고 driver별 예외 클래스를 주입받는 방식
# 2026-11-25 Viewer WebSocket 및 입력 gate 후속

목적은 사용자의 직접 인증 이후 서버가 같은 세션으로 승인된 모의 작업을 수행하도록 연결하는 것이다. 적용 main은 `094e4d2c5dd3fbb8e9c9352296f87d90cd659308`이다.

이번 구현은 `viewer.js`의 mount/dispose, R03 주입용 `viewer_router`, single-use Grant attach, finish 입력 barrier와 대기 입력 재검증, Source slot resolver 주입점이다. 전송 경로와 수치 상한은 R05 세부 제안이며 R03·R04가 실제 조립부에 반영하기 전 상태다. 공통 의존성과 다른 담당 경로는 수정하지 않았다.

Windows / Python 3.12.7 / Playwright 1.57.0 / 관리형 Chromium 143.0.7499.4에서 다음을 실행했다.

```powershell
uv run --locked --all-groups python dev.py test r05-remote
uv run --locked --all-groups python dev.py doctor
uv run --locked --all-groups python dev.py check-changes r05-remote --base 094e4d2
git diff --check
```

결과는 19개 통과, 실패 0개다. doctor·소유 경로·diff 검사도 통과했다. main의 R04 UI 원본을 테스트 서버로 제공하고 실제 viewer-container에 시험 코드가 mount를 호출했다. 실제 WS 프레임 수신, DOM 입력으로 가상 로그인, finish 이후 입력 0건, 반복 dispose, URL/storage Grant 미노출을 확인했다. 다른 owner/origin/query 거절, Grant 재사용·잘못된 generation 거절, finish 전 대기 입력 폐기를 확인했다. R04 기존 버튼/H6 호출을 연결한 전체 제품 E2E는 미실행이다. Uvicorn의 기본 WS 구현에서 승인된 라이브러리의 deprecation warning이 출력되지만 시험 실패는 없다.

브라우저 종료 시 남은 route task 정리를 추가했다. 일부 모의 연결 폐기에서는 서버 측 ConnectionAbortedError가 출력될 수 있으며 실제 제품 서버 통합 시 로그/teardown도 추가 확인한다.

R03과 남은 항목은 endpoint의 서비스 owner 인증 주입, Source 계보 기반 안정 slot resolver, 승인 asset reader의 registration/owner/lease 권한, D01 전체 Scope digest, D02 Permit consume와 Fence 실제 dispatch 원자 경계다. 현행 STORE는 Permit을 반환하지만 consume API가 없어 D02 완료를 주장하지 않는다. expected_operations가 없는 STORE를 driver registry로 대신 승인하던 fallback은 제거했다. Fence 이후 readback은 별도 late_read_authorizer가 허가할 때만 수행하며 기본은 unknown을 보존한다. 허가의 계약/관측 저장 경계는 R03과 확인한다.

R04는 정적 JS import와 mount/dispose 호출, H6 finish/refresh/close 연결, 서버 응답 기반 인증 상태 표시를 반영해야 한다. postMessage iframe 방식 대신 module/canvas 연결안을 제안한다. 실제 UI 수정은 R04 담당이다.

현재 변경은 로컬에서 검증했으며 새 커밋의 GitHub CI는 미실행이다. 다음 단계는 담당자 조립부 반영 후 공동 E2E와 공통 D01~D04 대조다. 기존 3~3.5근무일 추정에서 실제 남은 공수는 이 협의 후 다시 산정한다.
