import hashlib
import html
import io
import json
import os
import secrets
import sqlite3
import time
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image

ROOT = Path(__file__).parent
DATA = Path(os.environ.get('POC_DATA', ROOT / 'data'))
DATA.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='R03 모의 레슨 등록 PoC')
TIERS = ['STANDARD', 'DELUXE', 'PREMIUM']

def conn():
    c = sqlite3.connect(DATA / 'poc.sqlite', timeout=30)
    c.execute('CREATE TABLE IF NOT EXISTS records (kind TEXT, id TEXT, value TEXT, PRIMARY KEY(kind,id))')
    return c

def put(kind, key, value):
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO records VALUES (?,?,?)', (kind,key,json.dumps(value,ensure_ascii=False)))

def get(kind, key):
    with conn() as c:
        row = c.execute('SELECT value FROM records WHERE kind=? AND id=?',(kind,key)).fetchone()
    return json.loads(row[0]) if row else None

def uid(): return uuid.uuid4().hex

def user(request):
    token = request.cookies.get('poc_session')
    session = get('sessions', token or '')
    if not session or session['expires'] < time.time(): raise HTTPException(401,'로컬 시험 세션을 시작하세요')
    if request.method != 'GET' and request.headers.get('x-csrf-token') != session['csrf']:
        raise HTTPException(403,'CSRF 확인 실패')
    return session

def own(request, kind, key):
    u = user(request)
    value = get(kind,key)
    if not value or value.get('owner') != u['owner']: raise HTTPException(404,'찾을 수 없음')
    return value

def event(job, status, code=None):
    job['status']=status
    job['error_code']=code
    job['updated_at']=time.time()
    job.setdefault('events',[]).append({'at':time.time(),'status':status,'code':code})
    put('jobs',job['job_id'],job)

def validate(fields, lesson):
    errors=[]
    for name, lo, hi in [('service_title',10,30),('service_description',100,20000),('process',50,20000),('requirements',50,20000)]:
        value=fields.get(name)
        if not isinstance(value,str) or not lo<=len(value)<=hi: errors.append(name)
    for name in ['location_public','recruitment_type','category_1','category_2','category_3']:
        if not fields.get(name): errors.append(name)
    if fields.get('location_public') != lesson.get('location_public'): errors.append('location_mismatch')
    if not lesson.get('asset_ids') or fields.get('cover_asset_id') not in lesson['asset_ids']: errors.append('cover_asset_id')
    packages=fields.get('packages',{})
    if not isinstance(packages,dict) or set(packages)!=set(TIERS): return errors+['packages']
    for tier in TIERS:
        p=packages[tier]
        if not isinstance(p,dict): errors.append(tier); continue
        for key, expected in [('price_krw_vat_included',300000),('sessions',4),('minutes_per_session',90)]:
            if type(p.get(key)) is not int or p[key]!=expected: errors.append(tier+'.'+key)
        for key,limit in [('title',20),('description',60)]:
            if not isinstance(p.get(key),str) or not 1<=len(p[key])<=limit: errors.append(tier+'.'+key)
        for key in ['work_days','revision_count']:
            if type(p.get(key)) is not int or p[key] < (1 if key=='work_days' else 0): errors.append(tier+'.'+key)
        for key in ['materials_included','classroom_included']:
            if type(p.get(key)) is not bool: errors.append(tier+'.'+key)
    if [lesson.get(k) for k in ['monthly_price','sessions_per_month','minutes_per_session']] != [300000,4,90]: errors.append('source_price')
    if fields.get('trial_package_price') is not None: errors.append('trial_package_price')
    return sorted(set(errors))

@app.get('/',response_class=HTMLResponse)
def index(): return (ROOT/'index.html').read_text(encoding='utf-8')

@app.post('/api/session')
def session():
    from fastapi.responses import JSONResponse
    token=secrets.token_urlsafe(32)
    s={'owner':uid(),'csrf':secrets.token_urlsafe(32),'expires':time.time()+86400}
    put('sessions',token,s)
    response=JSONResponse({'csrf':s['csrf'], 'runner':os.environ.get('POC_RUNNER','simulator')})
    response.set_cookie('poc_session',token,httponly=True,samesite='strict',max_age=86400)
    return response

