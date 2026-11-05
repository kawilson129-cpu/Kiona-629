"""Retain per-test Assignment 5 outcomes in a fresh evidence directory.

Run from backend/: ../.venv/bin/python tests/run_assignment5_verification.py
Each suite runs separately: the original C-02 DB tripwire must not affect SQLite.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKER = r'''
import importlib, json, sys, traceback, unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "tests")
name, destination = sys.argv[1:]
module = importlib.import_module(name)
records = []
def record(tid, scenario, expected, status, actual):
    records.append(dict(id=tid, scenario=scenario, expected=expected, actual=actual,
        status=status, date=datetime.now(timezone.utc).isoformat(),
        environment="Cloud Linux; project .venv; isolated synthetic identities/fake or SQLite DB; no live Supabase",
        evidence_file=Path(destination).name))
class Result(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        record(test.id(), test.shortDescription() or test._testMethodName,
               "All named test assertions hold", "PASS", "All assertions passed")
    def addFailure(self, test, error):
        super().addFailure(test, error)
        record(test.id(), test.shortDescription() or test._testMethodName,
               "All named test assertions hold", "FAIL", self._exc_info_to_string(error, test))
    def addError(self, test, error):
        super().addError(test, error)
        record(test.id(), test.shortDescription() or test._testMethodName,
               "Test completes without error", "FAIL", self._exc_info_to_string(error, test))
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        record(test.id(), test.shortDescription() or test._testMethodName,
               "Test executes", "NOT TESTED", reason)
if name == "test_security_controls":
    try:
        for name in sorted(n for n in vars(module) if n.startswith("test_c02")):
            module.CURRENT_TEST = name
            try:
                getattr(module, name)()
            finally:
                module.teardown()
        for item in module.RESULTS:
            record(item["id"], item["scenario"], item["expected"], item["status"], item["actual"])
    finally:
        module.CLIENT.close()
elif name == "test_week8_stage1":
    for name in sorted(n for n in vars(module) if n.startswith("test_") and callable(getattr(module,n))):
        module.main.app.dependency_overrides.clear()
        try:
            getattr(module, name)()
            record(name, name, "Original incident regression assertions hold", "PASS", "All assertions passed")
        except Exception:
            record(name, name, "Original incident regression assertions hold", "FAIL", traceback.format_exc())
        print(records[-1]["status"], name)
    module.main.app.dependency_overrides.clear()
else:
    unittest.TextTestRunner(verbosity=2, resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromModule(module))
Path(destination).write_text(json.dumps(records, indent=2)+"\n")
sys.exit(0 if records and all(r["status"]=="PASS" for r in records) else 1)
'''


def run():
    backend = Path(__file__).resolve().parents[1]
    output = backend.parent / "docs/compliance/evidence" / datetime.now(timezone.utc).strftime("assignment5_%Y-%m-%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for name in ("test_assignment5_controls", "test_week8_stage1", "test_secure_api",
                 "test_validation_hardening", "test_security_controls"):
        command = [sys.executable, "-c", WORKER, name, str(output / (name + ".json"))]
        result = subprocess.run(command, cwd=backend, capture_output=True, text=True, timeout=90,
                                env={**os.environ, "DATABASE_URL": "postgresql+psycopg2://offline:offline@127.0.0.1:1/offline"})
        (output / (name + ".log")).write_text(result.stdout + result.stderr)
        records_path = output / (name + ".json")
        records = json.loads(records_path.read_text()) if records_path.exists() else []
        summary = {status: sum(r["status"] == status for r in records)
                   for status in ("PASS", "FAIL", "BLOCKED", "NOT TESTED")}
        results.append(dict(suite=name, return_code=result.returncode, counts=summary,
                            evidence_file=records_path.name, log=name + ".log"))
        print(name, result.returncode, summary, flush=True)
    # Hash the actual reviewed sources; preserve all earlier failing evidence.
    sources = [backend / n for n in ("main.py", "secure_api.py", "schemas.py", "models.py", "auth.py", "rbac.py", "dev_demo.py")]
    sources += sorted((backend / "tests").glob("*.py"))
    report = dict(date=datetime.now(timezone.utc).isoformat(), results=results,
                  environment="Cloud Linux; project .venv; isolated synthetic fixtures; no live services",
                  source_sha256={str(p.relative_to(backend)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (output / "verification_results.json").write_text(json.dumps(report, indent=2) + "\n")
    print("EVIDENCE", output / "verification_results.json")
    return 0 if all(r["return_code"] == 0 and r["counts"]["PASS"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(run())
