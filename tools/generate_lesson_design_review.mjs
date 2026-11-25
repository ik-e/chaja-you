#!/usr/bin/env node
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {dirname} from 'node:path';
function generate({ref,main,base,dest,groups,inventory,data}){
 const urls="https://github.com/ik-e/chaja-you/blob/",source=n=>urls+ref+"/"+base+n,oper=p=>urls+main+"/"+p;
 const files={},bindings=[],seen={},by=Object.fromEntries(inventory.map(x=>[x.path.slice(base.length),x]));
 const escape=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\|/g,"&#124;").replace(/\r?\n/g," ↵ ").replace(/([`*_\\[\]])/g,x=>"&#"+x.charCodeAt(0)+";");
 const scalar=v=>v===null||typeof v!=="object";
 const fmt=v=>typeof v==="string"?escape(v)||'`""`':"`"+JSON.stringify(v)+"`";
 const label=k=>({id:"ID",status:"상태",decision:"결정",why:"근거",reason:"이유",rationale:"이유",alternative:"대안",expected:"기대값",execution:"실행",source_refs:"출처",revisit_when:"재검토 조건",requirement_refs:"요구 참조",planned_test_refs:"계획 시험"}[k]||k);
 const leaf=v=>scalar(v)?1:Object.values(v).reduce((a,x)=>a+leaf(x),0);
 function render(v,depth=0){
  let pad="  ".repeat(depth);
  if(scalar(v))return pad+"- "+fmt(v);
  if(Array.isArray(v)){
   if(!v.length)return pad+"- `[]`";
   return v.map((x,i)=>scalar(x)?pad+"- "+fmt(x):Array.isArray(x)&&x.every(scalar)?pad+"- "+x.map(fmt).join(" · "):pad+"- **["+i+"] "+escape(x.id||"")+"**\n"+render(x,depth+1)).join("\n");
  }
  return Object.keys(v).length?Object.entries(v).map(([k,x])=>pad+"- **"+escape(label(k))+"** (`"+k+"`)"+(scalar(x)?": "+fmt(x):Array.isArray(x)&&x.every(scalar)?": "+(x.length?x.map(fmt).join(" · "):"`[]`"):"\n"+render(x,depth+1))).join("\n"):pad+"- `{}`";
 }
 const table=(heads,rows)=>[heads,heads.map(()=> "---"),...rows].map(row=>"| "+row.join(" | ")+" |").join("\n")+"\n";
 const header=t=>`# ${t}\n\n> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 \`${ref}\`. 설계 채택/구현/실서비스 승인 아님.\n\n[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)\n\n`;
 for(const [path,title,specs] of groups){
  let md=header(title),maps=[];
  for(const [n,keys] of specs){
   const j=data[n],ks=keys||Object.keys(j);
   seen[n]??=new Set();
   md+=`## ${n}\n\n[고정 JSON 원본](${source(n)}) · blob \`${by[n].sha}\`\n\n`;
   if(n==="wbs-v0.5.json")md+="> 이전 WBS 후보. A2 및 현재 공통 계약 우선. 일정/담당 배정 전.\n\n";
   if(n==="logical-data-contract-decision-v1.json")md+="> remaining/closure는 결정 당시 상태. 현재 해결 여부는 후속 V4/공통 V1에서 확인.\n\n";
   for(const k of ks){
    if(!Object.hasOwn(j,k)||seen[n].has(k))throw Error("invalid coverage "+n+"/"+k);seen[n].add(k);
    const v=j[k];md+="### "+k+"\n\n";
    if(k==="$defs")md+=Object.entries(v).map(([name,def])=>"#### "+name+"\n\n"+render(def)).join("\n\n");
    else if(Array.isArray(v)&&v.length&&v.every(x=>x&&typeof x==="object"&&!Array.isArray(x)&&typeof x.id==="string"))md+=v.map(x=>"#### "+escape(x.id)+"\n\n"+render(x)).join("\n\n");
    else md+=render(v);
    md+="\n\n";
   }
   maps.push({source:base+n,blob:by[n].sha,pointers:ks.map(k=>"/"+k.replace(/~/g,"~0").replace(/\//g,"~1")),leaf_count:ks.reduce((a,k)=>a+leaf(j[k]),0)});
  }
  files[dest+path]=md;bindings.push({path:dest+path,title,bindings:maps});
 }
 for(const [n,ks] of Object.entries(seen))if(n!=="implementation-v0.4.json"&&ks.size!==Object.keys(data[n]).length)throw Error("missing sections "+n);
 const c=data["common-integration-v1.json"],t=data["trace-index-v0.9.json"],s=data["data-schema-v4.1.json"],p=data["platform-profiles-v2.json"];
 const ids=c.gate.tests.map(x=>x.id);if(new Set(ids).size!==ids.length||ids.length!==c.gate.required.length||c.gate.required.some(x=>!ids.includes(x)))throw Error("gate mismatch");
 const inv=inventory.map(x=>{let n=x.path.slice(base.length);return {...x,url:source(n),status:n==="wbs-v0.5.json"?"historical_candidate":n==="implementation-v0.4.json"?"requirements_retained_other_sections_historical":seen[n]?(n.includes("validation")?"bounded_evidence":"current_or_explicitly_retained"):"history_or_supporting",views:bindings.filter(d=>d.bindings.some(b=>b.source===x.path)).map(d=>d.path)}});
 const coverage={inventory_files:inventory.length,projected_json_sources:Object.keys(seen).length,fully_projected_json_sources:Object.keys(seen).length-1,selected_leaf_values:bindings.reduce((a,d)=>a+d.bindings.reduce((b,x)=>b+x.leaf_count,0),0),schema_definitions:Object.keys(s.$defs).length,logical_rules:data["logical-behavior-v5.json"].rules.length,profiles:p.profiles.length,ports:c.ports.length,http_routes:c.routes.length,common_decisions:c.decisions.length,trace_inventory_records:t.inventory.length,required_product_tests:ids.length,product_execution:c.gate.execution};
 const manifest={id:"LR-DESIGN-REVIEW-PROJECTION-01",source_commit:ref,operational_main_commit:main,source_directory:base,precedence:[...t.precedence,"운영 단계는 main PHASE-20261124-03 우선. 기존 TASK/권한 변경 없음."],documents:bindings,inventory:inv,coverage,review_protocol:{reference:"source_commit + source path + JSON Pointer or design ID",outcomes:["동의","변경 제안","문제 발견","추가 검증 필요"],decision:"R01 판단; 의견만으로 정본/업무/승인 변경 금지"},validation:{source_keys_complete_except_explicit_subset:true,duplicate_sections:false,gate_ids_exact_match:true,limits:"읽기 뷰 완전성 검사. 실제 제품·설계 의미 검증 재실행 아님."}};
 files[dest+"MANIFEST.json"]=JSON.stringify(manifest,null,2)+"\n";
 files[dest+"12-HISTORY.md"]=header("전체 원본 및 설계 이력")+
 "## 우선순위\n\n"+manifest.precedence.map(x=>"- "+x).join("\n")+
 "\n\n과거 취소/재개/rollback 계약은 A2 이후 현행 기능이 아니다. 과거 stage replay는 해당 당시 계약으로만 해석한다. 아래 원본은 모두 고정 커밋에서 열 수 있다.\n\n"+
 table(["원본","적용","읽기 뷰"],inv.map(x=>[`[${x.path.slice(base.length)}](${x.url})`,x.status,x.views.map(p=>`[${p.slice(dest.length)}](${p.slice(dest.length)})`).join(" · ")||"원본 직접 조회"]))+
 "\n## 운영 정본\n\n"+["docs/human/phase-intents/PHASE-20261124-03.md","docs/review/README.md",...["043","044","045","046","047"].map(id=>`docs/artifacts/tasks/TASK-${id}.json`)].map(x=>`- [${x}](${oper(x)})`).join("\n")+"\n";
 files[dest+"README.md"]=header("레슨 등록 지원 서비스 · 채택 전 고정 설계 검토 스냅샷")+
 `[현행 설계 기준](CURRENT-DESIGN.md) · [현행 AI 인덱스](CURRENT-DESIGN.json)\n\n당시 운영 정본: [현재 단계](${oper("docs/human/phase-intents/PHASE-20261124-03.md")}) · [작업 검토](${oper("docs/review/README.md")}). 설계 정본: [재설계 기준선](${source("README.md")}).\n\n## 현재 적용 상태 확인\n\n이 문서는 고정된 설계 검토 스냅샷이다. 채택 및 배정 이후의 권한·작업·담당·일정은 [설계 채택 기록](../../artifacts/design/lesson-registration-20261124/adoption-20261125.json), [CURRENT](../../../CURRENT.md), [제품 WORKSPACE](../../../product/lesson-registration/WORKSPACE.json)를 우선한다. 아래 당시 후보 상태 및 이전 일정은 역사적 기록이다.\n\n## 1. 목표와 범위\n\n${data["top-design-v1.json"].goal}\n\n- 12/8 크몽 우선·숨고 확장 MVP 목표, 1/4 지원 URL 최초 등록 및 결과 확인 목표. 실제 플랫폼 권한 별도, 현재 mock-only.\n- 사전 확보 프로필로 등록 대행; 범용 사이트 자동 적응·AI 자유 재계획 불필요.\n- A2: 수락 후 사용자 중단/변경/재개/rollback 없음. 오류 시에만 시스템 중단 및 결과 반환.\n\n## 2. 논리 아키텍처\n\n`+
 "```mermaid\nflowchart LR\n U[사용자] --> UI[Web UI]\n UI --> CO[CO 업무 조정]\n UI --> V[VIEWER 직접 인증]\n CO --> KNOW[KNOW 플랫폼 지식]\n CO --> PREP[PREP 정보 준비]\n CO --> EXEC[EXEC 인증·실행]\n CO --> RESULT[RESULT 결과 판정]\n CO --> STORE[STORE 영속 기록]\n PREP --> KNOW\n EXEC --> KNOW\n EXEC --> RT[RUNTIME 원격 브라우저]\n V --> RT\n RT --> KNOW\n RT --> STORE\n```\n\n"+
 "화살표는 논리 의존 관계이며 물리 서비스 분리 강제가 아니다. Source(불변 원본), Profile(고정 규칙), Registration(준비·인증·승인·실행·결과) 세 구조. 원본/대상 지정 → 준비/질문 → 직접 인증 → 최종 승인 → 작업 수락 → 실행·관측 → 결과 조회.\n\n## 3. 업무 계약\n\n"+
 table(["포트","호출→제공","입력→출력"],c.ports.map(x=>[x.id,x.consumer+" → "+x.provider,escape(x.input+" → "+x.output)]))+"\n"+
 table(["ID","HTTP","역할"],c.routes.map(x=>[x.id,"`"+x.method+" "+x.path+"`",escape(x.purpose)]))+"\n## 4. 주요 결정\n\n"+
 table(["ID","선택","근거"],c.decisions.map(x=>[x.id,escape(x.fields.selection_and_reason.selection),escape(x.fields.selection_and_reason.reason)]))+
 "\n## 5. 상세 검토 뷰\n\n"+table(["순서","문서"],bindings.map((x,i)=>[String(i+1),`[${x.title}](${x.path.slice(dest.length)})`]))+
 `\n[전체 원본 ${inventory.length}개](12-HISTORY.md) · [AI 인덱스](MANIFEST.json). AI는 고정 commit/blob/JSON Pointer를 사용하여 원본을 조회하고 사람용 Markdown을 별도 정본으로 취급하지 않는다.\n\n## 6. 당시 팀원 검토 요청 (이력: 담당 후보, 배정 전)\n\n`+
 table(["팀원","중점 영역"],[["R02","원본·정보/AI 준비·fixture·인계와 사용자 요구"],["R03","서버·API·상태/원자 저장·멱등성·시험"],["R04","UI·사용자 흐름·뷰어 연동·숨고"],["R05","인증·원격 실행·동일 연결·격리·adapter"],["R01","전체 목적·공통 경계·통합·결정/근거"]])+
 "\n누구나 전체 설계에 의견 가능. 실제 환경/언어/DB/의존성/실행 명령/담당·공수는 11/27 목표 게이트에서 검토할 후보이며 확정 또는 신규 TASK 아님. 기존 정산 TASK 유지.\n\n## 7. 검증 한계\n\n- 선정 공통 설계 검사 14/14, V4 합성 사례 31/31은 해당 입력에 한정. 실제 통합 제품 22개 시험 모두 미실행, T5-08 실제 모델 필수. 개인 PoC 및 stub을 제품 성공으로 승격하지 않는다.\n- 실제 운영사 허용, DB 경쟁, 원격 격리, 모델 및 사용자 가치 미검증. mock-only 유지.\n\n## 8. 의견 제출\n\n```text\n검토 대상: 문서/설계 ID/JSON Pointer + 기준 커밋\n의견 유형: 동의 | 변경 제안 | 문제 발견 | 추가 검증 필요\n의견 및 근거:\n대안/검증 방법(선택):\n영향 계약/작업(선택):\n```\n\n채택·부분 채택·미채택·보류와 사유는 기존 설계 결정/IT-19 체계에 반영. 새 ISSUE/PR/TASK 자동 생성 없음.\n\n## 9. 갱신\n\n```sh\nnode tools/generate_lesson_design_review.mjs --check\nnode tools/generate_lesson_design_review.mjs --source <설계커밋> --main <운영커밋>\n```\n\n정본 변경 시 그룹/우선순위도 검토하고 재생성. --check는 생성물 및 HEAD 설계 원본 변경을 대조한다. 제품 시험과 별개.\n";
 return {files,manifest};
}
const base="docs/artifacts/design/lesson-registration-20261124/",dest="docs/design/lesson-registration/",groups=[["01-GOALS.md","목표·요구사항·상위 결정",[["direction-v0.4.json"],["top-design-v1.json"],["top-design-amendment-v1.json"],["implementation-v0.4.json",["requirements"]]]],["02-LOGIC.md","논리 설계 및 상태 모델",[["detail-decisions-v2.json"],["logical-behavior-v5.json"]]],["03-DATA.md","상위 데이터와 상세 공통 계약",[["logical-data-contract-decision-v1.json"],["data-contract-v4.json"]]],["04-SCHEMA.md","공통 타입과 스키마 V4.1",[["data-schema-v4.1.json"]]],["05-PLATFORMS.md","플랫폼 프로필 V2",[["platform-profiles-v2.json"]]],["06-API-PORTS.md","HTTP API·업무 포트·오류",[["common-integration-v1.json",["id","version","date","status","authority","basis","schema_delta","routes","ports","http"]]]],["07-EXECUTION.md","실행·저장·인증·뷰어·UI",[["common-integration-v1.json",["state","storage","runtime","ui"]]]],["08-INTEGRATION.md","통합 구조·작업 공간·책임 후보",[["common-integration-v1.json",["integration","closure"]]]],["09-TESTS.md","수용 시험·검증·미확인 사항",[["common-integration-v1.json",["gate"]],["common-integration-validation-v1.json"],["data-contract-validation-v4.json"],["logical-validation-v5.json"]]],["10-DECISIONS.md","결정·근거·대안·영향 추적",[["common-integration-v1.json",["decisions"]],["trace-index-v0.9.json"]]],["11-WBS.md","WBS 및 통합 일정 이력",[["wbs-v0.5.json"]]]],names=["direction-v0.4.json","top-design-v1.json","top-design-amendment-v1.json","implementation-v0.4.json","detail-decisions-v2.json","logical-behavior-v5.json","logical-data-contract-decision-v1.json","data-contract-v4.json","data-schema-v4.1.json","platform-profiles-v2.json","common-integration-v1.json","common-integration-validation-v1.json","data-contract-validation-v4.json","logical-validation-v5.json","trace-index-v0.9.json","wbs-v0.5.json"];
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:32*1024*1024});
const args=process.argv.slice(2),check=args.includes('--check'),opt=k=>args.includes(k)?args[args.indexOf(k)+1]:null;
const prior=check?JSON.parse(readFileSync(dest+'MANIFEST.json','utf8')):null;
const ref=git('rev-parse','--verify',(opt('--source')||prior?.source_commit||'HEAD')+'^{commit}').trim(),main=git('rev-parse','--verify',(opt('--main')||prior?.operational_main_commit||'main')+'^{commit}').trim();
const treeAt=ref=>git('ls-tree','-r','-z',ref,'--',base).split('\0').filter(Boolean).map(x=>{const [meta,path]=x.split('\t');return {path,sha:meta.split(' ')[2]}}).sort((a,b)=>a.path.localeCompare(b.path));
const inventory=treeAt(ref),data=Object.fromEntries(names.map(n=>[n,JSON.parse(git('show',ref+':'+base+n))]));
const result=generate({ref,main,base,dest,groups,inventory,data});
if(check){const changed=Object.entries(result.files).filter(([p,c])=>{try{return readFileSync(p,'utf8')!==c}catch{return true}}).map(([p])=>p),stale=JSON.stringify(inventory)!==JSON.stringify(treeAt('HEAD').filter(x=>x.path!==base+'adoption-20261125.json'));console.log(JSON.stringify({pass:!changed.length&&!stale,changed,stale,coverage:result.manifest.coverage},null,2));if(changed.length||stale)process.exitCode=1;}
else{for(const [p,c] of Object.entries(result.files)){mkdirSync(dirname(p),{recursive:true});writeFileSync(p,c,'utf8')}console.log(JSON.stringify(result.manifest.coverage,null,2));}
