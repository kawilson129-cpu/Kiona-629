# Test results — November 18, 2026

## Assignment 1 finalization — November 19, 2026

The existing **22 PASS / 0 FAIL** below were reused without rerunning HTTP, UI,
public feeds or authentication. Assignment 1 now has a matching two-page report;
Assignment 2–4 reports remain unchanged. The previous manual-screenshot deferral
is superseded: the supplied rubric is already supported by original transcripts
and UI captures. User-referenced Swagger 401 images were not located and are not
claimed embedded; the actual retained H02 transcript supplies 401 evidence.

New verification is limited to offline document/PDF/page-count/link/hash checks:
[finalization validation](evidence/finalization-20261119/validation.json).
These checks are not new API tests and are not added to the 22-pass total.

**Retained application result: 22 PASS / 0 FAIL**: 15 real socket HTTP checks + 7 browser checks.
No production verification is included in this total. The documentation/links/hash
audit is recorded separately in the evidence validation file.

| Check group | Result | Evidence and limits |
|---|---|---|
| H01–H06 | 6 PASS | Existing service metadata, real 401 challenge, local signed-token issuance, protected GET JSON and policy detail |
| H07–H09 | 3 PASS | Actual POST question → 200 guidance/resource IDs → follow-up GET proves SQLite persistence; search is mocked, AI off |
| H10–H12 | 3 PASS | Actual 422 validation, 403 identity mismatch, 404 private-conversation isolation |
| H13–H15 | 3 PASS | Actual Pulse GET JSON, at least one real JSON source, normalized source/title/URL/date |
| B01–B04 | 4 PASS | Original Library/Assistant UI, real POST/network payload, response-to-screen equality and friendly routing controls |
| B05–B07 | 3 PASS | Real Pulse article display, independent successful GET/POST observations and no browser runtime exceptions |

Machine-readable [HTTP results](evidence/20261118-api/http-results.json),
[browser results](evidence/20261118-api/browser-results.json), and
[public-network records](evidence/20261118-api/public-network.json) retain actual
requests/statuses/JSON, assertion outcomes, times and screenshot paths.

Public-source requests separately returned **4/4 HTTP 200**:
Federal Register JSON (43 normalized items), NIST JSON (9), FDIC RSS (25),
Federal Reserve RSS (15). These are source counts before combined-feed limiting
and deduplication. The HTTP demonstration requests five articles; the UI requests
60 from the same source cache. Four source statuses are not four extra test cases
in the 22-check total. Retrieval is point-in-time, not an uptime guarantee.

## Scope labels

- **PASS:** real loopback HTTP, original FastAPI routes/UI, token verification,
  role/ownership checks, synthetic SQLite persistence, real public feed requests.
- **MOCKED:** existing `messaging_fixture.OfflineSession` returns no PostgreSQL
  trigram matches and translates selected PostgreSQL SQL for SQLite. No production
  search quality, query plan, concurrency, RLS or Postgres behavior is inferred.
- **UNVERIFIED:** live Supabase/production identity, external AI-provider response,
  confidently retrieved LLM answers and human/instructor sign-off. Not prerequisites
  of the four supplied criteria when the demonstrated secured/public API is used.

The fixture sets process-local AI/email switches off, uses the existing PostgreSQL
connection tripwire and never changes `.env`, RBAC, schema or live users. The
browser observes network responses without substituting fetch results. No runtime
app change was needed.

## Earlier attempts retained

- `attempts/initial-browser/`: **6 PASS / 1 FAIL**. A case-sensitive assertion
  expected “Open thread”; the UI's rendered `innerText` is “OPEN THREAD”. Early
  screenshots were also taken during the existing blur/entry animation.
- `attempts/browser-timing/`: **5 PASS / 2 FAIL**. Reusing the same URL could keep
  an old conversation in the SPA, and assertions read before the new POST body
  arrived. Both actual requests still returned 200. Corrected test synchronization
  uses a fresh navigation query and waits for that run's actual response.
- Latest run: **7 PASS / 0 FAIL**. Original UI/API functionality was unchanged;
  corrected harness assertions and settled-animation captures supersede the earlier
  browser attempts. Earlier attempts are not counted again or erased.

## Existing commands — reference only

Original executed commands remain in [commands.txt](evidence/20261118-api/commands.txt).
They document the historical test run and cleanup; none were repeated now.
Because coursework was subsequently organized under `AAI 1 Assignment 1/`, old
output paths describe the earlier directory layout. No rerun is required for the
supplied rubric. Any separately requested future rerun must use a new output folder
inside this assignment, the isolated fixture and the appropriate local interpreter.

See [README](README.md) for final report/evidence scope; no application service was
started for this finalization.
