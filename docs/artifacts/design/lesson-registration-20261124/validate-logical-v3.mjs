export function verify(m){
 const key=s=>JSON.stringify(s),match=(s,t)=>Object.entries(t.when).every(([k,v])=>Array.isArray(v)?v.includes(s[k]):s[k]===v);
 const q=[m.initial],seen=new Map([[key(m.initial),[]]]),used=new Set(),errors=new Map(),edgeMap=new Map(),term=["done","stopped"],count={active:0,stopping:0,done:0,stopped:0};
 const fail=(id,p,s)=>{if(!errors.has(id))errors.set(id,{id,path:p,state:s});};
 const errorEvents=new Set(["error_detected","error_effect_absent"]); 
 for(let i=0;i<q.length;i++){
  const s=q[i],p=seen.get(key(s)),out=m.transitions.filter(t=>match(s,t));edgeMap.set(key(s),[]);
  if(s.job in count)count[s.job]++;
  if(term.includes(s.job)&&out.length)fail("terminal reopened",p,s);
  if(s.job==="stopping"&&(!out.length||out.some(t=>!t.id.startsWith("finish_stop"))))fail("stop finalization incomplete",p,s);
  if(s.job==="active"&&!out.some(t=>t.id==="error_detected"))fail("error stop unavailable",p,s);
  if(s.job==="done"&&(s.step!==3||s.effect!=="none"))fail("goal without proof",p,s);
  if(s.effect==="pending"&&!["active","stopping"].includes(s.job))fail("pending escaped",p,s);
  if(s.control==="worker"&&!(s.job==="active"&&s.auth==="verified"&&s.approval==="current"&&s.policy==="allowed"&&s.step<3))fail("worker unauthorized",p,s);
  if(s.job!=="none"&&(s.plan!=="current"||s.source!=="confirmed"||s.draft!=="confirmed"))fail("locked scope lost",p,s);
  if(s.approval==="current"&&!(s.plan==="current"&&s.target==="new"&&s.auth==="verified"&&s.draft==="confirmed"&&s.source==="confirmed"&&s.route==="supported"&&s.policy==="allowed"))fail("stale approval",p,s);
  for(const t of out){
   used.add(t.id);const n={...s,...t.set},np=[...p,t.id];edgeMap.get(key(s)).push(key(n));
   if(s.job!=="none"&&String(t.actor).includes("USER"))fail("user changes accepted job",np,n);
   if(s.job==="active"&&n.job==="stopping"&&(!errorEvents.has(t.id)||!["SYSTEM","TRUSTED_OBSERVATION"].includes(t.actor)))fail("nonerror stop",np,n);
   if(t.id==="error_detected"&&!t.external_guard)fail("error source not specified",np,n);
   if(errorEvents.has(t.id)&&(n.control!=="none"||n.step!==s.step||n.job!=="stopping"))fail("error stop unsafe",np,n);
   if(t.id==="admit"&&!(s.job==="active"&&s.route==="supported"&&s.policy==="allowed"&&s.source==="confirmed"&&s.draft==="confirmed"&&s.auth==="verified"&&s.target==="new"&&s.plan==="current"&&s.approval==="current"&&s.control==="worker"&&s.effect==="none"&&s.step<3))fail("unsafe admission",np,n);
   if(n.step<s.step||s.job!=="none"&&n.job==="none")fail("history reset",np,n);
   if(s.job==="stopping"&&(n.job!=="stopped"||n.control!=="none"||n.step!==s.step||n.effect!==(s.effect==="pending"?"unknown":s.effect)))fail("stop lost history",np,n);
   if(t.id==="open_auth"&&(n.plan!=="none"||n.approval!=="none"||n.target!=="unset"))fail("reauth retains old binding",np,n);
   if(["select_supported","select_unsupported","provide_or_revise_source","prepare_draft","prestart_auth_lost","prestart_policy_block"].includes(t.id)&&(n.plan!=="none"||n.approval!=="none"||n.target!=="unset"))fail("changed input retains binding",np,n);
   if(!seen.has(key(n))){seen.set(key(n),np);q.push(n);}
  }
 }
 const rev=new Map();for(const [a,bs] of edgeMap)for(const b of bs){if(!rev.has(b))rev.set(b,[]);rev.get(b).push(a);}
 const ends=q.filter(s=>term.includes(s.job)||s.route==="unsupported"||s.policy==="blocked"||["existing","ambiguous"].includes(s.target)).map(key),reachable=new Set(ends),r=[...ends];for(let i=0;i<r.length;i++)for(const a of rev.get(r[i])??[])if(!reachable.has(a)){reachable.add(a);r.push(a);}
 const stuck=q.filter(s=>!reachable.has(key(s)));if(stuck.length)fail("no outcome path",seen.get(key(stuck[0])),stuck[0]);
 return {states:q.length,edges:[...edgeMap.values()].reduce((a,b)=>a+b.length,0),counts:count,unused:m.transitions.filter(t=>!used.has(t.id)).map(t=>t.id),violations:[...errors.values()],no_outcome:stuck.length,normal_path:seen.get(key(q.find(s=>s.job==="done"))),unknown_stop_path:seen.get(key(q.find(s=>s.job==="stopped"&&s.effect==="unknown"))),known_absent_stop_path:seen.get(key(q.find(s=>s.job==="stopped"&&s.effect==="absent"))),limits:"Finite declared logical model only; error source, evidence, external effects, key storage and execution environment not tested."};
}
