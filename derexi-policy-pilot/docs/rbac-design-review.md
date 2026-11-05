# Server-side RBAC design for review

**November 5 update:** the later hardening request authorizes integration and
development-branch commits/pushes. The historical Stage 1 record below is retained.
The explicit secured API/local demo now implement this matrix; see
`security-entrypoints.md` and `compliance/assignment3_security_hardening_final.md`.
The legacy course entry point is not automatically migrated or exposed publicly.

Status: architecture approved with conditions; Stage 1 implemented for review. November 3, 2026.
Authorization is limited to pure permissions, principal resolution, synthetic identities and isolated offline tests. No route enforcement, browser changes, local switcher replacement, live data operation, migration, commit, push or deployment is authorized yet.

## Stage 1 review record

Added `backend/rbac.py`, `backend/principals.py`, and `backend/tests/test_rbac_stage1.py`. These modules are not imported by the application. No changes to main.py, auth.py, models.py, schemas.py, the browser UI, dependencies, environment configuration, database records or existing tests.

From `derexi-policy-pilot/backend`, run `../.venv/bin/python tests/test_rbac_stage1.py` — **40 passed**. Existing JWT foundation runner — **24 passed**. Both ran offline, without DATABASE_URL or application/database imports. Synthetic signed JWTs use fresh local EC keys and a mocked key resolver; no real identity or credential is used. The tests cover unknown/forged identities and roles, mapping failures, ownership/participation, initial publication, metadata-only oversight, incident escalation via status or escalation fields, mismatched actor IDs and linked records.

The incident suite is unchanged: its previously verified 3-pass/6-fail baseline is tracked independently with the missing Messages endpoint in `development-known-issues.md`. It was not rerun for these isolated modules because neither it nor its application dependencies changed.

PrincipalResolver requires an explicitly supplied SupabaseJWTVerifier, a one-to-one subject mapping and a trusted business-user lookup. It verifies first, reloads the server role on each resolution, and never links by email or token-supplied business IDs/roles. Mapping failures/unknown business roles raise PrincipalResolutionError; token failures retain AuthenticationError. There is no HTTP error translation or FastAPI dependency yet. No developer provider, production bypass flag or unsigned-header identity route was introduced.

Permission snapshots are trusted inputs, not request models. The future data adapter must validate target existence and relationships; a permission result for content editing must never authorize changing owner/status. Role names match the existing three exact names; numeric role ordering never grants privilege. Current conversation schema has one employee participant; clarification assignees may view their thread but cannot thereby access the entire originating conversation.

Policy Owners create self-owned drafts and edit only assigned `draft` content/versions. Edits to `in_review`, approved or retired policies are denied to them. Status transitions and ownership changes are separate administrator-only permissions. This conservative interpretation preserves administrator authorization for publication.

Administrative clarification oversight is an explicit metadata projection (thread/requester/assignee/policy IDs and status), without question, reason or reply bodies. It does not authorize reading private content, replying or resolving. Resolution requires actual assignment. Any broader administrative oversight or resolution operation needs a further explicit review.

The present persona switcher remains untouched. The secure local replacement and production principal adapter are future stages, not completed capabilities. Stop after Stage 1 for Kiona's review.

## Evidence and constraints

