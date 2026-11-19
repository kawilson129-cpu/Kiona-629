# Assignment 1 — final rubric checklist

Finalized November 19, 2026 using existing coursework evidence only.
**4/4 supplied criteria supported (PASS within the stated verification scope).**
This is a review status, not an instructor grade. The local LMS screenshot exposes
only the assignment header; the original task supplied the complete four criteria below.

| Supplied criterion | Status | Concrete implementation and evidence | Mandatory remaining requirement |
|---|---|---|---|
| Demonstrate at least 2 distinct RESTful HTTP methods to fetch/send data. | **PASS — local scope** | GET `/policies` + POST `/ask`; retained H04/H07–H09, B02/B06. [Two-page report](AI_API_Integration_1_Rubric_01_Report.pdf), [actual exchanges](api-evidence.md), [HTTP JSON](evidence/20261118-api/http-results.json). | None; no new success screenshot required |
| Format and display API data using at least one HTTP method. | **PASS** | B01/B03–B05, readable original Library/Assistant/Pulse, [actual captures](evidence/20261118-api/README.md), [Assignment 2 PDF](../AAI%201%20Assignment%202/AI_API_Integration_1_Rubric_02_Report.pdf). | None |
| Document structured requests/responses: HTTP method, endpoint/URL, headers, request body (if applicable), response, and status code. | **PASS** | [api-evidence.md](api-evidence.md), retained JSON, [Assignment 3 PDF](../AAI%201%20Assignment%203/AI_API_Integration_1_Rubric_03_Report.pdf). GET body absent; POST body shown; 200/401/422/403/404 explicitly distinguished. | None |
| Demonstrate a working public or secured API with user-friendly output. | **PASS — stated scope** | Existing local signed bearer/RBAC; H02/H03/H11/H12 and original UI. Historical public JSON H13–H15; [Assignment 4 PDF](../AAI%201%20Assignment%204/AI_API_Integration_1_Rubric_04_Report.pdf). | None; production and external AI remain outside the verified scope |

## Evidence interpretation

- **Reused, not rerun:** 22 PASS / 0 FAIL = 15 HTTP + 7 browser checks, November 18.
- **200 success:** authenticated GET returns resources; POST creates fixture records
  and returns guidance; follow-up GET verifies persistence only in disposable SQLite.
- **401 rejection:** retained H02 proves missing bearer authentication is rejected.
  User-referenced Swagger 401 images are not located/embedded; their status must
  never be converted into a success claim. [Availability and review](evidence/finalization-20261119/README.md).
- **422/403/404:** invalid fields, body identity mismatch and private-record denial.
- **Mocked/disabled:** PostgreSQL ranking mocked to no matches; external AI/email
  disabled. Deterministic clarification is not a generated provider answer.
- **Unverified:** production Supabase/authentication and live AI-provider responses.
  No supplied criterion requires those when the existing secured/public API is demonstrated.
- The four retained public 200 observations are not four added test cases or a
  guarantee of current feed availability; RSS alone does not establish two REST methods.

The former “deferred” Item 1 status is closed by the new report and already adequate
transcripts/UI evidence. No application change, API rerun or additional screenshot
is mandatory. Assignment 2–4 reports and historical evidence remain unchanged.
[Current offline artifact verification](evidence/finalization-20261119/validation.json)
is separate from the original application tests.
