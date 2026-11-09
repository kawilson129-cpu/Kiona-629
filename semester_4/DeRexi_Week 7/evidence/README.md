# Week 7 messaging verification — November 9, 2026

Reused every existing messaging endpoint. No database, schema, RLS, Auth-user,
seed, dependency, commit, or push changes. Source checkpoint (verified archive):
`/private/tmp/derexi-week7-20261109T182239Z/source.tar.gz`; baseline HEAD `5c31a93`.
Temporary checkpoints may be cleared by the OS.

| Verification | Final result | Evidence |
|---|---|---|
| Existing messaging workflow | 73 PASS / 0 FAIL | [Log](messaging-workflow.txt) |
| Additional authorization/notification cases | 29 PASS / 0 FAIL | [Log](messaging-edges.txt) |
| JWT verification | 24 PASS / 0 FAIL | [Log](jwt-verification.txt) |
| Offline Pulse regressions | 97 PASS / 0 FAIL | [Log](pulse-regression.txt) |
| Chrome workflows and responsive layouts | 26 PASS / 0 FAIL | [Results](browser-results.json) |
| Actual PostgreSQL list + notification queries | PASS for all three roles (6 calls) | [Read-only diagnostics](readonly-diagnostics.json) |

**249 final automated checks passed; zero final failures.** Initial edge testing
reproduced six failures (reply authorization, reassignment alerts, notification
totals, and remote development access); later checks reproduced incorrect sender
attribution and participant roles. All eight are repaired. Browser testing also
found a JavaScript name collision introduced during the UI changes; repaired.
The browser fixture now serializes its single SQLite connection after an interim
fixture process crash. Earlier browser attempts are not passing evidence; the
final JSON is the completed run. A diagnostic failure capture is kept in `attempts/`.

All workflow writes used ephemeral, in-memory SQLite fixtures with PostgreSQL
connections blocked before app import. The original runner's live transactional
writes were replaced because rollback does not protect sequence values. PostgreSQL
syntax is adapted in fixtures; actual list/notification SQL was additionally
checked against Supabase inside an explicitly read-only transaction. Live write
and direct-client RLS tests were intentionally not run. Supabase still contains
12 employees; no employee, department, ownership, or application records were edited.

## Messaging access matrix

| Action | Employee / Policy Owner | System Administrator |
|---|---|---|
| Read thread/history | Requester, current assignee, or previous reply participant | Organisation-wide, single Aurum tenant |
| Reply / resolve / close | Requester or current assignee; appropriate open/resolved state required | Any visible thread, with same state checks |
| Reopen | Own request | Any thread |
| Assign / triage / all-threads folder | Denied | Allowed |
| Governance clarification list | Employee denied; Policy Owner scoped to authorized threads | Organisation-wide |

Missing/invalid credentials return 401; forbidden actions return 403. Hidden
threads return 404 to avoid disclosing their existence. Database roles are loaded
on each request; JWT role labels cannot elevate permissions. Former assignees who
replied retain read access but cannot reply after reassignment. Local test identities
remain convenient, require verified sessions, and are restricted to direct loopback
connections in explicitly enabled development/test environments. Production rejects
them; cross-origin and forwarded development requests are rejected. Developer file
and tool access remains independent of application roles.

## Actual encryption verdict

- **Verified:** client-to-Supabase-pooler TLS 1.3, `TLS_AES_256_GCM_SHA384`, 256 bits,
  observed through psycopg2's negotiated connection information.
- **Observed gap:** `pg_stat_ssl` reports `ssl=false` for the PostgreSQL backend
  connection, and it is not a local Unix socket. Internal pooler-to-Postgres
  protection is unverified; no claim of full-path encryption is made.
- **Unverified:** production browser HTTPS, hostname/certificate verification,
  provider disk/backup encryption, production Supabase sign-in, and direct-client RLS.
  The existing production UI still displays a sign-in gate without a connected login flow.
- Local browser tests use HTTP loopback. Message/reply fields are ordinary text;
  no application field encryption or end-to-end encryption is implemented. Signed
  JWT verification supplies authentication/integrity, not message confidentiality.

`sslmode=require` establishes TLS but does not establish hostname validation;
see [PostgreSQL SSL modes](https://www.postgresql.org/docs/current/libpq-ssl.html).
JWT signing and encryption are separate structures in [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519).
Broader policy-write authorization remains a previously identified gap outside this
messaging repair: the policy creation/version routes still lack identity dependencies.
This report does not certify application-wide RBAC or regulatory compliance.

## Reproduce and submit

From `derexi-policy-pilot/backend/`, run the existing Python environment with
`../.venv/bin/python tests/test_week7_messaging.py`, `tests/test_week7_edges.py`,
`tests/test_week7_auth.py`, and `tests/test_pulse.py` (same interpreter for each).
For UI checks, start `../.venv/bin/python tests/serve_week7_fixture.py`, connect
Chrome's local debugging endpoint, then run `node tests/test_week7_browser.mjs`.
`CDP_URL` can select another Chrome JSON-list endpoint. The fixture binds only
`127.0.0.1:8027`, uses illustrative employee records, and never connects to Supabase.
The separate `verify_week7_readonly.py` is explicitly SELECT-only deployment diagnostics.

Submit these exact captures; 01–07 are visibly labelled **LOCAL FIXTURE**, not live data:

1. [Employee's three-panel inbox](screenshots/01-employee-inbox-fixture.png): Sam and My requests.
2. [Owner notification](screenshots/02-owner-notification-fixture.png): Jordan's assignment alert.
3. [Reply and resolution](screenshots/03-owner-resolved-fixture.png): stored owner reply, Resolved state, disabled composer.
4. [Employee reopening](screenshots/04-employee-reopened-fixture.png): reopened request and Awaiting Owner state.
5. [Admin oversight](screenshots/05-admin-oversight-fixture.png): Lucy, All threads, triage and assignment controls.
6. [390px mobile thread](screenshots/06-mobile-thread-fixture.png): folders, readable detail, Back to conversations.
7. [Unauthorized thread](screenshots/07-unauthorized-thread-fixture.png): unrelated Policy Owner denied access.
8. [Actual transport diagnostics](screenshots/08-observed-tls-diagnostics.png): negotiated client TLS and the unverified internal hop together.

Existing design-detector warnings reference the portfolio's root DESIGN.md and
incumbent styles; they are not a clean accessibility certification. Inbox contrast
and focus were improved; physical devices, other browsers, and a full screen-reader
audit remain untested. Original November 3 compliance evidence was not overwritten.