- Reviewed both staged and unstaged diffs before changes: empty at HEAD `dba7f8f` (`Saved updates to Pulse code files`). No prior RBAC implementation or dedicated RBAC tests were found here.
- Read AGENTS.md, MEMORY.md, the Week 7 messaging/auth proposal and verification plan, auth.py, models.py, schemas.py, current routes, and the UI API calls/persona selector.
- MEMORY.md describes October messaging fixes absent from this checkout. The UI requests `/messages?user_id=...`, but the backend has no `/messages` route. Replies check only whether the supplied sender exists, not thread participation. Do not claim those historical fixes are present or silently replace files from another version.
- auth.py verifies JWTs but is not wired into application routes. User has no ORM `auth_user_id` column. Old migration files remain unapplied proposals; do not execute them.
- Current API trusts caller-supplied `user_id`, `sender_id`, `reporter_id`, and `created_by`. Conversation/thread/incident access lacks effective identity scoping. UI governance visibility (`role_id > 1` or name matching) is not authorization.
- Backend uses a privileged database connection; API enforcement is required. Existing RLS must not be assumed to enforce API permissions. Historical RLS observations have not been rechecked live.
- Preserve every business user, department, assigned role, policy owner, and existing record. No employee/role/department CRUD, seed repair, Auth account creation, migrations, or RLS changes in this task.
- Roles documented by the repository are Employee, Policy Owner, System Administrator. Do not infer extra privilege from numeric ordering, email, job title, or department. Unknown/unmapped roles fail closed.
- Preview mock data and memory disagree on some department assignments and email domains. Neither is authority for changing the roster. Live roster was not queried; no roster reconciliation is proposed.

## Verified environment and test commands

Only project virtual environment found under /workspace:
`/workspace/Kiona-629/derexi-policy-pilot/.venv` (Python 3.12.14).
`pip check` passes. Direct script runners are the documented test commands; the Stage 1 RBAC runner is now documented above.

Run from `/workspace/Kiona-629/derexi-policy-pilot/backend`:

```bash
../.venv/bin/python tests/test_week7_auth.py
DATABASE_URL=postgresql+psycopg2://offline:offline@127.0.0.1:1/offline \
  ../.venv/bin/python tests/test_week8_stage1.py
```

Results rerun November 3: authentication 24 passed/0 failed; incidents 3 passed/6 failed.
The incident runner replaces get_db with fake sessions. The command-scoped unreachable local URL permits import only; it is not a working database or an authentication mechanism. Explicit `+psycopg2` selects the installed driver under SQLAlchemy 2.1.

Incident failures: three missing `incident_guidance` function cases, missing reporter filtering, missing-category rejection, and missing guidance in the successful creation response. These are existing source/test mismatches, not RBAC regressions. No test assertions were changed and no live Supabase connection was made. FastAPI TestClient requires execution outside this machine's restricted sandbox to complete.

## Proposed access matrix

All business routes require authentication. Permissions are checked on the server for every request. A list filter can narrow a caller's allowed rows, never widen them. All roles retain ordinary employee capabilities for their own work.

| Operation / route | Employee | Policy Owner | System Administrator |
| --- | --- | --- | --- |
| Proposed `GET /me` | Self | Self | Self |
| `GET /departments`, `/roles`, `/categories`, `/incident-categories` | Read reference data | Same | Same |
| `GET /users` | Minimal directory: id, name, role, department; no email | Same | Same; no role-edit endpoint |
| `GET /policies`, `/policies/{id}` | Approved policies | Approved + own non-approved policies | All policies |
| `GET /policies/search`, `POST /ask` | Approved corpus; ask as self | Same | Same |
| `POST /policies` | Deny | Create self-owned draft only | Create for a valid existing owner, any supported status |
| `POST /policies/{id}/versions` | Deny | Assigned drafts only | Any policy |
| `GET /conversations/{id}` | Own conversation only | Own conversation only | Own conversation only |
| Proposed `GET /messages`; `GET /clarifications`, `/clarifications/{id}` | Participant only | Participant only | Participant-only private content; separate metadata-only oversight |
| `POST /clarifications` | Create as self; only own linked conversation/message | Same | Same; admin does not impersonate requester |
| `POST /clarifications/{id}/replies` | Participant, open/in_progress only | Same | Same; oversight does not authorize impersonated replies |
| `POST /clarifications/{id}/resolve` | Only if assignee | Only if assignee | Only if assignee |
| `POST /incidents` | Report as self; server sets assignment/escalation defaults | Same | Same; triage changes via PATCH |
| `GET /incidents` | Own reports + assigned incidents | Own reports + assigned incidents | All incidents |
| `PATCH /incidents/{id}` | Assigned incident only; non-escalated status/severity/resolution notes | Same | All supported triage fields on any incident |
| `POST /feedback` | As self, only on assistant message in own conversation | Same | Same |
| `GET /dashboard/policy-health` | Deny | Existing aggregate dashboard, without private message bodies | Same |
| `GET /api/pulse`, `/api/pulse/health` | Read | Read | Read |
| User/role/department mutation, migrations, deletion | No new capability | No new capability | No new capability |

