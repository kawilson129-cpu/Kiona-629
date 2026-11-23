# Key Features & Functions

## Status language

**Implemented** means present in inspected source; **tested** identifies a specific
retained result and environment. **Planned** means a proposal, not delivered behavior.
**Unverified** means no suitable execution/deployment evidence. A feature can be
implemented and locally tested while remaining unverified in production.

| Feature | Implemented behavior | Tested evidence, retained | Planned/unverified boundary |
|---|---|---|---|
| Policy Assistant + Library | Approved current-version retrieval, score ≥0.22 plus keyword gate, citation/reference, optional rewrite/fallback and browse/detail | Source and local HTTP/UI uncertainty path; prior policy checkpoints | Lexical score is not calibrated probability. Representative PostgreSQL ranking/LLM-answer quality not established by mocked search |
| Answer feedback | POST saves Yes/No rating; repeat rating updates the row; Dashboard exposes authorized aggregates | Week 10 persistence/error/department-scope checks; earlier UI-only save claim superseded | A negative rating does not automatically email an owner, create a ticket or publish a revision |
| Clarification + Messages | Owner/triage routing, scoped replies, notifications, unread/read markers | Retained messages/security/integration suites | Real human response times and production UAT unverified |
| Directory/ownership | Protected `/users`, roles/departments and policy-owner relationships; email returned only to Admin/self | Source authorization and existing role tests; read-only core metadata | A dedicated full directory UI is not established; do not infer user-provisioning/role-editor functionality |
| Governance + document intake | Draft/revision, bounded DOCX/PDF text extraction, independent peer/final approval, explicit publication and history | 102 lifecycle and 47 document checks in retained Nov 12 suites | No OCR or automatic publication scheduler. Latest detailed live readiness observation (Nov 12) found Governance tables absent |
| Incident assistance | Event heuristics, urgent guidance, reviewed follow-ups/consent, internal reference, approved routing and explicit dispatch | 75 support and 17 mocked SMTP/TLS checks, plus isolated browser evidence | Support schema activation, approved real destinations and delivery/ticketing unverified; outbound default OFF |
| Policy Health Dashboard | Role-scoped policy/review/feedback/clarification/incident indicators | Retained scoped feedback/Dashboard integration | Operational visibility is not compliance certification; production metrics/SLAs unmeasured |
| Pulse | Four government feeds: two JSON, two RSS; normalization, classification labels/cache, original source links and source-linked draft/revision handoff | Isolated source-validation tests; Nov 18 public 200 observations and actual UI | Not a threat-intelligence platform or legal adjudicator. No automatic approval/publication; current feed uptime not rechecked |

## Evidence and practical limits

The preserved Nov 10 CT+V audit detected concurrent Pulse source drift. Its
original hashes limit that audit to the inspected revision; later test reports
do not rewrite the historical failed integrity check. This documentation neither
reruns that audit nor declares its drift record cleared. [S41 · concurrent-source-drift.json](../../cyber_threats_and_vulnerabilities_2/CT%2BV%202%20Assignment%203/evidence/concurrent-source-drift.json)

Feature implementation: [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S07 · governance.py](../../derexi-policy-pilot/backend/governance.py) [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) [S14 · messaging.py](../../derexi-policy-pilot/backend/messaging.py) [S15 · document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) [S36 · app.js](../../derexi-policy-pilot/backend/static/app.js).
Pulse: [S12 · sources.py](../../derexi-policy-pilot/backend/pulse/sources.py) [S13 · service.py](../../derexi-policy-pilot/backend/pulse/service.py). Testing and corrections: [S17 · test-report.md](../../semester_5/DeRexi_Week%2010/test-report.md) [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md) [S19 · final-summary.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/final-summary.json).
Original UI and HTTP evidence: [S28 · http-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json) [S29 · browser-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/browser-results.json).

The November 12 read-only readiness inventory is the latest reviewed observation
about absent Governance/support tables, zero Auth users and incomplete peer-owner
coverage. The later November 23 check verified core tables/counts only and **did
not recheck those missing tables or Auth state**. Do not silently carry either
observation beyond its measured scope. [S20 · live-readonly-preflight.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) [S21 · live-readonly-20261123.json](../../postgresql_1/evidence/live-readonly-20261123.json)

No standalone customer-data portal, user/role provisioning UI, semantic vector store,
real ticket-provider adapter or production deployment is claimed. These distinctions
replace broader expectations in the early design with the actual current build.

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
