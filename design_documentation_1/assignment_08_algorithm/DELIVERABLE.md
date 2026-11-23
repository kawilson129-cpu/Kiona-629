# Primary Policy-Assistance Algorithm

## Inputs, outputs and grounding

Input is an authenticated policy question through `POST /ask`, optional topic and
legacy user ID (which cannot override the verified actor). Pydantic trims text and
requires a 2–1,000 character question. Normal outputs are JSON guidance with
references/IDs or a saved clarification; an actual-event branch instead returns
immediate incident guidance without automatically creating a report. [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S05 · schemas.py](../../derexi-policy-pilot/backend/schemas.py) [S06 · security.py](../../derexi-policy-pilot/backend/security.py) [S08 · incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py)

Retrieval resolves the current version by `created_at DESC, id DESC` per policy,
keeps approved policies, ranks `0.6 * word_similarity(question, body) +
0.4 * similarity(title, question)` and takes the top three. The top score must be
at least **0.22**, plus substantive keyword/singular evidence in the selected title/
body. This is lexical matching, not vector similarity or a calibrated probability.
The reference is appended even if the optional AI rewrite succeeds. [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S11 · ai.py](../../derexi-policy-pilot/backend/ai.py)

## High-level pseudocode

```text
POLICY_ASSISTANCE(request, submitted_body):
    Framework validates JSON and resolves the verified actor/session.
    Reject missing/invalid credentials, invalid origin or configuration safely.
    Trim question; enforce 2..1000 characters and optional-field limits.
    If legacy body user_id differs from actor.user_id: return 403.
    Load actor's application user; if absent: return 404.
    Classify actual event versus policy/hypothetical question; unsafe input -> 422.
    If potential incident:
        return 200 with immediate guidance and reviewed-intake details.
        Do not create a report or send email in this branch.
    Stage a new conversation and the employee message.
    Query current versions of approved policies, returning the top 3 lexical scores.
    confident = top score >= 0.22 AND substantive keyword/singular evidence exists.
    If confident:
        Build context from rows meeting the threshold.
        Try optional context-grounded AI rewrite.
        If key missing, provider fails or text is empty: use deterministic guidance.
        Append top policy title/version reference.
        Save answer and citations; COMMIT; return 200 with IDs and score.
    Else:
        Choose top candidate policy/owner if available; otherwise unassigned triage.
        Save honest uncertainty answer, clarification and requester read watermark.
        COMMIT; return 200 with clarification/triage state and IDs.
    On handled validation/access errors: return the defined safe HTTP error.
    On unhandled/database error: middleware returns generic 500 + request ID.
    Close the request session; uncommitted work is discarded.
    Do not infer a failed commit acknowledgement means no records were saved.
```

Authentication/body validation are FastAPI/dependency responsibilities before the
handler's business work; the diagram is conceptual and does not assert an exact
ordering of simultaneous framework validation failures. Missing configuration can
fail safely as unavailable rather than creating a fallback identity.

## Decisions and exception behavior

- Missing/invalid identity: 401; identity/origin/access mismatch: 403; missing user: 404.
- Invalid/unsafe submitted data: safe 422. Do not echo credentials or rejected bodies.
- AI unavailable: use the existing deterministic approved-policy guidance, **not**
  a successful provider claim and not an invented answer.
- No evidence/confidence: save uncertainty and route to a candidate owner or triage.
  A negative answer rating is a separate saved-feedback operation, not auto-email.
- Database/unhandled failure: generic 500 with request ID; no success banner.
  Uncommitted work closes with the request session; unknown commit outcomes need
  reconciliation. `/ask` itself does not implement the support dispatch idempotency
  mechanism, so blind retries can create duplicate conversations.

These decisions describe actual source. Retained H07–H12 verify the isolated
clarification/error path, not real pg_trgm answer ranking or live AI output.
No algorithm was implemented or executed anew for this documentation. [S04 · main.py](../../derexi-policy-pilot/backend/main.py) [S10 · database.py](../../derexi-policy-pilot/backend/database.py) [S28 · http-results.json](../../ai_api_intergration_1/AAI%201%20Assignment%201/evidence/20261118-api/http-results.json)

[Standalone pseudocode](policy-assistance-pseudocode.txt).

---

**Document review:** 2026-11-23. [Master design](../assignment_01_design_document/DELIVERABLE.md) · [Evidence map](../EVIDENCE_MAP.md).