@app.post('/api/v1/lessons',status_code=201)
async def lesson(request:Request, source_text:str=Form(...), monthly_price:int|None=Form(None), sessions_per_month:int|None=Form(None), minutes_per_session:int|None=Form(None), location_public:str=Form(''), images:list[UploadFile]=File(default=[])):
    u=user(request)
    if not source_text.strip(): raise HTTPException(400,'원본 공고 필요')
    if len(images)>4: raise HTTPException(400,'대표 이미지 최대 4장')
    assets=[]
    for image in images:
        raw=await image.read(5*1024*1024+1)
        if len(raw)>5*1024*1024: raise HTTPException(413,'이미지당 최대 5MB')
        try:
            im=Image.open(io.BytesIO(raw)); fmt=im.format; im.verify()
            if fmt not in ['PNG','JPEG']: raise ValueError()
        except Exception: raise HTTPException(415,'정상 PNG/JPG 이미지 필요')
        aid=hashlib.sha256(raw).hexdigest()
        (DATA/aid).write_bytes(raw)
        assets.append(aid)
    lid=uid()
    obj={'lesson_id':lid,'owner':u['owner'],'source_text':source_text,'monthly_price':monthly_price,'sessions_per_month':sessions_per_month,'minutes_per_session':minutes_per_session,'location_public':location_public,'asset_ids':assets,'source_version':1,'preview_version':0}
    put('lessons',lid,obj)
    return obj

@app.post('/api/v1/lessons/{lid}/prepare')
async def prepare(lid:str,request:Request):
    lesson=own(request,'lessons',lid); body=await request.json()
    if body.get('target','mock_kmong')!='mock_kmong': raise HTTPException(403,'모의 대상만 지원')
    if body.get('source_version',1)!=lesson['source_version']: raise HTTPException(409,'원본 버전 불일치')
    fields={'service_title':'','service_description':lesson['source_text'],'process':'','requirements':'','location_public':lesson['location_public'],'recruitment_type':'','category_1':'','category_2':'','category_3':'','cover_asset_id':next(iter(lesson['asset_ids']),None),'trial_package_price':None,'packages':{t:{'title':'','description':'','price_krw_vat_included':lesson['monthly_price'],'sessions':lesson['sessions_per_month'],'minutes_per_session':lesson['minutes_per_session'],'work_days':None,'revision_count':None,'materials_included':None,'classroom_included':None} for t in TIERS}}
    extraction='manual_no_model'
    if os.environ.get('LLM_BASE_URL') and os.environ.get('LLM_API_KEY'):
        async with httpx.AsyncClient(timeout=60) as client:
            response=await client.post(os.environ['LLM_BASE_URL'].rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+os.environ['LLM_API_KEY']},json={'model':os.environ.get('LLM_MODEL',''),'messages':[{'role':'system','content':'Return JSON with service_title, service_description, process, requirements. Extract ONLY facts from source. Missing facts must be empty strings. Never invent benefits or prices.'},{'role':'user','content':lesson['source_text']}],'response_format':{'type':'json_object'}})
            response.raise_for_status()
            extracted=json.loads(response.json()['choices'][0]['message']['content'])
            for k in ['service_title','service_description','process','requirements']:
                if isinstance(extracted.get(k),str): fields[k]=extracted[k]
            extraction='llm_unapproved'
    return save_preview(lesson,fields,extraction)

def save_preview(lesson,fields,extraction):
    lesson['preview_version']+=1
    put('lessons',lesson['lesson_id'],lesson)
    errors=validate(fields,lesson)
    p={'lesson_id':lesson['lesson_id'],'owner':lesson['owner'],'preview_version':lesson['preview_version'],'fields':fields,'missing_fields':errors,'can_submit':not errors,'status':'needs_action' if errors else 'prepared','extraction':extraction,'calculated_hourly_rate':50000 if not errors else None}
    put('previews',lesson['lesson_id'],p)
    return p

@app.patch('/api/v1/lessons/{lid}/preview')
async def edit(lid:str,request:Request):
    lesson=own(request,'lessons',lid); body=await request.json()
    if body.get('preview_version')!=lesson['preview_version']: raise HTTPException(409,'미리보기 버전 불일치')
    return save_preview(lesson,body['fields'],'user_edited')

@app.post('/api/v1/lessons/{lid}/approve')
async def approve(lid:str,request:Request):
    p=own(request,'previews',lid); body=await request.json()
    if body.get('preview_version')!=p['preview_version']: raise HTTPException(409,'승인 버전 불일치')
    if not p['can_submit']: raise HTTPException(422,p['missing_fields'])
    token=secrets.token_urlsafe(32)
    put('approvals',token,{'owner':p['owner'],'lesson_id':lid,'version':p['preview_version'],'at':time.time(),'scope':'one_listing_one_submission'})
    return {'approval_token':token}

