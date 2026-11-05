# DeRexi: Policy Pilot
# Compliance 1 — Assignment 5: Legal & Ethical Implementation

**Institution:** Aurum Capital Bank (fictional classroom institution)

**Prepared:** November 5, 2026, America/New_York

**Baseline:** development commit `c4641b5`, branch `codex/derexi-security-hardening`

**Purpose:** capstone implementation and evidence report; no regulatory certification or determination of institutional compliance.

## 1. Executive Summary

DeRexi now has an obligations matrix, an eight-step ethical decision process with three applied scenarios, a scored 12-risk register, and an incident response procedure. These reuse Assignments 1–4 and the November 5 security evidence. Governance procedures below are **DOCUMENTED/PROPOSED**, pending institutional approval and operational exercises.

Small backend changes restore incident policy references and enforce coherent incident transitions. The final targeted run records **112 PASS, 0 FAIL**: 17 new controls/compatibility tests, nine original incident regressions, 32 secured/demo API tests, 28 validation tests and 26 original C-02 checks. The four previously failing guidance tests now pass without changing their assertions. Earlier failing evidence remains intact.

Production release remains blocked. The ordinary `main:app` is still an unguarded compatibility profile; protected behavior requires the explicit authenticated factory. Messages remains unavailable in this checkout. Real sign-in, PostgreSQL integration, deployment/TLS, record retention and immutable business audit history are unverified or incomplete. No live Supabase data, identities, RLS, grants or migrations were accessed or changed in this work.

## 2. Organizational and Regulatory Context

Aurum is described in project materials as a federally chartered private bank with Lending and Wealth Management divisions. This fictional description does not establish a legal charter, primary regulator, deposit-insurance status, actual business activities, jurisdiction or data-processing obligations. Confirm each before selecting applicable rules, reporting duties or retention periods. Internal policy text is not automatically GLBA nonpublic personal information; classification depends on its contents and processing context.

The baseline is GLBA, FFIEC guidance, NIST CSF 2.0 and NIST SP 800-53 Rev. 5. GLBA and applicable implementing regulations may be binding; FFIEC materials are supervisory guidance; NIST publications are frameworks/control catalogs unless separately adopted or made mandatory. The FTC Safeguards Rule is **not automatically the governing rule for a federally chartered bank**. Counsel must select the relevant regulator's standards; a national-bank analysis could consider OCC 12 CFR Part 30 Appendix B, subject to confirmation. Regulation P applicability also needs review.

Application roles remain **Employee, Policy Owner and System Administrator**. “Compliance lead,” “legal/privacy function,” “records custodian” and “deployment operator” below are proposed accountable business functions, not new database roles or permission grants. Policy Owners may create/edit their assigned drafts; initial approval/publication requires a System Administrator. Code/development-tool access confers no application authority. The isolated local persona switcher is development tooling, never production authentication.

Assignment 1's original artifact uses **Orange Capital Bank**; retain it as historical coursework and use Aurum here. Assignment 2 program/Pulse documents were reviewed from existing `origin/main` Git objects and were not merged into this branch. Assignment 4 is a dated assessment, preserved as written; the incident fixes below supersede its incident-gap status only.

## 3. Legal and Regulatory Obligations Matrix

The two keyed tables form one matrix. **All legal applicability, exact clause wording and source currency require legal review.** Official hosts are excluded by the enforced cloud allowlist; current reference verification is BLOCKED (E5). Stable repository references are reused. A tested technical safeguard is not proof that an entire legal obligation is fulfilled.

