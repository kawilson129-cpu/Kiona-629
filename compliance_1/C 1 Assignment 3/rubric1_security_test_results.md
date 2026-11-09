# Rubric 1 — Security Control Test Results (C-01, C-02)

**Project:** DeRexi: Policy Pilot — Aurum Capital Bank
**Controls under test:** C-01 Role-Based Access Control · C-02 Input Validation and Safe Error Handling
**Test date:** 3 November 2026
**Commit tested:** `5d1112a` (branch `main`)
**Result:** C-01 **unverified** (15 of 15 checks failed) · C-02 **partially verified** (16 passed, 10 failed)

---

## 1. Environment and safety

| Item | Value |
| --- | --- |
| Host | macOS 26.3.1 (arm64), local development machine |
| Python | 3.9.6 (`derexi-policy-pilot/.venv`) |
| FastAPI | 0.128.8 |
| Pydantic | 2.13.5 |
| SQLAlchemy | 2.0.54 |
| HTTP client | httpx 0.28.1 (FastAPI `TestClient`) |
| Backend entry point | `derexi-policy-pilot/backend/main.py` |
| Live Supabase data touched | **None** |

### How isolation was enforced

The suite was written so that it cannot reach the live Supabase/Postgres database even by
mistake:

1. **Dependency override** — every check installs its own in-memory `FakeSession` as the
   `get_db` dependency. Reads come from synthetic objects created in the test file; writes are
   appended to an in-memory list. The real route handlers, Pydantic validation, and response
   serialization all execute exactly as they do in production.
2. **Connection tripwire** — `sqlalchemy.engine.Engine.connect` is replaced with a function that
   raises `RuntimeError("Live database access attempted during an isolated test")` *before* the
   application module is imported. Any code path that tried to open a real connection would fail
   loudly rather than read or write.
3. **Synthetic identities** — all users are generated in-process with `@example.invalid` email
   addresses. No production user, incident, policy, message, or feedback record was read,
   created, modified, or deleted.
4. **No schema or permission changes** — no migration was run, no RLS policy was altered, no role
   or grant was changed, and the seeded Supabase project was not contacted.

Because the fake session stores objects instead of issuing SQL, this suite verifies
*application-layer* behaviour. Database-level constraints (foreign keys, `NOT NULL`, column
length limits, RLS) are **not** exercised — see §6 Limitations.

### Database permissions and role definitions (inspected)

| Layer | Observation |
| --- | --- |
| Role definitions | `roles` table with three rows: Employee, Policy Owner, System Administrator; `users.role_id` is a non-null FK (`models.py` lines 42–60) |
| Where role data is used | `main.py` reads `users.role_id` in only two places: to display `role`/`role_id` in `GET /users` (lines 264–265) and to pick a default clarification assignee in `/ask` (lines 490–501). It never authorizes a caller |
| Database permissions | `database.py` connects with the project's direct/service-role `DATABASE_URL` and states that Row Level Security therefore does not block backend operations. Any RLS policy on Supabase is bypassed by the API, so DB grants cannot act as a second enforcement layer for these routes |
| Backend authorization | None — `main.py` contains no `Depends` other than `Depends(get_db)`, and `auth.py` is documented as "not imported by the running application" |

---

## 2. Exact commands and file paths

Test file (new, non-destructive):

```
derexi-policy-pilot/backend/tests/test_security_controls.py
```

Executed from `derexi-policy-pilot/backend`:

```bash
cd derexi-policy-pilot/backend
../.venv/bin/python tests/test_security_controls.py
```

The same file also runs as `python tests/test_security_controls.py` when the virtual environment
is already active. It exits non-zero when any check fails (expected while the gaps below remain
open) and rewrites its JSON evidence on every run.

Supporting evidence files:

| File | Contents |
| --- | --- |
| `docs/compliance/evidence/security_controls_run.txt` | Full sanitized console output of the run |
| `docs/compliance/evidence/security_controls_results.json` | Machine-readable results plus an appendix: route inventory, CORS configuration, OpenAPI security schemes, and declared schema length limits |

