
# backend/pulse/service.py
import re
import time
from datetime import datetime
from html import unescape
from threading import Lock

from .sources import SOURCES, fetch_source

CACHE_SECONDS = 1800  # 30 minutes
_cache = None
_cached_at = 0
_cache_lock = Lock()


def clean_text(value):
    """Remove HTML formatting from feed descriptions."""
    value = re.sub(r"<[^>]*>", " ", str(value or ""))
    return " ".join(unescape(value).split())


def make_article(source, title, url, date,
                 summary="", category="Banking & Finance",
                 status="News", identifier=""):
    if not title or not url or not url.startswith("https://"):
        return None

    return {
        "id": identifier or url,
        "title": clean_text(title),
        "url": url,
        "published": str(date or "")[:10],
        "summary": clean_text(summary)[:400],
        "source": source,
        "category": category,
        "status": status,
    }


def xml_value(item, field):
    """Read an RSS field, including namespaced Atom fields."""
    node = item.find(field)
    if node is None:
        node = item.find("{http://www.w3.org/2005/Atom}" + field)
    return (node.text or "").strip() if node is not None else ""


def normalize(source, data):
    articles = []

    if source == "Federal Register":
        for item in data.get("results", []):
            kind = item.get("type", "Notice")
            status = {
                "Rule": "Final Rule",
                "Proposed Rule": "Proposed Rule",
                "Notice": "Notice",
            }.get(kind, kind)

            article = make_article(
                source,
                item.get("title"),
                item.get("html_url"),
                item.get("publication_date"),
                item.get("abstract") or item.get("excerpts"),
                "Regulations",
                status,
                item.get("document_number"),
            )
            if article:
                articles.append(article)

    elif source == "NIST":
        for item in data.get("entries", []):
            article = make_article(
                source,
                item.get("title"),
                item.get("link"),
                item.get("published") or item.get("updated"),
                item.get("summary"),
                "Cybersecurity",
                "Standards Draft",
                item.get("id"),
            )
            if article:
                articles.append(article)

    else:
        # RSS items or Atom entries
        items = data.findall(".//item")
        if not items:
            items = data.findall(
                ".//{http://www.w3.org/2005/Atom}entry"
            )

        for item in items:
            url = xml_value(item, "link")
            if not url:
                link = item.find(
                    "{http://www.w3.org/2005/Atom}link"
                )
                if link is not None:
                    url = link.get("href", "")

            article = make_article(
                source,
                xml_value(item, "title"),
                url,
                xml_value(item, "pubDate")
                or xml_value(item, "published")
                or xml_value(item, "updated"),
                xml_value(item, "description")
                or xml_value(item, "summary"),
                "Banking & Finance",
                "News / Guidance — Review",
                xml_value(item, "guid"),
            )
            if article:
                articles.append(article)

    return articles


def get_feed():
    """Retrieve, combine, and temporarily cache Pulse updates."""
    global _cache, _cached_at

    with _cache_lock:
        if _cache is not None and (
            time.monotonic() - _cached_at < CACHE_SECONDS
        ):
            return _cache

        articles = []
        source_status = {}

        for name in SOURCES:
            try:
                raw = fetch_source(name)
                items = normalize(name, raw)
                articles.extend(items)
                source_status[name] = {
                    "ok": True,
                    "count": len(items),
                }
            except Exception as exc:
                source_status[name] = {
                    "ok": False,
                    "error": type(exc).__name__,
                }

        # Remove duplicate source links.
        unique = {}
        for article in articles:
            unique[article["url"]] = article

        articles = list(unique.values())
        articles.sort(
            key=lambda a: a["published"],
            reverse=True,
        )

        result = {
            "articles": articles[:20],
            "total_normalized": len(articles),
            "sources": source_status,
            "generated_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        }

        # Don't overwrite a successful cache with total failure.
        if articles or _cache is None:
            _cache = result
            _cached_at = time.monotonic()

        return _cache
