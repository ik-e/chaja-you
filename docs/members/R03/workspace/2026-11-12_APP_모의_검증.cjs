// Local contract prototype: structured fixtures, mock tools, no LLM or web access.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../../..');
const specPath = path.join(root, 'docs/artifacts/specs/focus_apps.json');
const specBytes = fs.readFileSync(specPath);
const spec = JSON.parse(specBytes.toString('utf8').replace(/^\uFEFF/, ''));
const requests = Object.fromEntries(spec.requests.map(r => [r.id, r.text]));
const PASS = '충족', FAIL = '미충족', UNKNOWN = '미확인';
const domain = {
  id: 'R03-APP-MOCK-v1',
  roles: ['discovery', 'research', 'verification', 'comparison', 'synthesis'],
  sourceProfiles: {timer: ['mock-developer-help'], blocker: ['mock-pricing', 'mock-browser-help']},
};
// Manually annotated requests: this prototype does NOT validate natural-language extraction.
const a = {profile:'timer', platform:'Android', candidates:['PomoToki','Focus To-Do'],
  required:['offline_pomodoro'], preferred:['accountless'], followup:'never'};
const b = {profile:'blocker', platform:'Android', candidates:[],
  required:['two_sites','weekday_schedule','evening_schedule','free_scheduled_blocking'],
  preferred:[], followup:'never', contextChecks:['browser','permissions']};
