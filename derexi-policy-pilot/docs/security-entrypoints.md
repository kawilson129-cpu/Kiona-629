# Security entry points and developer demonstrations

**Documentation checkpoint:** the recovery implementation is tested locally but
uncommitted. The course-source option, session recovery, Messages additions and
new recovery test runners below require the pending code changes. Publishing
this documentation/evidence does not publish or deploy that implementation.

The existing `uvicorn main:app` is a **legacy compatibility entry point with no
integrated authentication**. It remains available to avoid locking out the
existing course UI. Keep it loopback-only; it is not the production entry point.

## Secured API

From `derexi-policy-pilot/backend`, with the project's `.venv` activated:

```bash
uvicorn main:authenticated_application --factory --host 127.0.0.1 --port 8000
```

Configure `SUPABASE_URL`, the existing secure `DATABASE_URL`, and
`DEREXI_SUBJECT_MAP` (path to a deployment-controlled JSON object mapping verified
Supabase `sub` UUID strings to existing business-user integer IDs). Do not put
credentials or real mapping files into Git. No Auth users or mappings are created
automatically. Missing/empty mappings fail startup rather than falling back.

The factory uses the existing ES256 verifier, requires the configured project's
issuer/JWKS, and declares HTTP Bearer authentication. It exposes no developer
switch routes, accepts no developer cookie/header identity, and disables public
docs/OpenAPI. The server can generate its contract with `app.openapi()` for
authorized tooling. Current business role/ownership relationships are read on
each request. The privileged database connection does not replace API RBAC.

The production UI login flow and real Supabase account provisioning are not part
of this activation. An empty Auth project cannot supply production credentials;
do not switch the normal course UI to this profile until sign-in is provisioned.

## Isolated developer selector

For the working course UI, the explicit authenticated developer profile is
`dev_demo:build_demo`; it shares the secured API/RBAC assembly below the cookie
adapter. The API-only factory is not a replacement UI login flow. See
[HTTP 401 recovery](mvp-401-recovery.md) for current evidence and limitations.

```bash
python dev_demo.py --database /absolute/path/to/approved-local.sqlite --activate --port 8000
```

This command is disabled unless explicitly launched with `--activate`. It binds
only `127.0.0.1`, ignores forwarded identity/address headers, verifies the Host
and browser Origin, and uses a read-only SQLite backup into a disposable private
runtime directory. It never creates/seeds business users, loads production .env,
connects to Supabase, or sends questions to a live AI provider. A URL/connection
string is not accepted in place of an existing local database file.

Open the local `/ui/` path. The server prints only the path of a protected,
five-minute, one-use activation-key file. Read that file locally and enter the
key on the activation screen. The key is not printed, hardcoded or stored in
Git/localStorage. Restart the process for a new activation after logout/expiry.

The original employee selector remains. In this profile it rotates an opaque
HttpOnly/SameSite=Strict cookie; the signed identity stays server-side. Writes/switching
require CSRF and exact Origin checks. A fresh process key/issuer and local-only
audience prevent acceptance by the production verifier. Reloading after a switch
clears prior employee requests and private UI state. Neither switching nor demo
writes modify the source snapshot, employee assignments, or policy ownership.

**Data dependency:** provide an approved SQLite snapshot matching the existing
14-table model with the original IDs, names, departments, roles and policy
ownership. Integer primary keys must support SQLite autoincrement for write
demos. No authoritative snapshot is available in this checkout. Historical
preview data is not imported as a substitute. Synthetic records used by tests
and screenshots are visibly labeled and are not replacements for the employees.

### Explicit read-only course source

Where the original `backend/.env`/`DATABASE_URL` is available, launch from backend/:

```bash
../.venv/bin/python dev_demo.py --course-database --activate --port 8000
```

This **explicit option** loads the existing database configuration and reads its
mapped application tables inside a PostgreSQL `REPEATABLE READ`, verified
`READ ONLY` transaction. The source receives SELECT/transaction commands only.
An owner-only temporary SQLite file preserves mapped rows, IDs and relationships;
per-table count/hash comparison and foreign-key checks must pass before launch.
Aware timestamps are normalized to the same UTC instant for SQLite. It does not
copy Supabase Auth, RLS, grants or unmapped extra tables/columns, nor change them.
It creates no replacement users. Missing configuration/access/schema or failed
verification stops startup rather than falling back to fixtures.

All UI writes occur only in the disposable local copy; they are not synchronized
back to the course database and disappear at shutdown. The existing local-file
`--database` mode still avoids .env/Supabase entirely. Neither option is a public
deployment or production authentication exception. Never put snapshots, mapping
files, tokens or activation keys into Git.

Use `/ui/`; `/ui/index.html` redirects to that canonical route so the session
bridge always loads. The browser waits for `/__dev/session`, includes same-origin
cookies and CSRF on writes, and rotates the signed server identity before reloading
on a persona switch. Expired pages return to activation. Authenticated responses
identify this profile with `X-DeRexi-Profile: developer-local-copy`; the production
API identifies `secured-api`. Authentication still rejects missing credentials.

`GET /messages` is now implemented **only in the secured/developer assembly**.
It derives the requester from the verified identity, rejects a different query
`user_id`, and lists only requester/assignee threads. Administrator privilege does
not override private clarification participation.

SQLite has no `pg_trgm`; only the local profile uses a documented lexical search
adapter over copied approved policies. Production ranking/thresholds are
unchanged. This validates demo workflows, not equivalence to PostgreSQL search.

## Reproduce verification without course data

Run the synthetic server from backend/ in one terminal:

```bash
../.venv/bin/python tests/browser_fixture_server.py /tmp/derexi-browser-metadata.json
```

In another terminal, with Playwright and Chromium available:

```bash
node tests/test_mvp_recovery_browser.cjs /tmp/derexi-browser-metadata.json /tmp/derexi-browser-evidence
../.venv/bin/python tests/run_mvp_recovery_verification.py
```

Use a new output directory for each browser run. Each server activation is
one-use: restart the fixture server before a new browser run. The regression
runner saves fresh JSON/logs with source hashes and never overwrites original
assessment evidence. The original nine incident tests now pass; their earlier
guidance failures remain recorded in historical evidence.
The original Assignment 3 browser script retains its historical missing-Messages
expectation and is not the current recovery acceptance runner. Original evidence
remains unchanged. The original audit runner refuses to reuse browser proof older than one hour. Its C-02
26 and C-03 54 backend assertions remain unchanged; C-01's old unsigned-header
role comparison now uses signed identities on an administrator action and the
schema assertion checks the real contract without requiring public exposure.

Live government feeds still require the pending official-host network allowlist
to be applied through environment settings; no proxy/TLS verification bypass is
implemented. Refer to the final Assignment 3 report for exact verification scopes.
