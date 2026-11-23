# Assignment 4 · Query filtering and sorting

**Objective / rubric:** use WHERE and ORDER BY. **Status: VERIFIED.**

## Existing DeRexi behavior

`backend/main.py:145–169` defines existing policy retrieval SQL: its approved-policy
`WHERE` appears at line 167 and score ordering at line 168; current-version ordering
is at line 155. `backend/dev_auth.py:229–234` demonstrates a parameterized
`WHERE u.id = :uid`. No retrieval logic, confidence threshold or RBAC was changed.

## Read-only demonstration

[example.sql](example.sql) uses the same verified policy table/status convention:

```sql
SELECT id, title, status FROM public.policies
WHERE status = 'approved'
ORDER BY title ASC, id ASC
LIMIT 5;
```

`WHERE` limits results to approved policies; `ORDER BY` uses the database's actual
text collation and an ID tie-breaker; LIMIT bounds output. This small course query
uses existing data, not a second implementation of the application's search ranking.

## Steps / actual result

1. Confirm `public.policies.id/title/status` from live metadata.
2. Execute the above SELECT inside enforced read-only mode; roll back.
3. Verify that all returned rows have status `approved` and at most five are returned.

Exactly **5 approved rows** were returned, starting with “Acceptable Use & Remote
Work” and “Anti-Harassment & Complaint Reporting”. The complete actual result is
in [verified-output.json](verified-output.json) and [evidence.md](evidence.md).
The PostgreSQL server actually parsed/executed this SELECT; no mock, SQLite ordering
or invented screenshot is used. No claim is made that this reruns pg_trgm ranking.

**Rubric coverage:** WHERE and ORDER BY are both demonstrated and verified.
No outstanding requirement within this criterion; no live data changes occurred.
