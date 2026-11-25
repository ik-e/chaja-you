// Common read-only design verification primitives and evidence gate; domain rules live in adapters.
export function canonical(x){if(Array.isArray(x))return "["+x.map(canonical).join(",")+"]";if(x&&typeof x==="object")return "{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";return JSON.stringify(x);}

export function guardedTransitions({transitions,from,to,event,required}){
 if(!Array.isArray(transitions)||!Array.isArray(from)||!Array.isArray(required)||!from.length||!required.length)throw Error("guard inputs incomplete");
 const findings=[];for(const state of from){const edges=transitions.filter(t=>Array.isArray(t.from)&&t.from.includes(state)&&t.to===to);if(!edges.length)findings.push({state,to,reason:"no declared transition"});for(const t of edges){if(!Array.isArray(t.conditions))throw Error("conditions not structured");const missing=required.filter(x=>!t.conditions.includes(x));if(t.event!==event||missing.length)findings.push({state,transition:t.id,event:t.event,expected_event:event,missing_guards:missing});}}
 return {pass:findings.length===0,findings,limit:"Declared edge/guard presence, not truth/update semantics or executable safety."};
}

export function compositionGraph({nodes,dependencies,calls}){
 if(!Array.isArray(nodes)||!nodes.length||!Array.isArray(dependencies)||!Array.isArray(calls)||!calls.length)throw Error("graph inputs incomplete");
 const known=new Set(nodes),next=new Map(nodes.map(x=>[x,[]])),findings=[];
 if(known.size!==nodes.length)findings.push({reason:"duplicate nodes"});
 for(const [a,b] of dependencies){if(!known.has(a)||!known.has(b)){findings.push({reason:"unknown dependency endpoint",from:a,to:b});continue;}next.get(a).push(b);}
 const reachable=(a,b)=>{const q=[...(next.get(a)??[])],seen=new Set();for(let n=0;n<q.length;n++){if(q[n]===b)return true;if(!seen.has(q[n])){seen.add(q[n]);q.push(...(next.get(q[n])??[]));}}return false;};
 for(const n of nodes)if(reachable(n,n))findings.push({reason:"dependency cycle",node:n});
 for(const {id,consumer,provider} of calls)if(!known.has(consumer)||!known.has(provider)||consumer!==provider&&!reachable(consumer,provider))findings.push({reason:"call not covered by declared dependency path",id,consumer,provider,reverse_dependency:known.has(provider)&&reachable(provider,consumer)});
 return {pass:findings.length===0,findings,limit:"Only valid if selected dependency graph is defined as logical call/use dependency; not implementation imports or actual runtime."};
}

export function typedUses({types,uses}){
 if(!Array.isArray(types)||!types.length||!Array.isArray(uses)||!uses.length)throw Error("type inputs incomplete");
 const known=new Set(types),findings=[];for(const x of uses)if(typeof x.type!=="string"||!known.has(x.type.replace(/\[\]$/,"")))findings.push({id:x.id,field:x.field,type:x.type,reason:"unresolved type declaration"});
 return {pass:findings.length===0,findings,limit:"Type-name resolution, not value-level compatibility or transport implementation."};
}

export function requiredCoverage({required,declared,linked}){
 if(!Array.isArray(required)||!required.length||!Array.isArray(declared)||!Array.isArray(linked))throw Error("coverage inputs incomplete");
 const findings=required.filter(x=>!declared.includes(x)||!linked.includes(x)).map(id=>({id,declared:declared.includes(id),linked:linked.includes(id)}));
 return {pass:!findings.length,findings,limit:"Coverage of explicitly selected obligations only; not completeness of requirements or test execution."};
}

export function ruleIdentity(rule,sources,revisions){
 if(!rule||typeof rule.id!=="string"||!rule.id||typeof rule.revision!=="string"||!rule.revision||!Array.isArray(rule.source_refs)||!rule.source_refs.length||new Set(rule.source_refs).size!==rule.source_refs.length||typeof revisions?.engine!=="string"||!revisions.engine||typeof revisions?.adapter!=="string"||!revisions.adapter)throw Error("rule identity incomplete");
 const fingerprints={};for(const id of rule.source_refs){const s=sources[id];if(!s||typeof s.blob_sha!=="string"||!s.blob_sha||!Object.hasOwn(s,"data"))throw Error("source unavailable: "+id);fingerprints[id]=s.blob_sha;}
 return {rule_signature:canonical(rule),engine:revisions.engine,adapter:revisions.adapter,inputs:fingerprints};
}

export function executeDesignRules(rules,sources,checkers,revisions){
 if(!Array.isArray(rules)||new Set(rules.map(x=>x.id)).size!==rules.length)throw Error("invalid rule manifest");
 return rules.map(rule=>{
  const result={id:rule.id,kind:rule.kind,method:rule.method,stage:rule.stage,verdict:"not_run",findings:[],product_execution:"not_run"};
  try{
   result.identity=ruleIdentity(rule,sources,revisions);
   if(!["refinement","composition","change","local"].includes(rule.kind)||!["deterministic","review","experiment"].includes(rule.method)||!/^L[0-7]$/.test(rule.stage)||typeof rule.required!=="boolean"||!Array.isArray(rule.policy_refs)||!rule.policy_refs.length||typeof rule.question!=="string"||!rule.question)throw Error("invalid rule definition");
   if(rule.method!=="deterministic"){result.reason="External review/experiment requires its own actual evidence; engine does not infer pass.";return result;}
   const check=checkers[rule.checker];if(typeof check!=="function")throw Error("checker unavailable: "+rule.checker);
   const observed=check(Object.fromEntries(rule.source_refs.map(id=>[id,sources[id].data])),rule);
   if(typeof observed?.pass!=="boolean"||!Array.isArray(observed.findings)||typeof observed.limit!=="string"||!observed.limit)throw Error("checker did not return evaluable evidence");
   return {...result,verdict:observed.pass?"pass":"fail",findings:observed.findings,limit:observed.limit};
  }catch(e){return {...result,verdict:"unknown",reason:String(e)};}
 });
}