Supporting (blocked) check:

```bash
cd derexi-policy-pilot/backend
../.venv/bin/python tests/test_week7_auth.py
# ModuleNotFoundError: No module named 'jwt'
```

`PyJWT` is not installed in the project virtual environment. Installing a package is a dependency
change, so it was not done without approval; the JWT verifier's own correctness therefore remains
**BLOCKED** and is not counted in the results table.

---

## 3. Results

41 checks were executed: 15 for C-01 and 26 for C-02. Statuses reflect the behaviour the control
*requires*, so a FAIL is a gap in the application, not a broken test.

**Totals:** 16 PASS · 25 FAIL · 0 BLOCKED · 0 runner errors.

| Test ID | Control | Test Scenario | Expected Result | Actual Result | Status | Evidence Path |
| --- | --- | --- | --- | --- | --- | --- |
| C01-01 | C-01 | Every API route declares an identity/role dependency | 0 routes without an authorization dependency | 22 route(s) unprotected: GET /departments, GET /roles, GET /categories, GET /users, GET /policies, GET /policies/search, GET /policies/{policy_id}, POST /policies, POST /policies/{policy_id}/versions, POST /ask, GET /conversations/{conversation_id}, GET /clarifications, POST /clarifications, GET /clarifications/{request_id}, POST /clarifications/{request_id}/replies, POST /clarifications/{request_id}/resolve, GET /incident-categories, GET /incidents, POST /incidents, PATCH /incidents/{incident_id}, POST /feedback, GET /dashboard/policy-health | **FAIL** | `tests/test_security_controls.py::test_c01_01_no_authorization_dependencies` |
| C01-02 | C-01 | Auth foundation (auth.py) is imported and used by main.py | main.py imports and enforces auth | main.py has no import of auth.py; the verifier is unwired | **FAIL** | `tests/test_security_controls.py::test_c01_02_auth_module_not_wired` |
| C01-03 | C-01 | Anonymous GET /users is denied | 401/403 and no user data | HTTP 200; returned 1 user record(s) including email addresses | **FAIL** | `tests/test_security_controls.py::test_c01_03_anonymous_user_directory` |
| C01-04 | C-01 | Anonymous GET /incidents is denied | 401/403 and no incident data | HTTP 200; incident description exposed | **FAIL** | `tests/test_security_controls.py::test_c01_04_anonymous_incidents` |
| C01-05 | C-01 | Anonymous GET /clarifications is denied | 401/403 and no thread data | HTTP 200; 1 thread(s) returned | **FAIL** | `tests/test_security_controls.py::test_c01_05_anonymous_clarifications` |
| C01-06 | C-01 | User 9 cannot read user 8's conversation | 401/403 for a non-owner | HTTP 200 (no ownership check; header ignored) | **FAIL** | `tests/test_security_controls.py::test_c01_06_cross_user_conversation_read` |
| C01-07 | C-01 | Employee cannot change incident status/severity | 401/403 for the Employee role | HTTP 200; incident modified by Employee | **FAIL** | `tests/test_security_controls.py::test_c01_07_employee_cannot_edit_incident` |
| C01-08 | C-01 | Employee cannot create or approve a policy | 401/403 before any write | HTTP 201; in-memory fake recorded 2 insert(s), 1 commit(s) | **FAIL** | `tests/test_security_controls.py::test_c01_08_employee_cannot_create_policy` |
| C01-09 | C-01 | Employee cannot publish a new policy version | 401/403 for the Employee role | HTTP 201 | **FAIL** | `tests/test_security_controls.py::test_c01_09_employee_cannot_add_policy_version` |
| C01-10 | C-01 | Anonymous caller cannot resolve a clarification thread | 401/403 for a non-participant | HTTP 200; in-memory thread status now 'resolved' | **FAIL** | `tests/test_security_controls.py::test_c01_10_anonymous_can_resolve_thread` |
| C01-11 | C-01 | A non-participant cannot post into a clarification thread | 401/403 for sender outside {requester, assignee} | HTTP 201; in-memory reply recorded=True | **FAIL** | `tests/test_security_controls.py::test_c01_11_identity_spoofing_on_reply` |
| C01-12 | C-01 | Anonymous GET /dashboard/policy-health is denied | 401/403 for a compliance/admin view | HTTP 200 | **FAIL** | `tests/test_security_controls.py::test_c01_12_anonymous_dashboard` |
| C01-13 | C-01 | Actor identity comes from a verified credential, not the request body | 401/403 when body identity conflicts with the caller | HTTP 201; 1 in-memory insert(s) attributed to user_id=9 | **FAIL** | `tests/test_security_controls.py::test_c01_13_identity_is_client_supplied` |
| C01-14 | C-01 | Employee and System Administrator receive different authority | Employee denied where admin is allowed (403 vs 200) | Employee HTTP 200, System Administrator HTTP 200 (identical responses) | **FAIL** | `tests/test_security_controls.py::test_c01_14_roles_are_cosmetic` |
| C01-15 | C-01 | OpenAPI contract declares an authentication scheme | at least one security scheme (e.g. bearerAuth) | declared schemes: none | **FAIL** | `tests/test_security_controls.py::test_c01_15_no_security_scheme_declared` |
| C02-01 | C-02 | Malformed /ask payloads are rejected with 422 | all 8 malformed payloads return 422 | all rejected | **PASS** | `tests/test_security_controls.py::test_c02_01_question_validation` |
| C02-02 | C-02 | Rejected /ask payloads create no records | 0 in-memory inserts | 0 insert(s), 0 commit(s) | **PASS** | `tests/test_security_controls.py::test_c02_01_question_validation` |
| C02-03 | C-02 | Unknown /ask fields are ignored, not applied | request accepted without granting admin fields | HTTP 200; response keys=['answer', 'assigned_to', 'citations', 'clarification_request_id', 'confidence', 'conversation_id', 'derexi_message_id', 'needs_clarification'] | **PASS** | `tests/test_security_controls.py::test_c02_03_ask_extra_field_ignored` |
| C02-04 | C-02 | Unknown user is rejected without creating a conversation | 404/401 with no records | HTTP 404, detail='User not found', inserts=0 | **PASS** | `tests/test_security_controls.py::test_c02_04_ask_unknown_user_is_generic` |
| C02-05 | C-02 | Malformed /feedback payloads are rejected with 422 | all 5 malformed payloads return 422 | all rejected | **PASS** | `tests/test_security_controls.py::test_c02_05_feedback_validation` |
| C02-06 | C-02 | Rejected /feedback payloads create no records | 0 in-memory inserts | 0 insert(s) | **PASS** | `tests/test_security_controls.py::test_c02_05_feedback_validation` |
| C02-07 | C-02 | Feedback for a missing message is refused | 404 and no record | HTTP 404, inserts=0 | **PASS** | `tests/test_security_controls.py::test_c02_05_feedback_validation` |
| C02-08 | C-02 | Overlong feedback comment is rejected | 422 for a 50,000-character comment | HTTP 201; 50,000 characters accepted and stored in the fake session | **FAIL** | `tests/test_security_controls.py::test_c02_08_feedback_comment_unbounded` |
| C02-09 | C-02 | Malformed /incidents payloads are rejected with 422 | all 6 malformed payloads return 422 | all rejected | **PASS** | `tests/test_security_controls.py::test_c02_09_incident_validation` |
| C02-10 | C-02 | Rejected /incidents payloads create no records | 0 in-memory inserts | 0 insert(s) | **PASS** | `tests/test_security_controls.py::test_c02_09_incident_validation` |
| C02-11 | C-02 | Overlong incident description is rejected | 422 for a 50,000-character description | HTTP 201; 50,000 characters accepted and stored in the fake session | **FAIL** | `tests/test_security_controls.py::test_c02_12_incident_description_unbounded` |
| C02-12 | C-02 | Malformed replies are rejected with 422 | all 5 malformed payloads return 422 | all rejected | **PASS** | `tests/test_security_controls.py::test_c02_13_reply_validation` |
| C02-13 | C-02 | Rejected replies create no records | 0 in-memory inserts | 0 insert(s) | **PASS** | `tests/test_security_controls.py::test_c02_13_reply_validation` |
| C02-14 | C-02 | Malformed /policies payloads are rejected with 422 | all 4 malformed payloads return 422 | all rejected | **PASS** | `tests/test_security_controls.py::test_c02_16_policy_payload_validation` |
| C02-15 | C-02 | Rejected policy payloads create no records | 0 in-memory inserts | 0 insert(s) | **PASS** | `tests/test_security_controls.py::test_c02_16_policy_payload_validation` |
| C02-16 | C-02 | Overlong policy title is rejected | 422 for a 100,000-character title | HTTP 201; 100,000 characters accepted and stored in the fake session | **FAIL** | `tests/test_security_controls.py::test_c02_19_policy_title_unbounded` |
| C02-17 | C-02 | Incident assignment to a nonexistent user is rejected | 400/404/422 and no change | HTTP 200; in-memory assigned_to=987654 | **FAIL** | `tests/test_security_controls.py::test_c02_20_incident_assignment_unchecked` |
| C02-18 | C-02 | Error responses contain no stack traces, SQL, or credentials | 0 internal details in 6 error responses | statuses 404,404,404,404,404,404; no internal details | **PASS** | `tests/test_security_controls.py::test_c02_21_error_bodies_are_safe` |
| C02-19 | C-02 | Not-found errors use short, employee-readable text | a plain-language detail string | HTTP 404, detail='Policy not found' | **PASS** | `tests/test_security_controls.py::test_c02_22_error_messages_are_human` |
| C02-20 | C-02 | Unhandled database failure does not leak internals | HTTP 500 with no traceback, SQL, or connection string | HTTP 500, leak markers=none, body='Internal Server Error' | **PASS** | `tests/test_security_controls.py::test_c02_23_unhandled_database_error_is_safe` |
| C02-21 | C-02 | Unhandled failure gives the employee an actionable message | a plain-language apology/retry message | HTTP 500, body='Internal Server Error' | **FAIL** | `tests/test_security_controls.py::test_c02_23_unhandled_database_error_is_safe` |
| C02-22 | C-02 | Non-boolean rating values are rejected | 422 for rating='yes' | HTTP 201; rating coerced and stored=True | **FAIL** | `tests/test_security_controls.py::test_c02_25_feedback_rating_coercion` |
| C02-23 | C-02 | Every free-text field declares an upper bound | 0 unbounded free-text fields | unbounded: FeedbackCreate.comment, IncidentCreate.description, IncidentUpdate.resolution_notes, PolicyCreate.title, PolicyCreate.summary, PolicyVersionCreate.title, PolicyVersionCreate.body, PolicyVersionAdd.body, PolicyVersionAdd.title | **FAIL** | `tests/test_security_controls.py::test_c02_26_schema_field_limits` |
| C02-24 | C-02 | Empty policy title and body are rejected | 422 for empty title and empty version body | HTTP 201; empty policy accepted and stored in the fake session | **FAIL** | `tests/test_security_controls.py::test_c02_24_empty_policy_fields` |
| C02-25 | C-02 | Clarification for nonexistent message/conversation/policy is rejected | 400/404/422 and no record | HTTP 201; 1 in-memory insert(s) with dangling foreign keys | **FAIL** | `tests/test_security_controls.py::test_c02_25_orphan_clarification` |
| C02-26 | C-02 | Feedback from a nonexistent user is rejected | 404 and no record | HTTP 201; 1 in-memory insert(s) referencing a missing user | **FAIL** | `tests/test_security_controls.py::test_c02_26_feedback_unknown_user` |
### Appendix recorded by the suite

