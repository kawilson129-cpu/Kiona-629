# Phase 4 — Content-aware bento packing for the lower feed

Implemented November 10, 2026. Phase 1–3 documentation and screenshots remain
intact; those results describe the earlier interface.

## Objective and scope

The Pulse page has two article regions: the editorial selection at the top
(espresso lead, spotlights, On the Radar) and the lower feed titled **The
Intelligence Desk** (`.pulse-river > .pulse-feed`). Phase 3 rendered that lower
feed as a normal CSS Grid of equal-height rows. Because the desk cards have very
uneven content — a two-line headline with no dek next to a headline plus a long
abstract — every row stretched to its tallest card. The result was large empty
blocks under short cards, the one visible layout defect left in the page.

Phase 4 changes **only that lower feed**. The masthead, lead, spotlights, On the
Radar, facets, source strip, navigation, backend endpoints, cache, and database
were not modified. No Supabase record, migration, or seed was touched. Nothing
was committed or pushed.

## Approach

The requirement was a bento/masonry arrangement that keeps natural card heights,
never clips text, keeps reading order intact, and reflows on filter change,
refresh, and resize.

Three candidate techniques were implemented or evaluated and two were rejected:

| Technique | Verdict |
|---|---|
| CSS multi-column masonry (`columns: 3`) | Rejected. Column order becomes vertical, which breaks left-to-right reading order, and a card that does not fit the remaining column height is pushed to the next column, leaving a real hole. |
| `grid-auto-flow: dense` with per-card row spans | Rejected. Dense packing is greedy: it backfills only when a later card happens to fit an earlier hole, so holes remain in mixed-length feeds. |
| Two-column tiles for emphasis | Rejected. A 2-of-3 span always leaves a gap under whichever of the two columns is shorter, which is the exact defect being removed. |
| **Explicit shortest-column packing (implemented)** | Each card is measured once and placed in the column that currently ends highest, starting exactly where that column finished. No column can contain a hole, and no card is resized after measurement. |

Implementation details that make the packing exact rather than approximate:

- `BENTO_ROW = 2`. In packed mode the grid collapses to 2px auto rows
  (`grid-auto-rows: 2px; row-gap: 0`) and each card's row span is
  `ceil((height + gutter) / 2)`. An 18px gutter is baked into each card's
  `margin-bottom`, so a placement matches the measured height to within 2px
  instead of rounding up to a full auto row (~40px of slack per card).
- `BENTO_GUTTER = 18` matches both the column gap and the card margin, so
  horizontal and vertical gutters stay visually equal (measured 17–20px in the
  browser, the small variance being sub-pixel rounding).
- Cards keep their natural height. No `max-height`, no line clamp, no
  `overflow: hidden`, so long headlines and deks are never cut off.
- The DOM is never reordered. Tab order, screen-reader order, and the ranked
  reading order are unchanged; only the visual grid placement moves, so the
  layout can never contradict the content order.
- One intentional span: the first desk card is the highest-ranked remaining
  story and becomes a full-width opener, applied **only** at three columns. At
  two columns and one column every card is a single tile, so tablet and phone
  layouts stay readable rather than squeezing a wide headline.

Re-packing is idempotent and triggered by every state change that can alter card
heights:

- after each render, once the feed is in the document and heights are real;
- on filter change and Refresh, which rebuild the feed from scratch;
- on a `ResizeObserver` width change of the feed itself;
- on window `resize` (rAF-throttled), because headline type uses `vw`-relative
  `clamp()`: card heights change with viewport width even when the capped
  1032px content column keeps the same computed width;
- on `document.fonts.ready`, because webfonts settle after first paint and
  change measured heights.

A single window-level hook and a single observer are reused
(`window.__derexiPulseBento`, `window.__derexiPulseBentoBound`), so re-mounting
the view — or re-importing the module in a test — never stacks listeners.
Before packing, every pass clears the previous inline placement, so each run
starts from the plain grid and converges on the same result.

The base stylesheet keeps a plain three-column grid (two on tablet, one on
phone) as a no-JS/early-paint fallback. The `.is-bento` class is added by
JavaScript only when the measured column count is two or more; a single column
is already an exact stack and needs no packing.

## Code guide

- `backend/static/pulse.js`
  - `columnCount(feed)` reads the computed `grid-template-columns` so the
    packing follows the CSS breakpoints rather than duplicating them in JS.
  - `opensDesk(index)` decides the single intentional full-width span
    (`index === 0`) **before** measurement, so no card is ever re-widened after
    its height is known (which would leave a stale row span).
  - `layoutFeed(feed)` clears prior placement, measures each card once, and
    assigns explicit `grid-column`/`grid-row` start and span values using
    shortest-column packing. It returns early for a single column.
  - `watchFeed(feed)` installs the throttled window resize hook and the
    width-only `ResizeObserver`; height-only notifications are ignored because
    they originate from the placement itself and would loop.
  - `watchFonts(feed)` re-packs after `document.fonts.ready`.
  - `paint()` adds `.is-wide` to desk index 0 and calls
    `layoutFeed` / `watchFeed` / `watchFonts` after the feed is appended.
  - The block comment above the implementation documents the packing rule and
    why the rejected techniques were rejected.
