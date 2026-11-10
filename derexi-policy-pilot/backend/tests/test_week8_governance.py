"""Week 8 real HTTP/ORM lifecycle tests, ephemeral SQLite + PostgreSQL tripwire."""
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
import main
from fastapi.testclient import TestClient
from database import get_db
from models import User, GovernanceDraft, GovernanceEvent, Policy, PolicyVersion

checks=[]
def check(name, condition):
    checks.append({'name':name,'pass':bool(condition)})
    print(('PASS ' if condition else 'FAIL ')+name)
    if not condition: raise AssertionError(name)

def run():
    engine,factory=isolated_database();factory.configure(bind=engine)
    with factory() as db:
        db.get(User,7).department_id=2
        db.commit()
    def override():
        with factory() as db: yield db
    main.app.dependency_overrides[get_db]=override
    c=TestClient(main.app)
    headers={}
    for uid in (1,2,4,7,8,9,12):
        r=c.post('/dev-auth/token',json={'user_id':uid});assert r.status_code==200,r.text
        headers[uid]={'Authorization':'Bearer '+r.json()['access_token']}
    def get(path,uid=4):return c.get(path,headers=headers[uid])
    def post(path,payload,uid=4):return c.post(path,json=payload,headers=headers[uid])
    base={'title':'Week 8 controlled policy','body':'Published guidance for safe customer handling.',
          'version_no':'1.0','department_id':1,'effective_date':date.today().isoformat()}
    def create(**extra):
        r=post('/governance/drafts',{**base,**extra});assert r.status_code==201,r.text;return r.json()
    def act(d,a,uid=4,code=200,**extra):
        r=post('/governance/drafts/'+str(d['id'])+'/actions',{'action':a,'expected_revision':d['revision'],**extra},uid)
        check(a+' by '+str(uid)+' -> '+str(code),r.status_code==code)
        return r.json() if code==200 else d
    def approved(d):
        d=act(d,'submit',reviewer_id=9);d=act(d,'peer_approve',9);return act(d,'final_approve',1)
    for path in ('/governance/drafts','/governance/owners','/dashboard/policy-health'):
        check('Employee denied '+path,get(path,8).status_code==403)
        check('Anonymous denied '+path,c.get(path).status_code==401)
    check('Employee draft creation denied',post('/governance/drafts',base,8).status_code==403)
    check('Author department spoof denied',post('/governance/drafts',{**base,'department_id':2}).status_code==403)
    check('Unknown department rejected',post('/governance/drafts',{**base,'department_id':999},1).status_code==422)
    check('Status injection rejected',post('/governance/drafts',{**base,'status':'published'}).status_code==422)
    legacy={'title':'Bypass','status':'approved','version':{'body':'Bypass content'}}
    for uid in (8,4,1):
        check('Legacy policy publication closed '+str(uid),post('/policies',legacy,uid).status_code==(403 if uid==8 else 409))
        check('Legacy version publication closed '+str(uid),post('/policies/1/versions',{'version_no':'2.0','body':'Bypass content'},uid).status_code==(403 if uid==8 else 409))
    d=create()
    check('Unpublished new policy absent from Library',all(p['title']!=d['title'] for p in get('/policies',8).json()))
    check('Employee detail denied',get('/governance/drafts/'+str(d['id']),8).status_code==403)
    check('Other department detail denied',get('/governance/drafts/'+str(d['id']),7).status_code==403)
    check('Other department list excludes draft',get('/governance/drafts',7).json()==[])
    act(d,'publish',1,409);act(d,'final_approve',1,409)
    act(d,'submit',4,403,reviewer_id=4)
    act(d,'submit',4,403,reviewer_id=8)
    act(d,'submit',4,403,reviewer_id=7)
    act(d,'submit',4,403,reviewer_id=1)
    d=act(d,'submit',reviewer_id=9)
    notices=get('/messages/notifications',9).json()
    check('Peer notification routes to governance',any(n['governance_draft_id']==d['id'] for n in notices['items']))
    check('Unrelated employee receives no governance notice',not get('/messages/notifications',8).json()['items'])
    act(d,'peer_approve',4,403);act(d,'peer_approve',12,403);act(d,'peer_changes',9,422)
    d=act(d,'peer_changes',9,comment='Clarify the customer handling rule.')
    check('Revision request author notified',any(n['governance_draft_id']==d['id'] for n in get('/messages/notifications',4).json()['items']))
    edit={k:base[k] for k in ('title','body','version_no','effective_date')};edit['body']='Revised handling rule.'
    r=c.patch('/governance/drafts/'+str(d['id']),headers=headers[9],json={**edit,'expected_revision':d['revision']})
    check('Peer cannot edit author draft',r.status_code==403)
    d=act(d,'submit',reviewer_id=9);d=act(d,'peer_approve',9)
    check('Final queue notifies both independent admins',all(any(n['governance_draft_id']==d['id'] for n in get('/messages/notifications',uid).json()['items']) for uid in (1,2)))
    act(d,'final_approve',9,403);act(d,'final_approve',4,403);act(d,'final_changes',1,422)
    d=act(d,'final_reject',1,comment='Add an exception process.')
    d=act(d,'submit',reviewer_id=9);d=act(d,'peer_reject',9,comment='Missing required steps.')
    d=approved(d)
    check('Independent approvals retained',d['peer_approved_by']==9 and d['final_approved_by']==1)
    old=d.copy()
    r=c.patch('/governance/drafts/'+str(d['id']),headers=headers[4],json={**edit,'expected_revision':d['revision']})
    check('Approved content author edit accepted',r.status_code==200);d=r.json()
    check('Editing invalidates both approvals',d['status']=='draft' and d['peer_approved_by'] is None and d['final_approved_by'] is None)
    act(d,'publish',1,409)
    act(old,'final_approve',1,409)
    d=approved(d)
    # Recheck reviewer role at publication time.
    with factory() as db:db.get(User,9).role_id=1;db.commit()
    act(d,'publish',1,409)
    with factory() as db:db.get(User,9).role_id=2;db.commit()
    d=act(d,'publish',1)
    check('New published policy visible',get('/policies/'+str(d['policy_id']),8).json()['versions'][-1]['body']==edit['body'])
    check('Publication decision notifies author',any('Published version' in n['snippet'] for n in get('/messages/notifications',4).json()['items']))
    r=c.patch('/governance/drafts/'+str(d['id']),headers=headers[4],json={**edit,'expected_revision':d['revision']})
    check('Published working copy immutable',r.status_code==409)
    history=get('/governance/drafts/'+str(d['id'])).json()['history']
    check('Audit retains decisions, content snapshots, actors and time',len(history)>12 and all(e['actor'] and e['at'] and e['snapshot']['body'] for e in history))
    source={'url':'https://www.fdic.gov/news/financial-institution-letters/example','title':'Fictional fixture regulatory update','published':'2026-11-01','context':'FDIC · Banking & Finance · synthetic fixture'}
    future=(date.today()+timedelta(days=3)).isoformat()
    rev=create(policy_id=d['policy_id'],title=d['title'],version_no='2.0',body='Replacement guidance.',effective_date=future,source=source)
    check('Revision stores published baseline',get('/governance/drafts/'+str(rev['id'])).json()['base_version']['body']==edit['body'])
    check('Pulse provenance retained exactly',rev['source']==source)
    rev=approved(rev);act(rev,'publish',1,409);act(rev,'publish',9,403)
    check('Future approved revision leaves published version available',get('/policies/'+str(d['policy_id']),8).json()['latest_version']=='1.0')
    check('Revision draft absent from employee policy versions',len(get('/policies/'+str(d['policy_id']),8).json()['versions'])==1)
    payload={**edit,'body':'Replacement guidance.','version_no':'2.0','source':source,'expected_revision':rev['revision']}
    r=c.patch('/governance/drafts/'+str(rev['id']),headers=headers[4],json=payload);assert r.status_code==200,r.text;rev=approved(r.json())
    # A competing revision approved from the same base must not replace a newer publication.
    competing=create(policy_id=d['policy_id'],title=d['title'],version_no='3.0');competing=approved(competing)
    rev=act(rev,'publish',1)
    check('Replacement published with complete old version history',len(get('/policies/'+str(d['policy_id']),8).json()['versions'])==2)
    act(competing,'publish',1,409)
    bad={**source,'url':'javascript:alert(1)'}
    check('Unsafe Pulse URL rejected',post('/governance/drafts',{**base,'source':bad}).status_code==422)
    check('Pulse API preserved',c.get('/api/pulse/health').status_code==200)
    # Existing Assistant triage workflow uses real SQLite ORM with live connection tripwire.
    r=post('/ask',{'question':'Where can I find a policy on hypothetical spaceships?'},8)
    check('Policy Assistant regression',r.status_code==200)
    check('Library search regression (offline ranking adapter)',get('/policies/search?q=customer',8).status_code==200)
    check('Dashboard health retained',get('/dashboard/policy-health',4).status_code==200)
    check('Policy Owners directory excludes employee/admin roles',all(u['id'] not in (1,2,8) for u in get('/governance/owners').json()))
    # An administrator author must use a second administrator for approval and publication.
    r=post('/governance/drafts',{**base,'title':'Administrator authored policy'},1)
    check('Administrator can author in chosen department',r.status_code==201)
    admin_draft=r.json()
    admin_draft=act(admin_draft,'submit',1,reviewer_id=9)
    admin_draft=act(admin_draft,'peer_approve',9)
    act(admin_draft,'final_approve',1,403)
    admin_draft=act(admin_draft,'final_changes',2,comment='Clarify applicability.')
    admin_draft=act(admin_draft,'submit',1,reviewer_id=9)
    with factory() as db:db.get(User,9).department_id=2;db.commit()
    act(admin_draft,'peer_approve',9,403)
    with factory() as db:db.get(User,9).department_id=1;db.commit()
    admin_draft=act(admin_draft,'peer_approve',9)
    admin_draft=act(admin_draft,'final_approve',2)
    act(admin_draft,'publish',1,403)
    admin_draft=act(admin_draft,'publish',2)
    check('Administrator author publication assigns department Policy Owner',get('/policies/'+str(admin_draft['policy_id'])).json()['owner_id']==9)
    # Transaction atomicity: roll back publication, audit and notices on flush failure.
    from sqlalchemy import event
    def abort(session, *_):
        if any(isinstance(o,GovernanceEvent) and o.action=='publish' for o in session.new):
            raise RuntimeError('Synthetic transaction failure')
    atomic=approved(create(title='Atomic transaction policy'))
    with factory() as db:before=db.query(Policy).count()
    event.listen(factory.class_,'before_flush',abort)
    try:
        with TestClient(main.app,raise_server_exceptions=False) as failing:
            r=failing.post('/governance/drafts/'+str(atomic['id'])+'/actions',headers=headers[1],json={'action':'publish','expected_revision':atomic['revision']})
        check('Injected transaction failure returned failure',r.status_code==500)
    finally:event.remove(factory.class_,'before_flush',abort)
    with factory() as db:
        check('Publication rollback preserves policy and workflow',db.query(Policy).count()==before and db.get(GovernanceDraft,atomic['id']).status=='approved_pending_publication')
    main.app.dependency_overrides.clear();engine.dispose()

if __name__=='__main__':
    try:run()
    finally:
        out=Path(os.environ.get('DEREXI_TEST_EVIDENCE_DIR',str(Path(__file__).resolve().parents[2]/'docs/week8/evidence')))/'lifecycle-results.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps({'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks},indent=2)+'\n')
        print(f"{sum(c['pass'] for c in checks)} passed, {sum(not c['pass'] for c in checks)} failed")
