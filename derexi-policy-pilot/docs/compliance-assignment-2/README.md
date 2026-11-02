# Pulse — Regulatory Intelligence

**Compliance Assignment 2 · DeRexi: Policy Pilot · Aurum Capital Bank**

Pulse is a read-only regulatory newsfeed inside DeRexi. It collects public
publications from four free government sources, normalizes them into one article
format, classifies each item honestly, and presents them on an editorial page at
**`/ui/#pulse`** with the nav label **Pulse**.

This deliverable documents the second phase of the existing Pulse feature:
hardening the backend, correcting date parsing, tightening relevance and
classification, building the editorial view, and testing all of it for real.

> Scope discipline: no Supabase table, migration, seed, RLS policy, secret, or
> policy record was changed. Nothing was committed or pushed. No paid API,
> account, or key is used.

---

## 1. Why it exists

Policy owners at a bank have to notice external change before it becomes an
internal problem: a proposed rule, an enforcement action, a supervisory
statement, a draft standard. Today that work is manual browsing across agency
websites. Pulse puts those signals in one place, next to the policies they will
eventually affect, and always links back to the issuing agency's own page.

Pulse is deliberately **not** a summarizer and **not** an advisor. It does not
generate opinions about what a rule requires, and it never invents an effective
date, obligation, or story.

---

## 2. What the finished feature does

| Behavior | Implementation |
|---|---|
| Aggregates four free sources | Federal Register API, FDIC RSS, NIST CSRC JSON, Federal Reserve RSS |
| Normalizes everything | One article shape: `title`, `url`, `published`, `summary`, `source`, `agency`, `category`, `status`, `identifier`, `doc_type` |
| Parses dates correctly | ISO 8601 **and** RFC 822/2822 (`Fri, 30 Oct 2026 13:09:02 -0500`) — the original bug truncated these to `Fri, 30 Oc` |
| Rejects unsafe links | https only, dotted host required, no embedded credentials, fragment stripped, 2048-char cap |
| Strips feed markup | Tags removed, entities unescaped, whitespace collapsed — the API only ever returns plain text |
| Removes duplicate stories | By canonical URL, then by identical headline on the same day within a source |
| Sorts newest first | Undated items sort last instead of pretending to be new |
| Classifies with a fixed vocabulary | Six document statuses, five categories, both allow-listed |
| Fails per source | One broken feed degrades to a status line; the rest still render |
| Caches briefly | 30 minutes per source, with last-good-articles fallback marked stale |
| Renders an editorial page | Masthead, last-updated stamp, featured story, filterable newsfeed, source-status strip |

---

## 3. Architecture

```
backend/
├── pulse/
│   ├── __init__.py     # module docstring
│   ├── sources.py      # source registry + safe download (timeout, byte cap)
│   ├── service.py      # dates, text, URLs, classification, dedupe, cache
│   └── routes.py       # GET /api/pulse, GET /api/pulse/health
├── static/
│   ├── pulse.js        # Pulse view module (window.PulseView)
│   ├── app.js          # routes #pulse, nav auto-scroll
│   ├── index.html      # nav item + script tag
│   └── style.css       # Pulse section, nav media queries
└── tests/
    └── test_pulse.py   # 76 offline checks (+12 with --live)
```

Data flow:

```
sources.py  ──fetch──►  service.normalize()  ──►  per-source cache (30 min)
                                                        │
                            service.get_feed()  ◄────────┘
                     dedupe → sort → limit → response
                                                        │
                        routes.py  /api/pulse  ◄────────┘
                                                        │
                               pulse.js  render(feed)  ◄┘
```

Pulse logic never touches `main.py` beyond registering the router, and the view
module is self-contained so `app.js` stays a router rather than growing another
feature.

---

## 4. Endpoints

### `GET /api/pulse?limit=40`

Returns the combined feed. `limit` is validated by FastAPI (`ge=1`, `le=60`);
out-of-range values return **422** rather than silently clamping. Example,
truncated and annotated — live values change as the agencies publish:

```json
{
  "articles": [
    {
      "title": "Proposed Third-Party Risk Management Guidance",
      "url": "https://www.federalregister.gov/documents/...",
      "published": "2026-09-15",
      "summary": "The OCC, Board, FDIC, and NCUA invite comments on ...",
      "source": "Federal Register",
      "agency": "Treasury Department, Comptroller of the Currency, ...",
      "category": "Supervisory Guidance",
      "status": "Supervisory Guidance",
      "identifier": "<document number>",
      "doc_type": "Notice"
    }
  ],
  "total_normalized": 83,
  "sources": {
    "Federal Register": { "ok": true, "count": 35, "error": null },
    "FDIC": { "ok": true, "count": 25, "error": null },
    "NIST": { "ok": true, "count": 8, "error": null },
    "Federal Reserve": { "ok": true, "count": 15, "error": null }
  },
  "generated_at": "2026-11-02T16:49:24Z",
  "checked_at": "2026-11-02T16:53:24Z",
  "categories": ["Banking & Finance", "Regulations", "Cybersecurity", "Privacy & Data Protection", "Supervisory Guidance"],
  "statuses": ["Proposed Rule", "Final Rule", "Notice", "Supervisory Guidance", "Standards Draft", "General News"]
}
```

A failed source appears as `{ "ok": false, "count": 0, "error": "Timed out" }`
(next to the first token), or with `"stale": true` and its last-good count when
a refresh failed after an earlier success.

### `GET /api/pulse/health`

