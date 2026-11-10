# Week 8 — Administrator Dashboard & Policy Governance

Implemented in the existing FastAPI/vanilla-JS application. No live writes, Auth-user creation, migration execution, commit, or push occurred. All local `.env` values and prior uncommitted memory changes were preserved.

## Workflow and permissions

`draft → pending_peer_review → pending_final_approval → approved_pending_publication → published`

Rejection and requested changes return work to the author. Rejection/change decisions require comments. Any saved edit clears both approvals and the reviewer; a fresh peer submission is required. A Policy Owner can read department working copies; an Administrator can read all. Only the author edits/submits, only the selected independent department Policy Owner reviews, and only an independent System Administrator approves/publishes. An Administrator author requires a different Administrator for final approval/publication. Employee and anonymous requests are denied before governance data access. Roles come from the verified database identity on each request; existing loopback/Host/origin/forwarded-header checks remain intact.

Drafts never enter `policy_versions`. Publication atomically creates the published version, audit snapshot, and Week 7 in-app assignment notices. Old versions/citations and existing policy ownership remain. The published-base check prevents a competing stale revision from replacing newer guidance. Policy-row locks, draft-row locks and optimistic revision checks protect concurrent changes. No background publishing runs: an Administrator clicks **Publish approved version** on/after the effective date. Future dates remain in Ready for Publication; the old version stays available. Automatic timed publication is not implemented.

Old POST `/policies` and `/policies/{id}/versions` paths now reject bypasses with 409 after role verification (Employees: 403; anonymous: 401). New writes use `/governance/drafts`, PATCH `/governance/drafts/{id}`, and POST `/governance/drafts/{id}/actions`; clients must send `expected_revision`. GET draft detail includes history, snapshots and the published baseline. `source` retains HTTPS URL/title/date/context, supplied by the human author from Pulse; linkage is provenance, not a verification of article authenticity. Pulse never saves a policy automatically.

Dashboard retains the previous Policy Health, Clarifications and Incidents views. The separate Governance workspace provides role-scoped queues, draft forms, review actions, side-by-side version comparison and audit history. Week 7's existing bell, inbox, assignment/read-watermark records and permission model are reused. Workflow notices link to the governance detail; replying/resolving a notice never approves a policy.

## Live database steps — APPROVAL REQUIRED, not executed

Read-only inventory succeeded: 12 existing users, seven departments. Deficits: Compliance 1, Information Technology 1, Operations 1, Human Resources 1, Marketing 2, Lending 1, Wealth Management 1. Existing administrator/employee policy ownership is retained; no ownership normalization is performed. Exact evidence: `evidence/inventory.json`.

1. Review `backend/migrations/2026-11-10_week8_governance.sql`. It adds two tables and nullable `users.job_title`, enables RLS, denies direct anonymous/authenticated access to working copies/audit, revokes direct-client policy-write privileges, and makes audit UPDATE/DELETE fail. Backend access continues through its existing privileged database connection. Existing SELECT permissions are unchanged. This is **not** a redesign of existing production authentication or RLS.
2. Review `backend/migrations/2026-11-10_week8_owner_seed.sql`. Eight named fictional profiles have department, job title and Policy Owner role. Transaction + advisory/table locks serialize repeated runs; only missing capacity is inserted, names/emails are checked, no existing record is overwritten. A collision/unknown uncovered department aborts the whole seed for manual review. No Auth accounts are created.
3. After explicit approval, run schema then seed using Supabase SQL Editor (or `psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f <exact-script-path>` with a separately configured connection). Do not paste credentials in evidence.
4. Verify every department has at least two Policy Owners using the SELECT at the end of the seed. Compare the original 12 user IDs, roles, departments and policy ownership against inventory. Confirm eight inserts only for this inventory (total 20), and confirm a second seed run inserts zero. In a read-only transaction inspect RLS flags, role grants, constraints, trigger and indexes. Verify authenticated/anonymous direct writes are denied in a staging deployment. Neither SQL migration nor seed idempotency has been executed against PostgreSQL here.
5. Restart the local service and verify `http://127.0.0.1:8000/ui/#dashboard` and `http://127.0.0.1:8000/ui/#governance` with owner/admin personas. An Employee direct hash route renders the Assistant; direct APIs return 403. New governance routes report migration pending if PostgreSQL tables/columns are missing. The rest of the application remains usable before migration.

Restart from `derexi-policy-pilot/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000 --no-proxy-headers
```

## Isolated verification

From `derexi-policy-pilot/`:

```powershell
.\.venv\Scripts\python.exe backend/tests/test_week8_governance.py
.\.venv\Scripts\python.exe backend/tests/run_week8_regression.py
.\.venv\Scripts\python.exe backend/tests/serve_week8_fixture.py
# Separate hidden headless Chromium/Edge with dedicated temporary profile and CDP port 9238:
node backend/tests/test_week8_browser.mjs
```

Fixtures use ephemeral SQLite and a psycopg2 connection tripwire. Production credentials are not used for test writes. Existing Week 7 evidence remains untouched; new results/logs/screenshots are under `evidence/`. PostgreSQL-specific locks, RLS/grants, SQL migration syntax/constraints/triggers, live seed repeatability and trigram ranking are **not** established by SQLite. Production Supabase login remains an existing unimplemented browser sign-in integration. Other pre-existing unrelated security findings, including Pulse publisher-host binding, remain outside this change.

## Screenshot evidence instructions

All supplied screenshots are **illustrative local fixtures**, not live-bank evidence. For live Week 8 screenshots, wait for approved migrations/seed, use fictional personas, and avoid showing tokens, credentials or employee emails.

1. Owner Governance overview and My Drafts/Peer Review/Revisions/Ready queues.
2. Independent peer review with same-department reviewer and mandatory change comment.
3. Administrator Final Approval Queue; show this queue absent for owners.
4. Approved / Pending Publication, effective date and administrator Publish action.
5. Published decision history with actors, timestamps, comments and content snapshots.
6. Pulse action opening an unsaved draft with source URL/title/date/context; demonstrate existing-policy revision selection.
7. Published baseline versus proposed content; show Library still serving the old published version while review is pending.
8. Mobile (390px) review controls, policy body and history without horizontal overflow.
9. Employee navigation/direct-URL denial, plus API 403/anonymous 401 evidence.
10. Preserved Dashboard Policy Health and Week 7 notification link into Governance.

See `evidence/lifecycle-results.json`, `regression-summary.json` and `browser-results.json` for actual pass/fail results. Screenshot filenames map to the list above; the report should distinguish fixture UI evidence from pending live PostgreSQL/production verification.

Final verification: **345 PASS / 0 FAIL** — 102 lifecycle, 73 Week 7 workflow, 29 messaging/RBAC edges, 24 JWT, 97 Pulse, 20 browser. Browser checks include real author/peer/admin actions, required comment focus, notification deep links, employee Dashboard/Governance/Pulse boundaries, published Library, preserved Dashboard, comparison, four viewport widths and zero runtime exceptions. Eleven final screenshots are provided. `evidence/attempts/reviewer-selector-before-fix.png` is historical pre-fix evidence and is not a final result.
