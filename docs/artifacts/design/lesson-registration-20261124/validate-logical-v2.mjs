export function verify(m){
 const key=s=>JSON.stringify(s),match=(s,t)=>Object.entries(t.when).every(([k,v])=>Array.isArray(v)?v.includes(s[k]):s[k]===v);
 const q=[m.initial],seen=new Map([[key(m.initial),[]]]),used=new Set(),edges=new Map(),errors=new Map(),terminal=["done","failed","stopped"],edit=["provide_or_revise_source","confirm_source","select_supported","select_unsupported","prepare_draft","confirm_draft","make_plan"],fail=(id,path,state)=>{if(!errors.has(id))errors.set(id,{id,path,state})};
 const count={active:0,waiting:0,stopping:0,done:0,failed:0,stopped:0};
 for(let i=0;i<q.length;i++){
 const s=q[i],p=seen.get(key(s)),out=m.transitions.filter(t=>match(s,t));edges.set(key(s),[]);if(s.job in count)count[s.job]++;
 if(terminal.includes(s.job)&&out.length)fail("terminal reopened",p,s);
 if(s.job==="stopping"&&(!out.length||out.some(t=>!t.id.startsWith("finish_stop"))))fail("stop not bounded",p,s);
 if(["active","waiting"].includes(s.job)&&!out.some(t=>t.id==="request_stop"))fail("stop unavailable",p,s);
 if(s.job==="done"&&!(s.step===3&&s.effect==="none"))fail("unproven completion",p,s);
 if(s.effect==="pending"&&!["active","stopping"].includes(s.job))fail("pending escaped",p,s);
 if(s.control==="worker"&&!(s.job==="active"&&s.auth==="verified"&&s.approval==="current"&&s.policy==="allowed"&&s.step<3))fail("worker unauthorized",p,s);
 if(s.job!=="none"&&(s.plan!=="current"||s.source!=="confirmed"||s.draft!=="confirmed"))fail("locked scope lost",p,s);
 if(s.approval==="current"&&!(s.plan==="current"&&s.target==="new"&&s.auth==="verified"&&s.draft==="confirmed"&&s.source==="confirmed"&&s.route==="supported"&&s.policy==="allowed"))fail("stale approval",p,s);
 for(const t of out){used.add(t.id);const n={...s,...t.set},np=[...p,t.id];edges.get(key(s)).push(key(n));
 if(t.id==="admit"&&!(s.job==="active"&&s.route==="supported"&&s.policy==="allowed"&&s.source==="confirmed"&&s.draft==="confirmed"&&s.auth==="verified"&&s.target==="new"&&s.plan==="current"&&s.approval==="current"&&s.control==="worker"&&["none","absent"].includes(s.effect)&&s.step<3))fail("unsafe admission",np,n);
 if(s.job!=="none"&&edit.includes(t.id)||s.control==="human"&&edit.includes(t.id))fail("scope edit at wrong stage",np,n);
 if(n.step<s.step||s.job!=="none"&&n.job==="none")fail("history reset",np,n);
 if(s.job==="stopping"&&(n.job!=="stopped"||n.step!==s.step||n.effect!==(s.effect==="pending"?"unknown":s.effect)))fail("stop lost history",np,n);
 if(t.id==="explicit_resume"&&!(s.job==="waiting"&&s.control==="read"&&["none","absent"].includes(s.effect)&&s.step<3))fail("unsafe resume",np,n);
 if(t.id==="open_auth"&&(n.plan!=="none"||n.approval!=="none"||n.target!=="unset"))fail("reauth retains old binding",np,n);
 if(["select_supported","select_unsupported","provide_or_revise_source","prepare_draft","prestart_auth_lost","prestart_policy_block"].includes(t.id)&&(n.plan!=="none"||n.approval!=="none"||n.target!=="unset"))fail("changed input retains binding",np,n);
 if(!seen.has(key(n))){seen.set(key(n),np);q.push(n)}
 }
 }
 const reverse=new Map();for(const [a,bs] of edges)for(const b of bs){if(!reverse.has(b))reverse.set(b,[]);reverse.get(b).push(a)}
 const ends=q.filter(s=>terminal.includes(s.job)||s.route==="unsupported"||s.policy==="blocked"||["existing","ambiguous"].includes(s.target)).map(key),r=[...ends],reachable=new Set(r);for(let i=0;i<r.length;i++)for(const a of reverse.get(r[i])??[])if(!reachable.has(a)){reachable.add(a);r.push(a)}
 const stuck=q.filter(s=>!reachable.has(key(s)));if(stuck.length)fail("no reachable outcome",seen.get(key(stuck[0])),stuck[0]);
 return {states:q.length,edges:[...edges.values()].reduce((a,b)=>a+b.length,0),counts:count,unused:m.transitions.filter(t=>!used.has(t.id)).map(t=>t.id),violations:[...errors.values()],no_outcome:stuck.length,normal_path:seen.get(key(q.find(s=>s.job==="done"))),limits:"Finite reachability, not guaranteed progress or actual runtime. Current permission, trusted observation, safe next step, identity and atomicity are abstract event preconditions."};
}
