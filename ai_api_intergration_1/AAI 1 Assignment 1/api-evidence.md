# Structured API evidence

## Assignment 1 finalization — November 19, 2026

The [new two-page report](AI_API_Integration_1_Rubric_01_Report.pdf) packages these
existing exchanges. **No API transaction below was rerun for finalization.**
The 200 GET/POST results are from November 18 automated HTTP/browser verification.
The separate H02 401 result proves rejection of absent credentials; it does not
prove successful retrieval or submission. User-referenced Swagger 401 images were
not located in available files, so no Swagger screenshot is claimed or fabricated.
[Finalization index](evidence/finalization-20261119/README.md).

Captured November 18, 2026 using actual loopback socket requests to the existing
DeRexi FastAPI application. Synthetic in-memory SQLite, existing development
bearer authentication and actual RBAC; PostgreSQL ranking is MOCKED to no matches.
External AI is DISABLED. These are not production/Supabase verification results.

Full sanitized [HTTP transcripts](evidence/20261118-api/http-results.json) and
[original frontend network responses](evidence/20261118-api/browser-results.json)
include method, full URL, relevant headers, JSON body, response and status code.
Headers shown are relevant selections, not every transport-generated header.
Authorization tokens are redacted; they are never included in screenshots.

## GET policy resources — rubric 1, 2, 3 and 4

- Method: `GET`
- URL: `http://127.0.0.1:8041/policies`
- Headers: `Accept: application/json`; `Authorization: Bearer [REDACTED]`
- Request body: none
- Actual response: **200 OK**, `Content-Type: application/json`, `Cache-Control: no-store`
- Entire captured response body (fictional fixture records):

```json
[
  {
    "id": 1,
    "title": "Unrelated fixture policy",
    "summary": null,
    "status": "approved",
    "category_id": null,
    "category": null,
    "owner_id": 12,
    "owner": "Rachel Sampson",
    "latest_version": "1.0",
    "review_date": null,
    "requires_review": false,
    "created_at": "2026-11-18T18:05:44.147108",
    "updated_at": "2026-11-18T18:05:44.147116"
  },
  {
    "id": 48,
    "title": "Employee Leave",
    "summary": null,
    "status": "approved",
    "category_id": null,
    "category": null,
    "owner_id": 9,
    "owner": "Jordan Rivera",
    "latest_version": "1.0",
    "review_date": null,
    "requires_review": false,
    "created_at": "2026-11-18T18:05:44.147121",
    "updated_at": "2026-11-18T18:05:44.147126"
  }
]
```

The original Library renders `title`, `owner`, `latest_version` and `status` as
readable rows rather than raw JSON. [Actual screenshot](evidence/20261118-api/screenshots/01-get-library.png).
The fixture has no categories, so its category count is zero even though two
uncategorized policy rows render; no live bank content is shown.

## POST a question — rubric 1, 2, 3 and 4

- Method: `POST`
- URL: `http://127.0.0.1:8041/ask`
- Headers: `Accept: application/json`; `Content-Type: application/json`;
  `Authorization: Bearer [REDACTED]`
- Actual request body:

```json
{
  "question": "How should I handle a hypothetical policy exception?"
}
```

- Actual response: **200 OK**, `Content-Type: application/json`, `Cache-Control: no-store`
- Entire captured response body:

```json
{
  "conversation_id": 1,
  "user_message_id": 1,
  "derexi_message_id": 2,
  "answer": "The policy library does not contain enough information to answer this confidently, so I have routed it to a policy owner for clarification rather than guess.",
  "citations": [],
  "needs_clarification": true,
  "clarification_request_id": 1,
  "assigned_to": null,
  "triage": true,
  "confidence": 0.0
}
```

The observed clarification branch of POST `/ask` processes a submitted question, creates a conversation/messages and
clarification resource, then returns guidance and their identifiers. Its existing
contract uses 200 rather than 201; the coursework does not change that behavior.
It is not a pure read. **Run this write demonstration only in the disposable
fixture, never against the normal server or production.** A subsequent real
`GET /conversations/1` confirms persistence in that fixture (H09).

The current handler also has incident-assistance and confident-policy branches;
those were not exercised by this transcript. Their response shapes must not be
inferred from the clarification example. [Item 3 lifecycle/report](../AAI%201%20Assignment%203/README.md).

