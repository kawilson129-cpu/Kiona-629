# Assignment 3 · INSERT and SELECT

**Objective / rubric:** demonstrate INSERT and SELECT operations with DeRexi data.
**Status: DOCUMENTED ONLY for INSERT; VERIFIED for the current SELECT.**

## Existing operations reused

- `backend/main.py:554–560` already contains a parameterized PostgreSQL
  `INSERT INTO clarification_reads ... ON CONFLICT ...`; it was inspected,
  not invoked. The following `db.commit()` is why the live `/ask` workflow was
  deliberately not called for this coursework.
- `backend/tests/messaging_fixture.py:114–148` already creates/seeds disposable
  **SQLite** departments, roles, users and policies. Existing API evidence proves
  fixture persistence; it is not native PostgreSQL INSERT execution evidence.
- Week 3 design section 8 documents historical seed data. The newer approval-only
  `2026-11-10_week8_owner_seed.sql` is not an executed seed and is not used as proof.

## Verified SELECT

```sql
SELECT id, name FROM public.departments ORDER BY id;
```

This actually returned **7 rows** from the existing PostgreSQL database. Full rows
and timestamp are in [verified-output.json](verified-output.json). Counts at the
same read-only run: 7 departments, 3 roles, 12 users and 49 policies.

## Clearly unexecuted INSERT example

[example.sql](example.sql) demonstrates `INSERT INTO public.departments(name)`,
`VALUES`, `RETURNING id,name`, and SELECT of the new name. It relies on the actual
verified department columns and identity primary key, so no IDs or relationships
were guessed. It is **LOCAL DISPOSABLE POSTGRESQL ONLY / NOT EXECUTED**.

To execute it in a separately authorized disposable PostgreSQL copy, first recreate
that existing table from verified metadata, run the example, inspect RETURNING/SELECT,
and roll back. No successful output is invented. **Do not run it on Supabase:**
rollback alone does not undo sequence advancement and is not a live-write safeguard.

## Rubric result / remaining evidence

SELECT is **VERIFIED**; INSERT syntax/workflow and original implementation are
**DOCUMENTED ONLY**, a permitted delivery mode in the task. No native PostgreSQL
INSERT was executed here, and this assignment is not labelled fully runtime-verified.
Additional execution evidence would require an isolated disposable PostgreSQL database.
See [evidence.md](evidence.md) for current and historical evidence boundaries.
