"""Run the approved offline assessment and preserve each execution separately."""
from datetime import datetime, timezone
from importlib import metadata, util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BACKEND = ROOT / "derexi-policy-pilot/backend"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def main():
    started = perf_counter()
    run = HERE / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run.mkdir(parents=True)
    commands = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")

    def execute(name, args):
        begin = perf_counter()
        with (run / (name+".log")).open("w",encoding="utf-8") as log:
            try:
                completed = subprocess.run(args,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code = "TIMEOUT"
        commands.append(dict(name=name, argv=[str(a) for a in args],exit=code,
                             elapsed_ms=round((perf_counter()-begin)*1000,3)))
        return code

    # Freeze the evidence inventory and hashes for this execution.
    assets = json.loads((HERE/"assets.json").read_text(encoding="utf-8-sig"))
    write_json(run/"assets.json",assets)
    packages = sorted([dict(name=d.metadata["Name"], version=d.version, requires=d.requires or [])
                       for d in metadata.distributions()],key=lambda d:d["name"].lower())
    write_json(run/"dependencies.json",packages)
    scanners={name:bool(util.find_spec(name)) for name in ("pip_audit","safety","bandit")}
    write_json(run/"scanner-availability.json",scanners)
    code=execute("controls",[sys.executable,str(HERE/"control_suite.py"),str(run/"controls.json")])
    checks=json.loads((run/"controls.json").read_text()) if (run/"controls.json").exists() else []
    if code not in (0,1):
        checks.append(dict(id="RUNNER",asset="APP",group="harness",status="ERROR",expected="suite completes",actual=code))
    pip_code=execute("dependency-consistency",[sys.executable,"-m","pip","check"])
    checks.append(dict(id="PACKAGE-CONSISTENCY",asset="PKGS",group="dependency",status="PASS" if pip_code==0 else "ERROR",
                       expected="pip check succeeds",actual=pip_code,likelihood=2,impact=3))
    requirements=(ROOT/"derexi-policy-pilot/requirements.txt").read_text()
    lower_bounds=any(">=" in line for line in requirements.splitlines() if line.strip() and not line.startswith("#"))
    checks.append(dict(id="DEPENDENCY-PINS",asset="PKGS",group="dependency",status="FAIL" if lower_bounds else "PASS",
                       expected="runtime requirement versions reproducible",actual="lower-bounded direct declarations" if lower_bounds else "no lower bounds found",
                       likelihood=3,impact=3))
    compose=(HERE.parent/"compose.yaml").read_text()
    expected=['read_only: true','65532:65532','no-new-privileges:true','127.0.0.1:8080:8080','cap_drop:','ALL','healthcheck:']
    missing=[item for item in expected if item not in compose]
    checks.append(dict(id="CONTAINER-CONFIG",asset="CONTAINER",group="configuration",status="FAIL" if missing else "PASS",
                       expected="required isolation settings declared",actual={"missing":missing,"scope":"static configuration, prior runtime evidence reused"},likelihood=3,impact=4))
    write_json(run/"results.json",checks)
    files=[BACKEND/p for p in ("main.py","security.py","dev_auth.py","schemas.py","pulse/service.py","pulse/sources.py","tests/test_security_controls.py")]
    files += list(HERE.glob("*.py"))+[HERE/"assets.json",HERE.parent/"compose.yaml",ROOT/"derexi-policy-pilot/requirements.txt"]
    write_json(run/"source-hashes.json",[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files])
    execute("inspector",[sys.executable,str(HERE/"derexi_vulnerability_inspector.py"),"--assets",str(run/"assets.json"),
                         "--results",str(run/"results.json"),"--dependencies",str(run/"dependencies.json"),"--output",str(run)])
    write_json(run/"execution.json",dict(commands=commands,elapsed_ms=round((perf_counter()-started)*1000,3),python=sys.version,
                                        scope="offline fixture and static evidence, no production database"))
    print(run)
    if (run/"findings.json").exists():
        report=json.loads((run/"findings.json").read_text())
        print(json.dumps(report["metrics"],indent=2))
    return 2 if any(c["status"]=="ERROR" for c in checks) else int(any(c["status"]=="FAIL" for c in checks))


if __name__=="__main__":
    sys.exit(main())
