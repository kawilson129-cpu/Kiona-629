# Risk Management & Audit Implementation

DeRexi: Policy Pilot / fictional Aurum Capital Bank. Assessment date: November 17, 2026. This is a scoped development-control audit and enterprise risk planning exercise, not a bank examination or certification.

| Read | Purpose |
|---|---|
| [Rubric checklist](docs/rubric-checklist.md) | Official requirements and exact evidence/limitations |
| [Risk assessment](docs/risk-assessment.md) / [risk register CSV](docs/risk-register.csv) | Quantitative assumptions, inherent/residual estimates and treatment priorities |
| [Audit program](docs/audit-program.md) | Scope, roles, procedures, cadence and escalation |
| [Framework mapping](docs/framework-control-mapping.md) | GLBA/OCC, FFIEC, NIST CSF 2.0 and SP 800-53 control support |
| [Control validation](docs/control-validation.md) | Fresh isolated execution, historical comparison and safe repeatability |
| [Audit report](docs/audit-report.md) | Findings, corrective actions and closure criteria |
| [Final summary](docs/final-summary.md) / [progress](docs/progress.md) | Results, remaining requirements and session handoff |
| [Evidence index](evidence/index.md) | Actual dated outputs and references to unchanged prior work |

Run from this directory with the existing environment:

```powershell
& ../../derexi-policy-pilot/.venv/Scripts/python.exe -B src/run_audit.py
& ../../derexi-policy-pilot/.venv/Scripts/python.exe -B tests/validate_package.py
```

The audit runner imports existing isolated test code by reference. It redirects evidence/temp paths here, blocks service network connections, blocks `.env` reads and disallows external writes. Windows' standard-library socketpair wakeup is allowed solely for TestClient's internal event loop. Fixture identities and records are in-memory; no real seeded user, database, application source or authorization configuration is changed. Historical evidence is neither copied nor overwritten.

Overall status: **local implementation/testing evidenced; enterprise operating assurance PARTIAL**. Proposed owners, monetary estimates, deadlines and risk appetite are planning assumptions awaiting management review.
