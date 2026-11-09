# Final evidence closure and submission guide

Assignment 2 is ready to submit as a documented local-lab vulnerability assessment with unresolved findings. Full enterprise-wide implementation remains PARTIAL. No finding was closed without correction and verification.

## Final measured results

| Measure | Verified result |
|---|---|
| Asset reconciliation | 13/13 local ecosystem records, 100% |
| Direct current control coverage | 6/13 assets, 46.15% |
| Historical classroom population | 10 active hosts reported, 1 detailed host; separate denominator |
| Isolated rerun | 33 checks, 27 PASS, 6 FAIL, 0 ERROR |
| Inspector regression validation | 9 PASS scenarios |
| Advisory query coverage | 35/35 installed release versions, 0 unavailable |
| Advisory identity deduplication | 4 registry records represent 2 distinct issues |
| Open findings after advisory triage | 5 total, 1 Critical / 2 High / 2 Medium on the local risk scale |
| Closed findings / approved exceptions | 0 / 0 |

The 13-asset reconciliation is complete against the approved local register. It does not imply 100% control coverage or enterprise asset completeness. Ownership remains proposed functional accountability. See [reconciliation](assets-reconciled.md) and [machine records](assets-reconciled.json).

## All six reproduced failures

| Assertion | Expected / actual | Investigation |
|---|---|---|
| EMP-APPROVE | 403 / 201 | Policy creation lacks signed identity and role dependencies; fake session recorded inserts. |
| OWN-APPROVE | 403 / 201 | Same handler permits approval. Administrator-only approval is the assessment criterion and awaits business sign-off. |
| ANON-APPROVE | 401 / 201 | Same handler permits an unsigned caller to create an approved policy. |
| EMP-VERSION | 403 / 201 | Version handler accepts signed Employee publication without a role guard. |
| FEED-HOST | Reject / accepted | make_article accepts HTTPS URL shape without binding FDIC attribution to its host. |
| DEPENDENCY-PINS | Reproducible versions / lower bounds | Current runtime declarations permit version drift. Snapshotting versions does not create a tested lock. |

The tests were rerun unchanged. Valid signed requests, cross-user denial, signature tampering and rejected input tests still pass. Full command, timestamp and expected/actual evidence is in [the new run](../runs/20261109T125144008620Z/execution.json) and [control log](../runs/20261109T125144008620Z/controls.log). Earlier runs remain preserved.

## Advisory-backed assessment

The audit queried PyPI's release-specific vulnerability data for each exact installed version. Raw responses, URL, time and response hash are preserved. Withdrawn entries are excluded and aliases are grouped by issue. Coverage applies to this Windows Python environment, not deployed OS/container packages. An empty response is a point-in-time absence of registry reports. [PyPI JSON API](https://docs.pypi.org/api/json/)