| ID | Source / citation and classification | Requirement or expected practice | DeRexi workflow / affected business function | Proposed control owner |
| --- | --- | --- | --- | --- |
| O01 | GLBA, 15 USC §6801(b); **conditional binding law**, implementing standard to be selected [S1] | Protect security/confidentiality of customer information against threats and unauthorized access. | Policy/incident/clarification data; Lending, Wealth Management, IT | Compliance lead + System Administrator |
| O02 | GLBA, 15 USC §6802; applicable privacy rule including Regulation P to be confirmed; **conditional binding law/regulation** [S1] | Determine permissible disclosure of covered nonpublic personal information and applicable notices/exceptions. | Private conversations, feedback, AI-provider disclosure; privacy/client services | Legal/privacy function |
| O03 | FFIEC IT Examination Handbook, Information Security; **supervisory guidance** [S2] | Restrict access by role, review permissions and apply least privilege. | Identity resolution, policy publication, private records; IT and policy governance | System Administrator |
| O04 | FFIEC IT Examination Handbook, Information Security; **supervisory guidance** [S2] | Define incident reporting, escalation, investigation and management oversight. | Incident/clarification handling; security and compliance operations | Incident handler + compliance lead |
| O05 | NIST CSF 2.0, PR.AA; **voluntary framework** [S3] | Manage identities, authentication and authorized access. | Secured API and separate local demo; IT | System Administrator |
| O06 | NIST CSF 2.0, PR.DS and DE.CM; **voluntary framework** [S3] | Protect data and monitor for adverse events with interpretable evidence. | Confidential records and Policy Health Dashboard; records/compliance | Records custodian + compliance lead |
| O07 | NIST CSF 2.0, RS.MA and RS.CO; **voluntary framework** [S3] | Manage incidents and coordinate appropriate communications. | Incident procedure and escalation; security/client operations | Incident handler + legal/privacy function |
| O08 | NIST SP 800-53 Rev. 5, AC-3/AC-6; **recommended control-catalog mapping**, not certification [S4] | Enforce approved access and least privilege. | Owner draft editing, admin publication, incident assignment/escalation; governance | System Administrator |
| O09 | NIST SP 800-53 Rev. 5, AU-2/AU-3/AU-6/AU-9/AU-11; **recommended control-catalog mapping** [S4] | Define event content, review, protection and retention of audit records. | Approvals, status changes, evidence packages; audit/records | Records custodian + System Administrator |
| O10 | NIST CSF 2.0 GV.SC; NIST SP 800-53 Rev. 5 SR-3/SR-6 and IR-4/IR-6; **framework/recommended controls** [S3–S4] | Manage third-party/source risks and incident handling/reporting. | Pulse attribution, stale data, uncertain applicability; regulatory intelligence | Compliance lead + Policy Owner |

| ID | Existing implementation | Evidence | Gap / residual risk | Corrective action | Verification status |
| --- | --- | --- | --- | --- | --- |
| O01 | Secured JWT/actor checks, scoped private records and sanitized errors. | E1 A501/A502/A510/A512; E2 C-01 | Legacy app unguarded; no real-data classification, TLS or full safeguard assessment. | Close R02/R03/R10 before real information processing. | **IMPLEMENTED AND TESTED** for isolated access controls; legal/full safeguard coverage unverified. |
| O02 | Conversation owner-only; clarification participant-only; admin clarification oversight exposes metadata only. | E1 A510/A511 and secured privacy tests | AI-provider processing, privacy notices, permitted disclosures and data minimization not legally assessed. | Classify information and review provider/disclosure arrangements; prohibit real customer data until approved. | **IMPLEMENTED AND TESTED** for record scopes; legal/privacy program **DOCUMENTED/PROPOSED**. |
| O03 | Current server business role is authoritative; body IDs, claimed roles and local demo cookies cannot grant production access. | E1 A516, secured/demo tests; E2 C-01 | Actual Auth mapping/access-review process absent or unverified. | Review subject mapping, real sign-in, joiner/mover/leaver and periodic reviews in isolated staging. | **IMPLEMENTED AND TESTED** synthetically; operational review unverified. |
| O04 | Existing incident category/severity validation; admin assignment/escalation; new state checks. | E1 A502–A509/A515; original incidents | No automatic alert, SLA timer or complete investigation history. | Approve/exercise sections 8–9 and audit design in section 12. | Technical subset **IMPLEMENTED AND TESTED**; SOP **DOCUMENTED/PROPOSED**. |
| O05 | Signed verified principals; separate loopback demo with activation/CSRF/session rotation. | E1 A517 and 32 secured/demo tests; E3 | Normal browser production sign-in and deployment still unverified. | Test authenticated UI with approved data/auth setup before activation. | **IMPLEMENTED AND TESTED** locally; deployment **IMPLEMENTED BUT UNVERIFIED**. |
| O06 | Relational records, dashboard aggregates and dated source/test evidence. | E1 governance test; E4 metric definitions | No hold/disposal controls, historical reporting or continuous detection; UI metric ambiguities. | Approve retention and KPI definitions; correct metrics in a separate reviewed change. | Basic access/total **IMPLEMENTED AND TESTED**; retention/monitoring gaps **MISSING**. |
| O07 | Controlled status/severity/assignment updates; section 9 response and legal-review procedure. | E1 A504–A509; this report | No operational exercise, staffing agreement, notification automation or legal trigger assessment. | Tabletop all severities; approve response owners and notification decision process. | State rules **IMPLEMENTED AND TESTED**; response procedure **DOCUMENTED/PROPOSED**. |
| O08 | Owner draft editing; admin-only publication and escalation; handler cannot reassign. | E1 policy tests, A504/A505/A509 | No immutable approval decision/actor history; compatibility app bypasses these guards. | Select secured entry point; implement approved event design later. | **IMPLEMENTED AND TESTED** in secured profile. |
| O09 | Policy version rows, mutable incident/clarification records, timestamped evidence and Git history. | E4; E1 source hashes | These are not an immutable employee action log; no retention enforcement. | Approve event schema, atomicity, read scopes and retention/hold tests before any migration. | Current records **IMPLEMENTED BUT UNVERIFIED** for audit sufficiency; event/retention controls **MISSING**. |
| O10 | Closed Pulse registry, source-specific URL checks, per-source stale/cache behavior; human review procedure. | E2 C-03 and integrity tests; E5 | Live government feeds blocked; allowed host does not prove authenticity/applicability; no persistent applicability decisions. | Validate live sources when allowed; use scenario C review record before policy action. | Synthetic source controls **IMPLEMENTED AND TESTED**; live/legal review BLOCKED. |

