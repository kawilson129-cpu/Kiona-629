# Week 11 release preparation checklist

## Documentation prepared

- [x] Existing canonical README improved; useful purpose/layout/Pulse material retained and stale setup/features corrected.
- [x] Mac/Windows virtual environment, install/startup, variable names, API access and troubleshooting documented.
- [x] Employee, Policy Owner and System Admin guides cover workflows, permissions, errors and escalation.
- [x] Demo script includes existing fictional users, local-only persona switching, independent review/publication, Pulse and incident → Admin triage.
- [x] Presentation outline links original labelled screenshots without copying/altering prior evidence.
- [x] Deployment runbook reviews outstanding schema/owner, Auth/RLS proposals and live QA gaps; activation/rollback remain instructions only.
- [x] VERIFIED DEVELOPMENT and PENDING PRODUCTION are distinguished throughout.
- [x] Lightweight documentation validation recorded in [evidence](evidence/documentation-validation.md); no extensive regressions repeated.

## Production gates — all pending, not performed here

- [ ] Review/authorize schema activation; validate real PostgreSQL constraints, locks, concurrency and repeated-run behavior.
- [ ] Resolve actual department peer capacity through authorized identity processes; do not automatically run fictional owner seed.
- [ ] Approve real Auth onboarding and immutable subject bindings; validate signup policy, login/refresh/logout, cookies, CSRF and expiry through HTTPS.
- [ ] Resolve direct-client grants/RLS/RPC exposure and prove denials alongside backend access.
- [ ] Verify production HTTPS/certificates/trusted proxy and database internal/external transport.
- [ ] Verify encrypted private storage/backups, isolated restore, retention, orphan reconciliation and operational ownership.
- [ ] Validate intended native parser host, shared/multi-worker strategy and durable access-controlled security logs/alerts.
- [ ] Capture approved artifact/exact dependencies and exercise reviewed rollback.
- [ ] Complete seven live workflow handoffs, PostgreSQL-specific retrieval, required real-device/cross-browser checks and human UAT sign-off.
- [ ] Complete an authorized rehearsal if interactive presentation is desired; prepared script is not evidence of execution.

No live Supabase writes, migrations, Auth users, owner seeding, RLS/grant changes, deployment, automatic commit or push occurred. Production RBAC and loopback persona boundaries remain unchanged.
