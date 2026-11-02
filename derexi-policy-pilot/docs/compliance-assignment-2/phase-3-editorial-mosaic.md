# Phase 3 — Editorial mosaic and regulatory discovery

Implemented November 2, 2026. Phase 1 and Phase 2 documentation and screenshots
remain intact; their results describe the earlier interface.

## Objective and layout

Pulse becomes an editorial financial intelligence publication within the existing
DeRexi application. It preserves the Pulse navigation label, tagline, source
connection strip, timestamps, refresh, original links, and cache behavior.
No Supabase records, authentication, policy workflows, or other application views
were changed. No commit or push was made.

The composition uses an espresso lead with a serif headline and factual docket,
two asymmetric olive/stone spotlights, a distinct On the Radar reading margin,
and a three-column Intelligence Desk (two columns on tablets, one on phones).
Card heights follow content; the desk uses CSS Grid rather than a masonry library.
The cards have restrained elevation, visible focus rings, and reduced-motion
support. Existing typography and application navigation are reused.

## Selection and classification

Lead selection sorts the matching articles by the backend's existing editorial
score, then publication date and title, with a stable ID fallback. It does not
label stories urgent. Scores combine document significance (up to 34), topic
relevance (22), source weight (12), and recency (24). Recency declines linearly
over 45 days relative to the newest publication in the full normalized feed.
The same ranking supplies secondary stories. Remaining desk articles retain
newest-first order. Selection is limited to articles returned by the API.

The document-type facet has All Types, Final Rules, Proposed Rules, Notices,
Guidance, Standards Drafts, and General News. Federal Register's explicit types
are preserved: a Notice discussing guidance stays a Notice. A Federal Reserve
or FDIC press release discussing a final/proposed rule remains General News.
Guidance inferred from a press-release headline is explicitly marked as a Pulse
reading category alongside the original Press release type. NIST's dedicated
open-draft feed supplies Standards Draft classifications.

Topic and type filters combine independently. Banking & Finance includes banking
issuers, so it can combine with Final Rules. Other source categories are preserved;
Guidance topics also include headlines discussing guidance. Topics may overlap;
topic counts should not be summed. Each facet count reflects the other active
facet. The result total counts unique matching articles, not repeated Radar links.
Counts describe the loaded selection (up to 60), not complete agency archives.
Reset, zero-match feedback, pressed states, and focus restoration are implemented.

## On the Radar

All demo personas can read this section. The existing API curator selects at most
one best-ranked item for each substantive classification and returns nonbinding
reading prompts: Worth Monitoring, Potential Policy Review, Regulatory Awareness,
and Standards Development. Entries display source, publication date, classification,
provenance, and a relevance note. They link to originals and follow active filters.
The UI says these are informational suggestions, not verified legal obligations.
An API correction keeps Radar references within the returned article limit.
No assignments, approvals, or policy changes are implemented.

## Media inspection

Raw responses from all four registered official endpoints were inspected for
article image fields, image tags, enclosures, and media content/thumbnail elements.
No article image/media candidates were found. Federal Register returned document
and PDF links; NIST returned publication links/content. No reuse rights were
assumed and no images were embedded. All visual treatment uses type and CSS color
surfaces; it does not depict events. No AI images or stock photographs were used.

## Code guide

- `backend/static/pulse.js`: `topicMatches` / `typeMatches` implement independent
  facets; `rankArticles` selects the lead without mutating the cached feed;
  `classification` discloses source versus inferred labels. `paint` builds facet
  controls, restores keyboard focus, renders the mosaic, Radar, and desk. Dynamic
  feed strings continue to use `textContent`; only the existing constant arrow
  uses static icon markup. External article links require HTTPS and use
  `noopener noreferrer`.
- `backend/static/style.css`: commented Phase 3 sections scope the grid, espresso
  lead, spotlights, Radar, responsive breakpoints, and reduced motion to Pulse.
- `backend/pulse/service.py`: preserves source types and press-release identity,
  uses neutral guidance notes, and limits Radar references to returned articles.
  Feed endpoints, fetching, per-source caching, stale handling, and deduplication
  remain unchanged.
- `backend/tests/test_pulse.py`: updates classification regressions, tests limited
  Radar references, and activates previously defined ranking/Radar tests that the
  script's main runner had not invoked.
