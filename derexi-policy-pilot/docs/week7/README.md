# DeRexi Week 7 — Internal Messaging & Supabase Authentication

**Status:** PROPOSAL — design approved, implementation ON HOLD, awaiting Kiona's approval
**Phase:** SDLC Week 7 of 12
**Codebase:** `derexi-policy-pilot/` (canonical)
**Database:** Supabase Postgres 17 — project ref `vnumvjamqtuxlctjdzoe`
**Rule for this package:** nothing here has been applied. No migrations have been run, no
Supabase Auth users created, no live data modified, no application code changed, no commits made.

This package is the reconstruction of the approved Week 7 direction after an editor crash
lost the in-conversation draft. The surrounding decisions are recorded in `MEMORY.md`
(entries for Oct 11–12, 2026) and the schema context is in `docs/database-design.md`.

## Package contents

| File | Purpose | Applied? |
|---|---|---|
| `README.md` (this file) | Full A–I proposal, authorization model, API surface, open decisions | n/a |
| `week7_messaging_auth_migration.sql` | Additive forward migration (auth linkage, thread reuse, read receipts, notifications, RLS) | **No** |
| `week7_messaging_auth_rollback.sql` | Exact reversal of the forward migration | **No** |
| `week7_verification_plan.md` | Test matrix + RLS/auth verification steps | **No** |

---

## Implementation status — authentication foundation (isolated, APPROVED)

The isolated JWT verification foundation is **built and verified**. It is **not imported by the
running application**; no route requires auth, no auth users exist, no migration/RLS change has
been applied, and the UI/persona selector is untouched.

| Artifact | What it is |
|---|---|
| `backend/auth.py` | Reusable verifier: JWKS signature (ES256), `exp`, `nbf`, `iss`, `aud`, required claims; `extract_bearer_token`; read-only `fetch_jwks`; unused FastAPI dependency factory for future wiring |
| `backend/tests/test_week7_auth.py` | 24 offline tests (synthetic EC P-256 JWTs + mocked JWKS) |
| `requirements.txt` | Added `PyJWT[crypto]>=2.10` |
| `backend/.env.example` | Documented public `SUPABASE_URL` / JWT settings (no secrets) |

**Verification:** 24/24 tests pass; `auth.py` `py_compile` clean. Live read-only JWKS fetch
confirmed the module retrieves the project's ES256 key (`kid 7400369a-…`) and the real
`PyJWKClient` path resolves it, rejecting unsupported algorithms.

**Rejected cases covered by tests:** missing token, malformed token, expired token, not-yet-valid
(`nbf`), invalid signature, wrong issuer, wrong audience, unsupported algorithm (HS256 / `none`),
missing required claim (`exp`/`iat`/`sub`), unknown `kid`. No token or secret is logged.

---

## A. Objective & scope

Give every authenticated DeRexi employee a private **internal messaging** surface, and put the
whole application behind **Supabase Auth** with verified JWTs. When DeRexi cannot confidently
answer a policy question it already routes the request to a policy owner; Week 7 turns that
routing into a **two-way conversation thread** that lives inside an **Inbox / Sent** experience.
Notifications stay **inside DeRexi** — there is no external email delivery.

### In scope
- Supabase Auth (email/password managed by Supabase) with backend JWT verification.
- Internal Messages for **all authenticated users** (employee ↔ employee and employee ↔ policy owner).
- **Reuse of the existing `clarification_requests` / `clarification_replies` tables as the thread
  substrate** (additive columns only — no parallel message system).
- **Inbox** (threads where you are a participant and have unread activity) and **Sent**
  (threads you started).
- Policy-owner replies to clarification threads.
- **Internal notifications** (in-app inbox badge / list) in place of external email.
- Authorization + Row Level Security aligned to thread participation.

### Out of scope (explicitly deferred)
- No external email/SMTP delivery.
- No real-time websockets/presence (poll or refresh-based for Week 7; Realtime is a later enhancement).
- No file attachments.
- No change to retrieval (`/ask`, `pg_trgm`, thresholds, evidence gate) or to existing
  policy-management, dashboard, feedback, or incident workflows beyond adding notification hooks.
- No production database change until this package is approved.

---

## B. Current state (what already exists)

- **Auth today:** none. The backend connects with the direct Postgres/service-role connection
  string; `users` models the *business* user and is deliberately separate from any auth identity
  (see `docs/database-design.md` §4.1 note). The UI selects a persona locally (`derexi.personaId`).
