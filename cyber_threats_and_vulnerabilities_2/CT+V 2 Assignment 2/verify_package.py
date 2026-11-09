import ast,json,re
from pathlib import Path
from urllib.parse import unquote
base=Path("cyber_threats_vulnerabilities_2_final/assignment2")
for path in base.glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"))
print("PASS Python syntax for all assignment2 scripts")
assets=json.loads((base/"assets.json").read_text(encoding="utf-8-sig"))
ids={a["id"] for a in assets}
for asset in assets:
    assert Path(asset["evidence"]).exists(),asset["evidence"]
    assert set(asset["depends_on"])<=ids,asset["id"]
print("PASS all 14 asset evidence paths and relationship IDs")
for path in base.glob("*.md"):
    for link in re.findall(r"\]\(([^)]+)\)",path.read_text(encoding="utf-8-sig")):
        if not link.startswith(("https:","http:")):
            assert (path.parent/unquote(link)).exists(),(path,link)
print("PASS local documentation links")
report=json.loads((base/"runs/20261109T124059033126Z/findings.json").read_text())
assert sum(report["metrics"]["tests"].values())==33
assert report["metrics"]["tests"]==dict(PASS=27,FAIL=6,ERROR=0,BLOCKED=0)
assert len(report["findings"])==3
print("PASS report metrics reconcile with saved run")