const c = {...a, preferred:[], followup:'all_fail'};
const fixtures = [
  {id:'APP-A', request:requests['APP-A'], input:a, outcomes:[PASS,UNKNOWN], expectDiscovery:0},
  {id:'APP-B', request:requests['APP-B'], input:b, outcomes:[], expectDiscovery:1},
  {id:'APP-C1', request:requests['APP-C'], input:c, outcomes:[FAIL,FAIL], expectDiscovery:1},
  {id:'APP-C2', request:requests['APP-C'], input:c, outcomes:[PASS,FAIL], expectDiscovery:0},
  {id:'APP-C3', request:requests['APP-C'], input:c, outcomes:[FAIL,UNKNOWN], expectDiscovery:0},
  {id:'V1', request:'Android에서 오프라인 뽀모도로 타이머를 쓸 앱을 찾아줘. 가능하면 계정 없이 쓰고 싶어.',
    input:{...a,candidates:[]},outcomes:[],expectDiscovery:1},
  {id:'V2', request:'Android에서 후보 X와 후보 Y의 무료 평일 저녁 사이트 2개 차단 기능을 비교해줘. 다른 앱은 찾지 마.',
    input:{...b,candidates:['후보 X','후보 Y']},outcomes:[UNKNOWN,UNKNOWN],expectDiscovery:0},
  {id:'V3', request:'PomoToki와 Focus To-Do의 Android 오프라인 타이머를 비교해줘. 둘 다 충족하지 않거나 충족 여부를 확인할 수 없으면 대안도 찾아줘.',
    input:{...c,followup:'no_pass'},outcomes:[FAIL,UNKNOWN],expectDiscovery:1},
  {id:'V4', request:'PomoToki와 Focus To-Do 중 Android 오프라인 뽀모도로 타이머를 반드시 계정 없이 쓸 수 있는 앱을 비교해줘.',
    input:{...a,required:['offline_pomodoro','accountless'],preferred:[]},
    outcomes:[UNKNOWN,UNKNOWN],expectDiscovery:0},
];
// Complete APP-C truth table, including order symmetry and unknown/unknown.
for (const left of [PASS,FAIL,UNKNOWN]) for (const right of [PASS,FAIL,UNKNOWN]) {
  fixtures.push({id:`C-MATRIX-${left}-${right}`,request:requests['APP-C'],input:c,
    outcomes:[left,right],expectDiscovery:left===FAIL && right===FAIL ? 1 : 0});
}
function execute(f) {
  const tasks=[], events=[], decisions=[];
  let version=0;
  const add=(type,target,deps=[],extra={})=>{
    const t={id:`T${tasks.length+1}`,type,role:type==='verify'?'verification':type==='discover'?'discovery':type,
      target,depends_on:deps,domain_id:domain.id,status:'pending',...extra};
    tasks.push(t); events.push({seq:events.length+1,event:'task_added',task_id:t.id,plan_version:++version});
    return t;
  };
  const run=t=>{
    if(t.depends_on.some(id=>tasks.find(x=>x.id===id)?.status!=='complete')) throw Error('dependency violation');
    t.status='complete'; events.push({seq:events.length+1,event:'mock_complete',task_id:t.id});
  };
  const discover=deps=>{const t=add('discover','mock-candidate',deps,{reason:'request requires discovery'});run(t);return t;};
  const investigate=(names,deps,outcomes)=>names.map((name,i)=>{
    const r=add('research',name,deps,{source_profiles:domain.sourceProfiles[f.input.profile]});
    const v=add('verify',name,[r.id],{conditions:[...f.input.required],preferences:[...f.input.preferred],
      context_checks:f.input.contextChecks||[],mock_verdict:outcomes[i]||UNKNOWN});
    return {r,v};
  });
  let discovery=null;
  if(!f.input.candidates.length) discovery=discover([]);
  const initial = investigate(f.input.candidates.length?f.input.candidates:['MockCandidate'],
    discovery?[discovery.id]:[],f.outcomes);
  // All input-independent researches are ready together. Execution remains serial simulation.
  const readyGroups=[initial.map(x=>x.r.id)];
  initial.forEach(x=>run(x.r)); initial.forEach(x=>run(x.v));
  const initialChecks=initial.map(x=>x.v.id);
  let finalChecks=[...initialChecks];
  if(f.input.candidates.length && f.input.followup!=='never') {
    const verdicts=initial.map(x=>x.v.mock_verdict);
    const trigger=f.input.followup==='all_fail'?verdicts.every(x=>x===FAIL):!verdicts.includes(PASS);
    decisions.push({condition:f.input.followup,verdicts,action:trigger?'add_discovery':'skip_discovery',
      reason:trigger?'request condition satisfied':verdicts.includes(PASS)?'qualifying candidate exists':'condition not established (unknown)'});
    if(trigger) {
      const d=discover(initialChecks);
      const follow=investigate(['MockAlternative'],[d.id],[UNKNOWN]);
      follow.forEach(x=>{run(x.r);run(x.v);});finalChecks.push(...follow.map(x=>x.v.id));
    }
  } else if(f.input.candidates.length) decisions.push({action:'skip_discovery',reason:'specified comparison; no discovery requested'});
  const comparison=add('comparison','all requested candidates',finalChecks);run(comparison);
  const synthesis=add('synthesis','mock report',[comparison.id]);run(synthesis);
  return {id:f.id,request:f.request,structured_input:f.input,mock_outcomes:f.outcomes,
    tasks,events,decisions,parallel_eligible_groups:readyGroups,
    execution_mode:'serial simulation; groups show eligibility only',
    app_fact_claims:[],source_evidence:'synthetic source profile labels only; not actual evidence'};
}
// Independent expected constraints; inspect plans AND event order, not output labels alone.
function evaluate(f,r) {
  const checks=[]; const check=(name,ok)=>checks.push({criterion:name,verdict:ok?'pass':'fail'});
  const completed=id=>r.events.findIndex(e=>e.event==='mock_complete'&&e.task_id===id);
  const discover=r.tasks.filter(t=>t.type==='discover');
  check('expected discovery count',discover.length===f.expectDiscovery);
  check('required and preferred preserved',r.tasks.filter(t=>t.type==='verify').every(t=>
    JSON.stringify(t.conditions)===JSON.stringify(f.input.required)&&JSON.stringify(t.preferences)===JSON.stringify(f.input.preferred)));
  check('dependency IDs and completion order',r.tasks.every(t=>t.depends_on.every(id=>
    r.tasks.some(x=>x.id===id)&&completed(id)>=0&&completed(id)<completed(t.id))));
  const initial=r.tasks.filter(t=>t.type==='verify'&&f.input.candidates.includes(t.target));
  if(f.input.followup!=='never' && f.input.candidates.length) {
    check('conditional discovery added after all initial verdicts',discover.every(t=>
      initial.every(v=>r.events.findIndex(e=>e.event==='task_added'&&e.task_id===t.id)>completed(v.id))));
    check('conditional decision recorded',r.decisions.some(d=>d.condition===f.input.followup&&d.reason));
  }
  const names=f.input.candidates.length?f.input.candidates:['MockCandidate'];
  check('all initial candidates covered',names.every(n=>r.tasks.some(t=>t.type==='research'&&t.target===n)&&r.tasks.some(t=>t.type==='verify'&&t.target===n)));
  const comparison=r.tasks.find(t=>t.type==='comparison');
  check('all candidate verdicts feed comparison',r.tasks.filter(t=>t.type==='verify').every(t=>comparison.depends_on.includes(t.id)));
  check('domain source/validation profiles selected',r.tasks.filter(t=>t.type==='research').every(t=>
    JSON.stringify(t.source_profiles)===JSON.stringify(domain.sourceProfiles[f.input.profile])));
  if(f.input.contextChecks) check('browser and permissions retained',r.tasks.filter(t=>t.type==='verify').every(t=>
    f.input.contextChecks.every(x=>t.context_checks.includes(x))));
  check('task roles belong to app candidate set',r.tasks.every(t=>domain.roles.includes(t.role)));
  return checks;
}
const runs=fixtures.map(execute);
const evaluations=runs.map((r,i)=>({case_id:r.id,checks:evaluate(fixtures[i],r)}));
// Negative controls: deliberately corrupt output so checker sensitivity is observable.
const negatives=[];
function negative(id,idx,mutate) {const bad=JSON.parse(JSON.stringify(runs[idx]));mutate(bad);
  const failures=evaluate(fixtures[idx],bad).filter(c=>c.verdict==='fail');
  negatives.push({id,detected:failures.length>0,failures});}
