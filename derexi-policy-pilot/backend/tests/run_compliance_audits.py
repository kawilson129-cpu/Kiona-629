"""Execute original audit assertions without overwriting their baseline evidence.

C-01 targets the explicit secured application; C-02/C-03 exercise the real shared
handlers on the preserved compatibility app. Positive role tests live separately.
"""
import importlib
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import main
from auth import AuthSettings, SupabaseJWTVerifier
from secure_api import create_app
from fastapi.testclient import TestClient


def run():
    security=importlib.import_module("test_security_controls")
    results=[]
    # Use the original C-02 assertions and tripwire exactly as supplied.
    for name in sorted(n for n in vars(security) if n.startswith("test_c02")):
        security.CURRENT_TEST=name
        try:
            getattr(security,name)()
        finally:
            security.teardown()
    results.extend(security.RESULTS)
    security.RESULTS.clear()
    security.CLIENT.close()
    settings=AuthSettings("https://audit.invalid","https://audit.invalid/jwks","https://audit.invalid/auth/v1")
    security.APP=create_app(SupabaseJWTVerifier(settings,jwk_client=Mock()),{})
    security.CLIENT=TestClient(security.APP,raise_server_exceptions=False)
    for name in sorted(n for n in vars(security) if n.startswith("test_c01")):
        security.CURRENT_TEST=name
        try:
            getattr(security,name)()
        finally:
            security.teardown()
    results.extend(security.RESULTS)
    security.CLIENT.close()
    pulse=importlib.import_module("test_c03_audit")
    try:
        for name in ("req1_registry_is_closed","req2_attribution","req3_url_safety", "req4_hostile_content",
                     "req5_dates","req6_dedupe","req7_classification","req8_9_failure_and_stale",
                     "req10_api_limits","req11_no_fabrication"):
            getattr(pulse,name)()
    finally:
        pulse.service.fetch_source=pulse._real_fetch_source
        pulse.reset_cache()
    for item in pulse.RESULTS:
        item=dict(item)
        item["control"]="C-03"
        item["original_basis"]=item.get("basis")
        item["original_evidence"]=item.get("evidence")
        if "prior evidence" not in item.get("basis",""):
            item["basis"]="executed in current audit run"
            item["evidence"]="this audit_results.json (current execution)"
        elif item["id"]=="C03-55" and os.environ.get("DEREXI_BROWSER_EVIDENCE"):
            path=Path(os.environ["DEREXI_BROWSER_EVIDENCE"])
            browser=json.loads(path.read_text())
            tested=datetime.fromisoformat(browser["date"].replace("Z","+00:00"))
            if not 0 <= (datetime.now(timezone.utc)-tested).total_seconds() < 3600:
                raise RuntimeError("Run the browser verification before the current audit")
            if not any(c["id"]=="C03-55" and c["status"]=="PASS" for c in browser["checks"]):
                raise RuntimeError("Current browser evidence did not pass C03-55")
            item["basis"]="executed in Chromium in this verification session"
            item["evidence"]=str(path)
        elif item["id"]=="C03-55":
            item["status"]="NOT TESTED"
            item["basis"]="Fresh browser evidence required; historical evidence retained separately"
        results.append(item)
    summary={}
    for control in ("C-01","C-02","C-03"):
        selected=[r for r in results if r.get("control")==control]
        summary[control]={s:sum(r["status"]==s for r in selected) for s in ("PASS","FAIL","BLOCKED","NOT TESTED")}
    now=datetime.now(timezone.utc)
    output=Path(__file__).resolve().parents[2]/"docs/compliance/evidence"/now.strftime("resume_%Y-%m-%dT%H%M%S%fZ")
    output.mkdir(parents=True,exist_ok=False)
    (output/"audit_results.json").write_text(json.dumps({"timestamp":now.isoformat(),
        "mode":"original assertions; synthetic fixtures; DB engine tripwire; no live requests",
        "targets":{"C-01":"secured API assembly","C-02":"shared FastAPI handlers","C-03":"Pulse normalization/API"},
        "summary":summary,"results":results},indent=2))
    print("AUDIT SUMMARY",json.dumps(summary))
    print("EVIDENCE",output/"audit_results.json")
    return 1 if any(v["FAIL"] or v["BLOCKED"] or v["NOT TESTED"] for v in summary.values()) else 0


if __name__=="__main__":
    sys.exit(run())
