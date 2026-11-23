# Future Considerations

## Ongoing maintenance requirements

| Requirement | Rationale / proposed owner | Implementation and validation considerations |
|---|---|---|
| Policy/version and source review | Guidance must remain accurate and owned; Compliance/Policy Owners | Review dates, explicit approved revisions, source-type/date verification and stale-feed notices; test that unpublished edits never replace current guidance |
| Identity, least privilege and dependency upkeep | Staff responsibilities and vulnerabilities change; Admin/operator | Review verified subject bindings and role/department access, remove obsolete grants, assess dependency updates in staging; requirements ranges are not a reproducible release lock |
| Backup, private-original retention and audit operations | Recover policy state and protect retained employee/document content; operator | Approve retention/access/encryption, test DB+file restore together, reconcile orphan/unknown-send states and durable redacted logs; current code/tests are not infrastructure evidence |
| Endpoint health and safe workflow regression | Provider/feed formats and deployment environments change; developer/operator | Re-run focused authorized tests in new evidence directories, preserve historical failures, verify data freshness, and confirm intended-host parser limits and rollback before release |

These are ongoing operational requirements/proposed cadences, not a claim that
production monitoring/restore/onboarding is already active. [S35 · deployment.md](../../derexi-policy-pilot/docs/deployment.md) [S23 · final-integration-approval-checklist.md](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md) [S13 · service.py](../../derexi-policy-pilot/backend/pulse/service.py) [S16 · requirements.txt](../../derexi-policy-pilot/requirements.txt)

## Proposed future features — not currently delivered

| Proposal | Rationale | Potential implementation and acceptance work |
|---|---|---|
| Evaluated semantic/hybrid policy retrieval | Lexical wording can miss equivalent employee questions | After source-policy permissions/versioning are reliable, pilot embeddings/vector indexing keyed to approved versions; compare against lexical baseline on G1 corpus, enforce authorization and citations, measure cost/latency and rollback safely. ChromaDB/FAISS was an early idea, not an existing dependency |
| Authenticated ticket-provider integration | The original goal included preliminary IT tickets; current references/email acceptance are not created tickets | Select an approved provider/API, least-privilege secret storage, employee consent, idempotency and durable delivery/ticket-ID reconciliation; verify actual provider acknowledgement without claiming resolution |
| Request deduplication for ordinary Assistant submissions | Repeated POST /ask after uncertain network outcomes can create duplicate conversations | Add a reviewed actor-scoped request key and database uniqueness/expiry contract, test concurrent retries and response replay; do not confuse this proposal with the existing support-dispatch claim mechanism |

The priority is to close documented schema, owner coverage, provider identity,
direct-client ACL/RLS, transport/storage and human-acceptance gates before adding
features. The Nov 23 catalog exposes a pending-seed column mismatch; migrations
must be reviewed and tested in isolated staging rather than applied from coursework.
[S01 · EDU_Project_Design_Doc_Final V.1.docx](../../semester_2/EDU_Project_Design_Doc_Final%20V.1.docx) [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) [S20 · live-readonly-preflight.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) [S40 · README.md](../../postgresql_1/Assignment_2_Schema_Design/README.md)

No new application feature, dependency, account, migration or operational job is
created by this future plan.

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
