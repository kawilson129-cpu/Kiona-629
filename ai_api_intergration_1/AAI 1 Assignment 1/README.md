# AI API Integration 1 - submission guide

Existing DeRexi project; original course spelling `ai_api_intergration_1/` preserved.
Finalized November 18, 2026. Instructor grading is separate from these evidence statuses.

| Item | Status | Final report / evidence |
|---|---|---|
| 2. Format and Display API Data | **COMPLETE - verified local display** | [Supplied one-page report](../AAI%201%20Assignment%202/AI_API_Integration_1_Rubric_02_Report.pdf); B01/B03-B05 and screenshots 01/02/03 |
| 3. Structuring API Requests and Responses | **COMPLETE - documented exchange** | [Two-page report](../AAI%201%20Assignment%203/AI_API_Integration_1_Rubric_03_Report.pdf); [lifecycle/source notes](../AAI%201%20Assignment%203/README.md); actual GET/POST and 401/422/403/404 transcripts |
| 4. Implement Open or Secured APIs | **COMPLETE - stated verified scope** | [Supplied one-page report](../AAI%201%20Assignment%204/AI_API_Integration_1_Rubric_04_Report.pdf); H02-H15 and B01-B07 |
| 1. GET/POST demonstration | **DEFERRED - final report not created** | Existing GET/POST tests preserved; manual screenshots listed below |

The supplied Item 2/4 PDFs were found in their existing folders, visually checked
and retained unchanged. All three reports use a consistent cream/espresso/gold
presentation and are within 1-2 pages. See [rubric mapping](rubric-checklist.md),
[full sanitized API exchanges](api-evidence.md), [test results](test-results.md)
and [report review / artifact validation](../AAI%201%20Assignment%203/evidence/finalization-review.md).

## What the evidence actually proves

**Reused: 22 PASS / 0 FAIL** (15 real loopback HTTP checks + 7 original-UI browser
checks, November 18). No application tests or public-feed requests were rerun for
report finalization. The original application, UI and signed development bearer
identity/RBAC were exercised with synthetic, disposable SQLite records.
PostgreSQL search was **MOCKED to no matches**; external AI/email were **DISABLED**.

Public feeds separately returned 4/4 HTTP 200 at their recorded times: Federal
Register/NIST JSON and FDIC/Federal Reserve RSS. These are retained point-in-time
public-live observations, not fresh availability or four extra test cases.
Production Supabase/authentication and AI-provider responses remain **UNVERIFIED**.
[Original JSON, actual screenshots and scope labels](evidence/20261118-api/README.md).

The available course screenshot contains the assignment header, not expanded
rubric rows. Completion mapping follows the supplied criteria already documented
here and the requested scope; confirm any additional LMS wording before submission.

## Item 1 - brief manual screenshot checklist

Use only the disposable fixture on **127.0.0.1:8041**, never the normal application
on 8000 or production. Keep the scope label: **local fixture / synthetic SQLite /
search mocked / AI off**. Open DevTools Network, filter Fetch/XHR and enable
Preserve log. Never capture Authorization, cookies, a token response, raw HAR or secrets.

- [ ] **GET:** reload `/ui/?as=8#library`; capture the Network table with Method/Name/Status showing GET `/policies` 200 beside the readable Library.
- [ ] **POST request:** ask `How should I handle a hypothetical policy exception?`; capture POST `/ask` 200, its General URL/method/status and JSON Payload. Collapse Request Headers.
- [ ] **POST response:** capture that same request's Response JSON beside the Assistant guidance. IDs must belong to this capture, not be copied from old evidence.
- [ ] Optional: GET Response JSON and GET/POST together in one Network table.

Save manual images beneath the existing `evidence/` directory with a new name.
Current UI screenshots 01/02 already exist; these additional captures document
HTTP details. No Item 1 final PDF is included.

## Optional fixture reproduction

Only if a manual capture is needed. Existing recorded commands and cleanup scope:
[evidence commands](evidence/20261118-api/commands.txt). Use an unused output path.
On this Windows checkout, from the repository root:

```powershell
& derexi-policy-pilot/.venv/Scripts/python.exe -B derexi-policy-pilot/backend/tests/api_integration_evidence.py serve --output "ai_api_intergration_1/AAI 1 Assignment 1/evidence/manual-01"
```

This offline fixture is sufficient for Item 1 GET/POST captures; public-feed health
is not implied. Open the original UI manually, wait for entry animations to settle,
and stop only the dedicated fixture terminal with Ctrl+C. Do not restart or change
an existing application service. No need to repeat the successful full suite.

Item 3 needs no additional runtime test evidence. An optional documentation capture
can show [api-evidence.md](api-evidence.md) beside sanitized `http-results.json`
with URL, method, selected headers, body, status and response; this is a document
capture, not a newly verified API transaction.
