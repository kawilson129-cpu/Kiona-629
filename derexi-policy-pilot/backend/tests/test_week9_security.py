"""Isolated Week 9 HTTP checks; real handlers/ORM/JWT crypto, mocked provider only."""
import json
import logging
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
import main
import security
import session_auth
import dev_auth
import test_week7_auth as jwt_fixture
from transport import protected_database_url
from database import get_db
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from security_events import AccessPathFilter
from models import User, IncidentReport, Policy, GovernanceDraft

OUT=Path(__file__).resolve().parents[3]/'semester_5/DeRexi_Week 9/evidence'
checks=[]
events=[]


class Capture(logging.Handler):
    def emit(self,record):
        events.append(json.loads(record.getMessage()))


def check(name,value,actual=None):
    checks.append({'name':name,'status':'PASS' if value else 'FAIL','actual':actual})
    print(('PASS ' if value else 'FAIL ')+name)


def run():
    engine,factory=isolated_database();factory.configure(bind=engine)
    def override():
        with factory() as db: yield db
    main.app.dependency_overrides[get_db]=override
    client=TestClient(main.app,raise_server_exceptions=False)
    def auth(uid):
        r=client.post('/dev-auth/token',json={'user_id':uid});assert r.status_code==200,r.text
        return {'Authorization':'Bearer '+r.json()['access_token']}
    headers={i:auth(i) for i in (2,4,8,9,12)}
    handler=Capture();logger=logging.getLogger('derexi.security');logger.addHandler(handler)
    try:
        # Real anonymous calls across every sensitive route, including bypass paths.
        exempt={'/','/health','/auth/config','/auth/login','/auth/logout','/auth/refresh','/dev-auth/token','/dev-auth/identities'}
        for route in main.app.routes:
            if not isinstance(route,APIRoute) or route.path in exempt or route.path.startswith('/api/pulse'): continue
            path=route.path
            for parameter in ('policy_id','conversation_id','request_id','incident_id','did','token'):
                path=path.replace('{'+parameter+'}','1')
            for method in sorted(route.methods-{'HEAD','OPTIONS'}):
                r=client.request(method,path,json={} if method in {'POST','PATCH'} else None)
                check('Anonymous denied '+method+' '+route.path,r.status_code==401,r.status_code)
        legacy={'title':'Bypass','status':'approved','version':{'body':'Private sentinel text'}}
        for uid,code in ((8,403),(4,409),(2,409)):
            check('Direct policy creation bypass blocked '+str(uid),client.post('/policies',json=legacy,headers=headers[uid]).status_code==code)
            check('Direct version bypass blocked '+str(uid),client.post('/policies/48/versions',json={'version_no':'9','body':'Private sentinel text'},headers=headers[uid]).status_code==code)
        with factory() as db:
            db.get(User,12).department_id=2
            db.add_all([IncidentReport(reporter_id=8,description='Private incident sentinel',severity='high',status='reported'),
                        IncidentReport(reporter_id=12,description='Other department sentinel',severity='low',status='reported')])
            db.commit()
        check('Policy Owner cannot read unrelated incident reports',client.get('/incidents',headers=headers[4]).json()==[])
        check('Employee sees only own incidents',len(client.get('/incidents',headers=headers[8]).json())==1)
        check('Administrator sees organizational incident reports',len(client.get('/incidents',headers=headers[2]).json())==2)
        check('Policy Owner cannot change incident status',client.patch('/incidents/1',json={'status':'resolved'},headers=headers[4]).status_code==403)
        check('Employee cannot assign incident handler',client.post('/incidents',json={'description':'Test report','assigned_to':9},headers=headers[8]).status_code==403)
        check('Policy Owner cannot assign incident handler',client.post('/incidents',json={'description':'Test report','assigned_to':9},headers=headers[4]).status_code==403)
        check('Employee cannot select escalation level',client.post('/incidents',json={'description':'Test report','escalation_level':5},headers=headers[8]).status_code==403)
        check('Administrator can update incident',client.patch('/incidents/1',json={'status':'triaged','assigned_to':9},headers=headers[2]).status_code==200)
        check('Explicit handler assignment permits incident access',len(client.get('/incidents',headers=headers[9]).json())==1)
        check('Unknown handler rejected safely',client.patch('/incidents/1',json={'assigned_to':99999},headers=headers[2]).status_code==422)
        check('Null incident workflow state rejected safely',client.patch('/incidents/1',json={'status':None},headers=headers[2]).status_code==422)
        check('Unknown category rejected safely',client.post('/incidents',json={'description':'Test report','category_id':99999},headers=headers[8]).status_code==422)
        check('Owner dashboard is explicitly department scoped',client.get('/dashboard/policy-health',headers=headers[4]).json().get('scope')=='department')
        scoped=client.get('/dashboard/policy-health',headers=headers[4]).json()
        check('Owner dashboard excludes other department policies',scoped['totals']['policies']==1)
        check('Owner dashboard conceals unrelated incident and chat aggregates',scoped['totals']['incidents']==0 and scoped['totals']['conversations']==0)
        draft=client.post('/governance/drafts',headers=headers[4],json={'title':'Log approval fixture',
            'body':'Private policy audit sentinel','version_no':'1.0'}).json()
        did=draft['id']
        def action(which,uid,revision,**extra):
            return client.post(f'/governance/drafts/{did}/actions',headers=headers[uid],json={
                'action':which,'expected_revision':revision,**extra})
        check('Author cannot select self for peer approval',action('submit',4,draft['revision'],reviewer_id=4).status_code==403)
        draft=action('submit',4,draft['revision'],reviewer_id=9).json()
        check('Author cannot approve own draft',action('peer_approve',4,draft['revision']).status_code==403)
        peer=action('peer_approve',9,draft['revision'])
        check('Independent department peer approval succeeds',peer.status_code==200)
        final=action('final_approve',2,peer.json()['revision'])
        check('Independent system administrator approval succeeds',final.status_code==200)
        # Logging validation and SQL failure must never reveal submitted data.
        bad=client.post('/incidents',headers=headers[8],json={'description':{'password':'sensitive-validation-marker'}})
        check('Validation response redacts rejected input','sensitive-validation-marker' not in bad.text and bad.status_code==422)
        class Broken:
            def query(self,*args): raise RuntimeError('postgresql://password-private-message-marker')
        main.app.dependency_overrides[get_db]=lambda:Broken()
        # Override only identity to simulate a verified actor during DB outage.
        main.app.dependency_overrides[security.get_identity]=lambda:security.Identity(8,'fixture8@example.invalid','Fixture','Employee',1,'dev')
        broken=client.get('/policies')
        check('DB failure is generic and actionable',broken.status_code==500 and 'try again' in broken.text.lower() and 'password-private' not in broken.text)
        check('Request id is generated, not trusted from caller',client.get('/policies',headers={'X-Request-ID':'untrusted-marker'}).headers.get('X-Request-ID')!='untrusted-marker')
        main.app.dependency_overrides.pop(security.get_identity)
        main.app.dependency_overrides[get_db]=override

        # Isolated Supabase production path: actual ES256 verification, stub JWKS.
        key=jwt_fixture.make_ec_key()
        verifier=jwt_fixture.make_verifier(jwt_fixture.make_jwks(key))
        subject='11111111-2222-3333-4444-555555555555'
        def token(**kw): return jwt_fixture.build_token(key,extra={'email':'fixture8@example.invalid',**kw.pop('extra',{})},**kw)
        env={'DEREXI_ENV':'production','SUPABASE_URL':jwt_fixture.PROJECT,
             'SUPABASE_PUBLISHABLE_KEY':'sb_publishable_fixture_only',
             'DEREXI_AUTH_SUBJECT_MAP':json.dumps({subject:8}),'DEREXI_PUBLIC_ORIGIN':'https://testserver'}
        with patch.dict(os.environ,env),patch.object(security,'_SUPABASE_VERIFIER',verifier):
            c=TestClient(main.app,base_url='https://testserver',raise_server_exceptions=False)
            origin={'Origin':'https://testserver','X-Derexi-Request':'1'}
            bearer={'Authorization':'Bearer '+token()}
            check('Valid Supabase JWT maps to existing employee',c.get('/me',headers=bearer).json().get('id')==8)
            check('Supabase JWT role claim cannot elevate access',c.get('/governance/drafts',headers={'Authorization':'Bearer '+token(extra={'role':'System Administrator'})}).status_code==403)
            for name,credential in [('expired',token(exp_offset=-10)),('wrong audience',token(aud='service_role')),('wrong issuer',token(iss='https://untrusted.example')),('invalid signature',jwt_fixture.build_token(jwt_fixture.make_ec_key(),extra={'email':'fixture8@example.invalid'}))]:
                check(name+' Supabase JWT denied',c.get('/me',headers={'Authorization':'Bearer '+credential}).status_code==401)
            with patch.dict(os.environ,{'DEREXI_AUTH_SUBJECT_MAP':'{}'}):
                check('Verified email alone does not prove employee identity',c.get('/me',headers=bearer).status_code==403)
            with patch.dict(os.environ,{'DEREXI_AUTH_SUBJECT_MAP':json.dumps({subject:4})}):
                check('Subject and business email must match the same user',c.get('/me',headers=bearer).status_code==403)
            with patch.dict(os.environ,{'SUPABASE_PUBLISHABLE_KEY':'sb_secret_not_allowed'}):
                check('Service keys cannot configure public sign-in',not c.get('/auth/config').json()['sign_in_enabled'])
            session_auth._ATTEMPTS.clear()
            provider_calls=[]
            def provider(path,payload=None,access_token=None):
                provider_calls.append(path)
                if payload and payload.get('password')=='wrong-private-credential': raise main.HTTPException(401,'Sign-in failed. Check your credentials.')
                return {'access_token':token(),'refresh_token':'fixture-refresh-private-marker'}
            with patch.object(session_auth,'provider_request',provider):
                check('Login rejects CSRF attempt',c.post('/auth/login',headers={'Origin':'https://untrusted.example'},json={'email':'fixture8@example.invalid','password':'private-password-marker'}).status_code==403)
                failed=c.post('/auth/login',headers=origin,json={'email':'fixture8@example.invalid','password':'wrong-private-credential'})
                check('Login failure is generic',failed.status_code==401 and 'wrong-private' not in failed.text)
                login=c.post('/auth/login',headers=origin,json={'email':'fixture8@example.invalid','password':'private-password-marker'})
                check('Mapped account can establish verified browser session',login.status_code==200)
                cookies=login.headers.get_list('set-cookie')
                check('Browser session cookies are Secure HttpOnly SameSite Strict',len(cookies)==2 and all('Secure' in s and 'HttpOnly' in s and 'SameSite=strict' in s for s in cookies))
                check('Login does not expose tokens in JSON','access_token' not in login.text and 'refresh_token' not in login.text)
                check('Session reads do not expose credentials',c.get('/auth/session').status_code==200 and c.get('/auth/session').json().get('user_id')==8)
                check('Cookie-authenticated writes require CSRF proof',c.post('/ask',json={'question':'Test request'}).status_code==403)
                check('Refresh rotates a verified mapped session',c.post('/auth/refresh',headers=origin).status_code==200)
                check('Authenticated data is not cached',c.get('/policies').headers.get('cache-control')=='no-store')
                check('Production response includes HSTS',c.get('/me').headers.get('strict-transport-security')=='max-age=31536000')
                check('Refresh token is scoped to auth endpoints',any('Path=/auth' in s for s in cookies))
                logout=c.post('/auth/logout',headers=origin)
                check('Logout clears local cookies and invokes provider revocation',logout.status_code==200 and 'logout?scope=local' in provider_calls and c.get('/auth/session').status_code==401)
                c.post('/auth/login',headers=origin,json={'email':'fixture8@example.invalid','password':'private-password-marker'})
                with patch.object(session_auth,'provider_request',side_effect=main.HTTPException(503,'Unavailable')):
                    logout=c.post('/auth/logout',headers=origin)
                    check('Failed remote logout still clears browser cookies honestly',logout.status_code==503 and logout.json()['signed_out'] and c.get('/auth/session').status_code==401)
                for _ in range(9):
                    rate=c.post('/auth/login',headers=origin,json={'email':'fixture8@example.invalid','password':'wrong-private-credential'})
                check('Login has bounded attempt throttling',rate.status_code==429)
            check('Production cannot mint developer tokens',c.post('/dev-auth/token',json={'user_id':2}).status_code==404)
            check('Production rejects valid local dev token',c.get('/me',headers=headers[2]).status_code==401)
            check('Production refuses plaintext API transport',client.get('/policies',headers=headers[2]).status_code==403)
        with patch.dict(os.environ,{'DEREXI_DEV_USER_IDS':'invalid-allowlist'}):
            check('Malformed developer allowlist fails closed',client.post('/dev-auth/token',json={'user_id':8}).status_code==503)
        with patch.dict(os.environ,{'DEREXI_ENV':''}):
            check('Missing explicit environment cannot enable developer identity',not dev_auth.dev_auth_enabled())
        for name,url,ok in [('remote default','postgresql://u:p@db.example/app',True),
                            ('username cannot impersonate localhost','postgresql://localhost:p@db.example/app',True),
                            ('plaintext remote refused','postgresql://u:p@db.example/app?sslmode=disable',False),
                            ('opportunistic remote refused','postgresql://u:p@db.example/app?sslmode=prefer',False),
                            ('verified mode retained','postgresql://u:p@db.example/app?sslmode=verify-full',True)]:
            try: value=protected_database_url(url); valid='sslmode=' in value
            except RuntimeError: valid=False
            check('Database TLS: '+name,valid==ok)
        serialized=json.dumps(events)
        check('Structured logs exclude credentials, tokens and private text',not any(marker in serialized for marker in ['private-password-marker','wrong-private-credential','fixture-refresh-private-marker','Private sentinel text','Private incident sentinel','Private policy audit sentinel','sensitive-validation-marker','eyJ','postgresql://']))
        check('Access denials and login failures are recorded',{'access_denied','authentication_failure','login_failure'} <= {e['event'] for e in events})
        check('Sensitive admin actions are recorded',any(e['event']=='administrative_action' and e['actor_id']==2 for e in events))
        check('Approval logs identify verified actors without policy text',any(e['event']=='approval' and e['action']=='peer_approve' and e['actor_id']==9 for e in events) and any(e['event']=='approval' and e['action']=='final_approve' and e['actor_id']==2 for e in events))
        check('Log route templates exclude raw resource parameters',all('/1' not in e['route'] for e in events))
        record=logging.LogRecord('uvicorn.access',logging.INFO,'',0,'%s %s %s %s %s',
            ('client','DELETE','/governance/documents/preview/private-token-marker?secret=private-query-marker','1.1',200),None)
        AccessPathFilter(lambda:main.app.routes).filter(record)
        check('Default access logging redacts preview tokens and query data','private-token-marker' not in record.getMessage() and 'private-query-marker' not in record.getMessage())
        for label,config in [('plaintext JWKS',{'SUPABASE_URL':jwt_fixture.PROJECT,'SUPABASE_JWKS_URL':'http://untrusted.example/jwks'}),
                             ('symmetric production algorithm',{'SUPABASE_URL':jwt_fixture.PROJECT,'SUPABASE_JWT_ALGS':'HS256'})]:
            try: jwt_fixture.AuthSettings.from_env(config); refused=False
            except jwt_fixture.AuthenticationError: refused=True
            check('Unsafe auth configuration rejected: '+label,refused)
    finally:
        logger.removeHandler(handler);main.app.dependency_overrides.clear();engine.dispose()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'week9-security-results.json').write_text(json.dumps({'mode':'isolated SQLite + real JWT crypto + mocked Supabase transport','checks':checks,'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks)},indent=2)+'\n')
    (OUT/'security-events-sanitized.json').write_text(json.dumps(events,indent=2)+'\n')
    print(f"{sum(c['status']=='PASS' for c in checks)} passed, {sum(c['status']=='FAIL' for c in checks)} failed")
    return 1 if any(c['status']=='FAIL' for c in checks) else 0


if __name__=='__main__': sys.exit(run())
