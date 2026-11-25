export function evaluateMvpGate(g,candidate,observations){
 const validCandidate=c=>c&&g.candidate_fields.every(k=>typeof c[k]==="string"&&c[k].length>0)&&c.environment===g.environment;
 if(!validCandidate(candidate))return {verdict:"incomplete",reason:"invalid candidate",missing:g.required_test_refs};
 const current=observations.filter(x=>x&&typeof x.run_ref==="string"&&x.run_ref.length>0&&x.execution_kind===g.execution_kind&&validCandidate(x.candidate)&&g.candidate_fields.every(k=>x.candidate[k]===candidate[k]));
 const failed=[],missing=[];
 for(const id of g.required_test_refs){
  const rs=current.filter(x=>x.test_ref===id);
  if(rs.some(x=>x.verdict==="fail"))failed.push(id);
  else if(!rs.some(x=>x.verdict==="pass"&&(!g.actual_model_test_refs.includes(id)||x.actual_model===true)))missing.push(id);
 }
 return {verdict:failed.length?"fail":missing.length?"incomplete":"pass",failed,missing};
}

export function validateV08(D,evaluate){
 const {core:c,api:a,implementation:d,physical:p,contract:o,wbs:w,index:i}=D,checks=[];
 const check=(id,pass)=>checks.push({id,pass:!!pass});
 const uniq=x=>new Set(x).size===x.length;
 const initial=c.transitions.find(x=>x.id==="V3-J03"),resume=c.transitions.find(x=>x.id==="V3-J20");
 check("RESUME-01 initial and recovery distinct",initial?.from.join()==="planned"&&initial.to==="ready"&&resume?.event==="explicit_resume_requested"&&resume.to==="ready"&&resume.from.slice().sort().join()==="blocked,needs_action");
 check("RESUME-02 no unguarded interrupted-to-ready edge",c.transitions.filter(t=>t.to==="ready"&&t.from.some(x=>c.recovery_contract.interruption_states.includes(x))).every(t=>t.id==="V3-J20"&&["explicit_resume_current","safe_next_step_proven",...c.guards.map(g=>g.condition)].every(g=>t.conditions.includes(g)))&&c.recovery_contract.resume_request_route==="HTTP-13"&&o.schemas.find(x=>x.id==="Resume5Request")?.fields.some(x=>x.name==="explicit_resume"&&x.required&&x.type==="boolean"));
 const adj=new Map(d.components.map(x=>[x.id,x.depends_on]));const reach=(s,e)=>{let q=[s],seen=new Set();while(q.length){let k=q.pop();if(k===e)return true;if(!seen.has(k)){seen.add(k);q.push(...(adj.get(k)??[]));}}return false;};
 const calls=[...i.route_groups.map(x=>({...x,consumers:[x.consumer]})),...i.port_groups];
 check("ARCH-02 mapped calls reachable and no gateway callback",calls.every(x=>x.consumers.every(k=>k===x.provider||reach(k,x.provider)))&&!reach("C4-07","C4-05")&&reach("C4-07","C4-10")&&d.dependency_contract.no_gateway_callback===true);
 const u=p.api.find(x=>x.id==="HTTP-02"),v=p.api.find(x=>x.id==="HTTP-17"),meta=a.schemas.find(x=>x.id==="AssetUploadMetadata"),read=a.schemas.find(x=>x.id==="ReadRequest");
 check("WIRE-04 multipart typed metadata and server ownership",u.input===meta.id&&u.request_wire.content_type==="multipart/form-data"&&u.request_wire.parts.length===2&&u.request_wire.parts.some(x=>x.name==="file"&&x.kind==="binary"&&x.required)&&u.request_wire.parts.some(x=>x.name==="metadata"&&x.schema===meta.id&&x.required)&&u.request_wire.reject_unknown_parts===true&&["rights_confirmed","permitted_use","key"].every(k=>meta.fields.some(f=>f.name===k&&f.required))&&["owner","owner_ref","upload_ref","digest"].every(k=>!meta.fields.some(f=>f.name===k)));
 check("WIRE-05 read query and no body",v.input===read.id&&v.request_wire.path.id==="ref"&&v.request_wire.query.after_revision.type==="positive_int"&&!v.request_wire.query.after_revision.required&&v.request_wire.body==="none"&&v.request_wire.order==="revision ascending");
 const g=w.mvp_gate,allTests=new Set(i.tests.map(x=>x.id)),mandatory=[...new Set(g.groups.flatMap(x=>x.test_refs))];
 check("GATE-01 complete declared scope and trace",g.id==="MVP-GATE-01"&&g.work_ref==="W09"&&g.milestone_ref==="M04"&&g.environment==="mock"&&g.execution_status==="not_run"&&uniq(g.required_test_refs)&&g.required_test_refs.slice().sort().join()===mandatory.sort().join()&&g.required_test_refs.every(x=>allTests.has(x)&&i.tests.find(t=>t.id===x).work_refs.includes("W09"))&&["AT-01","AT-02","AT-03","AT-04","AT-05","AT-06","T5-08","T5-04","T5-12","T5-07","T5-09"].every(x=>g.required_test_refs.includes(x))&&g.actual_model_test_refs.includes("T5-08")&&d.requirements.every(r=>g.groups.some(x=>x.requirement_refs.includes(r.id))));
 const fixture=o.test_fixtures.ai_extraction.cases;
 check("FIXTURE-01 known facts and uncertainty preserved",fixture.find(x=>x.id==="AI-01").expected.tiers.map(x=>[x.minutes_per_session,x.sessions_per_period,x.total_price_krw].join(":")).join()==="90:4:250000,180:4:400000,270:4:500000"&&fixture.find(x=>x.id==="AI-01").expected.vat_included===null&&fixture.find(x=>x.id==="AI-02").expected.auto_confirm===false&&fixture.find(x=>x.id==="AI-03").expected.manual_fallback_is_ai_pass===false);
 const spec=o.action_spec_contract;
 check("ACTION-01 deny unresolved or unbound arguments",spec.unverified_policy==="deny"&&spec.reject_unknown_args===true&&spec.require_exact_binding===true&&["before_spec","after_spec","evidence_spec","allowed_origin_ref"].every(x=>spec.require_resolved_refs.includes(x))&&o.schemas.some(x=>x.id===spec.schema));
 const candidate={build_sha:"synthetic-build",contract_digest:"synthetic-contract",fixture_digest:"synthetic-fixture",environment:"mock"};
 const pass=g.required_test_refs.map(id=>({test_ref:id,run_ref:"synthetic-"+id,verdict:"pass",execution_kind:g.execution_kind,candidate:{...candidate},actual_model:true}));
 const cases=[];const run=(id,rs,expected)=>{let actual=evaluate(g,candidate,rs).verdict;cases.push({id,expected,actual,pass:actual===expected});};
 run("complete synthetic evidence",pass,"pass");run("missing test",pass.slice(1),"incomplete");run("explicit fail",pass.map((x,n)=>n===0?{...x,verdict:"fail"}:x),"fail");run("stale build",pass.map(x=>({...x,candidate:{...candidate,build_sha:"old"}})),"incomplete");run("stale contract",pass.map(x=>({...x,candidate:{...candidate,contract_digest:"old"}})),"incomplete");run("stale fixture",pass.map(x=>({...x,candidate:{...candidate,fixture_digest:"old"}})),"incomplete");run("wrong environment",pass.map(x=>({...x,candidate:{...candidate,environment:"live"}})),"incomplete");run("static checks are not product evidence",pass.map(x=>({...x,execution_kind:"design_static"})),"incomplete");run("manual AI fallback",pass.map(x=>x.test_ref==="T5-08"?{...x,actual_model:false}:x),"incomplete");run("contradictory fail dominates",pass.concat({...pass[0],verdict:"fail",run_ref:"other"}),"fail");run("missing run reference",pass.map(x=>({...x,run_ref:""})),"incomplete");run("unknown",pass.map((x,n)=>n===0?{...x,verdict:"unknown"}:x),"incomplete");
 return {checks,passed:checks.filter(x=>x.pass).length,total:checks.length,gate_cases:cases,gate_passed:cases.filter(x=>x.pass).length,gate_total:cases.length,actual_mvp_verdict:evaluate(g,candidate,[]).verdict,product_execution:"not_run"};
}

