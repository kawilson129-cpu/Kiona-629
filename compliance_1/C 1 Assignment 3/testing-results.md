# Testing Results

Everything below was executed on **November 2, 2026** against the running
application. Only observed results are reported; nothing here is projected.

- Environment: macOS, Python 3.9.6 in `derexi-policy-pilot/.venv`, FastAPI +
  uvicorn on `http://127.0.0.1:8000`, Chrome 156 (headless, CDP on port 9222).
- Test command: `python tests/test_pulse.py` (offline) and
  `python tests/test_pulse.py --live` (real network), run from `backend/`.

---

## 1. Offline suite — `python tests/test_pulse.py`

Synthetic payloads only: no network, no database, no Supabase project, no API
key. Exits non-zero on any failure.

```
RESULT: 76 passed, 0 failed
```

| Group | Checks | What is pinned |
|---|---|---|
| `[dates]` RSS and ISO parsing | 11 | RFC 822 (`Fri, 30 Oct 2026 13:09:02 -0500`), GMT variant, ISO date, ISO datetime with and without `Z`, long and short month names, empty, `None`, garbage, and an impossible date (`2026-13-45` → `""`) |
| `[text]` markup, URLs, summaries | 11 | Tag stripping, entity unescaping, escaped angle brackets preserved as text, https accepted, `http`/`javascript:`/credentials/relative rejected, feed kicker removed, duplicated headline dropped, truncated-headline description suppressed, `None` safe |
| `[classification]` status + category | 16 | FR Rule/Proposed/Notice, Presidential Document → Notice, guidance notice → Supervisory Guidance, NIST → Standards Draft, FDIC board notice with rule words **in the body** → General News, FDIC supervisory-appeals release → General News, FDIC guidance headline → Supervisory Guidance, Fed final-rule headline → Final Rule, all statuses inside the allow-list, cyber rule still files under Regulations, NIST privacy draft, unrelated release → Banking & Finance |
| `[normalize]` per-source shaping | 22 | FR keeps substantive documents, drops routine paperwork notices, drops unsafe http links, carries agency, emits ISO dates, keeps the document number; NIST draft fields/status/category/date; FDIC items parsed, title prefix removed, RSS date parsed, body markup removed, duplicate headline removed from summary, board notice not a rule, guidance headline recognized; Fed parsed, headline-only description becomes empty summary, final rule detected, date normalized; article shape has no unexpected fields |
| `[feed]` dedupe, order, failure, cache | 16 | Combined feed non-empty and newest-first, four sources reported, all ok, no duplicate URLs, ISO UTC `generated_at`, limit clamps, second call served from cache, cache window is 30 minutes, a single failing source does not fail the feed, that source is flagged and explains itself, healthy sources unchanged, empty sources are not errors, empty feed still returns a full response shape |

The date group is the regression that matters most: the original code turned
`Fri, 30 Oct 2026 13:09:02 -0500` into `Fri, 30 Oc`, which is why FDIC and
Federal Reserve items previously had unusable dates.

---

## 2. Live suite — `python tests/test_pulse.py --live`

Adds 12 checks that hit the four real government endpoints and validate the
combined feed.

```
RESULT: 88 passed, 0 failed

Federal Register   count=35 ok=True
FDIC               count=25 ok=True
NIST               count=8  ok=True
Federal Reserve    count=15 ok=True

category counts: {'Banking & Finance': 27, 'Regulations': 23, 'Cybersecurity': 4,
                  'Privacy & Data Protection': 3, 'Supervisory Guidance': 3}
status counts:   {'Proposed Rule': 15, 'Final Rule': 8, 'Notice': 10,
                  'Supervisory Guidance': 3, 'Standards Draft': 5, 'General News': 19}
```

Live assertions: feed non-empty, all four sources reachable, every date ISO or
empty, every URL https, titles and summaries contain no markup, every article has
a known category and a known status, feed is newest-first.

### Feed composition at test time

| Measure | Observed |
|---|---|
| Articles normalized | 83 |
| Articles returned (`limit=60`) | 60 |
| Date range | 2026-09-04 → 2026-10-30 |
| Non-https URLs | 0 |
| Duplicate URLs | 0 |
| Cards with no summary (by design) | 10 |
| `generated_at` | 2026-11-02T16:49:24Z |

Ten empty summaries are expected, not a defect: the Federal Reserve feed's
description field repeats the headline, and `summarize()` returns `""` rather
than padding it with invented copy.

---

## 3. API boundary checks (curl against the running server)

| Request | Status | Result |
|---|---|---|
| `GET /api/pulse?limit=3` | 200 | 3 articles returned |
| `GET /api/pulse?limit=0` | 422 | rejected by `ge=1` |
| `GET /api/pulse?limit=999` | 422 | rejected by `le=60` |
| `GET /api/pulse/health` | 200 | `{"feature":"Pulse","status":"module loaded","sources":[...],"cache_seconds":1800}` |
| `GET /health` | 200 | unaffected |
| `GET /users` | 200 | unaffected |
| `GET /roles` | 200 | unaffected |
| `GET /categories` | 200 | unaffected |
| `GET /policies` | 200 | unaffected |
| `GET /dashboard/policy-health` | 200 | unaffected |

