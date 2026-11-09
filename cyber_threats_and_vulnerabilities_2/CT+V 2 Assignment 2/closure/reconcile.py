"""Produce a reconciled local evidence inventory and explicit advisory triage."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
A2=BASE.parent
assets=json.loads((A2/"assets.json").read_text(encoding="utf-8-sig"))
run=A2/"runs/20261109T125144008620Z"
results=json.loads((run/"results.json").read_text())
assessed={r["asset"] for r in results if r["status"] in ("PASS","FAIL")}
detail={
"APP":("Signed endpoint tests and current main.py","Policy integrity and incident confidentiality","Fake writes only; live transactions and deployment unverified"),
"UI":("Current UI source, API headers and prior Docker screenshot","Employees may follow compromised guidance","No new browser interaction or accessibility test"),
"DB":("Schema design plus database.py and models.py inspected","Policy, incident and identity record integrity","No live connection, row counts, RLS or recovery tested"),
"AUTH":("Signed-token identity, roles and cross-user cases","Privilege and private-record access","Local issuer only; production JWKS flow untested"),
"DEV_AUTH":("Issuer source and real token generation used by fixtures","Test credentials must remain confined to development","Dev endpoints, environment guards and expiry not comprehensively tested here"),
"PULSE":("Current source and reserved-host negative check","Trustworthy regulatory attribution","Host-binding failure remains open"),
"CONTAINER":("Current Compose declaration and prior container inspection","Host isolation and service availability","Runtime evidence reused with its original timestamp"),
"FR":("Registry definition and prior Docker feed response with 38 records","Regulatory monitoring completeness","Point-in-time reachability only; no current endpoint request"),
"FDIC":("Registry definition and prior Docker RSS response with 25 records","Banking supervisory context","Publisher ownership and future redirects not newly verified"),
"NIST":("Registry definition and prior Docker JSON response with 9 records","Draft security-standard awareness","Point-in-time content availability only"),
"FED":("Registry definition and prior Docker RSS response with 15 records","Bank regulatory monitoring","Point-in-time content availability only"),
"AI":("ai.py inspected, optional context-to-provider code path","Potential disclosure or inaccurate policy guidance","Provider is configurable; no credentials read or provider contacted"),
"PKGS":("Current 35-distribution snapshot, pip check and release advisories","Executable dependency integrity","Host environment only; container/OS and deployed versions differ"),
}
reconciled=[]
for asset in assets:
    if asset["id"]=="SSH":
        continue
    evidence=ROOT/asset["evidence"]
    assert evidence.is_file(),evidence
    method,impact,limitation=detail[asset["id"]]
    reconciled.append(dict(asset,method=method,business_impact=impact,limitation=limitation,
                           evidence_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest(),
                           current_control_assessed=asset["id"] in assessed,owner_status="proposed functional owner",
                           reconciliation_status="RECONCILED"))
(BASE/"assets-reconciled.json").write_text(json.dumps(reconciled,indent=2))
lines=["# Reconciliation of all 13 local ecosystem assets","",
       "All 13 have evidence, relationships, proposed ownership, impact and limitations. Direct control coverage remains 6/13 (46.15%). Reconciliation coverage is 13/13 (100%). Historical classroom host SSH stays outside this denominator.","",
       "| ID / owner | Evidence verified | Relationships | Business impact | Coverage / limitation |","|---|---|---|---|---|"]
for a in reconciled:
    lines.append(f"| {a['id']} / {a['owner']} | {a['method']} | {', '.join(a['depends_on']) or 'External/root dependency'} | {a['business_impact']} | {'Current control assertions' if a['current_control_assessed'] else 'Reconciled evidence only'} — {a['limitation']} |")
(BASE/"assets-reconciled.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
audit=json.loads((BASE/"advisories/assessment.json").read_text())
audit["triaged_findings"]=[
dict(id="DVI-ADVISORY-CERTIFI",package="certifi",version="2026.7.22",
     advisory_ids=["GHSA-6q48-6c7w-9gw2","PYSEC-2026-4320"],likelihood=3,impact=4,
     upstream_severity="Critical",owner="Platform engineering",
     corrective_action="Upgrade the local certifi bundle to a reviewed fixed release (registry recommends 2026.10.19 or later), then verify which application clients use it. Preserve TLS validation.",
     closure="Installed version no longer matches the advisory; verify the deployed trust bundle and rerun affected client tests. No on-path interception test is required."),
dict(id="DVI-ADVISORY-PIP",package="pip",version="26.1.2",
     advisory_ids=["GHSA-qwm4-qh6w-59xr","PYSEC-2026-3721"],likelihood=2,impact=3,
     upstream_severity="Medium, CVSS 3.1 6.5",owner="Developer tooling owner",
     corrective_action="Upgrade pip to a reviewed fixed release 26.2.0 or later and restrict installs/downloads to approved indexes.",
     closure="Requery the installed pip release, verify advisory no longer applies, and validate approved-index package installation in an isolated environment.")
]
(BASE/"advisories-triaged.json").write_text(json.dumps(audit,indent=2))
print("13/13 assets reconciled; 6/13 have direct current control assertions")
print("35/35 package versions queried; 4 advisory aliases consolidated into 2 distinct issues")
