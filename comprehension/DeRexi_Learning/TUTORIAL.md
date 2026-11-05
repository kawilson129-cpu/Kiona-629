# Mini-Tutorial | APIs and RSS Feeds for DeRexi Pulse

**Audience:** Beginners in cybersecurity, backend development, and compliance.  
**Authored by:** Kiona Wilson  
**Date:** 2026-11-05  
**Validation:** Documentation example; confirm live output on your machine.

## What this teaches
An **API (Application Programming Interface)** defines how one program requests information or actions from another program. Many web APIs return **JSON** over HTTP. An **RSS feed (Really Simple Syndication)** is a periodically updated XML document listing items such as news articles or notices. DeRexi Pulse can read both, normalize the content, and display updates to policy owners.

## Use case
- [x] Cybersecurity and governance
- [x] Backend integration
- [x] Compliance monitoring / research
- [x] Data validation and source attribution

### Two simple analogies
- **API:** Ordering at a counter: you make a specific request; a service returns a response.
- **RSS:** Subscribing to a bulletin: the latest headlines are published in a predictable format.

## Understand the formats
**Example JSON from a web API** (illustrative, not a real NIST response):
```json
{"title":"Draft guidance published","source":"Example Agency","published":"2026-11-05","url":"https://example.org/notice"}
```

**Example RSS/XML item** (illustrative, not a real Federal Reserve response):
```xml
<item>
  <title>New public notice</title>
  <link>https://example.org/notice</link>
  <pubDate>Thu, 05 Nov 2026 12:00:00 GMT</pubDate>
</item>
```

Both can be converted into the same Pulse fields: **title, source, published date, URL, content type, and optional summary**.

## Quick setup
Requires Python 3.10+ and internet access only for the optional live-source experiment.
```bash
python3 -m venv .venv
source .venv/bin/activate          # Mac/Linux
# On Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install requests feedparser
```

## Step-by-step: safely read a feed
1. Create `read_feed.py` and paste the example below.
2. Run `python read_feed.py`.
3. Examine each item's title and link. If the public feed URL changes or access fails, use the source's current official feed directory and update `FEED_URL`.

```python
import feedparser
import requests

# Public example feed; confirm its present availability at the publisher site.
FEED_URL = "https://www.federalreserve.gov/feeds/press_bcreg.xml"

try:
    response = requests.get(FEED_URL, timeout=10, headers={"User-Agent": "DeRexi-learning-demo/1.0"})
    response.raise_for_status()  # A failed HTTP response should not look like success.
    parsed = feedparser.parse(response.content)
    if parsed.bozo and not parsed.entries:
        raise ValueError("Feed could not be parsed")
    for entry in parsed.entries[:3]:
        print({"title": entry.get("title", "Untitled"),
               "url": entry.get("link", ""),
               "published": entry.get("published", "Unknown")})
except (requests.RequestException, ValueError) as error:
    print(f"Source temporarily unavailable: {error}")
```

## What you should see
On success: up to three dictionaries with a **title**, **original URL**, and **published** field. On failure: a readable unavailable-source message instead of a broken app. Actual results vary by date and source; this document does not claim the example was executed.

## How Pulse uses this
1. **Fetch** public source feeds or JSON endpoints.
2. **Parse** RSS/XML or API/JSON.
3. **Normalize** disparate field names into a consistent article record.
4. **Validate** links, dates, content lengths, and missing fields.
5. **Display** dated, attributed cards in Pulse with type filters.
6. **Review** official primary-source material before any policy action.

## Pro tips / edge cases
- A **200 OK** HTTP response means the request succeeded, not that content is trustworthy or legally binding.
- RSS is usually pulled on a schedule; it does **not** automatically push a notification to the app.
- Never insert remote feed HTML without sanitizing it; don't place secrets in client-side code.
- Never treat an agency press release as proof of a specific effective regulatory obligation.
- Use HTTPS, timeouts, limited retries, caching, and source-specific rate limits in production.

## Mini knowledge check
1. Which format usually uses `<item>`: RSS/XML or JSON? **RSS/XML.**
2. What does `GET` do? **Requests a resource from a server.**
3. Is every RSS feed an API? **Not necessarily; RSS is a feed format, while API describes an interface. Both can be retrieved via HTTP.**
4. Does a new Pulse card mean the bank must update a policy? **No. Human review is required.**

## Learn more
- [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [MDN JSON](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON)
- [RSS 2.0 specification](https://www.rssboard.org/rss-specification)
- [Federal Reserve RSS feeds](https://www.federalreserve.gov/feeds/)
- [NIST CSRC](https://csrc.nist.gov/)
