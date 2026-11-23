# Problem Statement

## Banking and fintech context

A lending or wealth-management employee may need a policy answer while handling
customer information, completing a process or reporting a suspicious event.
Policies distributed across documents and owners create practical ambiguity:
which version is approved, who can clarify it, whether an answer applies, and
which security channel should receive a report. DeRexi's original design identifies
this policy-governance information gap; the implemented domain is the fictional
Aurum Capital Bank. No real customer incident or quantified industry statistic is
used as evidence. [S01 · EDU_Project_Design_Doc_Final V.1.docx](../../semester_2/EDU_Project_Design_Doc_Final%20V.1.docx) [S22 · database-design.md](../../semester_3/DeRexi_Week%203/database-design.md) [S03 · README.md](../../derexi-policy-pilot/README.md)

## Problem to solve

Employees need source-backed guidance without guessing. Owners need visible,
traceable clarification and review work. Administrators need controlled publication
and scoped oversight while protecting staff conversations and draft policy data.
A generic generated answer or a negative-feedback counter alone does not provide
an accountable policy decision. [S24 · employee-guide.md](../../semester_5/DeRexi_Week%2011/employee-guide.md) [S25 · policy-owner-guide.md](../../semester_5/DeRexi_Week%2011/policy-owner-guide.md) [S26 · system-admin-guide.md](../../semester_5/DeRexi_Week%2011/system-admin-guide.md)

## Design response and limits

Use approved policy versions and lexical retrieval with an evidence gate, retain
citations, route uncertainty to an owner/triage, persist feedback and messages,
and require independent review before publication. Incident intake must request
employee review and consent; the normal institutional incident channel remains
essential for urgent response. The app assists governance; it does not grant policy
exceptions, certify regulatory compliance or replace investigation/ticket resolution.
[S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S07 · governance.py](../../derexi-policy-pilot/backend/governance.py) [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) [S14 · messaging.py](../../derexi-policy-pilot/backend/messaging.py)

## Boundary

The intended benefit is better access, accountability and consistency. Actual
productivity improvement, representative answer accuracy and production rollout
need measured acceptance evidence; current fixture passes do not establish them.
[S17 · test-report.md](../../semester_5/DeRexi_Week%2010/test-report.md) [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md)

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
