# 레슨 등록 MVP 테스트 환경 작업 공간

- 작업일: 2026-11-24
- 상태: 테스트 환경 구성 작업 배정안/브랜치, 실제 개발 작업은 담당자 실행 후 검증
- 목표: 실제 크몽 계정·실등록 정보 없이 합성 입력을 통해 테스트 데이터·모의 등록·오류 검증을 재현할 공용 기반 구성
- 기준: [기획안 V1.1](../../docs/artifacts/planning/lesson-registration-20261123/proposal-v1.1.md) · [최소 설계](../../docs/artifacts/design/lesson-registration-20261123/MVP-MINIMUM-DESIGN-V0.1.md)
- 오늘 배정안: [환경 작업 계약](../../docs/artifacts/design/lesson-registration-20261123/TEST-ENV-WORK-20261124.md)

## 작업 공간

| 위치 | 책임 | 오늘 산출물 |
| --- | --- | --- |
| [fixtures](fixtures/synthetic-lesson-001.json) | R02 오후 검증 | 합성 데이터·기대 결과·검증 결과 |
| [contracts](contracts/README.md) | R03 | 모의 등록 입력/결과·오류 정의와 인수 케이스 |
| [mock](mock/README.md) | R04 | 최소 필드 입력·첨부·결과·에러를 다루는 로컬 모의 페이지 |
| [tests](tests/README.md) | R03/R05 | pytest 환경 검사, 모의 등록 통합 테스트 |
| [ENVIRONMENT](ENVIRONMENT.md) | R05 | `uv` 환경 설치·검증·문서화 |
| [UV-AUDIT](UV-AUDIT-20261124.md) | R05 검토 | 기존 설정 검사와 실제 실행 증거 |

## 경계

- 오늘 **제품 F1/F2/F3 서비스 코드 구현, 실제 플랫폼 연동, 배포 스택 선정은 하지 않는다.**
- API 서버, DB, LLM 프레임워크, 브라우저 실행기 같은 미선정 컴포넌트는 생성하지 않는다.
- 브라우저 테스트가 필요하면 **정적 로컬 HTML·파일 입력·모의 오류**로 시작하며 외부 플랫폼을 조작하지 않는다.
- 새 Python 런타임 의존성은 현재 0개. 개발 검사에 필요한 `pytest`·`ruff`만 유지.
- 직접 계정·개인정보·비밀번호·실제 세션·실제 판매 조건 원본은 넣지 않는다.
- 각 담당자는 자기 TASK 브랜치에서 코드/실행 기록을 올리고, 공통 계약은 R03/R05의 상호 확인 후 반영한다.
- 완료 여부는 파일 생성이 아니라 **실행 명령 + 실제 결과 + 실패 사례 기록**으로 판정한다.

## 환경 재현

```bash
uv lock --check
uv sync --locked --group dev
uv run --locked pytest prototype/lesson-registration/tests -q
uv run --locked ruff check prototype/lesson-registration/tests
```

이 명령의 실제 CI 통과는 아직 확인되지 않았다.
