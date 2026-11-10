"""Local UI verification only: ephemeral SQLite and synthetic signed Supabase sessions.

No provider login, Auth-user creation, PostgreSQL connection, or production bypass.
Run ../.venv/bin/python tests/serve_week9_fixture.py; all data is illustrative.
"""
import os
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from serve_week7_fixture import main, factory  # existing scoped in-memory server fixture
import session_auth
import security
import test_week7_auth as tokens
from models import IncidentReport

with factory() as db:
    db.add(IncidentReport(reporter_id=8,description='Fixture incident response record',severity='high',status='reported'))
    db.commit()

key=tokens.make_ec_key()
security._SUPABASE_VERIFIER=tokens.make_verifier(tokens.make_jwks(key))
subjects={i:f'00000000-0000-0000-0000-{i:012d}' for i in (2,4,8)}
os.environ.update({'DEREXI_ENV':'test','DEREXI_DEV_AUTH':'0',
    'SUPABASE_URL':tokens.PROJECT,'SUPABASE_PUBLISHABLE_KEY':'sb_publishable_fixture_only',
    'DEREXI_AUTH_SUBJECT_MAP':json.dumps({sub:uid for uid,sub in subjects.items()})})
os.environ.pop('DEREXI_PUBLIC_ORIGIN',None)


def provider(path,payload=None,access_token=None):
    if path.startswith('logout'): return {}
    if path.startswith('token?grant_type=refresh_token'):
        uid=int(payload['refresh_token'].split('-')[-1])
    else:
        if payload.get('password')!='fixture-password':
            raise main.HTTPException(401,'Sign-in failed. Check your credentials.')
        uid=next((i for i in subjects if payload['email']==f'fixture{i}@example.invalid'),None)
        if not uid: raise main.HTTPException(401,'Sign-in failed. Check your credentials.')
    return {'access_token':tokens.build_token(key,sub=subjects[uid],extra={'email':f'fixture{uid}@example.invalid'}),
            'refresh_token':f'fixture-refresh-{uid}'}


session_auth.provider_request=provider
if __name__=='__main__':
    import uvicorn
    print('ISOLATED AUTH FIXTURE — mocked provider; never Supabase; test environment only')
    uvicorn.run(main.app,host='127.0.0.1',port=8029,proxy_headers=False,access_log=False)