The Assistant renders `answer` plus a human-routing card and helpfulness controls.
[Actual screenshot](evidence/20261118-api/screenshots/02-post-assistant.png).
The HTTP transcript's conversation ID is 1; independent browser exercises create
later IDs. The response-to-screen equality check uses that browser request's own
ID/body. Its clarification is deterministic: it does not demonstrate a generated
LLM answer or real PostgreSQL retrieval.

## Authentication and negative responses

The fixture's existing `POST /dev-auth/token` takes
`Content-Type: application/json`, body `{"user_id":8}`, and returns 200 with
`access_token`, `token_type`, `expires_in` and `issuer`. The complete
actual response with its token redacted is in the HTTP transcript. This endpoint
is development/test-only and loopback-only; production uses a different provider.

| Actual request | Status | Actual response meaning |
|---|---:|---|
| GET `/policies` without Authorization | 401 | Authentication required; `WWW-Authenticate: Bearer` |
| POST `/ask` with whitespace question | 422 | Safe validation error below |
| POST `/ask` with employee token and `user_id:2` | 403 | Identity mismatch |
| GET another employee's conversation | 404 | Conversation not found; private data not returned |

Actual 422 response:

```json
{
  "detail": "Check the submitted fields and try again."
}
```

## Public JSON APIs and Pulse — additional live evidence

`GET http://127.0.0.1:8041/api/pulse?limit=5`, `Accept: application/json`, no
Authorization/body, returned **200** with normalized article JSON. The existing
Pulse pipeline actually downloaded all four registered sources; observed upstream
URLs, request headers, HTTP status codes and times are retained in
[public-network.json](evidence/20261118-api/public-network.json).

| Upstream | Wire format | Actual HTTP status | Normalized source items |
|---|---|---:|---:|
| Federal Register | JSON | 200 | 43 |
| FDIC | RSS/XML | 200 | 25 |
| NIST | JSON | 200 | 9 |
| Federal Reserve | RSS/XML | 200 | 15 |

Full upstream source counts are before combined-feed deduplication/limiting. The
HTTP check requested five articles; the normal UI requests 60 and uses the same
in-memory source cache. A local 200 alone would not prove upstream availability;
these separate source statuses and observed upstream responses supply that proof.
RSS GETs alone are not used to satisfy the two-REST-method criterion.

Observed normalized article (selected fields, not a complete response):

```json
{
  "title": "Reserve Requirements of Depository Institutions",
  "source": "Federal Register",
  "url": "https://www.federalregister.gov/documents/2026/11/18/2026-23453/reserve-requirements-of-depository-institutions",
  "published": "2026-11-18",
  "status": "Final Rule",
  "summary": "The Board is amending Regulation D, Reserve Requirements of Depository Institutions, to reflect the annual indexing of the reserve requirement exemption amount and the low reserve tranche for 2027. The annual indexation of these amounts is required notwithstanding the Board's action in March 2020 of setting all\u2026"
}
```

The original Pulse UI displays titles, source names, dates, classifications and
source links. [Actual screenshot](evidence/20261118-api/screenshots/03-get-pulse.png).
[Federal Register API documentation](https://www.federalregister.gov/developers/documentation/api/v1)
confirms public API access without keys. Availability and content are point-in-time.

## Existing AI integration — UNVERIFIED external connectivity

`backend/ai.py` already calls an OpenAI-compatible Chat Completions API via the
OpenAI SDK. `POST /ask` invokes it only for sufficiently confident approved-policy
matches. Server-only `OPENAI_BASE_URL`, `OPENAI_MODEL` and `OPENAI_API_KEY` configure
the provider; current code defaults to OpenRouter, while the module's older
introductory comment mentions Groq/OpenAI examples. Actual secret configuration
was not printed or changed. No particular configured provider is claimed verified.

The outgoing request uses POST to the configured base URL's `/chat/completions`,
server-side bearer authentication, JSON model/messages/temperature/token settings;
the app reads `choices[0].message.content`. Those are inspected code contracts,
not captured provider responses. No provider status, model result, paid call or
live AI response is claimed. AI is not needed to satisfy the supplied four rubric
items because the existing secured API and public JSON API are working.