export function designStageGate({rules,sources,revisions,results,stage}){
 if(!Array.isArray(rules)||!Array.isArray(results)||!/^L[0-7]$/.test(stage))throw Error("invalid stage gate input");
 const required=rules.filter(r=>r.stage===stage&&r.required),failed=[],unresolved=[],fresh=[];
 if(!required.length)return {status:"review_required",reason:"no required checks declared for this slice and stage",failed,unresolved,fresh,authority:"not_granted",product_execution:"not_run"};
 for(const rule of required){
  let expected;try{expected=ruleIdentity(rule,sources,revisions);}catch(e){unresolved.push({id:rule.id,reason:String(e)});continue;}
  const matching=results.filter(x=>x.id===rule.id&&x.method===rule.method&&x.kind===rule.kind&&x.stage===rule.stage&&x.identity&&canonical(x.identity)===canonical(expected));
  if(matching.some(x=>x.verdict==="fail"))failed.push(rule.id);
  else if(matching.length!==1||matching[0].verdict!=="pass"||rule.method!=="deterministic")unresolved.push({id:rule.id,reason:matching.length===0?"missing or stale evidence":"nonpassing, ambiguous or external evidence"});
  else fresh.push(rule.id);
 }
 return {status:failed.length?"blocked":unresolved.length?"review_required":"declared_checks_pass",failed,unresolved,fresh,authority:"not_granted",product_execution:"not_run",limit:"Only the selected required deterministic rules; no stage adoption or overall completeness claim."};
}

export function selfTest(){
 const cases=[];const add=(id,pass)=>cases.push({id,pass:!!pass});
 const rule={id:"S1",revision:"1",kind:"refinement",method:"deterministic",stage:"L5",required:true,question:"upper approval preserved?",source_refs:["a"],policy_refs:["policy:approval"],checker:"guard"};
 const data={a:{blob_sha:"a1",data:{transitions:[{id:"t",from:["paused"],to:"ready",event:"resume",conditions:["approved"]}],from:["paused"],to:"ready",event:"resume",required:["approved"]}}};
 const checker={guard:d=>guardedTransitions(d.a)},rev={engine:"e1",adapter:"c1"},run=(r=rule,s=data,c=checker,v=rev)=>executeDesignRules([r],s,c,v),gate=(results,sources=data,revisions=rev,rules=[rule])=>designStageGate({rules,sources,revisions,results,stage:"L5"});
 const result=run();add("valid selected rule",result[0].verdict==="pass"&&gate(result).status==="declared_checks_pass");
 const broken={a:{blob_sha:"a2",data:{...data.a.data,transitions:[{...data.a.data.transitions[0],conditions:[]}]}}};add("actual removed guard",run(rule,broken)[0].verdict==="fail"&&gate(run(rule,broken),broken).status==="blocked");
 add("stale evidence",gate(result,broken).status==="review_required");add("unrelated change retained",gate(result,{...data,z:{blob_sha:"z1",data:{}}}).status==="declared_checks_pass");
 add("checker change",gate(result,data,{...rev,adapter:"c2"}).status==="review_required");add("rule change",gate(result,data,rev,[{...rule,question:"new question"}]).status==="review_required");
 add("missing source",run(rule,{})[0].verdict==="unknown");add("missing checker",run(rule,data,{})[0].verdict==="unknown");add("invalid checker result",run(rule,data,{guard:()=>({pass:true})})[0].verdict==="unknown");
 add("review not inferred",run({...rule,method:"review"})[0].verdict==="not_run");add("experiment not inferred",run({...rule,method:"experiment"})[0].verdict==="not_run");
 add("empty manifest not passed",gate([],data,rev,[]).status==="review_required");add("missing execution",gate([]).status==="review_required");add("duplicate evidence refused",gate([...result,...result]).status==="review_required");
 add("fail dominates",gate([...result,{...result[0],verdict:"fail"}]).status==="blocked");
 add("composition mismatch",!compositionGraph({nodes:["A","B"],dependencies:[],calls:[{id:"P",consumer:"A",provider:"B"}]}).pass);
 add("composition cycle",!compositionGraph({nodes:["A","B"],dependencies:[["A","B"],["B","A"]],calls:[{id:"P",consumer:"A",provider:"B"}]}).pass);
 add("unknown type",!typedUses({types:["A"],uses:[{id:"X",field:"input",type:"B"}]}).pass);
 add("missing required coverage",!requiredCoverage({required:["A"],declared:["A"],linked:[]}).pass);
 return {cases,passed:cases.filter(x=>x.pass).length,total:cases.length};
}
