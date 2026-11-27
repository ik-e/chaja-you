# R05 통합 사용자 스토리 V3.1 검토 의견

2026-11-27 · R05 · 공개 자료와 기존 플랫폼 조사 기록을 대조한 문서 검토

V3.1의 화면 흐름을 유지하면서, 플랫폼별 제약 때문에 승인 화면이나 완료 판정이 달라지는 네 가지를 보완하는 의견이다.

## 1. 크몽 신규 등록 한도

**관련 흐름** · UJ-01·02 / W / `PS-PL01-CREATE`

- **문제와 근거** · 현재 준비 흐름은 계정·기존 등록물·중복을 확인하지만, 2026년 11월 27일부터 적용된 신규 등록 한도가 빠져 있다. 크몽은 계정당 판매 중·승인 대기 합계 100개, 하루 신규 승인 요청 5개를 안내한다. [크몽 공식 공지](https://kmong.com/support/expert-center/posts/817)
- **개선 방향** · 신규 등록을 승인하기 전에 한도에 걸리는지 확인한다. 한도에 걸리면 크몽 건만 보류하고 입력안을 보존한다. 조회할 수 없으면 **한도 미확인**으로 표시하고 크몽 공식 관리 화면에서 확인하도록 안내한다.

## 2. 크몽 수정 후 공개와 재검토

**관련 흐름** · UJ-03 / W·R / `PS-PL01-UPDATE`, `ER-20`

- **문제와 근거** · 완료 기준의 ‘심사 승인 후 실제 판매 상세 변경’ 문구는 수정 내용이 승인 이후에 공개되는 것으로 읽힐 수 있다. 크몽은 판매 중인 상품의 수정 내용이 먼저 노출된 뒤 추가 검토가 진행될 수 있으며, 동영상은 승인 후 반영된다고 안내한다. [크몽 서비스 편집 안내](https://kmong.com/support/expert-center/posts/680)
- **개선 방향** · 작업 준비·승인 화면(W)에서 변경 내용이 먼저 공개될 수 있음을 보여 준다. 진행·결과 화면(R)에는 **변경값 저장**, **현재 공개 여부**, **검토 결과**를 각각 표시한다. 동일 상품에서 설명은 공개됐지만 동영상은 승인 대기인 경우를 모의 검증에 추가한다.

## 3. 탈잉 가격 환산과 타 플랫폼 등록 조건

**관련 흐름** · UJ-01·02·07 / W / `PS-PL02-CREATE`, `ER-09`

- **문제와 근거** · R05 예시에서는 120분씩 6회, 총 15만 원을 탈잉의 시간당 입력값인 12,500원으로 환산했다. 동일 클래스를 다른 플랫폼에서도 운영하는 경우에는 가격 조건과 별도 계약 여부를 함께 확인해야 한다. [R05 보컬 레슨 입력 예시](https://github.com/ik-e/chaja-you/blob/8ecf2034ab3b5e3df385f3bac8b855306ed87b73/docs/artifacts/planning/lesson-registration-20261126/R05/vocal-lesson-input-examples.md) · [탈잉 공식 FAQ](https://talingtutorguide.oopy.io/27041f37-bd7f-8071-9a6e-d412f50e46a9)
- **개선 방향** · W에서 **원본 총액·플랫폼 입력 단위·환산 후 총액**을 함께 보여 준다. 회차나 패키지 구성이 달라 동일 클래스인지 판단하기 어렵거나 가격이 맞지 않으면, 값을 자동 변경하지 않고 탈잉 건만 확인 대상으로 남긴다.

## 4. 숨고 활동명 입력 규격 충돌

**관련 흐름** · UJ-03·07 / W / `PS-PL03-UPDATE`, `ER-09`, `ER-29`

- **문제와 근거** · 통합 설계에는 활동명 30자가 화면 관찰값으로 남아 있고, 숨고 공식 약관 제31조에는 공백 포함 2~20자와 변경 후 30일간 재변경 제한이 명시돼 있다. 30자를 검증 기준으로 적용하면 약관 범위를 벗어난 입력안이 통과할 수 있다. [차자유 플랫폼 업무 설계](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/review/lesson-registration/PLATFORM-WORK-V1.0.md) · [숨고 이용약관 제31조](https://soomgo.com/terms/usage/2026-11-19)
- **개선 방향** · 화면 관찰값과 공식 약관 기준을 함께 기록하고, 활동명이 20자를 넘으면 수정하도록 안내한다. 활동명 변경 가능 시점과 실제 화면 적용 여부는 운영사에 확인한다. 활동명 때문에 수정 가능한 다른 항목까지 막히지 않도록 해당 항목의 제한을 따로 처리한다.

## 검토 범위

공개 자료와 기존 조사 기록을 대조했다. 실제 계정에서의 저장·제출·공개 결과와 차자유의 대행 허용 여부는 미확인이다.

- [V3.1 화면 중심 사용자 흐름](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/review/lesson-registration/USER-STORY-SCREEN-FLOWS-V3.1.md)
- [V3.1 멘토 형식 사용자 스토리](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/review/lesson-registration/USER-STORY-MENTOR-V3.1.md)
- [V3.1 팀원 자료 통합 결과 및 판단 근거](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/review/lesson-registration/USER-STORY-INTEGRATION-REVIEW-V3.1.md)
- [V3.1 의미 검토 및 보완 결과](https://github.com/ik-e/chaja-you/blob/70ae8e7169c284ba71c4dcbcc0cde4415929d079/docs/review/lesson-registration/USER-STORY-SEMANTIC-REVIEW-V3.1.md)
