import {readFileSync} from 'node:fs';
function verify(c,a,r,...b){
 const checks=[],cases=[];const check=(name,pass)=>checks.push({name,pass:!!pass});const set=x=>new Set(x);const refs=(x,s)=>x.every(y=>s.has(y));
 const base=set([...b.slice(0,4).flatMap(j=>j.records.map(x=>x.id)),...b[0].contract.transitions.map(x=>x.id),...b[0].contract.invariants.map(x=>x.id),...b[4].sections.flatMap(s=>s.tables.flatMap(t=>t.rows.map(x=>x[0])))]);
 const rule=set(c.rules.map(x=>x.id)),issue=set(r.issues.map(x=>x.id)),src=set(b[4].sources.map(x=>x.id)),schemas=set(a.schemas.map(x=>x.id));
 const ids=[...c.rules,...c.guards,...c.transitions,...c.evidence_profiles,...a.apis,...r.issues,...r.decisions,...r.tests].map(x=>x.id);
 check("unique IDs",set(ids).size===ids.length);
 check("baseline/source references",c.rules.every(x=>refs(x.baseline_refs,base)&&refs(x.source_refs,src))&&refs(c.replaces_transitions,base));
 check("issue and rule references",c.rules.every(x=>refs(x.issue_refs,issue))&&r.issues.every(x=>refs(x.rule_refs,rule))&&refs(a.rule_refs,rule));
 check("all issues covered by test plans",r.tests.every(x=>refs(x.issue_refs,issue))&&r.issues.every(x=>r.tests.some(t=>t.issue_refs.includes(x.id))));
 const types=set(["id","string","positive_int","nonnegative_int","json","digest","timestamp","boolean","EffectClass","EffectState","JobState",...Object.keys(a.types),...schemas]);
 check("typed fields",a.schemas.every(s=>set(s.fields.map(f=>f.name)).size===s.fields.length&&s.fields.every(f=>types.has(f.type.replace(/\[\]$/,""))&&typeof f.required==="boolean")));
 check("API references",a.apis.every(x=>schemas.has(x.request)&&schemas.has(x.response)));
 const states=set(c.job_states),keys=c.transitions.flatMap(t=>t.from.map(s=>s+"|"+t.event));
 check("deterministic state transitions",set(keys).size===keys.length&&c.transitions.every(t=>refs(t.from,states)&&states.has(t.to)));
 let reach=set([c.initial]);for(let i=0;i<states.size;i++)for(const t of c.transitions)if(t.from.some(s=>reach.has(s)))reach.add(t.to);
 check("active states reachable",c.job_states.filter(s=>!c.reserved.includes(s)).every(s=>reach.has(s)));
 check("live state unreachable",c.reserved.every(s=>!reach.has(s)));
 check("terminal states have no transitions",c.terminal.every(s=>c.transitions.every(t=>!t.from.includes(s))));
 const guards=c.guards.map(g=>g.condition),truth=Object.fromEntries(guards.map(x=>[x,true]));
 check("dispatch guards complete",refs(c.dispatch.required_guard_refs,set(c.guards.map(g=>g.id)))&&c.dispatch.required_guard_refs.length===c.guards.length&&c.transitions.filter(t=>t.event==="dispatch_admitted").every(t=>t.from.join()==="ready"&&guards.every(g=>t.conditions.includes(g))));
 check("effect transitions",c.effect_transitions.every(t=>c.effect_states.includes(t.from)&&c.effect_states.includes(t.to)&&!["effect_absent","effect_confirmed"].includes(t.from)));
 const visiting=set([]),done=set([]);let dag=true;function dfs(id){if(visiting.has(id)){dag=false;return;}if(done.has(id))return;const x=r.decisions.find(d=>d.id===id);if(!x){dag=false;return;}visiting.add(id);x.depends_on.forEach(dfs);visiting.delete(id);done.add(id);}r.decisions.forEach(x=>dfs(x.id));check("decision DAG",dag&&done.size===r.decisions.length);
 const record=(name,actual,expected)=>cases.push({name,actual,expected,pass:actual===expected});
 const step=(s,event,f)=>{const t=c.transitions.find(t=>t.from.includes(s)&&t.event===event);return t&&t.conditions.every(k=>f[k]===true)?t.to:null;};
 record("normal admission",step("ready","dispatch_admitted",truth),"running");
 guards.forEach(g=>record("guard false: "+g,step("ready","dispatch_admitted",{...truth,[g]:false}),null));
 record("missing account",step("ready","dispatch_admitted",Object.fromEntries(Object.entries(truth).filter(([k])=>k!=="account_verified_same"))),null);
 const ss=[
 ["ready revoked","ready","permission_blocked",{no_pending_effect:true},"blocked"],
 ["ready auth expired","ready","confirmation_needed",{no_pending_effect:true},"needs_action"],
 ["running stop","running","stop_requested",{},"stopping"],
 ["stop effect absent","stopping","stop_resolved_cancel",{no_pending_effect:true,goal_not_reached:true,stop_is_cancel:true},"cancelled"],
 ["stop uncertain","stopping","effect_uncertain",{pending_or_unresolved_effect:true},"unknown"],
 ["unknown cancel","unknown","cancel_or_revoke_requested",{},"unknown"],
 ["unknown dispatch","unknown","dispatch_admitted",truth,null],
 ["stopping dispatch","stopping","dispatch_admitted",truth,null],
 ["stop but goal verified","stopping","mock_goal_verified",{mock_environment:true,goal_evidence_valid:true,no_pending_effect:true},"mock_completed"],
 ["uncertain proof","unknown","mock_goal_verified",{mock_environment:true,goal_evidence_valid:false,no_pending_effect:false},null],
 ["safe recovery","unknown","safe_recovery_identified",{safe_next_step_proven:true,no_pending_effect:true,not_cancelled_or_policy_revoked:true},"needs_action"],
 ["cancelled recovery denied","unknown","safe_recovery_identified",{safe_next_step_proven:true,no_pending_effect:true,not_cancelled_or_policy_revoked:false},null],
 ["stop policy","stopping","stop_resolved_policy",{no_pending_effect:true,goal_not_reached:true,stop_is_policy:true},"blocked"],
 ["stop human","stopping","stop_resolved_human",{no_pending_effect:true,goal_not_reached:true,stop_needs_human:true},"needs_action"],
 ["live goal","running","live_goal_verified",{goal_evidence_valid:true},null],
 ["completed overwrite","mock_completed","definite_failure",{effect_absent:true,no_pending_effect:true},null],
 ["unknown cancel resolved","unknown","reconcile_cancel_resolved",{no_pending_effect:true,goal_not_reached:true,stop_is_cancel:true},"cancelled"],
 ["unknown policy resolved","unknown","reconcile_policy_resolved",{no_pending_effect:true,goal_not_reached:true,stop_is_policy:true},"blocked"]];
 ss.forEach(([name,s,e,f,x])=>record(name,step(s,e,f),x));
 for(const p of c.evidence_profiles){const yes=Object.fromEntries(p.required.map(k=>[k,true]));const ev=(env,kind,f)=>env===p.environment&&kind===p.kind&&p.required.every(k=>f[k]===true);record(p.id+" valid",ev("mock",p.kind,yes),true);record(p.id+" wrong environment",ev("live",p.kind,yes),false);record(p.id+" click only",ev("mock","click",yes),false);for(const k of p.required)record(p.id+" missing "+k,ev("mock",p.kind,{...yes,[k]:false}),false);}
 return {kind:"design_abstract_validation",checks,cases,static_pass:checks.filter(x=>x.pass).length,static_total:checks.length,abstract_pass:cases.filter(x=>x.pass).length,abstract_total:cases.length,product_execution:"not_run",limitations:"Boolean guard, declared transitions and evidence predicates only; no actual concurrency, browser, database, platform, API or user value execution. Prior design semantics not exhaustively proven."};
}
const files=["core-contract-v0.3.json","data-api-v0.3.json","review-v0.3.json","domain-workflow-v0.1.json","requirements-v0.1.json","system-contracts-v0.1.json","verification-decisions-v0.1.json","detail-design-v0.2.json"];
const result=verify(...files.map(p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'))));
console.log(JSON.stringify(result,null,2));
if(result.static_pass!==result.static_total||result.abstract_pass!==result.abstract_total)process.exitCode=1;
