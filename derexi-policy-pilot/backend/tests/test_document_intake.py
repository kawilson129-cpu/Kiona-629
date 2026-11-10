"""Document intake HTTP tests with real parsers and isolated SQLite persistence."""
import io,json,os,sys,tempfile,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
import main,document_intake as intake
from database import get_db
from models import GovernanceDraft,GovernanceEvent,Policy,User
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.exc import ProgrammingError
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
checks=[]
def check(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
 if not value:raise AssertionError(name)
def docx(text='Customer records must be handled securely.',extra=None):
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
  z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'+text+'</w:t></w:r></w:p></w:body></w:document>')
  for name,value in (extra or {}).items():z.writestr(name,value)
 return out.getvalue()
def pdf(encrypted=False,active=False,blank=False):
 w=PdfWriter();page=w.add_blank_page(width=600,height=800)
 if not blank:
  page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})})})
  stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 50 700 Td (Customer safeguards policy requirements.) Tj ET');page[NameObject('/Contents')]=w._add_object(stream)
 if encrypted:w.encrypt('private')
 if active:w.add_js('app.alert("active")')
 out=io.BytesIO();w.write(out);return out.getvalue()
def run():
 engine,factory=isolated_database();factory.configure(bind=engine)
 def override():
  with factory() as db:yield db
 main.app.dependency_overrides[get_db]=override;c=TestClient(main.app)
 auth={uid:{'Authorization':'Bearer '+c.post('/dev-auth/token',json={'user_id':uid}).json()['access_token']} for uid in (1,4,7,8,9)}
 def upload(data,name='safeguards.docx',uid=4,mime=None):return c.post('/governance/documents/preview',content=data,headers={**auth[uid],'X-File-Name':name,'Content-Type':mime or (intake.PDF_MIME if name.endswith('.pdf') else intake.DOCX_MIME)})
 def preview(data=None,**kw):
  r=upload(docx() if data is None else data,**kw);check('Valid preview '+kw.get('name','DOCX'),r.status_code==200)
  return r.json()
 cap=c.get('/governance/availability',headers=auth[4]).json();check('Availability probes both schema and parser',cap['save_available'] and cap['upload_available'])
 check('Three real templates provided',len(cap['templates'])==3 and all('Policy requirements' in t['body'] for t in cap['templates']))
 check('Employee preview denied',upload(docx(),uid=8).status_code==403)
 check('Anonymous preview denied',c.post('/governance/documents/preview',content=docx()).status_code==401)
 check('Employee capability probe denied',c.get('/governance/availability',headers=auth[8]).status_code==403)
 check('Oversized body rejected',upload(b'x'*(intake.MAX_BYTES+1)).status_code==413)
 check('Wrong extension rejected',upload(docx(),name='bad.exe').status_code==415)
 check('Mismatched signature rejected',upload(b'%PDF-1.7',name='bad.docx').status_code==422)
 check('Mismatched MIME rejected',upload(docx(),mime='text/plain').status_code==415)
 check('Corrupt ZIP rejected',upload(b'PK\x03\x04broken').status_code==422)
 check('Macro content rejected',upload(docx(extra={'word/vbaProject.bin':b'unsafe'})).status_code==422)
 check('Embedded object rejected',upload(docx(extra={'word/embeddings/object.bin':b'unsafe'})).status_code==422)
 check('Archive traversal rejected',upload(docx(extra={'../outside.txt':b'unsafe'})).status_code==422)
 check('ZIP bomb rejected',upload(docx(extra={'word/bomb.xml':b'x'*500000})).status_code==422)
 check('XML entities rejected',upload(docx(extra={'word/bad.xml':b'<!DOCTYPE a [<!ENTITY x "danger">]><a>&x;</a>'})).status_code==422)
 p=preview();check('Extracted words preserved in policy format','Customer records must be handled securely.' in p['body'] and all(x in p['body'] for x in intake.POLICY_SECTIONS))
 with factory() as db:check('Preview does not save draft',db.query(GovernanceDraft).count()==0)
 def payload(p):return {'title':'Customer records policy','body':p['body'],'version_no':'1.0','department_id':1,'import_id':p['import_id'],'confirm_document':True}
 save=payload(p)
 check('Explicit confirmation required',c.post('/governance/drafts',headers=auth[4],json={**save,'confirm_document':False}).status_code==422)
 check('Another owner cannot consume preview',c.post('/governance/drafts',headers=auth[9],json=save).status_code==404)
 r=c.post('/governance/drafts',headers=auth[4],json=save);check('Confirmed document persists through lifecycle create',r.status_code==201);d=r.json()
 check('Uploaded document remains draft',d['status']=='draft' and not d['peer_approved_by'] and not d['final_approved_by'])
 check('Preview cannot be replayed',c.post('/governance/drafts',headers=auth[4],json=save).status_code==404)
 detail=c.get('/governance/drafts/'+str(d['id']),headers=auth[4]).json()
 check('Original provenance stored in immutable creation event',detail['history'][0]['snapshot']['original_document']['sha256'] and not detail['history'][0]['snapshot']['original_document']['retained'])
 check('No original download claimed without storage',c.get('/governance/drafts/'+str(d['id'])+'/original',headers=auth[4]).status_code==404)
 check('Direct publication remains denied',c.post('/governance/drafts/'+str(d['id'])+'/actions',headers=auth[1],json={'action':'publish','expected_revision':d['revision']}).status_code==409)
 # Free previews so parser-specific cases do not hit intentional per-user quota.
 p=preview(pdf(),name='safe.pdf');check('Real PDF text extracted','Customer safeguards' in p['body']);c.delete('/governance/documents/preview/'+p['import_id'],headers=auth[4])
 check('Encrypted PDF rejected',upload(pdf(encrypted=True),name='encrypted.pdf').status_code==422)
 check('PDF active content rejected',upload(pdf(active=True),name='active.pdf').status_code==422)
 check('Image-only/blank PDF rejected',upload(pdf(blank=True),name='scan.pdf').status_code==422)
 with tempfile.TemporaryDirectory() as private:
  os.environ['DEREXI_DOCUMENT_STORAGE_DIR']=private
  original_bytes=docx();p=preview(original_bytes);save=payload(p);save['title']='Private original policy'
  r=c.post('/governance/drafts',headers=auth[4],json=save);check('Private original and draft saved',r.status_code==201);did=r.json()['id']
  original=c.get('/governance/drafts/'+str(did)+'/original',headers=auth[4]);check('Authorized original download exact bytes',original.status_code==200 and original.content==original_bytes)
  # ZIP timestamps may differ; validate stored hash and payload text instead if second boundary occurs.
  check('Original download not cacheable',original.headers['cache-control']=='no-store')
  check('Employee original download denied',c.get('/governance/drafts/'+str(did)+'/original',headers=auth[8]).status_code==403)
  check('No public static original path',c.get('/ui/'+next(Path(private).iterdir()).name).status_code==404)
  p=preview();save=payload(p)
  before=len(list(Path(private).iterdir()))
  def abort(session,*_):
   if any(isinstance(x,GovernanceEvent) and x.action=='created' for x in session.new):raise RuntimeError('Synthetic persistence failure')
  event.listen(factory.class_,'before_flush',abort)
  try:
   with TestClient(main.app,raise_server_exceptions=False) as failc:r=failc.post('/governance/drafts',headers=auth[4],json=save)
   check('Failed persistence never reports saved',r.status_code==500)
  finally:event.remove(factory.class_,'before_flush',abort)
  check('Failed transaction cleans private staged original',len(list(Path(private).iterdir()))==before)
  c.delete('/governance/documents/preview/'+p['import_id'],headers=auth[4])
 os.environ.pop('DEREXI_DOCUMENT_STORAGE_DIR',None)
 os.environ['DEREXI_DOCUMENT_STORAGE_DIR']=str(Path(main.__file__).parent/'static')
 check('Public storage directory forbidden',not c.get('/governance/availability',headers=auth[4]).json()['upload_available'])
 check('Misconfigured storage disables upload honestly',upload(docx()).status_code==503)
 os.environ.pop('DEREXI_DOCUMENT_STORAGE_DIR',None)
 class Missing(Exception):pgcode='42P01'
 def unavailable(conn,cursor,statement,params,context,many):
  if 'governance_drafts' in statement or 'governance_events' in statement:raise ProgrammingError(statement,{},Missing())
 event.listen(engine,'before_cursor_execute',unavailable)
 try:
  cap=c.get('/governance/availability',headers=auth[4]).json();check('Missing schema disables saving but permits parsing',not cap['save_available'] and cap['upload_available'])
  r=c.get('/governance/drafts',headers=auth[4]);check('Queue fails honestly with enterprise copy',r.status_code==503 and 'temporarily unavailable' in r.json()['detail'] and 'migration' not in r.text.lower())
  p=preview();r=c.post('/governance/drafts',headers=auth[4],json=payload(p));check('Save cannot succeed without tables',r.status_code==503)
 finally:event.remove(engine,'before_cursor_execute',unavailable)
 check('Existing Dashboard preserved',c.get('/dashboard/policy-health',headers=auth[4]).status_code==200)
 main.app.dependency_overrides.clear();engine.dispose()
if __name__=='__main__':
 try:run()
 finally:
  out=Path(__file__).resolve().parents[2]/'docs/governance-workspace/evidence';out.mkdir(parents=True,exist_ok=True)
  (out/'document-results.json').write_text(json.dumps({'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'checks':checks},indent=2)+'\n',encoding='utf-8')
  print(f"{sum(x['pass'] for x in checks)} passed, {sum(not x['pass'] for x in checks)} failed")