| Property | Observed value |
| --- | --- |
| API routes with a request handler | 26 |
| Data-bearing routes reachable without credentials | 22 |
| Public-by-design routes excluded | `GET /`, `GET /health`, `GET /api/pulse*`, `/ui`, `/docs`, `/redoc`, `/openapi.json` |
| Routes declaring an identity/role dependency | 0 |
| Times `auth.py` is imported by `main.py` | 0 |
| OpenAPI `components.securitySchemes` | none |
| CORS `allow_origins` | `http://127.0.0.1:8000`, `http://localhost:8000` |
| CORS `allow_credentials` / `allow_methods` | `true` / `GET, POST, PATCH` |

---

## 4. Findings, severity, and recommended remediation

No fixes were implemented. Everything below is a recommendation awaiting approval.

### F-01 (Critical) — No authentication or authorization on any data endpoint

*Evidence: C01-01, C01-02, C01-03, C01-04, C01-05, C01-12*

`main.py` declares 24 route handlers, none of which takes an identity or permission dependency;
the only dependency anywhere is `Depends(get_db)`. `auth.py` contains a complete, well-documented
Supabase JWT verifier but states it is "not imported by the running application", and the test
confirms `main.py` never imports it. `GET /users` (returns names, emails, roles), `GET /incidents`,
`GET /clarifications`, and `GET /dashboard/policy-health` all answered **HTTP 200** to a request
carrying no credentials and no headers at all.

