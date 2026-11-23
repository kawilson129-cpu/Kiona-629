# Risk Mitigation

## Assessment basis

Likelihood/impact below are **qualitative design assessments**, not measured
probabilities. Owners are proposed accountable roles, not newly assigned production
users. Existing security findings, release gates and operational design provide
evidence; an isolated passing suite does not erase a live deployment risk.
[S27 · security-findings.json](../../semester_5/DeRexi_Week%209/security-findings.json) [S23 · final-integration-approval-checklist.md](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md) [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md)

| Risk | Likelihood / impact | Mitigation | Proposed accountable role | Validation | Current evidence/status |
|---|---|---|---|---|---|
| R1 · Wrong policy or unsupported AI guidance | Medium / High | Lexical/keyword gate, approved versions, citations, uncertainty routing, optional-provider fallback; human review remains essential | Policy Owner / Compliance | Review G1 golden questions; test unsupported requests/provider failures | Implemented safeguards; representative answer accuracy unverified [S04 · main.py](../../derexi-policy-pilot/backend/main.py) |
| R2 · Unauthorized data access through privileged backend or direct clients | Medium / High | Verify identity, database roles and participant/department scope; keep personas loopback; separately validate least-privilege direct-client grants before release | System Administrator / deployment operator | Allow/deny matrix plus separately authorized staging Data API/RLS checks | Local RBAC tested; Nov 12 direct-client/provider gates pending [S27 · security-findings.json](../../semester_5/DeRexi_Week%209/security-findings.json) |
| R3 · Schema/staffing drift blocks governed publication or intake | High at last readiness observation / High | Ordered staged migration review, backups/recovery, eligible independent peers; fail unavailable rather than bypass review | Deployment operator with Policy Owner lead | Compare live catalogs and peer coverage with proposals; approved staging migration/idempotency trial | Nov 12 missing feature tables; Nov 23 core drift observed; no change made [S20 · live-readonly-preflight.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) |
| R4 · Duplicate or misdirected external handoff / false delivery claim | Medium / High | Approved destinations, employee consent, explicit dispatch, durable send claim, capped safe retries; unknown outcomes never auto-resend | IT/SOC operator | Retained mock transport/TLS cases plus separately approved real delivery/reconciliation test | SMTP adapter implemented/tested with mocks, default OFF; live delivery unverified [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) |
| R5 · Malicious document or sensitive content exposure | Medium / High | Bounded file/text/resources, safe parser failure, private originals, screened input and reviewed outbound details; no claim of comprehensive DLP | System Administrator / security reviewer | Malformed/encrypted/oversized parser cases, platform resource tests and private-file access checks | Local/native scopes tested; intended-host, storage retention and restore acceptance pending [S15 · document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) |
| R6 · Stale or mislabelled regulatory publication drives wrong action | Medium / High | Bind source host, retain dates/type/provenance, show stale/error states and require independent policy review; never auto-publish | Compliance Policy Owner | Publisher-spoof/source-failure tests; periodic endpoint/content checks and human source review | Local validation and prior public downloads observed; no freshness/compliance guarantee [S13 · service.py](../../derexi-policy-pilot/backend/pulse/service.py) |

## Explicit release gates

The preserved Nov 10 CT+V audit detected concurrent Pulse source drift. Its
original hashes limit that audit to the inspected revision; later test reports
do not rewrite the historical failed integrity check. This documentation neither
reruns that audit nor declares its drift record cleared. [S41 · concurrent-source-drift.json](../../cyber_threats_and_vulnerabilities_2/CT%2BV%202%20Assignment%203/evidence/concurrent-source-drift.json)

Do not activate a feature merely because its code is present: obtain approved
schema/peer capacity, real identity and scoped direct-client access, trusted transport,
private storage/backups/restore, durable redacted logs and human acceptance. The
Nov 12 inventory is dated; Nov 23 confirms core PostgreSQL and exposes the absent
job_title/pending-seed mismatch, not completion of every release gate. [S20 · live-readonly-preflight.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) [S21 · live-readonly-20261123.json](../../postgresql_1/evidence/live-readonly-20261123.json) [S40 · README.md](../../postgresql_1/Assignment_2_Schema_Design/README.md)

There is no automatic incident investigation or comprehensive secret detector.
The reviewed support dispatch has its own durable state/idempotency behavior;
ordinary repeated `/ask` POSTs can create another conversation. Future request
deduplication should not be described as already implemented. [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py)

## Review cadence

Proposed cadence: owners review source/content risks monthly and after policy or
regulatory changes; the operator reviews access/dependencies/backups before every
release and after incidents. Track evidence/date/owner and residual risk, then
approve, defer or remediate explicitly. This cadence is a maintenance proposal,
not a claim of an operating production risk committee.

[Editable risk register](risk-register.csv).

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