- **Threading today:** `clarification_requests` (header: requester `user_id`, `assigned_to` policy
  owner, `policy_id`, `status`, `reason`) and `clarification_replies` (`sender_id`, `body`).
  Endpoints already exist: `GET/POST /clarifications`, `GET /clarifications/{id}`,
  `POST /clarifications/{id}/replies`, `POST /clarifications/{id}/resolve`.
- **Routing today:** `POST /ask` auto-creates a `clarification_requests` row when retrieval is not
  confident (`main.py` around the `needs_clarification` branch).
- **Dashboard today:** `GET /dashboard/policy-health` already aggregates
  `clarifications_by_status`.

**Implication:** most of the thread data model already exists. Week 7 is primarily (1) auth
linkage + verification, (2) a small additive schema extension, (3) RLS + authorization, and
(4) the Inbox/Sent/notification UI + a few endpoints.

---

## C. Architecture & data flow

```
Supabase Auth (email/password)
        │  issues JWT (sub = auth uuid, email)
        ▼
Browser (DeRexi UI)  ──Bearer JWT──►  FastAPI  ──verify JWT (JWKS or HS256)──►  auth claims
                                        │
                                        ├─ resolve auth uuid → users.id (users.auth_user_id)
                                        ├─ per-request current user (get_current_user)
                                        └─ service-role DB connection (unchanged)

Thread = clarification_requests row (kind='message' | 'clarification')
  └── clarification_replies (ordered messages)
        └── message_reads (per-user read receipts)

Notifications = internal_notifications rows (per recipient), created on thread events
```

- The backend keeps using its **service-role connection** for MVP, exactly as today. JWT
  verification happens in the API layer, and authorization is enforced in endpoint logic.
- RLS is **additionally** tightened so that if/when the browser ever talks to Supabase directly
  (or a future client uses the anon key), participation rules hold at the database layer.

### Auth identity linkage
`users.auth_user_id uuid UNIQUE` maps a Supabase Auth `sub` to a business user. A user with no
`auth_user_id` cannot authenticate (they are a seed/business record only until linked).
Verification + linkage resolution is a single dependency, `get_current_user`, used by all new
messaging endpoints.

### Thread model (reuse, not rebuild)
- **Internal message thread:** `clarification_requests.kind = 'message'` with `subject` set;
  `assigned_to` is the recipient. The first `clarification_replies` row is the opening message.
- **Clarification/routing thread:** `kind = 'clarification'` (default, preserves all existing rows
  and behavior).
- `last_activity_at` is bumped on every new reply so Inbox/Sent can sort without joining replies.

---

## D. Data model changes (additive only)

All changes are **additive**: `ADD COLUMN IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`,
`CREATE INDEX IF NOT EXISTS`, new RLS policies. No column is dropped, no type is narrowed,
no existing row is rewritten except the optional, clearly-marked `last_activity_at` backfill.

1. **`users.auth_user_id uuid UNIQUE`** — link to `auth.users.id`.
2. **`clarification_requests`**: add `kind text NOT NULL DEFAULT 'clarification'` (check:
   `clarification` | `message`), `subject text`, `last_activity_at timestamptz NOT NULL DEFAULT now()`.
3. **`message_reads`** (new) — per-user read receipts: `(reply_id, user_id)` unique, `read_at`.
4. **`internal_notifications`** (new) — recipient-scoped in-app notifications
   (`kind`, `title`, `body`, `link_kind`, `link_id`, `read_at`, `created_at`).
5. **RLS policies** for the new tables plus participant policies for
   `clarification_requests` / `clarification_replies`, backed by helper
   `public.current_user_id()` (maps `auth.uid()` → `users.id`).

Full DDL: `week7_messaging_auth_migration.sql`.

### Backfill (DECIDED — YES)
Seeded `clarification_requests` rows would otherwise default `last_activity_at = now()` at
migration time. Per Kiona's decision, the migration **backfills `last_activity_at` from existing
request/reply timestamps only** — `greatest(request.created_at, max(reply.created_at))`. No new
data is invented and no external timestamps are used.

**Live scope (read-only check):** 33 `clarification_requests`, 1 `clarification_replies`, and
**only 1 thread has a reply**. The backfill therefore changes exactly that one row; the other 32
threads resolve to their own `created_at` and keep their existing ordering. The statement is
idempotent and touches only threads that already have replies.

---

