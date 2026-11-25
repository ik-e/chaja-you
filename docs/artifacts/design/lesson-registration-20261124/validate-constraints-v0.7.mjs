// V0.7: independent checks over original JSON, not product execution.
// No dependencies, network calls or product-specific fixture copies.
export function validateDesignConstraints(D){
 const {core:c,contract:o,api:a,physical:p,implementation:d,index:i,wbs:w,review:r}=D;
 const checks=[],review=[],unverified=[];
 const unique=x=>new Set(x).size===x.length;
 const group=(id,fn)=>{const findings=[];const need=(condition,detail)=>{if(!condition)findings.push(detail);};try{fn(need);}catch(e){findings.push("Invalid input: "+String(e));}checks.push({id,pass:findings.length===0,findings});};
 const reach=(start,links)=>{const seen=new Set(start),q=[...start];for(let n=0;n<q.length;n++)for(const [x,y] of links)if(x===q[n]&&!seen.has(y)){seen.add(y);q.push(y);}return seen;};
 const job=c.transitions.flatMap(t=>t.from.map(s=>({from:s,to:t.to,event:t.event,conditions:t.conditions,id:t.id})));
 const states=new Set(c.job_states),reserved=new Set(c.reserved),terminal=new Set(c.terminal),edges=job.map(t=>[t.from,t.to]);
 const allGuards=new Set(c.guards.map(g=>g.condition));
 const expectedRefs=new Set(c.guards.map(g=>g.id));
 const required=new Set(c.dispatch.required_guard_refs.map(id=>c.guards.find(g=>g.id===id)?.condition).filter(Boolean));
 group("STATE-01 declared states and transitions",need=>{
   need(unique(c.job_states)&&unique(c.terminal)&&unique(c.reserved),"Duplicate state/terminal/reserved");
   need(states.has(c.initial)&&!terminal.has(c.initial)&&!reserved.has(c.initial),"Invalid initial state");
   need([...terminal,...reserved].every(s=>states.has(s))&&[...terminal].every(s=>!reserved.has(s)),"Invalid terminal/reserved state");
   need(unique(c.transitions.map(t=>t.id)),"Duplicate transition ID");
   for(const t of c.transitions)need(t.from.length>0&&unique(t.from)&&states.has(t.to)&&t.from.every(s=>states.has(s))&&typeof t.event==="string"&&t.event.length>0&&Array.isArray(t.conditions)&&unique(t.conditions)&&t.conditions.every(g=>typeof g==="string"&&g.length>0),{transition:t.id,problem:"Invalid endpoints/event/condition declaration"});
   need(unique(job.map(t=>t.from+"|"+t.event)),"Same state/event has multiple transition definitions; disjointness not specified");
 });
 group("STATE-02 structural reachability and terminal isolation",need=>{
   const reachable=reach([c.initial],edges),canEnd=reach([...terminal],edges.map(([x,y])=>[y,x]));
   need([...states].filter(s=>!reserved.has(s)).every(s=>reachable.has(s)),{unreachable:[...states].filter(s=>!reserved.has(s)&&!reachable.has(s))});
   need([...reserved].every(s=>!reachable.has(s))&&job.every(t=>!reserved.has(t.from)&&!reserved.has(t.to)),{reserved_reachable:[...reserved].filter(s=>reachable.has(s))});
   need(job.every(t=>!terminal.has(t.from)),{terminal_outgoing:job.filter(t=>terminal.has(t.from)).map(t=>t.id)});
   need([...reachable].every(s=>canEnd.has(s)),{no_structural_terminal_path:[...reachable].filter(s=>!canEnd.has(s))});
 });
 group("STATE-03 all-guard dispatch admission",need=>{
   // R5-03/R5-07: all V3 guards mandatory, so the declared guard inventory is the reference.
   need(unique(c.guards.map(g=>g.id))&&unique(c.guards.map(g=>g.condition))&&c.guards.length>0,"Duplicate/empty guard inventory");
   need(unique(c.dispatch.required_guard_refs)&&c.dispatch.required_guard_refs.length===expectedRefs.size&&c.dispatch.required_guard_refs.every(id=>expectedRefs.has(id)),"Dispatch guard references do not equal full V3 guard inventory");
   // Minimum safety obligations are independently extracted from V3-R01..07/R5-03/R5-07; extra declared guards are also mandatory.
   const policyGuards=["mock_environment","owner_verified","account_verified_same","approval_current","permission_current","target_resolved","no_unresolved_effect","operation_allowed","before_state_verified","lease_current_exclusive","revision_current","operation_not_already_effective","not_stopping"];
   need(c.dispatch.only_state==="ready"&&policyGuards.every(g=>required.has(g)),{problem:"Required safety guard or ready-only entry missing",missing_policy_guards:policyGuards.filter(g=>!required.has(g))});
   const entries=job.filter(t=>t.to==="running");
   need(entries.length>0,"No running transition");
   for(const t of entries){
     const missing=[...allGuards].filter(g=>!t.conditions.includes(g));
     need(t.from===c.dispatch.only_state&&t.event==="dispatch_admitted",{transition:t.id,from:t.from,event:t.event,problem:"Running bypasses admission"});
     need(!missing.length,{transition:t.id,from:t.from,missing_guards:missing,counterexample:missing.length?{true_conditions:t.conditions,false_guard:missing[0],scope:"Boolean conjunction only"}:null});
   }
 });
 group("STATE-04 uncertainty, stop and completion safety",need=>{
   for(const t of job.filter(x=>x.from==="unknown"&&x.to!=="unknown")){
     need(["needs_action","blocked","cancelled","mock_completed"].includes(t.to),{transition:t.id,problem:"Unknown bypasses reconciliation"});
     need(t.conditions.includes("no_pending_effect"),{transition:t.id,problem:"Unknown exit lacks no_pending_effect"});
     if(t.to==="needs_action")need(t.conditions.includes("safe_next_step_proven")&&t.conditions.includes("not_cancelled_or_policy_revoked"),{transition:t.id,problem:"Recovery lacks safe step/current authority"});
   }
   for(const t of job.filter(x=>x.to==="mock_completed"))need(["mock_environment","goal_evidence_valid","no_pending_effect"].every(g=>t.conditions.includes(g)),{transition:t.id,problem:"Mock completion missing evidence or scope gate"});
   for(const t of job.filter(x=>x.from==="stopping"&&x.to!=="unknown"&&x.to!=="stopping"))need(t.to!=="ready"&&t.to!=="running"&&t.conditions.includes("no_pending_effect"),{transition:t.id,problem:"Stop path allows new work or unresolved effect exit"});
   for(const t of job.filter(x=>["cancelled","blocked","failed"].includes(x.to)))need(t.conditions.includes("no_pending_effect"),{transition:t.id,problem:"Pending effect can be discarded"});
 });
 group("EFFECT-01 attempt lifecycle and proof events",need=>{
   const es=new Set(c.effect_states),ts=c.effect_transitions;
   need(unique(c.effect_states)&&unique(ts.map(t=>t.from+"|"+t.event)),"Duplicate effect state/event");
   need(["not_dispatched","admitted","effect_absent","effect_confirmed","effect_unknown"].every(x=>es.has(x)),"Required attempt states missing");
   need(ts.every(t=>es.has(t.from)&&es.has(t.to)),"Unknown effect transition endpoint");
   const ee=ts.map(t=>[t.from,t.to]),reached=reach(["not_dispatched"],ee);
   need([...es].every(s=>reached.has(s)),"Unreachable attempt state");
   for(const t of ts){
     if(t.to==="admitted")need(t.from==="not_dispatched"&&t.event==="permit_consumed",{transition:t,problem:"Repeat admission of same attempt"});
     if(["effect_absent","effect_confirmed"].includes(t.from))need(false,{transition:t,problem:"Resolved attempt must not be reused"});
     if(t.to==="effect_absent")need(t.event==="absence_proven",{transition:t,problem:"Absence without proof event"});
     if(t.to==="effect_confirmed")need(t.event==="effect_proven",{transition:t,problem:"Effect confirmation without proof event"});
     if(t.from==="effect_unknown")need(["effect_unknown","effect_absent","effect_confirmed"].includes(t.to),{transition:t,problem:"Uncertain attempt may not be redispatched"});
   }
 });
 const schemas=[...a.schemas,...o.schemas],types=[...Object.keys(a.types),...Object.keys(o.schema_types),...schemas.map(s=>s.id),"JobState","EffectClass","EffectState","id","positive_int","nonnegative_int","timestamp","digest","string","boolean","json"],typeSet=new Set(types);
 const known=t=>typeof t==="string"&&typeSet.has(t.replace(/\[\]$/,""));
 const routes=[...p.api.filter(x=>!o.routes.some(y=>y.id===x.id)),...o.routes];
 group("WIRE-01 full inherited schema and enum resolution",need=>{
   need(unique(types),"Duplicate type name across inherited/overlay schema namespace");
   for(const [name,values] of Object.entries({...a.types,...o.schema_types}))need(Array.isArray(values)&&values.length>0&&unique(values)&&values.every(v=>typeof v==="string"),{type:name,problem:"Invalid enum"});
   for(const s of schemas){need(unique(s.fields.map(f=>f.name)),{schema:s.id,problem:"Duplicate field"});for(const f of s.fields)need(known(f.type)&&typeof f.required==="boolean"&&typeof f.name==="string"&&f.name.length>0,{schema:s.id,field:f.name,type:f.type,problem:"Unresolved type/requiredness"});}
 });
 group("WIRE-02 effective typed route/port resolution",need=>{
   need(unique(routes.map(x=>x.id))&&unique(routes.map(x=>x.method+" "+x.path)),"Duplicate effective route");
   for(const x of routes){
     // The two inherited descriptive input declarations are expressly not executable schemas.
     const descriptive=(x.id==="HTTP-02"&&x.input==="multipart file + rights + key")||(x.id==="HTTP-17"&&x.input==="after_revision optional");
     if(descriptive)unverified.push({id:x.id,reason:"Inherited input is descriptive, not a typed wire schema"});
     need(descriptive||known(x.input),{route:x.id,input:x.input,problem:"Unknown input type"});
     need(known(x.output),{route:x.id,output:x.output,problem:"Unknown output type"});
   }
   for(const x of o.ports){
     const inputs=x.input.split(" / "),outputs=x.output.split(" / ");
     need(inputs.length===outputs.length&&inputs.every(known)&&outputs.every(known),{port:x.id,problem:"Unresolved or mismatched signature"});
   }
 });
 group("WIRE-03 UI cannot call internal routes",need=>{
   for(const screen of i.screens)for(const id of screen.api_refs){const route=routes.find(x=>x.id===id);need(route&&route.method!=="INTERNAL",{screen:screen.id,route:id,problem:"Unknown or internal route exposed in UI mapping"});}
 });
 const comp=new Map(d.components.map(x=>[x.id,x])),depEdges=d.components.flatMap(x=>x.depends_on.map(y=>[x.id,y]));
 group("ARCH-01 declared component dependency DAG",need=>{
   need(comp.size===d.components.length,"Duplicate component ID");
   for(const x of d.components){need(unique(x.depends_on)&&x.depends_on.every(y=>comp.has(y)&&y!==x.id),{component:x.id,problem:"Unknown, duplicate or self dependency"});need(!x.depends_on.some(y=>reach([y],depEdges).has(x.id)),{component:x.id,problem:"Declared dependency cycle"});}
 });
 // A call map is not automatically a compile-time dependency. Report a discrepancy, do not force edges or assert a cycle in implementation.
 const calls=[...i.route_groups.map(x=>({id:x.id,provider:x.provider,consumers:[x.consumer]})),...i.port_groups];
 for(const call of calls)for(const consumer of call.consumers??[]){
   if(consumer===call.provider)continue;
   if(!comp.has(consumer)||!comp.has(call.provider))continue;
   if(!reach([consumer],depEdges).has(call.provider))review.push({id:"ARCH-R01",contract:call.id,consumer,provider:call.provider,reverse_dependency:reach([call.provider],depEdges).has(consumer),reason:"Consumer/provider call has no corresponding path in declared component dependencies; classify runtime call vs static dependency and update current architecture or mapping"});
 }
 group("TRACE-01 preserve original acceptance test subjects",need=>{
   const defs=[...w.tests,...o.tests,...r.tests,...(i.additional_test_plans??[])];
   need(unique(defs.map(x=>x.id)),"Duplicate ID among test catalogs");
   for(const t of w.tests){const mapping=i.tests.find(x=>x.id===t.id);need(mapping&&t.requirement_refs.every(id=>mapping.requirement_refs.includes(id)),{test:t.id,source:t.requirement_refs,mapped:mapping?.requirement_refs,problem:"WBS acceptance requirement lost in trace index"});}
 });
 const extraConditions=[...new Set(job.flatMap(t=>t.conditions))].filter(g=>!allGuards.has(g));
 unverified.push({id:"GUARD-SEMANTICS",conditions:extraConditions,reason:"Guard/event predicates lack a machine-readable truth/update model; topology and conjunct presence only, no semantic reachability/liveness proof"});
 unverified.push({id:"PRODUCT",reason:"No implementation/DB/browser/concurrency/security/real platform/user value execution"});
 return {kind:"design_constraint_validation",checks,passed:checks.filter(x=>x.pass).length,total:checks.length,review,unverified,product_execution:"not_run",scope:"Pinned source contracts; no design or phase adoption."};
}

