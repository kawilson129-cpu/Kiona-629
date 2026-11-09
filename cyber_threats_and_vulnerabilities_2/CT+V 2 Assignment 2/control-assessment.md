# Current control assessment and remediation register

Authoritative execution is [20261109T124059033126Z](runs/20261109T124059033126Z/). This is a current local assessment of synthetic API requests and static/local configuration. Prior coursework and Docker evidence retain their original scope.

## Metrics

| Metric | Result | Interpretation |
|---|---|---|
| Catalogued asset records | 14 | 13 ecosystem components plus 1 historical host |
| Assessed current assets | 6 of 13, 46.15% | APP, AUTH, UI, PULSE, PKGS and CONTAINER |
| Current assertions | 33 | 27 PASS, 6 FAIL, 0 ERROR |
| Grouped findings | 3 OPEN | 1 Critical, 1 High, 1 Medium |
| Installed distributions | 35 | Includes transitive requirements metadata |
| Dependency consistency | PASS | pip check returned 0 |
| Inspector regression scenarios | 6 PASS | Separate from application control counts |
| Remediation closed | 0 | No security remediation implemented in this task |
| Enterprise SLA/MTTR | Unknown | No operational closure history |

## Expected versus actual and impact

| Finding | Expected | Actual | Business impact | Risk |
|---|---|---|---|---|
| DVI-POLICY-WRITE | Anonymous denied 401, Employee/Owner approval denied 403, Employee version publication denied 403 | All four negative requests returned 201 and recorded fake writes. Administrator approval succeeded. | Unauthorized policy integrity change could alter bank staff guidance and incident escalation instructions. | Critical 20/25 |
| DVI-FEED-INTEGRITY | FDIC label must reject an unrelated article host | Reserved unrelated.example URL accepted by make_article | Misattributed external content can mislead regulatory monitoring. | High 12/25 |
| DVI-DEPENDENCY | Runtime versions reproducible from reviewed installation declarations | requirements.txt uses lower bounds, while local installed versions can vary | Dependency drift undermines repeatable validation and vulnerability triage. | Medium 9/25 |

The Policy Owner approval expectation follows an administrator-only approval rule for this assessment. Business owners must sign off on that matrix. Anonymous and Employee policy writes independently establish the access-control gap.

Positive findings include signed identity resolution, tampered-token rejection for all three roles, Employee governance denial, owner conversation access, cross-user conversation denial for Employee/Owner, administrator oversight, strict boolean and text-length validation, nosniff/frame-denial headers, and safe generic error bodies.

The source attribution failure concerns article host binding. It does not prove that a live publisher feed was compromised. Prior live feeds and Docker configuration checks are reused and are not rerun as Compliance 1 or Assignment 5 work.

## Corrective actions and tracking

| ID | Proposed owner | Status | Target from validated intake | Closure criteria |
|---|---|---|---|---|
| DVI-POLICY-WRITE | Platform engineering | OPEN | 72 hours | Enforce signed identity and role checks on both policy write routes. Repeat four failed negative requests with zero writes and legitimate administrator success. Verify object ownership where applicable. |
| DVI-FEED-INTEGRITY | Feed service owner | OPEN | 14 days | Approve publisher/tenant hosts, validate redirects and reject unrelated hosts. Preserve official-source compatibility and retest safe rendering. |
| DVI-DEPENDENCY | Platform engineering | OPEN | 30 days | Produce reviewed version/hash lock and deployed SBOM, clean install, advisory scan and documented triage. |

Validated intake is the generated_at timestamp in findings.json. Targets are program recommendations, not accepted work commitments. See remediation-tracking.csv for computed target dates. No risk exception or closure approval was invented.

## Unresolved verification

DEV_AUTH was used to mint signed credentials but has no dedicated endpoint/configuration assessment in the coverage denominator. Hosted DB, optional AI provider and four publisher endpoints lack fresh control checks in this run. Earlier publisher success remains useful prior evidence. Relational FK/rollback, broader private-resource authorization and production issuer integration require a disposable relational environment and explicit acceptance criteria. No new network scans were performed.

## Final retest and advisory update

The unchanged suite rerun 20261109T125144008620Z reproduced all six failures, with 27 PASS / 0 ERROR. The earlier counts and findings above are the initial baseline. Current consolidated tracking has five OPEN findings after two distinct package advisory matches. See closure/README.md and closure/inspector/findings.json for the latest evidence and metrics. No original finding is resolved.
