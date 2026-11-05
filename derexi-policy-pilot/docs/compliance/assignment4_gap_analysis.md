# Assignment 4 — Documentation & Reporting gap analysis

**Reviewed:** November 5, 2026; development commit `c4641b5`. Paths below are relative to `derexi-policy-pilot/` unless marked repository-root or `origin/main:`. This is a documentation/source/evidence review: no application changes, new test runs, live Supabase access, commits or pushes.

**Conclusion:** reuse the existing program documents, Policy Health Dashboard and evidence runners. Assignment 4 chiefly needs a controlled documentation package, management summary, metric definitions and records-management procedures—not another dashboard.

Labels: **IMPLEMENTED AND TESTED** means supported by the November 5 controlled evidence, not production certification; **IMPLEMENTED BUT UNVERIFIED** means code exists but the specific behavior/value lacks adequate verification; **DOCUMENTED/PROPOSED** identifies written requirements/design; **MISSING** identifies an absent capability/artifact.

## 1. Existing compliance documentation

| Item | Status | Reusable content / limitation |
| --- | --- | --- |
| Assignment 1 requirements analysis | DOCUMENTED/PROPOSED | Repository-root `compliance_1/DeRexi_Compliance_Assignment_1_Expanded.docx` and `.pdf`: GLBA applicability, FFIEC/NIST mapping, process map, responsibilities, C-01/C-02 procedures and verification-record template. Planning artifact, not legal certification. It still names **Orange Capital Bank**; current project uses Aurum. Retain original and add a current-context note. |
| Assignment 2 compliance program | DOCUMENTED/PROPOSED | `origin/main:compliance_1/C 1 Assignment 2.pdf`: governance chart, stakeholder communications, proposed weekly/monthly/quarterly cadence, draft **DRX-CMP-001 v0.1**, approval/version workflow, remediation SOP and training/assessment design. Explicitly not approved governance or delivered training. Available in the reviewed Git ref, not this branch's working files. |
| Assignment 2 Pulse documentation | DOCUMENTED/PROPOSED | `origin/main:derexi-policy-pilot/docs/compliance-assignment-2/README.md`, `integration-notes.md`, `testing-results.md`: API, classifications, cache, UI and historical tests. Do not confuse this feature package with the program-development PDF above. These files are upstream-only here. |
| Assignment 3 reporting/evidence process | IMPLEMENTED AND TESTED | Current final report, dated JSON/logs, control scenarios and browser screenshots already provide findings, baseline/retest comparisons, commands and limitations. Reuse them as the technical appendix. |
| Schema and policy procedures | DOCUMENTED/PROPOSED | `docs/database-design.md` and `policies/ACB-COMP-001_policy_governance_compliance_client_confidentiality.md`: record relationships, owner/review obligations, version history and audit preparation. Written retention/approval statements do not prove technical enforcement. |
| Assignment 4 expectations | DOCUMENTED/PROPOSED | Repository-root `compliance_1/Compliance 1 Tasks.pdf` (scanned rubric, reviewed via OCR): versioned templates/distribution; management status report; retention/access procedures; basic KPI monitoring/reporting framework. Existing assets cover parts of each, not complete operational implementation. |

## 2. Current Policy Health Dashboard metrics

Source: `backend/main.py::policy_health`; rendering: `backend/static/app.js::buildOverview`, `buildQueueMini`. All API metrics are current database-wide aggregates, without reporting-period, owner or department filters, historical snapshots or a returned report-as-of timestamp. The secured profile permits Policy Owners/System Administrators and denies Employees.

