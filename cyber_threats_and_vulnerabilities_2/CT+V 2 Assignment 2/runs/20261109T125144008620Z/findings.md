# DeRexi Vulnerability Inspector

Approved local evidence only; no production reachability or CVE scan inferred

## Metrics

```json
{
  "assets_catalogued": 14,
  "current_scope_assets": 13,
  "assets_assessed": 6,
  "coverage_pct": 46.15,
  "tests": {
    "PASS": 27,
    "FAIL": 6,
    "ERROR": 0,
    "BLOCKED": 0
  },
  "findings_by_severity": {
    "Critical": 1,
    "High": 1,
    "Medium": 1
  },
  "remediation": {
    "OPEN": 3,
    "CLOSED": 0
  },
  "installed_distributions": 35,
  "mean_time_to_remediate": null
}
```

## Prioritized findings

| Finding | Severity | Score | Evidence tests | Remediation |
|---|---|---|---|---|
| DVI-POLICY-WRITE | Critical | 20/25 | EMP-APPROVE, OWN-APPROVE, ANON-APPROVE, EMP-VERSION | OPEN |
| DVI-FEED-INTEGRITY | High | 12/25 | FEED-HOST | OPEN |
| DVI-DEPENDENCY | Medium | 9/25 | DEPENDENCY-PINS | OPEN |

### DVI-POLICY-WRITE

Require verified identity and server-side role checks on policy creation/version routes. Restrict approval to administrators.

Closure requires Signed Employee and Owner approval attempts denied without writes; administrator approval succeeds; anonymous policy writes denied.

Proposed owner is Platform engineering. SLA is 72 hours from validated intake.

### DVI-FEED-INTEGRITY

Bind article URLs to approved publisher hosts and validate redirects before following them.

Closure requires Unrelated hosts rejected; official publishers and expected GovDelivery tenant accepted; regression and current feed checks pass.

Proposed owner is Feed service owner. SLA is 336 hours from validated intake.

### DVI-DEPENDENCY

Create a reviewed version/hash lock and deployed SBOM, then perform advisory triage.

Closure requires Clean reproducible install from reviewed lock, dependency consistency check and documented advisory dispositions.

Proposed owner is Platform engineering. SLA is 720 hours from validated intake.

Unassessed assets are AI, DB, DEV_AUTH, FDIC, FED, FR, NIST.

BLOCKED: no local advisory scanner or database supplied
