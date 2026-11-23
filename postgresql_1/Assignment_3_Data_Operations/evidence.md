# Assignment 3 · Evidence

## Current verification

Source: [single read-only run](../evidence/live-readonly-20261123.json), recorded **2026-11-23T18:09:25.866139+00:00**.
Actual PostgreSQL, not SQLite or a mocked provider. Transaction mode **on**, final
state **ROLLED BACK**, writes executed **false**. The shared verifier recorded
**8 PASS / 0 FAIL**; these are not eight extra tests per assignment.

Exact command executed from repository root:

```sh
derexi-policy-pilot/.venv/bin/python -B postgresql_1/verify_readonly.py --live-readonly --output postgresql_1/evidence/live-readonly-20261123.json
```

An initial sandbox connection attempt was BLOCKED with `OperationalError` before
any query; [retained attempt](../evidence/live-readonly-20261123-attempt1.json).
The approved network retry succeeded. No raw error/DSN or credentials are exported.
No current connectivity blocker remains.

To repeat only safe verification, use a **new unused** output file:

```sh
derexi-policy-pilot/.venv/bin/python -B postgresql_1/verify_readonly.py --live-readonly --output postgresql_1/evidence/readcheck-NEW.json
```

The script loads existing private configuration, uses bounded timeouts, sets READ
ONLY and always rolls back. It never loads/runs any assignment's `example.sql`.
Do not print configuration or enable verbose connection tracing.

## Actual SQL and output

```sql
SELECT id, name FROM public.departments ORDER BY id;
```

```json
[
  {
    "id": 1,
    "name": "Compliance"
  },
  {
    "id": 2,
    "name": "Information Technology"
  },
  {
    "id": 3,
    "name": "Operations"
  },
  {
    "id": 4,
    "name": "Human Resources"
  },
  {
    "id": 5,
    "name": "Marketing"
  },
  {
    "id": 6,
    "name": "Lending"
  },
  {
    "id": 7,
    "name": "Wealth Management"
  }
]
```

[Full assignment output](verified-output.json) includes the other relevant catalog/
count queries and all sanitized rows. [README/report](README.md) maps the criterion.

**INSERT status: DOCUMENTED ONLY / unexecuted.** No RETURNING/inserted-row output exists from this session. The SELECT output above must not be presented as proof of a new INSERT.

## Existing evidence / scope

- [Historical Week 7 read-only diagnostics](../evidence/historical-week7-readonly.json):
  prior PostgreSQL read-model checks and TLS observations, not fresh results.
- [Historical Week 11 preflight](../evidence/historical-week11-preflight.json): prior
  metadata/seed-owner coverage; not proof that pending migrations or seeds ran.
- [Source inventory](../evidence/source-inventory.json): exact original paths/hashes.
- No relevant new screenshot was captured or fabricated. SQL transcripts and real
  catalog rows are primary evidence. The original course LMS image is unchanged.

- [Retained API test transcript](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json), H09: prior disposable SQLite POST/read-back persistence, **not PostgreSQL INSERT verification**; no rerun.
