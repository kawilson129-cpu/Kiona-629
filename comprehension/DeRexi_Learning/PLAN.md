# Learning Plan | APIs and RSS for DeRexi Pulse

**Student:** Kiona Wilson  
**Plan documented:** 2026-11-05  
**Chosen technology:** HTTP APIs (typically JSON) + RSS 2.0 / XML feeds  
**Capstone:** DeRexi; feature: Pulse

## Student commitment
I will work in small, testable steps, separate successful demonstrations from planned behavior, and keep evidence links and test output in `learning/README.md`.

## Why I chose these technologies
A fintech-facing policy governance product needs a reliable way to notice new guidance and announcements without requiring users to visit many sites manually. Public APIs and RSS feeds provide a practical, low-cost way to aggregate official updates into DeRexi Pulse, while keeping compliance decisions with human policy owners.

## Three integration tasks

### Task 1 — Retrieve public data
- **Description:** Request an available official public RSS or JSON source and capture a sample response.
- **Start:** 2026-10-21; **target:** 2026-11-05.
- **Success criterion:** At least one source responds with a parseable record containing a title and source link.
- **Proof:** Sanitized terminal output, source URL, timestamp, and screen capture.
- **Starting location:** DeRexi codebase, `pulse/` integration area; exact branch to be recorded.
- **Status:** Sources were explored; reproducible live test evidence still to attach.

### Task 2 — Normalize and display
- **Description:** Convert differing RSS/XML and API/JSON records into one shared article model and render source cards.
- **Start:** 2026-10-29; **target:** 2026-11-05.
- **Success criterion:** Sample items appear with title, publisher, date, category, and original link; missing optional fields do not crash the page.
- **Proof:** Pulse UI screenshot and actual test output.
- **Status:** UI development underway; final verification pending.

### Task 3 — Validate and explain
- **Description:** Document a beginner tutorial and check error handling, source attribution, and the distinction between a news item and binding regulation.
- **Start:** 2026-11-03; **target:** 2026-11-05.
- **Success criterion:** Another learner can explain API vs RSS and reproduce a safe local feed-read example; documented failure behavior is tested.
- **Proof:** `TUTORIAL.md`, peer review note, and real test log.
- **Status:** Tutorial drafted; peer and live validation pending.

## Risks and blockers
- Public URLs and formats may change; official sites may apply throttling or block automated requests.
- Some sources provide news rather than legal requirements; human interpretation is essential.
- Dates, categories, or article summaries may be missing or inconsistent.
- Third-party RSS aggregators can have free-tier limits; preserve source attribution.
- External content is untrusted; sanitize display and do not treat feed text as executable instructions.

## Timeline
- **Week 1 (Oct 21–25):** Select technology and explore official sources.
- **Week 2 (Oct 26–Nov 1):** Explore Pulse designs and aggregation options.
- **Week 3 (Nov 2–5):** Refine integration, document how the tools work, collect proof.
- **Next validation step:** Re-run tests, record outputs, and attach exact repository evidence before claiming completion.