| Metric | Actual calculation | Status / assurance |
| --- | --- | --- |
| Policy total | `count(*)` of all `policies`, including draft/retired; not approved-policy percentage. | IMPLEMENTED AND TESTED — synthetic total of three explicitly asserted. |
| Conversations, messages, incidents | Separate all-row counts of their respective tables. Messages include user and assistant messages. | IMPLEMENTED BUT UNVERIFIED — queries execute in the dashboard test; individual totals/edge cases are not explicitly asserted. |
| Policies by status | Count policy rows grouped by `status`. | IMPLEMENTED BUT UNVERIFIED — no dedicated distribution assertion found. |
| Reviews due | Latest version by `created_at DESC, id DESC`; count approved policies whose latest version has `requires_review=true`, non-null review date and `review_date <= UTC today + 30 days`. Includes overdue **and** upcoming reviews; excludes unflagged versions. | IMPLEMENTED BUT UNVERIFIED — cutoff, flag, null-date and tie cases lack targeted tests. |
| Clarifications by status | Count request rows grouped by `status`. | IMPLEMENTED BUT UNVERIFIED — full distribution not pinned by dashboard tests. |
| Incidents by status/severity | Independent counts grouped by each field. | IMPLEMENTED BUT UNVERIFIED — no dedicated aggregation assertions. |
| Feedback | Count all feedback rows; helpful = `rating=true`; not helpful = `rating=false`; rate = `round(helpful / total, 3)`, or `null` when total is zero. UI rounds rate × 100 to an integer percent. | IMPLEMENTED BUT UNVERIFIED — no dashboard denominator/zero-feedback/duplicate-rating assertions. This is feedback-row helpfulness, not distinct-employee satisfaction. |
| Top five cited policies | Count `policy_citations` joined through versions to policies, group by policy, order count descending/title, limit five. Counts citation rows, not unique users or conversations. | IMPLEMENTED BUT UNVERIFIED — ranking/count edge cases not explicitly asserted. |
| UI “Needs attention” | Badge = open/in-progress clarifications **plus all incident-status counts**. Review count is listed separately but excluded from badge. “Incidents in flight” therefore also counts resolved incidents. | IMPLEMENTED BUT UNVERIFIED — code-inspection finding; no new runtime reproduction performed. |

**IMPLEMENTED AND TESTED:** the endpoint's role restrictions, successful real aggregate-query execution on disposable SQLite, and browser governance access. Evidence is `test_secure_api.py::test_governance_real_aggregate_queries_role_matrix` plus the November 5 browser record. This does not validate every metric definition or real PostgreSQL totals.

## 3. Available KPIs: use existing measures only

| Existing measure | Status | Reporting interpretation |
| --- | --- | --- |
| Policy/review workload, status distributions, clarification/incident workload, citation counts and feedback rate | IMPLEMENTED BUT UNVERIFIED | Reuse Section 2 fields with their exact denominators/limitations. Do not turn counts into a regulatory-compliance score or invent targets. |
| Security-control test progress | IMPLEMENTED AND TESTED | November 5: C-01 **15/15**, C-02 **26/26**, C-03 **55/55** in their documented secured/offline/browser scopes. These are test outcomes, not production compliance percentages. |
| Pulse source health/freshness | IMPLEMENTED AND TESTED | Existing JSON provides per-source `ok`, `count`, `error`, optional `stale`, plus `generated_at`/`checked_at`. Refresh is request-driven with a 30-minute per-source cache—not scheduled monitoring or measured uptime. |
| SLA attainment, incident MTTR, training completion, acknowledgment coverage, regulatory coverage or audit-completeness score | MISSING | No implemented/verified KPI for these was found. Do not report them from partial timestamps, editorial Pulse scores or historical notes. |

## 4. Existing records, audit trails and version history

| Record capability | Status | Boundary |
| --- | --- | --- |
| Policy/version records and citations | IMPLEMENTED AND TESTED | Version creation/read path, author identity, permission checks and answer-to-version citations exercised with synthetic data. Model includes version number, text, dates and creator. |
| Clarification/feedback records | IMPLEMENTED AND TESTED | Requester/assignee, replies/senders, created/resolved timestamps and feedback user/message linkage support case traceability; API persistence/ownership tests exist. The Messages screen still lacks its GET endpoint. |
| Incident records | IMPLEMENTED AND TESTED | Reporting, assignment, severity/status, escalation and notes persist in controlled tests. Four pre-existing guidance tests still fail. |
| Complete event/approval audit trail | MISSING | Approval permission exists, but no `approved_by`/`approved_at`, immutable approval event, policy-status history, access-denial log or general audit-event model was found. Version `created_by` is not an approval signature. |
| Incident transition/resolution history | MISSING | Current fields are mutable; `updated_at` is not a transition log or reliable resolution timestamp. No incident `resolved_at` field. |
| Regulatory-review register | MISSING | Pulse is read-only with an in-memory cache, not a persistent archive of applicability decisions, assigned reviewers, linked policy changes or review sign-offs. Test feed fixtures are not operational regulatory records. |
| Tamper-proof history and retention enforcement | MISSING | Design calls versions immutable, but no append-only enforcement/evidence vault/legal-hold/disposal workflow was found. ORM cascade/set-null rules are not retention controls. No live database enforcement was inspected. |
| Training, acknowledgment, notification/read-receipt records | DOCUMENTED/PROPOSED | Assignment 2 describes training evidence; Week 7 proposes receipt/notification tables in unapplied SQL. Do not count these as completed operational records. |