- certifi 2026.7.22 matched GHSA-6q48-6c7w-9gw2 / PYSEC-2026-4320. The upstream advisory rates it Critical and lists 2026.10.18 as patched. Registry text recommends 2026.10.19 or later. Local risk is High 12/25 because use of the bundle and an on-path attacker remain unverified. Proposed action is a reviewed trust-bundle upgrade and client retest. No CVE ID was assigned in the source. [Upstream certifi advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2)
- pip 26.1.2 matched CVE-2026-13346 / GHSA-qwm4-qh6w-59xr / PYSEC-2026-3721. Fixed release is 26.2.0. The issue requires a malicious index and affects URL handling during package operations. Local risk is Medium 6/25, distinct from a deployed API vulnerability. Proposed action is a reviewed tooling upgrade and approved-index validation. [Advisory record](https://osv.dev/vulnerability/PYSEC-2026-3721)

No package was upgraded and no exploit was attempted. The new findings remain OPEN. [Raw assessment](advisories/assessment.json), [triaged records](advisories-triaged.json), [consolidated findings](inspector/findings.md).

## Demonstrated workflow

The original three findings proceeded through discovery, isolated validation, risk prioritization, OPEN tracking and an independent rerun that reproduced them. They remain OPEN with proposed mitigations, target dates and closure tests. The two new dependency findings proceeded through version discovery, registry matching, alias reconciliation, impact triage and OPEN tracking. Their remediation retest is pending.

Original intake dates and SLA targets were retained for the three existing findings. [Workflow ledger](workflow.json), [updated tracker](../remediation-tracking.csv), [preserved baseline tracker](remediation-baseline.csv). No accepted exception or approved owner commitment was fabricated.

## Official Assignment 2 rubric verification

| Official requirement | Status | Evidence and remaining limit |
|---|---|---|
| Complete enterprise vulnerability management program with documented processes/procedures | PARTIAL enterprise / COMPLETE local workflow | Program covers governance through closure. One discover-to-retest cycle demonstrated. Enterprise adoption, accepted ownership and recurring monitoring are unverified. |
| Advanced asset discovery with detailed relationship mapping and impact analysis | COMPLETE approved local inventory / PARTIAL enterprise | All 13 reconciled against source and prior runtime evidence. Full live enterprise discovery and host ownership remain unverified. |
| Automated testing framework developed and implemented with functionality evidence | COMPLETE local | Repeatable runner and unchanged 33-check rerun with logs and errors recorded honestly. |
| Custom assessment tool created and deployed with documentation | COMPLETE local | CLI executed, JSON/Markdown generated, advisory integration validated with 9 regression scenarios. |
| Advanced control assessment and comprehensive findings | COMPLETE local | Signed roles/ownership, input, errors, headers, dependency and container configuration evidence; five prioritized findings with treatment and retest criteria. |
| Performance metrics and validation evidence for implementations | COMPLETE local | Counts, coverage denominators, timings, package/advisory coverage and remediation state recorded. Enterprise MTTR/SLA adherence remains unknown. |

Overall PARTIAL against unrestricted enterprise wording. Failed controls are legitimate assessment findings; they do not invalidate the assessment evidence. Instructor acceptance determines whether the scoped local implementation satisfies the course's intended enterprise demonstration.

## Exact submission evidence and screenshots

Include these files with the existing report/checklist:

1. ../program.md and ../assets-and-impact.md, plus assets-reconciled.md/json.
2. ../runs/20261109T125144008620Z/execution.json, controls.log, results.json, dependencies.json and source-hashes.json.
3. inspector/findings.json and findings.md, inspector-cli.log, inspector-regression-workspace.log and commands.txt.
4. advisories/assessment.json, advisories-triaged.json and the raw certifi.json/pip.json responses in advisories/.
5. ../remediation-tracking.csv, workflow.json, and this rubric matrix.

Capture these real views for the instructor. Screenshots supplement the raw artifacts.

- S1 — Terminal showing the assessment command and final 27 PASS / 6 FAIL metrics. Label the run timestamp.
- S2 — Terminal or editor showing all six failed assertions with expected/actual outcomes from controls.log.
- S3 — Rendered asset relationship diagram and the 13-row reconciliation table, with 100% reconciliation and 46.15% control coverage visible.
- S4 — Inspector CLI output and generated severity table, plus the nine regression PASS lines.
- S5 — Advisory assessment showing 35 queried / 0 unavailable, installed certifi/pip versions, IDs and fixed versions. Show alias deduplication clearly.
- S6 — Remediation tracker with five OPEN items, proposed owners, target dates and retest evidence, alongside the discover-to-retest workflow.

No new screenshots were generated in this closure task. Existing Docker screenshots are reused evidence for Assignment 5.

## Remaining work

Enterprise ownership/approval and recurring monitoring records require organizational evidence. Deployed inventory, broader relational authorization tests and production issuer validation require an appropriately authorized environment. Actual remediation and post-fix retests are pending for all five findings. OS/container image advisories and exploitability were not assessed.
