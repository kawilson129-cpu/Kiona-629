# Final integration implementation and verification

November 12, 2026. Continued the canonical existing app and preserved prior uncommitted documentation and all earlier Weeks' evidence. No redesign, added runtime dependency, live mutation, external email or production deployment.

## Implemented

- Assistant event detection versus ordinary policy questions, immediate high-risk reporting guidance and incident-type follow-ups. Optional AI classification reuses existing provider configuration with its own opt-in, OFF by default.
- Structured employee-bound request review/editing, explicit confirmation, limited internal incident reference and durable status. Investigation/resolution belongs to the existing ticketing system.
- Backend approved-destination SMTP adapter, default OFF, implicit TLS verification, compare-and-swap send claims, stable references, capped/cooldown safe retries and no automatic resend of unknown/accepted/pending attempts. Acceptance never claims delivery/ticket creation.
- Technical Routing panel, operator-approved destination choices, department rules, no-email validation, scoped routing-only delegation, admin read-only readiness view and content-free audit. Existing Week 7 bell adds a separate incident triage link/count.
- Production DB configuration requires certificate/hostname verification. Existing Auth/session/RBAC/developer controls and private document protection remain intact.
- Approval-only support migration, current read-only live inventory, [architecture](final-integration-architecture.md), [pinned status](pinned-readiness-status.md), [activation/recovery plan](final-integration-approval-checklist.md) and [Week 12 demo](week12-demo-runbook.md).

## Evidence and reproduction

**Latest executed results: 622 PASS / 0 FAIL / 14 platform-skipped checks.** The skipped checks are POSIX/macOS resource tests unavailable on Windows, not failed Windows tests. Separately, all **134 local documentation links** across 18 Markdown documents passed; JavaScript syntax and `git diff --check` passed. Real production acceptance remains pending and is not counted as an automated pass.

| Suite | Pass | Fail | Platform skipped |
|---|---:|---:|---:|
| Incident/routing/readiness integration | 75 | 0 | 0 |
| Existing Week 10 handoffs | 42 | 0 | 0 |
| Governance lifecycle | 102 | 0 | 0 |
| Real document intake, native Windows | 47 | 0 | 0 |
| Auth/security | 88 | 0 | 0 |
| JWT | 24 | 0 | 0 |
| Pulse offline | 97 | 0 | 0 |
| Messaging | 73 | 0 | 0 |
| Messaging/RBAC edges | 29 | 0 | 0 |
| POSIX/macOS resource suite | 0 | 0 | 14 |
| Native Windows memory/CPU probes | 3 | 0 | 0 |
| SMTP/TLS no-network mocks | 17 | 0 | 0 |
| Desktop/mobile browser workflow | 18 | 0 | 0 |
| Final mobile acceptance-notice visibility | 1 | 0 | 0 |
| Internal-only reporting fallback browser smoke | 6 | 0 | 0 |

Machine-readable latest-per-suite totals: [final-summary.json](evidence/final-integration-20261112/final-summary.json). Initial failures and interrupted browser attempts are retained separately; their checks are not added to the latest totals.

The existing suite pass covers Assistant/clarification/Messages, independent Governance publication, real document parsing, Pulse, persisted feedback/Dashboard, incidents, Auth/JWT/CSRF/roles and developer isolation. Regression uses the existing SQLite SQL adapter/PostgreSQL tripwire, mock provider/feed/SMTP and fictional business users. It is not a Postgres execution-plan/RLS/concurrency or live authentication test.

Windows resource probes use native child processes and the unchanged Job Object memory/CPU limits. Fourteen POSIX/macOS tests are skipped on Windows rather than treated as passed. Browser tests run actual UI/API against a separate disposable fixture at desktop 1440×1000 and mobile emulation 390×844; no physical-phone claim.

From repository root, with the existing environment and a **new** evidence directory to preserve this run:

```powershell
$env:DEREXI_SPRINT_EVIDENCE = Join-Path (Get-Location) 'semester_5/DeRexi_Week 11/evidence/rehearsal-new'
& '.\derexi-policy-pilot\.venv\Scripts\python.exe' derexi-policy-pilot/backend/tests/run_final_sprint_checks.py
& '.\derexi-policy-pilot\.venv\Scripts\python.exe' derexi-policy-pilot/backend/tests/test_native_windows_limits.py
& '.\derexi-policy-pilot\.venv\Scripts\python.exe' derexi-policy-pilot/backend/tests/test_support_transport.py
```

The runner redirects prior suites' evidence into the specified new directory. It does not import old evidence-writing `__main__` entry points. Browser source/reproduction: `backend/tests/serve_support_fixture.py`, `test_support_browser.mjs`, and the targeted read-only `capture_support_mobile.mjs`. A dedicated headless browser debugging port is required; never use a normal personal browser profile. The explicit `readiness_readonly.py --live-readonly` is a separate metadata preflight, never invoked by the test runner.

## Initial findings preserved

The first support run recorded 66 PASS / 1 FAIL: the notification integration assumed the older clarification triage count included incidents. A separate incident count and Dashboard link fixed the gap without changing message unread totals. Two browser attempts stopped on harness issues (global lexical redeclaration and a login wait tied to the previous route); both were corrected with prior evidence retained. A mobile screenshot initially framed the top of the long request rather than its acceptance notice; the targeted reframe now checks actual notice visibility and preserves the first capture.

## Screenshots

All new captures are explicitly labelled isolated demonstrations. They contain fictional records and mock/OFF email only.

| Capture under `evidence/final-integration-20261112/screenshots/` | Purpose |
|---|---|
| `01-reviewed-support-request.png` | Identity/department/destination review and disabled confirmation before consent |
| `02-outbound-disabled.png` | Internal reference and honest no-email state |
| `03-technical-routing-desktop.png` | Approved rules/choices and no-email validation |
| `04-technical-routing-mobile.png` | Responsive routing with no horizontal overflow |
| `05-support-accepted-mobile.png` | Mobile request screen; acceptance detail lies below this capture |
| `06-acceptance-detail-mobile.png` | Reframed visible acceptance warning: no delivery/ticket claim |
| `07-final-acceptance-mobile.png` | Final status wording after confirmation; acceptance notice visible without stale review instructions |
| `08-internal-only-fallback.png` | Explicitly confirmed legacy internal reference; no outbound request/email |

The existing internal reporting form remains accessible under **Record an internal reference without email**, with a review-confirmation checkbox. This keeps reporting available while new routing tables/destinations await approval. The six targeted browser checks verified consent, existing incident API persistence, clear no-email wording and absence of any outbound request. No full regression suite was repeated for this compatibility polish.

Source-level normal product strings contain no SDLC/classroom/fixture labels. Simulation labels are injected only by the isolated evidence harness; fixture department names come from the isolated dataset. Evidence labels do not ship in normal mode. Desktop and mobile screenshots were visually reviewed. Full accessibility, cross-browser and physical-device acceptance remain outside this check.

## Production disposition

**Not production-ready.** Fresh read-only live metadata confirms owner deficits, missing Governance/support schema, zero Auth users and direct-client grant/policy exposure requiring review. Observed backend connection TLS remains unresolved. Provider storage/backups/restore/durable logs, real HTTPS/Auth, PostgreSQL concurrency/ACL checks, seven live workflows and human acceptance still require separate evidence/approval. See [pinned items](pinned-readiness-status.md) for exact scope and [approval gates](final-integration-approval-checklist.md) for actions, impact, recovery and verification. No real email, ticket or production security success is claimed.
