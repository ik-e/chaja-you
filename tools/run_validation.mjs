#!/usr/bin/env node
// Independent, read-only validation launcher. Node >=20, git and Python (model suite).
import {readFileSync, writeFileSync, mkdirSync, realpathSync, existsSync} from 'node:fs';
import {resolve, dirname, join, sep} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';

const suites=['model','trace','contract','wbs','markdown','all-design'];
const root='docs/artifacts/design/lesson-registration-20261124';
const args=process.argv.slice(2);
function options(){
  const a={repo:'.',suite:'trace',out:null,expected:null};
  const names={'--repo':'repo','--suite':'suite','--out':'out','--expected-sha':'expected'};
  for(let i=0;i<args.length;i+=2){
    if(!names[args[i]]||!args[i+1])throw Error('Invalid argument: '+args[i]);
    a[names[args[i]]]=args[i+1];
  }
  if(!suites.includes(a.suite))throw Error('Unknown suite: '+a.suite);
  if(a.expected&&!/^[a-f0-9]{40}$/.test(a.expected))throw Error('Expected full 40-character SHA');
  return a;
}
function command(cmd,argv,cwd){
  const p=spawnSync(cmd,argv,{cwd,encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024,env:{...process.env,PYTHONUTF8:'1'}});
  return {exit_code:p.status,stdout:p.stdout??'',stderr:p.stderr??'',error:p.error?.message??null};
}
function git(repo,argv){
  const p=command('git',argv,repo);
  if(p.exit_code!==0)throw Error('git '+argv[0]+': '+(p.error??p.stderr));
  return p.stdout.trim();
}
function inside(repo,rel){
  if(typeof rel!=='string'||!rel||rel.includes('\\')||rel.startsWith('/')||rel.split('/').some(s=>s==='..'||s==='.'||!s))throw Error('Unsafe source path: '+rel);
  const p=realpathSync(resolve(repo,rel));
  if(!p.startsWith(repo+sep))throw Error('Source escapes repository: '+rel);
  return p;
}
function read(repo,rel){return readFileSync(inside(repo,rel));}
function json(repo,rel){return JSON.parse(read(repo,rel).toString('utf8'));}
function sha(bytes){return createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');}
function result(name,checks,extra={}){
  return {suite:name,status:checks.every(c=>c.pass===true)?'pass':'fail',passed:checks.filter(c=>c.pass===true).length,total:checks.length,checks,...extra};
}
function subprocessCheck(repo,rel,cmd,extra=[]){
  const p=command(cmd,[inside(repo,rel),...extra],repo);
  let structured=null;try{structured=JSON.parse(p.stdout);}catch{}
  return {id:rel,pass:p.exit_code===0&&!p.error,exit_code:p.exit_code,details:structured??p.stdout,stderr:p.stderr,error:p.error};
}
async function loadTrace(repo){
  const idx=json(repo,root+'/trace-index-v0.6.json'),sources={},blobs={};
  if(Object.keys(idx.sources).length===0)throw Error('Empty source index');
  for(const [key,s] of Object.entries(idx.sources)){
    const bytes=read(repo,s.path);blobs[key]=sha(bytes);sources[key]=s.path.endsWith('.json')?JSON.parse(bytes.toString('utf8')):bytes.toString('utf8');
  }
  const core=await import(pathToFileURL(inside(repo,'tools/validate_design_information.mjs')).href);
  const trace=await import(pathToFileURL(inside(repo,root+'/validate-trace-v0.6.mjs')).href);
  return {idx,sources,blobs,core,trace};
}
async function traceSuite(repo,wbsOnly=false){
  const {idx,sources,blobs,core,trace}=await loadTrace(repo);
  const params=[idx,sources,blobs,core.validateDesignInformation,core.designImpact];
  const {normal,regression}=wbsOnly?{normal:trace.buildAndValidate(...params),regression:null}:trace.runRegression(...params);
  const checkList=normal.checks.map(x=>({...x,kind:'index'}));
  if(wbsOnly){
    const selected=checkList.filter(x=>x.id.startsWith('WBS-'));
    if(selected.length===0)throw Error('No WBS checks found');
    const integrity=checkList.filter(x=>x.id.startsWith('IDX-01'));
    if(integrity.length!==1)throw Error('Missing source-integrity check');
    return result('wbs',[...integrity,...selected],{source_count:Object.keys(blobs).length,note:'Shared graph construction is required; only source integrity and WBS checks are graded. No regression suite or product execution.'});
  }
  const graph=normal.graph.checks.map(x=>({...x,kind:'graph'}));
  const cases=regression.cases.map(x=>({...x,id:x.name,kind:'regression'}));
  if(!checkList.length||!graph.length||!cases.length)throw Error('Unexpected empty trace checks');
  return result('trace',[...checkList,...graph,...cases],{index_passed:normal.passed,index_total:normal.total,graph_passed:normal.graph.passed,graph_total:normal.graph.total,regression_passed:regression.passed,regression_total:regression.total,source_count:Object.keys(blobs).length,records:normal.graph.record_count,edges:normal.graph.edge_count,review_links:normal.graph.review_link_count,projection_edges:normal.graph.projection_count,warnings:normal.graph.warnings,impact:normal.impact,product_execution:'not_run'});
}
async function suite(repo,name){
  if(name==='trace')return traceSuite(repo);
  if(name==='wbs')return traceSuite(repo,true);
  if(name==='model')return result(name,[subprocessCheck(repo,'tools/validate_planning_design_model.py','python3')],{note:'Original planning model and example validator, separate from lesson trace.'});
  if(name==='contract')return result(name,[subprocessCheck(repo,root+'/validate-v0.5.mjs',process.execPath)],{note:'Existing V0.5 static and abstract contract tests; not real product execution.'});
  if(name==='markdown'){
    const tool='tools/check_markdown_ranges.mjs';
    return result(name,[subprocessCheck(repo,tool,process.execPath,['--self-test']),subprocessCheck(repo,tool,process.execPath,[root])],{note:'Read-only Markdown scan scoped to the lesson design directory. Existing findings are not automatically changed.'});
  }
  throw Error('Unsupported suite');
}
let report;
let cfg;
try{
  cfg=options();
  const repo=realpathSync(cfg.repo);
  const revision=git(repo,['rev-parse','HEAD']);
  const dirty=!!git(repo,['status','--porcelain','--untracked-files=no']);
  report={schema_version:1,kind:'validation_execution',requested_suite:cfg.suite,target_sha:revision,working_tree_dirty:dirty,executed_at:new Date().toISOString(),launcher_sha:sha(readFileSync(new URL(import.meta.url))),runtime:{node:process.version},product_execution:'not_run',approval:'not_granted',results:[]};
  if(cfg.expected&&(revision!==cfg.expected||dirty))throw Error('Target SHA mismatch or tracked working tree is dirty');
  for(const name of cfg.suite==='all-design'?suites.filter(x=>x!=='all-design'): [cfg.suite]){
    try{report.results.push(await suite(repo,name));}
    catch(e){report.results.push({suite:name,status:'error',error:String(e),passed:0,total:0,checks:[]});}
  }
  report.status=report.results.length>0&&report.results.every(x=>x.status==='pass')?'pass':'fail';
}catch(e){
  report={...(report??{schema_version:1,kind:'validation_execution',product_execution:'not_run',approval:'not_granted'}),status:'error',error:String(e)};
}
const rendered=JSON.stringify(report,null,2)+'\n';
if(cfg?.out){const path=resolve(cfg.out);mkdirSync(dirname(path),{recursive:true});writeFileSync(path,rendered);}
console.log(rendered);
process.exitCode=report.status==='pass'?0:1;
