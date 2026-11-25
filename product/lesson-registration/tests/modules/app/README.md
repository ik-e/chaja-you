# R03 TASK-050 · 연동 준비

H1~H9·CO·KNOW·STORE·RESULT; 원자 수락/admit/observe/fence와 API; 별도 브라우저·PREP 구현 제외

## mock 서버 실행

`product/lesson-registration`에서 실행한다.

```powershell
uv run --locked --group app --group verification python tests/modules/app/mock_server.py --platform kmong --origin http://localhost:5173
```

숨고는 `--platform soomgo`를 사용한다. 출력된 loopback URL을 UI API 주소로 지정하고
요청에 `X-Mock-Owner: demo-a`를 붙인다. 합성 owner 선택용이며 운영 인증이 아니다.
origin은 프로토콜·호스트·포트까지 정확히 일치해야 한다. 필요한 origin은 옵션을 반복해 추가한다.
Ctrl+C로 종료하며 임시 DB도 삭제한다. 플랫폼별 서버는 선택한 플랫폼 하나로 시험한다.

```powershell
$api = 'http://127.0.0.1:출력된포트'
$headers = @{ 'X-Mock-Owner' = 'demo-a' }
Invoke-RestMethod "$api/v1/sources" -Headers $headers
Invoke-RestMethod "$api/v1/sources" -Method Post -Headers $headers -ContentType 'application/json' -Body '{"raw_text":"synthetic lesson source"}'
```

## 연결 순서

원본 생성 → 등록 생성 → 준비 수정 → 인증 open/finish → review 확인 → start → 상세/목록 조회.
구체적인 요청은 [test_s8_http.py](test_s8_http.py)의 `source`, `ready`, `test_h1_to_h9_and_idempotency`를 참조한다.
이미지는 공통 합성 `fixtures/shared/mock-image.png`를 사용한다.
multipart는 application/json manifest와 `new_assets[].part_name`에 일치하는 파일 part를 보낸다.
H7 첫 수락은 202, 동일 요청 재전송은 200이다. 다른 owner 조회는 404이며 unknown은 자동 재실행하지 않는다.

PREP은 입력에서 사실을 추출하지 않고 고정 합성 결과를 반환한다. 인증은 fake 상태 전이이며 viewer는 제공하지 않는다.
기존 `dev.py serve api`는 고정 replay 서버다. 이 실행기는 실제 R03 CO/SQLite/HTTP에 synthetic provider를 명시 주입한다.

## 담당자 연결 지점

`mock_server.compose`의 `Providers(registry, preparation, execution, result)`가 교체 예제다.
R02는 preparation, R05는 execution을 공급한다. fake의 `runtime.gateway` 대입은 시험 편의 코드이며 실제 생성자 계약이 아니다.

- R02: I2 반환·누락/충돌·MODEL_UNAVAILABLE, timeout의 오류 코드와 저장 정책 확인.
- R05: GatewayStore, lease/operation/binding 연결. `acquire_context`와 `expected_operations`는 공동 검토 전 임시 helper.
- R04: API 주소·origin·합성 owner로 UI 연결. viewer endpoint/message는 R04/R05 합의 후 연결.

미응답은 합의가 아니다. 공통 계약 변경은 PLAN에 서명·예제·시험을 기록해 R01에게 반환한다.
실제 provider는 기존 fake 시험을 일괄 교체하지 않고 별도 연결 시험으로 검증한다.

```powershell
uv run --locked --group app --group verification python dev.py test r03-app
```

현재 독립 HTTP 시험과 실제 UI/viewer/provider 및 22개 제품 gate는 구분한다.
상세 설계·남은 미확인은 [PLAN](PLAN.md)과 [SPEC](SPEC.md)에 있다.
