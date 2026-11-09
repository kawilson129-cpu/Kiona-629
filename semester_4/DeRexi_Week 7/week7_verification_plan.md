# DeRexi Week 7 — Verification Plan (Internal Messaging & Supabase Auth)

**Status:** PROPOSED — run only after the migration and implementation are approved.
**Rule:** all automated tests use isolated fakes (`FakeSession` + `TestClient`
`dependency_overrides[get_db]`, as in `backend/tests/test_week8_stage1.py`) and write **nothing**
to live Supabase. Live checks are read-only unless explicitly marked.

---

## 1. Auth / JWT verification

Mode: **JWKS (ES256)**. Live-verified coordinates:
JWKS `https://vnumvjamqtuxlctjdzoe.supabase.co/auth/v1/.well-known/jwks.json`,
issuer `https://vnumvjamqtuxlctjdzoe.supabase.co/auth/v1`, audience `authenticated`,
active key `kid 7400369a-63e5-40bf-b6d3-d49e126b0859` (ES256/P-256).

| # | Scenario | Expected |
|---|---|---|
| 1.1 | Valid Bearer JWT (ES256, from project JWKS) | 200; current user resolved |
| 1.2 | Missing `Authorization` header | 401 |
| 1.3 | Expired token | 401 |
| 1.4 | Tampered signature | 401 |
| 1.5 | Wrong `aud` (not `authenticated`) | 401 |
| 1.6 | Wrong `iss` (not the project) | 401 |
| 1.7 | Valid JWT whose `sub` has no `users.auth_user_id` | 403 (unlinked) |
| 1.8 | `GET /me` returns linked business user only | 200, correct id/role/dept |
| 1.9 | JWKS key rotation (unknown `kid` rejected; refetch succeeds) | 401 then 200 |

## 2. Authorization

| # | Scenario | Expected |
|---|---|---|
| 2.1 | Requester reads own thread | 200 |
| 2.2 | Assignee reads assigned thread | 200 |
| 2.3 | Non-participant reads thread | 403/404 |
| 2.4 | Non-participant replies | 403/404 |
| 2.5 | Participant replies | 201 |
| 2.6 | System Administrator oversight read (dashboard) | allowed per policy |
| 2.7 | Anonymous (no token) on any messaging route | 401 |

## 3. Inbox / Sent / thread

| # | Scenario | Expected |
|---|---|---|
| 3.1 | `GET /messages` returns only participant threads | correct rows |
| 3.2 | Inbox ordering by `last_activity_at DESC` | correct order |
| 3.3 | `GET /messages/sent` returns only threads I created | correct rows |
| 3.4 | Unread count = replies without my `message_reads` row | matches |
| 3.5 | `POST /messages` creates `kind='message'` request + opening reply | 201, both rows |
| 3.6 | `POST /messages` to invalid `recipient_id` | 404 |
| 3.7 | Reply bumps `last_activity_at` | timestamp advances |
| 3.8 | `GET /messages/{id}` returns ordered replies + read state | correct |
| 3.9 | Existing clarification thread (`kind='clarification'`) still renders | unchanged |

## 4. Read receipts

| # | Scenario | Expected |
|---|---|---|
| 4.1 | Mark thread read writes `message_reads` for all current replies | rows created |
| 4.2 | Re-marking read is idempotent (unique `(reply_id, user_id)`) | no duplicates |
| 4.3 | Unread count drops to 0 after read | matches |
| 4.4 | New reply after read raises unread count again | increments |

## 5. Internal notifications

| # | Scenario | Expected |
|---|---|---|
| 5.1 | Thread creation notifies recipient | 1 notification, `kind='new_message'` |
| 5.2 | Reply notifies the other participant(s) | correct recipient(s) |
| 5.3 | Assignment notifies assignee | `kind='thread_assigned'` |
| 5.4 | Resolve notifies requester | `kind='thread_resolved'` |
| 5.5 | Incident escalation notifies assignee/owner | `kind='incident_escalated'` |
| 5.6 | `GET /notifications` is self-scoped only | own rows only |
| 5.7 | `POST /notifications/{id}/read` sets `read_at` | unread drops |
| 5.8 | No external email is sent | no outbound mail path exercised |

## 6. RLS (post-apply, non-service-role role)

Run as an `authenticated` role whose JWT maps to a linked user (not the service role).
**Precondition:** the forward migration replaced the permissive
`clarification_requests_select_authenticated` / `clarification_replies_select_authenticated`
(`using (true)`) policies. Without that replacement, participant scoping is a no-op because
permissive policies OR together — verify the permissive policies are gone first.

| # | Scenario | Expected |
|---|---|---|
| 6.0 | Permissive `*_select_authenticated` policies gone on thread tables | absent (else scoping void) |
| 6.1 | `select` own `message_reads` / `internal_notifications` | allowed |
| 6.2 | `select` another user's read receipt / notification | zero rows |
| 6.3 | `select` thread as participant | allowed |
| 6.4 | `select` thread as non-participant | zero rows |
| 6.5 | `insert` reply as participant | allowed |
| 6.6 | `insert` reply as non-participant | rejected |
| 6.7 | `current_user_id()` returns the right business id | correct |

## 7. Regression (must remain unchanged)

| # | Scenario | Expected |
|---|---|---|
| 7.1 | `POST /ask` confident answer + citations | unchanged |
| 7.2 | `POST /ask` low-confidence → clarification routing | unchanged |
| 7.3 | `GET /policies`, `GET /policies/search` | unchanged |
| 7.4 | `GET /policies/{id}` current-version resolution | unchanged |
| 7.5 | `POST /feedback` | unchanged |
| 7.6 | `GET /dashboard/policy-health` totals + `clarifications_by_status` | unchanged |
| 7.7 | `GET /incidents` scoping + `POST /incidents` guidance | unchanged |
| 7.8 | Existing `/clarifications` behavior for pre-Week-7 rows | unchanged |

## 8. Data integrity / rollback drill (staging only)

| # | Scenario | Expected |
|---|---|---|
| 8.1 | Migration applies idempotently (safe re-run) | no errors, no dup objects |
| 8.2 | Backfill (if approved) only touches threads with replies | correct rows, idempotent |
| 8.3 | Forward → rollback → forward leaves pre-existing data intact | lossless for pre-Week-7 rows |
| 8.4 | `py_compile` / `node --check` clean after implementation | clean |

## Commands
```powershell
# backend static checks
cd derexi-policy-pilot\backend
python -m py_compile main.py schemas.py models.py
# node --check static\app.js
# isolated tests (fakes, no live writes)
pytest tests\ -q
```
