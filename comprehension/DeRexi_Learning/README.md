# DeRexi Pulse | Learning How to Learn

**Topic:** APIs + RSS Feeds  
**Capstone:** DeRexi — Policy Governance Assistant  
**Feature:** Pulse — Regulatory Intelligence Feed  
**Learning track:** Cybersecurity / Compliance / Backend Integration  
**Status:** Learning guide prepared; remaining test evidence must be verified against the working repository.

## Purpose
This folder documents how I learned to retrieve and display public regulatory updates with **Application Programming Interfaces (APIs)** and **Really Simple Syndication (RSS)** feeds. I applied the concepts to **Pulse**, a feature of DeRexi that helps policy owners discover developments relevant to banking and fintech policies.

**One-sentence explanation:** An API lets software request structured information from another service; an RSS feed publishes an automatically updated list of articles or notices that an application can read.

## Start here
- [PLAN.md](./PLAN.md) — why I chose this technology and three small, measurable integration tasks.
- [TUTORIAL.md](./TUTORIAL.md) — plain-language explanation, setup, example code, expected output, and troubleshooting.
- [NOTES.md](./NOTES.md) — implementation notes, quality and security considerations, and learning reflection.
- [REFLECTION.md](./REFLECTION.md) — what I learned, how it influenced Pulse, and what remains.
- **DeRexi_API_RSS_Learning_Guide.pdf** — companion designed guide (kept with the submission or linked from repository).

## What these technologies do in Pulse

```text
FDIC public releases ──────────┐
Federal Reserve RSS ────────────┼──> Fetch/parse -> Normalize -> Sort/filter -> Pulse cards
NIST CSRC public JSON ─────────┘                         |
                                            Human reviews significance
                                            and decides policy action
```

**Important:** Pulse is a regulatory *awareness* tool. A published item does not by itself prove that a legal requirement has changed or applies to an institution. A policy owner must confirm the primary source, effective date, jurisdiction, and applicability.

## Dated progress log

| Date | Task | Outcome | Evidence status |
|---|---|---|---|
| 2026-10-21 | Selected regulatory intelligence as a learning/integration use case | Identified API and RSS as fit for a free public-source feed | Project discussion; repository proof to attach |
| 2026-10-29 | Explored editorial/news-feed layouts for Pulse | Defined card-based presentation direction | Design evidence/screenshots to attach |
| 2026-11-03 | Continued Pulse integration and compliance documentation | Worked on data sources, filters, and role access | Implementation specifics require repository verification |
| 2026-11-05 | Drafted this learning guide and mini-tutorial | Explained API/RSS and mapped the concepts to Pulse | Documentation created; live test results not claimed |

### Evidence checklist
- [ ] Paste actual commit/branch/PR link(s)
- [ ] Screenshot a valid response from one selected source (omit any secrets)
- [ ] Screenshot Pulse cards showing item title, source, publication date, and type
- [ ] Capture a successful refresh and a handled failed-source response
- [ ] Record exact test command, execution date, and unedited output
- [ ] Have another learner follow the mini-tutorial and note unclear steps

## Learning summary
I can distinguish the two tools: **API** describes a way systems communicate; **RSS** is a standard feed format. An RSS URL can itself be fetched using HTTP, so these concepts work together rather than compete. The learning milestone is explaining data flow, recognizing JSON versus XML, and verifying that Pulse displays trustworthy source links and handles errors appropriately.

## References
- [Instructor's learning templates](https://github.com/kakradetome/dae-6-month-cohort-2/tree/main/learning)
- [MDN: HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [MDN: JSON](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON)
- [RSS 2.0 specification](https://www.rssboard.org/rss-specification)
- [FDIC news](https://www.fdic.gov/news)
- [Federal Reserve RSS feeds](https://www.federalreserve.gov/feeds/)
- [NIST CSRC](https://csrc.nist.gov/)