## 5. Reporting and evidence management

| Capability | Status | Reuse / gap |
| --- | --- | --- |
| Repeatable technical evidence collection | IMPLEMENTED AND TESTED | Runners save timestamped JSON/logs, commands/return codes, source hashes and separate known failures; browser captures screenshots and hostile-content checks. Original baselines retained. |
| Git source/document version control | IMPLEMENTED AND TESTED | Reviewed development commit `c4641b5` and Stage 1 `4eac30a` establish code checkpoints. This is not employee-record audit history, signed management approval or proof of main-branch deployment. |
| Management status-report template and controlled distribution | MISSING | Technical reports are reusable, but no completed Assignment 4 management package with reporting period, recipient list, reviewer/sign-off and distribution record was found. Assignment 2 supplies the proposed stakeholder/cadence design. |
| Saved dashboard reports, period trends, CSV/PDF export or scheduled delivery | MISSING | API JSON and manually written documents exist; no dedicated business-report generation/snapshot/export/scheduler found. Do not describe test JSON as a business-report export. |
| Formal records/evidence procedure | DOCUMENTED/PROPOSED | Existing bank policy calls for retained evidence and references a retention schedule; no completed record-class schedule with durations/triggers, accountable custodian, access review, legal hold and authorized disposition procedure was found. |
| Production evidence integrity/availability | IMPLEMENTED BUT UNVERIFIED | Source hashes and Git support traceability, not signed/tamper-proof evidence storage or verified backup/restore. Actual record access, retention, PostgreSQL behavior and deployment are not established by the synthetic tests. |

## 6. Specific gaps and remaining limitations

| Gap | Status | Significance |
| --- | --- | --- |
| Dashboard presentation/definition accuracy | IMPLEMENTED BUT UNVERIFIED | “Reviews due” UI text says past review date although calculation includes next 30 days; “in flight” includes resolved incidents; zero-feedback API `null` becomes `0%` in JS; policy/conversation bars use fixed 100% and review bar fixed 60% when nonzero. Those bars are not measured compliance rates. |
| Policy definition versus implementation | DOCUMENTED/PROPOSED | ACB-COMP-001 defines current version as approved and effective; code selects most recently created version and applies policy-level status, without version-level approval/effective-date gating. Retained rows alone do not prove historical “effective policy at time X.” |
| Formal approvals, duplicate feedback and evidence provenance | MISSING | No approval-event log; feedback has no user/message uniqueness constraint, so repeated ratings can weight the rate. No complete evidence register with requirement/control, collector, date, reviewer, retention class and authoritative run designation. |
| Current operational validation | IMPLEMENTED BUT UNVERIFIED | `main:app` remains unguarded compatibility; explicit secured profile is tested. Real employee demo snapshot/Auth mapping absent; live feeds blocked by proxy 403; live Supabase and deployment untested. Earlier live-feed results must not replace November 5 limitations. |
| Messages and incident guidance | MISSING | GET `/messages` absent (browser explicitly BLOCKED); incident suite is 5 pass/4 existing guidance failures. These restrict a claim of complete case-reporting functionality. |

## 7. Prioritized recommendations — documentation first

