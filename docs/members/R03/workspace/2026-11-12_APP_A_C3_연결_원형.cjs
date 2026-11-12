'use strict';

// R03 review prototype only. No model, web, device, server, or real app facts.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../../..');
const outputPath = path.join(__dirname, '2026-11-12_APP_A_C3_연결_결과.json');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const specPath = 'docs/artifacts/specs/focus_apps.json';
const contractPath = 'docs/artifacts/tasks/TASK-006.json';
const requests = JSON.parse(fs.readFileSync(path.join(root, specPath))).requests;
const terminal = status => ['완료', '실패', '생략'].includes(status);
const clone = value => JSON.parse(JSON.stringify(value));

// Manually structured, condition-specific fixtures; not conversions of old verdicts.
const fixtures = [
  {case_id:'APP-A', request_case:'APP-A', conditions:[
    {condition_id:'offline_pomodoro', priority:'필수', label:'Android 오프라인 뽀모도로 타이머'},
    {condition_id:'accountless', priority:'선호', label:'계정 없는 사용'}],
    outcomes:[['충족','미확인'],['미확인','충족']], failed_source:null},
  {case_id:'APP-C3', request_case:'APP-C', conditions:[
    {condition_id:'offline_timer', priority:'필수', label:'Android 오프라인 타이머'}],
    outcomes:[['미충족'],['미확인']], failed_source:1,
    confirmation_limit:{kind:'simulation_tick', value:2, scope:'fixture-only; not product policy'}}
];

