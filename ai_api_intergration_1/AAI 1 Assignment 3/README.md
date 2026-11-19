# Item 3 - Structuring API Requests and Responses

**COMPLETE within the supplied criterion.** [Final two-page report](AI_API_Integration_1_Rubric_03_Report.pdf)
matches the supplied Item 2/4 reports. It is derived from existing real, sanitized
loopback exchanges, not a new app or an invented provider response.

## Lifecycle and contract

| Step | Existing behavior / evidence |
|---|---|
| Request | GET `http://127.0.0.1:8041/policies`, no body; POST `http://127.0.0.1:8041/ask` with JSON question. Relevant headers: Accept, signed Bearer authorization (redacted), POST Content-Type |
| Identity and validation | Existing identity dependency verifies the actor; AskRequest trims question and enforces 2-1,000 characters. Optional topic max 1,000; optional legacy user_id must agree with the verified actor |
| Handler | GET queries approved policies and serializes resources. The observed POST creates a fixture conversation/messages and clarification; PostgreSQL search returns mocked no matches |
| Response | Both observed successes return 200, application/json, no-store. GET array renders Library rows; POST object supplies IDs, guidance and routing state |
| Errors | Observed 401 Authentication required, 422 safe invalid-field detail, 403 Identity mismatch, 404 Conversation not found. The 404 is a related private-conversation GET, not an invented /ask error |
| Display | B03 compares the actual browser POST answer to displayed guidance. Original screenshot 02 shows that deterministic fallback; it does not show live AI |

[Full request/response bodies](../AAI%201%20Assignment%201/api-evidence.md) and
[machine transcripts](../AAI%201%20Assignment%201/evidence/20261118-api/http-results.json)
are authoritative. The report's selected JSON fields are clearly labelled excerpts.
POST returns 200 under the existing contract even though the observed branch persists
records; no API behavior was changed. IDs/timestamps are fixture-run specific.

Inspected implementation: [GET and POST handlers](../../derexi-policy-pilot/backend/main.py),
[request schema](../../derexi-policy-pilot/backend/schemas.py). GET accepts optional
status/category_id query filters, but the captured success uses neither. Other /ask
branches include incident assistance and confident-policy answers; neither is claimed
exercised by this transcript. Schema bounds/query behavior are source observations,
not additional executed tests.

## Evidence and remaining work

Reused successful tests: H02-H12 for methods/auth/body/JSON/status/persistence and
B02/B03/B06 for the actual UI exchange. No genuine runtime evidence gap was found;
no comprehensive or focused application rerun was needed. AI remained off in the
original fixture. Production Auth/Supabase/provider operation remains unverified.

Available captures are linked in the [original evidence index](../AAI%201%20Assignment%201/evidence/20261118-api/README.md).
For an optional Item 3 screenshot: open api-evidence.md alongside http-results.json;
show one sanitized GET/POST record with URL, headers, body, status and response.
Label it "retained Nov 18 local-fixture transcript" and save under this evidence
folder. Do not expose tokens or describe the document capture as a new API request.

[Report review](evidence/finalization-review.md) records supplied-PDF verification,
current artifact QA and source equivalence. `src/build_report.py` rebuilds only this
report using the existing bundled ReportLab runtime; no dependency install required.
