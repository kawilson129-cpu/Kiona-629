# Compliance 1 Assignment 3 — security hardening verification

Date: **November 5, 2026**. Application controls are integrated and verified in the explicit secured/test profiles. **The existing course UI has not been switched to production authentication. No deployment or real-database verification is claimed.**

## Environment, branches and preserved evidence

- Python 3.12.14, FastAPI 0.162.0, SQLAlchemy 2.1.6; existing project `.venv`; real headless Chromium/Playwright for browser checks.
- Work continues on `codex/derexi-security-hardening`, preserving Stage 1 checkpoint `4eac30aa0257b90c2098c1deba3a0b8117746c7e`.
- Refreshed/read `origin/main` at `5329718ed9f4292bfd0d0367636e5872b3b78ad3` and the remote development checkpoint. No automatic merge/reset was performed. Main contained the newer Pulse implementation/editorial UI and original audit files; Stage 1 remained authoritative on the development branch.
- The pre-resume working files/diff were archived outside the checkout under `/workspace/checkpoints/derexi-pre-resume-2026-11-05.*`. Previous local validation/source-integrity work was preserved and ported to the newer Pulse implementation.
- Original November 3 assessment evidence remains under `docs/compliance/evidence/`, including `baseline_2026-11-03/`. The former partial hardening report is preserved as `baseline_2026-11-03/assignment3_security_hardening_partial.md`. Original results are not overwritten by the new runners.

## Results and verification levels

| Control or suite | Original baseline | Current result | Verification scope |
| --- | --- | --- | --- |
| C-01 audit | 0/15 | **15/15 PASS** | Explicit secured API assembly and strengthened signed-identity/schema checks |
| C-02 audit | 16/26 | **26/26 PASS** | Original 26 assertions against shared FastAPI handlers/schemas |
| C-03 audit | 54/55 | **55/55 PASS** | 54 backend checks plus a newly executed Chromium hostile-renderer check |
| Stage 1 RBAC | 40 passed | **40 passed** | Pure rules/resolver; source unchanged |
| Existing JWT foundation | 24 passed | **24 passed** | Synthetic local keys and mocked JWKS; source unchanged |
| Secured API/local demo | Not previously integrated | **32 passed** | Real FastAPI handlers, signatures, role/object guards, SQLite writes, local activation/CSRF/switching |
| Validation/workflow regressions | Previously 28 passed | **28 passed** | Disposable relational SQLite with foreign keys |
| Additional integrity regressions | Previously 22 passed | **22 passed** | Host/source/redirect/final-response validation and cache/transport checks |
| Existing Pulse suite | Available on newer main | **97 passed** | Offline normalization, classification, ranking, radar, dedupe and per-source cache |
| Browser workflows | New current execution | **14 PASS, 0 FAIL, 1 BLOCKED** | Real Chromium, signed selector and real local API writes; MSG-001 separately blocked |
| Existing incident suite | Initially 3 passed / 6 failed | **5 passed / 4 known failures** | Category validation and reporter filtering fixed; four pre-existing guidance failures remain |
| Live feeds | Previously blocked | **BLOCKED** | All four configured feeds return proxy-tunnel 403; no bypass attempted |
| Course Supabase / production deployment | Not authorized for changes | **NOT RUN** | No live writes, Auth-user creation, migrations, RLS changes or deployment |

Current machine-readable evidence:

- `docs/compliance/evidence/verification_2026-11-05T170344061112Z/verification_results.json` — suite return codes/counts, commands, logs, source SHA-256 fingerprints and separate known failures.
- `docs/compliance/evidence/browser_resume_2026-11-05_EF61bG/browser_results.json` — current browser outcomes, no runtime exceptions, timestamps; adjacent desktop, mobile and inert-hostile-content screenshots.
- The control-audit JSON path is recorded in the `run_compliance_audits.py.log` alongside the verification summary. It records every scenario, expected/actual values and current browser evidence for C03-55. Earlier failed audit/browser attempts are retained as diagnostic history, not final passing proof.

The final regression runner reports no new regression failures; the original incident runner's four failures remain actual failures, explicitly labeled `KNOWN_FAILURES`, not counted as passes.

## C-01 implementation

