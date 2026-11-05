# DeRexi MVP — HTTP 401 recovery

November 5, 2026. Working branch: `codex/derexi-security-hardening`; starting commit `8cb49bd`.

**Documentation-only checkpoint:** this report and its supporting evidence are
being published at the user's request. Recovery application/test code remains
uncommitted and is not included. New commands/features described here require
those pending code changes; the test results refer to the source hashes in the
evidence, not the committed application. No merge or deployment.

## Finding and confidence

The frontend's `loadAll()` waits for `DeRexiIdentity.ready` when the developer
bridge exists, then requests `/users` and `/roles` together. A `/users` 401 rejects
that startup promise and produces “The register could not be opened.” The
developer bridge supplies same-origin cookie credentials; its HttpOnly cookie
selects a server-held signed identity. Selecting a name in localStorage alone
cannot authenticate a protected request.

The reported server's exact process/command remains **unidentified**: no DeRexi
server was running in this cloud workspace at investigation start, and the launch
command/location was unknown. Its 200 `/policies`, 200 `/roles`, 401 `/users`
pattern does not match the current secured API under identical credentials.
It could reflect a different checkout, partially integrated authentication,
different request credentials or another process serving the UI. Do not claim
that the home instance's precise entry point has been inspected.

| Current source profile | Anonymous behavior / browser contract |
| --- | --- |
| `main:app` | Unguarded legacy compatibility app. Not an authentication repair or recommended launch. |
| `main:authenticated_application --factory` | Bearer-token API; `/users`, `/roles` and `/policies` require valid credentials. Does not serve the developer UI/session bridge. No developer fallback. |
| `dev_demo:build_demo`, launched by `dev_demo.py` | Explicit loopback developer application over a private data copy. UI redirects to activation without a session; protected API requests return 401. Authenticated UI and signed persona switching share the secured RBAC assembly. |

Two concrete gaps were repaired: bookmarked `/ui/index.html` could bypass the
bridge injection on canonical `/ui/`, and stale browser API requests did not
return the user to activation. Neither proves the cause of the unidentified
remote process, but both are verified recovery cases. The missing `/messages`
endpoint was a separate known blocker and is now implemented in secured profiles.

There is no application call to `GET /v1/models`; the AI adapter uses chat
completion requests. Model discovery 404 is unrelated to the directory/startup
401. The recovery browser test verifies that 404 and a subsequent `/users` 200.

## Safe repair and dataset

- UI HTML aliases redirect to `/ui/`, which injects the session bridge before
  startup. The browser waits for the session, sends same-origin cookies, sends
  CSRF on writes and redirects a missing/expired session to activation.
- The existing employee selector rotates the server session before reloading;
  no client-selected ID grants permissions. Anonymous requests still fail,
  employee governance is forbidden and unrelated private records remain hidden.
- `/messages` derives identity from the verified principal. A mismatching query
  `user_id` returns 403; lists/details/replies remain participant-scoped, including
  administrators. Question/policy/reply metadata completes the existing UI's
  contract; no new schema, UI layout or seeded correspondence was introduced.
- Authenticated responses identify `developer-local-copy` or `secured-api` in
  `X-DeRexi-Profile`. Startup prints the explicit developer profile and URL.
- New explicit `--course-database` mode reads the existing configured course
  PostgreSQL inside server-verified `READ ONLY`/`REPEATABLE READ`, then copies
  mapped application tables to private temporary SQLite. Counts, SHA-256 row
  comparisons and foreign keys are checked before launch. IDs, names, role and
  department relations, policies, ownership, messages and incidents are copied
  without seeding replacements. UTC timestamp instants survive SQLite conversion.
- The original `--database` mode continues to use an existing approved SQLite
  file with byte-preserving read-only backup. Missing configuration/schema/access
  fails closed; there is no synthetic-roster fallback.

**Preservation status:** no live course database was connected to or modified in
this task; no Auth users, RLS, grants, migrations, roles, policies or employee
records were changed. No course `.env`, ready database credential or approved
course SQLite snapshot is available here. Actual course-copy verification is
therefore **BLOCKED**. Synthetic tests prove the copying/session contracts, not
the contents or identity count of the unavailable course dataset. Unmapped extra
tables/columns, Supabase Auth and database security settings are not copied.

Demo writes go only to the disposable copy and disappear at shutdown; no sync
back to Supabase occurs. External AI calls remain disabled in this profile;
Policy Assistant uses local retrieval/citations and its existing fallback answer.
Production authentication remains unchanged and rejects local developer keys,
cookies and unsigned headers. This profile must stay on loopback.

## Exact launch commands

Run on the machine containing the repaired working files and original course
`backend/.env` with its existing `DATABASE_URL`. Stop its previous DeRexi server
with Ctrl+C first. Do not overwrite an existing `.env` with the example.

Linux/cloud, from repository root:

```bash
cd derexi-policy-pilot/backend
../.venv/bin/python dev_demo.py --course-database --activate --port 8000
```

Windows PowerShell, from repository root:

```powershell
cd derexi-policy-pilot\backend
..\.venv\Scripts\python.exe dev_demo.py --course-database --activate --port 8000
```

