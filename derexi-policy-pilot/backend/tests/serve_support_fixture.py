"""Disposable final-integration UI. Importing does not execute old evidence writers."""
import sys
import os
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import serve_week10_fixture as prior
import incident_assistance as support
from models import User, TechnicalRoute
from fastapi import Depends
from security import require_admin

os.environ['DEREXI_APPROVED_MAILBOXES']=json.dumps({
    'security':{'address':'security@example.invalid','label':'Security service desk','channel':'security'},
    'it':{'address':'it@example.invalid','label':'IT service desk','channel':'it'}})
os.environ['DEREXI_OUTBOUND_EMAIL']='off'
os.environ['DEREXI_INCIDENT_AI']='off'
mode={'result':'disabled'}
class MockTransport:
    def send(self,*args):return mode['result']
def adapter():return support.DisabledTransport() if mode['result']=='disabled' else MockTransport()
support.transport=adapter
app=prior.fixture.main.app
with prior.fixture.factory() as db:
    departments={u.department_id for u in db.query(User) if u.department_id}
    for dept in departments:
        for channel in ('security','it'):
            db.add(TechnicalRoute(department_id=dept,channel=channel,mailbox_key=channel,enabled=True))
    db.commit()

@app.post('/__fixture/delivery/{result}')
def delivery_mode(result:str,actor=Depends(require_admin)):
    if result not in {'disabled','accepted','retryable','unknown'}:raise prior.fixture.main.HTTPException(422,'Unknown fixture mode')
    mode['result']=result
    return {'mock':True}

if __name__=='__main__':
    import uvicorn
    print('ISOLATED FICTIONAL FIXTURE: SQLite; provider/feed/SMTP mocked or OFF; no Supabase',flush=True)
    uvicorn.run(app,host='127.0.0.1',port=8041,proxy_headers=False,access_log=False)
