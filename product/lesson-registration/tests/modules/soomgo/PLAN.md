# r04-soomgo 상세 설계 및 구현 계획 — TASK-052 (R04)

- 작성일: 2026-11-25 · 작성: R04 (원민, 숨고 Adapter / 플랫폼 연동)
- TASK: [TASK-052](../../../../../docs/artifacts/tasks/TASK-052.json) "숨고 등록 adapter 및 독립 mock 구현" · 상태: 진행 중 (R04 수신 및 착수)
- Phase: [PHASE-20261125-01](../../../../../docs/human/phase-intents/PHASE-20261125-01.md) 공통 계약 기반 mock 제품 개발
- 패키지: `r04-soomgo` · 브랜치: `r04/product-soomgo` (로컬 통합: `akaraywon`) · 배정: HRESP-20261125-01
- 담당 경로: `src/lesson_registration/platforms/soomgo/`, `fixtures/platforms/soomgo/`, `tests/modules/soomgo/`
- 근거 설계: CS-01, CS-05, CS-06 ([공통 설계 V1](../../../../../docs/artifacts/design/lesson-registration-20261124/COMMON-INTEGRATION-V1.md), platform-profiles-v2.json, data-schema-v4.1.json)

---

## 1. 목적 및 작업 범위

숨고(Soomgo) 플랫폼의 레슨 서비스 설정(`service_configuration`) 자동 등록을 위한 전용 어댑터(Adapter)와 합성 mock 페이지 및 fixture를 구현한다. 공통 Runtime Gateway가 승인한 S1~S6 단계별 오퍼레이션을 실행하고, 1회 저장 및 독립적인 readback 관측을 통해 등록 성공 증거를 수집한다.

| 영역 | 포함 항목 | 제외 항목 |
|---|---|---|
| **Adapter 구현** | 숨고 전용 PlatformPort 구현, S1~S6 바인딩 실행, 관측 데이터 생성 | 공통 앱/스토어 상태 전이(R03) |
| **합성 Fixture** | 숨고 고수 서비스 설정 합성 HTML/DOM fixture, mock 응답 | 원격 브라우저 컨테이너 관리(R05) |
| **검증 로직** | 1회 저장 원칙, 독립 readback 검증, 응답 유실/에러 처리 | 실제 숨고 웹사이트 로그인/자격증명 (mock-only) |
| **독립 테스트** | Gateway 주입 mock 환경 기반 정상/실패/unknown 단위 테스트 | 크몽 어댑터 구현(R05) |

- **관련 요구사항**: REQ-02, REQ-05, REQ-06, REQ-07, REQ-08
- **품질/시험 참조**: AT-05, T5-13, DV-03, DV-04

---

## 2. 공통 설계 준수 규칙

1. **등록된 Operation 및 승인된 설정값 사용 (CS-01, CS-05)**:
   - 어댑터는 사전에 프로필(`soomgo.service_configuration.mock.v2`)에 정의된 규격과 강사가 승인한 exact bound value만을 사용하여 입력한다.
2. **1회 저장 및 독립 Readback 확인 (CS-06, DV-03)**:
   - 양식 입력 완료 후 최종 저장은 정확히 1회만 수행한다.
   - 저장이 완료된 후, 브라우저 세션이나 별도 조회를 통해 설정된 값들이 정상 반영되었는지 독립적으로 읽어(readback) 관측 증거(`EvidenceRecord`)를 생성한다.
3. **효과 멱등성 및 중복 방지**:
   - 동일한 logical operation에 대해 불필요한 반복 요청을 전송하지 않으며, 승인되지 않은 단계 진입을 차단한다.
4. **오류 및 응답 유실 실패 처리 (DV-04)**:
   - 잘못된 셀렉터, 타겟 불일치, 저장 후 응답 타임아웃/유실 발생 시 성공으로 간주하지 않고 명시적으로 `failed` 또는 `unknown` 오류를 Gateway에 보고한다.
5. **Mock-only 제약**:
   - 실제 숨고 계정이나 라이브 운영망에 접근하지 않으며, 로컬 fixture 및 모의 DOM 환경에서만 구동한다.

---

## 3. 상세 설계 결정

### 3.1 모듈 및 Fixture 구조

```
product/lesson-registration/
  ├── src/lesson_registration/platforms/soomgo/
  │     ├── __init__.py
  │     ├── adapter.py          # SoomgoAdapter (공통 PlatformPort 규격 구현)
  │     ├── operations.py       # S1~S6 오퍼레이션 정의 및 입력값 바인딩 매핑
  │     └── observation.py      # readback 관측 파서 및 EvidenceRecord 생성기
  ├── fixtures/platforms/soomgo/
  │     ├── service_config.html # 숨고 서비스 설정 합성 DOM 페이지
  │     └── mock_responses.json # 합성 API 응답 정의
  └── tests/modules/soomgo/
        ├── PLAN.md             # 본 계획서
        ├── test_bootstrap.py   # 기본 부트스트랩 테스트
        └── test_soomgo_adapter.py # 어댑터 정상/readback/실패 독립 검증
```

| 결정 ID | 항목 | 선택 | 근거 |
|---|---|---|---|
| **D1** | 대상 필드 | `category`, `daw`, `goals`, `keyboard`, `ages`, `genders`, `format`, `location_mode` 8개 필드 | `platform-profiles-v2.json`의 숨고 MIDI 레슨 공식 프로필 준수 |
| **D2** | Fixture 구현 | 독립 경량 HTML5 합성 페이지 + DOM 파서 | 무거운 외부 브라우저 없이도 빠른 독립 단위 테스트 수행 가능 |
| **D3** | 증거 수집 | Readback 시 각 폼 필드의 value/checked 상태를 JSON 해시와 함께 EvidenceRecord로 캡처 | RESULT 모듈(R03)의 엄격한 판정 규칙(CS-06) 통과 |

---

## 4. WBS 및 구현 계획

| 단계 | 작업 내용 | 예상 소요 | 산출물 |
|---|---|---|---|
| **W1** | 숨고 합성 HTML 페이지 및 mock 응답 fixture 작성 | 0.5 MD | `fixtures/platforms/soomgo/` |
| **W2** | SoomgoAdapter 및 S1~S6 오퍼레이션 바인딩 구현 | 1.0 MD | `src/.../soomgo/adapter.py`, `operations.py` |
| **W3** | 독립 Readback 검증 및 Evidence 생성 로직 구현 | 0.5 MD | `src/.../soomgo/observation.py` |
| **W4** | 독립 테스트 환경 검증 (HappyPath, Readback 실패, 유실) | 1.0 MD | `tests/modules/soomgo/test_soomgo_adapter.py` |

- **총 예상 소요 시간**: 3.0 MD (12/8 mock MVP 일정 내 완료)

---

## 5. 수용 조건 검증 계획

- **r04-soomgo-AC1 (S1~S6 등록 및 설정값 사용)**:
  - 8개 필드에 대한 승인 스냅샷 값들이 올바른 DOM 엘리먼트에 바인딩되는지 검증.
- **r04-soomgo-AC2 (1회 저장 및 독립 readback)**:
  - 저장 버튼 클릭 1회 실행 확인 및 저장 후 폼 재조회를 통한 readback 일치율 검증.
- **r04-soomgo-AC3 (독립 mock 페이지 및 오류 시험)**:
  - 필드 누락, 셀렉터 오류, 응답 유실 시 실패 판정이 정상 전달되는지 검증.
