# Week 9 verification checklist

- [x] Existing JWT/JWKS, development identity, messaging and governance reused.
- [x] Valid/expired/invalid/wrong-audience/wrong-issuer JWT cases executed.
- [x] Verified subject + email bind to an existing business user; role claims cannot elevate.
- [x] Every sensitive route rejects anonymous requests.
- [x] Employee and direct policy/version bypass attempts denied.
- [x] Owner department boundaries, independent approvals and self-approval denial tested.
- [x] Administrator oversight and incident actions tested.
- [x] Login/refresh/logout, CSRF, cookie attributes and generic errors tested in isolation.
- [x] Structured logs exclude credentials, tokens and private bodies; approvals/admin actors recorded.
- [x] Developer mode fails closed without explicit environment/flag; remote/forwarded/foreign-origin requests denied.
- [x] Existing messaging/governance regressions pass; five labelled browser captures saved.
- [x] Live TLS, bypass-RLS role, policies/grants, row counts and schema readiness read without writes.
- [x] All new coursework evidence saved in this existing Week 9 folder.
- [ ] Real approved Supabase Auth accounts and subject mappings available (currently zero accounts).
- [ ] Existing Governance schema/owner-coverage changes separately approved and applied.
- [ ] Direct-client grants/RLS/RPC exposure remediated and tested with approved credentials.
- [ ] Real HTTPS sign-in/refresh/logout and provider revocation verified.
- [ ] Hostname verification, internal transport, storage/backup encryption and log retention verified.
- [ ] Existing document-parser suite unblocked (`pypdf` absent locally).
- [ ] PostgreSQL locking, migrations/seed idempotency and real provider concurrency verified.

Final executed totals: **353 PASS, 0 FAIL; one parser suite BLOCKED**.
No migration execution, Auth-user creation, live record mutation, commit or push.
