# Enterprise vulnerability management program

Aurum Capital Bank is fictional. This program is implemented as a local coursework assessment cycle for DeRexi. Functional owners below are proposed responsibilities, with no personnel or account changes. Program approval, recurring enterprise operation and production coverage remain unverified.

## Governance, scope and objectives

The policy compliance function owns the risk register and accepts time-limited exceptions. Platform engineering maintains API, dependencies and container configuration. Identity engineering owns authentication and access review. Data platform owns database and backup assurance. Feed owners manage publisher integrity and availability. Security assessment staff validate findings independently of the implementer and retain evidence. Business owners set impact and authorize downtime.

Objectives are to inventory every in-scope component with a source and accountable function, detect unsafe privileged operations, reduce untrusted input and dependency exposure, and require an independently verified closure for each finding. Current scope includes local source, installed package metadata, signed synthetic API requests and prior Docker/feed evidence. Historical classroom Nmap findings have a separate population. Future scans require written target, operator, time window and allowed techniques.

## Discovery and intake

Read the asset register, source contracts, approved logs and dependency metadata before selecting tests. Each intake item records stable ID, affected asset/version, reported time, evidence, reproduction, trust boundary, business impact and owner. Vendor notices and advisories enter the same queue. Treat unverified scanner matches as candidates pending package/version and reachability confirmation.

The local runner snapshots assets, source hashes, environment versions, commands, elapsed time and results. It creates a new run directory each time. Unknown coverage is reported explicitly. Reconcile new source components weekly and supplier changes monthly. Retain approved raw Nmap XML if new authorized discovery becomes available. Existing reports establish only a historical selected-host result.

## Validation and scoring

Use positive and negative signed-identity requests, verify no writes on rejection, and preserve body-independent error assertions. A fake session demonstrates handler decisions and attempted writes. It does not establish relational constraints, transaction rollback or deployed row security. ERROR and BLOCKED outcomes never become PASS.

Risk score is likelihood multiplied by impact, each 1–5. Likelihood levels are rare, unlikely, possible, likely and near certain. Impact levels are negligible, team disruption, departmental exposure, major sensitive-data/service impact and bank-wide trusted-guidance compromise. Scores 1–4 Low, 5–9 Medium, 10–15 High and 16–25 Critical. This is a local ordinal scale, not CVSS or monetary loss. Policy writes score 4×5 based on direct negative-request success and the integrity of trusted policies. Feed attribution scores 3×4. Lower-bounded dependencies score 3×3 as a reproducibility/assurance gap, without asserting a known CVE. Sensitivity of one likelihood level changes these scores to 15–25, 8–16 and 6–12 respectively.

Inspector grouping merges failed tests for the same control cause. Counts of failed assertions and findings remain separate. No alert alone establishes compromise.

## Remediation SLAs and escalation

| Priority | Validated finding target | Escalation |
|---|---|---|
| Active exploitation | Immediate containment and incident process | SOC and business owner immediately |
| Critical | 72 hours | Owner at intake, risk lead at 24 hours, executive sponsor at deadline |
| High | 14 days | Owner at intake, risk lead at day 7 and overdue |
| Medium | 30 days | Weekly review and escalation at deadline |
| Low | 90 days | Monthly review and escalation at deadline |

Start the clock at validated intake in UTC. A reclassification retains the original discovery date and records why priority changed. Emergency isolation requires service-owner coordination. Closure time, overdue status and accepted exceptions are reported separately. Real elapsed remediation performance remains unknown until owners acknowledge tickets and execute treatment.

## Exceptions and continuous monitoring

Record exception ID, finding, business justification, affected assets, compensating controls, approver, approval date, expiry and retest trigger. Default maximum approval is 30 days for Critical/High and 90 days for Medium/Low. Security reviewers recommend treatment; business risk owners approve residual risk. Expired exceptions return to OPEN and escalate. No exceptions are currently approved.

Run the local assessment after relevant application or dependency changes and at each release candidate. Daily operations should review authentication denials, policy approvals, feed failures and container health. Weekly review compares inventory and finding trends. Monthly management reporting shows scope denominator, severity, aging, SLA compliance, exceptions, retest outcomes and coverage gaps. These schedules are documented procedures awaiting operational adoption.

## Closure, reporting and evidence retention

Workflow is NEW → VALIDATED/OPEN → IN_PROGRESS → READY_FOR_RETEST → CLOSED, with EXCEPTION or REOPENED transitions recorded. Before closure, repeat the original failing negative test, verify a legitimate positive workflow and confirm the affected deployment profile. Preserve prior failing evidence and record reviewer, timestamp, corrected revision and residual risk. Never close a finding solely because a configuration file changed.

Each execution is immutable by convention and stored under runs/<UTC timestamp>. Restrict original logs to the assessment team, sanitize credentials before broader sharing and retain one academic year subject to institutional policy. This local directory has no tamper-proof retention enforcement. Hashes support comparison but require trusted storage to support custody.

## Executed local cycle

This submission implements discovery, signed-fixture validation, finding grouping, scoring, reporting and an OPEN remediation queue. The current report is generated by DeRexi Vulnerability Inspector from the recorded run. Proposed owners and service levels are not management approvals. Enterprise operating history, production scans and verified remediation remain outstanding.
