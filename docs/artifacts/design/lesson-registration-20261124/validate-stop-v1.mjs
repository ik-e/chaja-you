export function verify(m){
 const match=(s,t)=>Object.entries(t.when).every(([k,v])=>Array.isArray(v)?v.includes(s[k]):s[k]===v),key=s=>JSON.stringify(s),active=["planned","ready","running","verifying","paused","unknown"],terminal=["done","failed","stopped"],edit=["source_provided","confirm_source","revise_before_start","make_plan"],seen=new Map([[key(m.initial),{state:m.initial,path:[]}]]),q=[m.initial],edges=new Map(),used=new Set(),failures=new Map(),counts={stopping:0,stopped:0,active:0,stop_entry:0,stop_finalize:0,unresolved_stop_results:0,known_stop_results:0};
 const fail=(id,state,path)=>{if(!failures.has(id))failures.set(id,{id,state,path});};
 for(let i=0;i<q.length;i++){const s=q[i],path=seen.get(key(s)).path,out=m.transitions.filter(t=>match(s,t));edges.set(key(s),[]);
  if(active.includes(s.job)){counts.active++;if(!out.some(t=>t.id==="request_stop"))fail("active stop unavailable",s,path);}
  if(s.job==="stopping"){counts.stopping++;if(!out.length||out.some(t=>!t.id.startsWith("finalize_stop")))fail("stopping has nonfinal or no transition",s,path);}
  if(s.job==="stopped"){counts.stopped++;if(s.effect==="unknown")counts.unresolved_stop_results++;else counts.known_stop_results++;}
  if(terminal.includes(s.job)&&out.length)fail("terminal not absorbing",s,path);
  if(s.goal!==(s.job==="done"))fail("normal goal proof mismatch",s,path);
  if(["pending","unknown"].includes(s.effect)&&!["running","stopping","unknown","stopped"].includes(s.job))fail("unresolved effect discarded",s,path);
  if(s.job==="stopped"&&(s.effect==="pending"||s.control!=="none"||s.stop!=="requested"))fail("stopped not settled/fenced",s,path);
  for(const t of out){used.add(t.id);const n={...s,...t.set},p=[...path,t.id];edges.get(key(s)).push(key(n));if(t.id==="request_stop"){counts.stop_entry++;if(n.job!=="stopping"||n.control!=="none"||n.effect!==s.effect||n.step!==s.step)fail("stop entry lost record or not fenced",n,p);}
   if(t.id.startsWith("finalize_stop")){counts.stop_finalize++;if(n.job!=="stopped"||n.step!==s.step||n.goal!==s.goal||n.control!=="none"||n.effect!==(s.effect==="pending"?"unknown":s.effect))fail("stop finalization discards evidence",n,p);}
   if(t.id==="admit"&&!(s.job==="ready"&&s.control==="worker"&&s.auth==="same"&&s.approval==="current"&&s.policy==="mock_allowed"&&s.stop==="none"&&s.info==="confirmed"&&s.plan==="current"&&s.target==="new"&&["none","absent"].includes(s.effect)&&s.step<3))fail("unsafe admission",n,p);
   if(s.job!=="none"&&edit.includes(t.id)||s.auth==="human"&&edit.includes(t.id))fail("scope edit at wrong stage",n,p);
   if(n.step<s.step||s.job!=="none"&&n.job==="none")fail("accepted history reset",n,p);
   if(s.job==="stopping"&&n.job!=="stopped")fail("stop did not terminate",n,p);
   if(!seen.has(key(n))){seen.set(key(n),{state:n,path:p});q.push(n);}
  }
 }
 const reverse=new Map();for(const [a,bs] of edges)for(const b of bs){if(!reverse.has(b))reverse.set(b,[]);reverse.get(b).push(a);}
 const outcomes=[...seen].filter(([k,x])=>terminal.includes(x.state.job)||x.state.job==="paused"||x.state.job==="unknown"||x.state.route==="unsupported"||x.state.policy==="revoked"||["existing","ambiguous"].includes(x.state.target)).map(([k])=>k);
 const reachable=new Set(outcomes),r=[...outcomes];for(let i=0;i<r.length;i++)for(const a of reverse.get(r[i])??[])if(!reachable.has(a)){reachable.add(a);r.push(a);}
 const noOutcome=[...seen].filter(([k])=>!reachable.has(k));if(noOutcome.length)fail("no possible outcome",noOutcome[0][1].state,noOutcome[0][1].path);
 return {state_count:q.length,edge_count:[...edges.values()].reduce((a,b)=>a+b.length,0),counts,unused:m.transitions.filter(t=>!used.has(t.id)).map(t=>t.id),violations:[...failures.values()],no_outcome_count:noOutcome.length,normal_path:[...seen.values()].find(x=>x.state.job==="done")?.path,failed_path:[...seen.values()].find(x=>x.state.job==="failed")?.path,stop_unknown_path:[...seen.values()].find(x=>x.state.job==="stopped"&&x.state.effect==="unknown")?.path,limitations:"Finite single-request model; result projection and reason metadata are independent, actual atomic admission, real side effects/stop, security and cross-request identity not verified."};
}

export function projectStoppedResult(s,late=[]){
 if(s.job!=="stopped")throw Error("not stopped");let step=s.step,effect=s.effect,goal=step===3||effect==="unknown"?"unknown":"not_reached";const observations=[];
 for(const x of late){if(!x.trusted||!x.read_authorized||x.same_target!==true||!x.evidence_ref)continue;
  if(x.kind==="absence"&&effect==="unknown"&&x.step===step){effect="absent";goal=step===3?"unknown":"not_reached";observations.push(x.evidence_ref);}
  else if(x.kind==="effect_confirmed"&&effect==="unknown"&&x.step===step&&step<3){step++;effect="none";goal=step===3?"unknown":"not_reached";observations.push(x.evidence_ref);}
  else if(x.kind==="goal_confirmed"&&step===3&&effect!=="unknown"){goal="confirmed";observations.push(x.evidence_ref);}
 }
 return {job:"stopped",confirmed_steps:step,effect,goal,observations,can_resume:false,can_dispatch:false};
}
