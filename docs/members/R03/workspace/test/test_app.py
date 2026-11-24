import io
import importlib
import pytest
from PIL import Image
from fastapi.testclient import TestClient

@pytest.fixture
def env(tmp_path,monkeypatch):
    monkeypatch.setenv('POC_DATA',str(tmp_path))
    monkeypatch.setenv('POC_RUNNER','simulator')
    monkeypatch.delenv('LLM_API_KEY',raising=False)
    import app
    importlib.reload(app)
    c=TestClient(app.app)
    csrf=c.post('/api/session').json()['csrf']
    c.headers['x-csrf-token']=csrf
    return c,app

def setup(c,price='300000',image=True):
    stream=io.BytesIO(); Image.new('RGB',(652,488),'navy').save(stream,format='PNG')
    data={'source_text':'테스트용 기존 공고입니다. '*15,'monthly_price':price,'sessions_per_month':'4','minutes_per_session':'90','location_public':'테스트 지역'}
    r=c.post('/api/v1/lessons',data=data,files={'images':('sample.png',stream.getvalue(),'image/png')} if image else None)
    lid=r.json()['lesson_id']; p=c.post(f'/api/v1/lessons/{lid}/prepare',json={}).json()
    f=p['fields']; f.update(service_title='테스트 음악 레슨 등록 공고',process='사용자가 제공한 수업 진행 절차입니다. '*5,requirements='사용자가 제공한 수업 준비 사항입니다. '*5,recruitment_type='모의 개인 수업',category_1='모의',category_2='음악',category_3='레슨')
    for v in f['packages'].values(): v.update(title='기본 과정',description='동일 조건 모의 수업',work_days=30,revision_count=0,materials_included=False,classroom_included=True)
    p=c.patch(f'/api/v1/lessons/{lid}/preview',json={'preview_version':p['preview_version'],'fields':f}).json()
    return lid,p

def job(c,lid,p,fault='none',key='one'):
    a=c.post(f'/api/v1/lessons/{lid}/approve',json={'preview_version':p['preview_version']}).json()
    body={'lesson_id':lid,'preview_version':p['preview_version'],'approval_token':a.get('approval_token'),'mode':'mock','target':'mock_kmong','fault':fault}
    return c.post('/api/v1/jobs',json=body,headers={'Idempotency-Key':key}),body

def test_initial_preview_contains_classroom_choice(env):
    c,_=env
    r=c.post('/api/v1/lessons',data={'source_text':'테스트 레슨 소개','monthly_price':'300000','sessions_per_month':'4','minutes_per_session':'90','location_public':'테스트 지역'})
    lid=r.json()['lesson_id']
    p=c.post(f'/api/v1/lessons/{lid}/prepare',json={}).json()
    assert all('classroom_included' in package and package['classroom_included'] is None for package in p['fields']['packages'].values())

def test_normal_receipt_and_prices(env):
    c,a=env; lid,p=setup(c); r,b=job(c,lid,p)
    j=c.get('/api/v1/jobs/'+r.json()['job_id']).json()
    assert j['status']=='mock_submitted'
    assert j['skyvern_run_status'] is None
    assert j['evidence']['mock_submission_id']
    assert all(x['price_krw_vat_included']==300000 and x['sessions']==4 and x['minutes_per_session']==90 for x in j['evidence']['fields']['packages'].values())
    assert j['fields']['trial_package_price'] is None

@pytest.mark.parametrize('fault,state',[('upload_failure','failed'),('session_expired','needs_action'),('response_lost','mock_submitted'),('no_receipt','unknown')])
def test_faults(env,fault,state):
    c,a=env; lid,p=setup(c); r,b=job(c,lid,p,fault)
    j=c.get('/api/v1/jobs/'+r.json()['job_id']).json(); assert j['status']==state
    if fault=='response_lost': assert 'unknown' in [e['status'] for e in j['events']]
    r2=c.post('/api/v1/jobs',json=b,headers={'Idempotency-Key':'two'}); assert r2.status_code==409

def test_idempotency(env):
    c,a=env; lid,p=setup(c); r,b=job(c,lid,p)
    r2=c.post('/api/v1/jobs',json=b,headers={'Idempotency-Key':'one'})
    assert r.json()['job_id']==r2.json()['job_id']

def test_live_blocked(env):
    c,a=env
    assert c.post('/api/v1/jobs',json={'mode':'live','target':'https://kmong.com'}).status_code==403

def test_stale_approval(env):
    c,a=env; lid,p=setup(c)
    token=c.post(f'/api/v1/lessons/{lid}/approve',json={'preview_version':p['preview_version']}).json()['approval_token']
    c.patch(f'/api/v1/lessons/{lid}/preview',json={'preview_version':p['preview_version'],'fields':p['fields']})
    r=c.post('/api/v1/jobs',headers={'Idempotency-Key':'one'},json={'lesson_id':lid,'preview_version':p['preview_version'],'approval_token':token,'mode':'mock','target':'mock_kmong'})
    assert r.status_code==409

@pytest.mark.parametrize('condition',['price','package_price','required','image'])
def test_missing_and_conflicts(env,condition):
    c,a=env; lid,p=setup(c,price='' if condition=='price' else '300000',image=condition!='image')
    if condition in ['package_price','required']:
        v=p['fields']['packages']['PREMIUM']; v['price_krw_vat_included']=290000 if condition=='package_price' else 300000
        if condition=='required': v['work_days']=None
        p=c.patch(f'/api/v1/lessons/{lid}/preview',json={'preview_version':p['preview_version'],'fields':p['fields']}).json()
    assert not p['can_submit']
    assert c.post(f'/api/v1/lessons/{lid}/approve',json={'preview_version':p['preview_version']}).status_code==422

def test_forged_image(env):
    c,a=env
    r=c.post('/api/v1/lessons',data={'source_text':'test'},files={'images':('x.png',b'not an image','image/png')})
    assert r.status_code==415

def test_other_session_cannot_read(env):
    c,a=env; lid,p=setup(c); r,b=job(c,lid,p)
    other=TestClient(a.app); other.post('/api/session')
    assert other.get('/api/v1/jobs/'+r.json()['job_id']).status_code==404
