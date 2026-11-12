# Final integration: incident support handoff

November 12, 2026. Runtime remains in `derexi-policy-pilot/`. New evidence lives in `evidence/final-integration-20261112/`; earlier evidence is preserved.

## Workflow and boundaries

Policy Assistant classifies actual IT/security events before policy retrieval. Deterministic indicators distinguish policy/hypothetical questions from reported events; high-risk actual events receive immediate reporting guidance. Optional bounded AI classification reuses the existing OpenAI-compatible provider, has its own off-by-default opt-in and cannot suppress deterministic urgency. No new provider call is made during tests. Classification is heuristic, not guaranteed detection or comprehensive DLP.

The employee answers two incident-type-specific questions, edits details, reviews the structured request and explicitly confirms. Identity/name/email/department come from the verified server actor, not client fields. Common explicit secret assignments, account-number-like strings, oversized input, control characters and extra recipient/identity fields are rejected. Never ask for secrets. This screening does not promise detection of all sensitive content; employee review and organizational DLP remain necessary.

`/support/assess` detects without persistence. `/support/prepare` saves a draft with identity snapshot, type, answers, urgency, approved route signature and server timestamp. `/support/requests/{id}/confirm` validates identity, route and a 24-hour review window, atomically transitions the draft and creates one existing internal incident reference. No email is sent by detection, preparation or confirmation. Editing before confirmation creates a new reviewed draft; the old draft does not submit itself.

`/support/requests/{id}/dispatch` is a separate explicit handoff attempt. Outbound defaults **OFF**. A durable compare-and-swap claim precedes external I/O; repeated confirmation/dispatch with the same reference is deduplicated. SMTP uses implicit TLS with CA/hostname verification, a fixed operator-configured sender and an exact approved recipient. No browser SMTP credentials or arbitrary To/CC/BCC are accepted. The user-generated request UUID also supplies a stable Message-ID; that header is an additional aid, not an exactly-once guarantee across external systems.

States: draft → queued → disabled, or sending → accepted/retryable/rejected/unknown/configuration_error. Only known pre-send connection/auth failures are retryable; at most three attempts, with 30/60-second exponential waits. Rejected/unknown/accepted/sending states never automatically resend. A crash after the durable sending claim requires operator reconciliation using the reference; do not reset it blindly. Accepted means SMTP server acceptance only, not inbox delivery or a created ticket. If post-send database persistence fails, the durable sending state prevents automatic resend.

Internal incident records provide a reference and administrative visibility. The existing Week 7 bell now includes a separate Admin incident-triage count/link, without changing message unread totals. Existing internal incident APIs remain supported; the employee report screen uses reviewed intake while retaining previous report history. Investigation/resolution stays in the institution's existing ticketing system. No ticketing-provider integration or delivery webhook was activated.

For compatibility before routing-schema activation, the existing internal-only form remains available in an expandable section with explicit employee review consent. It records an internal incident reference through the existing API and states that no email/ticket was created. It never calls the outbound adapter or fabricates a destination. This fallback does not replace the institution's urgent reporting channel.

## Technical Routing

The ivory/espresso/champagne panel configures department + IT/Security channel rules using only labels/keys from the operator-approved private mailbox registry. No destination is invented. Rules are revision-checked; changed routing invalidates a prepared confirmation/send rather than silently redirecting it. Disabled/missing/ambiguous rules fail closed with urgent alternative-channel guidance.

Admins can delegate routing-only access for existing users and specified departments. Grants are read from the database on every request; revocation is immediate. Delegates cannot delegate onward, edit another department or gain policy final-approval/Admin incident privileges. Their underlying business roles are unchanged. The panel validates configuration without sending mail; actual delivery testing is demonstrated with injected mock transport in isolated tests. It does not offer an accidental live test-send button.

Tables: `technical_routes`, `technical_routing_grants`, `support_requests`, `support_audit`. Existing `incident_reports` is reused. The [approval-only schema proposal](../../derexi-policy-pilot/backend/migrations/2026-11-12_support_routing.sql) enables RLS, revokes direct-client access and makes the content-free audit table append-only. Default SQL ends in ROLLBACK; it was not applied. Missing tables return honest 503 errors without rebuilding other features. PostgreSQL execution/concurrency, schema drift and direct-client denials still need staging verification.

## Configuration names

`DEREXI_APPROVED_MAILBOXES`, `DEREXI_OUTBOUND_EMAIL`, `DEREXI_INCIDENT_AI`, `DEREXI_SMTP_HOST`, `DEREXI_SMTP_FROM`, `DEREXI_SMTP_USERNAME`, `DEREXI_SMTP_PASSWORD`. Existing database/Auth/AI configuration remains in use. Keep values private; do not commit mailboxes/SMTP credentials. The registry is a map from approved key to address, human label and IT/Security channel. Invalid configuration fails closed. Only the deployment operator changes that registry; the panel selects approved entries.

No background email worker was added. Queue/dispatch status is explicit in the UI. Operational ownership, retention for unconfirmed drafts/support content, backups/restore, orphan reconciliation and delivery monitoring must be approved before activation. Audit entries record actor/reference/action/time without employee descriptions, answers, email addresses or provider exceptions. Access-controlled durable log collection remains an infrastructure requirement.
