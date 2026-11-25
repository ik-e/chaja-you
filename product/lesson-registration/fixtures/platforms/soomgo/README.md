# 숨고(Soomgo) 합성 Fixture 가이드 (r04-soomgo)

본 디렉토리는 숨고 플랫폼의 레슨 서비스 설정(`service_configuration`) 자동화 등록을 위한 합성(Synthetic) HTML DOM 및 모의 API 응답 fixture를 포함합니다. 실제 숨고 사이트에 접속하지 않고 완전 격리된 mock-only 환경에서 S1~S6 단계별 오퍼레이션과 독립 Readback 검증을 수행할 수 있도록 설계되었습니다.

## 포함 파일 목록

1. **`service_config.html`**:
   - 숨고 고수 레슨 서비스 설정 폼 페이지의 합성 HTML5 DOM.
   - 8대 필수 필드(`category`, `daw`, `goals`, `keyboard`, `ages`, `genders`, `format`, `location_mode`)의 입력 엘리먼트(`input[type=checkbox]`, `input[type=radio]`)와 단일 저장 버튼(`button#btn-save-service`)을 포함합니다.
2. **`service_detail.html`**:
   - 저장 완료 후 서비스 상세 관리 페이지의 합성 DOM.
   - S6(독립 Readback) 단계에서 실제로 저장된 데이터(`data-key`, `data-values`)를 재추출하여 증거 레코드(`EvidenceRecord`)를 생성하는 데 사용됩니다.
3. **`mock_responses.json`**:
   - S1~S6 단계별 정상 응답 및 오류 케이스(저장 실패, 타겟 불일치)의 합성 JSON 데이터.
