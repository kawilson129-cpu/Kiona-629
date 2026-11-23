# Evaluation Criteria

## Targets are not results

The targets below are **proposed design acceptance thresholds**, not previously
achieved production metrics. Keep the corpus, actor permissions, environment,
sample size and timestamps with every measurement. Human reviewers must confirm
business correctness; a green response status alone is insufficient.

| Indicator | Measurement method | Proposed target | Observed evidence / gap |
|---|---|---|---|
| Grounded retrieval/citation quality | Independently label 20 answerable + 10 unsupported synthetic banking questions; manually check citation/version and escalation | ≥18/20 correct citations; 10/10 unsupported requests avoid invented authoritative answers | Representative corpus not measured. Existing score gates and fixture clarification are not this accuracy result |
| Authorized workflow isolation | Predeclare at least 12 role/ownership allow-deny cases; inspect API status and private-object visibility | 12/12 expected outcomes; zero nonparticipant private-thread disclosures | Retained local messages/security/HTTP tests pass in their stated scope; real provider/RLS acceptance unverified |
| Governance consistency | Execute one independent three-actor draft→peer→Admin→publish cycle, edit invalidation and unchanged-Library checks | All required transitions/denials correct; zero unpublished draft exposure | 102 local lifecycle checks passed in Nov 12 suite; no live publication/UAT claim |
| Saved feedback integrity | Submit a rating, read its persisted record/aggregate, change rating and retry after an injected save failure | One row per actor/answer; exact authorized aggregates; no false “saved” state | Week 10 actual persistence defect corrected and isolated handoff/browser tests passed; early UI-only claim superseded |
| Approved-policy API responsiveness | After release prerequisites, measure 100 bounded staging GET /policies requests on stated hardware, capture p50/p95 and errors | p95 ≤2 seconds, zero unhandled failures for this controlled sample | No comparable benchmark retained. Provider rewrite latency is excluded and must be measured separately |

## Retained observations, kept separate

| Dated evidence family | Recorded result | What it does not establish |
|---|---|---|
| Nov 10 Week 10 report | 379 PASS / 0 FAIL, including 37 browser checks | Seven live handoffs not executed; fixtures/mock provider/feed, not production UAT [S17 · test-report.md](../../semester_5/DeRexi_Week%2010/test-report.md) |
| Nov 12 latest-per-suite summary | 622 PASS / 0 FAIL / 14 platform-skipped checks | Not an additive total with Week 10; mock SMTP/provider/SQLite and Windows-specific scope [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md) [S19 · final-summary.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/final-summary.json) |
| Nov 18 API coursework | 15 actual loopback HTTP + 7 original-UI browser passes | Search mocked, external AI off, synthetic SQLite; no real provider login/answer-quality metric [S28 · http-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json) [S29 · browser-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/browser-results.json) |
| Earlier Nov 23 PostgreSQL check | 8 read-only checks pass; 49 policies, 12 users, 7 departments, 3 roles | No INSERT, application workload, representative retrieval or production release validation [S21 · live-readonly-20261123.json](../../postgresql_1/evidence/live-readonly-20261123.json) |

No application test is rerun for this course. Do not sum overlapping suites or
convert platform skips, pending human sign-off or unverified delivery into passes.
Actual completion requires the appropriate release environment and a recorded
owner-approved acceptance decision. [S23 · final-integration-approval-checklist.md](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md)

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