**Remediation:** add a single `get_current_user` dependency built on `auth.py`'s
`SupabaseJWTVerifier` and apply it to every non-public route; return `401` for a missing/invalid
token. Declare the bearer scheme in OpenAPI so `/docs` stops advertising anonymous endpoints.

### F-02 (Critical) — Roles exist in the data model but never gate a request

*Evidence: C01-07, C01-08, C01-09, C01-14*

`User.role_id` → `roles` is populated and the UI labels users Employee / Policy Owner / System
Administrator (`static/app.js` lines 52, 241–244), but no server code reads it. An Employee-role
caller received exactly the same response as a System Administrator (both `200`), created a policy
in `approved` status (`201`, two inserts recorded), published version `2.0` of a live policy
(`201`), and changed an incident's status to `resolved` (`200`).

**Remediation:** add a `require_roles(...)` dependency (e.g. policy create/version =
Policy Owner or System Administrator; incident update = System Administrator or the assigned SOC
analyst; dashboard = Policy Owner or System Administrator) and return `403` on mismatch. Enforce
the same rules in the UI for usability, but treat the server as the only control.

### F-03 (High) — Identity is supplied by the caller, enabling impersonation (IDOR)

*Evidence: C01-06, C01-10, C01-11, C01-13*

There is no credential to compare against, so actor identity is read from the request body
(`user_id`, `sender_id`, `reporter_id`, `assigned_to`). A caller who posted
`{"user_id": 9}` created a clarification attributed to user 9; a non-participant posted a reply
into another user's thread (`201`); and any caller could resolve any thread, because
`POST /clarifications/{id}/resolve` takes no identity at all. `GET /conversations/{id}` returned
another user's conversation to an unrelated caller (`200`) since ownership is never compared.

