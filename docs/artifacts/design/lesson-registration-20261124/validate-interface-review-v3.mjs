export function schemaAudit(S,C){
const defs=S.$defs;const declared=new Set(Object.keys(defs)),refs=[],unhandled=new Set();const supported=new Set(["$ref","type","enum","const","properties","required","additionalProperties","items","minItems","maxItems","uniqueItems","minLength","maxLength","pattern","minimum","maximum","format","oneOf","anyOf"]);
function walk(s,path){if(typeof s==="boolean")return;if(s.$ref)refs.push({path,ref:s.$ref,resolved:s.$ref.startsWith("#/$defs/")&&declared.has(s.$ref.slice(8))});for(const k of Object.keys(s))if(!supported.has(k))unhandled.add(k);for(const [k,v] of Object.entries(s.properties??{}))walk(v,path+"."+k);for(const k of ["items","additionalProperties"])if(s[k]&&typeof s[k]==="object")walk(s[k],path+"."+k);for(const k of ["anyOf","oneOf"])for(const [i,v] of (s[k]??[]).entries())walk(v,path+"."+k+"["+i+"]");}
for(const [name,s] of Object.entries(defs))walk(s,name);
return {definitions:declared.size,references:refs.length,unresolved:refs.filter(x=>!x.resolved),unsupported_keywords:[...unhandled],route_missing:C.routes.flatMap(r=>[r.input,r.output].filter(t=>t&&!declared.has(t)).map(t=>[r.id,t])),port_missing:C.ports.flatMap(p=>[p.input,p.output].filter(t=>t!=="selector:string"&&!declared.has(t)).map(t=>[p.id,t])),duplicate_routes:C.routes.length-new Set(C.routes.map(x=>x.method+" "+x.path)).size,root_has_validation:!!(S.$ref||S.type||S.anyOf||S.oneOf)};
}

export function validate(S,name,value){
const d=S.$defs;
function test(s,v,p){if(s===true)return[];if(s===false)return[p+" false schema"];if(s.$ref)return test(d[s.$ref.slice(8)],v,p);
const errors=[];if(s.anyOf&&!s.anyOf.some(x=>!test(x,v,p).length))errors.push(p+" anyOf");if(s.oneOf&&s.oneOf.filter(x=>!test(x,v,p).length).length!==1)errors.push(p+" oneOf");if(s.const!==undefined&&JSON.stringify(s.const)!==JSON.stringify(v))errors.push(p+" const");if(s.enum&&!s.enum.some(x=>JSON.stringify(x)===JSON.stringify(v)))errors.push(p+" enum");
const ty=Array.isArray(v)?"array":v===null?"null":typeof v;
if(s.type&&!(s.type==="integer"?Number.isInteger(v):ty===s.type))return [...errors,p+" type"];
if(ty==="object"){for(const k of s.required??[])if(!Object.hasOwn(v,k))errors.push(p+"."+k+" required");for(const [k,x] of Object.entries(v)){if(s.properties&&Object.hasOwn(s.properties,k))errors.push(...test(s.properties[k],x,p+"."+k));else if(s.additionalProperties===false)errors.push(p+"."+k+" additional");else if(typeof s.additionalProperties==="object")errors.push(...test(s.additionalProperties,x,p+"."+k));}}
if(ty==="array"){if(s.minItems!==undefined&&v.length<s.minItems)errors.push(p+" minItems");if(s.maxItems!==undefined&&v.length>s.maxItems)errors.push(p+" maxItems");if(s.uniqueItems&&new Set(v.map(x=>JSON.stringify(x))).size!==v.length)errors.push(p+" uniqueItems");if(s.items)v.forEach((x,i)=>errors.push(...test(s.items,x,p+"["+i+"]")));}
if(ty==="string"){if(s.minLength!==undefined&&[...v].length<s.minLength)errors.push(p+" minLength");if(s.maxLength!==undefined&&[...v].length>s.maxLength)errors.push(p+" maxLength");if(s.pattern&&!new RegExp(s.pattern).test(v))errors.push(p+" pattern");if(s.format==="date-time"&&(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(v)||!Number.isFinite(Date.parse(v))))errors.push(p+" date-time");}
if(ty==="number"){if(s.minimum!==undefined&&v<s.minimum)errors.push(p+" minimum");if(s.maximum!==undefined&&v>s.maximum)errors.push(p+" maximum");}return errors;
}return test(d[name],value,"$");
}

