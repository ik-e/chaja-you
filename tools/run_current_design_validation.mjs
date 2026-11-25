#!/usr/bin/env node
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const b='docs/artifacts/design/lesson-registration-20261124/';
const p='product/lesson-registration';
const read=n=>JSON.parse(readFileSync(resolve(root,b+n),'utf8'));
const run=(cmd,args,cwd=root,env={})=>{
 const r=spawnSync(cmd,args,{cwd,encoding:'utf8',timeout:300000,maxBuffer:8*1024*1024,env:{...process.env,...env}});
 return {cmd,args,exit_code:r.status,stdout:r.stdout??'',stderr:r.stderr??'',error:r.error?.message??null,pass:r.status===0&&!r.error};
};
const git=(...args)=>{const r=run('git',args);if(!r.pass)throw Error(r.stderr||r.error||'git failed');return r.stdout.trim()};
const load=n=>import(pathToFileURL(resolve(root,b+n)).href);
const suites=['logical','data','integration','trace','model','implementation','markdown','all-design'];
const opts={suite:'all-design',expected:null,out:null};
let report={kind:'current_design_validation',product_execution:'not_run',approval:'not_granted',results:[]};
try {
 const argv=process.argv.slice(2);
 for(let k=0;k<argv.length;k+=2){const key={'--suite':'suite','--expected-sha':'expected','--out':'out'}[argv[k]];if(!key||!argv[k+1])throw Error('invalid argument');opts[key]=argv[k+1]}
 if(!suites.includes(opts.suite))throw Error('unknown suite');
 const sha=git('rev-parse','HEAD');
 report={...report,target_sha:sha,launcher_blob:git('rev-parse','HEAD:tools/run_current_design_validation.mjs'),node:process.version,executed_at:new Date().toISOString(),requested_suite:opts.suite};
 if(opts.expected&&(!/^[0-9a-f]{40}$/.test(opts.expected)||sha!==opts.expected))throw Error('target SHA mismatch');
 if(git('status','--porcelain','--untracked-files=no'))throw Error('tracked working tree is dirty');
 async function suite(name){
  if(name==='logical'){
   const {verify}=await load('validate-logical-v5.mjs'),m=read('logical-behavior-v5.json');
   const cases=[4,5].map(n=>verify(m,n));
   const a=structuredClone(m);a.rules.push({id:'injected_user_cancel',actor:'USER',when:{job:'active'},set:{job:'stopping'}});
   const z=structuredClone(m);delete z.rules.find(x=>x.id==='accept').when.review;
   const mutations=[{id:'user_cancel',detected:verify(a,4).violations.length>0},{id:'unreviewed_accept',detected:verify(z,4).violations.length>0}];
   return {pass:cases.every(x=>!x.violations.length&&!x.unused.length&&!x.no_outcome)&&mutations.every(x=>x.detected),cases,mutations,limit:'finite model only'};
  }
  if(name==='data'){
   const {run:check}=await load('validate-data-contract-v4.mjs');const cases=check(read('data-schema-v4.1.json'),read('platform-profiles-v2.json'));
   return {pass:cases.length===31&&cases.every(x=>x.pass),cases,limit:'existing subset semantic checker; not standards-complete'};
  }
  if(name==='integration'){
   const {verify}=await load('validate-common-integration-v1.mjs');
   const inputs=['common-integration-v1.json','trace-index-v0.9.json','data-schema-v4.1.json','platform-profiles-v2.json','detail-gate-v1.json','wbs-v0.5.json'].map(read);
   const result=verify(...inputs);
   const inject=(id,change,expected)=>{const x=structuredClone(inputs);change(x);const y=verify(...x);return {id,detected:!y.pass&&y.checks.some(c=>!c.pass&&c.id.startsWith(expected))}};
   const mutations=[
    inject('missing_test',x=>x[0].gate.tests.pop(),'COMMON-09'),
    inject('cycle',x=>x[0].integration.dependencies.push(['STORE','CO']),'COMMON-03'),
    inject('resume',x=>x[0].routes.push({...x[0].routes[0],id:'H99',path:'/v1/resume'}),'COMMON-10'),
    inject('unknown_prior',x=>x[0].decisions[0].prior_decision_refs.push('UNKNOWN'),'COMMON-06')
   ];
   return {pass:result.pass&&result.checks.length===14&&mutations.every(x=>x.detected),result,mutations,limit:'adopted frozen design checks; historical WBS is reference only'};
  }
  if(name==='trace'){
   const checks=['tools/generate_lesson_design_review.mjs','tools/generate_lesson_current_design.mjs'].map(f=>run(process.execPath,[f,'--check']));
   checks.push(run('python3',['tools/project_docs.py','--check']));
   return {pass:checks.every(x=>x.pass),checks,limit:'reference and projection consistency; no semantic proof'};
  }
  if(name==='model'){const checks=[run('python3',['tools/check_ai_design_playbook.py'])];return {pass:checks.every(x=>x.pass),checks,limit:'methodology/sample only'}}
  if(name==='markdown'){const checks=[run(process.execPath,['tools/check_markdown_ranges.mjs','--self-test']),run(process.execPath,['tools/check_markdown_ranges.mjs','docs/design/lesson-registration/CURRENT-DESIGN.md','docs/design/lesson-registration/BASELINE-POLICY.md'])];return {pass:checks.every(x=>x.pass),checks}}
  if(name==='implementation'){
   const cwd=resolve(root,p),env={PYTHONPATH:'.:src',LR_ENVIRONMENT:'mock'};
   const checks=[run('uv',['run','--locked','--python','3.12','python','dev.py','test','all'],cwd,env),run('uv',['run','--no-project','--python','3.12','--with','jsonschema==4.25.1','python','-m','unittest','discover','-s','tests/contract/standard_schema','-v'],cwd,env)];
   return {pass:checks.every(x=>x.pass),checks,limit:'synthetic boundary, not product'};
  }
  throw Error('unsupported suite');
 }
 for(const name of opts.suite==='all-design'?['logical','data','integration','trace']:[opts.suite]){
  try{const x=await suite(name);report.results.push({suite:name,status:x.pass?'pass':'fail',...x})}catch(e){report.results.push({suite:name,status:'error',error:String(e)})}
 }
 report.status=report.results.every(x=>x.status==='pass')?'pass':'fail';
}catch(e){report.status='error';report.error=String(e)}
const rendered=JSON.stringify(report,null,2)+'\n';
if(opts.out)writeFileSync(resolve(opts.out),rendered,'utf8');
console.log(rendered);
process.exitCode=report.status==='pass'?0:1;
