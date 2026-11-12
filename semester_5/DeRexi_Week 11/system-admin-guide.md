# DeRexi System Admin Guide

See the [Employee](employee-guide.md) and [Policy Owner](policy-owner-guide.md) guides for common functions. Organizational oversight does not remove independent-review requirements. Deployment operations are covered in the [technical runbook](../../derexi-policy-pilot/docs/deployment.md).

## Oversight, final approval and publication

1. Open **Dashboard** for organizational policy health, feedback, clarification and incident visibility. Owners receive narrower departmental/personal information.
2. Open **Governance → Final Approvals**. Review content, metadata, source, published comparison, peer decision and history.
3. Confirm the peer is an eligible independent department Owner and you are neither author nor peer. Approve, request revisions or reject; explain changes/rejection in a comment.
4. Approved items move to **Publication**. Check the unique version, current baseline and effective date, then explicitly publish on/after that date. Publication is not automatically scheduled.
5. Confirm Library content/version and history. After an error, refresh before retrying. Saved edits invalidate approvals; changed published baselines require fresh revisions.

Admins can inspect organizational working copies/history. An Admin author still needs an eligible independent peer and another final approver. Legacy direct policy/version writes remain closed.

## Incident report → administrator triage

1. Open **Dashboard → Incidents** and find the employee report. Review category, description, severity, status and existing assignee.
2. Select an appropriate existing handler and choose **Assign**. Confirm the saved row reflects the handler/status.
3. Use **Escalate** when institutional procedures require it. Levels increase up to five. Contact security through the established urgent channel when necessary.
4. Coordinate progress with the handler. Authorized API updates also support incident status/resolution notes; use an approved operational client where an interface control is unavailable. Assignment/escalation is not a complete automated response system.
5. After an uncertain save, refresh the report before retrying. Submission alone does not prove a SOC acknowledgement.

Only Admins assign or modify incident-management fields. Others see their own or explicitly assigned reports; department membership alone does not grant broad incident access.

## Access boundaries and escalation

**Technical Routing:** choose approved destinations for each department's IT/Security rules. The deployment operator maintains the private destination registry; this panel does not accept arbitrary addresses or reveal SMTP credentials. Validation sends no email. Outbound activation and real delivery testing require separate approval. Delegate routing-only access to existing employees for specified departments; this does not grant full Admin or policy-approval permission. See the [current architecture](final-integration-architecture.md) and [approval checklist](final-integration-approval-checklist.md).

New support requests use employee-reviewed confirmation and limited internal reference/status tracking. Keep investigation and resolution in the institution's ticketing system. A sending/unknown state must be reconciled before any manual resend; accepted means SMTP acknowledgement only. Legacy incident-management APIs remain supported for existing internal reports.

There is no in-app user-provisioning/role editor. Use the authorized identity-management process. Do not create accounts, seed users or change roles to bypass a blocked review. Fictional local business users are not real Supabase Auth accounts. Production uses approved immutable Auth-subject bindings; roles/departments come from database business records with verified email agreement.

For missing reviewers, sign-in failure or workspace outage, capture time, action, safe error and request ID if available. Send these to the deployment operator without passwords, tokens, customer content or connection strings. A 403/404 may intentionally protect a private resource. Original documents must remain outside static hosting.

Before activation, complete the runbook's schema, owner capacity, Auth, direct-client grants, TLS, backups, logs and live role checks. Green health alone is insufficient. On release failure, pause publication and use the reviewed rollback plan; do not erase history or restore blanket grants.