For an already approved SQLite snapshot, replace `--course-database` with
`--database /absolute/path/to/course.sqlite`. Do not use the test fixture server
as the course launcher. The confirmed cloud interpreter is
`/workspace/Kiona-629/derexi-policy-pilot/.venv/bin/python` (Python 3.12.14).

Open **http://127.0.0.1:8000/ui/** on that same machine. Read the activation key
locally from the protected file path printed in the terminal and enter it on the
page. The one-time key expires after five minutes; sessions last one hour.
Restart for a new key after logout/expiry. Use the exact `127.0.0.1` origin;
alternate Host/Origin/proxy URLs are deliberately rejected. No token is stored
in browser localStorage or printed into this report.

The command was checked here and correctly refused missing course configuration
without generating replacement employees. Successful course startup must still
be verified on the machine with the existing database configuration. Production
UI sign-in, Auth provisioning and public deployment are outside this local repair.

## Tests and evidence

| Verification | Outcome | Exact evidence |
| --- | --- | --- |
| Recovery backend tests | 16 PASS, 0 FAIL | `compliance/evidence/mvp_recovery_2026-11-05T214047807199Z/test_mvp_recovery.json` |
| Affected Assignment 5 / incident / secured-demo / validation / C-02 regressions | 17 + 9 + 32 + 28 + 26 PASS, 0 FAIL | Same directory, per-suite JSON/logs and `verification_results.json` with source hashes |
| **Final backend total** | **128 PASS, 0 FAIL** | [Final backend summary](compliance/evidence/mvp_recovery_2026-11-05T214047807199Z/verification_results.json) |
| Actual Chromium UI/HTTP/session checks | **16 PASS, 0 FAIL**, no JavaScript exceptions | [Browser results](compliance/evidence/mvp_browser_2026-11-05T2142Z/browser_results.json); `authenticated-messages.png`, `authenticated-governance.png` |
| Earlier recovery run | 127 PASS, 1 fixture error; corrected | `compliance/evidence/mvp_recovery_2026-11-05T213826449478Z/`; R09 incorrectly called a helper absent on its fixture. Corrected helper invocation; application assertion retained. |
| Actual course dataset / user's original server | BLOCKED | No source configuration/snapshot or identified original process available; not replaced by fixtures. |
| Source/JS/secret/whitespace review | PASS; two environment blockers recorded separately | [Handoff checks and exact file manifest](compliance/evidence/mvp_recovery_2026-11-05T214047807199Z/handoff_checks.json); these do not imply production certification. |

Browser acceptance covers application initialization, authenticated directory,
original selector, Policy Assistant, approved Policy Library, incident submission,
employee/owner replies and resolution, persistence across switches, administrator
dashboard, employee private-record/governance denials, session-cookie attributes,
unrelated model 404 and expired-session activation. The actual browser server
entry point was `tests/browser_fixture_server.py` → `dev_demo.build_demo`, using
explicitly synthetic copied data on `127.0.0.1:8014`; this was not a deployment or
substitution for the existing employees.

Reproduce from backend/ (fresh output directories and server activation each run):

```bash
../.venv/bin/python tests/run_mvp_recovery_verification.py
../.venv/bin/python tests/browser_fixture_server.py /tmp/derexi-recovery-metadata.json
# In another terminal:
node tests/test_mvp_recovery_browser.cjs /tmp/derexi-recovery-metadata.json /tmp/derexi-recovery-browser-evidence
```

Each new evidence directory preserves prior outcomes. The original Assignment 3
browser script remains historical and still expects the former missing Messages
route; use the recovery script for current acceptance. The original Assignments
1–5 reports/audits have not been rewritten to claim newer results.

## Changed files and remaining blockers

| Files | Change |
| --- | --- |
| `backend/dev_demo.py`, `backend/dev_bridge.js` | Explicit course-copy launch, canonical UI, session recovery and profile identification |
| `backend/course_snapshot.py` (new) | Verified read-only source copy; no live mutations or fabricated identities |
| `backend/secure_api.py` | Participant Messages contract, richer authorized thread response, profile response header |
| `backend/static/app.js` | Explain missing/expired authentication instead of raw startup “HTTP 401” |
| `backend/tests/test_mvp_recovery.py`, `run_mvp_recovery_verification.py`, `test_mvp_recovery_browser.cjs` (new) | Isolated backend and real Chromium recovery acceptance/evidence |
| `backend/tests/browser_fixture_server.py` | Exercise verified table-copy path with synthetic fixtures |
| `README.md`, `docs/security-entrypoints.md`, `docs/development-known-issues.md`, this report, repository-root `MEMORY.md` | Correct launch path, issue chronology, scope and handoff |
| `docs/compliance/evidence/mvp_recovery_*`, `mvp_browser_2026-11-05T2142Z` | Per-test logs/results, source hashes and actual browser screenshots |

Remaining blockers: verify course configuration and roster on the user's machine;
identify/stop the original process; launch these repaired files with the intended
developer command and validate the actual employees. Real production sign-in,
PostgreSQL search equivalence, live feed access, deployment/TLS and the previously
documented audit/retention gaps remain separate work. No authentication guard was
removed, `/users` was not made public, and no universal bypass was added.