`secure_api.py` assembles an explicit authenticated application over the existing handlers, using unchanged `auth.py`, `principals.py` and `rbac.py`. `main:authenticated_application --factory` is its production bootstrap. It requires a nonempty deployment-controlled subject map and the configured Supabase issuer/JWKS; no users or mappings are created automatically.

All protected API routes declare Bearer authentication. JWT signature, algorithm, issuer, audience, expiration and required claims are checked before database lookup. The resolver reloads current server-side business role/department data; it never links by email or trusts role/user claims, localStorage, unsigned headers or body actor IDs. Missing/invalid credentials return 401, insufficient authority 403, and inaccessible private records 404. Database-independent anonymous denial is tested.

Collections are scoped before serialization: employees see approved policies and their own/assigned incidents and threads; owners additionally see their owned non-approved policies; admins retain approved administrative authority. Actor-ID compatibility fields must match the verified principal. Stored author/reporter/requester identities come from that principal. Policy Owners create self-owned drafts and edit assigned drafts only; approval/publication is a separate administrator-authorized status operation. Incident assignees cannot reassign or escalate, including by setting status to `escalated`.

Conversations remain owner-only under the current single-employee conversation schema. Clarification participants alone can read/reply, with open-state checks; assignment is required to resolve. The separate administrative oversight operation returns only IDs/status, never private question/reason/reply bodies. The employee directory excludes email addresses. Governance metrics remain aggregates. Public docs/OpenAPI are disabled; authorized developer tooling can inspect the generated contract without public exposure.

`database.py` now initializes production configuration/session machinery lazily, so importing models for isolated demos never opens/loads a live database configuration. The existing driver is selected explicitly for bare PostgreSQL URLs. `ai.py` reads configuration at call time; local demos override answer generation to avoid external AI calls. Production retrieval/ranking thresholds are unchanged. Governance review-date SQL uses deterministic windowing and a bound cutoff, preserving latest-version semantics and permitting real SQLite integration tests.

### Developer entry point and compatibility

The existing selector is preserved. `dev_demo.py --database /approved/local.sqlite --activate` binds only loopback and starts from a read-only backup into an ephemeral private SQLite copy. It refuses connection strings/missing files, creates no employees, and never connects the switcher to live Supabase. Its per-process EC key, unique local issuer/audience and opaque HttpOnly/SameSite cookie are separate from production. Signed tokens remain server-side; activation is one-use/five-minute and stored only in a protected local runtime file. Exact Host/Origin and CSRF checks protect state changes; switching rotates/revokes the old session and reloads private browser state. Forwarded/unsigned identity headers do not grant authority.

The local profile uses a clearly separated lexical SQLite search adapter because SQLite lacks pg_trgm. It searches copied approved policy data; it is not a production ranking replacement or a claim of semantic equivalence.

**Important:** `main:app` is still the **unguarded compatibility entry point**, not the secured production profile. It was not automatically locked down while the course project has no Auth users and no approved local copy of its employee ecosystem. Keep it loopback-only. Production browser sign-in and migration of the normal UI remain blocked. Synthetic fixtures/screenshots demonstrate the new path, not successful migration of the original 12 employees. No generic users were installed as replacements for them.

## C-02 implementation

The actual schemas/handlers now provide whitespace stripping; required nonblank titles/bodies/version strings; maximum text lengths; strict true/false booleans; positive strict signed-bigint IDs; bounded escalation values; rejected unknown fields/empty patches/null required update values; and explicit foreign-reference validation before mutations.

References cover users, policy/incident categories, owners, authors, policies, assignees, conversations and messages. Clarification links must agree with the requester/conversation. Feedback must target the caller's assistant response. Secured entry-point guards additionally bind that caller to the verified principal. Existing optional references remain optional where supported.

Errors omit raw submitted inputs, SQL, credentials, exception context and traces. Invalid fields return 422, missing references 404, conflicts 409 and unavailable services 503. Unexpected exceptions produce an actionable generic 500 with a retry instruction, never false success. Tests compare persisted counts/state on rejected requests and preserve legitimate Assistant/feedback, policy/version, incident and clarification transactions.

Limits: policy title 200, body 100,000, version 40, summary/feedback comment 2,000, incident description/resolution notes 10,000; existing question/topic/reason 1,000 and reply 2,000 characters. Optional version-title limits are explicitly exposed in field metadata as well as enforced at runtime. Clients must send JSON booleans/integer IDs; coercions and unexpected fields now receive 422. Existing data is not truncated or rewritten.

