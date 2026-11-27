# DB 설계 입력 근거 연결 — 7개 플랫폼 및 R4/V5.1

> 상태: 근거 연결 완료(의미·물리 검증 미완료). V5.1 12개 테이블은 후보이며 변경·승인하지 않는다. mock-only.

[정본 JSON](../../artifacts/planning/lesson-registration-20261126/integrated/db-design-inputs-20261127.json)에서 생성한 검토용 읽기본. 이번 작업에서 직접 생성했으며 공식 project_docs.py/CI 실행은 하지 않았다.

## 기준선

- 최신 팀 자료: 14b3e5f380fbe4379a6eeb67dc8c991a4e38c912
- 최신 스토리/상위 명세: 1608d9b6b41e6812ce116bacd9c123aa2f28a1f3
- 기존 DB V5.1: 774465d765d2c776d6d415bc5222d2f02eff9d00
- 브랜치는 병합하지 않았다. R4 최신 의미와 승인된 원본 1:N 관계를 함께 사용한다.

## 조사 자료 연결

| 플랫폼 | R02 입력 묶음 | R02 독립 | R04 독립 | R05 독립 | R05 상세 | 객체/인증/완료 근거 |
|---|---:|---:|---:|---:|---:|---|
| 크몽 | 20 | 35 | 11 | 6 | 32 | [kmong-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/kmong-db-research.json) |
| 탈잉 | 20 | 26 | 11 | 7 | 22 | [taling-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/taling-db-research.json) |
| 숨고 | 8 | 10 | 28 | 5 | 21 | [soomgo-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/soomgo-db-research.json) |
| 프람피 | 14 | 29 | 9 | 2 | 7 | [prompie-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/prompie-db-research.json) |
| 뮬 | 12 | 17 | 11 | 1 | 23 | [mule-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/mule-db-research.json) |
| 힙합플레이야 | 6 | 7 | 10 | 3 | 11 | [hiphopplaya-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/hiphopplaya-db-research.json) |
| 힙합LE | 6 | 6 | 13 | 3 | 8 | [hiphople-db-research.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R05/hiphople-db-research.json) |

원본 필드 관측 374개(중복 의미 포함; 공통 250, 상세 124)의 ID·출처·방향·근거 참조를 보존했다. 이전 의미 후보 연결 258개; 추가 의미 정규화 필요 116개. 필드군 38개 및 플랫폼 업무 44개를 기존 DB 책임과 연결했다. 필드군 ↔ 입력 묶음은 플랫폼 수준 연결이며 개별 의미 일치 증명은 아니다.

