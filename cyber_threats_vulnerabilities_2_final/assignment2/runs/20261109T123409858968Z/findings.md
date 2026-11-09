# DeRexi Vulnerability Inspector

Approved local evidence only; no production reachability or CVE scan inferred

## Metrics

```json
{
  "assets_catalogued": 14,
  "current_scope_assets": 13,
  "assets_assessed": 2,
  "coverage_pct": 15.38,
  "tests": {
    "PASS": 2,
    "FAIL": 1,
    "ERROR": 1,
    "BLOCKED": 0
  },
  "findings_by_severity": {
    "Medium": 1
  },
  "remediation": {
    "OPEN": 1,
    "CLOSED": 0
  },
  "installed_distributions": 35,
  "mean_time_to_remediate": null
}
```

## Prioritized findings

| Finding | Severity | Score | Evidence tests | Remediation |
|---|---|---|---|---|
| DVI-DEPENDENCY | Medium | 9/25 | DEPENDENCY-PINS | OPEN |

### DVI-DEPENDENCY

Create a reviewed version/hash lock and deployed SBOM, then perform advisory triage.

Closure requires Clean reproducible install from reviewed lock, dependency consistency check and documented advisory dispositions.

Proposed owner is Platform engineering. SLA is 720 hours from validated intake.

Unassessed assets are AI, APP, AUTH, DB, DEV_AUTH, FDIC, FED, FR, NIST, PULSE, UI.

BLOCKED: no local advisory scanner or database supplied
