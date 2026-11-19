# AI API Integration 1 — Assignment 1

**Finalized November 19, 2026. All four supplied rubric criteria are supported.**
The assessment is evidence-based, not an instructor-awarded grade.

Submit the matching two-page [Assignment 1 report](AI_API_Integration_1_Rubric_01_Report.pdf).
[Editable report source](AI_API_Integration_1_Rubric_01_Report.html),
[rubric checklist](rubric-checklist.md), [full API evidence](api-evidence.md),
[test results](test-results.md), and [finalization index](evidence/finalization-20261119/README.md).

| Item | Status | Existing implementation and coursework evidence |
|---|---|---|
| 1. Demonstrate two distinct RESTful HTTP methods | **PASS — verified local scope** | GET `/policies` retrieves policy resources; POST `/ask` submits JSON and creates fixture conversation/clarification records. H04/H07–H09 and B02/B06; new report packages existing evidence. |
| 2. Format/display API data | **PASS** | Original Library/Assistant/Pulse UI; B01/B03–B05 and actual Nov 18 screenshots. [Completed Assignment 2 report](../AAI%201%20Assignment%202/AI_API_Integration_1_Rubric_02_Report.pdf), preserved. |
| 3. Document structured requests/responses | **PASS** | Full URLs, methods, selected headers, body/no-body, JSON and statuses in api-evidence.md and original transcripts. [Completed Assignment 3 report](../AAI%201%20Assignment%203/AI_API_Integration_1_Rubric_03_Report.pdf), preserved. |
| 4. Working public or secured API and friendly output | **PASS — stated scope** | Existing signed development bearer/RBAC, actual local HTTP and readable output; retained public JSON feeds. [Completed Assignment 4 report](../AAI%201%20Assignment%204/AI_API_Integration_1_Rubric_04_Report.pdf), preserved. |

## What was reused

**22 PASS / 0 FAIL** from November 18: 15 actual socket HTTP checks + 7 existing-UI
browser checks. Original requests, statuses, JSON, screenshot images and earlier
failed attempts remain unchanged. No API tests, public-feed downloads, login or
production calls were executed during this finalization. New report rendering and
artifact checks are separate from the reused application test results.

The earlier verified GET `/policies` and POST `/ask` both returned **200 OK** with
JSON. H09 subsequently retrieved the created fixture conversation. H02 records a
separate unauthenticated GET with **401**, `WWW-Authenticate: Bearer`, and
`{"detail":"Authentication required"}`. H10–H12 record 422/403/404 outcomes.
A 401 screenshot cannot be presented as a successful 200 request.

Policy data is synthetic, disposable SQLite; PostgreSQL search was mocked to no
matches and external AI/email disabled. The answer is deterministic clarification,
not a live LLM answer. Production Supabase/auth and AI-provider connectivity remain
**UNVERIFIED**; these are not missing requirements in the four supplied criteria.
Public JSON/RSS source observations are retained, not current availability claims.
RSS alone is not used to satisfy two REST methods.

## Swagger image availability and evidence distinction

The user referenced existing Swagger screenshots of authentication enforcement and
401 responses. Those images were not present in the Assignment 1/course image
inventory or the inspected Desktop/Downloads locations at finalization. Only their
existing location was requested; no additional capture or API rerun was requested.
They have **not** been fabricated, embedded, or labelled as visually verified.
The report explicitly records their availability limitation and uses the authentic
retained 401 transcript instead. The three Nov 18 UI captures are present and linked.

If the existing Swagger files become available, their proper caption is
**user-supplied Swagger capture / 401 authentication rejection**, not **200 success**.
The saved original 200 transcripts independently establish successful GET/POST.
Their absence is an incorporation limitation, not a mandatory gap in the supplied
rubric: no new screenshot or test is required to substantiate its four criteria.

## Original rubric and preserved reports

The [existing LMS image](../Screenshot%202026-11-17%20at%202.44.17%E2%80%AFPM.png)
contains the course/assignment header, not expanded rubric rows. The original four
requirements supplied in the task are transcribed in [rubric-checklist.md](rubric-checklist.md);
no unseen LMS condition is invented. There is no evidence-based mandatory unresolved
requirement under that supplied rubric. Additional manual Network/Payload/Response
screenshots in the older checklist are optional presentation material, not blockers.

The completed Assignment 2–4 reports and all their supporting files were preserved
byte-for-byte against the baseline in the finalization folder. Their older Item 1
“deferred” notes describe the previous state and are superseded here, not rewritten.
The application, database, RBAC, secret files and pre-existing unrelated work were
untouched. No commit, push, dependency install or API execution.
