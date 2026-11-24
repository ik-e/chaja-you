# R03 크몽형 모의 등록 PoC

2026-11-24 사용자의 직접 구현 요청에 따른 개인 실험입니다. 팀 Phase·TASK-031의 구현 보류나 제품 승인을 변경하지 않습니다. 실제 크몽 연결은 없고 모든 작업은 모의 접수입니다.

## 실행

저장소 루트(`C:\Users\최두나\Desktop\python\chaja-you`)에서 실행할 때는 아래 한 줄을 사용합니다. 스크립트가 PoC 폴더로 이동하고 필요한 가상환경을 준비합니다.

```powershell
.\docs\members\R03\workspace\test\start.ps1
```

직접 명령을 입력하려면 **먼저 이 폴더로 이동**합니다.

```powershell
cd .\docs\members\R03\workspace\test
uv venv .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
```

브라우저에서 http://127.0.0.1:8765 를 열고 시험 세션 시작 → 이미지와 원본 입력 → 미리보기 JSON의 빈 필드 수정 → 저장·검증 → 승인·모의 등록 순서로 사용합니다. API 문서는 `/docs`입니다. 주어진 사실이 없는 칸은 자동 생성하지 않습니다. 개발용 로컬 시험 세션이며 외부 공개 서버 인증으로 사용하면 안 됩니다.

기본 실행기는 **simulator**입니다. 서버에서 영수증·상태·가격·승인·중복 방지 흐름을 시험하며 브라우저 자동화 성공을 뜻하지 않습니다. 준비된 원본의 가격은 300000원, 4회, 90분이어야 합니다. 각 패키지의 제목·설명·기간·수정 횟수·준비물/강의실 제공 여부를 사용자가 입력해야 합니다.

## 선택 연동

LLM은 `LLM_BASE_URL`(OpenAI 호환 API의 /v1까지), `LLM_API_KEY`, `LLM_MODEL` 환경변수를 설정하면 prepare 때 호출합니다. 기본값에서는 원본을 그대로 옮기는 수동 모드이며 AI 실행으로 표시하지 않습니다. 모델이 반환한 문안도 사용자 승인 전 초안입니다.

Skyvern SDK를 별도로 설치하고 환경을 구성한 뒤 `POC_RUNNER=skyvern`으로 실행할 수 있습니다. `POC_BASE_URL`은 127.0.0.1 또는 localhost만 허용됩니다. 2026-11-24 로컬 모의 페이지에서 Skyvern 브라우저 입력·이미지 첨부·모의 제출·영수증 일치를 확인했습니다. 실제 크몽 입력과 유료 모델 호출은 검증되지 않았습니다.

```powershell
uv pip install --python .venv/Scripts/python.exe 'skyvern[local]'
$env:POC_RUNNER='skyvern'
```

참조: https://github.com/Skyvern-AI/skyvern/blob/main/docs/sdk-reference/complete-reference.mdx

## 검증과 제한

```powershell
.venv/Scripts/python.exe -m pytest -q
```

테스트는 TC-01~13의 서버 계약과 추가 세션 격리를 검사합니다. 화면 기반 Skyvern 입력, LLM 정확성, 실제 플랫폼은 별도 검증 대상입니다. 이미지 본문 형식과 5MB 제한은 검사하지만 실제 크몽 규격의 모든 해상도·옵션을 재현하지 않습니다. 모의 폼은 승인된 필드 JSON과 이미지로 접수하는 최소 형태입니다. SQLite에는 문서·승인·작업·영수증을 종류별 JSON 레코드로 보관합니다. 재시작 시 실행 중 작업 자동 재시도는 하지 않습니다. 데이터는 git에서 제외한 `data/` 아래에 저장됩니다. 사용자·사진·문안에는 시험 데이터만 사용하세요.

현 구현은 단일 로컬 사용자용입니다. 대조실험에서 사용자 직접 시간·클릭 수·모델 비용을 자동 계측하는 기능과 실제 사이트용 인증·세션 저장은 후속 작업입니다. 작업 이벤트 시각은 저장됩니다.

## 실제 크몽 실험용 분리 실행기 (조건부)

`live_kmong.py`는 모의 등록 API와 별도인 실험용 CLI입니다. 팀의 현재 단계에서는 실제 사이트 자동화가 보류되어 있으므로 기본적으로 실행이 차단됩니다. 화면 선택자와 드롭다운 값은 실제 크몽에서 끝까지 검증되지 않았습니다. `live_listing.example.json`을 `data/live_listing.json`으로 복사해 강사가 확인한 실제 내용, 가격, 계정 표시명, 화면의 정확한 옵션을 채우고 `content_approved`와 `image_rights_confirmed`를 `true`로 지정합니다. 원본 이미지는 `data/`에 두고 공개 저장소에 추가하지 않습니다. 모의 시험의 임의 문구와 가격은 사용하지 않습니다.

```powershell
cd .\docs\members\R03\workspace\test
Copy-Item .\live_listing.example.json .\data\live_listing.json
.venv\Scripts\python.exe .\live_kmong.py validate --listing .\data\live_listing.json --image .\data\cover.png
```

팀 실험 범위와 플랫폼 허용 경로를 확인한 후에만 `KMONG_LIVE_ENABLED=1`을 설정할 수 있습니다. `fill`은 강사가 직접 로그인하고 본인 공고 편집 화면을 연 다음, Skyvern이 문구·패키지·이미지를 입력합니다. 이 경로는 저장·제출을 누르지 않습니다. 최종 접수를 위한 `submit`은 추가로 `KMONG_SUBMIT_ENABLED=1`이 필요하며, 화면 대조와 현재 내용/이미지의 SHA-256 지문을 포함한 최종 승인 문구를 콘솔에서 다시 요구합니다. 버튼은 한 번만 누르고, 결과가 불명확하면 `data/live_submit_attempt.json`에 `unknown`을 남겨 자동 재시도를 막습니다. `review_pending`은 사용자가 크몽 관리 화면에서 심사 접수를 직접 확인했을 때만 기록합니다.

```powershell
$env:KMONG_LIVE_ENABLED='1'
.venv\Scripts\python.exe .\live_kmong.py fill --listing .\data\live_listing.json --image .\data\cover.png
$env:KMONG_SUBMIT_ENABLED='1'
.venv\Scripts\python.exe .\live_kmong.py submit --listing .\data\live_listing.json --image .\data\cover.png
```

현재 구현의 화면 입력은 Skyvern의 자연어 대상 탐색을 사용합니다. 실제 화면에서 리치 텍스트·드롭다운·이미지 업로드의 동작과 사이트 오류 표시를 사람이 대조해야 합니다. 테스트는 입력 검증·승인 지문·호스트 제한·중복 클릭 방지를 확인하지만 실제 크몽 동작이나 최종 심사 접수를 입증하지 않습니다.
