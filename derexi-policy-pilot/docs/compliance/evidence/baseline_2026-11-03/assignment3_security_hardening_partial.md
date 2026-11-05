# Compliance Assignment 3 — security hardening evidence

Date: November 3, 2026. **Overall result: INCOMPLETE / BLOCKED. Not production ready.**

This is the final evidence record for this attempt, not a claim that all requested phases completed. Existing evidence is retained. No course Supabase writes, schema/RLS changes, Auth-user creation, production credential changes, protected-branch merge or deployment occurred.

## GitHub checkpoint and release state

- Starting branch: `work`, HEAD `dba7f8f`. Reviewed staged/unstaged changes and explicit Stage 1 files for secrets before staging. Only the previously completed Stage 1 modules, tests and notes were checkpointed; no .env, employee export, private key or real credential was included. Synthetic loopback test values are not live credentials.
- Development branch: `codex/derexi-security-hardening`.
- Stage 1 commit: `4eac30aa0257b90c2098c1deba3a0b8117746c7e`.
- Push: **PASS**, confirmed by `git ls-remote origin refs/heads/codex/derexi-security-hardening` returning that exact SHA. Main/protected branches were not updated. No force push or deployment.
- Later C-02/C-03 improvements and this report remain **uncommitted and unpushed**. Phase 7 requires all required integration/regression checks to pass; that condition is not met. The checkpoint is preserved on GitHub, and later work is preserved in the working tree.

## Original findings and baseline

The available November 3 notes establish: C-01 has isolated permission/principal logic but no route enforcement; C-02 has missing text/boolean/reference validation; F-03-01 allows unrelated HTTPS article URLs to be labeled as government sources. The original 26 C-02 and 55 C-03 assessment scripts/checklists were not in this checkout, workspace scratch/shared directories or the pasted request. Their reruns are **BLOCKED**, not replaced with invented results. Their location was requested during work.

| Suite or check | Before | After this attempt |
| --- | --- | --- |
| Existing Stage 1 RBAC | 40 passed | 40 passed, unchanged |
| Existing JWT foundation | 24 passed | 24 passed, unchanged |
| Existing incident suite | 3 passed / 6 failed | 4 passed / 5 failed |
| New API/validation regression suite, 28 methods | 8 passed / 19 failed / 1 error against checkpoint source | 28 passed |
| New Pulse integrity suite | New suite; old code lacks the integrity module | 22 passed |
| Unrelated HTTPS URL attributed to FDIC | Reproduced: accepted by checkpoint make_article | Rejected by integrated normalizer |
| Original 26 C-02 checks | Exact baseline unavailable | BLOCKED — original checks missing |
| Original 55 C-03 checks | Exact baseline unavailable | BLOCKED — original checks missing |
| Live government feeds | No successful validation claimed | BLOCKED — URLError on all four configured sources; FDIC diagnosis confirms proxy tunnel 403 |

The before comparison used a temporary copy of the checkpoint's backend and unchanged static files, with the same new regression runner and a disposable SQLite database. It did not change the working checkout or create a Git worktree. The one baseline error is the new Pulse integration test expecting a destination-validation hook absent from the old implementation. These 28 methods are explicitly a new regression suite, not the original 26 assessment checks. Detailed synthetic-only run logs were captured under /tmp during this attempt; the durable results and limitations are recorded here.

## Phase 2 / C-01 — stopped at the compatibility prerequisite

**BLOCKED.** No approved local database or complete authoritative snapshot exists in this checkout. Historical preview data and memory disagree on department/role context and are not safe authority for reconstructing the fictional employees. Supabase has no configured Auth users according to the request, and creating them is forbidden without separate approval. No trusted production identity map is provisioned either.

The request expressly requires a usable, tested authenticated developer entry point before enabling authentication across the normal application. Therefore normal API authentication/guards were **not activated**. The existing UI and persona switcher were not changed or removed. No insecure fallback, permanent bypass, unsigned-header identity provider or local credential accepted by production was added. The 40/24 isolated passing tests do not establish that the running application enforces RBAC.

| Required C-01 check | Result | Evidence / limit |
| --- | --- | --- |
| Preserve Stage 1 foundation | PASS | Unchanged modules/tests, checkpointed and pushed |
| Pure role, ownership, participant and incident rules | PASS in isolation | 40 offline tests |
| JWT verification and verified-subject mapping | PASS in isolation | 24 existing auth tests plus resolver tests |
| Enforce auth on protected API routes | BLOCKED | Not enabled before developer-entry prerequisite |
| Employee/Owner/Admin API authorization | BLOCKED | Existing API still lacks integrated RBAC |
| Cross-user privacy and actor-ID impersonation prevention | BLOCKED | Consistency validation is not verified identity enforcement |
| Administrator-only policy publication | BLOCKED in running API | Pure rule exists; route guard not installed |
| Tested authenticated developer persona switching | BLOCKED | Requires approved isolated data source, then secure local-session implementation |
| Preserve current employees/IDs/departments/roles/ownership | PASS for non-modification | No business records read from or written to Supabase; no seeds rewritten |
| Preserve UI/source-code/developer-tool access | PASS for non-modification | Browser files and developer access configuration unchanged |
| No production auth bypass or shared dev credentials | PASS for introduced changes | No new identity mechanism activated |

