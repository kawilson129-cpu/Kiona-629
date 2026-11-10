# Integration results and database safety

Date: November 10, 2026. Baseline commit: `b66b7e4dd5b5d9203b64b5f15c7188192e2d64dc`. Final source hashes are in `evidence/source-manifest.json`.

| Required interaction | Isolated result/evidence | Live status |
|---|---|---|
| Assistant → clarification → Messaging | PASS, I01–I10 and U07. Real HTTP/ORM persistence, admin assignment, owner and employee notices/replies | BLOCKED / not executed |
| Draft → independent peer → independent System Admin → Library | PASS, 102 lifecycle checks; U14–U18. Includes self-review denial, invalid inputs, approval invalidation, audit snapshots, future dates, competing revisions and rollback | BLOCKED / not executed |
| Pulse → draft/revision with source | PASS, lifecycle provenance tests; U21–U23, exact URL and published baseline retained | BLOCKED / not executed |
| Feedback → Policy Health Dashboard | PASS, I11–I18, U03–U06/U19. Helpful/unhelpful edits use one row; department isolation verified | BLOCKED / not executed |
| Incident report → authorized administrator triage | PASS, I19–I25 and U09–U11/U20. Owner/Employee changes denied; assigned handler visibility verified | BLOCKED / not executed |
| Login/logout → role navigation and API access | PASS, synthetic signed JWTs and real BFF cookie flow; invalid password, no-session API denial, Employee/Owner/Admin checks | BLOCKED / not executed |
| Document upload/preview → draft | PASS, 47 real parser/intake checks and U14–U18. Explicit author confirmation and authenticated private-original controls retained | BLOCKED / not executed |

Existing published policies stay available while replacements are drafts or approved for a future date. The lifecycle suite confirms unpublished versions never enter employee history, and successful replacement retains the old version. U23 checks the Library still reports 1.0 while the Pulse revision is a draft; U24 verifies Library availability during a simulated Governance-table outage.

## Isolation and limits

- Reused `messaging_fixture.py`: in-memory SQLite, foreign keys, real FastAPI handlers/SQLAlchemy transactions and a `psycopg2.connect` tripwire. Schema creation and fictional records occur **only inside disposable SQLite**, never Supabase.
- The fixture translates PostgreSQL LATERAL/ILIKE/DISTINCT ON/date syntax. It does not validate PostgreSQL query plans, locks, migration correctness or RLS. The fixture intentionally returns no trigram matches: Assistant uncertainty/routing is real, retrieval scoring is not verified.
- Dashboard department testing attaches a clearly synthetic citation to a stored Assistant answer in SQLite. This verifies joins/scope/counting, not live retrieval or answer quality.
- Browser server reuses Week 9's mock provider/synthetic EC JWT verifier and Week 7's seeded SQLite threads. Pulse is a deterministic fictional feed. The real BFF, cookies, RBAC, API, parser and UI execute locally.
- Only the dedicated fixture binds `127.0.0.1:8031`; proxy headers stay disabled. Its outage controls exist in the test module only. No production auth bypass, credential map, runtime `.env`, migration or RLS/grant change was made.
- Native macOS DOCX/PDF extraction used the existing subprocess/resource controls and temporary private storage. Windows/Linux execution, worker affinity and production original-file retention remain outside this verification.
- HTTP loopback test cookies are not proof of production TLS/Secure-cookie deployment. The historical Week 9 HTTPS TestClient result is retained separately.

## Reproduction

From `derexi-policy-pilot/backend/` using the existing environment:

```sh
../.venv/bin/python tests/run_week10.py
```

The runner starts each suite in a fresh process and imports existing test functions without invoking old evidence writers. All new outputs go to this existing Week 10 directory. Run only named suites for focused retests, for example `tests/run_week10.py integration pulse`.

For browser UAT, start `../.venv/bin/python tests/serve_week10_fixture.py`, use a dedicated Chromium with remote debugging on loopback port 9230, then run `node tests/test_week10_browser.mjs`. Node's built-in WebSocket/CDP client adds no dependencies. Start a fresh fixture for a complete rerun: its unchanged sign-in throttle allows eight attempts per minute. A fresh fixture discards synthetic records only.

`--mobile-only` continues the same authenticated browser/fixture and carries forward passing U00–U28 checks. It reinstates the 390px emulation, retests the remaining mobile actions and records its predecessor rather than counting duplicate executions. It is not a standalone full UAT run.

## Attempts and retests

Initial corrected API baseline: 32 PASS / 8 FAIL (one non-answer-feedback failure and seven publisher variants). C-03: 53 PASS / 1 FAIL. Initial browser feedback baseline: 1 PASS / 1 FAIL. These overlap by defect and are not summed as distinct bugs.

Earlier harness mistakes included notification key `request_id` instead of `thread_id`, missing Origin on a Node fixture-control request, waiting for unloaded categories/thread details, old Pulse/Messaging selectors, and expecting the Ask tab after a retained Report tab. Repeated logins correctly triggered HTTP 429; the dedicated fixture was restarted instead of weakening the throttle. Earlier mobile continuation initially lost CDP emulation; the 756px screenshots were replaced by verified 390px captures. These are test-harness corrections, not application defect claims. Relevant attempt JSON is retained under `evidence/attempts/`.

Final: **342 backend checks + 37 browser checks = 379 PASS, 0 FAIL, 0 automated checks blocked**. Seven live workflow verifications remain blocked and are counted separately. No live checks were attempted this week.
