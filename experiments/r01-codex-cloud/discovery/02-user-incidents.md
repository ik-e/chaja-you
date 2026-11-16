# 02 — 공개 사용자 사건 기록

- 조사 확인일: 2026-11-16 (KST)
- 수집 방식: 공개 GitHub issue/comment의 읽기 전용 열람 및 R01 기존 조사 자료 대조. 무단 크롤링, 사용자 메시지, 인터뷰 요청은 하지 않았다.
- 해석 주의: 아래는 게시자 자신의 재현·사용 보고다. 조사자가 독립 재현한 결함이나 시장 빈도 통계가 아니다. 계정 수는 조직/사람 수와 같다고 볼 수 없다.

## 사건 1 — OpenSpec Store에서 한 변경을 여러 저장소에 적용하기 어려움

- source_url: [OpenSpec #725 — Multi-repository / microservice spec management](https://github.com/Fission-AI/OpenSpec/issues/725), [renatospaka 댓글](https://github.com/Fission-AI/OpenSpec/issues/725#issuecomment-5342286611)
- published_or_updated: issue 2026-02-18 생성, 2026-09-08 갱신; 사용자 댓글 2026-08-19
- checked_at (KST): 2026-11-16
- user_role (확인/추정): 실제 cross-repository migration을 수행했다고 1인칭 보고. 기술 구현자/프로젝트 역할은 추정, 직함과 팀 규모 미확인.
- task_context: planning Store와 platform, infra, processor 등 세 구현 저장소에서 한 마이그레이션을 하나의 권위 있는 변경으로 계획하려 함.
- trigger: 네 저장소를 workset에 묶고 Store change를 만들어 같은 계획으로 여러 저장소에 적용하려 함.
- observed_problem: 작성자는 OpenSpec 1.5.0으로 시험하고 1.8.0 구현을 검토한 결과 apply의 allowedEditRoots가 현재 projectRoot에만 묶여 있다고 보고함. Store/workset이 열려 있어도 단일 apply의 수정 범위가 다중 저장소로 확장되지 않는다고 설명.
- workaround: 저장소별 OpenSpec change를 따로 만들거나 외부 filesystem 권한을 주는 선택지가 있었고, 권한 경계를 우회하므로 후자는 거부했다고 보고. 저장소별 변경은 독립된 계획 권위가 생길 위험을 언급.
- cost (evidenced/unknown): 중복된 계획 권위와 조정 위험은 게시자가 설명. 소요 시간, 재작업 횟수, 실제 잘못된 변경은 unknown.
- existing_tool: OpenSpec Store/workset; issue 작성자는 central planning은 잘 작동한다고도 보고함.
- evidence_strength: 강한 자기 보고와 버전/구현 경로를 제시한 issue comment. 독립 재현·다른 팀에서의 빈도 측정은 없음.
- uncertainty: 이 댓글의 계정이 독립 조직·고객 한 명인지, 1.8 이후 현재 버전에서도 동일한지, 특정 호스트 권한 설정의 영향은 확인하지 않음.

## 사건 2 — 여러 저장소 중 일부만 처리하고도 적용 완료로 보고된다는 제보

- source_url: [OpenSpec #725](https://github.com/Fission-AI/OpenSpec/issues/725), [m13v 댓글 — partial apply](https://github.com/Fission-AI/OpenSpec/issues/725#issuecomment-5447038536), [후속 설명](https://github.com/Fission-AI/OpenSpec/issues/725#issuecomment-5580123829)
- published_or_updated: issue 2026-02-18 생성, 2026-09-08 갱신; 관련 댓글 2026-08-28 및 2026-09-08
- checked_at (KST): 2026-11-16
- user_role (확인/추정): 다중 저장소 적용 문제를 보고한 계정. 실제 운영자 역할은 추정, 직함/팀 규모 unknown.
- task_context: 한 spec을 네 저장소로 전달하는 cross-repository 적용.
- trigger: 대상 저장소 중 하나에서 오류 또는 계획 저장소 비접근이 발생.
- observed_problem: 댓글은 네 저장소 중 세 곳만 반영되고 오류 난 하나는 건너뛰었는데 전체 상태가 applied로 보고됐다고 주장. 후속 댓글은 계획 저장소 접근이 끊긴 상황에도 보이는 작업을 처리하고 완료로 표시될 수 있다고 설명.
- workaround: 보고자의 구체적인 복구 절차는 댓글에 없음. OpenSpec maintainer는 수동으로 저장소/작업 그룹을 명시하거나 각 구성 저장소에서 Store를 read-only 참조하는 local root를 쓰는 현재 모델을 설명.
- cost (evidenced/unknown): 적용 상태가 실제보다 완전하다고 보이는 위험과 spec drift를 보고. 실제로 어떤 고객 변경이 빠졌는지, 피해액/복구 시간은 unknown.
- existing_tool: OpenSpec Store/workset은 저장소들을 열어 보여주지만 maintainer 설명상 대상 repo 추론·작업 분배·모든 대상 성공을 강제하지 않음.
- evidence_strength: 공개 이슈의 구체적인 전부/부분 적용 주장 및 maintainer의 현재 동작 범위 설명. 조사자가 실행으로 확인하지 않음.
- uncertainty: 같은 이슈 안의 m13v 댓글들은 같은 계정으로 중복 인용하지 않음. 계정이 서로 다른 고객인지, 댓글의 적용 결과를 독립 확인할 자료가 있는지 unknown.

## 사건 3 — OpenSpec 검증은 통과했지만 archive 시 늦게 막힌 cross-change 의존성

- source_url: [OpenSpec #1112 — MODIFIED target validation timing](https://github.com/Fission-AI/OpenSpec/issues/1112), [73-change project workaround report](https://github.com/Fission-AI/OpenSpec/issues/1112#issuecomment-5937920619)
- published_or_updated: issue 2026-05-21 생성, 2026-10-06 갱신; 댓글 2026-10-01
- checked_at (KST): 2026-11-16
- user_role (확인/추정): 원 작성자 luigileap은 본인 프로젝트에서 두 번 겪었다고 보고. 개발/명세 작성 맥락은 확인, 직함·프로젝트 규모 unknown. 댓글의 jean-sturacci는 73-change 프로젝트의 외부 gate 구축을 보고.
- task_context: 변경안이 MODIFIED로 다른 change에서 추가한 요구사항을 수정하거나, 새로운 제목을 기존 요구사항 수정으로 오분류.
- trigger: 변경 spec을 작성하고 validate --strict로 확인한 뒤 archive 단계에서 base spec에 요구사항 헤더가 없다는 사실이 드러남.
- observed_problem: 원 작성자는 두 유형을 6일 안에 겪었다고 보고. 첫 경우 잘못된 MODIFIED 분류가 2026-05-15부터 21일까지 검출되지 않았고, 두 번째는 구현 PR이 이미 production에 반영된 뒤 sibling change를 canonical spec으로 archiving하려다 중단됐다고 설명. issue 재현 예제에서 validate는 valid, archive는 중단으로 나뉨.
- workaround: 사후 forensics와 cross-change unblock이 필요했다고 보고. 별도 댓글 작성자는 프로젝트 local blocked_by 필드와 archive deny-gate를 만들었으며 첫 버전의 시간 초과를 27.2초에서 0.8–3.9초로 줄였다고 보고.
- cost (evidenced/unknown): 두 사건, 6일 간격 및 구현 PR 후 수 주 늦게 검출된 사례, 수동 분석/차단 해소 필요가 게시자 보고에 기록됨. 실제 인시·복구 금액은 unknown.
- existing_tool: OpenSpec validate가 형식 유효성을 통과시켰지만 archive는 요구사항 target을 검사해 파일 변경 전에 막음. 일부 방어는 있으며 실패 발견 시점이 늦다는 주장.
- evidence_strength: 실제 재현 명령과 같은 프로젝트의 두 사례가 기재된 상세 issue. 다른 프로젝트의 gate 수치는 단일 프로젝트 작성자 보고. 조사자 독립 재현 아님.
- uncertainty: 보고 프로젝트의 브랜치 규칙, 릴리스 버전별 동작, 현재 버전에서 validate가 바뀌었는지, 일반 사용자 빈도는 unknown. 관련 댓글 작성자도 OpenSpec 기본 기능이 아니라 자체 gate를 사용했다고 구분.

## 사건 4 — OpenSpec 시나리오 이름 바꾸기가 누락으로 오인되어 archive를 막음

- source_url: [OpenSpec #1697 — Cannot rename a scenario](https://github.com/Fission-AI/OpenSpec/issues/1697), [Q-back의 1.14.3 보고](https://github.com/Fission-AI/OpenSpec/issues/1697#issuecomment-6415319268), [단일 저장소 retrospective](https://github.com/Fission-AI/OpenSpec/issues/1697#issuecomment-5349532792)
- published_or_updated: issue 2026-08-19 생성, 2026-10-26 갱신; Q-back 댓글 2026-10-26, retrospective 댓글 2026-08-20
- checked_at (KST): 2026-11-16
- user_role (확인/추정): RawanS는 재현 입력과 결과를 제시한 OpenSpec 사용자. 직무/조직 규모 unknown. Q-back은 1.14.3에서 같은 증상이라고 보고.
- task_context: 기존 동작을 보존하면서 시나리오 설명을 더 정확한 제목으로 변경하고 새 분기를 추가.
- trigger: MODIFIED block에서 이전 시나리오를 새 제목으로 적어 validate/archive 실행.
- observed_problem: 제목이 달라진 기존 시나리오를 삭제로 계산해 validate 오류와 archive 중단이 발생했다고 보고. Q-back은 1.14.3에서도 영향이 있다고 적음.
- workaround: Q-back은 모든 delta를 main specs에 수동 반영한 뒤 archive --skip-specs를 실행한다고 보고. 이는 동기화 단계를 우회함.
- cost (evidenced/unknown): 수동 반영과 정상 archive 흐름 우회는 보고됨. 시간·재작업 비용은 unknown. 다른 댓글의 단일 repo retrospective는 75개 MODIFIED change를 재생해 29개(39%)가 막혔고, id 없는 26건 중 16건은 의도적 rename/delete, 4건은 사람이 잡은 우발 누락, 2건은 배포 뒤 복구 사례였다고 주장. 표본은 한 프로젝트이며 독립 검증 안 됨.
- existing_tool: OpenSpec validator/archive guard는 accidental omission을 막는 안전 기능. 같은 guard가 의도된 rename을 구분하지 못한다는 사용자 보고.
- evidence_strength: 구체 재현과 버전, 우회 방식을 제시한 보고. 1.14.3 상태는 사용자 주장으로만 확인, 현재 실행으로 재현하지 않음.
- uncertainty: 연결된 최근 댓글들이 같은 프로젝트/조직인지 불명. #1809 관련 개선이 현재 증상 범위에 미친 영향과 실제 처리시간은 unknown.

## 사건 5 — Codex CLI에서 Allow always 이후 같은 MCP 승인이 반복됨

- source_url: [Codex #16911 — Constant ask for MCP Tool approvals](https://github.com/openai/codex/issues/16911), [Shunsuke2929의 후속 보고](https://github.com/openai/codex/issues/16911#issuecomment-6568876726)
- published_or_updated: issue 2026-04-06 생성, 2026-11-02 갱신; 후속 댓글 2026-11-02
- checked_at (KST): 2026-11-16
- user_role (확인/추정): 원 작성자는 Codex CLI 0.118.0, Pro, gpt-5.4, ida-pro-mcp를 썼다고 양식에 기재. 댓글 작성자는 Windows의 local MCP를 매일 쓴다고 보고. AI 도구 직접 사용자임은 확인, 직무/숙련도 unknown.
- task_context: 연속 작업에서 이미 Allow always를 선택한 도구를 다시 호출.
- trigger: Codex CLI 0.117.0 이후 보고자 환경에서 동일 MCP 도구를 반복 사용.
- observed_problem: 원 작성자는 매 두 번째 tool call 같은 승인 요구가 돌아올 때가 있다고 표현. 댓글 작성자는 같은 세션에서 몇 번 호출마다 다시 나타나고 장시간 실행이 몇 분마다 멈춘다고 보고.
- workaround: 원 작성자는 0.116.0으로 되돌리면 이전 동작으로 돌아가지만 Allow Always 선택 기능은 잃는다고 함. 댓글 작성자는 지원되는 pre-approval 방법을 질문했으며 완료된 우회는 제시하지 않음.
- cost (evidenced/unknown): 장시간 실행 정지와 터미널을 계속 지켜보는 감독 요구는 댓글의 자기 보고. 실제 시간/금전 비용은 unknown.
- existing_tool: Codex Allow always 승인 옵션. 제보자 설정에서 지속되지 않았다고 보고됨.
- evidence_strength: 같은 issue thread의 두 계정이 상세 동작과 빈도를 각각 보고. 실행 환경/버전이 다르고 독립 조직 여부 unknown. 조사자가 재현하지 않음.
- uncertainty: 현재 Codex 버전에서 해결됐는지, 승인 모드·MCP elicitation schema 차이인지, 영향 사용자 비율은 확인하지 않음.

## 사건 6 — BMad headless 실행이 endpoint 하나의 분석을 넓은 코드베이스 조사로 확장

- source_url: [BMad Method #3194](https://github.com/bmad-code-org/BMAD-METHOD/issues/3194)
- published_or_updated: 2026-11-13 생성·갱신
- checked_at (KST): 2026-11-16
- user_role (확인/추정): alvarofvr는 BMad v6.12.1, Claude Code headless 호출을 실행했다고 보고. 아키텍처/개발 작업자 역할은 추정, 직함 unknown.
- task_context: brief에 지정한 REST endpoint 하나를 분석하고 기술 분석 문서를 만들려 함. 읽기 전용으로 약 700개 저장소 트리가 보이는 환경이었다고 설명.
- trigger: claude -p 형태의 비대화식 실행에서 BMad architecture를 호출.
- observed_problem: BMad이 headless 조사로 전환돼 3개 subagent가 광범위한 sweep을 시작했고, 한 endpoint만 보라는 범위가 framework/gateway/deployment layer 전반으로 넓어졌다고 보고. 다섯 시간인 Claude Code plan quota를 약 8분 만에 소진해 분석 초안도 끝나지 않았다고 기재.
- workaround: 사용자는 최소 prompt-loop 비교에서 endpoint 범위는 유지됐지만 약 110 calls/12M cached tokens가 들었다고 보고. 그 방식의 총 작업 완료 여부는 unknown.
- cost (evidenced/unknown): 게시자는 약 330 calls, 48M cached input tokens, 약 365k output tokens, 11 denied calls, 5시간 plan quota 소진을 기록. 정확한 현금 비용은 unknown이며 토큰/쿼터 수치는 재현 검증 안 됨.
- existing_tool: BMad architecture workflow와 Claude Code headless mode. BMad 공식 기능의 평균 비용으로 일반화할 수 없음.
- evidence_strength: 구성/명령/수치를 담은 구체적인 단일 사용자 사건.
- uncertainty: 해당 사용자의 프로젝트/호스트 설정, 정확한 재현 가능성, 이후 릴리스에서의 변경, 개인 요금제 비용은 unknown.

## 사건 7 — BATHOS 안전 가드가 안전한 Git 브랜치 작업까지 차단

- source_url: [BATHOS #39](https://github.com/taxideftis/bathos/issues/39)
- published_or_updated: 2026-09-11 생성, 2026-09-15 종료
- checked_at (KST): 2026-11-16
- user_role (확인/추정): Danto7632가 shell 출력과 패턴을 이용한 재현을 기록. 개발자 역할 추정, 직함 unknown.
- task_context: 문서 작업용 새 브랜치 생성과 merge된 브랜치 삭제.
- trigger: BATHOS careful guard의 Git danger pattern 검사.
- observed_problem: checkout -b를 강제 덮어쓰기 -B처럼, branch -d를 강제 삭제 -D처럼 차단했다고 설명. SQL 패턴에 필요한 대소문자 무시가 Git flag까지 적용된 원인 분석도 제시.
- workaround: 브랜치 생성은 git switch -c로 바꿀 수 있었지만 안전 삭제에는 같은 대체가 없어 -D를 쓰도록 안내해 guard 의도와 반대되는 위험을 키웠다고 주장.
- cost (evidenced/unknown): 세션이 막히고 더 위험한 명령을 안내받았다는 피해는 보고됨. 시간·실제 데이터 손실은 unknown.
- existing_tool: BATHOS guard는 위험 명령 차단을 제공; 이슈는 오탐 경계를 지적.
- evidence_strength: 재현 명령과 flag 대조표를 갖춘 구체 이슈. 상태는 closed지만 어떤 수정/릴리스로 해결됐는지 이번 확인으로 알 수 없음.
- uncertainty: 종료 사유, 수정 내용, 현재 버전의 동작은 unknown. 현재 결함이라고 주장하지 않음.

## 반례·잘 해결된 사례

### 반례 1 — OpenSpec guard가 실제 누락을 명확하게 막은 보고

- source_url: [OpenSpec #1669 — overlap between open changes](https://github.com/Fission-AI/OpenSpec/issues/1669)
- published_or_updated: 2026-08-15 생성, 2026-08-27 갱신
- checked_at (KST): 2026-11-16
- 게시자 ryandemelo는 Phase 0 stale-base guard가 validate와 archive에서 명확한 오류, exit 1, 변경 파일 0개로 작동했다고 적음. 이것은 OpenSpec guard가 잘 해결하는 사례다.
- 같은 글에서 남은 문제는 각각 유효한 두 개의 열린 변경안이 같은 요구사항을 건드리는 충돌을 archive 전에는 발견하지 못하는 것이라고 분리함. 따라서 guard가 쓸모 없다는 증거가 아니라 보호 효과와 잔여 구간을 함께 보여준다.
- 게시자 계정이 OpenSpec #1112 등 관련 토론에도 등장하므로 독립 고객 수로 더하지 않는다. 단일 보고이고 조사자가 다시 실행하지 않았다.

### 반례 2 — OpenSpec 산출물이 장기 컨텍스트를 보존한 사용 사례

- source_url: [Pavel Rapoport, The OpenSpec method in production](https://rapoport.studio/en/lab/the-openspec-method-in-production)
- published_or_updated: 2026-05-14 게시, 2026-08-28 갱신
- checked_at (KST): 2026-11-16
- 작성자는 약 6개월간 OpenSpec을 사용했고 변경 proposal/design/tasks를 보관한 덕에 3개월 뒤 참여한 implementer가 작성자 기억 없이 결정 이유를 읽었다고 설명.
- 이 사례는 변경 문서와 아카이브가 실제로 유용할 수 있다는 반례다. 동시에 명시적 범위 지정, 문서화·승인, 동시 변경의 자동 충돌 탐지 부족을 조건으로 언급.
- 정량 시간 절감이나 독립 평가가 없으므로 한 사용자의 긍정적 경험 보고로만 취급한다.

## 표본 구성과 한계

- 사건 7건을 정리했고 서로 다른 계정의 보고/댓글은 11개로 확인했다. 이 수는 독립 사용자 수나 조직 수가 아니며 관련 issue 참여자의 계정 중복·소속 중복을 완전히 확인하지 못했다.
- 같은 OpenSpec #725와 Codex #16911에서 여러 댓글이 나왔다. 댓글을 각각 새로운 고객으로 세지 않고 사건 thread와 계정 수를 함께 표시했다.
- 비용은 BMad 사례의 호출/쿼터 자기보고와 일부 시간 표현 이외에는 대부분 금액·인시가 unknown.
- 이 자료만으로 발생률, 구매 의사, 시장 크기, 현재 미해결 비율은 알 수 없다.
- 인터뷰 요청·외부 사용자 메시지·독립 실행 재현은 하지 않았다.