## C-03 implementation

The authoritative newer main-branch Pulse source registry, editorial UI, ranking, classifications, radar and per-source stale-cache behavior are preserved. The prior local hostname/redirect checks were ported into that implementation, rather than replacing it with the older combined-cache design.

`make_article` now requires the source-specific approved HTTPS host in addition to generic URL safety. Lookalike/suffix domains, unsafe schemes, embedded credentials, controls/backslashes and unexpected ports are rejected. FDIC GovDelivery links are allowed only in the USFDIC bulletin account; other tenants/path traversal are rejected. Registry downloads validate the configured URL, every redirect before following it, and the actual final response URL. Inherited proxy/CA/TLS verification remains enabled.

Article hrefs are validated against their source; redirect verification occurs on URLs the backend actually fetches. No bulk article-HEAD prefetch is added to the authoritative per-source cache architecture. A separately tested destination-check utility is available, but future browser navigation to a publisher is not claimed to have been independently prefetched/verified. Normalization never invents articles for failed/empty feeds; document classifications remain conservative and source-attributed.

A fresh Chromium execution of C03-55 injected hostile `<img>`, `<script>` and `javascript:` metadata at the browser response boundary and verified no injected nodes, unsafe links, dialogs or execution. Backend checks separately verify normalization and host attribution.

Live validation is still blocked by the current environment's proxy 403 policy. The official/GovDelivery host additions saved in the earlier environment draft remain unapplied; review/save those settings and publish the cloud environment configuration before live-feed verification. This is not a public application deployment, and no proxy/TLS bypass is provided.

## Test provenance and changes to legacy checks

The original C-02 26 and C-03 54 backend assertions are unchanged. C03-55's historical browser PASS is no longer accepted as a current execution: the runner requires explicit fresh browser proof, otherwise reports NOT TESTED.

Two C-01 audit assumptions were corrected openly, without adding a bypass or weakening permission checks:

1. C01-14 formerly compared unsigned `X-Demo-Role` headers on `/users`. The approved matrix permits the minimal directory to all authenticated roles, and unsigned headers must never authenticate. The check now uses real locally signed Employee/Admin JWTs and asserts exact 403/200 outcomes on the administrator-only health action. The synthetic server role relationships are populated faithfully; the database tripwire stays active.
2. C01-15 formerly required unauthenticated `/openapi.json`. It now inspects the real generated security contract **and** requires anonymous schema access to be denied/disabled.

The newer Pulse suite had two positive schema/title fixtures using an unrelated example.gov URL. Only those positive fixture URLs changed to the approved FDIC host; assertions remain intact, and hostile-host rejection is independently asserted. Additional cache/transport tests were adapted to the newer registry/per-source response contract; no original negative security assertion was removed. Earlier unmodified audit results and original baseline source are retained for comparison.

## Exact commands and isolation

From `derexi-policy-pilot/backend` with the existing `.venv`:

```bash
../.venv/bin/python tests/browser_fixture_server.py /tmp/derexi-browser-metadata.json
# Separate terminal, new output directory for each one-use activation:
node tests/test_hardening_browser.cjs /tmp/derexi-browser-metadata.json /tmp/derexi-browser-evidence
DEREXI_BROWSER_EVIDENCE=/tmp/derexi-browser-evidence/browser_results.json \
  ../.venv/bin/python tests/run_hardening_regressions.py
```

The consolidated runner executes each of these separately, retaining exact return statuses/logs:

```bash
../.venv/bin/python tests/test_rbac_stage1.py
../.venv/bin/python tests/test_week7_auth.py
../.venv/bin/python tests/test_secure_api.py
../.venv/bin/python tests/test_validation_hardening.py
../.venv/bin/python tests/test_pulse_integrity.py
../.venv/bin/python tests/test_pulse.py
../.venv/bin/python tests/run_compliance_audits.py
../.venv/bin/python tests/test_week8_stage1.py
```

API/browser commands need local runtime capabilities outside this machine's restricted command sandbox. All write tests use disposable synthetic SQLite databases or original in-memory fake sessions. The original audit engine tripwire blocks live connections. The demo checks confirm the source snapshot stays byte-identical after switching and local writes. Stage 1, auth.py, principals.py, rbac.py and models.py remain byte-identical to their checkpoint versions.

## Required-scenario disposition

