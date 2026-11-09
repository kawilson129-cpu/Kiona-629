import os,sys,json,runpy,sqlite3,hashlib,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
os.environ.update(DATABASE_URL="sqlite:///never-open.sqlite",DEREXI_ENV="test",DEREXI_DEV_AUTH="1",PYTHONDONTWRITEBYTECODE="1")
sys.path.insert(0,str(Path("derexi-policy-pilot/backend").resolve()))
h=runpy.run_path("derexi-policy-pilot/backend/tests/test_security_controls.py")
import main,security,dev_auth
class Rows:
    def __init__(self,row): self.row=row
    def mappings(self): return self
    def first(self): return self.row
class Session(h["FakeSession"]):
    def execute(self,stmt,params=None):
        if "lower(u.email)" in str(stmt):
            row=dict(id=9001,email="test@example.invalid",first_name="Synthetic",last_name="Actor",department_id=1,role=self.actor_role)
            return Rows(row if params["email"]==row["email"] else None)
        return super().execute(stmt,params)
results=[]
for actor in ["Employee","Policy Owner","System Administrator"]:
    s=Session()
    s.actor_role=actor
    main.app.dependency_overrides[main.get_db]=lambda:s
    token=dev_auth.issue_token(9001,"test@example.invalid",actor)["access_token"]
    headers={"Authorization":"Bearer "+token}
    cases=[
      ("identity","GET","/me",None,200),
      ("governance","GET","/dashboard/policy-health",None,403 if actor=="Employee" else 200),
      ("strict rating","POST","/feedback",dict(message_id=1,rating="yes"),422),
      ("bounded feedback","POST","/feedback",dict(message_id=1,rating=True,comment="x"*50000),422),
      ("policy approval","POST","/policies",dict(title="Synthetic",status="approved",version=dict(body="Synthetic only")),403 if actor=="Employee" else 201),
    ]
    for name,method,url,payload,expected in cases:
        before=len(s.added)
        r=h["CLIENT"].request(method,url,json=payload,headers=headers)
        results.append(dict(actor=actor,case=name,expected=expected,actual=r.status_code,passed=r.status_code==expected,fake_writes=len(s.added)-before))
    r=h["CLIENT"].get("/me",headers={"Authorization":"Bearer "+token+"corrupt"})
    results.append(dict(actor=actor,case="tampered signature",expected=401,actual=r.status_code,passed=r.status_code==401))
(OUT/"authenticated-results.json").write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
# Recovery uses only synthetic in-memory SQLite. Backup and restore are actually executed.
started=time.perf_counter()
source=sqlite3.connect(":memory:")
source.execute("create table policies(id integer primary key, body text)")
source.execute("insert into policies values (1, 'Synthetic policy v1')")
source.commit()
backup=sqlite3.connect(":memory:")
source.backup(backup)
source.execute("update policies set body='Simulated corruption'")
source.commit()
damaged=source.execute("select body from policies").fetchone()[0]
backup.backup(source)
restored=source.execute("select body from policies").fetchone()[0]
assert damaged != restored and restored=="Synthetic policy v1"
result=dict(scope="SIMULATED recovery, synthetic in-memory SQLite only",restored=True,sha256=hashlib.sha256(restored.encode()).hexdigest(),elapsed_ms=round((time.perf_counter()-started)*1000,3),rows=1,live_restore=False)
(OUT/"recovery-results.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result))
