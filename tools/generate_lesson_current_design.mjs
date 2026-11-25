#!/usr/bin/env node
// Read-only navigation over existing canonical sources; no approval or source mutation.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
function generate(read,has){
 const b="docs/artifacts/design/lesson-registration-20261124/",p="product/lesson-registration/",d="docs/design/lesson-registration/";
 const ap=b+"adoption-20261125.json",tp=b+"trace-index-v0.9.json",rp=b+"implementation-v0.4.json",cp=b+"common-integration-v1.json",bp=p+"contracts/IMPLEMENTATION-BINDING.json",ep=p+"evidence/common-contract-ci-20261125.json",wp=p+"WORKSPACE.json",sp="docs/artifacts/state/current.json",mp=d+"MANIFEST.json";
 const a=read(ap),t=read(tp),r=read(rp),c=read(cp),i=read(bp),e=read(ep),w=read(wp),s=read(sp),m=read(mp),am=read(b+"top-design-amendment-v1.json");
 const need=(ok,msg)=>{if(!ok)throw Error(msg)};
 const same=(x,y)=>x.length===y.length&&new Set(x).size===x.length&&new Set(y).size===y.length&&x.every(v=>y.includes(v));
 const uniq=xs=>[...new Set(xs)];
 const one=(arr,id)=>{let matches=arr.filter(x=>x.id===id);need(matches.length===1,"Missing or duplicate ID "+id);return matches[0]};
 const source=(path,pointer)=>{need(has(path),"Missing path "+path);if(pointer!==undefined){let v=read(path);for(const token of pointer.slice(1).split("/")){const key=token.replace(/~1/g,"/").replace(/~0/g,"~");need(v!==null&&typeof v==="object"&&Object.hasOwn(v,key),"Missing pointer "+path+pointer);v=v[key]}}return pointer===undefined?{path}:{path,pointer}};
 const refs=(...paths)=>paths.map(x=>source(x));
 need(a.canonical_commit===m.source_commit&&w.canonical_commit===m.source_commit,"Design pin mismatch");
 need(w.implementation_binding.path===bp&&w.implementation_binding.authority_ref===i.approval.ref&&w.implementation_binding.verification_ref===ep&&e.source_commit===i.approval.reviewed_commit&&e.url===i.approval.verification_run&&e.conclusion==="success","Binding evidence mismatch");
 need(i.status==="direction_approved_initial_shared_binding"&&same(i.approval.approved_decisions,i.decisions.map(x=>x.id)),"Approval coverage");
 need(s.active_phase_intent_id===w.phase&&has(s.active_phase_intent_ref),"Phase mismatch");
 need(same(s.active_task_ids,w.packages.map(x=>x.task_ref.split("/").pop().replace(".json",""))),"Assignment mismatch");
 const tests=c.gate.required,reqs=r.requirements.map(x=>x.id),cs=c.decisions.map(x=>x.id),old=t.inventory.map(x=>x.id),ib=i.decisions.map(x=>x.id);
 need(same(tests,c.gate.tests.map(x=>x.id))&&same(reqs,t.requirements.map(x=>x.id))&&same(cs,t.current_trace.map(x=>x.id)),"Design trace coverage");
 need(new Set([...old,...ib]).size===old.length+ib.length&&cs.every(x=>old.includes(x)),"Decision IDs");
 const tasks=w.packages.map(pkg=>{let id=pkg.task_ref.split("/").pop().replace(".json","");need(pkg.decisions.every(v=>cs.includes(v))&&pkg.test_refs.every(v=>tests.includes(v)),"Package trace "+id);return {id,owner:pkg.owner,package:pkg.id,branch:pkg.work_branch,task_ref:source(pkg.task_ref),intent_ref:source(pkg.intent_ref),plan_path:p+pkg.plan_path,logical_decisions:pkg.decisions,planned_product_tests:pkg.test_refs}});
 const map={
 "IB-01":{title:"공통 호출 규약",tasks:["048","049","050","052","053","054"],tests:["T5-03"],checks:["test_port_wiring_and_missing_unknown","test_provider_error_and_invalid_output"],limit:"실제 provider timeout/동시성/worker·IPC 미검증"},
 "IB-02":{title:"공통 스키마 검사",tasks:["048","049","050","051","052","053","054"],tests:["T5-03","T5-13","DV-04"],checks:["test_all_named_replay_shapes","test_http_named_shapes","test_platform_specific_values","test_datetime_and_digest_negative"],limit:"선정 합성 payload 검사. 프런트에 Python 엔진 강제 아님; 전체 제품 dependency lock 미확정"},
 "IB-03":{title:"Storage·Runtime·Adapter 권한 경계",tasks:["048","050","052","053","054"],tests:["AT-03","T5-12","DV-01","DV-02","DV-04"],checks:["test_input_guards_before_provider","test_mismatched_auth_generation_rejected"],limit:"입력 및 인증 관계 일부만 검증. 실제 원자성·permit·lease·권한 검증 아님"},
 "IB-04":{title:"프레임워크 독립 Viewer",tasks:["048","051","053"],tests:["AT-02","T5-02","DV-05"],checks:[],limit:"타입 선언만. transport·브라우저·grant 보안 미검증"},
 "IB-05":{title:"명시적 provider 조립",tasks:["048","049","050","051","052","053","054"],tests:["T5-03"],checks:["test_port_wiring_and_missing_unknown","test_separate_instances_and_no_implicit_provider"],limit:"합성 주입/독립성만. 실제 CO·모듈 연결 및 launch 미검증"}
 };
 need(same(Object.keys(map),ib),"IB navigation coverage");
 const decisions=i.decisions.map((x,n)=>{const v=map[x.id],ids=v.tasks.map(k=>"TASK-"+k);need(x.status==="direction_approved"&&x.prior.every(id=>old.includes(id))&&ids.every(id=>tasks.some(y=>y.id===id))&&v.tests.every(id=>tests.includes(id)),"IB trace "+x.id);return {id:x.id,title:v.title,status:x.status,source:source(bp,"/decisions/"+n),authority:source(i.approval.ref),prior_decision_ids:x.prior,inherited_requirements:uniq(x.prior.filter(id=>cs.includes(id)).flatMap(id=>one(c.decisions,id).requirement_refs)),selection:x.selection,alternatives:x.alternatives,reason:x.reason,revisit_when:x.revisit_when,pending_review:x.review,related_tasks:ids,planned_product_tests:v.tests,actual_evidence:{source:source(ep),tested_commit:e.source_commit,url:e.url,selected_checks:v.checks,kind:v.checks.length?"selected_synthetic_checks":"no_runtime_check",limit:v.limit}}});
 for(const x of tasks)x.related_implementation_decisions=decisions.filter(y=>y.related_tasks.includes(x.id)).map(y=>y.id);
 const logical=t.current_trace.map(x=>({id:x.id,original_status:one(t.inventory,x.id).original_status,snapshot_status:one(t.inventory,x.id).current_status,current_application:"adopted_logical_baseline",authority:source(ap),source:source(cp,"/decisions/"+c.decisions.findIndex(y=>y.id===x.id)),prior:x.prior,requirements:x.requirements,planned_tests:x.planned_checks,related_tasks:tasks.filter(y=>y.logical_decisions.includes(x.id)).map(y=>y.id),related_implementation_decisions:decisions.filter(y=>y.prior_decision_ids.includes(x.id)).map(y=>y.id)}));
 const requirements=r.requirements.map((x,n)=>{let v=one(t.requirements,x.id);return {id:x.id,title:x.id==="REQ-08"?"결과·부분 효과·실패 (재개 조항 대체)":x.title,source:source(rp,"/requirements/"+n),retained_note:v.note,logical_decisions:v.current_decisions,planned_tests:v.planned_checks,related_tasks_via_logical_decisions:tasks.filter(y=>y.logical_decisions.some(id=>v.current_decisions.includes(id))).map(y=>y.id),related_implementation_decisions:decisions.filter(y=>y.inherited_requirements.includes(x.id)).map(y=>y.id)}});
 for(const row of logical)need(row.prior.every(x=>old.includes(x))&&row.requirements.every(x=>reqs.includes(x))&&row.planned_tests.every(x=>tests.includes(x)),"Logical trace "+row.id);
 for(const row of requirements)need(row.logical_decisions.every(x=>cs.includes(x))&&row.planned_tests.every(x=>tests.includes(x)),"Requirement trace "+row.id);
 const layers=[
 ["상위 의도·목표","현재 적용",refs("docs/human/INTENT.md",s.active_phase_intent_ref,b+"direction-v0.4.json",b+"top-design-v1.json",b+"top-design-amendment-v1.json"),refs(d+"01-GOALS.md"),"현재 Phase 우선, A2 오류 전용 중단·mock-only"],
 ["제품 요구사항","명시 보존",[source(rp,"/requirements"),source(tp,"/requirements")],refs(d+"01-GOALS.md"),"REQ-08 재개 문구는 A2 및 CS-05/06으로 대체. 구 컴포넌트/물리 설계는 이력"],
 ["논리·상태·업무 경계","채택",refs(b+"detail-decisions-v2.json",b+"logical-behavior-v5.json",cp,ap),refs(d+"02-LOGIC.md",d+"06-API-PORTS.md",d+"07-EXECUTION.md"),"CS-01~09 원본 당시 상태 유지, 현행 채택은 승인 기록"],
 ["데이터·프로필","동결/채택·mock",refs(b+"logical-data-contract-decision-v1.json",b+"data-contract-v4.json",b+"data-schema-v4.1.json",b+"platform-profiles-v2.json"),refs(d+"03-DATA.md",d+"04-SCHEMA.md",d+"05-PLATFORMS.md"),"V4.1 명시 델타·공통 V1 우선. 실제 운영사 규칙 미검증"],
 ["공통 구현 계약","방향 승인·초기 공유",refs(bp,i.approval.ref,p+"contracts/interfaces.py",p+"contracts/validation.py",p+"contracts/viewer.d.ts",p+"src/lesson_registration/composition/wiring.py"),refs(p+"contracts/README.md"),"IB-01~05, 세부 provider/제품 스택 미확정"],
 ["공통 물리 설계·실행환경","부분 준비·후속 설계",refs(wp,p+"pyproject.toml",p+"uv.lock",p+"evidence/bootstrap-ci-20261125.json"),refs(p+"README.md",p+"evidence/PLAN.md"),"Python bootstrap 검증, 실제 DB/transport/launch/lock 미확정"],
 ["담당별 상세 설계·작업","TASK 배정",refs(sp,wp,...tasks.map(x=>x.task_ref.path)),refs("CURRENT.md",p+"WORK-PACKAGES.md"),"담당자 PLAN/수신/착수 및 일정 별도 확인"],
 ["검증·수용 시험","설계/합성 검증",[source(cp,"/gate"),source(b+"common-integration-validation-v1.json"),source(ep),source(tasks.find(x=>x.id==="TASK-048").task_ref.path)],refs(d+"09-TESTS.md","docs/review/README.md"),"제품 22개 시험 실제 결과는 TASK/고정 실행 근거로 판정"],
 ["과거 설계·WBS","이력/선별 참조",refs(mp,tp,b+"wbs-v0.5.json"),refs(d+"10-DECISIONS.md",d+"11-WBS.md",d+"12-HISTORY.md","docs/design/TARGET-DESIGN.md"),"고정 98개 원본·88개 추적 보존, 이전 찾아you 및 WBS는 현행 배정 아님"]
 ].map(([title,status,sources,views,note])=>({title,status,sources,views,note}));
 const index={id:"LR-CURRENT-DESIGN",kind:"generated_navigation_not_authority",phase:source(s.active_phase_intent_ref),operational_state:source(sp),adoption:source(ap),snapshot:{manifest:source(mp),commit:m.source_commit,original_files:m.coverage.inventory_files,original_decisions:t.inventory.length},implementation_approval:{source:source(bp),authority:source(i.approval.ref),approved_ids:ib,reviewed_commit:i.approval.reviewed_commit},precedence:[...t.precedence,"Adoption sets current application without rewriting snapshot statuses.","IB approved direction is subordinate to logical contract. Current phase/workspace/TASK outrank older WBS. No new assignment, acceptance criterion or approval."],trace_semantics:{related_tasks:"Navigation via common logical decisions or affected interface, not direct requirement assignment or new acceptance criterion.",inherited_requirements:"Context from prior CS decisions, not claim of satisfaction.",planned_tests:"Related future product test IDs, not executed proof.",actual_evidence:"Bounded synthetic checks only; IB-04 has no runtime check."},layers,requirements,logical_decisions:logical,implementation_decisions:decisions,active_packages:tasks,verification:{source:source(ep),url:e.url,tested_commit:e.source_commit,checks:e.checks,product_gate:{source:source(cp,"/gate"),required:tests.length,snapshot_execution:c.gate.execution,actual_result:source(tasks.find(x=>x.id==="TASK-048").task_ref.path)}},pending_physical:i.pending};
 const rel=path=>{let f=d.split("/").filter(Boolean),to=path.split("/"),k=0;while(k<f.length&&f[k]===to[k])k++;return "../".repeat(f.length-k)+to.slice(k).join("/")};
 const link=(x,label)=>"["+(label||x.path.split("/").pop())+"]("+rel(x.path)+")"+(x.pointer?" `"+x.pointer+"`":"");
 const tbl=(head,rows)=>[head,head.map(()=> "---"),...rows].map(row=>"| "+row.map(x=>String(x??"").replace(/\|/g,"\\|").replace(/\n/g," ")).join(" | ")+" |").join("\n")+"\n";
 const tasklinks=ids=>ids.map(id=>link(one(tasks,id).task_ref,id)).join(" · ")||"—";
 let md="# 레슨 등록 지원 서비스 · 현행 설계 기준\n\n> 기존 정본에서 생성한 현재 적용 인덱스. 별도 설계 정본·승인·업무 배정이 아니다.\n\n[AI용 현행 인덱스](CURRENT-DESIGN.json) · "+link(source("CURRENT.md"),"운영 상태")+" · [채택 전 고정 검토 스냅샷](README.md) · [전체 이력](12-HISTORY.md)\n\n";
 md+="## 1. 현행 적용 우선순위\n\n- "+link(source(s.active_phase_intent_ref),s.active_phase_intent_id)+" · "+link(source(ap),"논리 설계 채택")+" · "+link(source(i.approval.ref),"IB-01~05 승인")+"\n- 고정 논리 기준선 `"+m.source_commit+"`: 원본 "+m.coverage.inventory_files+"개, 기존 결정 "+t.inventory.length+"개 보존. IB 결정 5개는 그 후속 구현 방향이다.\n- "+am.decisions.find(x=>x[0]==="A2")[1]+". 이전 재개/취소/rollback 조항보다 우선.\n- 현재 mock-only. 실제 서비스 허용, 제품 성공, 팀원 수신·착수, 물리 스택/일정 확정을 추정하지 않는다.\n\n";
 md+="## 2. 설계 계층\n\n"+tbl(["계층","현행 상태","정본","읽기 뷰 / 주의"],layers.map(x=>[x.title,x.status,x.sources.map(s=>link(s)).join(" · "),x.views.map(s=>link(s)).join(" · ")+" — "+x.note]))+"\n";
 md+="## 3. 요구사항 추적\n\n원본 보존. TASK 연결은 공통 논리 결정을 통한 탐색 관계이며 직접 배정 또는 충족 여부가 아니다. 정확한 배정 요구사항은 각 TASK 원본을 확인한다.\n\n"+tbl(["요구사항","논리 결정","관련 TASK","계획 시험"],requirements.map(x=>[link(x.source,x.id)+" "+x.title,x.logical_decisions.join(", "),tasklinks(x.related_tasks_via_logical_decisions),x.planned_tests.join(", ")]))+"\n";
 md+="## 4. 결정 추적\n\n과거 CS 원본 상태는 보존하고 채택 기록으로 현행 적용을 판정한다. IB 영향 관계는 기존 계약 탐색용이며 신규 업무·수용 기준·검증 승격이 아니다.\n\n"+tbl(["논리 결정","현행 적용","선행 결정","관련 IB","관련 TASK"],logical.map(x=>[link(x.source,x.id),"채택",x.prior.join(", "),x.related_implementation_decisions.join(", ")||"—",tasklinks(x.related_tasks)]))+"\n";
 for(const x of decisions)md+="### "+x.id+" · "+x.title+"\n\n**선택:** "+x.selection+"\n\n**근거:** "+x.reason+"\n\n**대안:** "+x.alternatives.join(" / ")+"\n\n- "+link(x.source,"결정 원본")+" · "+link(x.authority,"승인 근거")+" · 선행: "+x.prior_decision_ids.join(", ")+"\n- 영향 검토: "+tasklinks(x.related_tasks)+" · 관련 계획 제품 시험: "+x.planned_product_tests.join(", ")+"\n- 확인된 근거: "+(x.actual_evidence.selected_checks.length?x.actual_evidence.selected_checks.map(y=>"`"+y+"`").join(", "):"런타임 시험 없음")+" · "+link(x.actual_evidence.source,"검증 기록")+"\n- 검증 한계: "+x.actual_evidence.limit+"\n- 남은 검토: "+x.pending_review+"\n- 재검토 조건: "+x.revisit_when+"\n\n";
 md+="## 5. 현재 담당별 작업\n\n"+tbl(["TASK","담당","패키지","관련 IB","PLAN 작성 위치"],tasks.map(x=>[link(x.task_ref,x.id),x.owner,x.package,x.related_implementation_decisions.join(", "),"`"+x.plan_path+"`"]))+"\n담당자별 PLAN은 작성 위치이며 존재·수신·착수·완료 여부를 주장하지 않는다. 이전 WBS는 [이력](11-WBS.md)으로만 사용한다.\n\n";
 md+="## 6. 검증 및 남은 설계\n\n- [공통 CI]("+e.url+") · 계약 "+e.checks.standard_contract_unittest.pass+"개, 합성 포트 "+e.checks.named_replay_payloads+"개, HTTP "+e.checks.http_replay_payloads+"개, 회귀 "+e.checks.bootstrap_and_wiring_unittest.pass+"개, 문서 "+e.checks.project_projections.count+"개. 고정 후보에 대한 검사다.\n- 제품 gate "+tests.length+"개: "+link(source(cp,"/gate"),"수용 기준")+" · "+link(tasks.find(x=>x.id==="TASK-048").task_ref,"실제 결과 원본")+". 합성/제품 시험 구분, T5-08 실제 모델 필수.\n\n"+i.pending.map(x=>"- "+x).join("\n")+"\n\n";
 md+="## 7. 갱신\n\n```sh\nnode tools/generate_lesson_current_design.mjs\nnode tools/generate_lesson_current_design.mjs --check\n```\n\n기존 정본을 먼저 변경하고 생성기를 실행한다. 현재 Phase·TASK·승인·설계 ID·요구사항·시험 참조 및 경로/JSON Pointer를 확인한다. 고정 스냅샷은 기존 생성기로 관리하며 과거 원본을 수정하지 않는다.\n";
 return {[d+"CURRENT-DESIGN.json"]:JSON.stringify(index,null,2)+"\n",[d+"CURRENT-DESIGN.md"]:md};
}
const read=path=>JSON.parse(readFileSync(resolve(root,path),'utf8'));
const has=path=>existsSync(resolve(root,path));
const files=generate(read,has);
const index=JSON.parse(files['docs/design/lesson-registration/CURRENT-DESIGN.json']);
const state=read(index.operational_state.path);
for(const pkg of index.active_packages){
 const task=read(pkg.task_ref.path);
 if(task.id!==pkg.id||task.owner!==pkg.owner||task.package_id!==pkg.package||task.work_branch!==pkg.branch||task.phase_intent_ref!==state.active_phase_intent_ref||task.intent_ref!==pkg.intent_ref.path)throw Error('Task/workspace mismatch '+pkg.id);
 const planned=task.traceability.planned_product_test_refs;
 if(planned.length!==pkg.planned_product_tests.length||new Set(planned).size!==planned.length||!planned.every(id=>pkg.planned_product_tests.includes(id)))throw Error('Task test mismatch '+pkg.id);
}
if(process.argv.includes('--check')){
 const stale=Object.entries(files).filter(([p,v])=>!has(p)||readFileSync(resolve(root,p),'utf8')!==v).map(([p])=>p);
 console.log(JSON.stringify({pass:!stale.length,stale,files:Object.keys(files)},null,2));
 if(stale.length)process.exitCode=1;
}else{
 for(const [p,v] of Object.entries(files))writeFileSync(resolve(root,p),v,'utf8');
 console.log('Current design navigation regenerated.');
}
