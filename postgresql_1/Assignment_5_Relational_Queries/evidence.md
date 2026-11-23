# Assignment 5 · Evidence

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
SELECT d.name AS department, r.name AS role, count(u.id) AS user_count
FROM public.users AS u
JOIN public.departments AS d ON d.id = u.department_id
JOIN public.roles AS r ON r.id = u.role_id
GROUP BY d.name, r.name
ORDER BY d.name ASC, r.name ASC;
```

```json
[
  {
    "department": "Compliance",
    "role": "Policy Owner",
    "user_count": 1
  },
  {
    "department": "Compliance",
    "role": "System Administrator",
    "user_count": 1
  },
  {
    "department": "Human Resources",
    "role": "Employee",
    "user_count": 1
  },
  {
    "department": "Human Resources",
    "role": "Policy Owner",
    "user_count": 1
  },
  {
    "department": "Information Technology",
    "role": "Employee",
    "user_count": 1
  },
  {
    "department": "Information Technology",
    "role": "Policy Owner",
    "user_count": 1
  },
  {
    "department": "Information Technology",
    "role": "System Administrator",
    "user_count": 1
  },
  {
    "department": "Lending",
    "role": "Employee",
    "user_count": 1
  },
  {
    "department": "Lending",
    "role": "Policy Owner",
    "user_count": 1
  },
  {
    "department": "Operations",
    "role": "Employee",
    "user_count": 1
  },
  {
    "department": "Operations",
    "role": "Policy Owner",
    "user_count": 1
  },
  {
    "department": "Wealth Management",
    "role": "Policy Owner",
    "user_count": 1
  }
]
```

[Full assignment output](verified-output.json) includes the other relevant catalog/
count queries and all sanitized rows. [README/report](README.md) maps the criterion.

## Existing evidence / scope

- [Historical Week 7 read-only diagnostics](../evidence/historical-week7-readonly.json):
  prior PostgreSQL read-model checks and TLS observations, not fresh results.
- [Historical Week 11 preflight](../evidence/historical-week11-preflight.json): prior
  metadata/seed-owner coverage; not proof that pending migrations or seeds ran.
- [Source inventory](../evidence/source-inventory.json): exact original paths/hashes.
- No relevant new screenshot was captured or fabricated. SQL transcripts and real
  catalog rows are primary evidence. The original course LMS image is unchanged.