function execute(fixture) {
  const requestId = `MOCK-REQ-R03-${fixture.case_id}-001`;
  const id = suffix => `${requestId}-${suffix}`;
  const targets = ['PomoToki','Focus To-Do'].map((label,i) => ({candidate_id:id(`C${i+1}`), label}));
  const run = {
    schema_version:1, id:id('RUN1'), kind:'run', status:'모의 실행 완료',
    case_id:fixture.case_id, simulation:true, execution_mode:'serial deterministic simulation',
    input:{request_id:requestId, domain:'app_research', user_text:requests.find(r=>r.id===fixture.request_case).text,
      targets, criteria:clone(fixture.conditions), domain_context:{platform:'Android'},
      discovery_rule:fixture.case_id==='APP-A'?'지정 후보만 비교':'두 후보 필수 조건 모두 미충족 확인 후 발굴',
      structuring_method:'manually supplied; natural-language understanding not tested'},
    domain_definition:{id:'R03-APP-IO-REVIEW-v1', roles:['research','verification','discovery','comparison','synthesis'],
      condition_ids_status:'R03 example names; no R05 field-name agreement'},
    confirmation_limit:fixture.confirmation_limit || null,
    plan:[], tasks:[], steps:[], sources:[], evidence:[], verdicts:[], claims:[], decisions:[], snapshots:[]
  };
  let tick = 0;
  const step = (event, data={}) => run.steps.push({seq:run.steps.length+1, simulation_tick:tick, event, ...data});
  const add = (suffix, role, goal, dependsOn=[], runIf={op:'always'}) => {
    const task = {request_id:requestId, task_id:id(suffix), goal, role, depends_on:dependsOn,
      run_if:runIf, status:'대기', status_reason:null, failure_reason:null};
    run.tasks.push(task); return task;
  };
  const evaluateCondition = condition => {
    if(condition.op==='always') return true;
    if(condition.op==='all_tasks_terminal') return condition.task_ids.every(ref=>terminal(run.tasks.find(t=>t.task_id===ref)?.status));
    if(condition.op==='all_verdicts_are') {
      const values=condition.verdict_ids.map(ref=>run.verdicts.find(v=>v.verdict_id===ref)?.status);
      if(values.some(v=>v==='충족')) return false;
      if(values.some(v=>!v || v==='미확인')) return null;
      return values.every(v=>v===condition.status);
    }
    throw Error(`Unsupported fixture condition: ${condition.op}`);
  };
  const start = task => {
    if(task.status!=='대기' || task.depends_on.some(ref=>{
      const status=run.tasks.find(t=>t.task_id===ref)?.status;
      return task.run_if.op==='all_tasks_terminal'&&task.run_if.task_ids.includes(ref)
        ? !terminal(status) : status!=='완료';
    }) ||
       evaluateCondition(task.run_if)!==true) throw Error(`Task not ready: ${task.task_id}`);
    task.status='진행 중'; step('task_started',{task_id:task.task_id});
  };
  const finish = (task, status='완료', reason=null) => {
    task.status=status; task.status_reason=reason;
    if(status==='실패') task.failure_reason=reason;
    step('task_finished',{task_id:task.task_id,status,reason});
  };
  const research = targets.map((target,i)=>add(`R${i+1}`,'research',`${target.label} 자료 확인`));
  // Failed research is not re-labelled complete. Verdict task runs on its recorded outcome.
  const verify = targets.map((target,i)=>add(`V${i+1}`,'verification',`${target.label} 조건별 판정`,[research[i].task_id],
    {op:'all_tasks_terminal',task_ids:[research[i].task_id]}));
  targets.forEach((target,i)=>{
    research[i].candidate_id=target.candidate_id;
    verify[i].candidate_id=target.candidate_id;
    verify[i].condition_ids=fixture.conditions.map(c=>c.condition_id);
  });
  const primaryIds = targets.map((target,i)=>id(`J${i+1}-1`));
  const discovery = fixture.case_id==='APP-C3'
    ? add('D1','discovery','조건 충족 시 대안 앱 발굴',verify.map(t=>t.task_id),
      {op:'all_verdicts_are',verdict_ids:primaryIds,status:'미충족'}) : null;
  const compare = add('COMPARE','comparison','지정 후보의 조건별 결과 비교',verify.map(t=>t.task_id));
  const report = add('REPORT','synthesis','확인 내용과 미확인·실패를 보존한 보고서',[compare.task_id],
    discovery?{op:'all_tasks_terminal',task_ids:[discovery.task_id]}:{op:'always'});
  run.plan=clone(run.tasks);
  const snapshot = phase => run.snapshots.push({phase,simulation_tick:tick,tasks:clone(run.tasks),
    verdicts:clone(run.verdicts),decisions:clone(run.decisions),report:run.report?clone(run.report):null});
  snapshot('planned');
  tick=1;
  targets.forEach((target,i)=>{
    const task=research[i]; start(task);
    const failed=fixture.failed_source===i;
    const source={request_id:requestId,source_id:id(`S${i+1}`),task_id:task.task_id,
      candidate_id:target.candidate_id,url:`mock://r03-io/${fixture.case_id}/source-${i+1}`,
      retrieved_at:null,simulation_tick:tick,access_status:failed?'접근 실패':'원문 확인',
      error_reason:failed?'합성 자료 접근 실패':null,data_kind:'synthetic fixture; no URL fetched'};
    run.sources.push(source); step('synthetic_source_outcome',{task_id:task.task_id,source_id:source.source_id});
    finish(task,failed?'실패':'완료',source.error_reason);
    const vtask=verify[i]; start(vtask);
    fixture.conditions.forEach((condition,j)=>{
      const status=fixture.outcomes[i][j]; const evidenceIds=[];
      if(status!=='미확인') {
        if(failed) throw Error('Fixture cannot support a verdict from failed access');
        const evidenceId=id(`E${i+1}-${j+1}`);
        run.evidence.push({request_id:requestId,evidence_id:evidenceId,source_id:source.source_id,
          candidate_id:target.candidate_id,condition_id:condition.condition_id,
          finding:`합성 자료: 대상 ${i+1}의 ${condition.label} 조건 ${status}`,
          locator:`fixture.outcomes[${i}][${j}]`,simulation:true});
        evidenceIds.push(evidenceId);
      }
      const verdict={request_id:requestId,verdict_id:id(`J${i+1}-${j+1}`),task_id:vtask.task_id,
        candidate_id:target.candidate_id,condition_id:condition.condition_id,status,evidence_ids:evidenceIds,
        reason:status==='미확인'?(failed?'자료 접근 실패로 판단 근거 없음':'합성 자료에 해당 조건 근거 없음'):'합성 자료의 조건별 직접 근거',
        simulation:true};
      run.verdicts.push(verdict); step('verdict_recorded',{task_id:vtask.task_id,verdict_id:verdict.verdict_id});
    });
    finish(vtask);
  });
  if(discovery) {
    if(evaluateCondition(discovery.run_if)!==null) throw Error('C3 fixture must initially be unresolved');
    discovery.status='보류'; discovery.status_reason='condition_unknown';
    const decision={request_id:requestId,decision_id:id('DEC1'),task_id:discovery.task_id,
      verdict_ids:primaryIds,action:'보류',condition_result:'미확인',reason:'condition_unknown'};
    run.decisions.push(decision); step('discovery_deferred',clone(decision)); snapshot('awaiting_confirmation');
    // Injected boundary event only: not elapsed seconds, web calls, or automatic retries.
    tick=fixture.confirmation_limit.value;
    step('confirmation_limit_reached',{limit:clone(fixture.confirmation_limit)});
    if(evaluateCondition(discovery.run_if)!==null) throw Error('C3 fixture unexpectedly changed');
    discovery.status='생략'; discovery.status_reason='limit_reached_condition_unknown';
    const finalDecision={...decision,decision_id:id('DEC2'),action:'최종 미실행',
      reason:discovery.status_reason,limit:clone(fixture.confirmation_limit)};
    run.decisions.push(finalDecision); step('discovery_not_executed',clone(finalDecision)); snapshot('limit_closed');
  }
  start(compare); finish(compare); start(report);
  run.claims=run.verdicts.filter(v=>v.status!=='미확인').map((v,i)=>({request_id:requestId,
    claim_id:id(`CLAIM${i+1}`),verdict_id:v.verdict_id,
    text:`합성 판정 ${v.verdict_id}: ${v.status} (실제 앱 기능 주장 아님)`,
    status:'합성 근거 연결',evidence_ids:[...v.evidence_ids],simulation:true}));
  const unknown=run.verdicts.filter(v=>v.status==='미확인');
  const failures=run.tasks.filter(t=>t.status==='실패').map(t=>({task_id:t.task_id,reason:t.failure_reason}));
  run.report={request_id:requestId,report_id:id('REPORT1'),task_id:report.task_id,
    status:unknown.length||failures.length?'부분 결과':'완료',
    claim_ids:run.claims.map(c=>c.claim_id),verdict_ids:run.verdicts.map(v=>v.verdict_id),
    source_ids:run.sources.map(s=>s.source_id),
    unverified:unknown.map(v=>({verdict_id:v.verdict_id,candidate_id:v.candidate_id,
      condition_id:v.condition_id,reason:v.reason})),failures,
    decision_ids:run.decisions.map(d=>d.decision_id),
    termination_reason:discovery?'confirmation_limit_reached':'specified_comparison_finished',simulation:true};
  if(!run.claims.length) throw Error('No-known-claims termination policy is outside these fixtures');
  finish(report); step('report_created',{report_id:run.report.report_id}); snapshot('reported');
  // Proposed expanded payload for R04; the stored report still uses ID references.
  run.screen_payload={request_id:requestId,simulation:true,report_status:run.report.status,
    task_statuses:run.tasks.map(t=>({task_id:t.task_id,status:t.status,status_reason:t.status_reason,
      failure_reason:t.failure_reason})),claims:clone(run.claims),verdicts:clone(run.verdicts),
    evidence:clone(run.evidence),sources:clone(run.sources),uncertainties:clone(run.report.unverified),
    failures:clone(failures),discovery_decisions:clone(run.decisions)};
  return run;
}