---

## 4. Browser checks (Chrome 156 headless over CDP)

Loaded `http://127.0.0.1:8000/ui/#pulse` and probed the live DOM.

### Rendering

- Page title renders as **Pulse**; tagline renders exactly
  `What's changing. What matters. What comes next.`
- Masthead, "Last updated Nov 2, 2026, 11:49 AM", **Refresh**, source strip, six
  filter chips, featured story, and newsfeed all present.
- 60 articles: 1 featured + 59 cards.
- Chip counts match the feed: All Updates 60, Banking & Finance 27,
  Regulations 23, Cybersecurity 4, Privacy & Data Protection 3,
  Supervisory Guidance 3.
- Source strip: Federal Register 35, FDIC 25, NIST 8, Federal Reserve 15.
- No console errors and no uncaught exceptions on load.

### Link and text integrity

- 120 anchors in the Pulse view — **120/120 https**, **120/120**
  `target="_blank"`, **120/120** `rel="noopener noreferrer"`.
- No `Invalid`/`NaN`/`undefined`/`[object Object]` in rendered dates or text;
  0 undated cards in the current feed.
- No horizontal page overflow at 1440px (`scrollWidth - clientWidth = 0`).

### Filters

All six chips were clicked and re-checked: the active chip changes, the list
re-filters, counts stay consistent, and the featured story's category matches the
active filter (verified on **Supervisory Guidance**, which leads with
"Proposed Third-Party Risk Management Guidance" — captured as screenshot 03).
No filter produced an error or a duplicate story.

### States

| State | How it was produced | Result |
|---|---|---|
| Partial / degraded sources | Fetch stub returning two healthy sources and two failures | Strip shows `FEDERAL REGISTER UNAVAILABLE · TIMED OUT` and `FDIC UNAVAILABLE · HTTP 503 · SHOWING LAST GOOD FETCH`; remaining articles still render (screenshot 08) |
| API error | Fetch stub returning HTTP 503 | "Pulse could not be reached" + **Try again**; no articles, no invented stories (screenshot 09) |
| Empty feed | Fetch stub returning zero articles | Empty state, no error styling |
| XSS payload | Stub article with `<img onerror=...>`, `<script>`, and a `javascript:` URL | No injected nodes, no `javascript:` href, no alert; markup rendered as inert text |

> Screenshots 08 and 09 are **simulated** by stubbing `fetch` in the browser.
> They demonstrate the UI's handling of those responses; they are not evidence
> that a real source failed during the run.

### Navigation and responsive layout

- Nav row at 1440: Policy Assistant, Policy Library, Messages, Governance,
  **Pulse**, persona, Change — one row, no scroll (`navOverflow = 0`).
- One row verified at 1440, 1280, and 1100; at 900 and below the row scrolls
  horizontally and the active item is scrolled into view.
- Tablet 820 and mobile 390: no page-level horizontal overflow; masthead,
  chips, featured card, and newsfeed cards stack cleanly (screenshots 05–07).
- Regression pass across `#assist`, `#library`, `#messages`, `#governance`, and
  `#pulse`: no console errors, and no Pulse DOM remained after navigating away.

---

## 5. Not tested

- Real authentication / authorization (Pulse is read-only and ungated by design;
  persona switching is a local demo key, not a session).
- Safari, Firefox, and real iOS/Android devices (Chrome 156 and emulated
  viewports only).
- Screen-reader walkthrough (semantic landmarks and alt text are present, but no
  assistive-technology pass was run).
- Long-running cache expiry beyond the 30-minute window in a live session (the
  window itself is asserted in the offline suite).
- Legal accuracy of any agency publication. Pulse reports what the source says
  and links to it; it does not interpret it.

---

## 6. Reproduce

```bash
cd derexi-policy-pilot
source .venv/bin/activate
cd backend
python tests/test_pulse.py          # expect: 76 passed, 0 failed
python tests/test_pulse.py --live   # expect: 88 passed, 0 failed (needs network)
```

With the server running, open `http://127.0.0.1:8000/ui/#pulse`. The counts will
differ from the numbers above because the feeds move — the assertions in the
live suite are what stay true.

## Phase 3 results addendum

The results above are preserved Phase 2 evidence. Current Phase 3 execution:
97 offline checks passed; 109 with live feeds passed; all four sources connected.
Browser checks exercised 42 facet combinations and five viewport widths with zero
page overflow. See [Phase 3 report](phase-3-editorial-mosaic.md) for the complete
results, the unrelated incident-suite failures and missing auth dependency, and
[Phase 3 screenshot evidence](screenshots/phase3/README.md).
