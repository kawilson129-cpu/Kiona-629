"""Week 8 browser fixture. Synthetic rows only; no live PostgreSQL connections."""
import sys
from pathlib import Path
from threading import Lock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
import main
from database import get_db
from models import User
engine,factory=isolated_database();factory.configure(bind=engine)
lock=Lock()
with factory() as db:
    db.get(User,7).department_id=2
    db.commit()
def override():
    with lock,factory() as db:yield db
main.app.dependency_overrides[get_db]=override
# Deterministic government feed avoids network dependencies in visual tests.
import pulse.routes
pulse.routes.get_feed=lambda limit=60:{'articles':[{'id':'fixture-week8','title':'Review customer safeguards after a regulatory update',
    'url':'https://www.fdic.gov/news/financial-institution-letters/fixture','source':'FDIC','agency':'FDIC',
    'published':'2026-11-01','category':'Banking & Finance','status':'Supervisory Guidance',
    'summary':'Illustrative article for policy governance testing. No real regulatory change is asserted.',
    'score':10,'classified_by':'source','doc_type':'Guidance'}], 'sources':{},'fetched_at':'2026-11-10T12:00:00Z'}
if __name__=='__main__':
    import uvicorn
    print('LOCAL WEEK 8 FIXTURE: illustrative data, no Supabase writes',flush=True)
    uvicorn.run(main.app,host='127.0.0.1',port=8028,proxy_headers=False,access_log=False)
