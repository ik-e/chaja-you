// Reference fixtures and static cross-document checks; no actual platform or runtime proof.
import {readFileSync} from "node:fs";
function review(s,a,w,p,l,e){
 const failures=[],checks=[],assert=(ok,label)=>{checks.push(label);if(!ok)failures.push(label)},ids=xs=>new Set(xs.map(x=>x.id));
 const T=ids(l.transitions),A=ids(l.axes),W=ids(w.works),E=ids(e.error_cases),P=ids(p.operation_specs),C=ids(p.operation_specs.flatMap(o=>o.checkpoints)),F=ids(p.effect_contracts);
 assert(P.size===44&&s.operation_rows.every(o=>p.operation_specs.some(x=>x.id===o.id&&x.scope===o.scope)),"44 approved scope rows");
 assert(a.transitions.length===44&&a.transitions.every(t=>[w.transition_trace,l.screen_trace].every(xs=>xs.some(x=>x.id===t.id&&x.from===t.from&&x.to===t.to&&x.condition===t.condition))),"44 screen route traces");
 assert(["H","E","W","R","G","A","X","D"].every(from=>a.transitions.some(t=>t.from===from&&t.to==="V0")),"global authentication expiry routes");
 assert(T.size===73&&A.size===17&&l.transitions.every(t=>{const x=l.axes.find(a=>a.id===t.axis);return x&&t.from.every(v=>x.values.includes(v)&&!x.terminal.includes(v))&&x.values.includes(t.to)&&t.work_refs.every(id=>W.has(id))&&t.error_refs.every(id=>E.has(id))}),"73 transitions and state domains");
 for(const ax of l.axes){let r=new Set([ax.initial]),repeat=true;while(repeat){repeat=false;for(const t of l.transitions.filter(t=>t.axis===ax.id))if(t.from.some(v=>r.has(v))&&!r.has(t.to)){r.add(t.to);repeat=true}}assert(ax.values.every(v=>r.has(v)),"axis reachability "+ax.id)}
 assert(l.transitions.every(t=>t.error_refs.every(id=>l.error_trace.find(x=>x.id===id).transition_refs.includes(t.id)))&&l.error_trace.every(x=>x.transition_refs.every(id=>l.transitions.find(t=>t.id===id).error_refs.includes(x.id))),"bidirectional state/error references");
 assert(l.transitions.every(t=>t.work_refs.every(id=>l.work_trace.find(x=>x.id===id).transition_refs.includes(t.id))),"state/work references");
 assert([...l.atomic_boundaries,...l.screen_trace,...l.work_trace,...l.error_trace,...l.operation_trace.flatMap(x=>x.checkpoints)].every(x=>x.transition_refs.every(id=>T.has(id))),"transition refs");
 assert(F.size===45&&p.effect_contracts.every(f=>P.has(f.operation_ref)&&C.has(f.checkpoint_ref)&&f.read_scope.requires_frozen_plan&&f.actual_execution==="blocked_mock_only"&&f.recovery.disposition==="hold_until_independent_path_verified"),"45 effect contracts and recovery gates");
 const mut=p.operation_specs.flatMap(o=>o.checkpoints).filter(c=>c.mode==="effect_candidate");
 assert(mut.length===23&&mut.every(c=>p.effect_contracts.some(f=>f.checkpoint_ref===c.id)),"23 mutation checkpoints covered");
 assert(p.effect_contracts.every(f=>["included_priority","included_later"].includes(p.operation_specs.find(x=>x.id===f.operation_ref).scope)),"held/local/conditional no effect");
 assert(e.error_cases.every(x=>x.transition_refs.every(id=>T.has(id)))&&e.action_trace.length===155&&e.branch_trace.length===693&&e.checkpoint_trace.length===144,"error/legacy references preserved");
 assert(e.acceptance_cases.length===22&&e.acceptance_cases.every(x=>x.error_refs.every(id=>E.has(id))),"22 acceptance references");
 const overlap=(a,b)=>a.account===b.account&&a.platform===b.platform&&(a.path==="*"||b.path==="*"||a.path===b.path||a.path.startsWith(b.path+"/")||b.path.startsWith(a.path+"/"));
 const claim={account:"A",platform:"P",path:"profile/7"},child={account:"A",platform:"P",path:"profile/7/service/1"},other={account:"A",platform:"P",path:"profile/8"},diff={account:"B",platform:"P",path:"profile/7"};
 assert(overlap(claim,child)&&!overlap(claim,other)&&!overlap(claim,diff),"reference collision prefix/independent resource");
 const canSend=({approved,writeAllowed,readAllowed,readPlan,active,unknown,disputed,target})=>approved&&writeAllowed&&readAllowed&&readPlan&&![...active,...unknown,...disputed].some(x=>overlap(x,target));
 const b={approved:true,writeAllowed:true,readAllowed:true,readPlan:true,active:[],unknown:[],disputed:[],target:child};
 assert(canSend(b)&&!canSend({...b,readAllowed:false})&&!canSend({...b,readPlan:false})&&!canSend({...b,active:[claim]})&&!canSend({...b,unknown:[claim]})&&!canSend({...b,disputed:[claim]})&&canSend({...b,active:[other]}),"reference approval/read/claim/unknown/dispute gates");
 const verdict=fx=>fx.some(x=>x.effect==="unknown"||x.dispatch==="unknown")?"effect_unknown":fx.every(x=>x.effect==="confirmed")?"complete":fx.some(x=>x.effect==="confirmed")?"partial_confirmed":fx.every(x=>x.dispatch==="none")?"not_executed":fx.some(x=>x.dispatch==="sent")?"no_effect":"effect_unknown";
 const none={effect:"none",dispatch:"none"},sent={effect:"none",dispatch:"sent"},unk={effect:"unknown",dispatch:"unknown"},ok={effect:"confirmed",dispatch:"sent"};
 assert(verdict([none,none])==="not_executed"&&verdict([sent,none])==="no_effect"&&verdict([ok,unk])==="effect_unknown"&&verdict([ok,none])==="partial_confirmed"&&verdict([ok,ok])==="complete","reference result discrimination");
 assert(verdict([unk,none])==="effect_unknown"&&verdict([none,none])==="not_executed"&&l.transitions.some(t=>t.id==="LT-70"&&t.from.includes("effect_unknown")&&t.to==="not_executed"),"reference late non-dispatch path");
 const canRecover=x=>x.pathVerified&&x.exact&&x.fenced&&x.support&&x.newApproval&&x.effect!=="confirmed"&&x.effect!=="unknown"&&!x.conflict;
 const r={pathVerified:true,exact:true,fenced:true,support:true,newApproval:true,effect:"none",conflict:false};
 assert(canRecover(r)&&!canRecover({...r,pathVerified:false})&&!canRecover({...r,effect:"unknown"})&&!canRecover({...r,conflict:true}),"reference residual gate");
 return {checks:checks.length,failures,checks_detail:checks,effect_candidates:F.size,mutation_checkpoints:mut.length,screen_transitions:a.transitions.length,state_axes:A.size,state_transitions:T.size,scope_rows:P.size,actual_platform_tests:0,semantic_complete:false,official_python_ci:"not_run"};
}
const base=new URL("../docs/artifacts/planning/lesson-registration-20261126/integrated/",import.meta.url);
const names=["service-scope-v1.0.json","abstract-screen-v1.0.json","system-work-v1.0.json","platform-work-v1.0.json","logical-state-v1.0.json","error-response-v1.0.json"];
const result=review(...names.map(n=>JSON.parse(readFileSync(new URL(n,base),"utf8"))));
console.log(JSON.stringify(result,null,2));
if(result.failures.length)process.exitCode=1;