## 4. Ethical Decision-Making Framework

**DOCUMENTED/PROPOSED:** apply this process when a request is authorized technically but its purpose, accuracy or consequences remain questionable.

1. **Recognize:** pause the questionable disclosure/action and describe the concern without assuming misconduct.
2. **Identify stakeholders:** consider requester, subject employee/customer, Policy Owner, incident handler and institution.
3. **Identify requirements:** consult approved policy, role authority and the obligations matrix; ask compliance/legal where applicability is uncertain.
4. **Assess harm:** examine confidentiality, minimum necessary access, fairness, inaccurate guidance and reversible alternatives. Apply the same criteria regardless of seniority.
5. **Compare options:** record benefits/harms of doing nothing, limited action and escalation. Avoid collecting extra private information merely to investigate.
6. **Escalate uncertainty:** route to the assigned Policy Owner/handler; a System Administrator authorizes privileged actions. Legal/privacy/compliance determines legal duties.
7. **Record rationale:** document decision, alternatives, approving function, evidence IDs, UTC time and next review; restrict access and omit secrets/private message bodies from general reports.
8. **Review outcome:** confirm the action worked, seek affected-person correction where appropriate, update policy/training and track recurrence.

Use a controlled decision record with `decision_id`, concern, stakeholders, relevant policy/version/source, options, harm assessment, chosen action/rationale, accountable reviewer, escalation, evidence references and follow-up date. This template is proposed; no new persistent application table or operational decisions were created.

## 5. Three Applied Ethical Scenarios

These are **synthetic tabletop analyses**, not actual employee conduct, legal decisions or executed operational exercises. Associated API tests verify only the stated technical boundaries.

### A. Access to another employee's clarification or incident

| Field | Tabletop decision record ETH-A |
| --- | --- |
| Dilemma / stakeholders | An employee wants another person's private thread/report to “help.” Requester, subject employee, assignee, security and compliance may be affected. |
| Options | Disclose the full record; provide a non-sensitive procedure; route a new concern to an authorized participant/handler. |
| Legal/policy considerations | Minimum necessary disclosure, confidentiality and approved role scope; GLBA applicability depends on actual data (O01–O03/O08). Administrative clarification oversight is explicitly metadata-only. |
| Preferred response / rationale | Deny private access without confirming contents; supply the reporting procedure and route a separate concern. Helpful intent does not establish authority. |
| Responsible role / escalation | Employee → assigned Policy Owner/incident handler; System Administrator for authorized incident scope or suspected account misuse; legal/privacy function for disclosure questions. Admin has no blanket private-conversation override. |
| Evidence/record created | This ETH-A analysis; executed A501/A510/A511 denial records. Proposed operational decision record would retain request purpose, denial category and referral, excluding private bodies. |

### B. Incomplete or misleading Policy Assistant answer

| Field | Tabletop decision record ETH-B |
| --- | --- |
| Dilemma / stakeholders | A plausible answer omits an exception; employee may act incorrectly. Employee, affected customer/colleague, Policy Owner and compliance bear potential harm. |
| Options | Follow the answer; compare full policy/version and seek clarification; suspend reliance and report suspected guidance error. |
| Legal/policy considerations | Accurate policy use, approved/effective version, confidentiality and fair treatment (O01/O06/O08). AI guidance is not legal advice; lexical confidence is not legal correctness. |
| Preferred response / rationale | Read the cited policy, mark unhelpful where appropriate, open a clarification and pause consequential action pending owner review. Treat actual harmful guidance as an incident under section 8. |
| Responsible role / escalation | Employee → Policy Owner; System Administrator for publication/correction authority; compliance/legal if customer or legal consequences may exist. |
| Evidence/record created | This ETH-B analysis; A503/A513 reference-gate tests and original incident tests. Proposed restricted record: question/answer IDs, cited version, missing exception, owner determination and correction, without copying unnecessary customer data. Semantic/legal accuracy is NOT TESTED here. |

### C. Uncertain Pulse authenticity or applicability

