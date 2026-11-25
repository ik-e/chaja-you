# Auto-Healing 구현 결과서 · 시험 준비

> DLV-09 · 12/18 제출 예정 · 2026-11-25 **사전 계획, Auto-Healing 실제 복구 시험 미실행**. 구현 결과서 완성 아님. [강사 가이드](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/guidelines/instructor-snapshots/snapshots/299a7016748aab57c2de9f03fd38a8b09df4c07e/Lecture/FinalProject/Doc/Step4/멀티에이전트_AutoHealing_적용가이드.html) · [공통 안전 계약](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · [보안 가드레일](AI_보안_가드레일_설계_문서.md).

## 1. 목적 및 범위

기술 적용은 핵심 Pain과 안전한 작업 연속성에 기여해야 한다. Auto-Healing은 시스템/연결 장애 감지→분류→허용된 복구 전략→재검증→기록을 의미한다. Step3 자기 성찰(후보 품질 보정), 단순 재시도, 안전 중단과 구분. 수락된 등록의 외부 효과 재실행·사용자 취소/재개/rollback 금지 유지.

## 2. 장애 유형 및 복구 전략 후보

| TC | 장애·주입 | 후보 처리 | 검증·판정 |
| --- | --- | --- | --- |
| AH-01 | H8/H9 조회 일시 네트워크 장애 | 제한된 읽기 재조회 | 같은 owner/job/revision의 실제 저장 view, 외부 효과 추가 0 |
| AH-02 | Viewer detach (인증 prestart) | H6 refresh·새 유효 grant로 인간 연결 회복 후보 | 기존 grant 거절, current generation, 실제 화면 재연결; worker 실행 아님 |
| AH-03 | PREP 모델 일시 불가 (prestart) | 안전 차단, 승인 전 새 재준비/제한된 대체 전략 후보 | 실제 모델 정상화·검증, stale 결과 무시, 임의 사실 0 |
| AH-04 | H7 응답 유실 | 동일 요청/key의 영속 수락 조회 | 동일 registration, 외부 실행 추가 0; 통신 확인 회복만 |
| AH-05 | 외부 효과 응답 유실 | fence·unknown·독립 읽기 근거, 외부 효과 재실행 금지 | 안전한 stopped/unknown, **복구 성공으로 계산하지 않음** |
| AH-06 | 서버 재시작/고아 job | 시작 시 중단·unknown 보존, 조회 정상화 | 자동 재개/재제출 0; 업무 복구와 서비스 조회 회복 구분 |
| AH-07 | 401/403·계정 불일치 | 차단·사람 확인 | 자동 인증 우회 0, 자동 복구 대상 제외 |

자동화 여부/전략/상한은 담당자 확인 및 시험 전 확정. 현재 R03의 동일 key HTTP 재조회·시작 recovery·redaction 시험은 [독립 run](https://github.com/ik-e/chaja-you/blob/ec8917c63eb13a3d81d3234220bb346cb666028f/docs/artifacts/runs/TASK-050-s8-http-20261125.json)으로 참고하되 전체 Auto-Healing 복구 성공률로 환산하지 않는다.

## 3. 구현 및 검증 절차

합성 장애 주입, 동일 code/fixture/environment, 장애 감지/분류/조치/재검증/종료를 run ID로 연결. 자동 복구 허용 대상 및 단계/시간 상한 사전 고정. 복구 불가/실패/사람 이관 사례 포함, 사용자 승인·외부 효과 가드 유지. 실제 구현/실행 명령은 미확정. 추가 업무 배정 아님.

## 4. 실행 기록과 결과

AH-01~07 모두 not_run (이 Auto-Healing 실험 기준). 자동 복구 대상 건수, 실제 시도·성공·실패·사람 이관, 감지·복구 시간, 추가 호출/비용, 증거 및 재현 명령 미측정. 복구율은 사전에 자동 복구 대상으로 정한 주입 건수 중 재검증을 통과한 건수의 비율. 안전 중단·대체 응답·이관을 성공으로 합산하지 않는다.

## 5. 완료 전 확인

실제 적용할 전략·담당자·실패 출구·최대 반복/시간·시험 데이터 확정, 장애 주입 실행 및 로그/commit/환경/분모 확보 후 결과 문서로 갱신. 실제 제품 gate 22개와 운영 보안 검증은 별도 유지. 공식 양식/제출·접수 미확인.
