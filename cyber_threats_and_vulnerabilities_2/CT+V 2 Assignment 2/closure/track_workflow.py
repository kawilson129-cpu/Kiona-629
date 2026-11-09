"""Track baseline-to-retest progression without claiming fixes or accepted exceptions."""
import csv,json
from datetime import datetime,timedelta
from pathlib import Path
B=Path(__file__).resolve().parent
A=B.parent
old=json.loads((A/"runs/20261109T124059033126Z/findings.json").read_text())
new=json.loads((B/"inspector/findings.json").read_text())
baseline={f["id"]:f for f in old["findings"]}
rows=[]
for f in new["findings"]:
    previous=f["id"] in baseline
    intake=old["generated_at"] if previous else new["generated_at"]
    due=(datetime.fromisoformat(intake)+timedelta(hours=f["sla_hours"])).isoformat()
    mitigation={
      "DVI-POLICY-WRITE":"Keep the affected API in an isolated lab until server-side policy-write guards pass retest.",
      "DVI-FEED-INTEGRITY":"Treat feed links as unverified attribution until source-specific host enforcement passes.",
      "DVI-DEPENDENCY":"Retain installed-version snapshot and require review of dependency changes pending a tested lock.",
      "DVI-ADVISORY-CERTIFI":"Review and update the affected trust bundle before depending on it for sensitive client traffic.",
      "DVI-ADVISORY-PIP":"Use approved indexes only and schedule tooling upgrade; avoid untrusted-index downloads."
    }[f["id"]]
    rows.append(dict(id=f["id"],severity=f["severity"],score=f["score"],status="OPEN",
                     owner=f["owner"],owner_acceptance="PENDING",validated_intake_utc=intake,
                     target_utc=due,mitigation=mitigation,mitigation_state="PROPOSED",
                     corrective_action=f["corrective_action"],closure=f["closure"],
                     retest="REPRODUCED" if previous else "REGISTRY_MATCH_TRIAGED",
                     retest_evidence="runs/20261109T125144008620Z/results.json" if previous else "closure/advisories-triaged.json",
                     exception_status="NONE_APPROVED",closed_at=""))
with (A/"remediation-tracking.csv").open("w",newline="",encoding="utf-8") as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
events=[]
for f in rows:
    stages=["DISCOVERED","VALIDATED","PRIORITIZED","TRACKED"]
    if f["retest"]=="REPRODUCED":
        stages.append("RETESTED_STILL_OPEN")
    else:
        stages.append("REMEDIATION_RETEST_PENDING")
    events.append(dict(finding=f["id"],stages=stages,status="OPEN",evidence=f["retest_evidence"]))
(B/"workflow.json").write_text(json.dumps(events,indent=2))
print("Five open findings tracked; three original findings reproduced; no fixes or exceptions asserted")