@app.post('/api/v1/jobs',status_code=202)
async def jobs(request:Request,background:BackgroundTasks):
    u=user(request); b=await request.json()
    if b.get('mode')!='mock' or b.get('target')!='mock_kmong': raise HTTPException(403,'실제 사이트 등록 차단')
    key=request.headers.get('Idempotency-Key')
    if not key: raise HTTPException(400,'Idempotency-Key 필요')
    approval=get('approvals',b.get('approval_token',''))
    p=own(request,'previews',b['lesson_id'])
    if not approval or approval['owner']!=u['owner'] or approval['lesson_id']!=b['lesson_id'] or approval['version']!=p['preview_version'] or b.get('preview_version')!=p['preview_version']: raise HTTPException(409,'새 미리보기 승인 필요')
    if validate(p['fields'],get('lessons',b['lesson_id'])): raise HTTPException(422,'검증 실패')
    with conn() as c:
        c.execute('BEGIN IMMEDIATE')
        existing=[json.loads(r[0]) for r in c.execute("SELECT value FROM records WHERE kind='jobs'")]
        for j in existing:
            if j['owner']==u['owner'] and j['idempotency_key']==key:
                if j['lesson_id']!=b['lesson_id'] or j['preview_version']!=p['preview_version']: raise HTTPException(409,'멱등성 키 재사용 충돌')
                return j
            if j['lesson_id']==b['lesson_id']: raise HTTPException(409,'기존 작업 존재: 재제출 금지')
        job={'job_id':uid(),'owner':u['owner'],'lesson_id':b['lesson_id'],'preview_version':p['preview_version'],'idempotency_key':key,'fields':p['fields'],'approved_at':approval['at'],'status':'queued','fault':b.get('fault','none'),'runner':os.environ.get('POC_RUNNER','simulator'),'events':[],'skyvern_run_status':None,'evidence':None}
        if job['fault'] not in ['none','upload_failure','session_expired','response_lost','no_receipt']: raise HTTPException(400,'알 수 없는 오류 옵션')
        c.execute('INSERT INTO records VALUES (?,?,?)',('jobs',job['job_id'],json.dumps(job)))
    background.add_task(execute,job['job_id'])
    return job

def receipt(job,fields,asset):
    if fields!=job['fields'] or asset!=fields['cover_asset_id']: raise HTTPException(422,'승인 내용/이미지 불일치')
    old=get('receipts',job['job_id'])
    if old: return old
    r={'mock_submission_id':uid(),'fields':fields,'asset_id':asset}
    put('receipts',job['job_id'],r)
    return r

async def execute(jid):
    job=get('jobs',jid); event(job,'running')
    if job['fault'] in ['upload_failure','session_expired']:
        event(job,'failed' if job['fault']=='upload_failure' else 'needs_action',job['fault']); return
    try:
        if job['runner']=='skyvern':
            from runner import run_skyvern
            await run_skyvern(job,DATA)
            job['skyvern_run_status']='completed'
        elif job['runner']=='simulator':
            if job['fault']!='no_receipt': receipt(job,job['fields'],job['fields']['cover_asset_id'])
            job['simulator_status']='completed'
        else: raise ValueError('runner')
        if job['fault']=='response_lost': event(job,'unknown','response_lost')
        r=get('receipts',jid)
        if r and r['fields']==job['fields'] and r['asset_id']==job['fields']['cover_asset_id']:
            job['evidence']={'type':'mock_receipt_verified',**r}
            event(job,'mock_submitted')
        else: event(job,'unknown','receipt_missing_or_mismatch')
    except Exception as exc:
        job['runner_error_type']=type(exc).__name__
        event(job,'unknown','runner_error_requires_receipt_check')

@app.get('/api/v1/jobs/{jid}')
def result(jid:str,request:Request): return own(request,'jobs',jid)

@app.get('/mock-kmong/{jid}',response_class=HTMLResponse)
def mock_page(jid:str):
    job=get('jobs',jid)
    if not job: raise HTTPException(404)
    from runner import leaves
    controls=[]
    for i,(path,value) in enumerate(leaves(job['fields'])):
        label=html.escape('.'.join(path))
        if isinstance(value,bool):
            control=f'<select id="field_{i}" data-path="{label}"><option value="true">포함</option><option value="false">미포함</option></select>'
        else: control=f'<textarea id="field_{i}" data-path="{label}"></textarea>'
        controls.append(f'<label>{label}{control}</label>')
    return (ROOT/'mock.html').read_text(encoding='utf-8').replace('__JOB__',jid).replace('__FIELDS__',''.join(controls)).replace('__SHAPE__',json.dumps(job['fields'],ensure_ascii=False).replace('<','\\u003c'))

@app.post('/mock-kmong/{jid}/submit')
async def mock_submit(jid:str,payload:str=Form(...),image:UploadFile=File(...)):
    job=get('jobs',jid)
    if not job or job['status']!='running': raise HTTPException(409)
    data=await image.read(5*1024*1024+1)
    return receipt(job,json.loads(payload),hashlib.sha256(data).hexdigest())
