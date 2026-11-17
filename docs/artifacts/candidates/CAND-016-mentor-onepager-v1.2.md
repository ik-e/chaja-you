# 멘토 검토용 요약 — 시험장 부정행위 위험 탐지·감독 지원 V1.2

**상태:** R01 독립 기획 후보(미채택) · **V1.0/V1.1 원문 유지** · [상세 V1.2](CAND-016-v1.2-proposal.md) · [대안 조사 원장](CAND-016-evidence-review-2026-11-16.md)

**도입 기관:** 대면시험 운영기관 · **실사용자:** 현장 시험감독관 · **협업:** 판별 전담요원·시험 운영본부

| 멘토 판단 항목 | 이번에 좁힌 주장 |
|---|---|
| **타깃 상황** | 종이시험 등 대면시험 중 스마트안경/미허가 전자기기가 의심되지만 단정할 수 없고, 감독관이 확인·보류·이관 및 기록을 결정해야 하는 순간 |
| **P1 발견** | 탐지·광학 검사·영상 AI 자체는 이미 존재. 무송신/미지원 기기·외부 신호·잘못된 귀속 등 **실측 한계**가 남음 |
| **P2 판단** | 공식 규정과 전담인력·상용 사건 검토 절차도 이미 존재. **잔여 판단 부담의 빈도와 손실은 아직 미측정** |
| **P3 인계/기록** | 보고서·타임라인도 기존 제품에 존재. 일부 대면 교실의 CCTV 부재는 확인되나 **재질의/재구성 손실의 규모는 미측정** |
| **문제 정의** | 제한된 관측을 사실/추정/미확인·시험별 규정·조치로 연결하는 과정에서 부적절 개입과 인계·사후 부담이 **실제로 남는지, 개선 가능한지** 검증 |
| **F1 징후 선별** | 수동/승인 센서 이벤트 출처·불확실성 구분, 통제 실측에서 개선될 때만 적용 |
| **F2 판단·대응** | 시험별 규정 버전 + 확인/보류/전담요원 이관. 부정행위·학생 자동 확정 금지 |
| **F3 기록·재구성** | 사실·추정·검토자·조치·시각의 타임라인. 기존 조서보다 못하면 제외 |

## 이미 존재하는 경쟁·대체 수단

- **온라인:** [Monito](https://monito.co.kr/) (스마트안경 검증·AI 감독), [SmarterProctoring](https://help.smarterproctoring.com/en/articles/13045699-what-flags-are-detected) (웨어러블 플래그), [ProctorU](https://support.proctoru.com/hc/en-us/articles/360041137691-How-to-Review-an-Incident-Report) (사건 기록/보고).
- **대면:** [Innovatiview GuardView/CamView](https://www.innovatiview.com/products/camview) (반입검사·다중 시험장 CCTV/AI 관제), [VigIA](https://vigia.interbantu.com/) (행동 경고/영상).
- **소규모 구현:** [ExamGuard](https://github.com/epoko77-ai/examguard) (BLE·광학 검사), [Exam-Proctor-System](https://github.com/shubham5177/Exam-Proctor-System), [ExamShield](https://github.com/vandanamarripati/Exam_Proctoring) (영상·센서·로그).
- **공식 기준:** [교육부 시험별 대응](https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=340&boardSeq=107580&lev=0); [한국산업인력공단 11/13 현장 설명](https://webzine.hrdkorea.or.kr/section/press/view?id=13802&page=1).

**차별성의 현재 상태: 미입증.** 기능 조합 자체는 이미 존재한다. 남는 가치가 있다면 특정 대면시험의 **오인·적절한 이관·기록 품질·총업무시간**에서 기존 지침+비AI 체크리스트보다 실제 개선하는지로만 주장한다.

## 8주 안에 확인할 실험

| 대조군 | 내용 |
|---|---|
| A | 해당 시험 공식 지침 + 기존 보고 양식 |
| B | A + 비AI 체크리스트 |
| C | B와 **동일한 관측 정보량** + 사건 카드/규정·이관·기록 |
| D(조건부) | C + 통제 실측으로 검증된 단일 BLE/Wi-Fi 입력 |

**탐색적 12~20개 모의 사건**에서 필요한 확인 누락·부적절 개입·적절한 이관·사실/추정 혼동·기록 누락·재구성 시간·**총업무시간**을 측정한다. B 대비 C의 개선이 없거나 D의 증분 효과가 없으면 기능 축소/대체·주제 재검토. 승인 없는 실제 시험장 센서/녹화 시연 금지.

**멘토에게 확인할 질문:** 대면시험 감독관에게 현재 지침·전담요원으로도 해결되지 않는 *어떤 빈번한 손실*이 있는가? 비AI 체크리스트를 넘는 실질적인 개선을 실험으로 입증할 수 있는가?

[V1.2 상세](CAND-016-v1.2-proposal.md) · [근거 기록](CAND-016-evidence-review-2026-11-16.md) · [V1.0 동결본](CAND-016-v1.0-snapshot.md)
