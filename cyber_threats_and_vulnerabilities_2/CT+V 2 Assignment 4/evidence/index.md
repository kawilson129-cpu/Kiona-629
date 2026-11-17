# Evidence register and source ledger

Access/review date: November 17, 2026. All new output stays in Assignment 4. Historical files are referenced in place, not copied or altered. `reuse-manifest.json` records validation-time SHA-256 hashes of selected prior documents; it does not claim those files match their original published versions.

## Current evidence

Authoritative run: **20261117T114241633169Z**, identified by [latest-run.txt](latest-run.txt).

| Evidence ID | Artifact | Scope |
|---|---|---|
| E-FRESH | [summary](20261117T114241633169Z/summary.json) | Commands, timings, Python, outcomes: 297 PASS / 3 FAIL / 4 BLOCKED |
| E-FRESH-SEC | [security results](20261117T114241633169Z/security/results.json) | 88 existing assertions + safety check; `suite.log`, `week9-security-results.json` and `security-events-sanitized.json` adjacent |
| E-FRESH-GOV | [governance results](20261117T114241633169Z/governance/results.json) | 102 lifecycle assertions + safety check; fresh execution, no historical overwrite |
| E-FRESH-PULSE | [Pulse results](20261117T114241633169Z/pulse/results.json) / [focused checks](20261117T114241633169Z/focused/results.json) | 97 offline assertions, four focused host cases, PostgreSQL tripwire and child guards |
| E-FRESH-DEP | [dependency results](20261117T114241633169Z/dependency-results.json), [inventory](20261117T114241633169Z/inventory.json) | 37 distributions; lock and two historical version-match conditions fail; no full online/deployed advisory scan |
| E-SOURCE | [source fingerprints](20261117T114241633169Z/source-hashes-before.json), [integrity result](20261117T114241633169Z/source-integrity.json) | 56 app/test/harness files unchanged during final run |
| E-QA | `package-validation-*.json`, `reuse-manifest.json` | Independent artifact links, arithmetic, evidence consistency and source identity checks; not new security tests |

Each suite has `process.log`, `suite.log`, actual result JSON and an assignment-local `tmp/` folder. Empty temporary folders are expected for in-memory fixtures. No screenshots were necessary: raw commands, checks, logs and hashes provide verifiable evidence.

Retained diagnostic runs: `20261117T113049661426Z` (100/5/7), `20261117T113646825834Z` (296/4/4), and `diagnostic-security/` (88 existing assertions passed; NUL guard false alarms). These are **not added to final totals**. See [execution notes](execution-notes.md) for causes. Their failed guards blocked operations before side effects; they do not establish production control failure.

## Existing coursework and SDLC evidence

| Evidence ID | Existing source | Use and qualification |
|---|---|---|
| E-RUBRIC | [official tasks PDF](../../Cyber%20Threats%20and%20Vulnerabilities%202%20Tasks.pdf), [existing rendering](../../CT+V%202%20Assignment%203/evidence/official-rubric-page1.png) | Risk/audit row visually read; expected original SHA-256 `5961118200fea38c10c2e9cf1d4aa6685c6f5750ddbcc44082c5ebcd9351f07b` |
| E-A1 | [Assignment 1 supply chain](../../CT+V%202%20Assignment%201/docs/supply-chain-assessment.md), [final summary](../../CT+V%202%20Assignment%201/docs/final-summary.md) | Campaign/supply-chain threat context and unresolved version/provenance conditions; original sample work not claimed |
| E-A2 | [Assignment 2 closure](../../CT+V%202%20Assignment%202/closure/README.md), [assets](../../CT+V%202%20Assignment%202/closure/assets-reconciled.json), [raw advisories](../../CT+V%202%20Assignment%202/closure/advisories/assessment.json) | Historical controls/asset population and exact advisory records, aliases and prerequisites |
| E-A3 | [Assignment 3 final](../../CT+V%202%20Assignment%203/docs/final-summary.md) | 32 local passing / 5 platform blocked; capacity gate remains, no new platform claim |
| E-A5 | [Assignment 5 risk/audit](../../CT+V%202%20Assignment%205/04-risk-audit.md), [failure classification](../../CT+V%202%20Assignment%205/completion-matrix.md) | Earlier ordinal planning and profile-specific failures; this CSV adds explicit monetary assumptions without rewriting old scores |
| E-COMP | [C-01/C-02 baseline](../../../compliance_1/C%201%20Assignment%203/rubric1_security_test_results.md), [C-03 baseline](../../../compliance_1/C%201%20Assignment%203/assignment3_c03_audit_results.md), [secured profile](../../../compliance_1/C%201%20Assignment%203/assignment3_security_hardening_final.md) | November 3 failures and November 5 separate-profile improvements preserved |
| E-SDLC | [Week 11 readiness](../../../semester_5/DeRexi_Week%2011/pinned-readiness-status.md), [activation checklist](../../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md), [deployment documentation](../../../derexi-policy-pilot/docs/deployment.md) | Historical missing production/Auth/schema/ACL/transport/recovery/logging acceptance; not fresh live metadata |
| E-TESTS | [fixture](../../../derexi-policy-pilot/backend/tests/messaging_fixture.py), [security](../../../derexi-policy-pilot/backend/tests/test_week9_security.py), [governance](../../../derexi-policy-pilot/backend/tests/test_week8_governance.py), [Pulse](../../../derexi-policy-pilot/backend/tests/test_pulse.py) | Existing source imported freshly without copying/editing; only output adapters are process-local |

## Authoritative framework research

All accessed November 17, 2026. These sources support the crosswalk; our scoring, cadence and treatment priorities are local proposals.

- [GLBA 15 USC 6801](https://www.govinfo.gov/content/pkg/USCODE-2022-title15/pdf/USCODE-2022-title15-chap94-subchapI-sec6801.pdf): statutory safeguard context; 2022 printed compilation, current banking detail checked against eCFR.
- [Current 12 CFR Part 30 Appendix B](https://www.ecfr.gov/current/title-12/chapter-I/part-30/appendix-Appendix%20B%20to%20Part%2030): risk, access/change/dual controls, testing, provider oversight and reporting sections. Selected mapping is not an applicability opinion.
- [FFIEC Information Security booklet, September 2016](https://www.ffiec.gov/sites/default/files/media/press-releases/2016/2016-%20it-handbook-information-security-booklet.pdf): II.A–D, II.C.7/10/14/15/17–22, III.C–D, IV.A.3–4 used as navigable topics.
- [NIST CSF 2.0, February 26, 2024](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf): current outcome naming, including PR.PS-04 logging and PR.DS-11 backups.
- [SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final): risk assessment structure, not endorsement of hypothetical monetary inputs.
- [SP 800-53 Rev. 5 and 2025 update notice](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), [SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final): selected controls and examine/test/interview method.

Retrieval limits: legacy FFIEC audit landing/PDF routes and a guessed OCC handbook URL were inaccessible. They were not used as inspected authority; the accessible official FFIEC Information Security booklet's assurance chapter was used instead. A 2003 OCC issuance and Federal Reserve IT-audit guidance were discovery/context aids, not represented as a newly issued audit standard. No framework text was copied into the package.
