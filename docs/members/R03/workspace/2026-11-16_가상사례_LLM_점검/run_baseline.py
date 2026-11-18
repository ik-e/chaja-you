import subprocess,json,time,tempfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
case=json.loads((r/'case.json').read_text(encoding='utf-8'))
exe=r'C:/Users/최두나/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe'
instruction="""당신은 일반 텍스트 LLM의 사건 자료 정리 baseline이다. 아래 가상 입력만 사용해 한국어로 응답하라. 도구, 셸, 파일, 웹을 사용하지 말고 응답만 생성하라. 법적 판단이나 신고 제출은 하지 않는다. 모든 사건 문장에 원문 ID를 연결하라. 사용자 직접 경험, 판매자 주장, 사용자 추측을 보존하고 미확인과 충돌을 별도로 표현하라. 날짜/금액을 임의 선택하거나 없는 사실을 추가하지 말라. 사용자가 정정하면 관련 요약/질문/검토 상태를 일관되게 갱신하고 이전 원문과 정정 이력을 남겨라. 모르는 항목은 미확인으로 두고 이미 답한 것을 다시 묻지 말라. 출력은 JSON 객체로만: summary(array of {item_id,text,source_ids,kind,confirmation,conflict,review}), materials(array), unknowns(array), questions(array), changes(array). 추가 도구·코드 실행·외부 조사는 금지한다."""
result={'case_id':case['id'],'runner':'Codex CLI noninteractive, default model, ignore-user-config, ephemeral, read-only empty temp cwd','started_at':datetime.now(timezone.utc).isoformat(),'rounds':[],'limitations':['coding-agent harness, not standalone ChatGPT UI','single case, one run per turn, no service-C output','exact backend model may not be exposed; record available metadata only']}
history=''
with tempfile.TemporaryDirectory(prefix='r03-llm-input-') as cwd:
 for idx in (1,2):
  prompt=instruction+'\n'
  if idx==1:prompt+='가상 원문 자료:\n'+json.dumps(case['sources'],ensure_ascii=False)
  else:prompt+='이전 대화:\n'+history+'\n사용자 추가 정정:\n'+case['correction']
  (r/f'prompt-{idx}.txt').write_text(prompt,encoding='utf-8')
  args=[exe,'exec','--ignore-user-config','--ephemeral','--sandbox','read-only','--skip-git-repo-check','--json','--color','never','-C',cwd,'-']
  t=time.perf_counter()
  try:
   proc=subprocess.run(args,input=prompt,text=True,encoding='utf-8',capture_output=True,timeout=150)
  except subprocess.TimeoutExpired:
   result['rounds'].append({'round':idx,'status':'timeout','elapsed_seconds':round(time.perf_counter()-t,3)})
   break
  events=[];messages=[];tool_items=[];usage=None
  for line in proc.stdout.splitlines():
   try:e=json.loads(line)
   except ValueError:continue
   if e.get('type')=='turn.completed':usage=e.get('usage')
   item=e.get('item',{})
   if e.get('type')=='item.completed' and item.get('type')=='agent_message':messages.append(item.get('text',''))
   if e.get('type')=='item.completed' and item.get('type') not in ('agent_message','reasoning'):tool_items.append(item.get('type'))
   if e.get('type') in ('error','turn.failed'):events.append(e)
  response='\n'.join(messages)
  (r/f'response-{idx}.txt').write_text(response,encoding='utf-8')
  result['rounds'].append({'round':idx,'exit_code':proc.returncode,'status':'response_received' if response else 'no_response','elapsed_seconds':round(time.perf_counter()-t,3),'response_file':f'response-{idx}.txt','prompt_file':f'prompt-{idx}.txt','usage':usage,'tool_item_types':tool_items,'errors':events,'stderr_tail':proc.stderr[-1200:] if proc.returncode else ''})
  (r/'execution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({'round':idx,'exit_code':proc.returncode,'response_chars':len(response),'tool_items':tool_items,'usage':usage},ensure_ascii=False),flush=True)
  if not response or tool_items:break
  history='사용자 자료:'+json.dumps(case['sources'],ensure_ascii=False)+'\nassistant:'+response
result['finished_at']=datetime.now(timezone.utc).isoformat()
(r/'execution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
