# Evidence index

Actual DeRexi verification, November 18, 2026. **15 HTTP + 7 browser checks PASS**.
Policy/auth records are synthetic SQLite fixtures; PostgreSQL search is mocked to
no matches, external AI/email disabled. Public Pulse feeds were actually fetched.

| File | Contents |
|---|---|
| [fixture.json](fixture.json) | Isolation/settings scope and original app source hashes |
| [http-results.json](http-results.json) | Actual loopback methods, URLs, redacted headers, bodies, statuses and assertions |
| [public-network.json](public-network.json) | Actual upstream URLs, timestamps, request headers and 200 statuses |
| [browser-results.json](browser-results.json) | Original UI network exchanges, response-to-DOM assertions, displayed text and capture labels |
| [01 — Library](screenshots/01-get-library.png) | Actual GET JSON rendered as policy rows |
| [02 — Assistant](screenshots/02-post-assistant.png) | Actual POST result rendered as plain-English guidance |
| [03 — Pulse](screenshots/03-get-pulse.png) | Real fetched source counts and regulatory article display |
| `attempts/initial-browser/` | Initial 6/1 assertion result and animation-timing captures, retained |
| `attempts/browser-timing/` | Initial 5/2 synchronization result, retained |
| [validation.json](validation.json) | Final links, evidence/source hashes, sanitization and syntax checks |
| [commands.txt](commands.txt) | Executed verification commands and cleanup record |

Screenshots are 1440×1000 Chrome captures with an added scope label. No synthetic
article data was substituted into Pulse and no product CSS was changed. The
Assistant's clarification does not demonstrate a live LLM response. No production
records, raw tokens, browser profiles or secret files are included.

## Assignment 1 report finalization — November 19, 2026

The [new two-page report](../../AI_API_Integration_1_Rubric_01_Report.pdf) reuses the
existing 200 GET/POST results, original UI images and separate 401 authentication
rejection. **No API tests or captures rerun.** User-referenced Swagger images were
not located and are not fabricated or counted as success evidence.
[Current finalization index](../finalization-20261119/README.md) and
[offline artifact checks](../finalization-20261119/validation.json).
Original machine results/images and their historical manifests remain unchanged.