| Field | Tabletop decision record ETH-C |
| --- | --- |
| Dilemma / stakeholders | An article from an approved source appears relevant, but date, destination or institutional applicability is uncertain. Policy Owners, lending/wealth staff, customers and compliance could be affected. |
| Options | Immediately change policy; ignore the article; verify the official text, timing, source and applicability before action. |
| Legal/policy considerations | Source provenance and third-party risk (O10); guidance/frameworks are not automatically law; institution's regulator/activity must match. |
| Preferred response / rationale | Keep the item as unverified intelligence. Check official source, publication/effective dates, supersession and scope; log applicability rationale and require normal admin publication authorization. If blocked, record uncertainty and use an approved human source-review channel. |
| Responsible role / escalation | Policy Owner → compliance lead; legal function for applicability; System Administrator for approved publication or suspected malicious content. |
| Evidence/record created | This ETH-C analysis; reused C-03 evidence and E5 BLOCKED source checks. Proposed review record: canonical URL, source/title/date, retrieval time, relevant provision, applicability decision/reviewer and linked draft. No automated legal conclusion or new database record is claimed. |

## 6. Compliance Risk Methodology

**DOCUMENTED/PROPOSED:** score each scenario as **likelihood × impact**, using integer scales 1–5. Scores are illustrative planning estimates, not measured probabilities, losses or regulatory findings. Owners and timeframes are proposed functional assignments, not evidence of staff acceptance. The register distinguishes executed synthetic tests, source inspection and hypothetical future exposure.

| Level | Likelihood judgment | Impact judgment |
| --- | --- | --- |
| 1 | Rare under the assumed controlled use | Minimal reversible disruption; no expected sensitive disclosure |
| 2 | Unlikely, requiring several conditions | Limited team disruption or contained record error |
| 3 | Plausible in routine use | Material workflow interruption or limited confidentiality/policy harm |
| 4 | Likely if the documented gap persists | Significant sensitive disclosure, governance failure or prolonged interruption |
| 5 | Expected repeatedly under the stated exposure | Severe customer/institution harm, broad compromise or major legal exposure |

Severity bands: **Low 1–4; Moderate 5–9; High 10–16; Critical 17–25**. These risk bands differ from individual incident severity labels in section 8. P0 prevents unsafe release; P1 addresses material MVP/governance gaps; P2 improves reporting and automation after core controls. High-impact release dependencies can be P0 even when exposure is hypothetical.

Residual scores assume all recommended mitigation is implemented successfully. They are **estimated, unverified and not accepted risk**. Reassess after tests, tabletop exercises, material changes and each proposed monthly compliance review. Legal/compliance and the accountable business owner must approve any operational risk acceptance; there is no automated acceptance.

## 7. Risk Register with Scores

The authoritative detailed register is [assignment5_risk_register.csv](assignment5_risk_register.csv). Each row includes scenario, safeguards, evidence basis/type, gap, mitigation, proposed owner/timeframe, estimated residual likelihood/impact/score/band and status. E1–E5 refer to section 15.

| ID | Risk | L × I | Current planning band | Estimated residual L × I | Priority |
| --- | --- | --- | --- | --- | --- |
| R01 | Unauthorized access / impersonation | 3 × 5 = 15 | High | 2 × 4 = 8 Moderate | P1 |
| R02 | Unguarded compatibility entry point | 4 × 5 = 20 | Critical | 1 × 5 = 5 Moderate | P0 |
| R03 | Sensitive information disclosure | 3 × 5 = 15 | High | 2 × 4 = 8 Moderate | P1, before real data |
| R04 | Insecure/unavailable Messages workflow | 3 × 4 = 12 | High | 1 × 4 = 4 Low | P1 |
| R05 | Incorrect retrieval / citation | 3 × 4 = 12 | High | 2 × 3 = 6 Moderate | P1 |
| R06 | Delayed clarification escalation | 3 × 3 = 9 | Moderate | 2 × 3 = 6 Moderate | P1 manual queue review |
| R07 | Missing approval / audit events | 4 × 4 = 16 | High | 2 × 4 = 8 Moderate | P1 |
| R08 | Incomplete retention / legal hold | 4 × 4 = 16 | High | 2 × 4 = 8 Moderate | P1 |
| R09 | Stale/inaccurate regulatory attribution | 2 × 4 = 8 | Moderate | 1 × 4 = 4 Low | P1 before reliance |
| R10 | Unvalidated deployment / TLS | 3 × 5 = 15 | High | 1 × 5 = 5 Moderate | P0 |
| R11 | Incident workflow defects / outages | 3 × 4 = 12 | High | 2 × 3 = 6 Moderate | P1 |
| R12 | Inadequate compliance monitoring | 3 × 3 = 9 | Moderate | 2 × 3 = 6 Moderate | P1 metric correctness; P2 trends |

## 8. Compliance Incident Classification

**DOCUMENTED/PROPOSED taxonomy:** use existing incident category IDs where appropriate; the categories below are a procedure, not new seeded records. A compliance incident concerns failure to meet policy/legal/ethical requirements. A cybersecurity incident concerns compromise of confidentiality, integrity or availability. One event may be both and should have linked investigations, not duplicate conflicting facts.

