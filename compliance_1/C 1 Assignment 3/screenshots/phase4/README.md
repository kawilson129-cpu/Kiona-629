# Phase 4 screenshot checklist

Captured in headless Chrome on November 10, 2026 at
`http://127.0.0.1:8000/ui/#pulse`, signed in as Maya Patel, against the real
`/api/pulse` payload. All files are actual browser screenshots. Phase 2 and
Phase 3 screenshots in the parent directory and `screenshots/phase3/` remain
unchanged evidence for those phases.

- [x] Intelligence Desk packed, desktop 1440px (3 columns, 1 full-width opener):
      `01-desk-bento-desktop-1440.png`
- [x] Desk mid-scroll — mixed card heights, no internal holes: `02-desk-mid-1440.png`
- [x] Desk bottom — packed columns and the ragged tail: `03-desk-bottom-1440.png`
- [x] Tablet 820px (2 columns, single tiles): `04-desk-bento-tablet-820.png`
- [x] Mobile 390px (1 column, uniform 18px gutters): `05-desk-bento-mobile-390.png`

Automated runner: `backend/tests/test_pulse_feed_layout.mjs` (40 checks) also
exercises 1280, 1024, 820, 560, and 390px, plus filter change, refresh, and a
57-card stress feed, asserting zero overlap, zero clipping, zero page overflow,
and gutters between 16 and 20px.

Manual follow-up: alternate browsers, physical devices, screen-reader review,
and a visual regression pass. Ragged column bottoms are expected masonry
behaviour and are documented as a limitation in
[Phase 4](../phase-4-lower-feed-bento.md).
