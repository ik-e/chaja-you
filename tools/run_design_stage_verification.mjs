#!/usr/bin/env node
import {readFileSync,realpathSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,sep,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {executeDesignRules,designStageGate,selfTest} from './verify_design_stage.mjs';
const blob=b=>createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');
const root=realpathSync(process.cwd());
const read=rel=>{if(typeof rel!=='string'||rel.startsWith('/')||rel.split('/').some(x=>!x||x==='.'||x==='..'))throw Error('unsafe path: '+rel);const p=realpathSync(resolve(root,rel));if(!p.startsWith(root+sep))throw Error('path escapes repo');return {path:p,bytes:readFileSync(p)};};
if(process.argv[2]==='--self-test'){const t=selfTest();console.log(JSON.stringify(t,null,2));process.exitCode=t.passed===t.total?0:1;}
else {
 const manifest=JSON.parse(read(process.argv[2]).bytes.toString('utf8'));
 const adapter=read(manifest.adapter),module=await import(pathToFileURL(adapter.path).href);
 const engine=readFileSync(resolve(dirname(fileURLToPath(import.meta.url)),'verify_design_stage.mjs'));
 const revisions={engine:blob(engine),adapter:blob(adapter.bytes)};
 const sources=Object.fromEntries(Object.entries(manifest.sources).map(([k,v])=>{const f=read(v);return [k,{blob_sha:blob(f.bytes),data:v.endsWith('.json')?JSON.parse(f.bytes.toString('utf8')):f.bytes.toString('utf8')}];}));
 const results=executeDesignRules(manifest.rules,sources,module.checkers,revisions);
 const gates=[...new Set(manifest.rules.map(r=>r.stage))].map(stage=>({stage,...designStageGate({rules:manifest.rules,sources,revisions,results,stage})}));
 console.log(JSON.stringify({scope:manifest.scope,results,gates,product_execution:'not_run'},null,2));
 process.exitCode=gates.some(x=>x.status!=='declared_checks_pass')?1:0;
}