| Category | DeRexi example | Primary proposed routing |
| --- | --- | --- |
| Unauthorized disclosure | Private clarification or customer information sent to an unintended recipient | Incident handler + legal/privacy |
| Improper access / account misuse | Impersonation, scope probing or incorrect subject mapping | System Administrator + security handler |
| Security / phishing | Credential phishing report or compromised account | Security handler; admin for escalation/assignment |
| Incorrect policy guidance | Answer/citation omission causes or could cause harmful action | Policy Owner + compliance lead |
| Regulatory change not addressed | Verified applicable change lacks an owner or reviewed policy action | Compliance lead + Policy Owner |
| Approval / retention violation | Unapproved publication or disposal despite hold | System Administrator + records/legal function |
| Ethical / conduct concern | Pressure to disclose private employee information or conceal an error | Compliance lead; restricted independent reviewer if conflicted |

| Existing severity label | Classification example | Proposed internal response expectation |
| --- | --- | --- |
| `low` | Contained documentation issue with no known exposure | Acknowledge within two business days; agree correction/review date. |
| `medium` | Incomplete guidance or delayed review with limited potential harm | Acknowledge within one business day; assign an accountable reviewer. |
| `high` | Suspected sensitive disclosure, account misuse or material policy error | Acknowledge within one staffed hour; notify security/compliance promptly and assess containment. |
| `critical` | Active compromise, broad disclosure or severe ongoing harm | Escalate immediately through an approved emergency channel; target acknowledgement within 15 minutes under an approved coverage plan. |

These are **proposed internal targets**, not statutory deadlines, existing staffing commitments or application timers. The prototype has no on-call/notification service. Confirm coverage, backup contacts and legally required deadlines separately. Reassess severity as facts develop; employee-selected severity/category is intake information, not an authoritative legal determination. `escalation_level` is a routing field, not a notification deadline or risk score.

## 9. Incident Reporting and Escalation Procedure

**DOCUMENTED/PROPOSED SOP — operational approval and tabletop exercise required.** Functional owners must establish contact details and an independent route for conflicts before adoption.

| Step | Responsible function and required action | Record / control |
| --- | --- | --- |
| Detection | Employee/monitor recognizes concern; stop unsafe action without destroying evidence. | Time noticed, factual summary, affected workflow; do not paste passwords/customer account details. |
| Intake | Employee submits own incident; if unavailable, use approved restricted manual/emergency channel. | Incident ID, reporter, category if known, description and perceived severity. Do not wait for AI guidance. Manual fallback must be established before operation. |
| Classification | Assigned handler assesses category, actual/potential harm, data sensitivity and urgency. | Severity rationale; distinguish allegation from confirmed facts; link related cyber/compliance matter. |
| Assignment | System Administrator selects an authorized handler and backup; check conflicts. | Assignee, responsibility acceptance/time. Existing API has assignee but no acceptance timestamp. |
| Containment | Authorized security operator limits ongoing harm; preserve originals and obtain required authority. | Containment action, actor/time, scope and preservation rationale; no destructive cleanup by reporter. |
| Investigation | Handler gathers minimum necessary facts, checks cited policy/version and interviews authorized participants. | Restricted evidence references, timeline, uncertainties, findings and chain of custody. Avoid full private conversations in general notes/reports. |
| Escalation | Handler requests escalation; System Administrator authorizes app assignment/level/status changes. Route material privacy/legal issues to legal/compliance. | Trigger/rationale, decision-maker, recipient and time. Handler cannot independently reassign/escalate or close an escalated case. |
| Corrective action | Policy Owner proposes policy/training corrections; admin authorizes publication or privileged technical change. | Action owner, due date, approval reference and validation evidence. |
| Resolution | Handler may resolve a triaged ordinary case; admin decides closure of an escalated case after review. | Findings, corrective-action evidence, rationale, residual risk and follow-up owner/date. API notes are mutable; formal sign-off remains manual/proposed. |
| Follow-up | Compliance lead/owner verifies effectiveness and recurrence; communicate only what recipients need. | Review date/outcome; policy/training update and risk-register reassessment. |
| Evidence retention | Records custodian restricts access, preserves originals/hashes and applies legally reviewed retention/holds. | Evidence index, access/hold/disposal decisions. Do not delete evidence until schedule and hold status are confirmed. |

Escalate for suspected sensitive disclosure, active compromise, repeated denials/mapping errors, material incorrect guidance, overdue high-impact corrective action, conflicting authority, or uncertainty about a legal duty. An administrator's technical privilege does not authorize unrestricted private conversation access. Clarification oversight is metadata-only; incident visibility follows the explicit incident role matrix.

**External reporting decision:** legal/privacy/compliance must determine relevant jurisdiction, regulator, covered institution/data, event facts, contractual duties, applicable thresholds and timing before deciding whether regulators, law enforcement, customers or others must be notified. Record the decision and source even when no notification is required. Do not infer duties or universal deadlines from this SOP or an AI answer.

