# Pulse Screenshots

Captured November 2, 2026 from the running app
(`http://127.0.0.1:8000/ui/#pulse`) with Chrome 156 headless over the DevTools
Protocol. All nine are real renders of the current code.

**Two captures are simulated states.** Items 08 and 09 stub `fetch` in the
browser to force a degraded feed and an HTTP 503. They prove the UI handles those
responses; they are not evidence that a government feed actually failed. Every
other capture is an unmodified live feed.

| # | File | Viewport | Shows |
|---|---|---|---|
| 01 | `01-desktop-masthead-featured.png` | 1440 | Page title **Pulse**, tagline, "Last updated" stamp, Refresh, source strip (35 / 25 / 8 / 15), six filter chips, featured story with the At a Glance panel |
| 02 | `02-desktop-newsfeed.png` | 1440 | Newsfeed cards: date + source rail, category and status stamps, summary dek, issuing agency, "Read original ↗" |
| 03 | `03-desktop-filter-guidance.png` | 1440 | **Supervisory Guidance** filter active — chip count 3, featured story changes to "Proposed Third-Party Risk Management Guidance", proving the featured slot follows the filter |
| 04 | `04-desktop-navigation-1280.png` | 1280 | Nav on one horizontal row with **Pulse** directly after Governance, plus the persona control |
| 05 | `05-tablet-820.png` | 820 | Tablet layout: masthead and featured card stack, nav still one row (scrolled to keep Pulse visible), no page overflow |
| 06 | `06-mobile-masthead-390.png` | 390 | Phone masthead: letterhead, persona bar, scrollable nav with Pulse active, title, tagline, updated stamp, chips |
| 07 | `07-mobile-newsfeed-390.png` | 390 | Phone newsfeed cards under the sticky topbar — readable serif headlines, single-column dek, source/agency lines |
| 08 | `08-feed-degraded-simulated.png` | 1440 | **Simulated** partial failure: Federal Register timed out, FDIC HTTP 503 with "showing last good fetch"; remaining articles still render |
| 09 | `09-api-error-simulated.png` | 1440 | **Simulated** total failure: "Pulse could not be reached", explanation, **Try again** button, no invented stories |

## Manual checklist (for a reviewer re-shooting these by hand)

- [ ] Load `/ui/#pulse` at 1440 — masthead, tagline, updated stamp, source strip, chips, featured story all visible
- [ ] Confirm the nav label reads exactly **Pulse** and sits immediately after **Governance**
- [ ] Click each of the six chips; confirm the list narrows and the featured card matches the filter
- [ ] Click **Refresh**; confirm the stamp updates and no duplicate cards appear
- [ ] Click any card's "Read original ↗"; confirm it opens the agency's own page in a new tab
- [ ] Narrow the window to ~900px; confirm the nav scrolls horizontally rather than wrapping
- [ ] Load at 390px; confirm no sideways scrolling of the page itself
- [ ] Toggle the OS "reduce motion" setting; confirm transitions are suppressed
- [ ] Optional: force a failure (throttle/offline in DevTools) to see the error card and Try again

## Not captured

- Hover and focus styling (static images cannot show it)
- Screen-reader output
- Safari/Firefox rendering
