# Assignment 2 · Evidence

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
SELECT table_schema, table_name, ordinal_position, column_name,
        data_type, udt_name, is_nullable, column_default, is_identity, identity_generation
        FROM information_schema.columns WHERE table_schema = 'public'
        AND table_name IN ('departments','roles','users','policies','clarification_reads')
        ORDER BY table_name, ordinal_position
```

```json
[
  {
    "table_schema": "public",
    "table_name": "clarification_reads",
    "ordinal_position": 1,
    "column_name": "request_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "clarification_reads",
    "ordinal_position": 2,
    "column_name": "user_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "clarification_reads",
    "ordinal_position": 3,
    "column_name": "last_read_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "departments",
    "ordinal_position": 1,
    "column_name": "id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "YES",
    "identity_generation": "BY DEFAULT"
  },
  {
    "table_schema": "public",
    "table_name": "departments",
    "ordinal_position": 2,
    "column_name": "name",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "departments",
    "ordinal_position": 3,
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 1,
    "column_name": "id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "YES",
    "identity_generation": "BY DEFAULT"
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 2,
    "column_name": "title",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 3,
    "column_name": "summary",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "YES",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 4,
    "column_name": "category_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "YES",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 5,
    "column_name": "owner_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "YES",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 6,
    "column_name": "status",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "'draft'::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 7,
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "policies",
    "ordinal_position": 8,
    "column_name": "updated_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "roles",
    "ordinal_position": 1,
    "column_name": "id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "YES",
    "identity_generation": "BY DEFAULT"
  },
  {
    "table_schema": "public",
    "table_name": "roles",
    "ordinal_position": 2,
    "column_name": "name",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "roles",
    "ordinal_position": 3,
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 1,
    "column_name": "id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "YES",
    "identity_generation": "BY DEFAULT"
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 2,
    "column_name": "first_name",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 3,
    "column_name": "last_name",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 4,
    "column_name": "email",
    "data_type": "text",
    "udt_name": "text",
    "is_nullable": "NO",
    "column_default": "''::text",
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 5,
    "column_name": "department_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 6,
    "column_name": "role_id",
    "data_type": "bigint",
    "udt_name": "int8",
    "is_nullable": "NO",
    "column_default": null,
    "is_identity": "NO",
    "identity_generation": null
  },
  {
    "table_schema": "public",
    "table_name": "users",
    "ordinal_position": 7,
    "column_name": "created_at",
    "data_type": "timestamp with time zone",
    "udt_name": "timestamptz",
    "is_nullable": "NO",
    "column_default": "now()",
    "is_identity": "NO",
    "identity_generation": null
  }
]
```

[Full assignment output](verified-output.json) includes the other relevant catalog/
count queries and all sanitized rows. [README/report](README.md) maps the criterion.

**DDL status: DOCUMENTED ONLY execution.** The existing creation excerpt was not run; live catalog constraints and types are verified.

## Existing evidence / scope

- [Historical Week 7 read-only diagnostics](../evidence/historical-week7-readonly.json):
  prior PostgreSQL read-model checks and TLS observations, not fresh results.
- [Historical Week 11 preflight](../evidence/historical-week11-preflight.json): prior
  metadata/seed-owner coverage; not proof that pending migrations or seeds ran.
- [Source inventory](../evidence/source-inventory.json): exact original paths/hashes.
- No relevant new screenshot was captured or fabricated. SQL transcripts and real
  catalog rows are primary evidence. The original course LMS image is unchanged.
