import fs from 'node:fs';
import assert from 'node:assert/strict';
const base = new URL('../', import.meta.url);
const read = p => JSON.parse(fs.readFileSync(new URL(p, base), 'utf8'));
const v4 = read('docs/artifacts/planning/lesson-registration-20261126/integrated/db-minimal-v4.json');
const v5 = read('docs/artifacts/planning/lesson-registration-20261126/integrated/db-minimal-v5.json');
const sw = read('docs/artifacts/planning/lesson-registration-20261126/integrated/system-work-v1.0.json');
const prior = new Set(v4.tables.flatMap(t=>t.fields.map(f=>t.name+'.'+f.name)));
const audited = v5.field_audit.filter(a=>a.classification!=='add');
assert.equal(audited.length, prior.size);
assert.equal(new Set(audited.map(a=>a.table+'.'+a.field)).size, prior.size);
assert.ok(audited.every(a=>prior.has(a.table+'.'+a.field)));
const fields = new Set(v5.tables.flatMap(t=>t.fields.map(f=>t.name+'.'+f.name)));
assert.equal(fields.size,v5.counts.fields);
assert.equal(v5.work_information.length,sw.works.length);
assert.ok(sw.works.every(w=>v5.work_information.some(x=>x.id===w.id)));
assert.ok(v5.work_information.every(w=>w.reads.concat(w.writes).every(f=>fields.has(f))));
assert.ok(v5.payload_information.every(g=>fields.has(g.container)));

assert.equal(v5.tables.length,12);
assert.equal(fields.size,134);
assert.ok(!v5.tables.some(t=>t.name==='source_object_links'));
assert.ok(fields.has('platform_objects.source_id'));
assert.ok(v5.field_audit.filter(a=>a.table==='source_object_links').every(a=>a.candidate_field===null&&a.replacement_fields.every(f=>fields.has(f))));
function runBindingModels(){
 const cases=[];function test(id,description,fn){try{const pass=!!fn();cases.push({id,description,pass,verdict:pass?"pass":"fail"})}catch(e){cases.push({id,description,pass:false,verdict:"fail",error:String(e)})}}
 function state(){return {objects:{o1:{owner:"a",source:null,head:"initial",shared:false},o2:{owner:"a",source:null,head:"initial",shared:false},profile:{owner:"a",source:null,head:"initial",shared:true}},sources:{s1:{owner:"a",active:true},s2:{owner:"a",active:true},s3:{owner:"b",active:true}},receipts:{},events:[],effects:[]}}
 function apply(s,c){const known=s.receipts[c.key];if(known)return known.digest===c.digest?known.result:"digest_mismatch";const o=s.objects[c.object],src=s.sources[c.source];if(!o||!src||o.owner!==c.owner||src.owner!==c.owner||o.shared||!src.active||o.head!==c.expected)return "rejected";if(c.action==="link"&&o.source!==null)return "conflict";if(c.action==="unlink"&&o.source!==c.source)return "rejected";const id="binding-"+(s.events.length+1);const before=o.head;o.source=c.action==="link"?c.source:null;o.head=id;s.events.push({id,previous:before,object:c.object,source:c.source,action:c.action});s.receipts[c.key]={digest:c.digest,result:id};return id}
 const cmd=(key,object="o1",source="s1",action="link",expected="initial",owner="a")=>({key,object,source,action,expected,owner,digest:[object,source,action,expected,owner].join(":")});
 test("B01","강사 원본 1개에 복수 등록물",()=>{const s=state();apply(s,cmd("k1"));apply(s,cmd("k2","o2"));return s.objects.o1.source==="s1"&&s.objects.o2.source==="s1"&&s.events.length===2});
 test("B02","같은 객체에 다른 원본 암묵 덮어쓰기 금지",()=>{const s=state(),head=apply(s,cmd("k1"));return apply(s,cmd("k2","o1","s2","link",head))==="conflict"&&s.objects.o1.source==="s1"});
 test("B03","공유 프로필 및 다른 owner 연결 금지",()=>{const s=state();return apply(s,cmd("k1","profile"))==="rejected"&&apply(s,cmd("k2","o1","s3"))==="rejected"&&s.events.length===0});
 test("B04","내부 해제 후 객체 및 외부 효과 유지",()=>{const s=state(),head=apply(s,cmd("k1"));s.effects.push({object:"o1",state:"confirmed"});apply(s,cmd("k2","o1","s1","unlink",head));return s.objects.o1.source===null&&s.effects[0].state==="confirmed"&&s.events.length===2});
 test("B05","동일 키 응답 유실 복구, 다른 digest 거절",()=>{const s=state(),c=cmd("k1"),r=apply(s,c);return apply(s,c)===r&&apply(s,{...c,digest:"other"})==="digest_mismatch"&&s.events.length===1});
 test("B06","해제 후 같은 원본 재연결 시 낡은 unlink 거절",()=>{const s=state(),a=apply(s,cmd("k1")),b=apply(s,cmd("k2","o1","s1","unlink",a));apply(s,cmd("k3","o1","s1","link",b));return apply(s,cmd("k4","o1","s1","unlink",a))==="rejected"&&s.objects.o1.source==="s1"&&s.events.length===3});
 test("B07","늦은 등록 결과가 명시 해제 덮어쓰지 않음",()=>{const s=state(),a=apply(s,cmd("k1"));apply(s,cmd("k2","o1","s1","unlink",a));s.effects.push({object:"o1",state:"confirmed"});return apply(s,cmd("late","o1","s1","link","initial"))==="rejected"&&s.objects.o1.source===null&&s.effects[0].state==="confirmed"});
 test("B08","원본 retire 이후 새 연결 차단",()=>{const s=state();s.sources.s1.active=false;return apply(s,cmd("k1"))==="rejected"&&s.objects.o1.source===null});
 return cases;
}
const cases=runBindingModels();
console.log(JSON.stringify({scope:'V5.1 static references and sequential mock binding cases; NOT PostgreSQL/platform execution',cases},null,2));
assert.ok(cases.every(c=>c.pass));
