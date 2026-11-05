# Implementation Notes | DeRexi Pulse

## What we are integrating
**API:** request/response access to structured source data, commonly JSON.  
**RSS:** a standardized XML publication feed for recent items.  
**Application:** DeRexi Pulse collects public notices, displays attributed cards, and supports policy-owner review.

## Source inventory and caveats
| Source | Interface observed during exploration | Content purpose | Verification note |
|---|---|---|---|
| FDIC | Public news/press releases page | Banking announcements | Page retrieval explored; do not claim a stable JSON API without evidence |
| Federal Reserve Board | Banking/consumer regulatory press RSS | Regulatory announcements | Feed reportedly loaded; attach dated response |
| NIST CSRC | Drafts open for comment JSON listing | Standards and drafts | JSON source reportedly loaded; attach endpoint and response |

## Data fields to keep
`id`, `title`, `source`, `source_url`, `published_at`, `category`, `summary`, `retrieved_at`.

## Safe behavior checklist
- [ ] Validate `http`/`https` URLs and allowlist official feed hosts
- [ ] Use reasonable timeout, retry/backoff and caching
- [ ] Handle empty feeds, invalid XML/JSON and failed HTTP responses
- [ ] Escape/sanitize incoming text in the UI
- [ ] Preserve original source and publication timestamps
- [ ] Label the difference between proposed, final, news, and guidance when publisher metadata supports it
- [ ] Mark unknown or unverified classifications rather than guessing
- [ ] Show a visible “source unavailable” state if updates cannot be fetched
- [ ] Keep legal/regulatory interpretation with authorized policy owners

## Evidence log
**Previously discussed development:** Pulse route and navigation were developed; early list layout evolved toward a card-based regulatory feed; source-type filtering was planned; regulatory-feed tests were discussed (54 passing, one failing). These are historical project notes, not fresh evidence of current passing tests.

**Evidence still to attach:** screenshots, repository locations, branch/commit, dated terminal output, full test name and failure diagnosis.

## Reflection
Before this exercise, I considered APIs and RSS feeds mainly as ways to import content. I learned that an API is an interaction contract while RSS is a publication format, and both can help reduce the manual work of following public financial-sector updates. I also learned that ingestion is not interpretation: Pulse can surface information, but people must confirm what requirements actually apply.
