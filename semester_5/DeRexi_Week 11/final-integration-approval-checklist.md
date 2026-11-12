# Deployment approval and recovery checklist

**Prepared, not executed.** Continue the [existing runbook](../../derexi-policy-pilot/docs/deployment.md), [Week 9 proposal](../DeRexi_Week%209/production-activation.md), [Week 8 lifecycle preparation](../../semester_4/DeRexi_Week%208/README.md) and [Week 10 acceptance gaps](../DeRexi_Week%2010/final-mvp-checklist.md).

## Exact proposed actions, impact, rollback and verification

| Order | Action requiring separate explicit approval | Impact | Recovery / verification |
|---|---|---|---|
| 1 | Capture read-only live schema, identities, exact ACLs/function definitions, provider settings and tested backups | Establishes the actual baseline; historical inventory is not current proof | Retain private exports and test isolated restore before writes. Never expose secrets in coursework. |
| 2 | Trial canonical `backend/migrations/2026-11-10_week8_governance.sql` in staging | Adds Governance tables/constraints and nullable job title; changes specified direct-client writes | Review its transaction/COMMIT before execution. For a rollback trial, use an explicitly reviewed rollback copy. Compare definitions/ACLs; verify publication locks/history and repeat behavior. Do not drop existing data to recover. |
| 3 | Review canonical `backend/migrations/2026-11-10_week8_owner_seed.sql` against actual two-Owner departmental coverage | Adds fictional business users only if approved; never Auth identities | Prefer institution-approved real staffing for production. Verify original IDs/ownership unchanged and second run adds zero. Rollback after commit requires reviewed dependent-record reconciliation; sequence increments may persist. No blanket user deletion. |
| 4 | Trial `backend/migrations/2026-11-12_support_routing.sql` in staging | Adds four support/routing tables, indexes, RLS and content-free append-only audit protection | Script ends ROLLBACK. Check exact schema drift/constraints/ACLs, then obtain separate approval for committed activation. Preserve additive tables/history on application rollback rather than dropping them. |
| 5 | Trial Week 9 `APPROVAL_ONLY_bff_access_boundary.sql` | Removes broad direct business-table/RPC access for the BFF-only design | Preserve its ROLLBACK default. Capture exact before ACLs/definitions; verify anon/authenticated denial plus working backend. Restore only captured privileges with security approval, never blanket grants. |
| 6 | Configure/activate real provider Auth and immutable subject bindings; approve any actual accounts separately | Changes real sign-in access | Snapshot approved bindings/settings, test HTTPS login/refresh/logout/CSRF/cookie attributes and disabled accounts. Revert to reviewed settings or disable traffic, not developer personas. Previously issued access JWTs may survive until expiry. |
| 7 | Provision HTTPS/proxy, CA trust, storage/backups and durable logs | Establishes host/provider operational controls | Verify certificates/hostname, actual DB TLS including internal pooler leg, restore, retention and alert delivery. Application configuration is not encryption evidence. Preserve private originals outside public roots. |
| 8 | Approve exact IT/Security destinations, sender/SMTP endpoint and narrowly scoped routing grants | Establishes institution-owned recipients and permitted routing managers | Validate with outbound OFF first. Review department/channel mappings. Restore prior approved rule/registry/grants if needed; pending reviewed requests invalidate on route changes. Never auto-seed destinations. |
| 9 | Separately authorize one external test email to an approved recipient, then controlled SMTP activation | Causes real external communication; not authorized by this sprint | Record a test reference and verify receiver acknowledgement/ticket behavior separately. Default OFF until approval. Disable outbound immediately on failure; reconcile sending/unknown states before retrying. SMTP acceptance alone is insufficient. |
| 10 | Approve staging/live workflow writes and production deployment | Makes application externally operational | Freeze reviewed artifact/exact packages/config, retain last good artifact, execute seven prior handoffs plus new confirmation/routing/retry controls, verify PostgreSQL concurrency and human acceptance. Stop/restrict traffic and restore compatible artifact on failure. Preserve new records/audit and reconcile post-checkpoint writes. |

## Before/after validation set

- [ ] Read-only two-Owner coverage query returns every department with at least two actual eligible Owners; do not equate fixture coverage with live coverage.
- [ ] Governance/support schema definitions and indexes/constraints/triggers match the reviewed proposals; actual PostgreSQL concurrent confirms/dispatches/publications tested in staging.
- [ ] Direct-client table/sequence/RPC grants and RLS allow only the reviewed BFF boundary; backend authorization still works. RLS enabled alone is insufficient.
- [ ] Auth subject/email/business ID/role/department agree; wrong mappings/forged IDs fail; cookies Secure/HttpOnly/Strict; CSRF and signed-out access denied; developer endpoints absent in production.
- [ ] Production remote database configuration requires `verify-full`; CA availability, actual TLS handshake and internal provider transport independently verified. Native Windows document checks are evidence for Windows only.
- [ ] Outbound OFF makes no SMTP connection. Approved mock success/failure/retry/dedup pass; no arbitrary recipient or delegate privilege escalation. Unknown sends require human reconciliation.
- [ ] Approved live recipient acknowledges receipt; any existing ticket creation is independently checked and never inferred from SMTP acceptance.
- [ ] Private support/original storage, encrypted backups, isolated restoration, content retention and durable sanitized audit/security logs validated with named operational owners.
- [ ] Stakeholder UAT, required physical-device/cross-browser checks and Week 12 rehearsal signed off. Unavailable native Mac/Linux checks remain pending rather than marked passed.

No action above has been applied to live systems. This checklist presents the concrete review scope; it is not authorization to execute it.
