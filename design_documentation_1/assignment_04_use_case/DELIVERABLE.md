# Users and Use Cases

## Roles and interaction needs

| User/role | Need | Interaction with existing DeRexi | Evidence boundary |
|---|---|---|---|
| Employee; Sam is an illustrative tested profile | Find guidance and get human help when uncertain | Ask a question, inspect reference/Library, rate answer, open own clarification thread and read/reply | Real isolated HTTP/UI; representative retrieval accuracy and live identity unverified |
| Policy Owner; Jordan is an illustrative profile | Resolve assigned questions and maintain department policy | Reply in Messages; edit/import a draft; select an independent same-department peer; address changes | Scoped lifecycle/messages tested locally; live peer capacity/schema activation pending |
| System Administrator; Lucy is an illustrative profile | Oversight without bypassing independent review | Route triage, review incidents, independently approve then explicitly publish; monitor scoped Dashboard | Local role and lifecycle tests; production infrastructure/provider acceptance pending |
| IT/SOC responder or approved routing delegate | Receive actionable, correctly routed support information | Use reviewed internal reference/approved route; investigate in existing institutional system | Delegation grants are separate from business roles; actual email/ticket delivery unverified |

Names above refer to existing fixture/walkthrough examples, not evidence of real
production Auth accounts. The early persona PDF uses different conceptual names/
roles (for example Dana as an Owner and Maya as an employee). It is historical
design material, not the current authorization directory. Database-derived roles
and current workflow evidence take precedence. [S32 · Meet the DeRexi Users.pdf](../../derexi-policy-pilot/design/Meet%20the%20DeRexi%20Users.pdf) [S34 · employee-messages-walkthrough.md](../../semester_5/DeRexi_Week%2011/employee-messages-walkthrough.md) [S06 · security.py](../../derexi-policy-pilot/backend/security.py)

## UC-01 · Employee question to accountable clarification

**Preconditions:** verified employee identity, accessible published-policy database.
**Trigger:** employee submits one policy question without secrets/customer content.
The Assistant returns cited guidance when its lexical/evidence gates pass; otherwise
it stores an uncertainty answer and clarification for the policy owner, or unassigned
Admin triage when no owner is available. The employee follows the Messages link;
the assigned owner replies in the same thread. The result is a recorded answer or
accountable clarification, not permission to make an exception. [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S14 · messaging.py](../../derexi-policy-pilot/backend/messaging.py) [S24 · employee-guide.md](../../semester_5/DeRexi_Week%2011/employee-guide.md)

Unauthorized people cannot read a private thread; invalid input/session yields a
safe error. H07–H12 in the retained November 18 HTTP evidence support the actual
uncertainty path, persistence and access denials; PostgreSQL search in that fixture
was mocked to no matches. The seven retained browser checks establish actual
display/network behavior, not a new runtime verification. [S28 · http-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json) [S29 · browser-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/browser-results.json)

## UC-02 · Owner revision to independent publication

An Owner creates or revises a draft, reviews extracted text if a file was imported,
then submits to an independent eligible department peer. A separate Admin grants
final approval and explicitly publishes on/after the effective date. Saved changes
invalidate approvals; employees continue reading the published version meanwhile.
Self-approval/foreign-department access is denied. Local lifecycle evidence covers
the workflow; live staffing/schema prerequisites remain pending. [S07 · governance.py](../../derexi-policy-pilot/backend/governance.py) [S25 · policy-owner-guide.md](../../semester_5/DeRexi_Week%2011/policy-owner-guide.md) [S38 · README.md](../../semester_4/DeRexi_Week%208/README.md)

## UC-03 · Suspected incident to reviewed support reference

An actual-event question produces immediate safety guidance before retrieval.
Separate support intake collects bounded follow-ups, presents identity/route/details
for employee review, and requires explicit confirmation. Dispatch is a separate
action and defaults OFF; SMTP acceptance is never delivery or ticket creation.
An Admin can triage the internal incident reference. Urgent events use the existing
institutional IT/Security channel immediately. [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) [S26 · system-admin-guide.md](../../semester_5/DeRexi_Week%2011/system-admin-guide.md) [S18 · final-integration-results.md](../../semester_5/DeRexi_Week%2011/final-integration-results.md)

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