- `backend/static/style.css` — commented "The Intelligence Desk" section: the
  base three/two/one-column grid, the `.is-bento` packed-mode rules, the
  `.is-wide` opener typography scoped to `min-width: 1101px`, and the unchanged
  card surfaces, badges, hover elevation, and focus rings.
- `backend/tests/test_pulse_feed_layout.mjs` — new dependency-free Node/Chrome
  CDP runner. It mounts the real Pulse module against the real stylesheet with
  a stubbed `/api/pulse` payload, so no agency request is repeated and nothing
  is written. 40 checks plus optional screenshot capture.

No backend, API, schema, or database file was changed by this phase.

## Executed tests

Run from `derexi-policy-pilot/` with the app already running on `:8000`, a
headless Chrome CDP endpoint on `:9222`, and a signed-in demo session (the Week 9
sign-in gate is removed inside the test page only):

| Check | Observed result |
|---|---|
| New lower-feed layout runner | **40 checks, 40 passed, 0 failed** (exit 0) |
| Desktop 1440px | 3 columns, 57 desk cards, 1 full-width opener, gutters 18–20px, overlaps 0, clipped 0, page overflow 0 |
| Stress feed (57 mixed-length cards) | Every card placed; height variance from measurement ≤ 2px; column bottoms ragged by 430px (normal masonry tail); DOM order still top-down |
| Tablet 820px | 2 columns, no full-width opener, gutters 18–20px, overlaps 0, clipped 0 |
| Phone 390px / 560px | 1 column, uniform 18px gutters, no overflow |
| Filter change | 24 cards rebuilt, all 24 re-packed, gutters 17–19px |
| Refresh | 24 cards rebuilt and re-packed |
| Resize 1280 → 390px | Columns 3 → 2 → 2 → 1 → 1; no overlap, clipping, or page overflow at any width |
| Text clipping | 0 clipped cards at every tested width (no clamp, no max-height) |
| Uncaught Pulse exceptions | None. Two unrelated shell exceptions (`ps.forEach`, `cats.forEach` in `app.js` against an unavailable Library backend) are printed as a NOTE and are pre-existing. |
| Pulse offline suite | `tests/test_pulse.py`: 97 passed, 0 failed |
| Pulse live suite | `tests/test_pulse.py --live`: 109 passed, 0 failed |
| Existing compliance audit suite | `tests/test_c03_audit.py`: 54 passed, 1 failed (pre-existing C03-54 publisher host binding; unrelated to layout) |
| Legacy browser runner | `tests/test_pulse_browser.mjs` fails identically on unmodified Pulse code (Week 9 sign-in gate). Proven by stashing the two changed files, re-running, and restoring them. It was not "fixed" by this phase. |
| JavaScript syntax | `node --check backend/static/pulse.js` passed |
| Navigation integrity | Assistant, Library, Messages, Governance, Pulse visited at `/ui/`: Pulse DOM removed on navigate-away, no Pulse DOM leakage into other views |

Reproduce:

```sh
cd derexi-policy-pilot
# app running on :8000, headless Chrome CDP on :9222
PULSE_TEST_URL=http://127.0.0.1:8000 \
PULSE_SCREENSHOTS=/private/tmp/pulse-bento \
node backend/tests/test_pulse_feed_layout.mjs
```

The runner requires a page tab in the CDP endpoint and rewrites the gate and
`#app` state inside that tab only. Use a test browser profile.

## Evidence and limitations

See [Phase 4 screenshot checklist](screenshots/phase4/README.md). Screenshots are
actual headless-Chrome captures, not mockups.

- **Ragged column tails are intended.** Packing removes *internal* gaps, but the
  three columns rarely end at exactly the same height. At 1440px the last
  column bottoms differ by roughly 430px on a 57-card feed. Filling that would
  require either changing card heights (clipping) or reordering the feed
  (breaking reading order), so it is left as normal masonry behaviour.
- **JavaScript-dependent enhancement.** Without JavaScript, or before the first
  pack, the desk is a plain row grid — correct and readable, but with the
  original row-height gaps. Nothing is hidden or unreadable in that state.
- **Chrome emulated viewports only.** Safari, Firefox, physical devices, and
  screen readers were not tested in this phase.
- **Viewport-driven repacking depends on a resize event.** Resizes that change
  the content width without firing `resize` (for example, some zoom paths) rely
  on the `ResizeObserver` feed-width check.
- **Card heights are measured, not predicted.** If a card grows after packing
  without a resize, filter change, or font settle — for example, an image or
  embed loading late — its column can show slack until the next pack. Pulse
  cards contain no late-loading media, so this is theoretical today.
- The two pre-existing `app.js` exceptions and the C03-54 audit failure exist
  independently of this change and were reported, not fixed.
- Recovery: the change is confined to `pulse.js` and `style.css`; reverting
  those two files restores Phase 3 exactly. Prior uncommitted Week 9 work
  remains in the working tree and was not touched.

Future work: measure and pack in the same frame as card creation using
`ResizeObserver` on individual cards, evaluate a CSS `masonry` value once it
ships broadly, and add a visual regression pass across browsers.
