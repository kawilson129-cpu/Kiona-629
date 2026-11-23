# Three-Month Development Timeline

## Planning basis

Use **project Month 1 = Weeks 1–4, Month 2 = Weeks 5–8, Month 3 = Weeks 9–12**.
These are relative months, not invented calendar start/end dates. The original
design is version-dated Aug 13, 2026; no authoritative project-start calendar date
was established. The editable timeline table/CSV maps the actual 12-week workbook
outcomes to current evidence and delays. [S01 · EDU_Project_Design_Doc_Final V.1.docx](../../semester_2/EDU_Project_Design_Doc_Final%20V.1.docx) [S02 · EDU_Project_Design_Excel_Final V.1 .xlsx](../../semester_2/EDU_Project_Design_Excel_Final%20V.1%20.xlsx)

| Month | Planned milestone | Verified checkpoint / outstanding work |
|---|---|---|
| 1 | W4: organized policy/database and document-management foundation | Existing relational/core backend and policy record/version evidence; full secure file intake came later |
| 2 | W8: usable employee-to-owner workflow and administrator oversight | Existing UI, Messages and local Governance/Dashboard; persistence corrections and live schema/peer staffing still needed attention |
| 3 | W12: evaluated, documented MVP ready to release/present | Local tests/guides/runbooks retained; actual production activation, live UAT and final presentation acceptance remain unverified |

## Weekly milestones, targets versus observations

| Month / week | Original target | Existing observation | Status / change |
|---|---|---|---|
| 1 / W01 | Requirements, scope, users and 12-week plan | Original design/Week 1 mockup exists; precise completion date not established [S01 · EDU_Project_Design_Doc_Final V.1.docx](../../semester_2/EDU_Project_Design_Doc_Final%20V.1.docx) | Artifact/documented; no invented calendar deadline |
| 1 / W02 | Research, personas, architecture and wireframes | Existing personas/design artifacts reviewed; roles evolved; proposed stack not all adopted [S32 · Meet the DeRexi Users.pdf](../../derexi-policy-pilot/design/Meet%20the%20DeRexi%20Users.pdf) | Historical design, not current role directory |
| 1 / W03 | Database/backend design and setup | Relational design and earlier Nov 23 core PostgreSQL catalog/connectivity verified [S21 · live-readonly-20261123.json](../../postgresql_1/evidence/live-readonly-20261123.json) | Existing foundation verified; later check is not proof of meeting original week deadline |
| 1 / W04 | Document-management upload/extraction/metadata | Week 4 report proves policy storage/retrieval/version metadata; secure DOCX/PDF intake evidenced later [S39 · DeRexi_Week4_Document_Management_Validation_Report.pdf](../../semester_3/DeRexi_Week%204/DeRexi_Week4_Document_Management_Validation_Report.pdf) | Partial original target at early checkpoint; bounded intake matured in Weeks 8–10 |
| 2 / W05 | Grounded AI search/retrieval and citations | Lexical pg_trgm, 0.22/keyword gate and optional rewrite implemented [S04 · main.py](../../derexi-policy-pilot/backend/main.py) | Method changed from vector proposal; representative accuracy unmeasured |
| 2 / W06 | Employee UI and source/owner visibility | Sep 30 UI report exists; actual feedback persistence repair documented in Week 10 [S33 · DeRexi_Week6_Employee_UI_Validation_Report_FINAL.pdf](../../semester_4/DeRexi_Week%206/DeRexi_Week6_Employee_UI_Validation_Report_FINAL.pdf) | UI checkpoint verified historically; early saved-feedback assurance superseded |
| 2 / W07 | Feedback/email previews and owner notifications | Messages/clarification implemented; saved-feedback repair and handoffs tested Nov 10 [S17 · test-report.md](../../semester_5/DeRexi_Week%2010/test-report.md) | Internal messaging supplies primary loop; planned general email workflow not fully delivered |
| 2 / W08 | Administrator/policy-management dashboard | Independent lifecycle, Dashboard and document intake implemented/tested in fixtures [S38 · README.md](../../semester_4/DeRexi_Week%208/README.md) | Live Governance schema/peer-owner prerequisites pending at Nov 12 inventory |
| 3 / W09 | Authentication, least privilege, validation and logging | JWT/session/RBAC/security code and isolated tests exist [S27 · security-findings.json](../../semester_5/DeRexi_Week%209/security-findings.json) | Real provider onboarding, direct-client ACL/RLS and intended-host acceptance unverified |
| 3 / W10 | Unit/integration/usability/UAT and defect correction | Nov 10 report: 379 PASS/0 FAIL; later isolated Nov 12 summary: 622/0 with 14 platform skips [S17 · test-report.md](../../semester_5/DeRexi_Week%2010/test-report.md) | Not additive totals; seven live handoffs/human acceptance not completed |
| 3 / W11 | Release documentation, guides and installation preparation | Nov 11–12 guides, deployment/recovery plan and reviewed incident/routing integration prepared [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md) | Documentation/local work delivered; activation, real SMTP and production gates remain |
| 3 / W12 | Deploy, present, collect feedback and lessons learned | Week 12 demo/runbook exists; no reviewed proof of final live deployment or human sign-off [S23 · final-integration-approval-checklist.md](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md) | Planned/pending; no completion date or successful presentation invented |

## Schedule interpretation

Evidence dates are observation/report dates, not invented completion dates or proof
the original deadline was met. The original ambition for vector search, automatic
email and preliminary tickets was narrowed to lexical retrieval, internal messaging
and reviewed internal support references. A local “complete” report does not close
production identity, schema, operational or human-acceptance gates. [S03 · README.md](../../derexi-policy-pilot/README.md) [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md) [S20 · live-readonly-preflight.json](../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/live-readonly-preflight.json) [S23 · final-integration-approval-checklist.md](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md)

The Nov 23 read-only record re-verifies core schema/counts only; it does not
reclassify the Nov 12 Governance/support/Auth gaps as fixed or unchanged today.
The 622/0/14 and 379/0 totals describe overlapping later/earlier suite collections;
they must not be added together. No test or release was executed for this timeline.

[Editable timeline table](timeline.csv).

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
