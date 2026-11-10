# DeRexi Week 9 — Security and user authentication

**Result: application controls implemented and tested in isolation; production activation is BLOCKED.**
No live Auth accounts, migrations, database records, approvals, RLS rules or grants
were changed. Runtime source remains in `derexi-policy-pilot`. Existing coursework
changes and prior evidence were preserved. No dependencies installed, commit or push.

## Existing controls reused

| Requirement | Finding before this work | Final verification |
|---|---|---|
| JWT/JWKS signature, issuer, audience and expiry | VERIFIED in existing isolated suite | Reused; unsafe endpoint/algorithm configuration also rejected |
| Messaging role/record authorization | VERIFIED in existing isolated suites | 73 workflow + 29 edge checks pass |
| Governance department boundaries, independent approvals, history | VERIFIED in isolated Week 8 lifecycle | 102 checks pass; live tables remain absent |
| Real sign-in/logout and business-user binding | MISSING browser integration; email-only bridge PARTIAL | Cookie-based flow and immutable subject bindings tested with mocked provider; live activation BLOCKED |
| Sensitive API protection | PARTIAL: anonymous published-policy/reference reads, broad incident/dashboard access | Every sensitive route denies anonymous access; role/department/record restrictions tested |
| Security-event logs | MISSING structured cross-application telemetry | Sanitized JSON events tested; durable production collection remains PARTIAL |
| Data transport and RLS | PARTIAL | Live TLS/RLS metadata reviewed; infrastructure/direct-client gaps below remain |

## Focused changes

- Added Supabase password login, refresh and local-session logout through the backend.
  Production cookies are HttpOnly, Secure, SameSite Strict, with host-only scope;
  refresh cookies are limited to `/auth`. Tokens never enter production JavaScript
  storage or login JSON. Same-origin/custom-header checks protect cookie writes.
- A verified Supabase subject must be explicitly bound to an existing business-user
  ID in server configuration, and its verified email must match that record. Roles
  and departments are reloaded from the database; signup/account creation is absent.
- Protected policy/library/reference reads. Legacy policy/version writes remain
  blocked in favor of the existing independently reviewed Governance lifecycle.
- System Administrators retain oversight and incident management. Other users see
  their own or explicitly assigned incidents; Policy Owners receive departmental
  policy-health data and authorized request/incident aggregates. Existing message
  participant rules and Governance department/self-approval checks remain in force.
- Added bounded login throttling, no-store responses, production HTTPS rejection,
  HSTS on production HTTPS, safe validation/500 errors, generated request IDs, and
  structured login/denial/change/approval/admin events. Credentials, tokens, query
  strings and private bodies are excluded; Uvicorn access paths are templated too.
- Development authentication now requires an explicit development/test environment
  and opt-in, direct loopback/Host/origin checks, and a valid optional allowlist.
  The real ignored `.env` was untouched; developer code/tool access is independent.
- Connected real admin incident assignment/escalation controls, fixed unassigned
  handler rendering, retained the selected incident view after changes, and cleared
  private client state on logout. Existing visual design was retained.

## Executed results

| Suite | PASS | FAIL | BLOCKED | Evidence |
|---|---:|---:|---:|---|
| Week 9 API/auth/logging/TLS configuration | 110 | 0 | 0 | `evidence/week9-security-results.json` |
| Existing JWT foundation | 24 | 0 | 0 | `evidence/test_week7_auth.txt` |
| Existing messaging workflow | 73 | 0 | 0 | `evidence/test_week7_messaging.txt` |
| Existing messaging security edges | 29 | 0 | 0 | `evidence/test_week7_edges.txt` |
| Existing governance lifecycle | 102 | 0 | 0 | `evidence/lifecycle-results.json` |
| Browser sign-in/logout, roles, cookie privacy, admin action, mobile | 15 | 0 | 0 | `evidence/browser-results.json` |
| Parser after portability fix | 47 | 0 | 0 | `evidence/parser-fix-results.json` |
| Parser resource protections | 14 | 0 | 0 | `evidence/parser-limit-results.json` |
| **Latest results per suite** | **414** | **0** | **0** | `evidence/regression-summary.json` |