R02 [user-stories-20261127.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R02/user-stories-20261127.json)의 실제 배열은 필수 52+선택 34=86. [v31-review-20261127.json](https://github.com/ik-e/chaja-you/blob/14b3e5f380fbe4379a6eeb67dc8c991a4e38c912/docs/artifacts/planning/lesson-registration-20261126/R02/v31-review-20261127.json)의 보고 96과 불일치한다. 탈잉 정산 및 뮬 약관은 직접 선행 절차, 탈잉 사용자 확인일은 조사 메타데이터. 86개 전체는 아래 후보로 연결하되 실제 서버 검증이 아니다.

## 저장 위치 후보

| 플랫폼 | 보고 분류 | 입력/절차 | 공통 원본 후보 | 업무별 저장/경계 |
|---|---|---|---|---|
| 크몽 | required | 제목 10\~30자 | sources.content.facts.title | 레슨 사실이면 원본, 글자 수/플랫폼 문구는 plan |
| 크몽 | required | 카테고리 | sources.content.facts.subject | 공통 분야와 플랫폼 분류 코드 분리; plan의 실제 선택값 |
| 크몽 | required | 서비스 설명 100\~20,000자 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 크몽 | required | 모집 형태 | sources.content.facts.delivery | 수업 제공 방식/모집 형태 구분, 채널별 선택은 plan |
| 크몽 | required | 메인 이미지 1\~4장 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 크몽 | required | 서비스 제공 절차 | sources.content.facts.curriculum | 레슨 절차 사실; 플랫폼의 별도 단계나 문구는 plan |
| 크몽 | required | 의뢰인 준비사항 | sources.content.facts.prerequisites/materials | 재사용 사실과 작업 전 요청 표현 구분 |
| 크몽 | required | 지역 | sources.content.facts.location/disclosure | 장소의 사실과 공개 범위, 채널별 정확 필드 구분 |
| 크몽 | required | 판매 패키지 가격 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 크몽 | required | 작업 기간 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 크몽 | required | 수정 횟수 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 크몽 | required | 1회 레슨 시간 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 크몽 | required | 레슨 횟수 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 크몽 | optional | 상세 이미지·동영상 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 크몽 | optional | 검색 키워드 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 크몽 | optional | 자주 묻는 질문 | sources.content.facts (확정된 재사용 사실만) | 질문답변 문구/순서 등 채널 표현은 plan |
| 크몽 | optional | 작업 전 요청사항 | sources.content.facts.prerequisites/materials | 재사용 사실과 작업 전 요청 표현 구분 |
| 크몽 | optional | 대상자·서비스 내용·준비물 | sources.content.facts.audience | 대상 사실과 채널별 길이/선택 코드 분리 |
| 크몽 | optional | 커리큘럼 | sources.content.facts.curriculum | 회차 순서/내용/시간 의미; 채널별 회차 구성 변환은 plan |
| 크몽 | optional | 수업 가능일 | sources.content.facts.availability | 수업 가능 조건과 외부 모집 일정 객체/관측을 구분 |
| 탈잉 | required | 카테고리 | sources.content.facts.subject | 공통 분야와 플랫폼 분류 코드 분리; plan의 실제 선택값 |
| 탈잉 | required | 클래스명 10\~30자 | sources.content.facts.title | 레슨 사실이면 원본, 글자 수/플랫폼 문구는 plan |
| 탈잉 | required | 대표 썸네일 1\~10장 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 탈잉 | required | 클래스 대상 50\~500자 | sources.content.facts.audience | 대상 사실과 채널별 길이/선택 코드 분리 |
| 탈잉 | required | 상세 소개 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 탈잉 | required | 회차와 회차별 커리큘럼 50\~500자 | sources.content.facts.curriculum | 회차 순서/내용/시간 의미; 채널별 회차 구성 변환은 plan |
| 탈잉 | required | 참여 인원 | sources.content.facts.audience | 대상 사실과 채널별 길이/선택 코드 분리 |
| 탈잉 | required | 수강료 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 탈잉 | required | 튜터명 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 탈잉 | required | 튜터 소개 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 탈잉 | required | 프로필 사진 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 탈잉 | required | 수업 장소·상세 주소 | sources.content.facts.location/disclosure | 장소의 사실과 공개 범위, 채널별 정확 필드 구분 |
| 탈잉 | required | 정산 정보 — 탈잉에서 본인 직접 입력 | 저장 안 함 | 외부에서 강사가 직접 입력; 민감 값 수집 금지; plan.prerequisite_status 및 필요한 최소 확인 근거만 |
| 탈잉 | required | 사용자 확인 — 2026년 11월 27일 | 저장 안 함 | 조사일은 설계 근거 메타데이터; 업무 입력/원본 DB 필드 아님 |
| 탈잉 | optional | 클래스 요약 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 탈잉 | optional | 승인 메시지 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 탈잉 | optional | 태그 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 탈잉 | optional | 유튜브 영상 | sources.content.facts.links | 공개/사용 허용 URL만; 채널별 링크 위치/용도 및 승인값은 plan |
| 탈잉 | optional | 클래스 공지사항 | 저장 안 함 | 채널 고유 표현·옵션/규칙; plan에서 해당 업무 값/제약으로 관리 |
| 탈잉 | optional | 이력 | sources.content.facts.experience | 강사 학력/경력 사실, 수집 최소화; 공유 프로필 영향/채널 구조는 plan |
| 숨고 | required | 활동명 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 숨고 | required | 한 줄 소개 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 숨고 | required | 서비스 상세 설명 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 숨고 | optional | 질문답변 5개 | sources.content.facts (확정된 재사용 사실만) | 질문답변 문구/순서 등 채널 표현은 plan |
| 숨고 | optional | 제공 서비스 선택 | sources.content.facts.subject/delivery/audience | 서비스 분류·질문/대표 선택의 정확 대상/범위는 plan, 외부 서비스·프로필은 platform_objects |
| 숨고 | optional | 레슨 목적·대상 연령·성별·진행 방식 | sources.content.facts.subject/delivery/audience | 서비스 분류·질문/대표 선택의 정확 대상/범위는 plan, 외부 서비스·프로필은 platform_objects |
| 숨고 | optional | 사진·유튜브 영상 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 숨고 | optional | 연락 가능 시간·직원 수·외부 링크 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 프람피 | required | 프로필 제목 최대 30자 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 프람피 | required | 전문가 활동명 최대 20자 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 프람피 | required | 프로필 사진 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 프람피 | required | 주소 | sources.content.facts.location/disclosure | 장소의 사실과 공개 범위, 채널별 정확 필드 구분 |
| 프람피 | required | 진행 방식 | sources.content.facts.delivery | 수업 제공 방식/모집 형태 구분, 채널별 선택은 plan |
| 프람피 | required | 전문가 소개 | sources.content.facts.instructor_profile | 재사용할 강사 소개 사실만; 외부 공유 프로필의 현재 상태는 정확 객체/history, 변경은 영향 범위 확인 |
| 프람피 | required | 분야별 소개 | sources.content.facts.subject/delivery/audience | 서비스 분류·질문/대표 선택의 정확 대상/범위는 plan, 외부 서비스·프로필은 platform_objects |
| 프람피 | required | 커리큘럼 | sources.content.facts.curriculum | 회차 순서/내용/시간 의미; 채널별 회차 구성 변환은 plan |
| 프람피 | required | 비용 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 프람피 | optional | 학력 | sources.content.facts.experience | 강사 학력/경력 사실, 수집 최소화; 공유 프로필 영향/채널 구조는 plan |
| 프람피 | optional | 경력 | sources.content.facts.experience | 강사 학력/경력 사실, 수집 최소화; 공유 프로필 영향/채널 구조는 plan |
| 프람피 | optional | 포트폴리오 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 프람피 | optional | FAQ | sources.content.facts (확정된 재사용 사실만) | 질문답변 문구/순서 등 채널 표현은 plan |
| 프람피 | optional | 포트폴리오 영상 설명 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 뮬 | required | 레슨 구분 | sources.content.facts.subject | 공통 분야와 플랫폼 분류 코드 분리; plan의 실제 선택값 |
| 뮬 | required | 제목 | sources.content.facts.title | 레슨 사실이면 원본, 글자 수/플랫폼 문구는 plan |
| 뮬 | required | 지역·주소 | sources.content.facts.location/disclosure | 장소의 사실과 공개 범위, 채널별 정확 필드 구분 |
| 뮬 | required | 수강료 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 뮬 | required | 본문 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 뮬 | required | 전화번호 | sources.content.facts.contact/disclosure | 공개하려는 최소 연락 수단만 명시 확인; 인증/정산 연락처와 분리 |
| 뮬 | required | 새 글 작성 시 약관 동의 | 저장 안 함 | 강사가 외부에서 직접 동의; 약관 동의 대행/자동화 가정 금지; 완료 상태·최소 근거만 |
| 뮬 | optional | 팩스 | sources.content.facts.contact/disclosure | 공개하려는 최소 연락 수단만 명시 확인; 인증/정산 연락처와 분리 |
| 뮬 | optional | 메인 사진 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 뮬 | optional | 본문 이미지·동영상 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 뮬 | optional | 홈페이지 | sources.content.facts.links | 공개/사용 허용 URL만; 채널별 링크 위치/용도 및 승인값은 plan |
| 뮬 | optional | 사운드클라우드 링크 | sources.content.facts.links | 공개/사용 허용 URL만; 채널별 링크 위치/용도 및 승인값은 plan |
| 힙합플레이야 | required | 제목 | sources.content.facts.title | 레슨 사실이면 원본, 글자 수/플랫폼 문구는 plan |
| 힙합플레이야 | required | 본문 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 힙합플레이야 | required | 카테고리 | sources.content.facts.subject | 공통 분야와 플랫폼 분류 코드 분리; plan의 실제 선택값 |
| 힙합플레이야 | optional | 사진 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 힙합플레이야 | optional | 동영상 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 힙합플레이야 | optional | 오디오 첨부 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 힙합LE | required | 제목 | sources.content.facts.title | 레슨 사실이면 원본, 글자 수/플랫폼 문구는 plan |
| 힙합LE | required | 가격 | sources.content.facts.price | 금액·통화·단위·회차·시간·세금 의미; plan에 가격 변환 및 실제 승인값 |
| 힙합LE | required | 본문 | sources.content.facts.description | 확정 사실을 원본에, 채널별 생성 본문/규격은 plan |
| 힙합LE | optional | 레슨 분류 | sources.content.facts.subject | 공통 분야와 플랫폼 분류 코드 분리; plan의 실제 선택값 |
| 힙합LE | optional | 썸네일·사진 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |
| 힙합LE | optional | 동영상·외부 링크 | sources.content.attachments; assets | 원본의 자료 참조·권리, 채널별 사용 역할/순서/규격은 plan; 외부 URL은 허용 링크 |

## 플랫폼별 식별과 인증 경계

### 크몽
- 정확 상품과 전문가 계정은 별도; 실제 외부 ID 미확인
- 심사 접수와 공개/모집 구분
- 가격 패키지/옵션/회차, 매체 역할; 동일 계정 한도는 규칙/효과 claim
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 탈잉
- 클래스/튜터/일정 구분; 클래스명·날짜는 식별 키 아님
- 심사 접수와 오픈/모집 구분
- 회차·시간/수강료; 동일 클래스 적용 관계 확인 전 영향 변경 보류; 정산 직접
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 숨고
- 공유 고수 프로필과 개별 제공 서비스 구분; 공통 프로필 source_id=NULL
- 정확 서비스/프로필 저장 반영, 미리보기≠공개
- 대표 서비스·카테고리 질문·공유 프로필의 범위 확인
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 프람피
- 전문가 프로필과 분야/지역/경력 관계; 단계 URL은 ID 아님
- 등록 저장과 공개/분야 연결 별도
- 공유 프로필에 직접 source 연결 안 함; 분야 객체 식별 불명은 hold
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 뮬
- 게시판과 공고 ID 범위 검증; 목록 번호=상세 ID 단정 금지
- 기존 글 갱신과 새 글 등록 별도; 정확 효과/시각 관측
- 본문/메인사진 역할, 연락처 공개 범위, 약관 직접, 갱신 조건/간격
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 힙합플레이야
- 게시판+글 ID 후보; 이동/수정 시 동일성 미검증
- 등록/공개 결과 독립 확인
- 글 옵션/첨부; 가입·게시 간격 충돌 미확정
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

### 힙합LE
- 레슨 글 ID·계정 범위 및 소유권 확인 전 보류
- 정확 작성/공개 결과 독립 확인
- 유사 게시 간격, 계정 대리사용 금지의 적용 범위; 권한 확인 전 live 금지
- 계정 식별·관리 연결과 일시 접근 문맥을 구분한다. 업무별 공식 대행 허용/정확 native ID 및 실제 저장 응답은 미확인; 기본 인증 비밀 보존 없음.

## 결정과 미결정

| ID | 상태 | 내용 |
|---|---|---|
| D01 | existing_accepted_direction | 최신 원본만 보존, 수락 작업의 승인값/필요 근거만 별도 동결 |
| D02 | existing_accepted_direction | 원본 1:N 관리 등록물, 정확 관리 등록물 0..1 원본; 공유 프로필 직접 연결 없음 |
| D03 | design_boundary | 기본 장기 비밀 저장 없음; 외부 계정 식별/관리 연결과 일시 인증 문맥 구분; 조건부 vault/opaque ref 검토 |
| D04 | existing_design_direction | 정확 계정/객체/단계 및 독립 관측으로 외부 효과 확인; 조회 실패/효과 불명/심사/공개 별도 |
| D05 | open_product_decision | 동일 외부 계정 활성 연결 1인 제약은 R05 권장 의견, R01 승인 전 강제하지 않음 |
| D06 | open_evidence_gate | 7개 플랫폼 native identity namespace, 실제 반환·검증값, 업무별 허용 및 재사용 가능한 공식 위임 미검증. 확인 전 live 및 비밀 저장 불가 |
| D07 | open_design_gate | 원본 공통 사실과 반복 사용할 채널 전용 설정의 경계: 공통 사실 명시 저장 후 해당 준비 재검증, 채널 표현 기본 plan. 채널 전용 사용자 선호를 향후 업무에도 유지해야 하는 경우만 source의 typed 설정 필요성을 별도 검토; 현재 새 테이블 결정 없음. |
| D08 | open_evidence_gate | 보존 기간·권리·물리 삭제, 외부 계정 식별 정보 저장 허용, 자료 제약/실제 PostgreSQL 동시성 검증 필요 |
| D09 | open_source_discrepancy | R02 보고서 96과 배열 86 불일치. 보고값 보존, 실제 86 매핑; 추가 10개가 존재한다는 근거 없음. R02 확인 전 전수 검증 주장 금지. |

## 최신 R4 반영 시 유의

- R03 후속 SAVE_SOURCE 미해결 관련 명령 범위와 수락 원자 경계, 저장 선행 stale/수락 선행 동결 유지; V5.1 commands.scope/receipt와 source_id/work_request_id 후보에 연결. V4 13개 구조를 채택하지 않음.
- 가격/공유 관계의 W 준비·승인 전 영향 변경 제한; 실행 직전 재검증; 결합 불명은 보류
- 보류/제외는 미수락 처분, 실패/잔여 효과 아님. R 후속 안내 및 명시 새 요청, 신규 승인; 이전 기록 불변
- 정확 링크/해제에 V5.1 source_id CAS + 최신 binding event + 명령 영수증. 기존 source_object_links 물리 참조는 대체, 1:N 방향 유지.
- 조건부 credential_bindings의 '14번째'는 13개 기반 잔류 문구. 기본 12개 기준 단일 추가라면 13개; 실제 필요성 미확정.

## 검증

- 플랫폼 7, 관측 ID 374/374, 입력 묶음 86, 플랫폼 업무 44, 필드군 38; DB 참조 오류 0.
- 원본 직접 읽기와 정적 참조/집계 검증만 수행. 96 대 86 불일치, 전체 leaf 의미 정규화, 공식 DB/CI/외부 시험은 남음.
