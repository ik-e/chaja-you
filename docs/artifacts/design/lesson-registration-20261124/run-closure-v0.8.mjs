import {readFileSync} from 'node:fs';
import {evaluateMvpGate,validateV08,regression} from './validate-closure-v0.8.mjs';
const files={"core":"core-contract-v0.3.json","api":"data-api-v0.3.json","implementation":"implementation-v0.4.json","physical":"physical-v0.4.json","contract":"contract-v0.5.json","wbs":"wbs-v0.5.json","index":"trace-index-v0.6.json"};
const D=Object.fromEntries(Object.entries(files).map(([k,p])=>[k,JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'))]));
const normal=validateV08(D,evaluateMvpGate),reg=regression(D,validateV08,evaluateMvpGate);
console.log(JSON.stringify({normal,reg},null,2));
process.exitCode=normal.passed===normal.total&&normal.gate_passed===normal.gate_total&&reg.passed===reg.total?0:1;