// Checks target the observed integration gaps, not production schema validation.
function evaluate(run) {
  const checks=[]; const check=(criterion,ok)=>checks.push({criterion,verdict:ok?'pass':'fail'});
  const by=(list,key,id)=>list.find(x=>x[key]===id);
  const task=id=>by(run.tasks,'task_id',id);
  const verdict=id=>by(run.verdicts,'verdict_id',id);
  const evidence=id=>by(run.evidence,'evidence_id',id);
  const source=id=>by(run.sources,'source_id',id);
  const seq=(event,id)=>run.steps.find(e=>e.event===event&&e.task_id===id)?.seq;
  const objects=[...run.tasks,...run.sources,...run.evidence,...run.verdicts,...run.claims,...run.decisions,run.report];
  const ids=[...run.tasks.map(t=>t.task_id),...run.sources.map(s=>s.source_id),...run.evidence.map(e=>e.evidence_id),
    ...run.verdicts.map(v=>v.verdict_id),...run.claims.map(c=>c.claim_id),...run.decisions.map(d=>d.decision_id),run.report.report_id];
  check('FR-02/03: request scope and unique object IDs',objects.every(x=>x.request_id===run.input.request_id)&&new Set(ids).size===ids.length);
  check('FR-02: task goals, roles, run_if and reasons are explicit',run.tasks.every(t=>t.goal&&t.role&&t.run_if&&
    Object.hasOwn(t,'status_reason')&&(['실패','보류','생략'].includes(t.status)?!!t.status_reason:true)));
  check('FR-03: dependency outcomes precede starts; failed input allowed only by explicit terminal gate',run.tasks.every(t=>t.depends_on.every(ref=>!!task(ref)&&
    (!seq('task_started',t.task_id)||((task(ref).status==='완료'||
      (t.run_if.op==='all_tasks_terminal'&&t.run_if.task_ids.includes(ref)&&terminal(task(ref).status)))&&
      seq('task_finished',ref)<seq('task_started',t.task_id))))));
  check('FR-03: result-based task gates have finished inputs',run.tasks.every(t=>t.run_if.op!=='all_tasks_terminal'||
    t.run_if.task_ids.every(ref=>!!task(ref)&&terminal(task(ref).status)&&
      (seq('task_finished',ref)||run.steps.find(e=>e.event==='discovery_not_executed'&&e.task_id===ref)?.seq)<seq('task_started',t.task_id))));
  const pairs=run.input.targets.flatMap(t=>run.input.criteria.map(c=>[t.candidate_id,c.condition_id]));
  check('FR-01/04: every target x required/preferred condition has one verdict',run.verdicts.length===pairs.length&&
    pairs.every(([target,condition])=>run.verdicts.filter(v=>v.candidate_id===target&&v.condition_id===condition).length===1));
  check('FR-04: verdict -> task and supporting evidence -> original source',run.verdicts.every(v=>task(v.task_id)?.candidate_id===v.candidate_id&&
    task(v.task_id)?.condition_ids.includes(v.condition_id)&&
    ['충족','미충족','미확인'].includes(v.status)&&(v.status==='미확인'?!!v.reason:v.evidence_ids.length>0)&&
    v.evidence_ids.every(ref=>{const e=evidence(ref),s=e&&source(e.source_id);
      return e&&s&&e.candidate_id===v.candidate_id&&e.condition_id===v.condition_id&&
        s.candidate_id===v.candidate_id&&s.access_status==='원문 확인'&&!!task(s.task_id);})));
  check('FR-04: claims and report retain resolvable verdict/evidence/source references',run.claims.every(c=>
    !!verdict(c.verdict_id)&&c.evidence_ids.length>0&&c.evidence_ids.every(ref=>!!evidence(ref)))&&
    run.report.claim_ids.every(ref=>by(run.claims,'claim_id',ref))&&
    run.verdicts.every(v=>run.report.verdict_ids.includes(v.verdict_id))&&run.report.source_ids.every(ref=>!!source(ref)));
  check('FR-04: failed access produces no evidence; unknown stays separate from task status',run.sources.filter(s=>s.access_status==='접근 실패').every(s=>
    !run.evidence.some(e=>e.source_id===s.source_id)&&task(s.task_id)?.status==='실패')&&
    run.verdicts.filter(v=>v.status==='미확인').every(v=>task(v.task_id)?.status==='완료'&&v.evidence_ids.length===0));
  check('FR-04: partial report preserves known and unknown conditions',run.report.status==='부분 결과'&&run.report.claim_ids.length>0&&
    run.verdicts.filter(v=>v.status==='미확인').every(v=>run.report.unverified.some(u=>u.verdict_id===v.verdict_id)));
  check('FR-03/04: screen payload retains failures, unknowns, report state and reasons',
    run.screen_payload.report_status===run.report.status&&JSON.stringify(run.screen_payload.failures)===JSON.stringify(run.report.failures)&&
    JSON.stringify(run.screen_payload.uncertainties)===JSON.stringify(run.report.unverified)&&
    JSON.stringify(run.screen_payload.discovery_decisions)===JSON.stringify(run.decisions));
  if(run.case_id==='APP-A') {
    check('APP-A: no discovery task; preference does not become required',!run.tasks.some(t=>t.role==='discovery')&&
      run.input.criteria.find(c=>c.condition_id==='accountless')?.priority==='선호');
  } else {
    const discovery=run.tasks.find(t=>t.role==='discovery');
    const waiting=run.snapshots.find(s=>s.phase==='awaiting_confirmation');
    const closed=run.snapshots.find(s=>s.phase==='limit_closed');
    const dseq=run.steps.find(e=>e.event==='discovery_deferred')?.seq;
    const lseq=run.steps.find(e=>e.event==='confirmation_limit_reached')?.seq;
    const nseq=run.steps.find(e=>e.event==='discovery_not_executed')?.seq;
    check('APP-C3: unresolved run_if references condition verdict IDs',discovery.run_if.op==='all_verdicts_are'&&
      discovery.run_if.verdict_ids.every(ref=>!!verdict(ref))&&discovery.run_if.verdict_ids.some(ref=>verdict(ref)?.status==='미확인'));
    check('APP-C3: defer -> limit event -> final non-execution -> report',waiting?.tasks.find(t=>t.task_id===discovery.task_id)?.status==='보류'&&
      closed?.tasks.find(t=>t.task_id===discovery.task_id)?.status==='생략'&&dseq<lseq&&lseq<nseq&&
      nseq<run.steps.find(e=>e.event==='report_created')?.seq&&run.report.termination_reason==='confirmation_limit_reached');
    check('APP-C3: discovery never starts; terminal reason and fixture limit retained',!run.steps.some(e=>e.event==='task_started'&&e.task_id===discovery.task_id)&&
      discovery.status==='생략'&&discovery.status_reason==='limit_reached_condition_unknown'&&
      run.decisions.at(-1)?.action==='최종 미실행'&&run.decisions.at(-1)?.limit?.scope.startsWith('fixture-only'));
  }
  return checks;
}

