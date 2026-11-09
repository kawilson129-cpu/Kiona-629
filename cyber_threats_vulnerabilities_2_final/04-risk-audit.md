# Assignment 4 | Risk Management & Audit Implementation

**Scope.** Aurum Capital Bank's fictional DeRexi environment. Review policy and incident data, employee access, external feeds, administration, dependencies, and recovery. Evidence spans classroom, in-process, and historical secured profiles. Findings apply to their specific profile. Assessment date November 9, 2026.

## Quantified risk register

Use a 12-month horizon. Likelihood 1 rare, 2 unlikely, 3 possible, 4 likely, 5 near certain. Impact is the greatest expected effect across confidentiality, integrity, and availability: 1 negligible, 2 small team interruption, 3 departmental exposure or outage, 4 sensitive data or major interruption, 5 compromise of trusted guidance, bank-wide operations, or downstream clients. Score = likelihood × impact. 1–4 low, 5–9 moderate, 10–15 high, 16–25 critical. Ratings are analyst judgments. Target scores assume verified treatments. Reassess likelihood by one level in either direction when evidence is stale, e.g. R2 varies from 10 to 20.

| Risk | Basis | Inherent | Observed or estimated residual | Target | Proposed owner and due |
|---|---|---:|---:|---:|---|
| R1 unauthorized access or policy publication | E07 baseline, E08 historical retest and current fake-session policy-write findings | 4×5=20 | 4×5=20 for compatibility exposure | 1×5=5 | Platform lead, before any exposure |
| R2 SSH administrative compromise | E03 classroom TCP/22, management ACL unverified | 3×5=15 | 3×5=15 | 1×5=5 | Infrastructure, 14 days |
| R3 unsafe input or reference failure | E07 baseline, E08 historical retest | 4×4=16 | 3×4=12 pending current validation | 1×4=4 | API lead, 14 days |
| R4 feed impersonation | E07 historical host mismatch, E08 report of hardened redirects | 3×4=12 | 2×4=8 provisional | 1×4=4 | Feed owner, 14 days |
| R5 dependency/AI provider compromise or exposure | Direct dependencies and provider boundary E10 | 3×5=15 | 3×5=15 | 2×5=10 | Platform/procurement, 30 days |
| R6 loss of policy history or availability | Restore evidence absent | 3×5=15 | 3×5=15 | 1×5=5 | Data owner, 30 days |

## Audit program

Compliance lead sets scope and independence. Control owners produce records and an independent reviewer signs findings. Quarterly and after material releases, freeze revision/profile, sample every privileged route and feed source, and select both valid and invalid actions per role, including cross-user object access. Examine configurations and historical logs, interview owners about operating procedures, and test on disposable fixtures with a connection tripwire. Record requirement, UTC time, command, expected/actual result, artifact hash, and reviewer. Preserve original artifacts with restricted access and redact credentials before sharing. Resolve disputes against evidence, track exceptions with expiration, and close findings only after independent retest. Escalate active unauthorized access immediately.

Use [NIST SP 800-30](https://csrc.nist.gov/pubs/sp/800/30/r1/final) for assessment structure and [NIST CSF 2.0](https://www.nist.gov/cyberframework) as an outcome map. The scoring scale is local to this report.

| Control / CSF outcome | Test or monitoring evidence | Assurance |
|---|---|---|
| C-01 / PR.AA-05 access permissions | E07 0/15 baseline. E08 reports 15/15 in explicit secured profile. Check weekly for anonymous access and monitor unauthorized role changes. | Baseline failed. Secured result historical. Deployment unverified. |
| C-02 / PR.DS-10 data in use | E07 16/26 baseline. E08 reports 26/26. Sample rejected writes and 5xx response hygiene each release. | Historical scope only. |
| C-03 / PR.DS-06 integrity | E07 54/55 incl. one prior browser result. E08 reports 55/55 with fresh browser check. Track stale sources, host mismatches and partial failures daily. | Local evidence. Ongoing operations unverified. |
| SSH / PR.PS-01 configuration | E03 observed one open port. Request ACL evidence and negative test from non-management segment. | Operating control unverified. |
| Recovery / RC.RP-03 restoration integrity | Restore known policy versions in disposable storage and compare hashes. Record time and data loss against agreed targets. | No restore proof. |

## Findings and remediation

| Priority | Condition and effect | Closure evidence |
|---|---|---|
| P0 R1 | Current isolated policy creation and publication returned 201 where the legacy suite expected denial. Fake-session records confirm attempted writes. Verify which profile is exposed and enforce server-side policy-write authorization. | Verify deployed entry point, deny anonymous requests, validate role matrix and private-object boundaries, record approved rollout. |
| P1 R2/R3 | Classroom admin exposure and historic schema failures leave profile-specific uncertainty. | ACL test and real local relational negative-write checks with evidence. |
| P1 R4 | The baseline accepted a reputable source label on an unrelated host. | Per-source origin, redirect and browser inert-render tests with revision and official-source success proof. |
| P1 R5/R6 | Dependency and recovery assurance incomplete. | Lock/SBOM review, advisory triage, supplier data-flow review, witnessed restore with integrity checks. |

**Exact rubric requirements satisfied:** detailed quantification methodology and scoped risk assessment, formal audit procedures and guidelines, professional findings and recommendations. Control mapping and advanced validation evidence are provided with historical scope. Operating compliance controls and monitoring are partial.

**Existing evidence reused:** E03, E06–E10, including comparative historical control counts.

**New tests performed:** The current legacy suite recorded 23 passes and 18 failures in [raw results](control-bounded.txt) and [JSON](control-results.json). Policy creation and publication returned 201. Several validation expectations received 401 before payload validation, so those assertions require signed-identity retesting. Historical retests retain original dates and profiles.

**Missing evidence:** deployed secured control validation, operating monitoring records, management-network ACL verification, and witnessed recovery test.

**Evidence completion review:** See [failure classification, fresh evidence and manual requirements](completion-matrix.md). New results are preserved under followup/. JWT foundation passed 24/24 and five schema checks passed. Installed package metadata covers 35 local distributions. These checks apply to their stated local scope. Remaining limitations and overall PARTIAL status are retained.

**Status: PARTIAL.**


