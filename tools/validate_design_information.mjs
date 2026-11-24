// Model-driven information graph checks. No product-specific fixtures or network calls.
export function validateDesignInformation(model, graph, {authorityRefs=[], registryIds=[]}={}) {
  const checks=[], warnings=[];
  const group=(id,run)=>{const errors=[];const need=(condition,message)=>{if(!condition)errors.push(message);};try{run(need);}catch(e){errors.push(String(e));}checks.push({id,pass:errors.length===0,errors});};
  const isObj=v=>v!==null&&typeof v==="object"&&!Array.isArray(v);
  const nonempty=v=>v!==undefined&&v!==null&&v!==""&&(!Array.isArray(v)||v.length>0)&&(!isObj(v)||Object.keys(v).length>0);
  const unique=xs=>new Set(xs).size===xs.length;
  const fieldsOk=(v,t)=>v===null||(["string","enum","ref"].includes(t)?typeof v==="string":["string[]","ref[]"].includes(t)?Array.isArray(v)&&v.every(x=>typeof x==="string"):t==="object"&&isObj(v));
  const stages=new Map(model.decision_stages.map(x=>[x.id,x])), types=new Map(model.information_types.map(x=>[x.id,x])), relations=new Map(model.relationship_types.map(x=>[x.id,x])), allowed=new Set(model.type_edges.map(x=>`${x.from_type}|${x.to_type}|${x.relation}`));
  const rs=graph.records??[], es=graph.edges??[], by=new Map(rs.map(x=>[x.id,x])), current=rs.filter(x=>x.lifecycle==="current"), causal=new Set(["derived_from","constrains","satisfies"]);
  const validTypes=new Set(model.field_type_enum??["string","string[]","object","ref","ref[]","enum"]);
  function acyclic(nodes,links){const next=new Map(nodes.map(x=>[x,[]])), inDeg=new Map(nodes.map(x=>[x,0]));for(const [a,b] of links){if(!next.has(a)||!inDeg.has(b))return false;next.get(a).push(b);inDeg.set(b,inDeg.get(b)+1);}const q=nodes.filter(x=>inDeg.get(x)===0);for(let i=0;i<q.length;i++){for(const b of next.get(q[i])){inDeg.set(b,inDeg.get(b)-1);if(inDeg.get(b)===0)q.push(b);}}return q.length===nodes.length;}
  group("MODEL-01 stage and type definitions",need=>{
    need(stages.size===model.decision_stages.length&&types.size===model.information_types.length&&relations.size===model.relationship_types.length,"duplicate stage/type/relation");
    for(const s of stages.values()){need((s.blocking_on??[]).every(x=>stages.has(x)),`${s.id}: unknown prerequisite`);need((s.output_types??[]).every(x=>types.has(x)),`${s.id}: unknown output`);need(s.verification_design?.question&&s.verification_design?.test_plan_type_ref==="IT-20",`${s.id}: missing verification design`);}
    for(const t of types.values()){need(stages.has(t.first_defined_at)&&stages.get(t.first_defined_at)?.output_types?.includes(t.id),`${t.id}: first stage invalid`);need(unique(t.fields.map(f=>f.key)),`${t.id}: duplicate field`);for(const f of t.fields){need(validTypes.has(f.value_type)&&typeof f.required_for_baseline==="boolean",`${t.id}.${f.key}: invalid field definition`);}}
    need(acyclic([...stages.keys()],[...stages.values()].flatMap(s=>(s.blocking_on??[]).map(a=>[a,s.id]))),"stage prerequisite cycle");
    for(const l of model.progressive_design_layers??[]){need(l.stage_ids.every(x=>stages.has(x))&&l.verification_design?.design_record_type==="IT-20",`${l.id}: missing stage/verification`);}
  });
  group("MODEL-02 allowed relations and causal ordering",need=>{
    need(allowed.size===model.type_edges.length,"duplicate typed relation");
    for(const e of model.type_edges){need(types.has(e.from_type)&&types.has(e.to_type)&&relations.has(e.relation),`bad model edge ${e.id}`);if(causal.has(e.relation)&&e.contract_phase!=="baseline_reconcile"&&types.has(e.from_type)&&types.has(e.to_type)){const start=types.get(e.from_type).first_defined_at,end=types.get(e.to_type).first_defined_at;const seen=new Set(),todo=[end];while(todo.length){const x=todo.pop();if(seen.has(x))continue;seen.add(x);todo.push(...(stages.get(x)?.blocking_on??[]));}need(seen.has(start),`${e.id}: stage order mismatch`);}}
    need(acyclic([...types.keys()],model.type_edges.filter(e=>causal.has(e.relation)).map(e=>[e.from_type,e.to_type])),"causal type graph cycle");
  });
  group("INFO-01 record envelope, fields and status",need=>{
    need(by.size===rs.length,"duplicate record ID");
    const statuses=new Set(model.record_contract.status_values), evidence=new Set(model.record_contract.evidence_values), required=model.record_contract.envelope.required;
    for(const r of rs){
      need(required.every(k=>Object.hasOwn(r,k)),`${r.id}: incomplete envelope`);
      need(typeof r.id==="string"&&r.id.length>0&&types.has(r.type_id),`${r.id}: invalid id/type`);
      need(statuses.has(r.status)&&evidence.has(r.evidence_level),`${r.id}: invalid status/evidence`);
      need(["current","upstream","historical"].includes(r.lifecycle),`${r.id}: invalid lifecycle`);
      need(Array.isArray(r.source_refs)&&r.source_refs.length>0&&r.source_refs.every(x=>typeof x==="string"&&x.length>0),`${r.id}: missing source refs`);
      need(isObj(r.fields),`${r.id}: fields not object`);
      const t=types.get(r.type_id);if(!t||!isObj(r.fields))continue;
      const spec=new Map(t.fields.map(f=>[f.key,f]));
      for(const [k,v] of Object.entries(r.fields)){const f=spec.get(k);need(!!f,`${r.id}.${k}: unknown field`);if(f){need(fieldsOk(v,f.value_type),`${r.id}.${k}: wrong type ${f.value_type}`);need(v===null||!f.allowed_values||f.allowed_values.includes(v),`${r.id}.${k}: invalid enum`);}}
      const absent=t.fields.filter(f=>f.required_for_baseline&&!nonempty(r.fields[f.key])).map(f=>f.key);
      if(["provisional","adopted"].includes(r.status))need(!absent.length,`${r.id}: missing baseline fields ${absent.join(",")}`);
      else if(r.lifecycle==="current"&&absent.length&&r.status!=="not_applicable")warnings.push({kind:"candidate_baseline_fields",id:r.id,fields:absent,note:"제안 상태; 기준선 확정 전에 의미와 필요성 검토"});
    }
  });
  group("INFO-02 human authority and execution claims",need=>{
    const auth=new Set(authorityRefs);
    for(const r of rs){
      if(r.status==="adopted"){need(["IT-06","IT-19","IT-25"].includes(r.type_id)&&auth.has(r.fields.authority_ref),`${r.id}: adoption without allowed human direction`);need(r.lifecycle==="current",`${r.id}: historical adoption claim`);}
      if(r.type_id==="IT-20"){need(r.fields.run_ref==null&&r.execution_status==="not_run",`${r.id}: plan falsely asserts execution`);const m=r.fields.plan_maturity;if(m){need(/^L[0-6]$/.test(r.fields.design_level??""),`${r.id}: invalid design level`);}if(m==="detailed_test_case"){const b=r.fields.verdict_boundary??"";need(nonempty(r.fields.case_conditions)&&nonempty(r.fields.expected)&&["pass:","fail:","unknown:"].every(x=>b.includes(x))&&!b.includes("not_run"),`${r.id}: incomplete detailed verdict`);}}
    }
    need(!es.some(e=>e.relation==="verified_by"),"observed verification cannot be inferred from a design-only graph");
  });
  group("GRAPH-01 endpoints, relation and causal DAG",need=>{
    need(unique(es.map(e=>e.id))&&unique(es.map(e=>`${e.from}|${e.to}|${e.relation}`)),"duplicate graph edge");
    for(const e of es){const a=by.get(e.from),b=by.get(e.to);need(a&&b&&e.from!==e.to,`${e.id}: unknown or self endpoint`);need(relations.has(e.relation)&&relations.get(e.relation)?.edge_scope==="information",`${e.id}: invalid information relation`);if(a&&b&&e.relation!=="impacts"){need(allowed.has(`${a.type_id}|${b.type_id}|${e.relation}`),`${e.id}: forbidden typed edge`);}if(e.relation==="impacts")need(e.review_only===true,`${e.id}: impacts must be review-only`);}
    need(acyclic([...by.keys()],es.filter(e=>causal.has(e.relation)).map(e=>[e.from,e.to])),"causal instance graph cycle");
  });
  group("GRAPH-02 planned verification coverage",need=>{
    const testLinks=es.filter(e=>e.relation==="planned_check_by");
    for(const e of testLinks){const t=by.get(e.to);need(t?.type_id==="IT-20",`${e.id}: check target not IT-20`);if(e.scope!=="legacy")need(t?.fields.subject_refs?.includes(e.from),`${e.id}: subject mismatch`);}
    for(const r of rs.filter(x=>["IT-09","IT-10"].includes(x.type_id)&&x.status!=="not_applicable"))need(testLinks.some(e=>e.from===r.id),`${r.id}: requirement without planned check`);
    for(const r of current.filter(x=>["IT-13","IT-16","IT-17","IT-18","IT-14","IT-15","IT-26","IT-27"].includes(x.type_id)))need(testLinks.some(e=>e.from===r.id),`${r.id}: current design without planned check`);
    for(const t of current.filter(x=>x.type_id==="IT-20")){need(t.fields.subject_refs.every(x=>by.has(x)),`${t.id}: missing subject`);need(t.fields.subject_refs.every(x=>testLinks.some(e=>e.from===x&&e.to===t.id)),`${t.id}: subject has no planned_check_by edge`);}
  });
  group("GRAPH-03 runtime ownership and component responsibility",need=>{
    for(const r of current.filter(x=>x.type_id==="IT-13")){
      const f=r.fields, parent=by.get(f.parent_runtime_unit_ref);
      need(parent?.type_id==="IT-27"&&parent.lifecycle==="current",`${r.id}: missing current runtime unit`);
      need(parent?.fields.component_refs?.includes(r.id)&&es.some(e=>e.from===parent.id&&e.to===r.id&&e.relation==="constrains"),`${r.id}: runtime membership inconsistent`);
      need((f.dependencies??[]).every(id=>by.get(id)?.type_id==="IT-13"),`${r.id}: invalid dependency`);
      const contrib=Object.entries(f.requirement_contributions??{});need(contrib.length>0,`${r.id}: no requirement responsibility`);
      for(const [id,meaning] of contrib){need(["IT-09","IT-10"].includes(by.get(id)?.type_id)&&typeof meaning==="string"&&meaning.length>0,`${r.id}: invalid contribution ${id}`);need(es.some(e=>e.from===id&&e.to===r.id&&e.relation==="satisfies"),`${r.id}: missing satisfies relation for ${id}`);}
      need((f.verification_refs??[]).length>0&&f.verification_refs.every(id=>by.get(id)?.type_id==="IT-20"&&es.some(e=>e.from===r.id&&e.to===id&&e.relation==="planned_check_by")),`${r.id}: verification refs invalid`);
    }
  });
  group("GRAPH-04 projection and review links",need=>{
    const dlv=new Set(registryIds);const pe=graph.projection_edges??[];
    need(unique(pe.map(e=>`${e.from}|${e.to}`)),"duplicate projection mapping");
    for(const e of pe){need(by.has(e.from)&&dlv.has(e.to)&&e.status==="mapping_only"&&e.relation==="projection_candidate",`${e.from}: invalid projection or submission claim`);}
    for(const r of current.filter(x=>x.type_id==="IT-22")){need(dlv.has(r.fields.deliverable_id)&&r.fields.submission_status==="not_asserted",`${r.id}: invalid deliverable status`);need(r.fields.source_refs.every(id=>by.has(id)&&pe.some(e=>e.from===id&&e.to===r.fields.deliverable_id)),`${r.id}: unmapped source`);}
    const reviewLinks=graph.review_links??[];
    need(unique(reviewLinks.map(e=>`${e.from}|${e.to}|${e.kind}`)),"duplicate review link");
    for(const e of reviewLinks)need(by.has(e.from)&&by.has(e.to)&&e.from!==e.to&&e.review_only===true,`invalid review link ${e.from} -> ${e.to}`);
  });
  return {checks,warnings,passed:checks.filter(x=>x.pass).length,total:checks.length,record_count:rs.length,current_count:current.length,edge_count:es.length,projection_count:(graph.projection_edges??[]).length,review_link_count:(graph.review_links??[]).length,types_present:[...new Set(current.map(r=>r.type_id))].sort(),product_execution:"not_run"};
}

