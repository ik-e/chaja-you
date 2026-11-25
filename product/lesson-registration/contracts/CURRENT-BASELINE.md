# 공동 개발 기준선 · 2026-11-25

**먼저 이 문서를 읽고 main을 적용한다.** [R01 전달 기록](../../../docs/human/responses/HRESP-20261125-08_common-baseline-release.md) · [고정 논리 계약](../../../docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [WORKSPACE](../WORKSPACE.json) · [IB/PD 및 세부 후보](README.md).

## 1. 이미 적용해야 하는 기준 (재협의/재승인 불필요)

- 기존 CS-01~09, IB-01~05, PD-01~08 방향과 pinned data-schema-v4.1 / platform-profiles-v2 / trace V0.9 유지. Python 3.12 제품 lock, app/remote/verification 그룹 사용. Playwright 1.57.0/Chromium, FastAPI/SQLite, CDP screencast + WebSocket 방향 채택.
- H1~H9와 named schema는 정본. UI에 필요한 파생값은 UI 내부에서 계산한다. H8 `progress={step_index,step_count,confirmed_steps,current_step?}`; StepView는 step_id,label,status. job_state는 null 또는 active/stopping/done/stopped; pending은 단계 상태만 가능. H8은 저장된 상태만 조회, 외부 readback/실행 없음. revision으로 오래된 응답 무시.
- H6 open: action, expected_revision; finish/close/refresh: generation 추가. 응답은 registration + open/refresh의 grant(generation,viewer_grant,expires_at). Viewer는 R05 제공 mount(container,grant,onEvent) / dispose; grant URL/query/log/storage 노출 금지, 메모리에서만 전달. 정적 endpoint, 인증된 same-origin WS 첫 메시지 전달 방향; owner/registration/generation/expiry 검증, 연결 후 입력 차단과 갱신·폐기 시험. 실제 endpoint/message는 아래 협의.
- H7: expected_revision,review_digest,approved:true,request_key. 첫 durable 수락 202, 정확한 동일 요청 재조회 200; 전송 유실은 동일 key와 동일 body만. 수락 후 변경/취소/재개/자동재실행 금지. H8 polling 간격·UI backoff 자율(1.5~3초 가능); 60초 조회 제한은 조회 중단/재조회 안내이며 goal_verdict 변경 금지. terminal result는 CO 저장 goal_verdict(confirmed/not_reached/unknown), evidence, next_action을 사용한다.
- Source 원본 불변, 플랫폼별 선택만 registration 변경; 원문 근거 충분한 값의 불필요한 재확인 방식 재검토, 최종 승인 1회 유지. 누락·충돌·미확인 추정 금지. 실제 모델은 OpenAI API 방향이나 기관 권한·예산 미확정; 합성 fake 독립 개발 가능.
- CO 상태 권위, STORE durable admission, stable logical effect key, same verified connection/exclusive lease, unknown 보존, 등록 operation만 dispatch. Adapter는 BoundGateway 경계 준수; ScopedPage는 내부 제한 page 구현으로만 사용. 원시 driver/credential/permit을 외부 adapter로 노출 금지. 실제 readback에 근거한 판정.
- 공통 canonical bytes/digest 사용; ProfileRef.digest는 named Profile view의 ref.digest 제외(원본 registry/value schema 별도 pin). exact Scope, 실제 정규화 payload, 원본 asset bytes와 업로드 순서. 기존 profile/schema를 변경하거나 미승인 실제 플랫폼/계정/자격증명을 사용하지 않는다.

## 2. D01~D06 reference: 확정된 방향, 구현 세부 반환 대상

[DETAIL-CANDIDATE.json](DETAIL-CANDIDATE.json), [SESSION-SECURITY.md](SESSION-SECURITY.md), [reference tests](../tests/contract/test_detail_candidate.py), [INTERFACE-REVIEW.md](INTERFACE-REVIEW.md). Reference는 대조 기준이며 실제 제품 provider로 자동 주입하지 않는다.

| 항목 | 담당 협의 | 반환할 최소 결과 |
| --- | --- | --- |
| D01 | R03/R04/R05 | 크몽·숨고 operation/manifest/binding과 slot, readback normalized values+asset 순서에 대한 동일 예제·digest. R03 임시식/R05 독자식은 그대로 동시 사용 금지. |
| D02 | R03/R05 | opaque claim/context/lease/one-shot permit, atomic admit/consume/fence; actual dispatch race 및 응답 유실 시험. |
| D03 | R03/R04/R05 | admission-linked Observation/EvidenceRecord, terminal CAS/unknown 보존, optional 별도 late-read 승인 범위. |
| D04 | R03/R04/R05 | same-origin endpoint/message/events, grant TTL/owner/refresh, finish 입력 차단, detach·재접속·폐기 시험. URL grant 금지. |
| D05 | R02/R03 | 동기 I2 제한 호출, timeout/late revision 무시, blocking issue/typed error, 중첩 수정 시 부모/나머지 패키지 보존. |
| D06 | R01/각 담당 | provider factory/config, 명시 주입, single app process, runtime async bridge, startup orphan fence/bounded shutdown. |

각 담당은 자기 PLAN에 공통 기준 SHA, 기존 구현과 차이, 제안/합의한 예제·정상/실패/unknown 검증, 남은 공수만 반환한다. 기존 계약 준수는 별도 승인 대기 없이 진행. 공통 계약 변경만 R01 검토(근거·영향·시험 포함). 다른 담당 영역 직접 변경 금지. 11/27은 협의 목표 후보이지 새 마감일 아님.

## 3. 적용 절차

자신의 변경을 먼저 커밋/보존하고 `git fetch origin`, `git merge origin/main`으로 최신 main 반영. 강제 reset 금지. 적용 SHA 기록. 제품 root에서:

```sh
uv sync --locked --all-groups --python 3.12
uv run --locked --all-groups --python 3.12 python dev.py doctor
uv run --locked --all-groups --python 3.12 python dev.py test <package>
uv run --locked --all-groups --python 3.12 python dev.py check-changes <package> --base <applied-main-SHA>
```

브라우저 필요 시 `uv run --locked --group remote python -m playwright install chromium`; Linux 시스템 의존성은 지원 Ubuntu 24.04에서 --with-deps. 자기 package 및 실제 provider 간 검증은 개별 근거 기록. bootstrap/합성/reference/물리 probe는 전체 제품 gate가 아니다.

## 4. 검증 상태

고정 후보 [81ade0f](https://github.com/ik-e/chaja-you/commit/81ade0f0287d5827aee6575e37d83d19d297973f)의 [공통](https://github.com/ik-e/chaja-you/actions/runs/45551936586) · [물리](https://github.com/ik-e/chaja-you/actions/runs/45551936592) · [bootstrap](https://github.com/ik-e/chaja-you/actions/runs/45551937159) · [문서](https://github.com/ik-e/chaja-you/actions/runs/45551936530) CI 모두 성공. Profile digest와 접근 가능한 차단 origin 비교 검증 포함. 최신 main의 추가 구현과 함께 재검증하고, 담당자 실제 적용/제품 22개 gate는 별도 판정. 실제 서비스 인증/보안은 미승인·미검증.