Policy details include version bodies; the same visibility rule must cover them and every citation/linked record. Approved retrieval/ranking stays unchanged. Non-approved access is an object-access rule, not a change to search thresholds.

Policy ownership is separate from role: Dana/Lucy can remain administrators and own policies. Chris remains a Policy Owner; an incident assigned to Chris is accessible through assignment, without inventing a SOC role or granting every Policy Owner global incident access. No department-wide access is implicit. A non-admin assignee cannot reassign/escalate an incident through PATCH to acquire or grant access.

The user's approval conditions supersede the old Week 7 blanket admin thread oversight/resolve proposal. Admin oversight is limited to a separate metadata projection; private content remains participant-only. A thread participant may see the originating question and replies, not the requester's entire linked conversation. Requesters cannot resolve via the current resolve endpoint unless also assignees; a separate requester-close feature is outside scope.

Public surface: static login/UI assets, minimal service root and a minimal liveness response only. The existing database-backed `/health` should be restricted to administrators/operations; public readiness must not disclose database errors. Interactive docs/OpenAPI should be disabled or protected in production. No new public data routes.

## Identity and request authorization

Production path:

1. Verify Bearer JWT with the existing ES256/JWKS verifier, pinned issuer/audience and expiration checks. No fallback on missing/invalid tokens or JWKS failure.
2. Resolve verified `sub` through an explicit, deployment-controlled mapping to an existing business `users.id`. Proposed first increment: a read-only configuration file outside the checkout, avoiding the unapplied `auth_user_id` migration. Require unique subject/user mappings and reject unknown subjects. Never auto-link by email, create employees, or rewrite roles. Provisioning that map and real Auth users is a separate approval, not part of this task.
3. Read that business user's current role and relationships from the server's data source. Never accept a role claim, arbitrary business-user header, localStorage value, or body identity as authority. Missing user/role denies access.
4. Share a single current-principal dependency and permission/object checks across existing and proposed routes. Scope queries before returning rows/counts and validate all foreign-key relationships before writes.
5. During API transition retain existing actor-ID fields only as compatibility assertions: require equality to the principal or reject with 403; derive stored identity from the principal. Do not silently ignore a mismatch. Treat `owner_id`/`assigned_to` as separately authorized targets, not actor identity.
6. Confirm feedback message ownership; clarification message belongs to the permitted conversation/requester; replies use the principal; incident reporters cannot set privileged assignment/escalation values. Fail before any mutation, AI request, or other side effect.
7. Missing/invalid credentials: 401. Authenticated but unmapped/unknown role or forbidden operation: 403. Inaccessible object IDs: 404 to avoid existence disclosure. Infrastructure/JWKS outages may return 503, always deny access. Do not log tokens, credentials, or message bodies.

No production auth switch, `AUTH_DISABLED`, dev header, trusted localhost shortcut, default-admin identity, or test-key acceptance in the production app. Dependency overrides belong only to offline tests.

## Development persona switching without a production bypass

Proposed separate local development entry point, never mounted by the production entry point:

- Preserve the current employee picker and ability to switch among existing fictional employees. A selection changes the local session's principal, never `users.role_id`, departments, ownership, or any live data. Keep the existing roster display, including assigned roles; no replacement of Chris/Alex/etc. with generic test accounts.
- Use an approved local roster/data copy or a dedicated development database containing those unchanged business records. Do not use the preview fixture as an authoritative roster. No automatic production export or seed rewrite. Until a local data source is available, use synthetic records only in offline tests and do not claim full persona-demo readiness.
- Local entry point binds loopback only, requires explicit launch, rejects nonlocal/external database targets, and must not load backend/.env containing live credentials. It must verify the effective DB target before opening any session. No Supabase proxy/remote DB route is permitted from this dev application. Loopback by itself is not authentication.
- On startup generate a short-lived bootstrap credential for the developer through a local channel; never hard-code it or place it in source, URLs, logs, or localStorage. Use a one-time local activation flow to establish an HttpOnly, SameSite=Strict session. Persona-switch POST requires that session, a CSRF token and exact allowed Origin/Host checks; no wildcard CORS. Select only a valid existing local user, reissue/rotate session on switch, and invalidate expired sessions. Secrets remain in memory/local protected storage and never enter Supabase.
- The browser keeps its visual persona selector. After an authorized switch it obtains `/me` and renders the role returned by the server; clear prior employee conversations, messages and cached responses. Ignore/reject forged actor IDs or roles even in development. Unsigned `X-User-ID`/`X-Role` alone never authenticates.
- Production accepts only its Supabase issuer/key path. Local sessions and bootstrap credentials cannot authenticate to production; the production application never imports or registers development session/switch endpoints. No automatic mode detection from Host, missing credentials, debug status, or failed production authentication.
- The same RBAC checks run after identity resolution in both entry points. Development switching changes identity deliberately in the isolated local application; it does not disable authorization checks.

Deployment separation must be tested, not assumed from an environment flag. Developer switching against live Supabase is deliberately excluded by the user's no-live-data-change constraint. If that is essential later, stop for a separate design review rather than introducing a production impersonation route.

## Implementation and acceptance plan after approval

1. Add pure permission rules/current-principal resolution and offline RBAC tests; leave roster/schema/data untouched. Exercise the existing production verifier with mocked JWKS and explicit mapping.
2. Integrate scoped guards and actor matching across every business route, including Pulse, dashboard, linked records, and list/detail endpoints. Add the missing messages read route only after its current contract is confirmed; do not attempt to recover it by overwriting main.py from old notes.
3. Build isolated local development entry point/session switch, then wire the existing UI selector to its authenticated session and `/me`. Production UI must use its authenticated identity; hidden navigation is only presentation.
4. Test every matrix allow/deny pair, unknown roles, missing/forged/expired identities, unlinked subjects, cross-user IDs, unrelated owners, indirect record access, lists/counts, closed threads, incident field escalation, and rejected requests causing zero writes. Use fake sessions/synthetic fixtures or an explicitly approved disposable local database only.
5. Test production has no dev endpoints, rejects dev sessions/headers, and cannot start with a dev auth provider. Test dev refuses Supabase/nonlocal targets, requires session+CSRF, and preserves employees/roles across switches. Rerun auth baseline; report existing incident failures separately. Never weaken tests to get green.
6. No live DB smoke tests, migrations, changes to RLS/auth users, commits, pushes, or deployment in this approval phase.

Future integration files (not changed in Stage 1): backend/main.py, backend/schemas.py, backend/static/app.js, backend/auth.py only as needed, a separate dev entry point/session module and further offline tests. No ORM schema or dependency change is presumed necessary.

## Decisions and blockers

Architecture and Stage 1 are authorized under the user's ten conditions. Stage 1 stops here for review; no later stage is authorized. The local-session design remains the future direction, with the existing switcher preserved until a replacement is working and tested.

No blocker remains for Stage 1. Later stages require review authorization, confirmation of the Messages contract, an authoritative local roster/database for the full demo, and a trusted production business-user adapter and identity mapping. The missing Messages route and six incident failures are separately tracked repository issues, not failed RBAC tests. Live Supabase access is unnecessary for Stage 1 and was not attempted.