export function designImpact(model, graph, changedIds, maxDepth=3) {
  if(!Number.isInteger(maxDepth)||maxDepth<1||maxDepth>8)throw Error("impact depth must be 1..8");
  const by=new Map(graph.records.map(r=>[r.id,r])),prop=new Set(model.relationship_types.filter(r=>r.propagate_review&&r.id!=="verified_by").map(r=>r.id)), next=new Map();
  const push=(from,to,kind)=>{if(!next.has(from))next.set(from,[]);next.get(from).push({to,kind});};
  for(const e of graph.edges)if(prop.has(e.relation))push(e.from,e.to,e.relation);
  for(const e of graph.review_links??[])push(e.from,e.to,e.kind);
  for(const e of graph.projection_edges??[])push(e.from,`PROJ-${e.to}`,"projection_candidate");
  const seen=new Map(), q=[];for(const id of changedIds){if(!by.has(id))throw Error(`unknown record ${id}`);if(!seen.has(id)){seen.set(id,{id,depth:0,path:[id],via:[]});q.push(id);}}
  for(let i=0;i<q.length;i++){const at=q[i],prev=seen.get(at);if(prev.depth===maxDepth)continue;for(const link of next.get(at)??[]){if(seen.has(link.to))continue;seen.set(link.to,{id:link.to,depth:prev.depth+1,path:[...prev.path,link.to],via:[...prev.via,link.kind]});q.push(link.to);}}
  const candidates=[...seen.values()].filter(x=>x.depth>0).map(x=>({...x,type_id:by.get(x.id)?.type_id??"projection",lifecycle:by.get(x.id)?.lifecycle??"mapping_only"}));
  return {changed:[...new Set(changedIds)],max_depth:maxDepth,candidates,review_only:true,automatic_invalidation:false,automatic_assignment:false};
}
