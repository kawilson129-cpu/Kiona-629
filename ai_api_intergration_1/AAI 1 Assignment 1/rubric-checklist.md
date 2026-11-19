# AI API Integration 1 - final rubric checklist

Reviewed November 18, 2026. These are evidence-based completion statuses, not an
instructor grade. The local course screenshot shows only the assignment heading;
the mapping uses the four supplied criteria already recorded in this coursework.
Confirm any expanded LMS conditions separately.

| Item | Final status | Concrete evidence | Remaining qualification |
|---|---|---|---|
| 1. At least two distinct HTTP methods | **DEFERRED - report/manual captures** | GET `/policies`, POST `/ask`: H04/H07-H09, B02/B06; originals preserved | [Manual Network/Payload/Response checklist](README.md); no final Item 1 report created |
| 2. Format and display API data | **COMPLETE** | [Supplied one-page report](../AAI%201%20Assignment%202/AI_API_Integration_1_Rubric_02_Report.pdf), B01/B03-B05; Library/Assistant/Pulse captures | Verified local display and point-in-time public data; supplied PDF retained unchanged |
| 3. Structured methods, URLs, headers, bodies, JSON and statuses | **COMPLETE** | [Two-page report](../AAI%201%20Assignment%203/AI_API_Integration_1_Rubric_03_Report.pdf), [full exchanges](api-evidence.md), [source/lifecycle notes](../AAI%201%20Assignment%203/README.md); H02-H12 | Report excerpts explicitly select fields; complete captured bodies remain linked; optional documentation screenshot not required by supplied criterion |
| 4. Working open or secured API with friendly output | **COMPLETE - stated scope** | [Supplied one-page report](../AAI%201%20Assignment%204/AI_API_Integration_1_Rubric_04_Report.pdf); actual 200/401/403/404 and public source records, readable UI | Signed development bearer, synthetic SQLite; production and external AI unverified |

## Evidence boundaries and review

- Existing functional evidence: **22 PASS / 0 FAIL**, 15 HTTP + 7 browser checks; reused, not rerun.
- Four upstream 200 responses are separate source observations, not four additional tests.
- Search is mocked; AI/email disabled. Deterministic clarification is not an LLM response.
- Items 2/4 PDFs were already supplied in the correct folders; visually reviewed, not regenerated.
- Item 3 report uses actual sanitized transcripts and inspected current `main.py`/`schemas.py`.
- All 11 fixture source hashes match after CRLF-to-LF normalization. Raw hashes differ due to checkout line endings; no byte-identical cross-platform claim is made.
- [Finalization review and validation](../AAI%201%20Assignment%203/evidence/finalization-review.md) records page counts, report checks, hashes and remaining submission actions.
- No application/UI/RBAC/database/secret change, production write, dependency install, commit or push.

Earlier failures remain in the original attempt folders. The old document audit's
hashes describe documents before this finalization; its result is historical, not
an assertion that edited README/checklist files retain their old hashes.
