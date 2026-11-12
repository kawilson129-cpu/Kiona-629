"""Isolated support handoff checks. No provider, SMTP or PostgreSQL connections."""
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
from fastapi.testclient import TestClient
from database import get_db
import main
import incident_assistance as service
from models import User, TechnicalRoute, SupportRequest, SupportAudit, IncidentReport

checks=[]
def check(name, value):
    checks.append({'name':name,'pass':bool(value)})
    print(('PASS ' if value else 'FAIL ')+name,flush=True)

class MockTransport:
    def __init__(self,outcome='accepted'):
        self.outcome=outcome;self.calls=[]
    def send(self,*args):self.calls.append(args);return self.outcome

def run():
    check('Review clocks preserve timezone offsets',service.utc(datetime(2026,11,12,10,tzinfo=timezone(timedelta(hours=-5)))).hour==15)
    for text,expected in [('I lost my work laptop',True),('I clicked a phishing link',True),
        ('My account is hacked',True),('Unexpected MFA prompts right now',True),
        ('Our banking system is down',True),('My printer is not working',True),
        ('How should I report a lost work laptop?',False),('What is phishing?',False),
        ('What is our password policy?',False),('How much paid time off?',False),
        ('This is a hypothetical phishing training question',False)]:
        check('Classification: '+text,service.classify(text,use_ai=False)['potential_incident']==expected)
    for kind in service.QUESTIONS:
        check('Two bounded followups: '+kind,len(service.QUESTIONS[kind])==2)
    with patch('ai.classify_support_event',return_value='compromise'):
        check('Optional AI hint used',service.classify('An unfamiliar computer event')['incident_type']=='compromise')
        check('AI cannot suppress deterministic urgency',service.classify('I lost my laptop')['urgency']=='urgent')
    engine,factory=isolated_database();factory.configure(bind=engine)
    def override():
        with factory() as db:yield db
    main.app.dependency_overrides[get_db]=override
    os.environ['DEREXI_APPROVED_MAILBOXES']=json.dumps({'security':{'address':'security@example.invalid','label':'Security service desk','channel':'security'},
        'it':{'address':'it@example.invalid','label':'IT service desk','channel':'it'}})
    os.environ.pop('DEREXI_OUTBOUND_EMAIL',None)
    c=TestClient(main.app,raise_server_exceptions=False)
    try:
        headers={i:{'Authorization':'Bearer '+c.post('/dev-auth/token',json={'user_id':i}).json()['access_token']} for i in (2,4,8,9,12)}
        with factory() as db:dept=db.get(User,8).department_id;other=next(d for d in [1,2,3,4] if d!=dept)
        def get(path,uid=8):return c.get(path,headers=headers[uid])
        def post(path,data=None,uid=8):return c.post(path,json=data,headers=headers[uid])
        check('Anonymous assessment denied',c.post('/support/assess',json={'text':'I lost a laptop'}).status_code==401)
        check('Employee routing denied',get('/technical-routing/config').status_code==403)
        check('Employee readiness inventory denied',get('/technical-routing/readiness').status_code==403)
        ready=get('/technical-routing/readiness',2)
        check('Admin read-only owner coverage available',ready.status_code==200 and len(ready.json()['owner_coverage'])>0)
        check('Deficient departments not falsely marked ready',any(not d['ready'] for d in ready.json()['owner_coverage']))
        check('Infrastructure not falsely verified',any(x['state']=='PENDING_EXTERNAL_VERIFICATION' for x in ready.json()['configuration']))
        for channel in ('security','it'):
            r=post('/technical-routing/config',{'department_id':dept,'channel':channel,'mailbox_key':channel,'enabled':True,'expected_revision':0},2)
            check('Admin saves approved '+channel+' route',r.status_code==200)
        check('Arbitrary recipient/key denied',post('/technical-routing/config',{'department_id':dept,'channel':'it','mailbox_key':'attacker','enabled':True,'expected_revision':1},2).status_code==422)
        check('Unknown body fields forbidden',post('/support/assess',{'text':'I lost a laptop','recipient':'attacker@example.invalid'}).status_code==422)
        check('Secret assignment rejected',post('/support/assess',{'text':'password=do-not-store-me'}).status_code==422)
        check('Compromise status is not mistaken for a secret',post('/support/assess',{'text':'My password is compromised'}).status_code==200)
        check('Account number rejected',post('/support/assess',{'text':'My account 1234567890123456 is broken'}).status_code==422)
        a=post('/ask',{'question':'I clicked a phishing link'}).json()
        check('Assistant supplies urgent intake without auto-submitting',a.get('incident_assistance',{}).get('urgency')=='urgent' and 'incident_id' not in a)
        with factory() as db:check('Detection persists no support request',db.query(SupportRequest).count()==0)
        def payload(**kw):return {'idempotency_key':str(uuid.uuid4()),'incident_type':'phishing','details':'I clicked a suspicious email link','answers':['Yes, clicked; no credentials entered','Today in the work email application'],**kw}
        p=payload();r=post('/support/prepare',p);check('Structured draft prepares',r.status_code==200)
        rid=r.json()['id'];d=r.json()['request']
        check('Verified identity and department bound',d['employee_id']==8 and d['department_id']==dept and 'employee' in d and 'email' in d)
        check('Security destination and urgent status derived',d['destination']=='Security service desk' and d['channel']=='security' and d['urgency']=='urgent')
        check('Unconfirmed preview is draft',r.json()['state']=='draft' and r.json()['incident_id'] is None)
        downgrade=post('/support/prepare',payload(incident_type='technical')).json()
        check('Client cannot downgrade phishing to IT',downgrade['request']['channel']=='security')
        check('Idempotent preparation returns same draft',post('/support/prepare',p).json()['id']==rid)
        check('Same key changed content denied',post('/support/prepare',{**p,'details':'A different event happened today'}).status_code==409)
        check('Client identity injection forbidden',post('/support/prepare',payload(user_id=2)).status_code==422)
        check('Recipient injection forbidden',post('/support/prepare',payload(recipient='attacker@example.invalid')).status_code==422)
        check('Other user cannot read draft',get('/support/requests/'+rid,4).status_code==404)
        check('Owner cannot confirm another employee request',post('/support/requests/'+rid+'/confirm',{'confirmed':True},4).status_code==404)
        check('False confirmation rejected',post('/support/requests/'+rid+'/confirm',{'confirmed':False}).status_code==422)
        check('String confirmation rejected',post('/support/requests/'+rid+'/confirm',{'confirmed':'true'}).status_code==422)
        mock=MockTransport()
        with patch.object(service,'transport',return_value=mock):
            check('Draft cannot dispatch',post('/support/requests/'+rid+'/dispatch').json()['state']=='draft' and not mock.calls)
        check('Confirmed request queued internally',post('/support/requests/'+rid+'/confirm',{'confirmed':True}).json()['state']=='queued')
        post('/support/requests/'+rid+'/confirm',{'confirmed':True})
        with factory() as db:check('Repeated confirmation creates one incident',db.query(IncidentReport).filter(IncidentReport.description.like('%'+rid+'%')).count()==1)
        check('Existing notification triage includes incident',get('/messages/notifications',2).json()['incident_triage_count']>=1)
        with patch('smtplib.SMTP_SSL',side_effect=AssertionError('Network forbidden')):
            check('Outbound defaults OFF without SMTP call',post('/support/requests/'+rid+'/dispatch').json()['state']=='disabled')
        with patch.object(service,'transport',return_value=mock):
            result=post('/support/requests/'+rid+'/dispatch').json()
            check('Mock acceptance accurately reported',result['state']=='accepted' and 'not confirmation' in result['delivery_notice'])
            post('/support/requests/'+rid+'/dispatch')
            check('Repeated dispatch deduplicated',len(mock.calls)==1)
            check('Destination exclusively server approved',mock.calls[0][0]=='security@example.invalid')
            check('Stable Message-ID and structured body',rid in mock.calls[0][3] and json.loads(mock.calls[0][2])['employee_id']==8)
        def queued():
            response=post('/support/prepare',payload());key=response.json()['id'];post('/support/requests/'+key+'/confirm',{'confirmed':True});return key
        retry=queued();failing=MockTransport('retryable')
        with patch.object(service,'transport',return_value=failing):
            check('Known pre-send failure retryable',post('/support/requests/'+retry+'/dispatch').json()['state']=='retryable')
            check('Retry cooldown enforced',post('/support/requests/'+retry+'/dispatch').status_code==429)
            for _ in range(2):
                with factory() as db:db.get(SupportRequest,retry).next_attempt=datetime.now(timezone.utc)-timedelta(seconds=1);db.commit()
                post('/support/requests/'+retry+'/dispatch')
            check('Retry attempt cap enforced',post('/support/requests/'+retry+'/dispatch').status_code==409 and len(failing.calls)==3)
        for state in ('unknown','rejected'):
            key=queued();adapter=MockTransport(state)
            with patch.object(service,'transport',return_value=adapter):
                post('/support/requests/'+key+'/dispatch');post('/support/requests/'+key+'/dispatch')
                check('No unsafe retry after '+state,len(adapter.calls)==1 and get('/support/requests/'+key).json()['state']==state)
        key=queued()
        with factory() as db:db.get(SupportRequest,key).state='sending';db.commit()
        with patch.object(service,'transport',return_value=mock):
            before=len(mock.calls);post('/support/requests/'+key+'/dispatch');check('Crash-pending claim never automatically resends',len(mock.calls)==before)
        key=post('/support/prepare',payload()).json()['id']
        with factory() as db:
            route=db.query(TechnicalRoute).filter_by(department_id=dept,channel='security').one();route.enabled=False;db.commit()
        check('Routing disabled before confirmation blocks submission',post('/support/requests/'+key+'/confirm',{'confirmed':True}).status_code==409)
        with factory() as db:route=db.query(TechnicalRoute).filter_by(department_id=dept,channel='security').one();route.enabled=True;db.commit()
        check('Routing revision change invalidates review',post('/support/requests/'+key+'/confirm',{'confirmed':True}).status_code==409)
        expired=post('/support/prepare',payload()).json()['id']
        with factory() as db:db.get(SupportRequest,expired).created_at=datetime.now(timezone.utc)-timedelta(hours=25);db.commit()
        check('Expired review requires new preparation',post('/support/requests/'+expired+'/confirm',{'confirmed':True}).status_code==409)
        check('Admin grants narrow routing access',post('/technical-routing/grants',{'user_id':8,'department_id':dept,'enabled':True},2).status_code==200)
        check('Delegate can read own routing',get('/technical-routing/config').status_code==200)
        check('Delegate cannot edit other departments',post('/technical-routing/config',{'department_id':other,'channel':'it','mailbox_key':'it','enabled':True,'expected_revision':0}).status_code==403)
        check('Delegate cannot grant permissions',post('/technical-routing/grants',{'user_id':4,'department_id':dept,'enabled':True}).status_code==403)
        check('Routing delegate gains no policy approval access',get('/governance/drafts').status_code==403)
        check('Routing delegate gains no Admin incident access',c.patch('/incidents/1',headers=headers[8],json={'status':'triaged'}).status_code==403)
        check('Route validation sends nothing',post('/technical-routing/test',{'department_id':dept,'channel':'security','confirmed':True}).json()['notice'].startswith('Configuration validated; no email sent'))
        post('/technical-routing/grants',{'user_id':8,'department_id':dept,'enabled':False},2)
        check('Permission revocation immediate',get('/technical-routing/config').status_code==403)
        with factory() as db:
            events=db.query(SupportAudit).all()
            check('Sanitized audit contains no submitted content',all(not any(term in e.action for term in ['clicked','password','example.invalid']) for e in events))
        # Missing-table behavior is honest, leaving the policy API untouched.
        from sqlalchemy import event
        from sqlalchemy.exc import ProgrammingError
        def missing(conn,cursor,statement,params,context,many):
            if 'technical_routes' in statement:raise ProgrammingError(statement,{},Exception('missing schema'))
        event.listen(engine,'before_cursor_execute',missing)
        try:check('Missing routing schema fails safely',post('/support/prepare',payload()).status_code==503)
        finally:event.remove(engine,'before_cursor_execute',missing)
    finally:
        main.app.dependency_overrides.clear();engine.dispose();c.close()
    return 1 if any(not x['pass'] for x in checks) else 0

if __name__=='__main__':
    out=Path(os.environ['DEREXI_SPRINT_EVIDENCE']);out.mkdir(parents=True,exist_ok=True)
    try:code=run()
    finally:
        (out/'support-results.json').write_text(json.dumps({'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks},indent=2)+'\n',encoding='utf-8')
    sys.exit(code)