Next safe action: provide an approved local database/snapshot path, implement/test the local entry point with those unchanged business records, then integrate shared guards. Do not expose the present API publicly. Developer OS/tool access remains separate from application permissions.

## Phase 3 / C-02 — integrated validation changes

`schemas.py` now trims text, forbids unexpected body fields, constrains IDs to positive strict signed-bigint values, rejects blank titles/bodies/versions, and enforces strict feedback/review booleans. Limits: title 200, policy body 100,000, version 40, summary/feedback comment 2,000, incident description/resolution notes 10,000, existing question/topic/reason 1,000 and reply 2,000 characters. Incident updates reject empty patches and null status/severity/escalation values.

`main.py` validates referenced owners, authors, policy/incident categories, assignees, users, policies, conversations and messages before constructing/mutating rows. Clarification message/conversation/requester links must agree. Feedback must refer to an assistant response in the specified user's conversation. These consistency checks do not substitute for C-01's blocked verified-principal enforcement. Optional existing references remain optional; legitimate workflows are tested.

API errors omit raw submitted inputs, exception contexts, SQL and connection details. Conflicts return 409, unavailable data services 503, and unexpected failures a generic 500. Session cleanup retains transaction rollback behavior on failures. No ORM schema change is required.

| Required C-02 check | Result | Evidence |
| --- | --- | --- |
| Maximum lengths on formerly unbounded text | PASS | Schema and actual API boundary tests |
| Blank/whitespace policy titles/bodies rejected | PASS | API requests rejected before persistent writes |
| Feedback true/false strict; strings/numbers rejected | PASS | Valid booleans persist; coercions rejected |
| Referenced users/policies/categories/messages/conversations/assignments checked | PASS in isolated API | Disposable relational DB with foreign keys and link-consistency tests |
| Invalid requests cause no writes | PASS for tested cases | Persisted row counts and incident status compared before/after rejection |
| Safe understandable errors | PASS for tested cases | Validation input not echoed; simulated DB exception details hidden |
| Legitimate questions, feedback, policies/versions, incidents and clarification flow | PASS in isolated API | Successful requests and persisted rows/relationships checked |
| Original 26-check rerun | BLOCKED | Exact original script/checklist required |

Compatibility: clients must send actual JSON booleans and integer IDs, not string/number coercions; oversized or extra fields now return 422. No existing record is rewritten/truncated. The tests use strict SQLite foreign keys and a test-only INTEGER rendering for bigint autoincrement. Search rows are deterministic in the assistant tests: PostgreSQL pg_trgm scoring is not validated by SQLite.

## Phase 4 / C-03 — integrated feed integrity changes

The existing fetch → normalize → cache flow remains. `pulse/integrity.py` adds source-specific exact HTTPS hosts, rejects userinfo, misleading suffixes, unexpected ports, controls/backslashes and malformed URLs. FDIC's multi-tenant `content.govdelivery.com` links must use `/accounts/USFDIC/bulletins/<id>`; unrelated GovDelivery accounts are rejected. Configured feed URLs are checked before contact, each redirect hop is checked before following it, and the response's actual final URL is rechecked.

Articles are checked with HEAD before inclusion; publishers returning 405/501 may use a same-policy GET without consuming the body. Policy denials/authentication errors are never retried this way. Unverifiable destinations are omitted. Validation uses inherited proxy and TLS verification, up to eight workers and at most 200 candidate articles per refresh. This adds network cost and may omit links when their destination cannot be verified. The 30-minute cache interval, previous-success fallback, classifications/source labels, output article limit and editorial UI remain intact. Cache counts now reflect verified articles.

| Required C-03 check | Result | Evidence |
| --- | --- | --- |
| Configured source and approved publication hosts | PASS offline | Four configured sources plus expected official publication hosts |
| FDIC GovDelivery bulletins retained, wrong tenants denied | PASS offline | Exact-account/path tests |
| Unrelated/misleading domain and cross-source attribution rejection | PASS offline | Normalizer and hostname regression cases |
| Redirect hops validated before contact | PASS offline | 301/302/303/307/308 allow/deny tests |
| Actual final response destination revalidated | PASS offline | Controlled final-URL response tests |
| HEAD compatibility and policy-denial behavior | PASS offline | 405/501 fallback, no body read, no 403 retry |
| Editorial fields, classifications, cache semantics, bounded response size | PASS offline | Existing pipeline and API exercised with controlled feed responses |
| Live government feeds and publication redirects | BLOCKED | Current proxy policy denies access; no verification bypass attempted |
| Original 55-check rerun | BLOCKED | Exact original script/checklist required |

