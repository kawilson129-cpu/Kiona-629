# Evidence map · Existing DeRexi repository

All paths below are original evidence references, not new execution claims.
The original binary plan was read through its OOXML cells/text without changing it.
Hashes protect inspected sources; no secret/environment files are included.

| ID | Existing source | Supports assignments | Evidence scope |
|---|---|---|---|
| S01 | [semester_2/EDU_Project_Design_Doc_Final V.1.docx](../semester_2/EDU_Project_Design_Doc_Final%20V.1.docx) | 01, 02, 03, 05, 07, 10, 13 | Original Aug 13 design: purpose, proposed tools and goals |
| S02 | [semester_2/EDU_Project_Design_Excel_Final V.1 .xlsx](../semester_2/EDU_Project_Design_Excel_Final%20V.1%20.xlsx) | 01, 10 | Original 12-week SDLC outcomes; cells extracted read-only |
| S03 | [derexi-policy-pilot/README.md](../derexi-policy-pilot/README.md) | 01, 02, 03, 06, 07, 13 | Canonical app, architecture, endpoint inventory and operational caveats |
| S04 | [derexi-policy-pilot/backend/main.py](../derexi-policy-pilot/backend/main.py) | 01, 04, 05, 06, 08, 09, 11, 12 | Actual /ask, retrieval gates, directory, feedback and safe-error middleware |
| S05 | [derexi-policy-pilot/backend/schemas.py](../derexi-policy-pilot/backend/schemas.py) | 01, 07, 08, 09, 11 | Request validation and body fields |
| S06 | [derexi-policy-pilot/backend/security.py](../derexi-policy-pilot/backend/security.py) | 01, 04, 06, 07, 08, 09, 11 | Verified identity, database-derived roles and access boundaries |
| S07 | [derexi-policy-pilot/backend/governance.py](../derexi-policy-pilot/backend/governance.py) | 01, 04, 06, 07, 10, 11 | Draft/review/approval/publication and schema-availability behavior |
| S08 | [derexi-policy-pilot/backend/incident_assistance.py](../derexi-policy-pilot/backend/incident_assistance.py) | 01, 04, 06, 07, 08, 09, 11, 13 | Event detection, reviewed confirmation, explicit dispatch and OFF-by-default SMTP |
| S09 | [derexi-policy-pilot/backend/models.py](../derexi-policy-pilot/backend/models.py) | 01, 06, 07 | Implemented ORM entities and relationships; not proof all tables are deployed |
| S10 | [derexi-policy-pilot/backend/database.py](../derexi-policy-pilot/backend/database.py) | 01, 07, 08, 11 | SQLAlchemy engine/session and private configuration loading |
| S11 | [derexi-policy-pilot/backend/ai.py](../derexi-policy-pilot/backend/ai.py) | 01, 06, 07, 08, 09, 11, 13 | Optional OpenAI-compatible rewriting and failure fallback |
| S12 | [derexi-policy-pilot/backend/pulse/sources.py](../derexi-policy-pilot/backend/pulse/sources.py) | 01, 06, 07, 11, 13 | Four actual source endpoints: two JSON and two RSS |
| S13 | [derexi-policy-pilot/backend/pulse/service.py](../derexi-policy-pilot/backend/pulse/service.py) | 01, 06, 07, 11, 13 | Source normalization, provenance, cache and degraded-source states |
| S14 | [derexi-policy-pilot/backend/messaging.py](../derexi-policy-pilot/backend/messaging.py) | 01, 04, 06, 07, 11 | Participant-scoped messages, assignments, replies and notifications |
| S15 | [derexi-policy-pilot/backend/document_intake.py](../derexi-policy-pilot/backend/document_intake.py) | 01, 06, 07, 11, 13 | Bounded document intake and private-original controls |
| S16 | [derexi-policy-pilot/requirements.txt](../derexi-policy-pilot/requirements.txt) | 01, 07, 13 | Declared runtime dependencies/ranges, not an installed-version lock |
| S17 | [semester_5/DeRexi_Week 10/test-report.md](../semester_5/DeRexi_Week%2010/test-report.md) | 01, 04, 05, 06, 10, 11, 12 | 379 isolated passes; feedback/publisher fixes, mocks and seven unexecuted live workflows |
| S18 | [semester_5/DeRexi_Week 11/final-integration-results.md](../semester_5/DeRexi_Week%2011/final-integration-results.md) | 01, 04, 05, 06, 10, 11, 12 | November 12 final isolated results, native Windows probes and scope |
| S19 | [semester_5/DeRexi_Week 11/evidence/final-integration-20261112/final-summary.json](../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/final-summary.json) | 01, 06, 10, 12 | Machine-recorded 622 PASS, 0 FAIL, 14 platform skips; live UAT pending |
| S20 | [semester_5/DeRexi_Week 11/evidence/final-integration-20261112/live-readonly-preflight.json](../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) | 01, 04, 06, 07, 10, 11, 12, 13 | Nov 12 schema/owner/Auth/grant metadata; dated observation only |
| S21 | [postgresql_1/evidence/live-readonly-20261123.json](../postgresql_1/evidence/live-readonly-20261123.json) | 01, 06, 07, 10, 11, 12 | Earlier Nov 23 read-only PostgreSQL 17.6 core-schema/count/JOIN evidence |
| S22 | [semester_3/DeRexi_Week 3/database-design.md](../semester_3/DeRexi_Week%203/database-design.md) | 01, 03, 07, 10 | Historical relational design and migration/seed narrative |
| S23 | [semester_5/DeRexi_Week 11/final-integration-approval-checklist.md](../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md) | 01, 04, 06, 10, 11, 12, 13 | Ordered release approval, validation and recovery gates |
| S24 | [semester_5/DeRexi_Week 11/employee-guide.md](../semester_5/DeRexi_Week%2011/employee-guide.md) | 01, 04, 06 | Employee questions, feedback, messaging and reviewed incident flow |
| S25 | [semester_5/DeRexi_Week 11/policy-owner-guide.md](../semester_5/DeRexi_Week%2011/policy-owner-guide.md) | 01, 04, 06 | Independent review and Owner workflow; no self-approval or OCR claim |
| S26 | [semester_5/DeRexi_Week 11/system-admin-guide.md](../semester_5/DeRexi_Week%2011/system-admin-guide.md) | 01, 04, 06, 11, 13 | Admin scope, explicit publication and operational duties |
| S27 | [semester_5/DeRexi_Week 9/security-findings.json](../semester_5/DeRexi_Week%209/security-findings.json) | 01, 11, 13 | Historical security risks, fixes and remaining deployment limits |
| S28 | [ai_api_intergration_1/AAI 1 Assignment 1/evidence/20261118-api/http-results.json](../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json) | 01, 04, 06, 08, 12 | 15 real loopback HTTP checks; synthetic SQLite/search mock/AI off |
| S29 | [ai_api_intergration_1/AAI 1 Assignment 1/evidence/20261118-api/browser-results.json](../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/browser-results.json) | 01, 04, 06, 12 | Seven original-UI checks; actual retained screenshots and DOM/response evidence |
| S30 | [derexi-policy-pilot/backend/migrations/2026-11-12_support_routing.sql](../derexi-policy-pilot/backend/migrations/2026-11-12_support_routing.sql) | 01, 06, 07, 10, 11 | Approval-only routing/support schema, rollback-default proposal |
| S31 | [derexi-policy-pilot/backend/session_auth.py](../derexi-policy-pilot/backend/session_auth.py) | 01, 04, 06, 07, 11 | Browser session/CSRF/provider integration code; not real onboarding proof |
| S32 | [derexi-policy-pilot/design/Meet the DeRexi Users.pdf](../derexi-policy-pilot/design/Meet%20the%20DeRexi%20Users.pdf) | 01, 04 | Historical persona concept; differs from current fixture authorization roles |
| S33 | [semester_4/DeRexi_Week 6/DeRexi_Week6_Employee_UI_Validation_Report_FINAL.pdf](../semester_4/DeRexi_Week%206/DeRexi_Week6_Employee_UI_Validation_Report_FINAL.pdf) | 01, 06, 10 | Sep 30 employee UI checkpoint; later feedback persistence fix supersedes early save claims |
| S34 | [semester_5/DeRexi_Week 11/employee-messages-walkthrough.md](../semester_5/DeRexi_Week%2011/employee-messages-walkthrough.md) | 01, 04 | Illustrative Sam/Jordan/administrator use-case walkthrough, not human sign-off |
| S35 | [derexi-policy-pilot/docs/deployment.md](../derexi-policy-pilot/docs/deployment.md) | 01, 07, 10, 11, 13 | Runtime setup and staged release/backup/rollback requirements |
| S36 | [derexi-policy-pilot/backend/static/app.js](../derexi-policy-pilot/backend/static/app.js) | 01, 04, 06, 07, 08 | Existing UI components, API calls, saved-feedback behavior and Library |
| S37 | [derexi-policy-pilot/backend/static/index.html](../derexi-policy-pilot/backend/static/index.html) | 01, 07 | Existing HTML application shell and entry points |
| S38 | [semester_4/DeRexi_Week 8/README.md](../semester_4/DeRexi_Week%208/README.md) | 01, 04, 06, 10, 11 | Governance lifecycle, unchanged Library and unexecuted activation proposals |
| S39 | [semester_3/DeRexi_Week 4/DeRexi_Week4_Document_Management_Validation_Report.pdf](../semester_3/DeRexi_Week%204/DeRexi_Week4_Document_Management_Validation_Report.pdf) | 01, 06, 10 | Historical policy storage/retrieval/version checkpoint; not full secure file intake |
| S40 | [postgresql_1/Assignment_2_Schema_Design/README.md](../postgresql_1/Assignment_2_Schema_Design/README.md) | 01, 07, 11, 13 | Nov 23 drift: roles.created_at UNIQUE, absent users.job_title; no remediation performed |
| S41 | [cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 3/evidence/concurrent-source-drift.json](../cyber_threats_and_vulnerabilities_2/CT%2BV%202%20Assignment%203/evidence/concurrent-source-drift.json) | 01, 06, 11, 13 | Historical Nov 10 Pulse source drift: audit limited to original hashes; not a current integrity verdict |

