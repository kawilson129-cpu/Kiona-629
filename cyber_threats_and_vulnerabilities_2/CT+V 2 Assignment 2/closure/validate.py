"""Validate closure metrics, preserved outcomes and deliverable links."""
from datetime import datetime,timezone
import csv,hashlib,json,re
from pathlib import Path
from urllib.parse import unquote
B=Path(__file__).resolve().parent
A=B.parent
old=json.loads((A/"runs/20261109T124059033126Z/results.json").read_text())
new=json.loads((A/"runs/20261109T125144008620Z/results.json").read_text())
assert {r["id"]:r["status"] for r in old}=={r["id"]:r["status"] for r in new}
print("PASS original 33 check identities and outcomes preserved on retest")
assets=json.loads((B/"assets-reconciled.json").read_text())
assert len(assets)==13 and sum(a["current_control_assessed"] for a in assets)==6
print("PASS 13 reconciled assets and 6 directly assessed assets")
audit=json.loads((B/"advisories/assessment.json").read_text())
assert audit["queried"]==35 and audit["unavailable"]==0
assert len(audit["active_advisories"])==4
report=json.loads((B/"inspector/findings.json").read_text())
assert len(report["findings"])==5 and report["metrics"]["tests"]==dict(PASS=27,FAIL=6,ERROR=0,BLOCKED=0)
assert report["metrics"]["distinct_triaged_advisories"]==2
print("PASS advisory aliases and finding counts reconcile without changing executed test totals")
with (A/"remediation-tracking.csv").open(newline="",encoding="utf-8-sig") as f:
    tracker=list(csv.DictReader(f))
assert len(tracker)==5 and all(r["status"]=="OPEN" and not r["closed_at"] for r in tracker)
print("PASS all five unresolved findings tracked")
for doc in B.glob("*.md"):
    for link in re.findall(r"\]\(([^)]+)\)",doc.read_text(encoding="utf-8-sig")):
        if not link.startswith(("https:","http:")):
            assert (doc.parent/unquote(link)).exists(),(doc,link)
print("PASS closure document local links")
paths=list(A.glob("*.py"))+[B/"reconcile.py",B/"track_workflow.py",B/"validate.py",B/"advisories-triaged.json",A/"remediation-tracking.csv"]
manifest=dict(captured_at=datetime.now(timezone.utc).isoformat(),files=[dict(path=str(p.relative_to(A)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
(B/"closure-source-hashes.json").write_text(json.dumps(manifest,indent=2))
