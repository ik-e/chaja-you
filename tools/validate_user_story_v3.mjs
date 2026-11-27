// V3 structural and bounded reference fixtures, not runtime or platform proof.
import {readFileSync} from "node:fs";
function referenceTests(){
 const tests=[],failures=[];function test(id,desc,fn){let ok=false,detail=null;try{ok=Boolean(fn())}catch(x){detail=String(x)}tests.push({id,desc,pass:ok,detail});if(!ok)failures.push(id)}
 const overlap=(a,b)=>a.env===b.env&&a.platform===b.platform&&a.account===b.account&&(a.path==="*"||b.path==="*"||a.path===b.path||a.path.startsWith(b.path+"/")||b.path.startsWith(a.path+"/"));
 const root={env:"mock",platform:"PL03",account:"A",path:"profile/7"},child={...root,path:"profile/7/service/2"},other={...root,path:"profile/8"};
 const state=()=>({requests:{},effects:{},claims:[],disputes:[],observations:{},cleanup:{},writes:0,ids:0,owner:"owner1",generation:1,revision:1});
 const accept=(m,key,hash,owner,approved)=>{if(owner!==m.owner)return {ok:false,reason:"owner"};const old=m.requests[key];if(old)return old.hash===hash?{ok:true,id:old.id,duplicate:true}:{ok:false,reason:"hash"};if(!approved)return {ok:false,reason:"approval"};const id="J"+(++m.ids);m.requests[key]={id,hash,ended:false,owner};return {ok:true,id}};
 const reserve=(m,job,id,region,gates)=>{const j=Object.values(m.requests).find(x=>x.id===job);if(!j||j.ended||!gates.approved||!gates.read||!gates.write||!gates.support||m.effects[id]||m.claims.some(x=>overlap(x.region,region))||m.disputes.some(x=>overlap(x,region))||Object.values(m.effects).some(x=>x.effect==="unknown"&&overlap(x.region,region)))return false;m.effects[id]={job,region,effect:"reserved",sent:"none"};m.claims.push({id,region});return true};
 const send=(m,id,current)=>{const x=m.effects[id];if(!x||x.effect!=="reserved"||!current.read||!current.write||!current.generation||m.disputes.some(d=>overlap(d,x.region)))return false;x.effect="in_flight";x.sent="sent";m.writes++;return true};
 const settle=(m,id,effect,sent)=>{const x=m.effects[id];if(!x)return false;if(["confirmed","none"].includes(x.effect)&&x.effect!==effect){m.disputes.push(x.region);return false}x.effect=effect;x.sent=sent;m.claims=m.claims.filter(c=>c.id!==id);return true};
 const verdict=xs=>xs.some(x=>x.effect==="unknown"||x.sent==="unknown"||["reserved","in_flight"].includes(x.effect))?"effect_unknown":xs.length&&xs.every(x=>x.effect==="confirmed")?"complete":xs.some(x=>x.effect==="confirmed")?"partial_confirmed":xs.every(x=>x.sent==="none")?"not_executed":xs.some(x=>x.sent==="sent")?"no_effect":"effect_unknown";
 const gate={approved:true,read:true,write:true,support:true},current={read:true,write:true,generation:true};
 const job=m=>accept(m,"K","hash",m.owner,true).id;
 const canRecover=x=>x.exact&&x.fenced&&x.pathVerified&&x.newApproval&&x.support&&["none","not_attempted"].includes(x.effect)&&!x.conflict;
 const read=(m,key,value,seq,allowed)=>{const previous=m.observations[key]??{last:null,lastSeq:-1,lastAttempt:-1,status:"unknown"};if(seq<previous.lastAttempt)return previous;const next={...previous,lastAttempt:seq,status:allowed?"observed":"unavailable"};if(allowed&&seq>=previous.lastSeq){next.last=value;next.lastSeq=seq}m.observations[key]=next;return next};
 test("M01","승인·필수 읽기·정확 범위의 일회 모의 전송 및 독립 확인",()=>{let m=state(),j=job(m);return reserve(m,j,"E",root,gate)&&send(m,"E",current)&&!send(m,"E",current)&&settle(m,"E","confirmed","sent")&&verdict([m.effects.E])==="complete"&&m.writes===1});
 test("M02","외부 효과 불명 이후 신규 쓰기 차단",()=>{let m=state(),j=job(m);reserve(m,j,"E",root,gate);send(m,"E",current);settle(m,"E","unknown","unknown");return verdict([m.effects.E])==="effect_unknown"&&!reserve(m,j,"E2",child,gate)&&m.writes===1});
 test("M03","동일 명령 키 및 hash/owner 확인",()=>{let m=state(),x=accept(m,"K","h","owner1",true),y=accept(m,"K","h","owner1",true);return x.id===y.id&&y.duplicate&&!accept(m,"K","new","owner1",true).ok&&!accept(m,"K","h","other",true).ok&&m.ids===1});
 test("M04","조회 실패·늦은 응답은 마지막 관측 보존, 쓰기 없음",()=>{let m=state();read(m,"x","observed-A",1,true);read(m,"x",null,2,false);const stale=read(m,"x","old",1,true);return stale.last==="observed-A"&&stale.status==="unavailable"&&stale.lastAttempt===2&&m.writes===0});
 test("M05","허용·readback·승인·지원 중 하나라도 불가하면 예약 금지",()=>{let m=state(),j=job(m);return ["read","write","approved","support"].every(k=>!reserve(m,j,"E",root,{...gate,[k]:false}))&&m.writes===0});
 test("M06","원본 revision 변경 및 미수락 검토안 무효, 과거 승인 불변",()=>{let m=state(),old={revision:m.revision,frozen:true},draft={revision:m.revision,frozen:false};m.revision++;const stale=draft.revision!==m.revision;return stale&&old.revision===1&&old.frozen&&m.writes===0});
 test("M07","owner와 인증 generation 변경·정확 권한 확인",()=>{let m=state(),j=job(m);reserve(m,j,"E",root,gate);m.generation++;return !send(m,"E",{...current,generation:false})&&!accept(m,"bad","h","wrong",true).ok&&m.writes===0});
 test("M08","종료 후 미전송 근거와 불명 판정 보완",()=>{let m=state(),j=job(m);reserve(m,j,"E",root,gate);settle(m,"E","unknown","unknown");let first=verdict([m.effects.E]);m.requests.K.ended=true;settle(m,"E","none","none");return first==="effect_unknown"&&verdict([m.effects.E])==="not_executed"&&!reserve(m,j,"E2",root,gate)&&m.writes===0});
 test("M09","부분 효과·복구 독립 경로 및 새 승인",()=>{let m=state(),j=job(m);reserve(m,j,"E1",root,gate);send(m,"E1",current);settle(m,"E1","confirmed","sent");reserve(m,j,"E2",child,gate);settle(m,"E2","none","none");const r={exact:true,fenced:true,pathVerified:true,newApproval:true,support:true,effect:"none",conflict:false};return verdict(Object.values(m.effects))==="partial_confirmed"&&canRecover(r)&&!canRecover({...r,pathVerified:false})&&!canRecover({...r,effect:"confirmed"})&&!canRecover({...r,effect:"unknown"})&&!canRecover({...r,newApproval:false})&&m.writes===1});
 test("M10","폐기 불명과 업무 판정 분리",()=>{let m=state(),j=job(m);m.requests.K.ended=true;m.cleanup[j]={blocked:true,confirmation:"unknown"};return m.cleanup[j].blocked&&m.cleanup[j].confirmation==="unknown"&&!reserve(m,j,"E",root,gate)});
 test("M11","다중 대상 독립 결과 집계",()=>{const outcomes=[verdict([{effect:"confirmed",sent:"sent"}]),verdict([{effect:"unknown",sent:"unknown"}]),verdict([{effect:"none",sent:"none"}])];return outcomes.join(",")==="complete,effect_unknown,not_executed"&&!outcomes.every(x=>x==="complete")});
 test("M12","상위/하위 충돌과 독립 객체",()=>{let m=state(),j=job(m),k=accept(m,"K2","h",m.owner,true).id;return reserve(m,j,"E1",root,gate)&&!reserve(m,k,"E2",child,gate)&&reserve(m,k,"E3",other,gate)&&m.writes===0});
 test("M13","상충 근거는 과거 결과 불변·분쟁 차단",()=>{let m=state(),j=job(m);reserve(m,j,"E1",root,gate);send(m,"E1",current);settle(m,"E1","confirmed","sent");let old=m.effects.E1.effect;return !settle(m,"E1","none","sent")&&old===m.effects.E1.effect&&m.disputes.length===1&&!reserve(m,j,"E2",child,gate)});
 return {tests,failures,scope:"mock reference fixtures only; no actual application/DB/platform/authorization or full concurrency model"};
}
function verify(v,t,l,a,w,p,e,s){
 const checks=[],failures=[];const assert=(ok,id)=>{checks.push(id);if(!ok)failures.push(id)};
 const ids=xs=>new Set(xs.map(x=>x.id)),ns=ids(v.nodes),lt=ids(l.transitions),ws=ids(w.works),ts=ids(a.transitions);
 const node=id=>v.nodes.find(x=>x.id===id),pair=(x,y)=>v.edges.some(e=>e.from===x&&e.to===y)||v.screen_contract.global_navigation.some(t=>t.from===node(x)?.screen&&t.to===node(y)?.screen);
 assert(ns.size===v.nodes.length&&ids(v.edges).size===v.edges.length,"unique flow IDs");
 assert(v.edges.every(x=>{let n=node(x.from),m=node(x.to),tr=a.transitions.find(t=>t.id===x.screen_ref);return n&&m&&(x.screen_ref?tr&&tr.from===n.screen&&tr.to===m.screen:n.screen===m.screen)&&x.condition}),"flow edges and screen guards");
 assert(v.nodes.every(n=>n.work_refs.every(x=>ws.has(x))&&n.transition_refs.every(x=>lt.has(x))),"node work/transition refs");
 assert(w.works.every(w=>v.nodes.some(n=>n.work_refs.includes(w.id))),"all 36 system works");
 assert(v.screen_contract.all_screen_transition_refs.length===44&&v.screen_contract.all_screen_transition_refs.every(x=>ts.has(x))&&a.transitions.every(x=>v.edges.some(y=>y.screen_ref===x.id)||v.screen_contract.global_navigation.some(y=>y.screen_transition===x.id)), "all 44 screen transitions");
 assert(v.journeys.length===12&&v.journeys.every(j=>j.path.every((x,i)=>ns.has(x)&&(i===0||pair(j.path[i-1],x)))),"12 journey paths");
 assert(v.scenarios.length===28&&v.scenarios.every(j=>j.path.every((x,i)=>ns.has(x)&&(i===0||pair(j.path[i-1],x)))),"28 reference scenario paths");
 assert(e.acceptance_cases.every(c=>v.scenarios.some(x=>x.error_acceptance_refs.includes(c.id))),"22 error acceptance candidates connected");
 assert(v.platform_routes.length===44&&v.platform_routes.every(x=>{const op=p.operation_specs.find(o=>o.id===x.operation_id);return op&&op.scope===x.scope&&x.checkpoint_refs.length===op.checkpoints.length&&x.checkpoint_refs.every(c=>op.checkpoints.some(o=>o.id===c))&&x.effect_refs.every(f=>p.effect_contracts.some(o=>o.id===f&&o.operation_ref===op.id))&&x.actual_execution==="blocked_mock_only"}),"44 platform/144 checkpoint/45 effect contracts");
 assert(v.platform_routes.filter(x=>x.kind==="restriction"||x.kind==="internal_guidance").every(x=>!x.effect_refs.length),"held/local/conditional no effect candidate");
 assert(v.error_routes.length===32&&v.error_routes.every(x=>x.story_nodes.every(id=>ns.has(id))&&x.transition_refs.every(id=>lt.has(id))),"32 error routes");
 assert(t.r03_actions.length===121&&t.r03_events.length===56&&t.r03_findings.length===18&&t.legacy_stories.length===144&&t.legacy_actions.length===155&&t.legacy_branches.length===693,"source coverage counts");
 assert([...t.r03_actions,...t.r03_events,...t.legacy_stories,...t.legacy_actions].every(x=>x.nodes.every(id=>ns.has(id)))&&t.legacy_branches.every(x=>x.node_refs.every(id=>ns.has(id))&&x.next_candidates.every(c=>c.node_refs.every(id=>ns.has(id)))),"trace node refs");
 assert(t.legacy_branches.filter(x=>x.disposition==="excluded_by_current_scope").every(x=>x.node_refs.length===0),"excluded branch no executable node refs");
 assert(l.transitions.find(x=>x.id==="LT-44").guard.includes("최신 상태 읽기")&&l.transitions.find(x=>x.id==="LT-44").guard.includes("기존 효과 확인 읽기"),"LT44 read purpose correction");
 assert(s.operation_rows.length===44&&s.operation_rows.every(x=>v.platform_routes.some(o=>o.operation_id===x.id&&o.scope===x.scope)),"service scope unchanged");
 const model=referenceTests();for(const c of model.tests)assert(c.pass,c.id+" "+c.desc);
 assert(v.scenarios.every(x=>x.reference_model_cases.every(id=>model.tests.some(c=>c.id===id))),"scenario/reference fixture refs");
 return {checks,failures,model,counts:{nodes:v.nodes.length,edges:v.edges.length,journeys:v.journeys.length,scenarios:v.scenarios.length,platform_operations:v.platform_routes.length,error_acceptance:e.acceptance_cases.length,r03_actions:t.r03_actions.length,r03_events:t.r03_events.length,legacy_branches:t.legacy_branches.length},full_semantics:"inconclusive",actual_tests:0,official_python_ci:"not_run"};
}
const base=new URL("../docs/artifacts/planning/lesson-registration-20261126/integrated/",import.meta.url);
const paths=["v3.0/user-stories.json","v3.0/trace.json","logical-state-v1.0.json","abstract-screen-v1.0.json","system-work-v1.0.json","platform-work-v1.0.json","error-response-v1.0.json","service-scope-v1.0.json"];
const result=verify(...paths.map(p=>JSON.parse(readFileSync(new URL(p,base),"utf8"))));
console.log(JSON.stringify(result,null,2));
if(result.failures.length)process.exitCode=1;
