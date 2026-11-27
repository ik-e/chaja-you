// Bounded logical model and structural checks. No real platform access.
import {readFileSync} from "node:fs";
function verify(r){
 const fail=(v,m)=>{if(!v)throw Error(m)};
 const ax=new Map(r.axes.map(a=>[a.id,a])),ts=new Set(r.transitions.map(t=>t.id));
 fail(ax.size===17&&ts.size===73,"axis/transition IDs");
 const reachable={};
 for(const a of r.axes){const seen=new Set([a.initial]);let change=true;while(change){change=false;for(const t of r.transitions.filter(t=>t.axis===a.id))if(t.from.some(s=>seen.has(s))&&!seen.has(t.to)){seen.add(t.to);change=true;}}fail(a.values.every(v=>seen.has(v)),"unreachable "+a.id);reachable[a.id]=seen.size;}
 fail(r.transitions.every(t=>{const a=ax.get(t.axis);return a&&a.values.includes(t.to)&&t.from.every(x=>a.values.includes(x)&&!a.terminal.includes(x));}),"domain/terminal violation");
 const refs=[...r.atomic_boundaries.flatMap(x=>x.transition_refs),...r.prior_rule_trace.flatMap(x=>x.transition_refs),...r.screen_trace.flatMap(x=>x.transition_refs),...r.operation_trace.flatMap(x=>x.checkpoints.flatMap(c=>c.transition_refs)),...r.work_trace.flatMap(x=>x.transition_refs),...r.error_trace.flatMap(x=>x.transition_refs),...r.instructor_trace.flatMap(x=>x.transition_refs)];
 fail(refs.every(x=>ts.has(x)),"transition trace");
 // one write target; two ordered distinct effects; trusted evidence events. States abstract away identities/revisions, external permission, and real concurrency.
 const initial={j:"not_accepted",a:"presented",g:"verified",c:"not_required",e:["not_attempted","not_attempted"],sent:[0,0],q:"pending",ack:"waiting"};
 const copy=s=>JSON.parse(JSON.stringify(s)), key=s=>JSON.stringify(s), succ=s=>{
  let result=[];const emit=(event,mut)=>{let n=copy(s);mut(n);result.push([event,n]);};
  if(s.ack==="waiting")emit("LT-15",n=>n.ack="unknown");
  if(s.j!=="not_accepted"&&s.ack!=="known")emit("LT-16",n=>n.ack="known");
  if(s.j==="not_accepted"&&s.g==="verified"&&s.a==="presented")emit("AT-02",n=>{n.j="accepted";n.a="frozen";});
  if(s.j==="accepted"&&s.g==="verified")emit("LT-34",n=>n.j="running");
  if(["accepted","running"].includes(s.j))emit("AT-04/06-fence",n=>{n.j="fencing";n.g="blocked";n.c="pending";});
  if(s.j==="running"&&s.g==="verified")for(let i=0;i<2;i++){
   if(s.e[i]==="not_attempted"&&(i===0||s.e[i-1]==="confirmed"))emit("LT-38-"+i,n=>n.e[i]="reserved");
   if(s.e[i]==="reserved"&&s.sent[i]===0)emit("LT-39-"+i,n=>{n.e[i]="in_flight";n.sent[i]++;});
  }
  for(let i=0;i<2;i++){
   if(s.e[i]==="reserved"&&s.sent[i]===0)emit("LT-40-"+i,n=>{n.e[i]="none_confirmed";if(n.j==="running"){n.j="fencing";n.g="blocked";n.c="pending";}});
   if(["reserved","in_flight"].includes(s.e[i]))emit("LT-41-"+i,n=>{n.e[i]="unknown";if(n.j==="running"){n.j="fencing";n.g="blocked";n.c="pending";}});
   if(["in_flight","unknown"].includes(s.e[i])&&s.sent[i]===1)emit("LT-42-"+i,n=>n.e[i]="confirmed");
   if(["in_flight","unknown"].includes(s.e[i]))emit("LT-43-"+i,n=>{n.e[i]="none_confirmed";if(n.j==="running"){n.j="fencing";n.g="blocked";n.c="pending";}});
  }
  if(s.j==="running"&&s.e.every(x=>x==="confirmed"))emit("AT-05-complete",n=>{n.j="ended";n.q="complete";n.g="blocked";n.c="pending";});
  if(s.j==="fencing"&&!s.e.some(x=>["reserved","in_flight"].includes(x)))emit("AT-05-end",n=>{n.j="ended";n.q=n.e.includes("unknown")?"effect_unknown":n.e.every(x=>x==="confirmed")?"complete":n.e.includes("confirmed")?"partial_confirmed":n.sent.some(x=>x>0)?"no_effect":"not_executed";});
  if(s.j==="ended"&&s.q==="effect_unknown"&&!s.e.includes("unknown")){const q=s.e.every(x=>x==="confirmed")?"complete":s.e.includes("confirmed")?"partial_confirmed":s.sent.some(x=>x>0)?"no_effect":"not_executed";emit(q==="complete"?"LT-64":q==="partial_confirmed"?"LT-62":q==="no_effect"?"LT-61":"LT-70",n=>n.q=q);}
  if(s.c==="pending")emit("LT-58",n=>n.c="unknown");
  if(["pending","unknown"].includes(s.c))emit("LT-57",n=>n.c="confirmed");
  return result;
 };
 let queue=[initial],seen=new Set([key(initial)]),edges=0,terminal=0,partial=0,unknown=0,complete=0,late=0,violations=[],witness={};
 for(let qi=0;qi<queue.length;qi++){const s=queue[qi];if(s.j==="ended"){terminal++;if(s.q==="partial_confirmed")partial++;if(s.q==="effect_unknown")unknown++;if(s.q==="complete")complete++;}
  if(s.q==="complete"&&!s.e.every(x=>x==="confirmed"))violations.push("false completion");
  if(s.sent.some(x=>x>1))violations.push("duplicate send");
  if(s.sent[1]&&s.e[0]!=="confirmed")violations.push("out of order");
  if(s.j==="ended"&&s.g!=="blocked")violations.push("ended access open");
  if(s.c!=="not_required"&&s.g!=="blocked")violations.push("cleanup without block");
  if(s.j!=="not_accepted"&&s.a!=="frozen")violations.push("no approval");
  for(const [event,n] of succ(s)){edges++;
   if(s.j==="ended"&&n.j!=="ended")violations.push("terminal reopened");
   if(s.g==="blocked"&&n.sent.some((x,i)=>x>s.sent[i]))violations.push("dispatch after fence");
   if(s.e.some((x,i)=>["confirmed","none_confirmed"].includes(x)&&n.e[i]!==x))violations.push("confirmed overwritten");
   if(s.j==="ended"&&event.startsWith("LT-42"))late++;
   if(s.ack==="unknown"&&event==="LT-16")witness.same_command=true;
   if(s.c==="unknown"&&s.g==="blocked")witness.cleanup_unknown_blocked=true;
   if(s.j==="ended"&&s.q==="effect_unknown"&&n.q==="partial_confirmed")witness.late_partial=true;
   if(s.j==="ended"&&s.q==="effect_unknown"&&n.q==="not_executed"&&event==="LT-70")witness.late_not_executed=true;
   const k=key(n);if(!seen.has(k)){seen.add(k);queue.push(n);}
  }
 }
 fail(!violations.length&&partial>0&&unknown>0&&complete>0&&late>0&&witness.late_not_executed===true&&Object.values(witness).every(Boolean),"bounded model invariant/witness: "+JSON.stringify({violations,witness,partial,unknown,complete,late}));
 return {axis_reachability:reachable,abstract_write_model:{targets:1,ordered_effects:2,states:seen.size,edges,terminal_states:terminal,complete_states:complete,partial_states:partial,unknown_states:unknown,late_confirmation_edges:late,violations,witness,scope:"trusted-event bounded model; no actual runtime, full guards, DB transactions, multi-target concurrency or real platform proof"}};
}
const record=JSON.parse(readFileSync(new URL("../docs/artifacts/planning/lesson-registration-20261126/integrated/logical-state-v1.0.json",import.meta.url),"utf8"));
const result=verify(record);
const stable=x=>Array.isArray(x)?x.map(stable):x&&typeof x==="object"?Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;
if(JSON.stringify(stable(result))!==JSON.stringify(stable(record.verification.model)))throw Error("Recorded verification differs; inspect before updating baseline");
console.log(JSON.stringify(result,null,2));
