# r05-kmong — R05 · TASK-054

크몽형 **합성** 서비스 등록 adapter (`kmong.service_listing.mock.v2`). 실제 크몽 접속·계정·제출 없음.

| 파일 | 역할 |
|---|---|
| `profile.py` | pin된 profile의 단계(K1~K7)·필드 미러, 효과 전 값 검증(조건부 지역, 이미지 규격·권리) |
| `operations.py` | 등록 operation 목록(RT-02), 안정 operation_id, binding_digest |
| `page.py` | runtime이 넘겨주는 좁은 페이지 인터페이스 `ScopedPage`, 자산 `AssetSource`, `KmongContext` |
| `adapter.py` | `KmongAdapter.perform`(RT-03), `observe_goal`(RT-04, slot 기준 독립 재조회) |
| `errors.py` | 관측을 담은 typed 오류 `KmongError(code, verdict)` |

runtime(r05-remote)은 `ScopedPage`를 브라우저로 구현하고, 각 operation 실행 전 STORE admission을 받는다. adapter는 job 상태를 바꾸지 않는다.
설계·시험: [`tests/modules/kmong/PLAN.md`](../../../../tests/modules/kmong/PLAN.md)