| Scenario | Status | Evidence scope |
| --- | --- | --- |
| Signed authentication, invalid/expired claims, unknown mappings/roles | PASS | Existing JWT tests + real secured API tests |
| Employee/Owner/Admin operations, cross-user ownership, actor-ID spoofing | PASS | Secured API tests and updated audit |
| Approval/versioning, private conversations/threads, limited admin oversight | PASS | Real handlers + disposable relational data |
| Incident reporting/assignment/escalation boundaries | PASS | Secured API + browser incident write |
| Questions, feedback, clarification replies/resolution and rejected writes | PASS | API/session/validation suites |
| Developer activation, loopback/Origin/CSRF, revocation, production token isolation | PASS | Demo/API suite and real browser switching |
| Existing selector, Assistant, Library, Governance, Pulse rendering | PASS with synthetic records | Current Chromium run, desktop/mobile screenshots |
| Messages interface | BLOCKED | Pre-existing MSG-001: missing GET /messages; UI degrades to Messages unavailable |
| Incident policy-guidance function/response | FAIL — pre-existing | Four unchanged incident-suite failures, not new regressions |
| Original employee ecosystem in a migrated authenticated demo | BLOCKED | Approved authoritative local snapshot unavailable |
| Live source fetching/redirects | BLOCKED | Fresh read-only attempts hit proxy 403 |
| Supabase integration, production UI sign-in and deployment | NOT RUN / BLOCKED | Auth users/map and separately approved deployment prerequisites absent |

## Files created/modified

Application changes relative to the Stage 1 checkpoint:

- `backend/secure_api.py`, `backend/dev_demo.py`, `backend/dev_bridge.js` (new).
- `backend/main.py`, `backend/database.py`, `backend/ai.py`, `backend/schemas.py`.
- `backend/pulse/integrity.py` (new), `backend/pulse/service.py`, `backend/pulse/sources.py`, `backend/pulse/routes.py`, `backend/pulse/__init__.py`.
- `backend/static/app.js` (identity bridge/exact role-name navigation plus restored upstream Pulse integration).
- `backend/static/index.html`, `backend/static/style.css`, `backend/static/pulse.js` — adopted from reviewed newer main to preserve the existing editorial design; no agent redesign.

Test/evidence/documentation changes:

- `backend/tests/test_secure_api.py`, `test_validation_hardening.py`, `test_pulse_integrity.py` (new).
- Recovered `backend/tests/test_security_controls.py`, `test_c03_audit.py`, `test_pulse.py`, `test_pulse_browser.mjs`; the two deliberate C-01/positive-fixture adjustments are explained above.
- New `backend/tests/browser_fixture_server.py`, `test_hardening_browser.cjs`, `run_compliance_audits.py`, `run_hardening_regressions.py`.
- `docs/security-entrypoints.md`, this report, dated evidence JSON/logs/screenshots and recovered original audit documents/evidence.
- `README.md`, `docs/rbac-design-review.md`, `docs/development-known-issues.md`, `MEMORY.md`.

No changes to actual employees, IDs, departments, assigned roles, policy owners, Supabase data, Auth users, credentials, ORM schema, RLS, migrations, dependencies or unrelated coursework. No production/developer access settings were removed. Only the development branch is authorized for the reviewed commit/push; main is not merged and nothing is deployed. Git metadata/session handoff records the resulting integration commit.

## Final verdict and remaining deployment requirements

- **C-01: VERIFIED for the explicit secured API and synthetic local-demo profile. NOT VERIFIED for migration of the normal course entry point or real Supabase identities.** The legacy compatibility profile remains unguarded and must not be publicly exposed.
- **C-02: VERIFIED for the original 26 checks and isolated real API workflows.** Live PostgreSQL deployment remains untested; SQLite Assistant tests do not validate pg_trgm equivalence.
- **C-03: VERIFIED for the 55 control scenarios (including current browser execution) and additional host/redirect/renderer tests.** Live government connectivity remains blocked.
- **Overall production release is NOT READY.** Supply an approved 14-table local SQLite snapshot preserving the actual employee ecosystem; provision real Auth subjects and an approved one-to-one mapping separately; test normal-UI sign-in before activation; apply/retest network allowances; resolve MSG-001 and the four incident guidance failures; validate against a separate PostgreSQL environment before any approved live integration/deployment. No automatic deployment/merge is authorized.
