import {readFileSync} from 'node:fs';
import {validateDesignConstraints,runConstraintRegression} from './validate-constraints-v0.7.mjs';
const files={
  "core": "core-contract-v0.3.json",
  "contract": "contract-v0.5.json",
  "api": "data-api-v0.3.json",
  "physical": "physical-v0.4.json",
  "implementation": "implementation-v0.4.json",
  "index": "trace-index-v0.6.json",
  "wbs": "wbs-v0.5.json",
  "review": "review-v0.3.json"
};
const D=Object.fromEntries(Object.entries(files).map(([k,p])=>[k,JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'))]));
const normal=validateDesignConstraints(D),regression=runConstraintRegression(D,validateDesignConstraints);
console.log(JSON.stringify({normal,regression},null,2));
process.exitCode=normal.passed===normal.total&&regression.passed===regression.total?0:1;