- `backend/tests/test_pulse_browser.mjs`: dependency-free Node/Chrome CDP browser
  checks and screenshot capture; synthetic states are explicitly labeled.

## Executed tests

| Check | Observed result |
|---|---|
| Before: Pulse offline | 82 passed, 0 failed |
| Before: Pulse live | 94 passed, 0 failed after network permission; initial sandbox run failed DNS for all sources |
| After: Pulse offline | 97 passed, 0 failed |
| After: Pulse live | 109 passed, 0 failed |
| Live source counts | Federal Register 35; FDIC 25; NIST 8; Federal Reserve 15; 60 returned articles |
| Browser filtering | All 42 topic/type combinations exercised; totals match cards and both selected facet counts; focus retained |
| Browser lead / links | Ranked lead rendered; 60 unique editorial/desk cards and four Radar entries; rendered article anchors use HTTPS, new tabs, safe rel attributes |
| Responsive Chrome | 1440, 1280, 1024, 820, 390px: page overflow 0; desk columns 3/3/2/2/1 |
| Simulated states | Loading, empty, HTTP 503, degraded/stale source, and malicious HTML/JavaScript URL all handled |
| Navigation | Assistant, Library, Messages, Governance, Pulse visited; Pulse DOM removed when navigating away; no uncaught browser exceptions observed |
| API boundary | `/api/pulse?limit=3` 200; limit 0 and 999: 422; `/api/pulse/health` 200 |
| Other read-only APIs | `/health`, `/users`, `/roles`, `/categories`, `/policies`, `/dashboard/policy-health`: 200 |
| JavaScript syntax | `node --check` passed for Pulse and browser test runner |
| Existing incident suite | `tests/test_week8_stage1.py`: 3 passed, 6 failed (missing `incident_guidance`, response/fixture mismatches in unchanged incident code) |
| Existing auth suite | `tests/test_week7_auth.py` cannot start: `ModuleNotFoundError: jwt` in current virtualenv |

No live writes were performed by these checks. API checks issue GET requests only;
the existing incident suite substitutes a fake database session. Broader failures
were reported without modifying unrelated application code.

Reproduce from `derexi-policy-pilot/backend/`:

```sh
../.venv/bin/python tests/test_pulse.py
../.venv/bin/python tests/test_pulse.py --live
# Start the app separately; default browser test URL is localhost:8013.
../.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8013
# In another terminal, with headless Chrome CDP available on port 9222:
node tests/test_pulse_browser.mjs
```

The browser runner supports `PULSE_TEST_URL`, `PULSE_SCREENSHOTS`, and
`PULSE_TEST_REPORT`. It uses a test browser profile and simulated in-page fetches,
then reloads the application to restore real requests. Do not run in a browser
session containing unsaved work. Live feed counts naturally change.

## Evidence and limitations

See [Phase 3 screenshot checklist](screenshots/phase3/README.md). Screenshots show
actual browser output; simulated failures do not imply an agency outage.

- Chrome emulated viewports only; Safari, Firefox, physical devices, and screen
  readers have not been tested. Visual contrast has not had a full automated audit.
- Browser tests check link construction and provenance; they do not independently
  open every agency publication or verify legal content or image reuse licenses.
- Backend cache remains 30 minutes, client cache 60 seconds; Refresh bypasses the
  client cache but does not force agency downloads inside the server cache window.
- Topic matching and inferred guidance remain conservative heuristics, not legal
  analysis. Radar is a small global curated set intersected with active filters;
  a filtered selection can have no Radar prompts even when it has articles.
- Large official headlines remain intact and can produce tall lead cards. The desk
  uses row-based Grid with varying card heights, not tightly packed masonry.
- Recovery snapshot: `/private/tmp/derexi-pulse-phase3-baseline/` contains the
  pre-edit Pulse JS, CSS, service, test, and tracked diff. Temporary files are not
  permanent backups. Prior uncommitted work remains in the working tree.

Future work: cross-browser/accessibility review, richer source-provided topic
metadata, pagination, explicit cache-age presentation, and separately addressing
the existing incident/auth test environment. Any future institution-specific
obligation analysis or assignment workflow needs its own scope and validation.
