"""Regression checks for scoring, grouping and honest coverage reporting."""
from derexi_vulnerability_inspector import analyze, severity, attach_advisories
import hashlib
from pathlib import Path
import tempfile


def main():
    assets = [{"id":"APP","evidence_type":"current source"},
              {"id":"DB","evidence_type":"design"},
              {"id":"OLD","evidence_type":"historical classroom"}]
    checks = [dict(id="A",asset="APP",group="policy-write",status="FAIL",likelihood=4,impact=5),
              dict(id="B",asset="APP",group="policy-write",status="FAIL",likelihood=3,impact=5),
              dict(id="C",asset="DB",group="harness",status="ERROR")]
    report = analyze(assets,checks,[])
    assert len(report["findings"]) == 1 and report["findings"][0]["score"] == 20
    print("PASS group repeated control failures without inflating finding count")
    assert report["metrics"]["coverage_pct"] == 50 and report["unassessed_assets"] == ["DB"]
    print("PASS exclude historical host and error-only assets from assessed coverage")
    assert report["metrics"]["tests"]["ERROR"] == 1 and report["metrics"]["remediation"]["CLOSED"] == 0
    print("PASS retain harness errors and avoid unsupported closure")
    assert [severity(n) for n in [4,5,9,10,15,16,25]] == ["Low","Medium","Medium","High","High","Critical","Critical"]
    print("PASS severity boundary cases")
    for bad in [dict(checks[0],asset="UNKNOWN"),dict(checks[0],likelihood=0),dict(checks[0],status="UNTESTED-PASS")]:
        try:
            analyze(assets,[bad],[])
        except ValueError:
            continue
        raise AssertionError("Invalid evidence accepted")
    print("PASS reject unknown asset, invalid risk score and invalid status")
    assert analyze([],[],[])["metrics"]["coverage_pct"] is None
    print("PASS undefined denominator stays unknown")
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
        dependency_path = Path(directory)/"dependencies.json"
        dependency_path.write_text("[]")
        finding = dict(id="SYNTHETIC",package="example",advisory_ids=["DEMO-1","DEMO-ALIAS"],
                       likelihood=2,impact=3,owner="Fixture",corrective_action="Fixture",closure="Fixture")
        audit = dict(dependencies_sha256=hashlib.sha256(dependency_path.read_bytes()).hexdigest(),
                     active_advisories=[dict(package="example",id="DEMO-1"),dict(package="example",id="DEMO-ALIAS")],
                     triaged_findings=[finding],queried=1,total=1)
        merged = analyze(assets,checks,[])
        original_counts = dict(merged["metrics"]["tests"])
        attach_advisories(merged,audit,dependency_path)
        assert len(merged["findings"])==2 and merged["metrics"]["tests"]==original_counts
        print("PASS advisory alias pair adds one finding without inflating executed tests")
        try:
            attach_advisories(analyze(assets,checks,[]),dict(audit,dependencies_sha256="wrong"),dependency_path)
        except ValueError:
            print("PASS reject mismatched dependency snapshot")
        else:
            raise AssertionError("Mismatched snapshot accepted")
        try:
            attach_advisories(analyze(assets,checks,[]),dict(audit,triaged_findings=[finding,finding]),dependency_path)
        except ValueError:
            print("PASS reject duplicate advisory finding")
        else:
            raise AssertionError("Duplicate advisory accepted")


if __name__ == "__main__":
    main()
