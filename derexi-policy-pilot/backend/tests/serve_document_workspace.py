"""Dedicated document workspace browser server; SQLite only, no live writes."""
import os,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import serve_week8_fixture as fixture
from sqlalchemy import event
from sqlalchemy.exc import ProgrammingError
from models import Department,PolicyVersion,Policy
from fastapi import Depends
from security import require_admin
from test_document_intake import docx,pdf
state={'available':True}
class Missing(Exception):pgcode='42P01'
@event.listens_for(fixture.engine,'before_cursor_execute')
def availability(conn,cursor,statement,params,context,many):
 if not state['available'] and ('governance_drafts' in statement or 'governance_events' in statement):
  raise ProgrammingError(statement,{},Missing())
@fixture.main.app.post('/__fixture/workspace')
def switch(available:bool,actor=Depends(require_admin)):
 state['available']=available;return {'available':available}
with fixture.factory() as db:
 db.get(Policy,1).title='Information handling'
 for d,name in zip(db.query(Department).order_by(Department.id),['Compliance','Information Technology','Operations','Human Resources','Marketing','Lending','Wealth Management']):d.name=name
 for v in db.query(PolicyVersion):v.title='Employee guidance';v.body='Contact your department owner for guidance on policy exceptions.'
 db.commit()
out=Path(__file__).resolve().parents[2]/'docs/governance-workspace/evidence/inputs';out.mkdir(parents=True,exist_ok=True)
(out/'Customer safeguards.docx').write_bytes(docx('Purpose\nProtect customer information.\n\nScope\nAll employees handling customer records.\n\nPolicy requirements\nVerify authorization before sharing customer information.\n\nResponsibilities\nDepartment owners oversee compliance.\n\nExceptions\nDocument and escalate exceptions before proceeding.\n\nRelated guidance\nRefer to the information security policy.'))
(out/'Customer safeguards.pdf').write_bytes(pdf())
if __name__=='__main__':
 import uvicorn
 with tempfile.TemporaryDirectory(prefix='derexi-workspace-private-') as private:
  os.environ['DEREXI_DOCUMENT_STORAGE_DIR']=private
  uvicorn.run(fixture.main.app,host='127.0.0.1',port=8030,proxy_headers=False,access_log=False)
