export function verify(m,N){
const key=s=>JSON.stringify(s),match=(s,t)=>Object.entries(t.when).every(([k,v])=>v==="ltN"?s[k]<N:v==="eqN"?s[k]===N:Array.isArray(v)?v.includes(s[k]):s[k]===v),q=[m.initial],seen=new Map([[key(m.initial),[]]]),used=new Set(),errors=new Map();let edges=0;const reverse=new Map();const fail=(id,p,s)=>{if(!errors.has(id))errors.set(id,{id,path:p,state:s});};
for(let i=0;i<q.length;i++){const s=q[i],p=seen.get(key(s)),out=m.rules.filter(t=>match(s,t));
if(["done","stopped"].includes(s.job)&&out.length)fail("terminal reopened",p,s);
if(s.job==="active"&&!out.some(t=>t.id==="error_detected"))fail("error stop unavailable",p,s);
if(s.job==="stopping"&&(!out.length||out.some(t=>!t.id.startsWith("finish_stop"))))fail("stop not finalizable",p,s);
if(s.review&&s.job==="none"&&!(s.prep==="ready"&&s.profile==="supported"&&s.auth==="verified"&&s.target==="new"))fail("stale review",p,s);
if(s.job==="done"&&(s.step!==N||s.effect!=="clear"))fail("unproven completion",p,s);
if(s.job!=="none"&&!(s.source&&s.profile==="supported"&&s.prep==="ready"&&s.review&&s.target==="new"))fail("scope lost",p,s);
for(const t of out){used.add(t.id);edges++;const n={...s,...t.set};if(t.set.step==="inc")n.step=s.step+1;const np=[...p,t.id],k=key(n);if(!reverse.has(k))reverse.set(k,[]);reverse.get(k).push(key(s));
if(s.job!=="none"&&t.actor==="USER")fail("postaccept user mutation",np,n);
if(t.id==="admit"&&!(s.job==="active"&&s.auth==="worker"&&s.effect==="clear"&&s.step<N&&s.review&&s.target==="new"))fail("unsafe admit",np,n);
if(s.job==="active"&&n.job==="stopping"&&!["error_detected","error_effect_absent"].includes(t.id))fail("nonerror stop",np,n);
if(s.job==="stopping"&&(n.job!=="stopped"||n.step!==s.step||n.effect!==(s.effect==="pending"?"unknown":s.effect)))fail("stop evidence loss",np,n);
if(n.step<s.step||n.step>N)fail("progress invalid",np,n);
if(["source_select","select_supported","select_unsupported","select_blocked","prepare_issues","prepare_ready","answer_or_edit","auth_open","auth_close","auth_invalid"].includes(t.id)&&n.review)fail("changed input retains review",np,n);
if(t.id==="accept"&&!(s.job==="none"&&s.prep==="ready"&&s.auth==="verified"&&s.review&&s.target==="new"))fail("accept without review",np,n);
if(!seen.has(k)){seen.set(k,np);q.push(n);}
}}
const ends=q.filter(s=>["done","stopped"].includes(s.job)||["unsupported","blocked"].includes(s.profile)||["existing","ambiguous"].includes(s.target)).map(key),reachable=new Set(ends),r=[...ends];for(let i=0;i<r.length;i++)for(const a of reverse.get(r[i])??[])if(!reachable.has(a)){reachable.add(a);r.push(a);}
const stuck=q.filter(s=>!reachable.has(key(s)));if(stuck.length)fail("no outcome path",seen.get(key(stuck[0])),stuck[0]);
return {N,states:q.length,edges,unused:m.rules.filter(x=>!used.has(x.id)).map(x=>x.id),violations:[...errors.values()],no_outcome:stuck.length,normal_path:seen.get(key(q.find(s=>s.job==="done"))),unknown_stop_path:seen.get(key(q.find(s=>s.job==="stopped"&&s.effect==="unknown")))};
}
