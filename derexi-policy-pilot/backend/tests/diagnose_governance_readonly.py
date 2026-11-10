"""Read-only diagnosis of local HTTP failure and live schema dependencies."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from sqlalchemy import create_engine,text
from database import DATABASE_URL
r={'http':[],'schema':{},'mode':'GETs plus local token issuance; SELECT-only database transaction'}
try:
 with httpx.Client(base_url='http://127.0.0.1:8000',timeout=12,trust_env=False) as c:
  cfg=c.get('/auth/config');r['http'].append({'path':'/auth/config','status':cfg.status_code,'dev_auth':cfg.json().get('dev_auth')})
  owner=next(x for x in cfg.json()['identities'] if x['role']=='Policy Owner')
  token=c.post('/dev-auth/token',json={'user_id':owner['id']});assert token.status_code==200
  for path in ('/me','/governance/owners','/governance/drafts'):
   res=c.get(path,headers={'Authorization':'Bearer '+token.json()['access_token']})
   item={'path':path,'status':res.status_code}
   if path=='/me':item['role']=res.json().get('role')
   if res.status_code>=400:item['detail']=res.json().get('detail')
   r['http'].append(item)
except Exception as e:r['http_error']=type(e).__name__
engine=create_engine(DATABASE_URL,connect_args={'connect_timeout':8,'options':'-c default_transaction_read_only=on -c statement_timeout=8000'})
try:
 with engine.connect() as c:
  c.execute(text('SET TRANSACTION READ ONLY'));assert c.execute(text('SHOW transaction_read_only')).scalar()=='on'
  for name in ('governance_drafts','governance_events','clarification_requests','users','policy_versions'):
   r['schema'][name]=c.execute(text('SELECT to_regclass(:table) IS NOT NULL'),{'table':'public.'+name}).scalar()
  c.rollback()
except Exception as e:r['schema_error']=type(e).__name__
finally:engine.dispose()
out=Path(__file__).resolve().parents[2]/'docs/governance-workspace/evidence';out.mkdir(parents=True,exist_ok=True)
(out/'diagnosis.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
