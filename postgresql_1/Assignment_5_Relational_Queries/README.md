# Assignment 5 · Relational queries

**Objective / rubric:** JOIN related tables. **Status: VERIFIED.**

## Reused relationships and application query

The live catalog confirms `public.users.department_id` references
`public.departments.id`, and `public.users.role_id` references `public.roles.id`.
The existing roster query at `backend/dev_auth.py:170–175` already joins those three
tables. The role lookup at lines 229–234 is another actual JOIN implementation.
No new application query handler was added.

## Verified, privacy-conscious demonstration

[example.sql](example.sql) joins those existing tables and aggregates rather than
exporting employee names/emails:

```sql
SELECT d.name AS department, r.name AS role, count(u.id) AS user_count
FROM public.users AS u
JOIN public.departments AS d ON d.id = u.department_id
JOIN public.roles AS r ON r.id = u.role_id
GROUP BY d.name, r.name
ORDER BY d.name ASC, r.name ASC;
```

`u`, `d`, and `r` are aliases. Each ON clause follows a verified FK relationship.
The inner JOIN returns matching department/role groups; GROUP BY counts users in
each group. It does not invent a direct relationship between policies and roles.
The separate policy-owner relationship is `policies.owner_id → users.id`.

## Actual verification

1. Inspect actual PK/FK metadata before running the relational SELECT.
2. Run the exact query on PostgreSQL in a read-only transaction.
3. Sum returned user counts and compare with `SELECT count(*) FROM public.users`.

**12 groups** were returned, totaling **12 users**, matching the independent table
count. For example, Compliance has one Policy Owner and one System Administrator
in separate groups. Full sanitized output is in [verified-output.json](verified-output.json)
and [evidence.md](evidence.md). No personal/customer fields were selected.

**Rubric coverage:** actual JOINs combine related tables and return verified data.
No live mutation or production-authentication test was performed.