| Record fields | Current capability versus proposed requirement |
| --- | --- |
| Incident ID, reporter, category, description, severity, status, assignee, escalation level, resolution notes, created/updated time | Existing stored fields. `updated_at` is mutable, not transition history; no persisted `resolved_at`. |
| Detection/acknowledgement time, classification rationale, assignment acceptance, timeline, evidence custody, escalation decision/recipient, containment, legal notification assessment, action due dates, resolution sign-off, follow-up, retention/hold | Proposed restricted case record/template; not separately structured or enforced by the current app. |
| Evidence access | Existing secured incident list is reporter/assignee-scoped with admin visibility; private clarification bodies remain participant-only. Proposed evidence repository requires approved access, encryption, backup/restore and retention tests. |

## 10. Technical Controls Implemented

**New, IMPLEMENTED AND TESTED:**

- `backend/main.py::incident_guidance` restores the missing helper and incident-create `guidance` response. It uses the existing approved-policy search, confidence threshold and substantive-keyword evidence gate; returns policy/version IDs, title, score and excerpt or `null`. It makes no AI call and adds a human-review notice. UI already consumes these fields; no UI edits were necessary.
- New reports start at escalation level 1. State transitions are `reported → triaged/escalated`, `triaged → escalated/resolved`, `escalated → resolved`; each status also permits an idempotent update. `resolved` is terminal. Direct reported-to-resolved and reopening return 409. Escalated requires level ≥2; reported/triaged requires level 1 when state fields change; inconsistent pairs return 422.
- `backend/secure_api.py` requires administrator authority for status/level changes on an already escalated incident, including closure. The assigned handler can still add notes/change severity. Existing admin-only assignment/escalation and own-report creation guards remain active in the secured profile.
- Validation occurs before updates. A guidance lookup error produces the existing sanitized 503 before any incident insert. Historical inconsistent records can receive notes without silent status/level repair. No existing rows or category seeds were rewritten.

**Reused, tested in the secured profile:** synthetic signed identity/role enforcement, private record filtering, participant-only clarification access, feedback ownership, safe errors, admin publication and loopback demo isolation. Test changes to two existing positive-intake cases only substitute an empty SQLite reference lookup because SQLite lacks PostgreSQL `pg_trgm`; their original assertions remain intact. The nine original incident tests are unchanged.

**Compatibility concerns:** callers must triage before ordinary resolution and send a coherent status/level pair for escalation; handler closure of escalated cases now requires admin action. Response `guidance` is additive. Reference lookup is synchronous; an unavailable search/database prevents API intake, so an approved manual fallback is necessary. The production search's “latest version of an approved policy” behavior is unchanged and does not prove version-level approval/effective-date correctness. No browser UI, ORM/schema, dependencies, authentication foundation, role names or policy ownership changed.

## 11. Testing Methodology and Results

Run from `derexi-policy-pilot/backend/` with the confirmed project virtual environment:

```bash
../.venv/bin/python tests/run_assignment5_verification.py
```

The runner executes suites in separate processes, overriding live database access with synthetic fake sessions or disposable SQLite. Original C-02 retains its `Engine.connect` tripwire. New secured tests use locally signed synthetic JWTs and a stubbed JWKS client. PostgreSQL policy ranking is substituted only in SQLite-specific fixtures; A517 exercises the actual local lexical adapter and persona switching. None of this validates PostgreSQL ranking, real Auth users or deployment.

| Current suite | PASS | FAIL | Evidence / scope |
| --- | --- | --- | --- |
| Assignment 5 controls | 17 | 0 | E1 `test_assignment5_controls.json`: A501–A517 privacy, creation, guidance, assignment, escalation, transitions, feedback, safe errors, legacy compatibility and local demo. |
| Original incident regressions | 9 | 0 | E1 `test_week8_stage1.json`; original assertions unchanged. Previous 5 PASS / 4 FAIL retained in E2. |
| Secured/demo API | 32 | 0 | E1 `test_secure_api.json`; roles, policy publication, scopes, local sessions and switching. |
| Validation hardening | 28 | 0 | E1 `test_validation_hardening.json`; real SQLite transactions and rejection/no-partial-write checks. |
| Original C-02 | 26 | 0 | E1 `test_security_controls.json`; original per-control scenarios/expected/actual outcomes. |
| **Current total** | **112** | **0** | No skipped or blocked tests in these five offline suites. |

Each E1 per-test JSON record includes ID, scenario, expected result, actual assertion outcome, status, date, environment and evidence filename; paired logs and source SHA-256 hashes support reproduction. Exact expected values/assertions remain in the identified test functions. E1's earlier `assignment5_2026-11-05T211936461949Z/` run (111 PASS) predates the additional A517 compatibility check; retain it as preliminary evidence, not an additional test count.

E1 `handoff_checks.json` separately records document structure, risk calculations,
local links, per-test record completeness, tested-source hashes, changed-file
secret-pattern scan and preservation/whitespace checks. These review checks are
not included in the 112 application-test total; the scan is not a guarantee
against every possible secret or defect.