Module check only — confirms the router imports, lists the configured sources,
and reports the cache window. It does **not** hit the network.

---

## 5. Classification rules

Status is decided from evidence the source actually provides, never guessed:

| Source | Rule |
|---|---|
| Federal Register | Uses the API's `type` field (`Rule` → Final Rule, `Proposed Rule`, `Notice`, `Presidential Document` → Notice). A Notice whose headline/abstract is guidance language becomes **Supervisory Guidance**. |
| NIST | Always **Standards Draft** (the feed is drafts open for comment). |
| FDIC / Federal Reserve | Headline only: "final rule" → Final Rule, "proposed rule"/"notice of proposed rulemaking" → Proposed Rule, guidance language → Supervisory Guidance, otherwise **General News**. |

Category precedence is fixed and documented so a cyber *rule* is still a
Regulation:

1. NIST → Cybersecurity, or Privacy & Data Protection when privacy terms appear
2. Proposed Rule / Final Rule → **Regulations**
3. Supervisory Guidance → **Supervisory Guidance**
4. Cyber vocabulary → **Cybersecurity**
5. Privacy vocabulary → **Privacy & Data Protection**
6. Everything else → **Banking & Finance**

Why headline-only for RSS: the first version scanned body HTML. FDIC board
meeting notices embed agenda links whose labels contain the words "rule" and
"guidance", so ordinary press releases were being labeled Regulations. Body text
is now used only for the summary, and only a short cleaned lead-in may confirm
guidance phrasing.

---

## 6. Editorial decisions

These are judgment calls, stated so they can be challenged:

- **Query regulators, not the word "banking."** The Federal Register call asks
  for seven banking/fintech agencies (`federal-reserve-system`, `fdic`, `occ`,
  `cfpb`, `ncua`, `fincen`, `ffiec`) with `order=newest` and `per_page=100`.
  Full-text searching "banking" returned unrelated agencies that merely mention
  the word.
- **Curate routine Federal Register paperwork.** Information-collection
  clearances, bank-control lists, and holding-company formation lists are
  legitimate records but not regulatory intelligence. They are dropped by
  title pattern. Nothing is rewritten or hidden silently — this document is the
  record of the decision.
- **No invented summaries.** When a feed's description just repeats the
  headline (the Federal Reserve feed does this), the card simply shows no dek.
- **Featured story follows the active filter.** It is the lead of what you are
  currently looking at, not a fixed headline that ignores the filter.
- **Partial source states are visible.** If FDIC is down, the page says FDIC is
  down and shows the other three; if a stale copy exists, it says so.

---

## 7. Running it

```bash
cd derexi-policy-pilot
source .venv/bin/activate
uvicorn main:app --reload --port 8000   # from backend/
```

- Employee UI: `http://127.0.0.1:8000/ui/`
- Pulse: `http://127.0.0.1:8000/ui/#pulse`
- Feed: `http://127.0.0.1:8000/api/pulse?limit=5`

Tests:

```bash
cd backend
python tests/test_pulse.py          # 76 offline checks, no network/DB
python tests/test_pulse.py --live   # +12 checks against the four real feeds
```

---

## 8. Access and permissions

Pulse is readable by **every demo role** — Alex Chen, Jordan Rivera, Sam
Okonkwo, Maya Patel, Chris Tanaka — because regulatory awareness is not
role-restricted at a bank. The feature is read-only: there is no assign, edit,
delete, or acknowledge action, and the API has no write route.

Persona switching in the UI is a **local demo affordance** (a `localStorage`
key), not authentication. Nothing in Pulse is protected by it, and nothing about
Pulse should be read as an authorization boundary. Real authentication remains
unwired in the backend.

---

## 9. Known limitations

| Limitation | Effect |
|---|---|
| FDIC links resolve to `content.govdelivery.com` | The RSS feed supplies these URLs; Pulse preserves them rather than rewriting. They are the agency's own bulletin links. |
| Federal Reserve descriptions are headline-only | Cards for that source intentionally show no dek. |
| Four sources, no persistence | Nothing is stored; the feed is a live read with a 30-minute cache. No history or "since last visit" yet. |
| No full-text search of Pulse items | Filters only. Search would need an index and is future work. |
| Classification is keyword and type based | Honest but not semantic; a rule that never says "cyber" will not file under Cybersecurity. |
| Feed HTML is removed, not sanitized | Deliberate: the API returns plain text only and the UI uses `textContent`. |
| No source is authoritative for legal interpretation | Every card links to the original publication. |

---

## 10. Deliverable index

| File | Contents |
|---|---|
| `README.md` | This document — purpose, behavior, architecture, rules, decisions, limits |
| `integration-notes.md` | How Pulse hooks into DeRexi without disturbing it, plus security and rollback notes |
| `testing-results.md` | Executed tests only: offline suite, live suite, API boundaries, browser checks |
| `screenshots/` | Nine captures + a checklist marking which are automated and which are simulated states |

---

## Phase 3 — Editorial mosaic (November 2, 2026)

The earlier sections preserve Phase 1/2 implementation history. Phase 3 adds an
espresso lead, asymmetric spotlights, the Intelligence Desk, combined topic/type
facets, and a read-only On the Radar section. It also preserves explicit Federal
Register types and keeps press releases about rules classified as news.
See [Phase 3 implementation and executed tests](phase-3-editorial-mosaic.md) and
[Phase 3 screenshots](screenshots/phase3/README.md) for current behavior, evidence,
known limitations, and reproduction instructions.
