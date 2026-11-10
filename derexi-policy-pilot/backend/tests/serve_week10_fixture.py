"""Week 10 browser UAT: existing Week 9 BFF/provider and Week 7 SQLite fixture.

No production routes or configuration are altered. Only this loopback test app
has outage controls. All simulated writes disappear when the process exits.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import serve_week9_fixture as fixture
from fastapi import Depends
from fastapi.responses import JSONResponse
from security import require_admin
from sqlalchemy import event
from sqlalchemy.exc import ProgrammingError
from models import IncidentCategory, Policy, PolicyVersion, PolicyCitation, Message, Conversation
from test_document_intake import docx
import pulse.routes

for uid in (9, 12):
    fixture.subjects[uid] = f'00000000-0000-0000-0000-{uid:012d}'
os.environ['DEREXI_AUTH_SUBJECT_MAP'] = json.dumps({sub: uid for uid, sub in fixture.subjects.items()})
state = {'available': True, 'feedback': True}

class Missing(Exception):
    pgcode = '42P01'

@event.listens_for(fixture.factory.kw['bind'], 'before_cursor_execute')
def outage(conn, cursor, statement, params, context, many):
    if not state['available'] and ('governance_drafts' in statement or 'governance_events' in statement):
        raise ProgrammingError(statement, {}, Missing())

@fixture.main.app.post('/__fixture/state')
def switch(available: bool = True, feedback: bool = True, actor=Depends(require_admin)):
    state.update(available=available, feedback=feedback)
    return state

@fixture.main.app.middleware('http')
async def feedback_outage(request, call_next):
    if request.url.path == '/feedback' and request.method == 'POST' and not state['feedback']:
        return JSONResponse({'detail': 'Feedback is temporarily unavailable. Please try again.'}, status_code=503)
    return await call_next(request)

article = {'id': 'week10-fdic', 'title': 'Customer safeguards policy review',
           'url': 'https://www.fdic.gov/news/financial-institution-letters/fixture',
           'source': 'FDIC', 'agency': 'FDIC', 'published': '2026-11-01',
           'category': 'Banking & Finance', 'status': 'Supervisory Guidance',
           'summary': 'Synthetic article for workflow verification; no regulatory claim.',
           'score': 10, 'classified_by': 'source', 'doc_type': 'Guidance'}
pulse.routes.get_feed = lambda limit=60: {'articles': [article], 'sources': {}, 'fetched_at': '2026-11-10T12:00:00Z'}

with fixture.factory() as db:
    db.add(IncidentCategory(id=1, name='Suspicious document', default_severity='high'))
    db.commit()

if __name__ == '__main__':
    import uvicorn
    with tempfile.TemporaryDirectory(prefix='derexi-week10-') as private:
        os.environ['DEREXI_DOCUMENT_STORAGE_DIR'] = private
        out = Path(__file__).resolve().parents[3] / 'semester_5/DeRexi_Week 10/evidence/inputs'
        out.mkdir(parents=True, exist_ok=True)
        (out / 'Customer safeguards.docx').write_bytes(docx('Verify authorization before sharing customer records.'))
        print('WEEK 10 ISOLATED FIXTURE: mock provider/feed, SQLite; no Supabase', flush=True)
        uvicorn.run(fixture.main.app, host='127.0.0.1', port=8031, proxy_headers=False, access_log=False)
