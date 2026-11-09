# DeRexi Vulnerability Inspector and automated testing framework

The inspector is a Python CLI that reads approved local JSON evidence and emits prioritized JSON and Markdown findings. It requires no production credentials and makes no network calls. The companion runner discovers installed Python distribution metadata, executes isolated controls, checks dependency consistency and reads the existing Compose configuration.

## Run

From the repository root in PowerShell, use the existing project environment:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& ./derexi-policy-pilot/.venv/Scripts/python.exe cyber_threats_vulnerabilities_2_final/assignment2/run_assessment.py
```

Each run writes a new UTC-named directory under assignment2/runs. Exit 0 means no failed or errored assertions. Exit 1 records actual failed controls. Exit 2 means the harness could not complete reliably. A nonzero result is evidence to investigate.

Inspect a previously approved set of evidence with:

```powershell
& ./derexi-policy-pilot/.venv/Scripts/python.exe cyber_threats_vulnerabilities_2_final/assignment2/derexi_vulnerability_inspector.py --assets cyber_threats_vulnerabilities_2_final/assignment2/runs/20261109T124059033126Z/assets.json --results cyber_threats_vulnerabilities_2_final/assignment2/runs/20261109T124059033126Z/results.json --dependencies cyber_threats_vulnerabilities_2_final/assignment2/runs/20261109T124059033126Z/dependencies.json --output cyber_threats_vulnerabilities_2_final/assignment2/review-export
```

The standalone inspector exits successfully when it generates a valid report, even if the input contains failed controls. It refuses to overwrite findings.json or findings.md. Use a new output directory for each review.

## Controls and isolation

control_suite.py reuses existing synthetic model builders and FakeSession from the original security-controls harness. That harness replaces Engine.connect before importing main. The new suite suppresses dotenv loading, supplies a dummy SQLite URL, generates process-local development tokens and blocks external socket connections. All business records and role lookups are synthetic. Loopback is permitted for the Windows event loop, with HTTP requests handled by FastAPI TestClient.

Signed requests use the actual bearer parser, development-token verifier, server-side identity resolver, role guards and handlers. Tests exercise Employee, Policy Owner and System Administrator. Positive owner access is paired with cross-user denial and administrator access. Public root headers and a simulated database exception cover middleware and safe errors. A reserved .example publisher URL exercises feed attribution without a request to that host.

The suite measures fake write counts and commits. These are attempted handler mutations, not database persistence. No live auth users or personas are created. Database FK behavior, real transactions, production JWT/JWKS integration and operating network ACLs remain outside this test scope.

## Tool behavior

Inputs are an array of assets with unique IDs, control results referencing those IDs and installed distribution metadata. Risk dimensions must be integers 1–5. Duplicate controls, unknown assets and invalid statuses are refused. Findings are grouped by control cause, preserve supporting check IDs and include severity, risk score, proposed owner, SLA, action and closure criteria.

Coverage equals current-scope asset IDs with at least one PASS or FAIL control divided by the 13 application/lab asset records. ERROR-only, untested and historical classroom assets never increase assessed coverage. A passing static config check does not imply a fresh runtime check. Deployed package versions cannot be inferred from local installed versions.

Six regression scenarios in test_inspector.py passed. They cover finding deduplication, coverage scope, error/closure accounting, severity boundaries, invalid input and undefined denominator. See inspector-validation.txt.

## Dependencies and limitations

The inspector uses the standard library. The control runner uses the existing application environment and dependencies, including FastAPI, SQLAlchemy, Pydantic and PyJWT. No packages were installed. pip check passed for 35 installed distributions. pip-audit, safety and bandit are absent in this environment. Dependency advisory matching is BLOCKED pending an approved scanner or advisory database. Lower-bound dependency findings concern reproducibility and do not claim a vulnerable CVE.

A sandbox run timed out because the Windows TestClient event loop could not complete under restricted socket access. It is preserved under runs/20261109T123409858968Z. The authorized retry completed under runs/20261109T124059033126Z with external-network and database tripwires still active.

## Latest evidence closure

The [closure guide](closure/README.md) supersedes the earlier advisory blocker. All 35 installed release versions were queried using PyPI's public release API. Two distinct advisory issues were triaged, and the Inspector now accepts optional --advisories input tied to the exact dependency snapshot hash. Original 33-check counts remain unchanged when advisory findings are attached. Nine tool regression scenarios passed. Exact commands are in closure/commands.txt and CLI help in closure/cli-help.txt. Use the updated five-item remediation tracker.

The Inspector itself remains offline. audit_advisories.py is the separately invoked, read-only network step. Original runs and the initial regression permission error are preserved.