**Remediation:** derive the actor from the verified token's `sub` claim and ignore body-supplied
identity (or reject payloads whose `user_id` disagrees with the token). Add ownership/participant
checks before reading a conversation, posting a reply, or resolving a thread; return `403`/`404`
rather than leaking existence.

### F-04 (High) — Personal and incident data exposed to anonymous callers

*Evidence: C01-03, C01-04, C01-05, C01-12*

`GET /users` returned staff email addresses with no credentials (GLBA Safeguards Rule / Reg P
concern for non-public personal information). `GET /incidents` returned incident descriptions and
`/dashboard/policy-health` returned aggregate compliance data anonymously.

**Remediation:** covered by F-01 and F-02; additionally restrict the user directory to
System Administrator, and return only the fields the calling screen needs (no emails) for any
wider audience.

### F-05 (Medium) — Nine free-text fields accept unbounded input

*Evidence: C02-08, C02-11, C02-16, C02-23*

`FeedbackCreate.comment`, `IncidentCreate.description`, `IncidentUpdate.resolution_notes`,
`PolicyCreate.title`, `PolicyCreate.summary`, `PolicyVersionCreate.title`,
`PolicyVersionCreate.body`, `PolicyVersionAdd.title`, `PolicyVersionAdd.body` declare no
`max_length`. 50,000-character incident and feedback payloads and a 100,000-character policy title
were accepted with `201`.

