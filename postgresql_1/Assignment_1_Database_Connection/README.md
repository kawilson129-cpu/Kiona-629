# Assignment 1 · Database connection

**Objective / rubric:** create and connect to PostgreSQL, using the already-created
DeRexi Supabase database rather than provisioning a duplicate.

**Status: VERIFIED — existing PostgreSQL instance and current connectivity.**
New provisioning/`CREATE DATABASE` was not performed or claimed.

## Reused implementation

- `derexi-policy-pilot/backend/database.py:19–43`: loads server-only `DATABASE_URL`,
  applies the existing transport policy and builds a SQLAlchemy engine/pool.
- `database.py:45–63`: reusable session factory and request-scoped cleanup.
- `backend/transport.py:6–18`: existing TLS policy, unchanged.
- `backend/main.py:276–279`: existing health route executes `SELECT 1`.
- `semester_3/DeRexi_Week 3/database-design.md:380–400`: historical Supabase schema
  and migration/provisioning context. Database creation is historical project work,
  not a fresh deployment or a newly captured provisioning log.

## Steps and actual result

1. Use the existing project virtual environment and private configuration; never
   print the DSN, host, password or provider error details.
2. Run the bounded read-only verifier documented in [evidence.md](evidence.md).
3. It enforces read-only mode before coursework queries and always rolls back.
4. `SELECT 1` returned **1**; database **postgres**, schema **public**, server
   version number **170006 (PostgreSQL 17.6)**. The existing instance is reachable.

Client-to-pooler transport was encrypted with **TLSv1.3**, configured `sslmode=require`.
This is not certificate/hostname validation or proof of every provider network leg.
The course does not modify transport settings or production authentication.

## Evidence / completion

[example.sql](example.sql) contains the actual SELECT, wrapped for read-only use.
[verified-output.json](verified-output.json) records actual sanitized output;
[evidence.md](evidence.md) gives commands and historical references. The existing
created database plus real connectivity support the criterion. A fresh server/database
creation audit trail is **DOCUMENTED ONLY**, not a new execution claim.