negative('remove required condition',0,r=>r.tasks.find(t=>t.type==='verify').conditions=[]);
negative('missing candidate comparison dependency',0,r=>r.tasks.find(t=>t.type==='comparison').depends_on=[]);
negative('unknown treated as all-fail',4,r=>r.tasks.push({id:'ILLEGAL',type:'discover',role:'discovery',depends_on:[]}));
negative('early conditional task insertion',2,r=>{const t=r.tasks.find(t=>t.type==='discover');
  const e=r.events.find(e=>e.event==='task_added'&&e.task_id===t.id);r.events=r.events.filter(x=>x!==e);r.events.unshift(e);});
const report={id:'R03-APP-MOCK-2026-11-12',generated_at:new Date().toISOString(),
  scope:'structured-input, deterministic contract prototype only',
  spec_path:'docs/artifacts/specs/focus_apps.json',spec_sha256:crypto.createHash('sha256').update(specBytes).digest('hex'),
  domain,summary:{cases:runs.length,passed:evaluations.filter(e=>e.checks.every(c=>c.verdict==='pass')).length,
    failed:evaluations.filter(e=>e.checks.some(c=>c.verdict==='fail')).length,
    negative_controls:negatives.length,detected:negatives.filter(n=>n.detected).length},
  limitations:['Natural-language understanding untested: structured requests manually supplied.',
    'Rule-based prototype is not an LLM dynamic planner or the production application.',
    'No real app facts, citations, web calls, parallel execution, device tests or performance comparison.',
    'B0/D0 baseline comparison not executed; no superiority or TASK completion claim.'],
  runs,evaluations,negative_controls:negatives};
fs.writeFileSync(path.join(__dirname,'2026-11-12_APP_모의_검증_결과.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.summary));
if(report.summary.failed||report.summary.detected!==negatives.length)process.exitCode=1;
