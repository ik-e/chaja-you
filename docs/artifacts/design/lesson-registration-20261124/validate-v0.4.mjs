import {readFileSync} from 'node:fs';
const iso=(dt)=>dt.toISOString().slice(0,10);
function dates(start,end,cal){const hs=new Set(cal.holidays.map(h=>h.date)),out=[];for(let dt=new Date(start+"T00:00:00Z");iso(dt)<=end;dt.setUTCDate(dt.getUTCDate()+1)){const day=iso(dt);if(!cal.weekend_days_utc.includes(dt.getUTCDay())&&!hs.has(day))out.push(day);}return out;}
function validate(d,p,w,c,a,di){
 const checks=[];const ok=(id,v)=>checks.push({id,pass:!!v});const uniq=x=>new Set(x).size===x.length;const refs=(arr,ids)=>arr.every(x=>ids.has(x));const req=new Set(d.requirements.map(x=>x.id)),comp=new Set(d.components.map(x=>x.id)),src=new Set(d.sources.map(x=>x.id)),tasks=new Set(w.tasks.map(x=>x.id)),api=new Set(p.api.map(x=>x.id));
 ok("unique IDs",uniq([...d.requirements,...d.components,...d.ports,...d.flows,...d.platforms,...d.deployment,...d.decisions,...p.api,...p.ui,...w.tasks,...w.tests,...w.milestones].map(x=>x.id)));
 ok("source refs",d.requirements.every(x=>refs(x.source_refs,src)));
 ok("component req and dependency refs",d.components.every(x=>refs(x.requirement_refs,req)&&refs(x.depends_on,comp)));
 ok("port endpoints",d.ports.every(x=>comp.has(x.consumer)&&comp.has(x.provider)));
 ok("API schemas",p.api.filter(x=>x.input.match(/^[A-Z][a-zA-Z]+$/)).every(x=>a.schemas.some(s=>s.id===x.input)));
 ok("UI API refs",p.ui.every(x=>refs(x.api_refs,api)));
 ok("table names",uniq(p.tables.map(x=>x.name)));
 ok("test refs",w.tests.every(x=>refs(x.requirement_refs,req)));
 ok("all requirements covered by tests",d.requirements.every(x=>w.tests.some(t=>t.requirement_refs.includes(x.id))));
 ok("all requirements covered by work",d.requirements.every(x=>w.tasks.some(t=>t.requirement_refs.includes(x.id))));
 ok("task refs",w.tasks.every(x=>refs(x.requirement_refs,req)&&refs(x.depends_on,tasks)));
 ok("task dates and strict precedence",w.tasks.every(x=>x.start<=x.end&&x.depends_on.every(id=>w.tasks.find(t=>t.id===id).end<x.start)));
 ok("R02 unavailable interval excluded",w.tasks.filter(x=>x.owner==="R02").every(x=>x.work_dates.every(day=>day<w.availability.R02.unavailable_from||day>w.availability.R02.unavailable_through)));
 ok("R02 handoff before absence",w.tasks.find(x=>x.id==="W02").end<=w.availability.R02.handoff_by&&w.availability.R02.handoff_by<w.availability.R02.unavailable_from&&w.tasks.find(x=>x.id==="W02").end===w.availability.R02.planned_handoff);
 ok("milestone refs/date",w.milestones.every(m=>refs(m.refs,tasks)&&m.refs.every(id=>w.tasks.find(x=>x.id===id).end<=m.date)));
 let done=new Set(),visiting=new Set(),acyclic=true;function dfs(id){if(visiting.has(id)){acyclic=false;return;}if(done.has(id))return;visiting.add(id);w.tasks.find(x=>x.id===id).depends_on.forEach(dfs);visiting.delete(id);done.add(id);}w.tasks.forEach(x=>dfs(x.id));ok("WBS DAG",acyclic);
 ok("MVP and final dates",w.milestones.some(x=>x.date==="2026-12-08")&&w.milestones.some(x=>x.date==="2027-01-04"));
 ok("existing state and mock gate",c.guards.some(x=>x.condition==="mock_environment")&&p.api.some(x=>x.id==="HTTP-19"&&x.method==="INTERNAL")&&w.tests.every(x=>x.execution==="not_run"));
 ok("remote technical choice delegated",di.decisions.find(x=>x.id==="DIR-02").state==="delegated_with_constraints"&&d.decisions.some(x=>x.id==="B4-03"&&x.status==="delegated"));
 const cal=w.calendar;const isWork=day=>dates(day,day,cal).length===1;
 ok("calendar weekend and holiday rule",cal.weekend_days_utc.join(",")==="0,6"&&["2026-12-25","2027-01-01"].every(day=>cal.holidays.some(h=>h.date===day&&h.source))&&cal.timezone==="Asia/Seoul");
 ok("all task endpoints and milestones on workdays",w.tasks.every(t=>isWork(t.start)&&isWork(t.end))&&w.milestones.every(m=>isWork(m.date)));
 ok("exact working dates/counts, no weekends or holidays",w.tasks.every(t=>t.workdays>0&&t.workdays===t.work_dates.length&&JSON.stringify(t.work_dates)===JSON.stringify(dates(t.start,t.end,cal))));
 ok("calendar totals",cal.total_workdays===dates(cal.period_start,cal.period_end,cal).length&&cal.mvp_workdays===dates(cal.period_start,"2026-12-08",cal).length&&cal.post_mvp_workdays===dates("2026-12-09",cal.period_end,cal).length&&cal.total_workdays===cal.mvp_workdays+cal.post_mvp_workdays&&cal.r02_unavailable_workdays===dates(w.availability.R02.unavailable_from,w.availability.R02.unavailable_through,cal).length);
 ok("no double-booked primary owner workdays",uniq(w.tasks.flatMap(t=>t.work_dates.map(day=>t.owner+"|"+day))));
 ok("MVP reserve after first integration and before MVP",w.tasks.find(t=>t.id==="W07").end==="2026-12-04"&&w.tasks.find(t=>t.id==="W18").start==="2026-12-07"&&w.tasks.find(t=>t.id==="W09").depends_on.includes("W18")&&w.tasks.find(t=>t.id==="W09").depends_on.includes("W08"));
 ok("final acceptance only on 12/31 and 1/4",JSON.stringify(w.tasks.find(t=>t.id==="W17").work_dates)===JSON.stringify(["2026-12-31","2027-01-04"]));
 return {kind:"static_design_validation",checks,passed:checks.filter(x=>x.pass).length,total:checks.length,calendar_summary:{timezone:cal.timezone,project_workdays:cal.total_workdays,mvp_workdays:cal.mvp_workdays,post_mvp_workdays:cal.post_mvp_workdays,r02_unavailable_workdays:cal.r02_unavailable_workdays,excluded_holidays:cal.holidays.map(x=>x.date),tasks:w.tasks.length},product_execution:"not_run",limitations:"참조·일정·구조·선행조건·근무일·주책임자 중복의 정적 검사만. 실제 DDL·API·보안·브라우저·사용자 가치·공수·실서비스 검증 아님. 보조 참여와 시간 단위 업무량은 배정 전 검토."};
}
const names=["implementation-v0.4.json","physical-v0.4.json","wbs-v0.4.json","core-contract-v0.3.json","data-api-v0.3.json","direction-v0.4.json"];
const result=validate(...names.map(p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'))));
console.log(JSON.stringify(result,null,2));
if(result.passed!==result.total)process.exitCode=1;
