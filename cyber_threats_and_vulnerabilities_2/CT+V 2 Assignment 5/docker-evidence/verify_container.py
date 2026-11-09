import errno,json,os,urllib.request
from pathlib import Path
checks={}
checks["uid_nonroot"]=os.getuid()==65532
status=Path("/proc/self/status").read_text()
checks["capabilities_dropped"]="CapEff:\t0000000000000000" in status
checks["no_new_privileges"]="NoNewPrivs:\t1" in status
checks["no_database_environment"]=not any("DATABASE" in k or "SUPABASE" in k for k in os.environ)
checks["no_database_module"]=not Path("/app/database.py").exists()
try:
    Path("/app/write-probe").write_text("synthetic")
    checks["readonly_root"]=False
except OSError as exc:
    checks["readonly_root"]=exc.errno==errno.EROFS
for path in ("/healthz","/"):
    with urllib.request.urlopen("http://127.0.0.1:8080"+path,timeout=5) as r:
        body=r.read().decode()
        checks[path+" status"]=r.status==200
        checks[path+" CSP"]="default-src 'none'" in r.headers.get("Content-Security-Policy","")
        if path=="/":
            checks["synthetic_label"]="Synthetic fixture" in body
            checks["metric_count"]="1 unique normalized items" in body
            checks["source_bars"]=body.count("<meter")==4
            checks["simulated_failures"]=body.count("unavailable, 0 items")==3
print(json.dumps(checks,indent=2))
assert all(checks.values()),checks