Saved an **unapplied environment configuration draft** adding these required hosts while preserving the existing package-manager presets: federalregister.gov, www.federalregister.gov, fdic.gov, www.fdic.gov, public.govdelivery.com, content.govdelivery.com, federalreserve.gov, www.federalreserve.gov, nist.gov, www.nist.gov, csrc.nist.gov, nvlpubs.nist.gov. Draft persistence is confirmed. Activating access requires review/save in environment settings and cloud-environment publication; nothing was applied or publicly deployed by this save. No broader network access or credential requirement was added.

## Phase 5 — regression scope and commands

Use the existing project `.venv`, Python 3.12.14. Run each suite separately from `derexi-policy-pilot/backend`:

```bash
../.venv/bin/python tests/test_rbac_stage1.py
../.venv/bin/python tests/test_week7_auth.py
../.venv/bin/python tests/test_validation_hardening.py
../.venv/bin/python tests/test_pulse_integrity.py
DATABASE_URL=postgresql+psycopg2://offline:offline@127.0.0.1:1/offline \
  ../.venv/bin/python tests/test_week8_stage1.py
```

API/TestClient suites need the local runtime capabilities denied by this machine's restricted command sandbox. All write tests used fresh disposable in-memory SQLite databases or the original fake sessions, with synthetic identities, never course Supabase. The validation runner disables .env loading and sets an unreachable local import-only Postgres URL. No production credential is read for those tests.

Verified API workflows: policy creation/versioning, Assistant answer/citations/conversation/feedback (deterministic search rows), Assistant fallback → clarification → reply → resolve, incident creation/update, Pulse endpoint, safe errors and served static UI/persona-selector source. `node --check backend/static/app.js` passes and the browser files are unchanged.

Not validated: real authenticated browser switching, live Employee/Owner/Admin guarded API workflows, live Supabase permissions, PostgreSQL trigram behavior, full governance dashboard SQL, live AI provider, live feed redirects, original assessment suites or secure deployment. The current UI is preserved and serves in tests; that is not a claim that the user's complete data-backed demo works in this machine.

## Separately tracked existing defects

- MSG-001: UI calls a missing `/messages` backend endpoint. No endpoint was silently fabricated in this attempt.
- INC-001: original incident suite now has five remaining failures: three `incident_guidance` function tests, reporter-scoped listing and the guidance response field. The category-not-found failure was fixed by C-02. Existing tests were not modified or weakened.
- Other existing application routes remain unauthenticated because C-01 activation is blocked. This is an unresolved finding, not a passing authorization result.

## Exact file changes

Stage 1 checkpoint (six files, preserved and pushed):

- `MEMORY.md`
- `backend/rbac.py`
- `backend/principals.py`
- `backend/tests/test_rbac_stage1.py`
- `docs/rbac-design-review.md`
- `docs/development-known-issues.md`

Later application/evidence changes (uncommitted):

- `backend/schemas.py`
- `backend/main.py`
- `backend/pulse/integrity.py` (new)
- `backend/pulse/sources.py`
- `backend/pulse/service.py`
- `backend/tests/test_validation_hardening.py` (new)
- `backend/tests/test_pulse_integrity.py` (new)
- `docs/compliance/assignment3_security_hardening_final.md` (new, this report)
- `docs/development-known-issues.md` (appended status only)
- `MEMORY.md` (current work record)

No changes to browser design/switcher, business-user records, models/schema, auth.py, rbac.py/principals.py after checkpoint, migrations, RLS, dependencies, existing test assertions or unrelated coursework. A final diff/secret review covers the listed working-tree paths; no real credentials/employee exports were added.

## Final control verdict and unblock actions

- **C-01: BLOCKED / NOT VERIFIED.** Supply an approved isolated local data source; build/test usable authenticated developer switching before activating route authentication; then test verified principals and every role/object guard.
- **C-02: implemented and passing the 28-method isolated API/regression suite; overall required assessment verification BLOCKED** until the original 26 checks are available and rerun.
- **C-03: implemented and passing 22 offline integrity tests plus the API pipeline check; overall required verification BLOCKED** until network access permits live checks and the original 55 checks are available.
- **Release: BLOCKED.** Keep later changes local for review. After prerequisites arrive, resume outstanding phases, rerun all required checks, then commit/push verified improvements to the same development branch. Do not merge or deploy automatically.
