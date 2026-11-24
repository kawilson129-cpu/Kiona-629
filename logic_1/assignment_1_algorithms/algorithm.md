# Policy question to guidance or accountable clarification

This is a newly documented algorithm extracted from the existing `POST /ask`
workflow. It reuses the earlier Design Documentation algorithm and checks it against
the current source; it is not a newly implemented endpoint.

## Inputs and outputs

**Inputs:** JSON question (2–1,000 characters), optional topic/legacy user ID,
request credentials/session, authenticated actor and existing policy database.
The actor comes from verified identity, not a body-supplied role or ID.

**Outputs:** a 200 guidance response with citations/IDs; a 200 saved clarification
with `needs_clarification=true` and `triage` based on missing assignment; a 200
incident-guidance response without an automatic report/email; or a safe HTTP error.

## Numbered algorithm

1. Receive the request. FastAPI/dependencies validate the schema and resolve the
   authenticated identity. Reject invalid input, identity or configuration safely.
2. Compare the optional legacy user ID with the verified actor. If it is supplied
   **AND** differs, return 403; otherwise continue with the actor's ID.
3. Load that application user. If absent, return 404. Trim the question; if blank,
   return 422. Do not create a substitute identity.
4. Protect and classify the text. Unsafe content returns 422. If a potential
   incident is detected, return the existing incident guidance immediately; the
   normal policy path ends without creating a report or sending email.
5. For a policy question, stage a conversation and the user's message in the
   request's database session.
6. Query the three highest-scoring **approved current policy versions**. Current
   version selection uses `created_at DESC, id DESC`; ranking uses the existing
   weighted PostgreSQL `word_similarity`/`similarity` expression.
7. Set the first confidence gate to `bool(results) AND top_score >= 0.22`.
   False goes to the clarification branch at step 11.
8. If the first gate passes, derive substantive keywords, then require both a
   nonempty keyword list **AND** `contains_keyword` evidence in the top title/body.
   False also goes to step 11. This lexical threshold is not calibrated probability.
9. **Confident branch:** build context from qualifying rows and try the optional AI
   rewrite. If it returns usable text, use it; otherwise use deterministic guidance.
   Missing configuration/provider failure must not become an invented AI success.
10. Append the policy reference, save the assistant message and qualifying citations,
    commit, and return 200 with `needs_clarification=false`. This branch ends.
11. **Clarification branch:** if a top candidate exists, look up its policy owner.
    If no owner is available, keep the assignee empty for administrator triage.
12. Save an honest uncertainty answer, clarification request and requester read
    watermark; commit. Return 200 with clarification/record IDs and
    `triage = (assignee is None)`. This branch ends.
13. For handled errors return the defined safe status. An unhandled database or
    other failure reaches middleware's generic 500 with a request ID; no successful
    save/import/delivery claim is made.
14. On request-session cleanup, close the session through `get_db`'s `finally`.
    Uncommitted work is discarded. An ambiguous commit acknowledgement does not
    prove no record was saved; ordinary `/ask` retries are not idempotent.

Framework validation/dependency ordering is conceptual here; the algorithm does not
promise which simultaneous validation/authentication error is reported first.
Steps 13–14 apply to the relevant error/resource lifecycle, including early returns.

## Source mapping

| Steps | Existing source responsibility |
|---|---|
| 1–3 | `schemas.AskRequest`, `security.get_identity`, first guards in `main.ask` |
| 4 | `incident_assistance.protect/classify`, incident early return in `main.ask` |
| 5–8 | Conversation staging, `SEARCH_SQL`, confidence gates, `substantive_keywords`, `contains_keyword` |
| 9–10 | `ai.generate_answer` call/fallback, guidance/reference and citation persistence |
| 11–12 | Policy-owner lookup, clarification/read-watermark persistence, triage response |
| 13–14 | `main.add_security_headers`, `database.get_db` |

Exact paths/line ranges and actual test scope: [evidence.md](evidence.md).
The [A2 diagram](../assignment_2_flowcharts/policy-assistance.mmd) visualizes these
same branches. Negative answer feedback is a separate rating operation; it does
not automatically email an owner or open this clarification branch.
