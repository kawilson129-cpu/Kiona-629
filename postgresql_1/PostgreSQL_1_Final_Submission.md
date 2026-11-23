# PostgreSQL 1 · Final submission

**Project:** existing DeRexi: Policy Pilot · **Review:** November 23, 2026.
Each assignment's `README.md` is its concise report. All coursework remains in
the existing `postgresql_1/` folder; no duplicate app/database or root course folder.

| Criterion | Status | Implementation and evidence |
|---|---|---|
| A1 · Create/connect to PostgreSQL | **VERIFIED — existing instance/connectivity** | [Report](Assignment_1_Database_Connection/README.md), [evidence](Assignment_1_Database_Connection/evidence.md). DeRexi's existing Supabase instance is reachable; SELECT 1 → 1, PostgreSQL 17.6, database postgres/public. Original provisioning is documented, not repeated or newly claimed. |
| A2 · Tables, columns, types, primary keys | **VERIFIED — actual schema** | [Report](Assignment_2_Schema_Design/README.md), [catalog output](Assignment_2_Schema_Design/verified-output.json). Core public tables, identity columns, PK/FKs and the existing clarification_reads table verified. Original CREATE TABLE excerpt is documented; no DDL executed. |
| A3 · INSERT and SELECT | **DOCUMENTED ONLY for INSERT; SELECT VERIFIED** | [Report](Assignment_3_Data_Operations/README.md), [local-only unexecuted example](Assignment_3_Data_Operations/example.sql). Actual department SELECT returns seven rows. Existing app INSERT and SQLite tests referenced; no native PostgreSQL INSERT execution claimed. |
| A4 · WHERE and ORDER BY | **VERIFIED** | [Report](Assignment_4_Query_Filtering/README.md), [output](Assignment_4_Query_Filtering/verified-output.json). Exact read-only query returned five approved policies ordered by title/id. |
| A5 · JOIN related tables | **VERIFIED** | [Report](Assignment_5_Relational_Queries/README.md), [output](Assignment_5_Relational_Queries/verified-output.json). users → departments/roles PK/FKs verified; 12 grouped rows total 12 users without exporting personal fields. |

These are evidence statuses, not an instructor grade. Four criteria have current
verification of the reused implementation/data; A3's INSERT remains intentionally
unexecuted under the task's permitted documentation-only option. Creating a fresh
database or rerunning existing CREATE TABLE/seed code is not claimed.

## Actual verification

[Sanitized live record](evidence/live-readonly-20261123.json): **8 PASS / 0 FAIL**,
PostgreSQL read-only mode **on**, transaction **ROLLED BACK**, mutations **false**.
Actual current counts: **7 departments, 3 roles, 12 users, 49 policies**. Queries
selected reference data, policy titles/statuses and aggregate counts; no credential,
customer, personal-name or email values were exported.

An initial sandbox connection attempt was [BLOCKED](evidence/live-readonly-20261123-attempt1.json)
before queries. The approved network retry succeeded; this is not a current blocker
or a failed functional assertion. Client-to-pooler TLSv1.3 was observed with
`sslmode=require`; certificate/hostname and all provider network-leg guarantees
are not inferred. Existing DeRexi configuration was not changed.

## Audit / reuse decisions

- Existing engine/session code, models, SQL handlers, migrations, original design,
  seed proposals and isolated test fixture were inspected and referenced, not rebuilt.
- `public.users.department_id → public.departments.id`, `users.role_id → roles.id`,
  `policies.owner_id → users.id` and `policies.category_id → policy_categories.id`
  are catalog-backed relationships, not guesses from display labels.
- The live catalog has a UNIQUE constraint on `roles.created_at` missing from the
  ORM declaration. The pending seed refers to absent `users.job_title`. It was not run.
  The original design's 43-policy count is historical; current SELECT reports 49.
- [Historical Week 7](evidence/historical-week7-readonly.json) and
  [Week 11](evidence/historical-week11-preflight.json) logs are retained separately
  from current results. Prior SQLite persistence is not PostgreSQL execution proof.
- [Source inventory](evidence/source-inventory.json) and
  [offline artifact validation](evidence/artifact-validation.json) record provenance,
  links, SQL/example matching and status checks. No screenshots were fabricated.

## Remaining evidence and safe reproduction

There is **no current connectivity blocker**. Native PostgreSQL INSERT execution
is unverified; obtaining that additional proof requires a separately isolated,
disposable PostgreSQL database. Do not use Supabase or treat ROLLBACK as protection
against sequence advancement. Unexecuted DDL/INSERT examples are labelled in place.
No migration, schema change, seed, INSERT, UPDATE or DELETE was executed live.

Executed verification command (repository root):

```sh
derexi-policy-pilot/.venv/bin/python -B postgresql_1/verify_readonly.py --live-readonly --output postgresql_1/evidence/live-readonly-20261123.json
```

The script refuses an existing output. For another authorized read-only run, use
a new course evidence filename; do not run the assignment SQL files as a batch.
The verifier runs a fixed SELECT/catalog allowlist and never loads those files.
No installs, application changes, live authentication changes, commit or push.
