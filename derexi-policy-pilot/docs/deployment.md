# DeRexi deployment preparation

Prepared November 11, 2026. **Instructions only: nothing in this runbook was applied.** This release candidate has verified development workflows and pending production gates. Do not infer production readiness, live UAT or infrastructure verification from local results.

November 12 supplement: [support/routing architecture](../../semester_5/DeRexi_Week%2011/final-integration-architecture.md), [current results](../../semester_5/DeRexi_Week%2011/final-integration-results.md), and [ordered approval/recovery checklist](../../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md). Remote production DB connections now require `verify-full`; actual TLS and provider controls still need evidence. The approval-only support migration ends in ROLLBACK and was not applied. SMTP and optional incident AI remain OFF by default.

## Evidence and decisions

| Area | VERIFIED DEVELOPMENT | PENDING PRODUCTION |
|---|---|---|
| Workflow | Week 7 Messages, Week 8 lifecycle/intake, Week 10 integrated flows | Actual PostgreSQL schema, locks/concurrency, retrieval and seven live handoffs |
| Identity | JWT/JWKS validation, mocked browser provider, server-side roles and loopback personas | Real Auth accounts/bindings, provider settings and deployed session tests |
| Data boundary | Backend participant/department/Admin restrictions | Direct-client RLS/grants/RPC denial; privileged backend bypasses RLS |
| Documents | Real extraction in isolated checks; native Mac parser/resource evidence | Native Windows/Linux limits; private storage/backup controls; crash-orphan reconciliation |
| Operations | Safe application errors, request IDs, structured stdout security logs | HTTPS/proxy/TLS, internal DB transport, durable logs, backups/restore and operational alerting |

Week 10 recorded 379 PASS / 0 FAIL in isolated checks, including 37 browser UAT checks. Human acceptance is pending. Week 9 historical read-only inventory reported 12 business users, 49 policies/51 versions, zero Auth users and absent Governance tables. It also observed broad authenticated direct reads, 90 grants, six definer helpers and a privileged backend role. These are historical findings, not a new live inventory.

Review these existing artifacts before any activation:

- [Week 8 implementation](../../semester_4/DeRexi_Week%208/README.md) and [document intake](../../semester_4/DeRexi_Week%208/governance-workspace/README.md).
- Canonical [Governance schema proposal](../backend/migrations/2026-11-10_week8_governance.sql): additive working-copy/event tables, constraints, indexes/triggers and RLS. Startup does not execute it. PostgreSQL execution, idempotency and locking remain unverified.
- Canonical [owner-capacity proposal](../backend/migrations/2026-11-10_week8_owner_seed.sql): eight fictional business profiles for historical department coverage. Review identities/collisions and minimum two Owners per department. It creates no Auth users and must not be run merely to enable sign-in. Do not assume the historical expected total of 20 still applies.
- [Week 9 activation instructions](../../semester_5/DeRexi_Week%209/production-activation.md) and [approval-only BFF access proposal](../../semester_5/DeRexi_Week%209/proposed-database/APPROVAL_ONLY_bff_access_boundary.sql). The latter ends in **ROLLBACK** and removes broad direct business-table/RPC access for a BFF-only architecture. It is not applied and is not a generic policy for future direct-client integrations. Do not replace ROLLBACK with COMMIT without separate review/authorization. Preserve platform-managed helpers.
- [Week 10 checklist](../../semester_5/DeRexi_Week%2010/final-mvp-checklist.md) and [acceptance records](../../semester_5/DeRexi_Week%2010/uat-records.md). Earlier Pulse host/feedback defects were fixed in Week 10; do not carry those historical failures forward as unresolved.

## Dependencies and configuration

Install only the reviewed [runtime dependencies](../requirements.txt): FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic, python-dotenv, openai, PyJWT with crypto support, pypdf and defusedxml. [Development dependencies](../requirements-dev.txt) are for existing checks. The frontend is served static HTML/CSS/JavaScript; there is no Node build. Python 3.10+ is the documented baseline; validate the selected host/interpreter and native parser constraints. Version ranges are not a lock: capture the exact approved environment and reproducible artifact before activation.

Require an approved Supabase/PostgreSQL schema with `pg_trgm`; outbound HTTPS for provider JWKS/Auth, optional AI and Pulse publishers; a private writable document directory only if originals are retained; and a monitored application host behind trusted HTTPS termination. GitHub Pages hosts the portfolio, **not this Python backend**.

Configuration names only:

| Purpose | Names |
|---|---|
| Database | `DATABASE_URL`, `PGSSLROOTCERT` |
| Environment/personas | `DEREXI_ENV`, `DEREXI_DEV_AUTH`, `DEREXI_DEV_USER_IDS`, `DEREXI_DEV_AUTH_SECRET` |
| Supabase JWT | `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISS`, `SUPABASE_JWT_AUD`, `SUPABASE_JWT_ALGS`, `SUPABASE_JWT_LEEWAY`, `SUPABASE_JWKS_TIMEOUT` |
| Browser sessions | `SUPABASE_PUBLISHABLE_KEY`, legacy fallback `SUPABASE_ANON_KEY`, `DEREXI_PUBLIC_ORIGIN`, `DEREXI_AUTH_SUBJECT_MAP` |
| Optional AI | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` |
| Optional originals | `DEREXI_DOCUMENT_STORAGE_DIR` |

Keep real values in an ignored environment file or host secret/config store. Never embed connection strings, private mappings, keys or cookies in JavaScript, screenshots or coursework. A publishable key is not a service-role key. The exact public origin must agree with HTTPS requests. Approved immutable Auth subjects map to existing business IDs, verified emails must agree, and role/department come from the database. Unknown bindings fail closed. Optional JWT overrides normally derive from the Supabase project; keep asymmetric production verification.

## Ordered activation plan — not executed

1. **Record authorization and freeze a candidate.** Name release/operator/security approvers, maintenance window, rollback owner, acceptance criteria and approved writes. Inventory source revision, exact package versions, current schema, business identities/owners, Auth settings, grants, helper definitions, storage and running host configuration. Do not print private values. Preserve a known-good artifact.
2. **Prepare recovery first.** Take authorized consistent backups of database data/schema/roles/grants plus retained originals and required configuration references. Encrypt and restrict backups, define retention/RPO/RTO, and test restore into isolated staging. Database backup alone does not include local originals or provider Auth/configuration. Record private recovery evidence and exact restore steps. No restore verification is claimed here.
3. **Validate schema in staging.** Review and, only with separate authorization, apply the existing additive Governance proposal to a representative staging database. Verify compatibility, constraints, audit events, RLS, indexes, triggers, transaction behavior and repeated-run behavior. Validate actual PostgreSQL concurrent revision/publication and `pg_trgm` ranking. Do not drop/recreate published content.
4. **Resolve owner capacity explicitly.** Inventory eligible same-department peers. Review the proposed fictional seed against current identities and collisions; use real institution-approved provisioning for production rather than assuming coursework users are suitable. Any approved staging seed must preserve old IDs/roles/ownership and prove a second run adds nothing. No new account or seed is authorized by this document.
5. **Close direct-client exposure before onboarding.** Capture exact table grants, function signatures/ACLs/owners and RLS policies as described in Week 9. Review the BFF-only proposal in an approved rollback trial, confirm backend still works and anonymous/authenticated direct business reads/writes/RPCs are denied. Do not infer denial from RLS-enabled flags or backend tests alone. Live grant changes require separate approval.
6. **Prepare identity with separate approval.** Review signup/invitation policy; provision only authorized real Auth identities, bind immutable subjects to existing business IDs, and verify email agreement. Configure real provider sessions, public HTTPS origin and JWKS. Never reuse fixture provider credentials or enable public personas. Validate account-disable/expiry behavior; logout does not instantly revoke every previously issued JWT.
7. **Prepare infrastructure.** Enforce development-auth disabled and production mode. Configure HTTPS, trusted certificate/hostname and only the actual proxy's forwarded headers. Require database CA/hostname verification (`verify-full`) and provider CA trust. Client-to-pooler TLS was observed previously, but pooler-to-Postgres `ssl=false` requires provider investigation; do not claim end-to-end transport verification. Verify encrypted storage/backups, private document permissions, restore, monitoring, secret rotation and log retention. Native Windows/Linux parser limits remain a gate on those hosts.
8. **Start a supervised candidate.** Use the reviewed environment and a service manager, with no reload. From `derexi-policy-pilot/`, the following process command applies **only if** the reviewed HTTPS-terminating proxy connects from exactly IPv4 loopback and strips/replaces client-supplied forwarded headers. Certificate, origin, proxy and service policies must be configured and verified separately:

   ```text
   python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1
   ```

   This command alone does not establish HTTPS: production protected routes reject requests without the correct HTTPS scheme. For another proxy topology, review its actual peer addresses and trust only those addresses; never use wildcard trust. Direct TLS requires a separately reviewed certificate configuration. Do not expose this backend listener publicly. In-memory previews require one worker or validated affinity; the built-in login limiter is per process, so multi-instance deployment requires a validated shared strategy. Original retention needs private storage outside `backend/static` and `docs`; reconcile files after process crashes.
9. **Validate before traffic/publication.** Perform the checks below using approved credentials and staging writes. Halt at any failed gate. After separate approval, repeat required live checks without recording secrets. Obtain security/operator and stakeholder acceptance before production traffic. Real live UAT has not occurred.
10. **Monitor the controlled release.** Record artifact/config version, operator, time and acceptance evidence; monitor latency, 5xx, sign-in failures, access denials, feed freshness, DB pool health, parser failures and disk capacity. Route alerts to named operators and review access periodically.

## Validation plan and health checks

Read-only local commands after an authorized local startup (these commands were not used against the live database in Week 11):

```bash
# macOS
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/api/pulse/health
```

```powershell
# Windows PowerShell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/pulse/health
```

`/health` executes a database reachability query and expects status `ok` / database `reachable`. It does not check all tables, Auth, grants, backups or infrastructure. `/api/pulse/health` reports module/source/cache settings, not proof that each external source is currently reachable; inspect source statuses on the feed too. The UI loading or OpenAPI responding is not release acceptance.

Required staged/live validation, with safe evidence and separately approved writes:

- Employee, Owner and Admin real HTTPS login; `/me` agrees with business identity; unknown/mismatched bindings deny access. Refresh/logout, expiry, wrong password, CSRF and Secure/HttpOnly/Strict cookie **attributes only**; signed-out protected requests deny access.
- Direct anonymous/authenticated Data API/RPC denial alongside working backend access; cross-user messages, cross-department drafts, self-peer/final approval and non-Admin incident modifications denied.
- Seven Week 10 handoffs: Assistant→clarification Messages; answer feedback→saved Dashboard aggregate; document intake→draft; draft→independent peer→independent Admin publication; revision→Library baseline isolation; Pulse→source-linked revision; employee report→Admin triage. Confirm navigation/notifications and error/retry behavior.
- Actual PostgreSQL retrieval/version resolution/concurrent publication; original download authorization and configured native parser bounds; backup restoration; deployed TLS/certificates/internal DB transport; durable audit/security logs; physical/mobile and human stakeholder acceptance as required.

## Logging and operations

Application security events are redacted JSON with request IDs, safe error responses and templated Uvicorn paths. Collect stdout into access-controlled durable storage, define retention/rotation and alert ownership, and confirm log delivery without recording tokens/passwords/full sensitive payloads. Governance history is application audit evidence, not a substitute for durable host/security logs. Restrict `/docs` and operational diagnostics according to the institution's reviewed exposure policy. Rate limiting is per process. Investigate repeated 401/403/5xx without weakening RBAC.

## Ordered rollback — prepare and authorize before activation

1. Declare rollback on failed identity/access boundaries, data integrity, publication or required operational checks. Halt traffic/publication and restrict the candidate; preserve logs and the incident timeline.
2. Restore the last reviewed application artifact and compatible configuration under the service manager. Keep developer auth disabled. Do not print secret values or restore a vulnerable public access boundary merely to make old code run.
3. Prefer keeping additive Governance schema when compatible. Do not drop audit/draft tables or delete newly approved users/history. Assess writes since the checkpoint; no blind destructive down-migration is supplied. A pre-commit SQL trial uses its existing ROLLBACK; committed changes require a separately reviewed recovery plan.
4. Restore grants/functions only from the exact captured pre-change ACLs and definitions, with security review. Never use blanket grants. Restore Auth bindings/configuration through the approved process; preserve business identities. Revoke/rotate compromised credentials if applicable.
5. Restore database/private originals only when needed and authorized, from the tested consistent backup set. Reconcile post-backup writes and document hashes privately. Sequence increments are not undone by transaction rollback; do not assume inserts leave no trace.
6. Recheck health, real HTTPS identity, direct-client denials, Library version/history and Admin boundaries before reopening traffic. Record lost/reconciled writes, recovery evidence and stakeholder decision. Failed production gates remain pending; rollback is not release acceptance.

## Documentation scope

No migrations, seeds, grant/RLS changes, Auth users, deployments or live database checks were performed for Week 11. No full regression run was repeated. [Week 11 checklist and evidence](../../semester_5/DeRexi_Week%2011/README.md) records lightweight documentation verification and the prepared demonstration.