export function runConstraintRegression(D,validate){
 const clone=x=>JSON.parse(JSON.stringify(x)),cases=[];
 const mutate=(name,target,fn)=>{const copy=clone(D);try{fn(copy);const output=validate(copy);const failure=output.checks.find(x=>x.id.split(" ")[0]===target&&!x.pass);cases.push({name,target,pass:!!failure,detected:output.checks.filter(x=>!x.pass).map(x=>x.id)});}catch(e){cases.push({name,target,pass:false,error:String(e)});}};
 mutate("transition to nonexistent state","STATE-01",x=>x.core.transitions[0].to="nonexistent");
 mutate("duplicate event from same state","STATE-01",x=>x.core.transitions.push({...x.core.transitions[0],id:"bad-duplicate"}));
 mutate("orphan state","STATE-02",x=>x.core.job_states.push("orphan"));
 mutate("live reserved state reachable","STATE-02",x=>x.core.transitions.push({id:"bad-live",from:["ready"],to:"target_confirmed",event:"bad_live",conditions:[]}));
 mutate("terminal can restart","STATE-02",x=>x.core.transitions.push({id:"bad-restart",from:["cancelled"],to:"planned",event:"restart",conditions:[]}));
 mutate("remove approval guard from actual dispatch","STATE-03",x=>{const t=x.core.transitions.find(t=>t.to==="running");t.conditions=t.conditions.filter(g=>g!=="approval_current");});
 mutate("remove mandatory guard reference and actual condition","STATE-03",x=>{x.core.dispatch.required_guard_refs=x.core.dispatch.required_guard_refs.filter(id=>id!=="V3-G10");x.core.transitions.find(t=>t.to==="running").conditions=x.core.transitions.find(t=>t.to==="running").conditions.filter(g=>g!=="lease_current_exclusive");});
 mutate("delete owner safety obligation from all declarations","STATE-03",x=>{x.core.guards=x.core.guards.filter(g=>g.id!=="V3-G02");x.core.dispatch.required_guard_refs=x.core.dispatch.required_guard_refs.filter(id=>id!=="V3-G02");for(const t of x.core.transitions)t.conditions=t.conditions.filter(g=>g!=="owner_verified");});
 mutate("direct dispatch from unknown","STATE-03",x=>x.core.transitions.find(t=>t.to==="running").from.push("unknown"));
 mutate("uncertain recovery without absence gate","STATE-04",x=>{const t=x.core.transitions.find(t=>t.id==="V3-J11");t.conditions=t.conditions.filter(g=>g!=="no_pending_effect");});
 mutate("completion without goal proof","STATE-04",x=>{const t=x.core.transitions.find(t=>t.to==="mock_completed");t.conditions=t.conditions.filter(g=>g!=="goal_evidence_valid");});
 mutate("cancel with pending effect","STATE-04",x=>{const t=x.core.transitions.find(t=>t.id==="V3-J14");t.conditions=t.conditions.filter(g=>g!=="no_pending_effect");});
 mutate("unknown attempt readmitted","EFFECT-01",x=>x.core.effect_transitions.push({from:"effect_unknown",event:"retry",to:"admitted"}));
 mutate("timeout interpreted as absence","EFFECT-01",x=>x.core.effect_transitions.find(t=>t.from==="effect_unknown"&&t.to==="effect_absent").event="timeout");
 mutate("inherited schema type broken","WIRE-01",x=>x.api.schemas[0].fields[0].type="InventedType");
 mutate("duplicate enum value","WIRE-01",x=>x.contract.schema_types.Support.push(x.contract.schema_types.Support[0]));
 mutate("inherited output type broken","WIRE-02",x=>x.physical.api.find(t=>t.id==="HTTP-17").output="InventedType");
 mutate("internal route exposed to UI","WIRE-03",x=>x.index.screens[0].api_refs.push("HTTP-19"));
 mutate("component dependency cycle","ARCH-01",x=>x.implementation.components.find(t=>t.id==="C4-10").depends_on.push("C4-02"));
 mutate("acceptance requirement removed from index","TRACE-01",x=>{const t=x.index.tests.find(t=>t.id===x.wbs.tests[0].id);t.requirement_refs=t.requirement_refs.filter(id=>id!==x.wbs.tests[0].requirement_refs[0]);});
 const baseline=validate(D);
 // Review checks are separate from hard assertions. Test a novel discrepancy by removing a real dependency.
 const extra=clone(D);extra.implementation.components.find(t=>t.id==="C4-02").depends_on=extra.implementation.components.find(t=>t.id==="C4-02").depends_on.filter(id=>id!=="C4-03");
 const reviewCase=validate(extra).review.some(t=>t.contract==="HTTP-01"&&t.consumer==="C4-02"&&t.provider==="C4-03")&&!baseline.review.some(t=>t.contract==="HTTP-01");
 cases.push({name:"new call/dependency discrepancy",target:"ARCH-R01",pass:reviewCase});
 // A killed mutant must start from a passing baseline for the targeted check.
 for(const t of cases){const b=baseline.checks.find(x=>x.id.split(" ")[0]===t.target);if(b&&!b.pass){t.pass=false;t.reason="Baseline already failed this check; cannot count as detected mutation";}}
 return {cases,passed:cases.filter(x=>x.pass).length,total:cases.length};
}
