import * as E from '../../../../tools/verify_design_stage.mjs';
function lessonCheckers(E){
 return {
  resume:d=>E.guardedTransitions({transitions:d.core.transitions,from:["needs_action","blocked"],to:"ready",event:"explicit_resume_requested",required:["explicit_resume_current","safe_next_step_proven"]}),
  calls:d=>E.compositionGraph({nodes:d.implementation.components.map(x=>x.id),dependencies:d.implementation.components.flatMap(x=>x.depends_on.map(y=>[x.id,y])),calls:[...d.index.route_groups.map(x=>({id:x.id,consumer:x.consumer,provider:x.provider})),...d.index.port_groups.flatMap(x=>x.consumers.map(c=>({id:x.id,consumer:c,provider:x.provider})))]}),
  wire:d=>{const types=[...Object.keys(d.api.types),...Object.keys(d.contract.schema_types),...d.api.schemas.map(x=>x.id),...d.contract.schemas.map(x=>x.id),"JobState","EffectClass","EffectState","id","positive_int","nonnegative_int","timestamp","digest","string","boolean","json"];const routes=[...d.physical.api.filter(x=>!d.contract.routes.some(y=>y.id===x.id)),...d.contract.routes];return E.typedUses({types,uses:routes.flatMap(x=>[{id:x.id,field:"input",type:x.input},{id:x.id,field:"output",type:x.output}])});},
  mvp:d=>{const required=["AT-01","AT-02","AT-03","AT-04","AT-05","AT-06","T5-08","T5-04","T5-12","T5-07","T5-09"];return E.requiredCoverage({required,declared:d.wbs.mvp_gate?.required_test_refs??[],linked:d.index.tests.filter(x=>x.work_refs.includes("W09")).map(x=>x.id)});}
 };
}
export const checkers=lessonCheckers(E);