| Reused or separate verification | Status and limit |
| --- | --- |
| November 5 C-01 / C-03 | E2: 15/15 and 55/55 PASS, respectively; historical controlled execution, not rerun for this incident-only change. C-03 includes its actual Chromium proof. |
| Other November 5 regressions | E2: Stage 1 40, auth 24, Pulse 97 and additional integrity 22 PASS; unchanged areas, reused rather than counted in current 112. |
| Browser | E2: 14 PASS, 0 FAIL; MSG-001 BLOCKED. No new browser run or claim that Messages works. |
| Official legal reference verification | E5: four BLOCKED records; official hosts excluded by enforced allowlist. No citation currency/applicability verification or bypass. |
| Live Pulse sources | E2: BLOCKED by proxy 403 for all four configured sources; no new live-source claim. |
| Production Auth/UI, PostgreSQL integration, TLS/deployment, semantic/legal answer correctness, operational SOP exercise | NOT TESTED in this task; acceptance work remains in section 12. |

## 12. Gaps, Residual Risks and Remediation Plan

| Priority / risks | Next controlled action | Acceptance evidence required; current status |
| --- | --- | --- |
| P0 — R02/R10 | Select explicit secured factory for any deployment; keep compatibility isolated. Provision reviewed Auth mapping and approved local data separately; validate normal UI sign-in and TLS/proxy setup in staging. | Deployment/config review plus actual sign-in, denial and transport tests. BLOCKED/NOT TESTED; no deployment authorized here. |
| P1 — R03/R05 | Classify data and approve AI-provider use; review effective/approved version retrieval and answer corpus in isolated PostgreSQL. | Privacy decision, corpus expectations, negative retrieval and data-minimization tests. NOT TESTED. |
| P1 — R04/R06/R11 | Resolve MSG-001 with a scoped contract; approve SOP/manual fallback/backup contacts and exercise assignment, escalation, guidance outage and follow-up. | Participant-only Messages tests, timed tabletop records and corrective-action ownership. Missing route remains BLOCKED; incident guidance is now fixed. |
| P1 — R07/R08 | Approve audit-event/retention design before a migration or operational records use. | Atomic event tests, authorization, hold, restoration and disposal evidence. Persistent controls MISSING. |
| P1 — R09 | Enable approved official-source access separately and review current law/source text/applicability. | Read-only live fetch/redirect evidence plus legal applicability decision. BLOCKED. |
| P1/P2 — R12 | Reuse dashboard and Assignment 4 definitions. Correct “open” incident counts, null feedback and due-window labels; distinguish decorative bars from measured rates, then add period snapshots if required. | Metric edge-case assertions and reviewed management report. Source-inspected issues remain; no UI changes in this task. |

**Exact proposed audit change — not applied:** add `compliance_audit_events` with server-generated event ID, UTC occurrence time, stable business actor ID, object type/ID, action, prior/new status, reason code, correlation ID, entry profile and allowlisted non-sensitive metadata. Record approval/publication and incident assignment/escalation/closure in the same transaction as the business change. Preserve actor identity if accounts are deactivated; do not cascade-delete audit history. Restrict writers to the approved service path, restrict reads to authorized oversight, and control retention/legal holds and administrative deletion. General audit records must exclude private message bodies, credentials and unnecessary customer information. Policy/version approval needs an explicit approved-version decision so later drafts cannot silently become “current approved” content.

**Proposed tests — NOT TESTED:** failed business change creates no event; failed event insert rolls back the business change; actor/time cannot be supplied or overwritten by the client; unauthorized read/write/update/delete is denied; permitted oversight omits private payloads; concurrent transitions produce a consistent history; held records survive disposal; approved expiry disposes only eligible records; evidence backup restores with matching hashes; deactivation preserves attribution. This requires reviewed schema/migration, privileges/RLS, retention policy and staging authorization. No SQL migration or live audit table was created.

## 13. Legal and Operational Limitations

This report is a classroom artifact, not legal advice, regulator approval, certification or a claim of actual bank compliance. Current official-source wording and legal applicability were not independently verified online. A qualified legal/compliance reviewer must determine the applicable rules, required notifications and retention periods.

Passing synthetic tests establishes the asserted local behavior only. Production Auth mapping, existing live employee data and counts, real PostgreSQL query behavior, deployment/TLS, AI-provider privacy, legal/semantic correctness, durable event history and operational staffing were not validated. Metadata-only clarification oversight does not grant permission to inspect private conversations. The browser's developer selector remains available; its existence is not production authentication.

No live Supabase connection, data modification, Auth identity creation, RLS/grant/migration change, public deployment or main-branch merge occurred. Policies, versions, employee IDs/departments, assigned roles/ownership, UI assets and earlier coursework/evidence are preserved. Commit/push is limited to the authorized development branch after review and checks; this report's E1 hashes identify the tested source independently of the later commit ID.

