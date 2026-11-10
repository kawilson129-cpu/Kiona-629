"""Targeted messaging regressions, isolated rows, verified dev credentials."""
import sys
import os
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
from fastapi.testclient import TestClient
import main
from database import get_db
from models import ClarificationRequest, User
import dev_auth

RESULTS = []


def check(name, condition):
    RESULTS.append(bool(condition))
    print(('PASS  ' if condition else 'FAIL  ') + name)


def run():
    engine, factory = isolated_database()
    factory.configure(bind=engine)
    db = factory()
    main.app.dependency_overrides[get_db] = lambda: db
    client = TestClient(main.app)
    def auth(uid):
        r = client.post('/dev-auth/token', json={'user_id': uid})
        assert r.status_code == 200, r.text
        return {'Authorization': 'Bearer ' + r.json()['access_token']}
    employee, owner, admin, other = auth(8), auth(9), auth(2), auth(12)
    try:
        thread = ClarificationRequest(user_id=8, assigned_to=9, policy_id=48, status='open', reason='Edge fixture')
        db.add(thread); db.commit()
        tid = thread.id
        client.post(f'/clarifications/{tid}/replies', json={'body':'Owner response'}, headers=owner)
        client.post(f'/clarifications/{tid}/assign', json={'assignee_id':12}, headers=admin)
        permissions = client.get(f'/clarifications/{tid}',headers=owner).json()['permissions']
        check('former owner remains an authorized historical reader', client.get(f'/clarifications/{tid}',headers=owner).status_code == 200)
        check('former owner has read-only permissions', permissions['can_reply'] is False)
        denied = client.post(f'/clarifications/{tid}/replies', json={'body':'Former owner reply'},headers=owner)
        check('reply endpoint enforces its advertised permissions', denied.status_code == 403)
        client.post(f'/clarifications/{tid}/read',headers=other)
        client.post(f'/clarifications/{tid}/assign',json={'assignee_id':9},headers=admin)
        client.post(f'/clarifications/{tid}/assign',json={'assignee_id':12},headers=admin)
        check('reassignment notifies a previous assignee who already read it', client.get(f'/clarifications/{tid}',headers=other).json()['unread_count'] >= 1)

        db.add_all([ClarificationRequest(user_id=8,assigned_to=9,policy_id=48,status='open',reason='Notification fixture '+str(i)) for i in range(105)])
        db.commit()
        notices=client.get('/messages/notifications',headers=owner).json()
        mailbox=client.get('/messages',headers=owner).json()
        check('notification preview stays limited to 20 items',len(notices['items']) == 20)
        check('unread total includes more than 100 unread threads',notices['unread_total'] == 105)
        check('list and notification totals agree',notices['unread_total'] == mailbox['unread_total'])
        db.add(ClarificationRequest(user_id=8,assigned_to=None,status='open',reason='Triage fixture')); db.commit()
        check('unrelated employee list omits all private threads',client.get('/messages?folder=requests',headers=auth(3)).json()['threads'] == [])
        check('unrelated owner notifications contain no private previews',client.get('/messages/notifications',headers=auth(4)).json()['items'] == [])
        for action in ['read','resolve','close','reopen']:
            check('unrelated employee cannot '+action,client.post(f'/clarifications/{tid}/{action}',headers=auth(3)).status_code == 404)
        check('owner cannot reopen a resolved employee request',
            client.post(f'/clarifications/{tid}/resolve',headers=other).status_code == 200 and
            client.post(f'/clarifications/{tid}/reopen',headers=other).status_code == 403)
        check('admin can reopen with organization oversight',client.post(f'/clarifications/{tid}/reopen',headers=admin).status_code == 200)
        check('anonymous notification request is denied',client.get('/messages/notifications').status_code == 401)
        token=owner['Authorization'][7:]
        check('invalid signature rejected',client.get('/messages',headers={'Authorization':'Bearer '+token[:-8]+'tampered'}).status_code == 401)
        remote=TestClient(main.app,client=('203.0.113.10',1234))
        check('remote clients cannot retrieve the dev identity roster',remote.get('/auth/config').status_code in (403,404))
        check('remote clients cannot reuse a local development token',remote.get('/messages',headers=owner).status_code in (401,403,404))
        check('foreign-origin dev token request rejected',client.post('/dev-auth/token',json={'user_id':8},headers={'Origin':'https://untrusted.example'}).status_code == 403)
        check('forwarded development token rejected',client.get('/messages',headers={**owner,'X-Forwarded-For':'127.0.0.1'}).status_code == 403)
        forged_role=dev_auth.issue_token(8,'fixture8@example.invalid','System Administrator')['access_token']
        check('token role labels cannot elevate a database Employee',client.get('/messages?folder=all',headers={'Authorization':'Bearer '+forged_role}).status_code == 403)
        db.get(User,2).role_id=1; db.commit()
        check('database role demotion applies to an already-issued token',client.get('/messages?folder=all',headers=admin).status_code == 403)
        db.get(User,2).role_id=3; db.commit()
        client.post(f'/clarifications/{tid}/replies',json={'body':'Administrative reply'},headers=admin)
        notice=next(n for n in client.get('/messages/notifications',headers=employee).json()['items'] if n['thread_id']==tid)
        check('reply notification names the actual sender',notice['actor']=='Lucy Chen')
        assigned=client.post(f'/clarifications/{tid}/assign',json={'assignee_id':2},headers=admin).json()
        check('participant metadata preserves the administrator role',
              next(p for p in assigned['participants'] if p['id']==2)['role']=='System Administrator')
        try:
            os.environ['DEREXI_ENV']='production'
            secure=TestClient(main.app,base_url='https://testserver')
            check('production rejects development tokens',secure.get('/messages',headers=owner).status_code == 401)
            check('production refuses local identity issuance',secure.post('/dev-auth/token',json={'user_id':8}).status_code == 404)
            check('production config exposes no test identities',secure.get('/auth/config').json()['identities'] == [])
            os.environ['DEREXI_ENV']='staging'
            check('unrecognized deployment environments cannot enable dev auth',secure.post('/dev-auth/token',json={'user_id':8}).status_code == 404)
        finally:
            os.environ['DEREXI_ENV']='test'
    finally:
        main.app.dependency_overrides.clear()
        db.close(); engine.dispose()
    print(f'{sum(RESULTS)} passed, {len(RESULTS)-sum(RESULTS)} failed, {len(RESULTS)} checks')
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    try: sys.exit(run())
    except Exception:
        traceback.print_exc(); sys.exit(2)