**Parser portability fix: 47 PASS / 0 FAIL / 0 BLOCKED.**
`backend/document_limits.py` now clamps POSIX limits to existing soft/hard ceilings.
Linux retains its address-space limit; Windows retains its Job Object. On macOS,
a separate supervisor samples resident memory/physical footprint every 10 ms,
killing extraction above 256 MiB (or a stricter inherited ceiling), on probe failure,
or after 10 seconds. The existing 8-second CPU and outer 12-second extraction limits
remain, together with input, XML and archive protections. Sampling permits transient
overshoot between polls; this is not a kernel allocation ceiling.

Mac `.venv` has `pypdf 6.21.4` and `defusedxml 0.7.1`. Native parser and resource
checks pass (47 + 14). Essential Week 9 security and JWT suites were rerun: 110 + 24
PASS, 0 FAIL/BLOCKED. Other 219 prior passing checks were reused, not rerun.
Native Windows/Linux execution remains unverified; unsupported protections fail
closed. Results: `evidence/parser-fix-results.json`, `evidence/parser-limit-results.json`,
`evidence/parser-fix-regressions/summary.json`. Earlier failures and diagnosis are
preserved. See [focused fix and reproduction](parser-portability-fix.md).
An interim
staging test expected a plaintext identity endpoint rather than testing HTTPS;
the expectation was updated and the suite re-passed. Browser testing found and
repaired incident navigation returning to Overview after assignment. Initial
Week 9 run output is retained separately from the final 110-check log.

All write scenarios used ephemeral SQLite, a PostgreSQL tripwire, synthetic JWT
keys/JWKS and mocked Supabase password/refresh/logout responses. Browser evidence
uses HTTP **only in the explicit test environment**, not a production TLS claim.
Live checks were SELECT-only with `transaction_read_only=on`.

## Live findings and production blockers

The read-only inventory observed **12 business users, 49 policies, 51 versions,
zero Auth users, and absent governance tables**. Fifteen existing public tables
have RLS enabled, but the backend role has `rolbypassrls=true`. Eight policies
permit unconditional authenticated SELECT, including users and incident reports;
90 direct-client grants were inventoried. App RBAC does not protect direct Data
API access. Review the approval-only BFF access-boundary proposal before onboarding.

Client-to-pooler encryption was observed as **TLS 1.3 / TLS_AES_256_GCM_SHA384 /
256 bits**. The PostgreSQL backend reports `ssl=false`; internal-hop protection is
unverified. `sslmode=require` does not establish hostname verification. Production
HTTPS, provider disk/backup encryption, private-original storage encryption,
public-signup restrictions, durable log retention/alerts, and direct-client role
tests remain unverified. Message/field/end-to-end encryption is not implemented.
See [PostgreSQL TLS modes](https://www.postgresql.org/docs/current/libpq-ssl.html)
and [Supabase RLS bypass rules](https://supabase.com/docs/guides/database/postgres/row-level-security).

The real provider URL/public key/subject map/HTTPS-origin setup is incomplete.
There has been **no real password login, refresh or logout**. Approval steps and
existing migration copies are in [production activation](production-activation.md).
JWTs can remain valid until expiry after provider logout; immediate access-token
revocation/session introspection is not implemented. The UI reports provider
revocation failures honestly. [Supabase sign-out semantics](https://supabase.com/docs/reference/javascript/auth-signout).

## Evidence and screenshots

`evidence/live-readonly-security.json` contains current metadata; no live message
bodies, employee emails or credentials were saved. `security-events-sanitized.json`
contains synthetic test events, not production incident/audit records. Exact runtime
file changes are listed in `evidence/files-changed.txt`.

Five captures are saved under `evidence/screenshots/`, visibly labelled AUTH FIXTURE:

1. `01-signin-fixture.png` — password form; ordinary persona switching unavailable.
2. `02-employee-session-fixture.png` — protected Employee library access.
3. `03-owner-dashboard-fixture.png` — Policy Owner departmental dashboard.
4. `04-admin-incident-fixture.png` — real fixture API assignment by System Administrator.
5. `05-mobile-signin-fixture.png` — responsive logged-out screen with identity/activity cleared.

After separate approval, capture real HTTPS sign-in/logout, verified cookie **attributes
without values**, a rejected cross-department/self-approval action with matching
sanitized audit events, and provider encryption/log-retention settings. These live
screenshots are **not available yet**; do not substitute fixture images as live proof.

Suggested commit: `Complete Week 9 authentication, scoped RBAC and security logging`