const runs=fixtures.map(execute);
const evaluations=runs.map(run=>({case_id:run.case_id,run_id:run.id,checks:evaluate(run)}));
const negatives=[];
function negative(id,index,mutate) {
  const bad=clone(runs[index]); mutate(bad);
  const failures=evaluate(bad).filter(c=>c.verdict==='fail');
  negatives.push({id,detected:failures.length>0,failures});
}
negative('dangling evidence reference',0,r=>r.verdicts[0].evidence_ids=['MISSING']);
negative('unsupported positive verdict',0,r=>r.verdicts.find(v=>v.status==='미확인').status='충족');
negative('premature discovery during unknown',1,r=>r.steps.push({seq:0,event:'task_started',task_id:r.tasks.find(t=>t.role==='discovery').task_id}));
negative('lost final non-execution reason',1,r=>r.tasks.find(t=>t.role==='discovery').status_reason=null);
const result={schema_version:1,id:'R03-APP-A-C3-IO-MOCK-20261112',kind:'mock_contract_review',
  status:'R03 합성 출력 검사',generated_at:new Date().toISOString(),
  provenance:{workspace_revision:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),
    contract_basis_revision:'6eb42c8c30f4b53cd36640657b5e9829e733b46d',
    task_id:'TASK-005',contract_path:contractPath,contract_sha256:hash(path.join(root,contractPath)),
    spec_path:specPath,spec_sha256:hash(path.join(root,specPath)),script_sha256:hash(__filename)},
  scope:'APP-A ID chain and APP-C3 deferred-to-terminal handoff only; local R03 proposal',
  limitations:['All findings, source outcomes and condition verdicts are synthetic; not real app facts.',
    'retrieved_at is null: simulation ticks are not actual retrieval times or elapsed time.',
    'No model, search, device, real parallelism, API/UI integration or B0/D0 comparison.',
    'Field names, deferred-node representation and fixture-only limit are not a team contract.',
    'No-known-claims report policy and C1/C2 end-to-end execution are outside this small prototype.',
    'Old 18-case/4-negative-control result is preserved and is not combined with these counts.'],
  summary:{cases:runs.length,passed:evaluations.filter(e=>e.checks.every(c=>c.verdict==='pass')).length,
    checks:evaluations.reduce((n,e)=>n+e.checks.length,0),failed_checks:evaluations.flatMap(e=>e.checks).filter(c=>c.verdict==='fail').length,
    negative_controls:negatives.length,detected:negatives.filter(n=>n.detected).length},
  runs,evaluations,negative_controls:negatives};
// Write failing results too, so an unsuccessful check is reviewable.
fs.writeFileSync(outputPath,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result.summary));
if(result.summary.failed_checks || result.summary.detected!==negatives.length) process.exitCode=1;
