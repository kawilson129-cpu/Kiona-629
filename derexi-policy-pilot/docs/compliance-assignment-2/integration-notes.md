# Integration Notes

How Pulse attaches to the existing DeRexi application, what was touched, and how
to undo it. Evidence for every claim here is in `testing-results.md`.

---

## 1. Integration points

| Layer | File | Change | Risk |
|---|---|---|---|
| Router | `backend/main.py` | `from pulse.routes import router as pulse_router` + `app.include_router(pulse_router)` | None — additive mount, no existing route touched |
| Feed registry | `backend/pulse/sources.py` | Rewritten with comments, timeout, byte cap, agency-scoped FR query | Isolated module |
| Normalization | `backend/pulse/service.py` | Rewritten with comments: dates, text, URLs, classification, dedupe, cache | Isolated module |
| Endpoints | `backend/pulse/routes.py` | `/api/pulse` + `/api/pulse/health` | Additive |
| Nav | `backend/static/index.html` | `<a href="#pulse" data-view="pulse" class="nav-link">Pulse</a>` after Governance; `<script src="pulse.js">` | One link, one script tag |
| Router | `backend/static/app.js` | `#pulse` hash → `renderPulse(app)`; nav auto-scroll | ~25 lines, no existing view changed |
| View | `backend/static/pulse.js` | New self-contained module (`window.PulseView`) | New file |
| Styles | `backend/static/style.css` | Pulse section appended; nav media queries | Appended + 3 media-query blocks |
| Docs | `derexi-policy-pilot/README.md` | Pulse section, layout tree, curl example | Documentation only |

No change was made to: Supabase schema, migrations, seeds, RLS, `.env`, AI
provider config, `/ask`, retrieval, policy library, messages, governance
dashboard, incidents, roles, or persona switching.

---

## 2. Why Pulse is not in `app.js`

`app.js` already owns the policy assistant, library, messages, and governance
views. Adding network aggregation, filtering, featured-story selection, and
partial-source rendering there would have made one file responsible for two
unrelated concerns.

Instead:

- `pulse.js` exposes `window.PulseView.render(app)`.
- `app.js` only maps `#pulse` to `renderPulse()`, which mounts the module — and
  degrades to a plain "Pulse is unavailable, reload" card if the script fails to
  load.
- Pulse keeps its own state (feed, active filter, request generation counter)
  inside the closure, so navigating away and back cannot leak stale results.

---

## 3. Routing and navigation

- Pulse is a hash route: `/ui/#pulse`. It participates in the same
  `hashchange` render loop as the other views.
- The nav item is labeled exactly **Pulse** and sits directly after
  **Governance**.
- Nav stays on one horizontal row. At narrow widths it scrolls horizontally
  rather than wrapping or collapsing into a hidden menu, and the active item is
  scrolled into view (`navBar.scrollLeft`) so Pulse is reachable on a phone.
- Media queries: at ≤1500px the persona label is shortened, at ≤1340px links are
  compacted and the region label is hidden. Verified on one row at 1440, 1280,
  1100; horizontal scroll at 900 and below.
- Mobile letterhead: `.lh-sub` / `.lh-class` are hidden at ≤680px. This also
  removes a pre-existing 43px horizontal page overflow that affected every view,
  not just Pulse.

---

## 4. API contract the UI relies on

The view depends only on the documented response shape:

- `articles[]` — rendered in order; the first item becomes the featured story.
  Missing/empty `summary` omits the dek. Missing `published` shows no date.
- `sources` — drives the status strip. `ok: false` shows the error in red;
  `stale: true` adds "showing last good fetch".
- `checked_at` — the "Last updated" stamp.
- `categories` — used to order chips, but the UI also derives counts from the
  articles it actually received, so chips never claim items that are not shown.

`limit` is requested as 60 (the server maximum). Invalid `limit` values are
rejected by FastAPI with 422 — the UI never sends them, and the tests pin that
boundary.

---

## 5. Failure behavior

| Situation | What the user sees |
|---|---|
| One source times out / 5xx | Other sources render normally; that source is listed as unavailable with the reason |
| One source fails after a good fetch | Its last-good articles still render, labeled stale |
| Every source fails, no cache | Honest empty state — never placeholder stories |
| `/api/pulse` unreachable or 5xx | "Pulse could not be reached" card with a **Try again** button; no skeleton left spinning |
| Malformed record inside a feed | That record is skipped; the rest of the source survives |
| Feed returns zero usable items | Empty state, not an error |
| Slow request superseded by a refresh | Generation counter discards the older response |

Refresh is manual (the **Refresh** button) plus first load. Nothing polls.

---

## 6. Security notes

- **No feed HTML is trusted.** `clean_text()` strips tags and unescapes
  entities server-side; `pulse.js` builds nodes and assigns `textContent`. A
  stubbed article containing `<img onerror>` and a `javascript:` URL produced no
  injected nodes and no unsafe anchor.
- **Links are validated, not repaired.** `safe_url()` accepts only https, a
  dotted host, and no credentials; anything else becomes `""` and the card is
  dropped. Every rendered link opens in a new tab with
  `rel="noopener noreferrer"`.
- **Server-side fetching is bounded.** 12s timeout, 2 MB response cap,
  `Accept-Encoding: identity`, BOM strip, honest User-Agent, XML parsed with
  `xml.etree` (no DTD/entity expansion), JSON parsed defensively.
- **Read-only.** No write route, no database access from the Pulse module, no
  credentials, no API keys.
- **Caching is concurrency-safe.** A lock guards the cache dictionary only;
  network I/O happens outside it, so one slow feed cannot block other requests.
  Failed sources back off for the same 30-minute window instead of retrying on
  every request.

---

## 7. Persona switching is not authentication

Pulse is visible to every demo role and gated by nothing. The persona picker
writes `derexi.personaId` to `localStorage`; the server does not verify it.
Anyone who can load `/ui/` can read Pulse. This is stated in the project README
and in this document so nobody mistakes the picker for a security boundary —
the UI itself still labels the control "Signed in as", which is aspirational
copy, not an access control. Wiring a real session would require `auth.py` JWT
support, which is out of scope for this assignment.

---

## 8. Regression checks performed

All existing surfaces were re-exercised after the Pulse work: `#assist`,
`#library`, `#messages`, `#governance`, and back to `#pulse`. No console errors,
no Pulse DOM left behind after navigating away, and the existing endpoints
(`/health`, `/users`, `/roles`, `/categories`, `/policies`,
`/dashboard/policy-health`) all returned 200.

The only pre-existing defect observed is a `favicon.ico` 404 under `/ui/`, which
predates Pulse and was left alone.

---

## 9. Rollback

Pulse can be removed without touching data or other features:

1. Remove the `<a href="#pulse" …>` line and `<script src="pulse.js">` from
   `backend/static/index.html`.
2. Remove the `#pulse` case, `renderPulse()`, and the nav auto-scroll block from
   `backend/static/app.js`.
3. Delete `backend/static/pulse.js` and the appended Pulse CSS section.
4. Remove the two router lines from `backend/main.py` and delete
   `backend/pulse/` (or leave it — an unregistered router is inert).

No migration, seed, or stored row depends on Pulse, so there is nothing to
reverse in Supabase.

## Phase 3 addendum

See [Phase 3 notes](phase-3-editorial-mosaic.md) for the current frontend layout,
facet logic, classification provenance, Radar, and tests. The source fetchers and
cache windows are unchanged. Federal Register guidance notices now retain Notice;
RSS press releases announcing rules remain General News. Radar references are
restricted to returned articles. Earlier sections describe the Phase 2 baseline.