## 14. Conclusion and Rubric Completion Checklist

| Assignment 5 rubric requirement | Documentation completion | Traceability |
| --- | --- | --- |
| Legal/regulatory obligations | Complete structured matrix, with legal/source verification limitations explicit | Sections 2–3/15, O01–O10, E5 |
| Ethical decision-making | Complete eight-step framework and three applied tabletop decisions | Sections 4–5, ETH-A/B/C; selected E1 privacy/reference tests |
| Compliance risk assessment | Complete 5×5 method, 12 scored risks, proposed owners/actions and estimated residuals | Sections 6–7/12; detailed CSV |
| Compliance incident response | Complete classification, reporting/escalation/investigation/resolution/follow-up procedure | Sections 8–10; E1 tested technical subset |

All four **documentation** requirements are addressed. Operational adoption, legal approval and the remaining implementation controls require further work; an SOP or proposed test does not constitute implemented functionality. The technical scope completed here is incident guidance restoration, coherent state validation, escalated-closure authority and their isolated tests.

## 15. References and Evidence Index

Paths are relative to `derexi-policy-pilot/` unless prefixed **repository root** or `origin/main:`.

| ID | Exact reusable artifact / reference | Purpose and limitation |
| --- | --- | --- |
| E1 | [Current verification summary](evidence/assignment5_2026-11-05T212025135075Z/verification_results.json); paired `test_assignment5_controls.json`, `test_week8_stage1.json`, `test_secure_api.json`, `test_validation_hardening.json`, `test_security_controls.json` and `.log` files in the same folder | Current 112 tests; per-test outcomes and source hashes. Preliminary run retained in `evidence/assignment5_2026-11-05T211936461949Z/`. |
| E2 | [Assignment 3 final report](assignment3_security_hardening_final.md); `evidence/verification_2026-11-05T170344061112Z/verification_results.json`; `evidence/resume_2026-11-05T170350233804Z/audit_results.json`; `evidence/browser_resume_2026-11-05_EF61bG/browser_results.json` and PNGs | November 5 C-01/C-02/C-03, browser, feed blockers and original incident failures. Historical evidence remains unchanged. |
| E3 | [Security entry points](../security-entrypoints.md), [RBAC review](../rbac-design-review.md), [known issues](../development-known-issues.md) | Exact profiles, permissions and issue chronology. |
| E4 | [Assignment 4 analysis](assignment4_gap_analysis.md), [database design](../database-design.md), `backend/{main.py,secure_api.py,rbac.py,auth.py,principals.py,models.py,schemas.py,dev_demo.py}`, `backend/static/app.js`, `policies/ACB-COMP-001_policy_governance_compliance_client_confidentiality.md` | Reused implementation, metric definitions and governance text; policy prose does not establish enforcement. |
| E5 | [Official-source access status](evidence/assignment5_2026-11-05T212025135075Z/source_access_status.json) | Four BLOCKED reference checks against current enforced cloud allowlist; no content fetch/bypass. |
| E6 | **Repository root:** `compliance_1/DeRexi_Compliance_Assignment_1_Expanded.docx`, corresponding `.pdf`, `compliance_1/Compliance 1 Tasks.pdf` | Prior baseline, rubric and planned procedures; original institution name retained. |
| E7 | `origin/main:compliance_1/C 1 Assignment 2.pdf`; `origin/main:derexi-policy-pilot/docs/compliance-assignment-2/{README.md,integration-notes.md,testing-results.md}` at reviewed `5329718` | Program/governance/training proposals and Pulse documentation; upstream-only artifacts, not merged. |
| E8 | `backend/tests/{test_assignment5_controls.py,run_assignment5_verification.py,test_week8_stage1.py,test_secure_api.py,test_validation_hardening.py,test_security_controls.py}` | Reproduction commands and exact assertions; no live DB use. |
| S1 | [FTC GLBA overview](https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act); [FTC Safeguards explanation](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know) | Stable official links already in Assignment 1. Legal statutory locators above require review; FTC materials do not establish bank regulator jurisdiction. |
| S2 | [FFIEC IT Examination Handbook booklets](https://ithandbook.ffiec.gov/it-booklets) | Existing official baseline; applicable booklet edition and wording require review. |
| S3 | [NIST CSF 2.0, CSWP 29](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) | Existing official framework reference; mapping/currency require review. |
| S4 | [NIST SP 800-53 Rev. 5 official publication locator](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), DOI `10.6028/NIST.SP.800-53r5` | Official reference locator supplied for the requested baseline; current page/control wording not fetched or independently verified. |

**Report to upload for PDF preparation:** `derexi-policy-pilot/docs/compliance/assignment5_legal_ethical_implementation.md`. Include the risk CSV if the full register should appear as an appendix.
