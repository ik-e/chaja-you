import os
import json
from urllib.parse import urlparse

def leaves(value,path=()):
    for key,item in value.items():
        if isinstance(item,dict): yield from leaves(item,path+(key,))
        else: yield path+(key,),item

async def run_skyvern(job, data_dir):
    from skyvern import Skyvern
    base=os.environ.get('POC_BASE_URL','http://127.0.0.1:8765')
    u=urlparse(base)
    if u.hostname not in ['127.0.0.1','localhost'] or u.scheme!='http' or u.path not in ['', '/']:
        raise ValueError('Only local mock origin allowed')
    job['runner_stage']='initialize'
    client=Skyvern.local()
    try:
        job['runner_stage']='launch_browser'
        browser=await client.launch_local_browser()
        job['runner_stage']='open_page'
        page=await browser.new_page()
        job['runner_stage']='navigate_mock_form'
        await page.goto(base.rstrip('/')+'/mock-kmong/'+job['job_id'])
        job['runner_stage']='fill_fields'
        for i,(path,value) in enumerate(leaves(job['fields'])):
            if isinstance(value,bool): await page.select_option(f'#field_{i}',value=str(value).lower())
            else: await page.fill(f'#field_{i}',value='' if value is None else str(value))
        job['runner_stage']='upload_image'
        # Skyvern's upload_file expects a URL; this local PoC keeps the image on disk.
        await page.locator('#image').set_input_files(str((data_dir/job['fields']['cover_asset_id']).resolve()))
        job['runner_stage']='submit_mock_form'
        submit_url=base.rstrip('/')+'/mock-kmong/'+job['job_id']+'/submit'
        async with page.expect_response(lambda response: response.url == submit_url, timeout=15000) as response_info:
            await page.click('#submit')
        response=await response_info.value
        job['mock_http_status']=response.status
        if response.status != 200:
            raise RuntimeError('mock form rejected the submission')
        job['runner_stage']='finished'
    finally:
        await client.aclose()