| Priority | Recommendation | Status |
| --- | --- | --- |
| P0 | Carry the secured-versus-legacy distinction, synthetic-only evidence, live-feed block and outstanding defects into every management report. Do not publicly expose compatibility mode or claim certified/legal compliance. | DOCUMENTED/PROPOSED |
| P1 | Assemble Assignment 4 from Assignment 1 framework mapping + Assignment 2 governance/policy/SOP/training design + current Assignment 3 results. Add a short management summary with dated status, business impact, action owner, target/review date and evidence references; keep old reports unchanged. | DOCUMENTED/PROPOSED |
| P1 | Write one metric dictionary using Section 2 formulas, scope, denominator, source, owner and refresh rules. Reconcile the policy's current-version definition. Separately scope focused tests/corrections for review dates, resolved incidents, zero/duplicate feedback, citation ordering and misleading bars—do not rebuild the dashboard. | DOCUMENTED/PROPOSED |
| P1 | Complete a records-management SOP/schedule and evidence index; obtain authorized retention/legal review rather than invent statutory durations. Reuse existing access matrix and proposed stakeholder/cadence plans. Record approval/distribution and residual-risk decisions. | DOCUMENTED/PROPOSED |
| P2 | In a separate implementation task, add narrowly scoped approval/change events and reporting snapshots/export only where the agreed procedure needs them; address Messages/guidance defects and verify on approved isolated data before operational rollout. | DOCUMENTED/PROPOSED |

## 8. Exact reuse files

All rows below refer to existing assets; statuses describe the supported capability, not a fresh test run.

| Files | Status | Reuse |
| --- | --- | --- |
| Repository-root `compliance_1/DeRexi_Compliance_Assignment_1_Expanded.docx` / `.pdf`; `compliance_1/Compliance 1 Tasks.pdf` | DOCUMENTED/PROPOSED | Requirements, verification template and Assignment 4 rubric. |
| `origin/main:compliance_1/C 1 Assignment 2.pdf` | DOCUMENTED/PROPOSED | Existing program policy/SOP, governance/distribution and training design; upstream-only. |
| `origin/main:derexi-policy-pilot/docs/compliance-assignment-2/{README.md,integration-notes.md,testing-results.md}` | DOCUMENTED/PROPOSED | Existing Pulse feature/reporting documentation; upstream-only, historical results. |
| `docs/compliance/{rubric1_security_test_results.md,assignment3_c03_audit_results.md,assignment3_security_hardening_final.md}` | IMPLEMENTED AND TESTED | Baseline/finding/retest report structure; latest final report governs assurance limits. |
| `docs/compliance/evidence/verification_2026-11-05T170344061112Z/{verification_results.json,*.log}` | IMPLEMENTED AND TESTED | Actual suite outcomes, known failures, commands and source hashes. |
| `docs/compliance/evidence/resume_2026-11-05T170350233804Z/audit_results.json`; `docs/compliance/evidence/browser_resume_2026-11-05_EF61bG/{browser_results.json,*.png}` | IMPLEMENTED AND TESTED | Per-control scenario evidence and current browser screenshots/results. Earlier failed attempts/baselines remain historical evidence. |
| `backend/main.py::policy_health`; `backend/static/app.js::{buildOverview,buildQueueMini}` | IMPLEMENTED BUT UNVERIFIED | Reuse calculations/UI; preserve the metric-specific caveats above. |
| `backend/models.py`; `backend/secure_api.py`; `backend/tests/{test_secure_api.py,test_validation_hardening.py}` | IMPLEMENTED AND TESTED | Existing records, secured access, transaction and dashboard endpoint evidence; no proof of immutable audit history. |
| `backend/pulse/{service.py,sources.py,integrity.py,routes.py}`; `backend/static/pulse.js`; `backend/tests/{test_pulse.py,test_c03_audit.py,test_pulse_integrity.py}` | IMPLEMENTED AND TESTED | Regulatory-awareness metadata, classifications, freshness/error state and tested integrity checks. |
| `backend/tests/{run_hardening_regressions.py,run_compliance_audits.py,test_hardening_browser.cjs}` | IMPLEMENTED AND TESTED | Existing evidence-generation framework; no new runner needed. |
| `docs/database-design.md`; `policies/ACB-COMP-001_policy_governance_compliance_client_confidentiality.md`; `docs/week7/README.md` | DOCUMENTED/PROPOSED | Schema/procedure language and explicitly proposed additions. Reconcile “immutable/current version” claims with implementation. |
| `docs/{security-entrypoints.md,rbac-design-review.md,development-known-issues.md}` | DOCUMENTED/PROPOSED | Access/distribution boundaries, known defects and accurate deployment caveats. |

**Assessment outcome:** existing documentation and monitoring provide the starting package. Management reporting, controlled distribution and a concrete records-retention procedure remain to be completed; technical history must not be presented as an immutable operational audit trail. No new KPI values or live record counts are asserted here.
