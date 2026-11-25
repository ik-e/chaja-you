export function check(p,d,l){
 const errors=[];const assert=(ok,id)=>{if(!ok)errors.push(id)};const names=new Set(d.entities.map(e=>e[0]));const fields=new Set(d.api.map(a=>a[0]));const roles=new Set([...Object.keys(l.ownership),"BROWSER","PLATFORM"]);
 assert(names.size===d.entities.length,"entity_duplicate");assert(fields.size===d.api.length,"api_duplicate");
 for(const a of d.api){assert(a[3] in d.schemas&&a[4] in d.schemas,"schema_missing:"+a[0]);assert(roles.has(a[5]),"api_owner:"+a[0]);assert(!/cancel|resume|rebind|reconcile|stop/.test(a[2]),"obsolete_api:"+a[0]);}
 for(const e of d.entities)assert(roles.has(e[3]),"entity_owner:"+e[0]);
 for(const a of d.ports){for(const r of a[1].split("/"))assert(roles.has(r),"port_caller:"+a[0]);assert(roles.has(a[2]),"port_provider:"+a[0]);}
 assert(l.platform_contract&&l.platform_contract.plan.includes("결정적"),"fixed_plan");
 for(const pr of p.profiles){
 const keys=new Set(pr.fields.map(f=>f[0]));assert(keys.size===pr.fields.length,"duplicate_field:"+pr.platform);assert(pr.live_allowed===false,"live_allowed:"+pr.platform);
 const steps=pr.steps,ids=new Set(steps.map(s=>s[0]));assert(ids.size===steps.length,"duplicate_step:"+pr.platform);assert(steps.at(-2)[2]==="read"&&steps.at(-1)[2]==="mutation","precommit_read:"+pr.platform);assert(steps.filter(s=>/submit_once|save_once/.test(s[1])).length===1,"commit_count:"+pr.platform);
 for(const s of steps){const bind=s[3];if(!["account+target","target+approval","all approved fields","all approved fields+asset"].includes(bind))for(const k of bind.split(","))assert(keys.has(k),"unknown_binding:"+pr.platform+":"+k);assert(s[4].length>0,"missing_observation:"+s[0]);}
 assert(pr.goal.required.includes("target_ref")&&pr.goal.required.includes("payload_digest"),"goal_binding:"+pr.platform);
 if(pr.platform==="kmong")assert(keys.has("main_image")&&pr.goal.required.includes("asset_digest"),"kmong_asset");
 if(pr.platform==="soomgo")assert(!keys.has("main_image"),"soomgo_fake_asset");
 }
 return errors;
}