export function regression(D,validate,evaluate){
 const cases=[];const test=(name,id,mutate)=>{const x=JSON.parse(JSON.stringify(D));mutate(x);const r=validate(x,evaluate);cases.push({name,target:id,pass:r.checks.some(t=>t.id.startsWith(id)&&!t.pass)});};
 test("implicit resume restored","RESUME-01",x=>x.core.transitions.find(t=>t.id==="V3-J03").from.push("blocked"));
 test("explicit guard removed","RESUME-02",x=>{const t=x.core.transitions.find(t=>t.id==="V3-J20");t.conditions=t.conditions.filter(k=>k!=="explicit_resume_current");});
 test("gateway callback restored","ARCH-02",x=>x.implementation.components.find(t=>t.id==="C4-07").depends_on.push("C4-05"));
 test("client supplied upload digest","WIRE-04",x=>x.api.schemas.find(t=>t.id==="AssetUploadMetadata").fields.push({name:"digest",type:"digest",required:true}));
 test("GET body enabled","WIRE-05",x=>x.physical.api.find(t=>t.id==="HTTP-17").request_wire.body="json");
 test("AI required test removed","GATE-01",x=>{x.wbs.mvp_gate.required_test_refs=x.wbs.mvp_gate.required_test_refs.filter(t=>t!=="T5-08");x.wbs.mvp_gate.groups.forEach(g=>g.test_refs=g.test_refs.filter(t=>t!=="T5-08"));});
 test("fixture price corrupted","FIXTURE-01",x=>x.contract.test_fixtures.ai_extraction.cases[0].expected.tiers[1].total_price_krw=300000);
 test("unresolved action allowed","ACTION-01",x=>x.contract.action_spec_contract.unverified_policy="allow");
 return {cases,passed:cases.filter(x=>x.pass).length,total:cases.length};
}