## Reconciliation rules and gaps

- Original plan alternatives are intent, not implementation. Current code shows
  lexical pg_trgm, vanilla UI, optional compatible LLM rewrite and SMTP OFF.
- Original persona PDF differs from current fixture roles; it is not the live
  authorization directory. Role-based workflows and database-derived identity govern.
- Nov 10's 379 passes, Nov 12's 622/0/14 summary, Nov 18's 22 loopback/UI passes
  and Nov 23's eight read-only DB checks are different/overlapping scopes; never add them.
- Source documents differ in age: Week 6 UI save claims were superseded by Week 10
  persisted-feedback repair; older Week 7 proposal labels do not erase later implementation.
- Nov 12 readiness gaps about Auth/feature tables/owners are not closed by the Nov 23
  core-table-only query. Actual production state beyond each observation remains unverified.
- No representative retrieval corpus, target latency benchmark, real provider/SMTP
  acceptance, live human UAT or final deployment/presentation evidence is invented.
- A1 master contains all topic content; supporting references are not substitutes
  for missing master sections. Mermaid files are editable; no unavailable renderer is claimed.

[Source manifest](evidence/source-manifest.json) · [Original timeline extraction](evidence/original-plan-extract.json)
· [Tool availability](evidence/tooling.json) · [Current offline validation](evidence/validation.json).