**Remediation:** declare explicit bounds in `schemas.py` (for example `Field(min_length=2,
max_length=4000)` for descriptions, `max_length=200` for titles) and mirror the same limits in the
database columns. Note `ClarificationReplyCreate.body` already has the correct pattern
(`min_length=1, max_length=2000`) and can serve as the template.

### F-06 (Medium) — Empty policy title and body are accepted and stored

*Evidence: C02-24*

`POST /policies` with `title: ""` and `version.body: ""` returned `201` and committed two rows.
`PolicyCreate.title` and `PolicyVersionCreate.body` have neither `min_length` nor a strip
constraint, so an empty, apparently approved policy can enter the library.

**Remediation:** apply `Field(min_length=1)` (ideally with whitespace stripping and a 2–3
character minimum) to both fields and reject whitespace-only values after trimming.

### F-07 (Medium) — Boolean rating accepts arbitrary strings

*Evidence: C02-22*

`FeedbackCreate.rating: bool` coerced `"yes"` to `True` and stored a feedback row (`201`).
Pydantic's lenient bool parsing also accepts `"no"`, `"on"`, `"0"`, etc., so rating analytics can
be polluted by malformed client payloads.

**Remediation:** use `StrictBool` (or an explicit `Literal[True, False]`) so only real booleans are
accepted; return `422` otherwise.

### F-08 (Medium) — Related records are not checked before a write

*Evidence: C02-17, C02-25, C02-26*

`PATCH /incidents/{id}` stored `assigned_to=987654` for a user that does not exist (`200`), and
`POST /clarifications` stored `message_id`, `conversation_id`, and `policy_id` values that
reference nothing (`201`). `POST /feedback` accepted a `user_id` that does not exist (`201`).

In the isolated harness these become dangling references. Against the real database the same
payloads are expected to hit foreign-key constraints and surface as an unhandled
`IntegrityError` → generic `500` instead of a `4xx` explaining the problem. That DB-level
consequence is inferred from `models.py`/`schemas.py`, not observed (see §6).

**Remediation:** validate each referenced id with `db.get(...)` before inserting or updating
(the handlers already do this for `message_id` on feedback and `policy_id` on versions), and add a
JSON exception handler that converts `IntegrityError` into a `409`/`422` with a plain-language
message.

### F-09 (Low) — Unhandled failures are safe but not actionable

*Evidence: C02-20, C02-21*

A simulated database outage produced `HTTP 500` with the body `Internal Server Error`: no
traceback, SQL, DSN, or credential leaked (good), but nothing a bank employee could act on.

**Remediation:** add a global exception handler returning a small JSON envelope such as
`{"error": "temporary_failure", "message": "Something went wrong on our side. Please try again, or contact the IT Help Desk if it continues.", "request_id": "..."}`
and log the technical detail server-side only.

### Controls that behaved correctly

* Schema validation rejects wrong types, missing fields, invalid enums, and blank/short values on
  `/ask`, `/feedback`, `/incidents`, clarification replies, and `/policies` (`C02-01`, `C02-05`,
  `C02-09`, `C02-12`, `C02-14`).
* Rejected payloads created **zero** records in every validator test (`C02-02`, `C02-06`,
  `C02-10`, `C02-13`, `C02-15`) — validation fails before any write is attempted.
* Error bodies contained no stack traces, SQL statements, connection strings, or file paths across
  six 404 paths (`C02-18`), and 404 messages were short and readable (`C02-19`, e.g.
  `Policy not found`).