export function cases(S){
const h="a".repeat(64),time="2026-11-24T00:00:00Z",profile={platform:"kmong",object_kind:"service_listing",version:"v1",digest:h,environment:"mock"},asset={asset_id:"asset-1",digest:h,mime:"image/png",bytes:100,width:652,height:488,rights_confirmed:true},target={environment:"mock",platform:"kmong",external_account_ref:"account-A",object_kind:"service_listing",slot_ref:"slot-A"},km={title:"음악 레슨 초보자 맞춤 수업",category:"music",description:"수업 내용 ".repeat(21),delivery:"in_person",region:"서울",packages:[{minutes_per_session:90,sessions_per_period:4,period:"month",total_price_krw:250000},{minutes_per_session:180,sessions_per_period:4,period:"month",total_price_krw:400000},{minutes_per_session:270,sessions_per_period:4,period:"month",total_price_krw:500000}],vat_included:false,process:"단계별 수업 진행 ".repeat(10),preparation:"준비사항 안내 ".repeat(10),main_image:asset},sg={category:"midi",daw:["logic"],goals:["hobby"],keyboard:"yes",ages:["20s"],genders:["male"],format:["individual"],location_mode:["studio"]},prep={ready:true,values:km,issues:[],provenance:[{field:"packages",kind:"source",refs:["source-1"]}]},rv={registration_id:"reg-1",source_id:"source-1",revision:3,support:"supported",profile_ref:profile,preparation:prep,auth:{state:"verified",generation:2,account_label:"test"},job_state:null},scope={registration_id:"reg-1",source_id:"source-1",revision:3,profile_ref:profile,values:km,provenance:prep.provenance,assets:[asset],target,procedure_ids:["K1","K2","K3","K4","K5"],goal_kind:"mock_listing_receipt"},accepted={scope,review_digest:h,accepted_at:time,owner_ref:"owner-1",request_key:"key-1"},goal={goal_kind:"mock_listing_receipt",target,payload_digest:h,external_ref:"receipt-1",asset_digest:h,evidence_ref:"ev-1",environment:"mock"};
const omit=(o,k)=>Object.fromEntries(Object.entries(o).filter(([x])=>x!==k));
const data=[
["P01","KmongValues",km,true,"synthetic exact 90/180/270 min and amounts, VAT false"],
["P02","SoomgoValues",sg,true,"no fake image"],
["P03","StartInput",{expected_revision:3,review_digest:h,approved:true,request_key:"key-1"},true,"one explicit start"],
["P04","AuthCommand",{action:"finish",expected_revision:3,generation:2},true,"generation-bound finish"],
["P05","ExecuteInput",{accepted,connection:{connection_ref:"connection-A",generation:3,account_ref:"account-A"}},true,"accepted scope plus runtime connection"],
["P06","GoalObservation",goal,true,"valid mock goal shape"],
["P07","RegistrationView",rv,true,"valid prestart review shape"],
["N01","KmongValues",{...km,packages:[{...km.packages[0],total_price_krw:"250000"}]},false,"price string rejected"],
["N02","KmongValues",omit(km,"vat_included"),false,"missing VAT rejected"],
["N03","SoomgoValues",{...sg,main_image:asset},false,"foreign field rejected"],
["N04","StartInput",{expected_revision:3,review_digest:h,approved:false,request_key:"key-1"},false,"no approval"],
["N05","StartInput",{expected_revision:3,review_digest:"fake",approved:true,request_key:"key-1"},false,"digest shape"],
["N06","AuthCommand",{action:"finish",expected_revision:3},false,"generation required"],
["N07","AuthCommand",{action:"cancel",expected_revision:3,generation:2},false,"no cancel"],
["N08","ProfileRef",{...profile,environment:"live"},false,"no live"],
["N09","SoomgoValues",{...sg,daw:["logic","logic"]},false,"duplicate enum options"],
["N10","RegistrationInput",{source_id:"s",selector:"kmong",steps:["arbitrary"]},false,"client cannot choose steps"],
["N11","SourceInput",{raw_text:"sample",owner_id:"other"},false,"owner not supplied by client"],
["S01","KmongValues",omit(km,"region"),false,"semantic S03 conditional region, separate check required"],
["S02","KmongValues",{...km,main_image:{...asset,width:1,rights_confirmed:false}},false,"semantic S03 rights/dimensions"],
["S03","Preparation",{...prep,issues:[{issue_id:"i",field:"packages",code:"conflict",message:"conflict",blocking:true}]},false,"semantic S02 blocking issue"],
["S04","RegistrationView",{...rv,job_state:"done"},false,"semantic S12 terminal result required"],
["S05","RegistrationView",{...rv,support:"unsupported"},false,"semantic S12 unsupported not ready"],
["S06","PreparationEdit",{expected_revision:3},false,"semantic S11 requires change"],
["S07","GoalObservation",omit(goal,"asset_digest"),false,"semantic S08 Kmong proof needs asset"],
["S08","ExecuteInput",{accepted,connection:{connection_ref:"connection-other",generation:3,account_ref:"account-B"}},false,"semantic S05/S07 account binding"],
["S09","SourceInput",{raw_text:""},false,"semantic S01 no content"],
["S10","Value",9007199254740992,false,"semantic S10 safe integers"],
["G01","ProfileRef",{platform:"kmong",object_kind:"service_configuration",version:"v1",digest:h,environment:"mock"},false,"registry pair validation, not schema"],
["G02","ProfileRef",{platform:"third_supported",object_kind:"class",version:"v1",digest:h,environment:"mock"},true,"C02 expansion requires common schema change despite registry"],
["G03","AuthOutput",{auth:{state:"verified",generation:2},target:{identity:target,status:"new",evidence_ref:"e",account_label:"test"}},true,"verified auth output contains no connection_ref"],
["G04","ExecuteInput",{accepted,connection:{connection_ref:"connection-other",generation:3,account_ref:"account-A"}},false,"same account, different runtime connection cannot compare against AcceptedScope"],
["G05","GoalObservation",goal,true,"no field distinguishes readback from submit response"],
["G06","ExecutionReport",{observations:[{operation_id:"o",step_id:"K5",verdict:"confirmed",evidence_refs:[],observed_at:time}]},false,"confirmed effect without evidence accepted by shape; trusted evidence semantic guard"],
["G07","Result",{goal_verdict:"confirmed",environment:"mock",effects:[],evidence:[]},false,"success shape lacks evidence; semantic rule requires proof"]
];
return data.map(([id,def,value,expected,why])=>{const errors=validate(S,def,value);return {id,def,expected,actual:errors.length===0,match:expected===(errors.length===0),why,errors};});
}
