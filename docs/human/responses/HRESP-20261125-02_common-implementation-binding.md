# HRESP-20261125-02 · 공통 구현 설계 방향 수용

- 일자: 2026-11-25
- 권위: R01
- target: IB-01, IB-02, IB-03, IB-04, IB-05 / TASK-048
- action: approve
- 사용자 지시 원문: “너가 권장한 거에 대해 큰 문제 없어 보여 진행하면 될 것 같아”
- 대상: [검토한 공통 구현 결정](https://github.com/ik-e/chaja-you/blob/5876907585666c0389719d90331b2b231afea3d0/product/lesson-registration/contracts/IMPLEMENTATION-BINDING.json), [수정 후 검증](https://github.com/ik-e/chaja-you/actions/runs/45527624382)

## 적용 범위

R01이 IB-01~05 공통 구현 방향을 수용했다. 초기 공통 구현 경계는 공동 개발에 사용하되 담당자 확인이 필요한 세부 서명·실행 기술·공수 및 실제 제품 검증은 별도로 결정한다.

Python 3.12 Protocol 및 JSON 경계, 기존 JSON Schema 정본과 표준 검사, Storage/Runtime/Adapter 권한 분리, framework-neutral Viewer, 명시적인 provider 조립 원칙을 수용한다. 공통 코드 기준선을 제공하고 이후 담당자의 근거 있는 변경 의견을 추적한다. 공통 제품 dependency lock·프레임워크·DB·브라우저·viewer transport·실제 원자성/권한/모델 및 일정까지 확정한 것은 아니다. 팀원 수신·동의·구현 완료로 간주하지 않는다. 실서비스 실행 금지, 기존 TASK와 논리 정본 유지.