* Unknown extra JSON fields (`is_admin`, `role`) were accepted by the model but had no effect and
  appeared in no response (`C02-03`) — they grant no authority.
* An unknown user on `/ask` was rejected with `404` and produced no conversation (`C02-04`).
* CORS is restricted to two localhost origins, so a hostile web page cannot read API responses
  from a browser in the default configuration.

---

## 5. Verification verdict

### C-01 Role-Based Access Control — **UNVERIFIED**

The role *data model* exists (Employee, Policy Owner, System Administrator) but there is no
server-side enforcement to verify: 15 of 15 checks failed, no route declares an identity or role
dependency, `auth.py` is unwired, and the API contract declares no authentication scheme.
Authorized and unauthorized callers are currently indistinguishable to the backend. Any role
behaviour observed in the UI is client-side only (`static/app.js`) and is bypassed by calling the
API directly, which is exactly what these tests did.

### C-02 Input Validation and Safe Error Handling — **PARTIALLY VERIFIED**

Field-level type, presence, enum, and minimum-length validation is genuinely implemented and
working: 16 of 26 checks passed, and the error-handling posture is good — no internal detail
leaked in any tested failure path, and error text is brief and employee-readable. The partial
verdict comes from ten failures concentrated in three areas: missing upper bounds on free-text
fields, missing semantic checks (empty policy content, lenient boolean coercion, unchecked foreign
keys), and a 500 handler that is safe but not actionable.

No code fix should be merged before the critical C-01 gaps are addressed, because validation
hardening alone does not stop an anonymous caller from writing to the policy library.

---

## 6. Testing limitations

1. **Fake session, not Postgres.** Because writes are captured in memory, database constraints
   (foreign keys, `NOT NULL`, `varchar`/`text` limits, RLS) were never executed. Findings F-06,
   F-08, and the "500 instead of 4xx" consequence are based on reading `models.py`, `main.py`, and
   the live schema design; reproducing them against a real database is a separate, approved step.
2. **RLS was not exercised.** `database.py` connects with the project's direct/service-role
   connection string and documents that RLS therefore does not block backend operations. Any RLS
   protection on Supabase would not cover requests arriving through this API, so RLS policies were
   out of scope for a non-destructive test.
3. **JWT verifier proof is BLOCKED.** `tests/test_week7_auth.py` fails at import with
   `ModuleNotFoundError: No module named 'jwt'`. Installing `PyJWT` into the project virtual
   environment is a dependency change, so it was not done without approval. The verifier's own
   signature/claim handling is therefore untested, though its unused status is proven.
4. **No live tokens.** No Supabase user was created and no JWT was issued; all role scenarios
   carried synthetic headers that the backend ignores. This is sufficient to prove the absence of
   enforcement but cannot show how the API behaves *after* authentication is added.
5. **UI gating read, not driven.** Client-side role logic in `static/app.js` was inspected in
   source, not exercised in a browser; no browser automation was run.
6. **Messaging surface approximated.** There is no `/messages` endpoint. In-app messaging is
   implemented as `/clarifications` plus `/clarifications/{id}/replies` and `.../resolve`, which is
   what was tested.
7. **No load, fuzz, or penetration testing.** Payload sizes were chosen to prove the absence of
   limits, not to measure throughput or resource exhaustion; no scanner or brute-force tooling was
   used.

---

## 7. Files created or changed

| Path | Change |
| --- | --- |
| `derexi-policy-pilot/backend/tests/test_security_controls.py` | **New.** Isolated C-01/C-02 suite (41 checks, in-memory session, engine tripwire, writes JSON evidence). |
| `docs/compliance/rubric1_security_test_results.md` | **New.** This report. |
| `docs/compliance/evidence/security_controls_run.txt` | **New.** Sanitized console output of the executed run. |
| `docs/compliance/evidence/security_controls_results.json` | **New.** Machine-readable results plus route/CORS/OpenAPI/schema appendix. |

No application code, schema, migration, RLS policy, role, or production record was modified. No
commit was created and nothing was pushed to GitHub.
