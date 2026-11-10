Policy ownership is separate from role: Dana/Lucy can remain administrators and own policies. Chris remains a Policy Owner; an incident assigned to Chris is accessible through assignment, without inventing a SOC role or granting every Policy Owner global incident access. No department-wide access is implicit. A non-admin assignee cannot reassign/escalate an incident through PATCH to acquire or grant access.

Admin thread oversight and resolve follow the old Week 7 proposal and require review here. A thread participant may see the originating question and replies, not the requester's entire linked conversation. Requesters cannot resolve via the current resolve endpoint unless also assignees; a separate requester-close feature is outside scope.

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

Likely future implementation files (not changed now): backend/main.py, backend/schemas.py, backend/static/app.js, backend/auth.py only as needed for integration, new permission/principal module, separate dev entry point/session module and offline tests. No ORM schema or dependency change is presumed necessary.

## Decisions and blockers

Review this matrix and the isolated local-session design before implementation. Specifically approve or revise admin thread oversight/resolve; Policy Owner access to aggregate governance metrics; assigned-incident triage without a new SOC role; owner self-service draft creation with admin-only initial approval; and the separate local switching workflow.

Remaining blockers: no RBAC design approval yet; earlier alleged RBAC work is not available in this checkout/diff; missing messages route and six existing incident failures; no confirmed authoritative local roster/database for the full demo; production Auth-to-business-user mapping is unprovisioned. Current environment reports no configured secret/runtime-variable bindings. Live Supabase access is unnecessary for design and offline RBAC work and was not attempted.