## E. Authorization & RLS model

**Principle:** a user may read a thread only if they are a participant — the requester
(`clarification_requests.user_id`) or the assignee (`assigned_to`) — and may write a reply only
if they are a participant. Notifications and read receipts are strictly self-scoped.

| Actor | Read thread | Post reply | Create thread | Resolve | Notifications |
|---|---|---|---|---|---|
| Requester | yes | yes | yes | close own | own only |
| Assignee (policy owner / recipient) | yes | yes | yes | yes | own only |
| Other authenticated employee | no | no | yes (to any valid recipient) | no | own only |
| System Administrator | oversight read (dashboard) | no | yes | yes | own only |
| Anonymous / no token | no | no | no | no | no |

RLS helpers and policies are in the migration SQL. `current_user_id()` returns the business
`users.id` for the calling `auth.uid()`; the backend service role bypasses RLS as it does today,
so these policies are the enforcement layer for any direct/anon client and a defense-in-depth
backstop for the API.

**Live RLS finding (important).** Every one of the 14 tables currently has exactly one policy,
`<table>_select_authenticated ... FOR SELECT TO authenticated USING (true)`, and **no**
INSERT/UPDATE/DELETE policies at all. RLS permissive policies are **OR-ed**, so *adding* a
participant policy beside the existing `using (true)` one would leave every authenticated user
able to read every thread. The migration therefore **replaces** the permissive SELECT policies on
`clarification_requests` and `clarification_replies` with participant-scoped ones; the rollback
restores the originals verbatim. Policy/catalog/reference tables keep their permissive read
domain exactly as `docs/database-design.md` §7 documents.

### JWT verification (DECIDED — JWKS)
Verified against the **live** project signing configuration (read-only):

| Item | Value |
|---|---|
| JWKS URI | `https://vnumvjamqtuxlctjdzoe.supabase.co/auth/v1/.well-known/jwks.json` |
| Active signing key | **ES256 / P-256**, `use:"sig"`, `key_ops:["verify"]`, `kid 7400369a-63e5-40bf-b6d3-d49e126b0859` |
| Issuer | `https://vnumvjamqtuxlctjdzoe.supabase.co/auth/v1` |
| Audience (logged-in users) | `authenticated` |
| `auth.users` | **0 rows** — no auth users exist yet (unchanged by this package) |

JWKS is **compatible** with this project: the asymmetric key is published and discoverable, so the
backend can verify signature + `exp` + `iss` + `aud` with no shared secret and automatic key
rotation. Recommended implementation: `PyJWT[crypto]` with `PyJWKClient` (caches the JWKS).

Config (env): `SUPABASE_URL`, `SUPABASE_JWKS_URL` (default
`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`), `SUPABASE_JWT_AUD` (default `authenticated`),
`SUPABASE_JWT_ISS` (default `{SUPABASE_URL}/auth/v1`), `JWT_ALGORITHMS` (default `["ES256"]`).
HS256 shared-secret mode is intentionally **not** used.

---

## F. API surface (proposed — not implemented)

