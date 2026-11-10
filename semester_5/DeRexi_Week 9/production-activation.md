# Production activation — requires separate approval

None of the database/provider steps below were executed. Source changes alone
do not establish production readiness. Current counts: 12 users / 49 policies /
51 versions / 0 Auth users. Preserve identities, ownership and approval records.

1. **Review and approve scope.** `proposed-database/` contains unchanged copies of
   the existing Week 8 governance schema and fictional-owner seed. The seed adds
   business users, so it requires explicit approval; it creates no Auth accounts.
   Review table/column compatibility and capture record IDs, ownership, approvals,
   schema and grants before any action. Do not run the seed merely to enable login.
2. **Close direct-client exposure before onboarding.** Current metadata shows broad
   authenticated reads and privileged backend bypass. For this BFF-only application,
   review `APPROVAL_ONLY_bff_access_boundary.sql`: it removes direct business-table
   grants and business identity RPC access for PUBLIC/anon/authenticated, preserves
   backend/owner access, and ends in ROLLBACK for an explicitly approved trial.
   It intentionally disables future direct-client integrations. Do not replace its
   ROLLBACK with COMMIT without approval and a recovery plan. Platform-managed
   `rls_auto_enable()` is excluded. Existing RLS policies are not silently replaced.
3. **Capture exact rollback privileges before an approved trial.** Run these
   read-only queries and retain their outputs privately before changing grants:

   ```sql
   SELECT table_name, grantee, privilege_type, is_grantable
   FROM information_schema.role_table_grants
   WHERE table_schema='public' AND grantee IN ('PUBLIC','anon','authenticated')
   ORDER BY table_name,grantee,privilege_type;

   SELECT p.oid::regprocedure AS signature, p.proowner::regrole AS owner, p.proacl
   FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
   WHERE n.nspname='public' AND p.proname IN
     ('current_app_user_id','current_app_role','can_access_clarification',
      'can_access_conversation','can_access_message');
   ```

   Restore exactly the captured privileges if rollback is required; do not use
   blanket grants. The trial uses transaction rollback. Do not rely on rollback
   to reverse identity-sequence increments from live test inserts.
4. **Approve Auth onboarding separately.** Verify project signup/invitation policy
   in the provider console; public signup status is unverified. Obtain approval
   before creating real Auth users. Bind each approved immutable Auth subject to
   its existing `public.users.id`; verified emails must agree. No user-row update
   or schema migration is required by the new mapping mechanism itself.
5. **Set private deployment configuration** using the host secret/config store:

   ```dotenv
   DEREXI_ENV=production
   DEREXI_DEV_AUTH=0
   SUPABASE_URL=https://YOUR_APPROVED_PROJECT.supabase.co
   SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_PUBLISHABLE_KEY
   DEREXI_PUBLIC_ORIGIN=https://YOUR_APPROVED_HOST
   DEREXI_AUTH_SUBJECT_MAP={"APPROVED_AUTH_UUID":EXISTING_BUSINESS_ID}
   ```

   The map example requires a real integer in place of `EXISTING_BUSINESS_ID`.
   Never supply a service-role/secret key as the publishable key. Never put the
   database URL, secret keys or subject bindings in browser code. Keep `.env`
   ignored. Use the existing environment's declared dependencies; this local
   Mac `.venv` has compatible `pypdf 6.21.4` and `defusedxml 0.7.1`.
   Native Mac parser/resource tests now pass (47 + 14) after the focused
   resource setup fix. Linux address-space and Windows Job Object limits remain;
   validate on their native hosts before deployment. Mac physical-memory monitoring
   samples every 10 ms, allowing transient overshoot between polls. See
   `parser-portability-fix.md` and `evidence/parser-fix-results.json`.
6. **Provision and verify transport/operations.** Terminate HTTPS at a trusted
   host, trust forwarded headers only from the actual reverse proxy, and match
   the configured public origin. Use `sslmode=verify-full` plus the provider CA
   for database hostname verification; confirm a negotiated TLS connection.
   Investigate pooler-to-Postgres `ssl=false` with the provider. Verify encrypted
   storage/backups/private originals, session-expiry policy, centralized rate
   limiting, security-log access/retention and alerts. The built-in limiter is
   bounded and per process; stdout logs are not durable audit storage.
7. **Validate with approved credentials.** Sign in Employee, department Owner and
   System Administrator through HTTPS. Confirm `/me` matches the intended business
   row; wrong/unknown bindings deny access. Check cookie Secure/HttpOnly/Strict
   attributes without recording values; exercise refresh and logout. Existing
   access JWTs can remain valid until expiry; stronger immediate revocation needs
   separately validated session checks. Verify direct Data API/RPC denials and
   application access with anon/approved user credentials. Test cross-department
   drafts, self-approval, independent approval/publication and incident privileges.
   Use isolated/staging fixtures for writes until live-write testing is approved.

Offline reproduction from `derexi-policy-pilot/backend/`:

```text
../.venv/bin/python tests/test_week9_security.py
../.venv/bin/python tests/test_week7_auth.py
../.venv/bin/python tests/test_week7_messaging.py
../.venv/bin/python tests/test_week7_edges.py
```

For lifecycle results, set `DEREXI_TEST_EVIDENCE_DIR` to this Week 9 `evidence`
folder before running `tests/test_week8_governance.py` so old evidence is not
recreated or overwritten. Browser checks use `serve_week9_fixture.py` on loopback
8029, a dedicated Chrome debugging profile on 9230, and `test_week9_browser.mjs`.
Live metadata checks use `verify_week9_readonly.py` (SELECT-only). No automated
runner performs live password login or applies a proposed migration.

Reference: [Supabase password auth](https://supabase.com/docs/guides/auth/passwords),
[session lifecycle](https://supabase.com/docs/guides/auth/sessions),
[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security),
[PostgreSQL TLS](https://www.postgresql.org/docs/current/libpq-ssl.html).
