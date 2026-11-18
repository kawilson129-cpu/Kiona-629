# AI API Integration 1 — rubric gap analysis

Existing course folder: `ai_api_intergration_1/` (original spelling retained).
Implementation: canonical `derexi-policy-pilot/`; no separate application.

| Item | Existing implementation/evidence | Gap before this session | Initial status |
|---|---|---|---|
| 1. Two distinct RESTful HTTP methods | GET `/policies`, POST `/ask`, prior Week 10 isolated tests | Course-specific real socket HTTP transcripts and scope labels | UNVERIFIED for this course |
| 2. Format/display API data | Library formats GET JSON as rows; Assistant displays POST JSON answer | Fresh rendered-output assertions/captures | UNVERIFIED for this course |
| 3. Structured request/response documentation | Existing FastAPI schemas/OpenAPI | Course method/URL/headers/body/status/response examples and curl | PARTIAL |
| 4. Working public or secured API and friendly output | Server-verified bearer identity/RBAC, Library/Assistant, public Pulse JSON | Current real HTTP, security and browser evidence; upstream checks separate | UNVERIFIED for this course |

Pulse's RSS downloads alone are not evidence of two REST methods. The primary
demonstration uses DeRexi's JSON resource GET and request-processing POST.
Public Federal Register/NIST JSON, RSS aggregation and optional OpenAI-compatible
AI calls are separate integrations with separate connectivity claims.

## Final rubric mapping — November 18, 2026

| Rubric item | Final status | Implemented behavior / actual evidence | Tests | Remaining gap |
|---|---|---|---|---|
| 1. At least two distinct RESTful HTTP methods fetch/send data | **PASS — isolated app** | Existing GET `/policies` retrieves resources; POST `/ask` submits JSON and creates fixture conversation/clarification. [Transcripts](evidence/20261118-api/http-results.json), [structured examples](api-evidence.md) | H04, H07–H09; B02/B06 | No production write demonstration, intentionally |
| 2. Format and display API data via at least one method | **PASS** | Original Library formats GET response; Assistant displays POST answer; Pulse formats public data. [Actual captures](evidence/20261118-api/README.md) | B01, B03–B05 | No UI implementation gap found |
| 3. Document method, endpoint/URL, headers, body, response and status | **PASS** | [api-evidence.md](api-evidence.md) includes complete actual GET/POST examples, errors and headers; [README](README.md) supplies curl and capture steps | Machine transcripts record all required fields; documentation audit recorded separately | Optional documentation-panel screenshot not captured; written requirement complete |
| 4. Working public or secured API with friendly output | **PASS — stated scope** | Existing signed development bearer/RBAC path over real HTTP; readable guidance/rows; live public JSON feeds. [Results](test-results.md) | H02/H03/H07/H11–H15; B01–B07 | Production auth/Supabase and live AI-provider connectivity UNVERIFIED |

**22 PASS / 0 FAIL**: 15 real HTTP checks plus 7 browser checks. Real public
collection: 4/4 HTTP 200, including two JSON sources. Search ranking is explicitly
mocked, AI disabled, policy data synthetic. This supports the four supplied items;
it does not award an instructor grade or claim production readiness.

Minimum implementation decision: **no runtime app changes**. Added only reusable
verification harnesses in the canonical backend test directory and coursework
material in this existing course folder. No secrets, schema, RBAC, production
data or existing UI were changed; no dependencies installed or commit/push.
[Exact screenshot instructions for each criterion](README.md).
