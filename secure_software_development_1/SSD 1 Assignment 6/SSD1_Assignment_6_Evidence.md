# SSD1 Assignment #6 — Evidence Package
## Criterion #6: Produce Security Documentation and Reporting

| Field | Value |
|---|---|
| Course | Secure Software Development 1 |
| Project | DeRexi: Policy Pilot (Aurum Capital Bank) |
| Student | Kiona Wilson |
| Evidence assembled | 2026-10-11 |
| Scope | Existing SSD1 Assignments #1–#5 + the canonical DeRexi code in `derexi-policy-pilot/backend/` |
| Status | Evidence collection complete — ready for report layout by another tool |

> **Fidelity statement:** Every result below is either (a) transcribed from a prior
> SSD1 assignment report, or (b) newly executed and verified on 2026-10-11 in a
> safe local manner. No test was marked PASS unless observed. No screenshot was
> invented. No production data was modified (no database-writing tests were run).

---

## 1. Executive Summary

- Prior SSD1 work (Assignments #1–#5) already produced a secure-development
  environment report, secure-coding/input-validation evidence, a static-analysis
  and runtime-testing report, an OWASP ZAP vulnerability assessment, and a
  best-practices report.
- This package consolidates that material and adds **new verification performed
  tonight**: request-schema validation tests and live HTTP checks against the
  local API (no database writes).
- **Confirmed strengths (verified):** input validation is enforced in code
  (whitespace stripping + length/pattern constraints return HTTP 422);
  `.env` is excluded from Git; the API rejects malformed requests before
  processing.
- **Confirmed weaknesses (verified):** the canonical API currently uses a
  **permissive wildcard CORS policy with credentials enabled** (a preflight from
  an arbitrary origin is allowed), and the `/ui` response is **missing key
  browser security headers** (CSP, X-Frame-Options, X-Content-Type-Options).
- **Material discrepancy:** SSD1 Assignment #1 and #5 reports describe a narrowed
  FastAPI CORS policy, but the **committed canonical code does not contain it** —
  the policy is still `allow_origins=["*"]`. This is flagged in §5 (Remediation
  Status) and must be re-applied if the report is to remain accurate.
- Overall: the reporting criterion is well-supported by prior artifacts; the most
  valuable new content is the verified test table (§4) and the accurate
  remediation status (§5).

---

## 2. Security Issues and Severity

| ID | Issue | Category | Severity | Confirmed how |
|---|---|---|---|---|
| V-01 | Permissive CORS: `allow_origins=["*"]` with `allow_credentials=True` | OWASP A02:2025 Security Misconfiguration | **High** | Live preflight (2026-10-11) |
| V-02 | `Content-Security-Policy` header not set on `/ui` | OWASP A05:2025 Security Misconfiguration | Medium | ZAP (A#4) + live header check |
| V-03 | Missing anti-clickjacking control (`X-Frame-Options` / CSP `frame-ancestors`) | OWASP A02/A05 Security Misconfiguration | Medium | ZAP (A#4) + live header check |
| V-04 | `Subresource Integrity` attribute missing on external Google Fonts stylesheet | Supply-chain / integrity hardening | Low–Medium | ZAP (A#4) |
| V-05 | `X-Content-Type-Options: nosniff` not set | OWASP A05 Security Misconfiguration | Low | ZAP (A#4) + live header check |
| V-06 | Malformed user input returns a technical backend error (HTTP 422) rather than a user-friendly message | Error handling / information exposure | Low | A#3 runtime test |
| V-07 | CSS quality: unknown type selector `.ledger num` (likely typo) | Maintainability / Reliability | Low | SonarQube (A#3) + static re-check |
| V-08 | CSS quality: duplicate `.gate` selector | Maintainability | Low | SonarQube (A#3) + static re-check |
| V-09 | CSS quality: low text/background contrast flagged | Accessibility | Low | SonarQube (A#3) |

Severity notes: V-01 is rated High because with `allow_credentials=True` the
server echoes any requesting origin (verified), which permits credentialed
cross-origin requests from arbitrary sites — not merely a blanket public API.

---

## 3. Detailed Vulnerability Assessment

### 3.1 Method
- **Scan tool (prior work):** OWASP ZAP automated scan (Default Policy) against
  the local UI at `http://127.0.0.1:8000/ui` — documented in
  `SSD 1 Assignment 4\SSD Assignment 4.pdf` (5 alert categories: 3 medium /
  1 low / 1 informational; OWASP A02:2025 Security Misconfiguration).
- **New verification (2026-10-11):** live HTTP checks against a locally started
  instance of the canonical API (`uvicorn main:app`, `127.0.0.1:8000`). Only
  read-only requests were used (static `/ui` fetch and a CORS preflight); **no
  database-writing endpoint was called.**

### 3.2 Primary findings (from OWASP ZAP, re-confirmed live)
1. **CSP header not set** — `GET /ui/` returns HTTP 200 but **no**
   `Content-Security-Policy` header. A CSP restricts which sources a browser may
   load and is a key defense-in-depth control against injected content.
2. **Missing anti-clickjacking control** — no `X-Frame-Options` and no CSP
   `frame-ancestors`; the page can be framed by another site (clickjacking risk).

### 3.3 Supporting findings
- **Subresource Integrity missing** on the externally loaded Google Fonts
  stylesheet (integrity/supply-chain observation).
- **`X-Content-Type-Options` missing** (`nosniff` not set).

### 3.4 New verified finding — permissive CORS (V-01)
A CORS preflight was sent to the live local API:

```
OPTIONS /ask
Origin: http://evil.example
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type
```

Observed response (HTTP 200):

```
access-control-allow-origin: http://evil.example
access-control-allow-credentials: true
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, QUERY
access-control-allow-headers: content-type
access-control-max-age: 600
```

The server grants the arbitrary origin access **and** allows credentials, which
contradicts the narrowed policy described in Assignments #1 and #5.

### 3.5 Live security-header check (2026-10-11)
`GET /ui/` → HTTP 200, headers present: `vary, accept-ranges, content-length,
content-type, etag, last-modified, server`. **Absent:** `Content-Security-Policy`,
`X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`,
`Referrer-Policy`.

> Note: the assessment ran against a local development instance over HTTP
> (`127.0.0.1`). HSTS is expected to be irrelevant on plain HTTP and is listed
> for completeness only.

---

## 4. Test Execution Results

Legend — **PASS**: observed as expected. **PARTIAL PASS**: expected protection
occurred but with a secondary defect. **FAIL**: observed behavior is insecure.
**PASS (documented)**: executed and recorded in a prior graded assignment with
screenshot evidence.

| Test ID | Objective | Test input / scenario | Expected outcome | Actual observed outcome | Result | Supporting evidence |
|---|---|---|---|---|---|---|
| T-01 | Valid policy question answered with citation | A supported DeRexi policy question (AML) | Grounded answer + cited policy + confidence | Grounded AML answer with policy reference, related results, visible confidence score | PASS (documented) | `SSD 1 Assignment 3\SSD 1 Assignment 3.pdf` (Test 1) |
| T-02 | Unsupported question declined & routed | “What are my main tasks?” | Decline to guess; route for human clarification | Routed to a policy owner for clarification | PASS (documented) | `SSD 1 Assignment 3\SSD 1 Assignment 3.pdf` (Test 2) |
| T-03 | Malformed input rejected safely | Single slash `/` | Reject invalid data; clear user message | HTTP 422 returned (invalid data not processed) but message exposes a technical backend error | PARTIAL PASS (documented) | `SSD 1 Assignment 3\SSD 1 Assignment 3.pdf` (Test 3) |
| T-04 | Credential verification (Stay Data Stay) | Correct username + password | Access granted and flow continues | Credentials verified; program proceeds | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| T-05 | Generic authentication failure | Incorrect credentials | Single generic failure message (no user/pass disclosure) | One generic message; no indication which field failed | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| T-06 | Required-field validation | Blank hotel name / room number | Reject blank; re-prompt | Re-prompts until required data supplied | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| T-07 | Type & range validation | Non-numeric and ≤0 stay length | Handle exception; reject out-of-range | `int()` in try/except; value must be > 0 | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| T-08 | Allow-list selection | Account number not in known options | Reject invalid selection | Selection compared against `account_options`; invalid rejected | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| T-09 | Duplicate entry prevention | Add an account already present | Prevent duplicate append | Duplicate entries prevented before append | PASS (documented) | `SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| **T-10** | Reject blank/whitespace question (schema) | `AskRequest(user_id=8, question="   ")` | Validation error (HTTP 422) | `ValidationError: string_too_short` — “String should have at least 2 characters” | **PASS (verified 2026-10-11)** | Schema test output (this package, §6) |
| **T-11** | Accept valid question (schema) | `AskRequest(user_id=8, question="How much paid time off do I get?")` | Accepted | Validated successfully | **PASS (verified 2026-10-11)** | Schema test output |
| **T-12** | Reject 1-char question (boundary) | `question="x"` | Validation error | `ValidationError: string_too_short` | **PASS (verified 2026-10-11)** | Schema test output |
| **T-13** | Require `user_id` (schema) | Omit `user_id` | Validation error | `ValidationError: missing` — “Field required” | **PASS (verified 2026-10-11)** | Schema test output |
| **T-14** | Incident severity allow-list | `severity="urgent"` then `"high"` | Bad rejected; good accepted | `urgent` → `string_pattern_mismatch`; `high` → accepted | **PASS (verified 2026-10-11)** | Schema test output |
| **T-15** | Policy status allow-list | `status="publish"` then `"draft"` | Bad rejected; good accepted | `publish` → `string_pattern_mismatch`; `draft` → accepted | **PASS (verified 2026-10-11)** | Schema test output |
| **T-16** | CORS preflight from untrusted origin | `OPTIONS /ask`, `Origin: http://evil.example` | Non-allowed origin should be denied | **Origin allowed** with `allow-credentials: true` | **FAIL (verified 2026-10-11)** | Live preflight dump (§3.4) |
| **T-17** | Security headers on `/ui` | `GET /ui/` | CSP, X-Frame-Options, X-Content-Type-Options present | All three **absent** | **FAIL (verified 2026-10-11)** | Live header check (§3.5) |
| **T-18** | CSS static analysis | Inspect `style.css` | No invalid/duplicate selectors | `.ledger num` (line 121) invalid; `.gate` duplicated (lines 802, 843) | **FAIL (verified 2026-10-11)** | Static re-check |

Counts: **PASS (documented): 9** · **PARTIAL PASS: 1** · **PASS (verified tonight): 6** · **FAIL (verified tonight): 3**. No test was marked PASS without observation. No database-writing endpoint was executed.

---

## 5. Remediation Status

| Finding | Described as fixed in SSD1 reports? | Present in committed code? | Verified on 2026-10-11? | Status |
|---|---|---|---|---|
| Input validation (whitespace strip + length/pattern → 422) | Yes (A#3, A#5) | **Yes** — `schemas.py`, `main.py` `/ask` | Yes (T-10…T-15 PASS) | **IMPLEMENTED & VERIFIED** |
| `.env` excluded from source control | Yes (A#1, A#5) | **Yes** — `.gitignore` rule | Yes (`git check-ignore -v .env` per A#1) | **IMPLEMENTED** |
| `User.full_name` whitespace normalization | Yes (A#5) | **Yes** — `models.py:66-68` | Static confirmation | **IMPLEMENTED** |
| Narrowed FastAPI CORS policy | **Yes** (A#1, A#5) | **No** — code is still `allow_origins=["*"]` w/ credentials | Yes — preflight allowed (T-16 FAIL) | **NOT IMPLEMENTED (report/code mismatch)** |
| CSP header | Recommendation only (A#4) | No | Yes — absent (T-17) | **RECOMMENDED — NOT IMPLEMENTED** |
| Anti-clickjacking header | Recommendation only (A#4) | No | Yes — absent (T-17) | **RECOMMENDED — NOT IMPLEMENTED** |
| `X-Content-Type-Options: nosniff` | Recommendation only (A#4) | No | Yes — absent (T-17) | **RECOMMENDED — NOT IMPLEMENTED** |
| Subresource Integrity on Google Fonts | Recommendation only (A#4) | No | Not re-tested | **RECOMMENDED — NOT IMPLEMENTED** |
| Client-side input validation (avoid raw 422) | Recommendation only (A#3) | No | — | **RECOMMENDED — NOT IMPLEMENTED** |
| Fix invalid selector `.ledger num` | Recommendation only (A#3) | **No** — still line 121 | Yes (T-18) | **RECOMMENDED — NOT IMPLEMENTED** |
| Consolidate duplicate `.gate` selector | Recommendation only (A#3) | **No** — lines 802 & 843 | Yes (T-18) | **RECOMMENDED — NOT IMPLEMENTED** |
| Contrast improvement | Recommendation only (A#3) | Presumed not done | Not re-measured | **RECOMMENDED — NOT VERIFIED** |

**Confirmed remediations (actually present):** input validation, `.env` exclusion, and model-output normalization.
**Recommendations not implemented:** CORS narrowing (despite being described as done), security headers, SRI, client-side validation, CSS selector fixes.

---

## 6. Evidence File Paths

All paths are relative to the repository root `Kiona-629/`.

| Evidence | Path |
|---|---|
| A#1 report (env tooling, CORS before/after) | `secure_software_development_1\SSD 1 Assignment 1\SSD 1 Assignment 1.pdf` |
| A#1 screenshots (VS Code tools, git check-ignore) | `secure_software_development_1\SSD 1 Assignment 1\SSD 1 Assignment 1 Screenshots.pdf` |
| A#2 report (secure login / validation) | `secure_software_development_1\SSD 1 Assignment 2\SSD 1 Assignment 2.pdf` |
| A#2 input-validation figure | `secure_software_development_1\SSD 1 Assignment 2\Secure Input Validation Lab.png` |
| A#3 report (SonarQube findings + runtime tests) | `secure_software_development_1\SSD 1 Assignment 3\SSD 1 Assignment 3.pdf` |
| A#4 report (OWASP ZAP vulnerability assessment) | `secure_software_development_1\SSD 1 Assignment 4\SSD Assignment 4.pdf` |
| A#5 report (best practices) | `secure_software_development_1\SSD 1 Assignment 5\SSD 1 Assignment 5.pdf` |
| Rubric / task definition | `secure_software_development_1\Secure Software Development 1 Tasks.pdf` |
| This evidence package | `secure_software_development_1\SSD 1 Assignment 6\SSD1_Assignment_6_Evidence.md` |
| Code — API & CORS & `/ask` validation | `derexi-policy-pilot\backend\main.py` |
| Code — request schemas/validation | `derexi-policy-pilot\backend\schemas.py` |
| Code — model normalization | `derexi-policy-pilot\backend\models.py` |
| Code — CSS findings | `derexi-policy-pilot\backend\static\style.css` |

Tonight's raw test output (schema validation and live HTTP header/preflight dumps)
was produced by direct inspection commands and is summarized in §3.4, §3.5 and §4.
No separate log file was generated by prior assignments for these checks.

---

## 7. Outstanding Security Risks

1. **Wildcard CORS with credentials (High, V-01)** — the single most significant
   confirmed risk. Any origin can issue credentialed cross-origin requests to the
   API. This must be narrowed to explicit local/production origins before the API
   handles real users.
2. **No browser hardening headers (Medium, V-02/V-03/V-04/V-05)** — missing CSP,
   anti-clickjacking, SRI, and `nosniff` leave the UI open to clickjacking and
   reduce defense-in-depth against injected content.
3. **No authentication/authorization or rate limiting on the API (structural)** —
   endpoints such as `/ask`, `/incidents`, and clarifications currently accept a
   caller-supplied `user_id`; the API is a local MVP and is not exposed publicly.
   Documented as a known limitation of the MVP, not a tested finding.
4. **Error-message information exposure (Low, V-06)** — malformed input surfaces a
   technical 422 body instead of a friendly prompt.
5. **Report/code mismatch (governance risk)** — Assignments #1 and #5 state the CORS
   policy was narrowed; the committed code shows otherwise. Any submitted report
   must be corrected or the code change re-applied so documentation matches reality.

---

## 8. References to Relevant Code Files

| File | Reference | Relevance |
|---|---|---|
| `derexi-policy-pilot\backend\main.py` | lines 59–65 | CORS middleware — currently `allow_origins=["*"]`, `allow_credentials=True`, wildcard methods/headers (V-01) |
| `derexi-policy-pilot\backend\main.py` | lines 388–396 | `/ask` route: `question.strip()` then HTTP 422 when empty; validates before search (T-10/11/12) |
| `derexi-policy-pilot\backend\schemas.py` | lines 44–49 | `AskRequest`: `str_strip_whitespace=True`, `min_length=2`, `max_length=1000` (V-06 validation) |
| `derexi-policy-pilot\backend\schemas.py` | lines 70–84 | `Incident` severity/status `pattern=` allow-lists (T-14/15) |
| `derexi-policy-pilot\backend\schemas.py` | line 30 | `PolicyCreate.status` pattern allow-list (T-15) |
| `derexi-policy-pilot\backend\models.py` | lines 66–68 | `User.full_name` applies `.strip()` (A#5 normalization evidence) |
| `derexi-policy-pilot\backend\static\style.css` | line 121 | `.ledger num` invalid type selector (V-07 / T-18) |
| `derexi-policy-pilot\backend\static\style.css` | lines 802, 843 | duplicate `.gate` selector (V-08 / T-18) |

---

## 9. Documentation-Template Requirement

The Criterion #6 rubric text states **“Proper documentation templates must be
followed.”** No instructor-provided template file was found anywhere in the
`secure_software_development_1/` directory or the repository. The requirement is
therefore generic. Recommendation for the final report: use a standard security
documentation structure (scope → methodology → findings with severity →
test results → vulnerability assessment → remediation status → evidence →
residual risk), which this package already reflects section-by-section.

---

## 10. Verification Notes and Limitations

- **No production data was modified.** No database-writing endpoint (e.g. `POST /ask`,
  `POST /incidents`) was executed. Only the static `/ui` fetch and a CORS preflight
  were run against the API; both are read-only.
- **Timezone:** live checks ran 2026-10-11/12 local (Eastern).
- **A#2 tests (T-04…T-09)** relate to the *Stay Data Stay* application documented
  in Assignment #2; their status is transcribed from that report (screenshots
  embedded there) and was not re-executed tonight.
- **A#4 ZAP findings** were re-confirmed for the header-related items only
  (V-02/V-03/V-05); SRI (V-04) was not re-tested.
- **T-18** is a static (non-executing) confirmation of the SonarQube findings.
- The CORS discrepancy (§5) is reported as observed; it is **not** corrected in
  this package (no application code was modified).

*End of evidence package.*
