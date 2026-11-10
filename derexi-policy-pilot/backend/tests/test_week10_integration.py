"""Week 10 handoff checks. Reuses Week 7 SQLite fixture; never connects to Supabase."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
from fastapi.testclient import TestClient
from database import get_db
from models import User, PolicyCitation, PolicyVersion
import main
from pulse.service import make_article

checks = []


def check(name, value, actual=None):
    checks.append({'name': name, 'pass': bool(value), 'actual': actual})
    print(('PASS ' if value else 'FAIL ') + name, flush=True)


def run():
    engine, factory = isolated_database()
    factory.configure(bind=engine)
    def override():
        with factory() as db:
            yield db
    main.app.dependency_overrides[get_db] = override
    c = TestClient(main.app)
    try:
        h = {i: {'Authorization': 'Bearer ' + c.post('/dev-auth/token', json={'user_id': i}).json()['access_token']}
             for i in (2, 4, 8, 9, 12)}
        with factory() as db:
            db.get(User, 12).department_id = 2
            db.commit()
        def get(path, uid=8): return c.get(path, headers=h[uid])
        def post(path, payload, uid=8): return c.post(path, json=payload, headers=h[uid])

        r = post('/ask', {'question': 'How should I handle a hypothetical policy exception?'})
        check('I01 Assistant persists uncertain answer and clarification', r.status_code == 200 and r.json()['needs_clarification'])
        answer = r.json()
        tid = answer['clarification_request_id']
        mid = answer['derexi_message_id']
        check('I02 New Assistant thread reaches requester Messaging', any(t['id'] == tid for t in get('/messages?folder=requests').json()['threads']))
        check('I03 Unmatched policy reaches administrator triage', any(t['id'] == tid for t in get('/messages?folder=triage', 2).json()['threads']))
        check('I04 Unrelated owner cannot open Assistant thread', get('/clarifications/' + str(tid), 12).status_code == 404)
        check('I05 Administrator routes thread to Jordan', post(f'/clarifications/{tid}/assign', {'assignee_id': 9}, 2).status_code == 200)
        check('I06 Assigned owner receives notification', any(n.get('thread_id') == tid for n in get('/messages/notifications', 9).json()['items']))
        check('I07 Owner response persists through Messaging', post(f'/clarifications/{tid}/replies', {'body': 'Ask your manager and document the exception.'}, 9).status_code == 201)
        detail = get('/clarifications/' + str(tid)).json()
        check('I08 Employee sees owner response with original question', any('document the exception' in x['body'] for x in detail['replies']))
        check('I09 Owner reply notifies employee', any(n.get('thread_id') == tid for n in get('/messages/notifications').json()['items']))
        check('I10 Empty Assistant input rejected', post('/ask', {'question': '   '}).status_code == 422)

        # The existing fixture deliberately returns no PostgreSQL search matches.
        # Attach a real citation to its stored answer to exercise department aggregation;
        # this does NOT verify pg_trgm ranking or a live generated answer.
        with factory() as db:
            version = db.query(PolicyVersion).filter_by(policy_id=48).first()
            db.add(PolicyCitation(message_id=mid, policy_version_id=version.id, excerpt='Synthetic citation for dashboard integration'))
            db.commit()
        rate = post('/feedback', {'message_id': mid, 'rating': True})
        check('I11 Answer feedback accepted', rate.status_code == 201)
        check('I12 Administrator dashboard counts saved helpful feedback', get('/dashboard/policy-health', 2).json()['feedback'] == {'total': 1, 'helpful': 1, 'not_helpful': 0, 'helpful_rate': 1.0})
        check('I13 Department owner dashboard includes cited feedback', get('/dashboard/policy-health', 9).json()['feedback']['helpful'] == 1)
        check('I14 Other department cannot see cited feedback', get('/dashboard/policy-health', 12).json()['feedback']['total'] == 0)
        update = post('/feedback', {'message_id': mid, 'rating': False, 'comment': 'Needs clearer steps.'})
        check('I15 Re-rating updates existing row', update.status_code == 201 and update.json()['id'] == rate.json()['id'] and get('/dashboard/policy-health', 2).json()['feedback']['not_helpful'] == 1)
        check('I16 Another employee cannot rate private answer', post('/feedback', {'message_id': mid, 'rating': True}, 4).status_code == 404)
        check('I17 Non-boolean rating rejected', post('/feedback', {'message_id': mid, 'rating': 'yes'}).status_code == 422)
        bad = post('/feedback', {'message_id': answer['user_message_id'], 'rating': True})
        check('I18 Employee questions cannot pollute answer feedback', bad.status_code == 422, bad.status_code)

        incident = post('/incidents', {'description': 'A suspicious customer document was received.'})
        check('I19 Employee incident report accepted', incident.status_code == 201)
        iid = incident.json()['id']
        check('I20 Incident reaches authorized administrator', any(i['id'] == iid for i in get('/incidents', 2).json()))
        check('I21 Owner cannot triage incident', c.patch(f'/incidents/{iid}', headers=h[9], json={'status': 'triaged'}).status_code == 403)
        check('I22 Administrator triage and assignment persist', c.patch(f'/incidents/{iid}', headers=h[2], json={'status': 'triaged', 'assigned_to': 9}).status_code == 200)
        check('I23 Explicit handler sees assigned incident', any(i['id'] == iid and i['status'] == 'triaged' for i in get('/incidents', 9).json()))
        check('I24 Other department incident access denied', get('/incidents', 12).json() == [])
        check('I25 Employee dashboard denied', get('/dashboard/policy-health').status_code == 403)

        for source, url, accepted in [
            ('FDIC', 'https://www.fdic.gov/news/example', True),
            ('FDIC', 'https://fdic.gov/news/example', True),
            ('FDIC', 'https://content.govdelivery.com/accounts/USFDIC/bulletins/abc', True),
            ('FDIC', 'https://content.govdelivery.com/accounts/OTHER/bulletins/abc', False),
            ('FDIC', 'https://content.govdelivery.com/accounts/USFDIC/bulletins/../../OTHER/bulletins/abc', False),
            ('FDIC', 'https://content.govdelivery.com/accounts/USFDIC/bulletins/%2e%2e/OTHER', False),
            ('FDIC', 'https://secure-fdic-verification.example/login', False),
            ('FDIC', 'https://www.fdic.gov.evil.example/login', False),
            ('FDIC', 'https://evilfdic.gov/login', False),
            ('FDIC', 'https://www.fdic.gov:444/login', False),
            ('FDIC', 'https://www.fdic.gov:bad/login', False),
            ('FDIC', 'https://www.fdic.gov\\@evil.example/login', False),
            ('FDIC', 'https://user@www.fdic.gov/news', False),
            ('NIST', 'https://csrc.nist.gov/pubs/example', True),
            ('Federal Register', 'https://www.federalregister.gov/documents/example', True),
            ('Federal Reserve', 'https://www.federalreserve.gov/newsevents/example', True),
            ('Unknown', 'https://www.fdic.gov/news/example', False),
        ]:
            article = make_article(source, 'Synthetic regulatory update', url, '2026-11-01')
            check('I26 Publisher binding ' + source + ' ' + url, bool(article) == accepted)
    finally:
        main.app.dependency_overrides.clear()
        engine.dispose()