All new routes require a valid Bearer JWT via `get_current_user`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/me` | Current authenticated business user (id, name, role, department) |
| `GET` | `/messages` | **Inbox** — threads where I am a participant, newest `last_activity_at` first, with unread count |
| `GET` | `/messages/sent` | **Sent** — threads I created |
| `GET` | `/messages/{thread_id}` | Thread detail: header + ordered replies + per-user read state |
| `POST` | `/messages` | Create an internal thread `{recipient_id, subject, body}` → new `kind='message'` request + opening reply + notification to recipient |
| `POST` | `/messages/{thread_id}/replies` | Post a reply (participant only) → bumps `last_activity_at`, notifies the other participant(s) |
| `POST` | `/messages/{thread_id}/read` | Mark the thread read for the current user (write `message_reads`) |
| `GET` | `/notifications` | My notifications, newest first, unread count |
| `POST` | `/notifications/{id}/read` | Mark one notification read |

Existing clarification routes are retained and become JWT-guarded participant operations:
`GET /clarifications` (scoped to my threads), `GET /clarifications/{id}`,
`POST /clarifications/{id}/replies`, `POST /clarifications/{id}/resolve`.

**Event → notification hooks:** on thread creation, on reply, on assignment, on resolve, and on
incident escalation, insert an `internal_notifications` row for the affected user(s). This is the
internal substitute for email.

---

## G. Frontend

- **Auth:** login/logout against Supabase Auth; store the session token; attach
  `Authorization: Bearer <jwt>` to API calls. Replaces the local persona picker as the source
  of identity (persona picker can remain as an admin/dev affordance).
- **Messages surface:** two tabs — **Inbox** and **Sent** — plus a **thread detail** view
  (subject, participant, ordered replies, reply composer). Threads created by DeRexi routing show
  as `kind='clarification'`; freeform internal messages as `kind='message'`.
- **Notifications:** header bell with unread badge; dropdown list; click routes to the linked
  thread/incident.
- **Styling:** reuse the existing DeRexi editorial tokens in `backend/static/style.css`; no new
  design system.

---

## H. Testing & verification

See `week7_verification_plan.md` for the full matrix. Highlights:
- JWT: valid token accepted; missing/expired/tampered/wrong-`aud` tokens rejected (401).
- Auth linkage: `sub` with no `auth_user_id` → 403; linked user resolves correctly.
- Authorization: non-participant cannot read or reply to a thread (404/403).
- Inbox/Sent: correct scoping, ordering by `last_activity_at`, unread counts.
- Read receipts: marking read writes `message_reads`; unread count drops.
- Notifications: created on the right events, self-scoped, mark-read works.
- RLS: verify participation policies with a non-service-role role after applying.
- Regression: `/ask`, `/policies`, `/feedback`, `/dashboard/policy-health`, and existing
  `/clarifications` behavior unchanged for existing data.

Isolated tests must use a `FakeSession` / `TestClient` `dependency_overrides` pattern (as in
`backend/tests/test_week8_stage1.py`) with **no writes to live Supabase** until approved.

---

## I. Rollout, rollback, risks & open decisions

### Rollout (after approval)
1. Apply `week7_messaging_auth_migration.sql` to Supabase (single additive migration).
2. Enable Supabase Auth; link seeded users via `auth_user_id` (separate, explicit step).
3. Add `get_current_user` (JWKS/ES256 with signature, `exp`, `iss`, `aud` checks) + JWT config to
   the backend; add messaging/notification endpoints.
4. Add Inbox/Sent/notifications UI.
5. Run `week7_verification_plan.md` end to end.

### Rollback
`week7_messaging_auth_rollback.sql` reverses the migration exactly (drops policies, tables,
helpers, columns, constraints, indexes). Because the migration is additive and does not rewrite
policy/message data, rollback is lossless for pre-existing records.

### Risks
- **Auth mode choice** affects config + key handling; mitigate by making verification mode
  pluggable via env (JWKS vs HS256).
- **Reusing clarification tables** reduces new surface but means `kind` must be filtered
  everywhere existing queries assume clarification semantics; mitigated by defaulting
  `kind='clarification'` and filtering explicitly in new endpoints.
- **RLS + service role** — the API bypasses RLS, so endpoint-level authorization is the real
  control; RLS is defense-in-depth. Tests must cover both.
- **No external email** is intentional; confirm stakeholders accept in-app-only notifications.

### Decisions (recorded — design direction approved, execution NOT approved)
1. **JWT verification mode — JWKS.** Confirmed compatible with the live project (ES256/P-256 key
   published at the JWKS URI). See §E.
2. **`last_activity_at` backfill — YES**, from existing request/reply timestamps only. Live scope
   is 1 thread with replies; 32 threads unaffected. See §D.

These decisions approve the **design direction and preparation of the migration scripts**, not
their execution.

### Review findings from live (read-only) verification
- JWKS/ES256 confirmed against the live project (issuer + audience captured above).
- `auth.users` has 0 rows → no auth users exist; **do not create any**.
- All 14 tables have RLS enabled, each with a single permissive `SELECT using (true)` policy and
  **no write policies** → the migration must **replace** (not merely add) the thread-table SELECT
  policies for participant enforcement. Reflected in the SQL and rollback.
- Thread-table indexes and constraints match the design; all Week 7 objects
  (`message_reads`, `internal_notifications`, `current_user_id()`, `users.auth_user_id`) are
  absent, so the forward migration is clean and additive.

### Approval checklist
- [x] Confirm architectural direction (this document)
- [x] Decide JWT mode → **JWKS** (ES256 verified live)
- [x] Decide backfill → **YES** (request/reply timestamps only)
- [ ] Approve applying the forward migration
- [ ] Approve creating/linking Supabase Auth users
- [ ] Authorize implementation of endpoints + UI
