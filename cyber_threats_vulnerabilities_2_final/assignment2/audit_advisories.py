"""Read release-specific PyPI advisories for an approved installed-package snapshot."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import urllib.parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    packages = json.loads(args.dependencies.read_text(encoding="utf-8-sig"))
    results = []
    for package in packages:
        name, version = package["name"], package["version"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError("Invalid package name")
        url = "https://pypi.org/pypi/" + urllib.parse.quote(name, safe="") + "/" + urllib.parse.quote(version, safe="") + "/json"
        record = dict(name=name, version=version, url=url, checked_at=datetime.now(timezone.utc).isoformat())
        try:
            request = urllib.request.Request(url, headers={"User-Agent":"DeRexi-Vulnerability-Inspector/1.0 coursework assessment", "Accept":"application/json"})
            with urllib.request.urlopen(request, timeout=12) as response:
                raw = response.read(5_000_001)
                if len(raw) > 5_000_000:
                    raise ValueError("Metadata response too large")
                data = json.loads(raw)
                if "vulnerabilities" not in data:
                    raise ValueError("Advisory field absent")
                record.update(status="QUERIED", http_status=response.status,
                              response_sha256=hashlib.sha256(raw).hexdigest(),
                              vulnerabilities=data["vulnerabilities"], last_serial=data.get("last_serial"))
                (args.output/(name+".json")).write_bytes(raw)
        except Exception as exc:
            record.update(status="UNAVAILABLE", error=str(exc))
        results.append(record)
        print(name, version, record["status"], flush=True)
    active = [{"package":r["name"], "version":r["version"], **v}
              for r in results for v in r.get("vulnerabilities",[]) if not v.get("withdrawn")]
    report = dict(source="https://docs.pypi.org/api/json/", dependencies_sha256=hashlib.sha256(args.dependencies.read_bytes()).hexdigest(),
                  generated_at=datetime.now(timezone.utc).isoformat(), packages=results,
                  queried=sum(r["status"]=="QUERIED" for r in results), total=len(results),
                  active_advisories=active, unavailable=sum(r["status"]=="UNAVAILABLE" for r in results),
                  limitation="Registry-reported release advisories only; no proof of exploitability, deployed inventory, OS CVEs or absence of unknown vulnerabilities")
    (args.output/"assessment.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("total","queried","unavailable")}),flush=True)
    print("Active package/advisory pairs:",len(active),flush=True)


if __name__ == "__main__":
    main()
