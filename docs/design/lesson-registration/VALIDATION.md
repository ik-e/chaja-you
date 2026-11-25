# 현행 설계 독립 검증

기존 검증기를 호출하는 경량 실행기. [현행 기준선](BASELINE-POLICY.md)과 [AI 인덱스](CURRENT-DESIGN.json)를 먼저 확인한다.

| suite | 검사 범위 |
| --- | --- |
| logical | V5 유한 상태 탐색 N=4,5 및 사용자 중단·승인 우회 반례 |
| data | V4.1 스키마와 프로필 V2의 기존 의미 검사 31개 |
| integration | 채택된 공통 V1의 14개 검사 및 결함 주입. 기존 WBS는 고정 스냅샷의 참조 무결성 검사 입력일 뿐 현재 일정이 아님 |
| trace | 현행 인덱스, 고정 스냅샷, TASK/승인/참조 정합성 |
| model | 공통 설계 방법론 검증 (제품 검증 아님) |
| implementation | 기존 bootstrap 및 표준 스키마 계약 시험 (합성) |
| all-design | logical/data/integration/trace만 실행 |
| markdown | 별도 선택 문법 검사. 과거 문서는 제외 |

```sh
node tools/run_current_design_validation.mjs --suite logical
node tools/run_current_design_validation.mjs --suite all-design --expected-sha <full-commit-sha>
node tools/run_current_design_validation.mjs --suite implementation
```

Node 22, Git 필요. model은 Python 3.12, implementation은 uv 및 Python 3.12 필요. 추적 검증은 고정 커밋 이력이 있는 checkout에서 실행한다. 실행기는 tracked 변경이 있으면 거부한다. 선택된 검사에 한해서 pass/fail/error를 기록하고, 대상 SHA와 실행기 blob, 하위 검사 관측값을 JSON으로 출력한다. 실제 제품 시험은 실행하지 않으며 승인 상태를 변경하지 않는다. --out은 선택적인 결과 파일 경로이다.

GitHub Actions: **Current design selective validation**에서 suite 및 full target SHA를 지정. 읽기 전용 권한, 정확한 커밋 checkout, 결과 artifact. 기존 과거 V0.7 manifest의 resume 검사는 현행 suite에 포함하지 않는다. 기존 공통 CI와 중복되는 검사는 필요할 때 독립 재실행할 수 있다.

현재 물리 설계/실제 provider/제품 수용 시험은 후속으로 명시적인 검사와 근거가 마련되면 추가한다. 과거 검사 결과와 제품 검증을 혼합하지 않는다.
