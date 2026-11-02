"""Pulse: normalization, classification, and caching of regulatory updates.

``sources.py`` knows where the data lives; this module turns four very
different payloads (two JSON APIs, two RSS feeds) into one stable article
shape, then caches each source independently so a single failing endpoint can
never blank out the feed.

Article shape returned to the API and the UI::

    {
      "id":        "fdic-70314918",       # stable key for the DOM
      "title":     "FDIC Board ...",      # plain text, tags removed
      "url":       "https://...",         # original publication, https only
      "published": "2026-10-30",          # ISO date, "" when the source omits it
      "summary":   "Board approved ...",   # plain text, may be ""
      "source":    "FDIC",                # the feed the item came from
      "agency":    "Federal Deposit ...", # the issuing organization
      "category":  "Banking & Finance",   # one of CATEGORIES (UI filters)
      "status":    "General News",        # one of DOCUMENT_STATUSES
      "doc_type":  "Press release",       # the source's own label, when it has one
      "classified_by": "inferred",        # "source" or "inferred" (honesty flag)
      "score":     81.4                   # editorial rank, see relevance_score()
    }
"""

import json
import re
import socket
import time
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from threading import Lock

from .sources import SOURCES, fetch_source

# Per-source cache lifetime. Government feeds update a few times a day at most,
# so 30 minutes keeps the page fast without going stale.
CACHE_SECONDS = 1800

# Feed sizing. The UI shows a featured story plus a filterable list; 60 items is
# plenty and keeps the payload small.
MAX_ARTICLES = 60
DEFAULT_LIMIT = 40
SUMMARY_CHARS = 320
TITLE_CHARS = 300

# The five editorial buckets exposed as filters. They intentionally mix a
# document's nature (Rules, Guidance) with its subject (Cyber, Privacy); the
# classification order below makes that precedence explicit and stable.
CATEGORIES = (
    "Banking & Finance",
    "Regulations",
    "Cybersecurity",
    "Privacy & Data Protection",
    "Supervisory Guidance",
)

# Classification vocabulary. Anything outside this set is never sent to the UI.
DOCUMENT_STATUSES = (
    "Proposed Rule",
    "Final Rule",
    "Notice",
    "Supervisory Guidance",
    "Standards Draft",
    "General News",
)

# Federal Register document types. A "Presidential Document" is published as a
# notice-class document, not a rule, so it is reported as a Notice.
FR_TYPE_STATUS = {
    "Rule": "Final Rule",
    "Final Rule": "Final Rule",
    "Proposed Rule": "Proposed Rule",
    "Notice": "Notice",
    "Presidential Document": "Notice",
}

# Routine administrative notices that dominate the Federal Register (paperwork
# clearances, bank-control lists, holding-company formation lists). They are
# legitimate records but not regulatory intelligence, and repeating them would
# bury actual rules. This is editorial curation; nothing is altered or invented.
ROUTINE_FR_TITLE_PATTERNS = (
    "agency information collection",
    "change in bank control notices",
    "formations of, acquisitions by, and mergers of bank holding companies",
    "notice of proposals to engage in or to acquire companies",
    "applications for membership in the federal reserve system",
    "senior executive service performance review boards",
)

# Phrases that mark a document as supervisory guidance. Deliberately narrow:
# plain "statement" or "advisory" would mislabel advisory committees and
# speeches as guidance.
GUIDANCE_PHRASES = (
    "supervisory guidance",
    "issues guidance",
    "issued guidance",
    "final guidance",
    "proposed guidance",
    "interagency guidance",
    "guidance on",
    "guidance for",
    "guidance to",
    "policy statement",
    "interagency statement",
    "supervisory expectations",
    "advisory bulletin",
    "issues advisory",
    "financial institution letter",
    "fil-",
)

CYBER_TERMS = (
    "cyber",
    "malware",
    "ransomware",
    "phishing",
    "vulnerability",
    "zero trust",
    "encryption",
    "cryptograph",
    "authentication",
    "network security",
    "information security",
    "incident response",
    "supply chain",
    "artificial intelligence",
    "quantum",
    "secure software",
    "software security",
    "operational technology",
    "security control",
)

PRIVACY_TERMS = (
    "privacy",
    "personal data",
    "personally identifiable",
    "pii",
    "gramm-leach-bliley",
    "glba",
    "regulation p",
    "safeguards rule",
    "data protection",
    "data breach",
    "consumer data",
    "data security",
)

_TAG_RE = re.compile(r"<[^>]*>")
_WS_RE = re.compile(r"\s+")
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
# "Press Release: ..." is feed furniture, not part of the headline.
_TITLE_PREFIX_RE = re.compile(
    r"^(?:press release|media advisory|press advisory)\s*[:\-\u2014]\s*",
    re.IGNORECASE,
)
_GUIDANCE_WORD_RE = re.compile(r"\bguidance\b")
# Leading wire-service furniture in RSS descriptions, e.g.
# "PRESS RELEASE | OCTOBER 30, 2026 Title of the release ...".
_KICKER_RE = re.compile(
    r"^(?:press release|board meeting|media advisory|statement|speech|testimony)"
    r"\s*(?:\|\s*)?(?:[A-Z][A-Za-z]+\.?\s+\d{1,2},\s+\d{4})?\s*[|:\u2014\u2013-]?\s*",
    re.IGNORECASE,
)
_DATELINE_RE = re.compile(r"^washington(?:\s*[,.]?\s*d\.?c\.?)?\s*[\u2014\u2013-]\s*", re.IGNORECASE)

# source name -> {"articles": [...], "fetched_at": monotonic, "fetched_iso": str,
#                 "status": {...}}. The lock guards dictionary access only;
# network calls happen outside it so one slow feed cannot block other requests.
_cache = {}
_cache_lock = Lock()


# --------------------------------------------------------------------------
# Text and date helpers
# --------------------------------------------------------------------------
def clean_text(value, limit=None):
    """Strip markup and collapse whitespace; optionally truncate on a word.

    Tags are removed rather than escaped because the API returns plain text and
    the UI renders it with textContent, so no feed HTML is ever executed.
    """
    text = _TAG_RE.sub(" ", str(value or ""))
    text = unescape(text).replace("\u00a0", " ")
    text = _WS_RE.sub(" ", text).strip()

    if limit and len(text) > limit:
        cut = text[:limit]
        space = cut.rfind(" ")
        if space > limit * 0.6:
            cut = cut[:space]
        text = cut.rstrip(" ,.;:-") + "\u2026"
    return text


def parse_date(value):
    """Return an ISO ``YYYY-MM-DD`` date, or ``""`` when it cannot be trusted.

    Handles ISO timestamps (Federal Register, NIST) and RFC 822/2822 strings
    such as ``Fri, 30 Oct 2026 13:09:02 -0500``, which the first version of
    Pulse truncated to ``Fri, 30 Oc``.
    """
    if isinstance(value, datetime):
        return value.date().isoformat()

    text = str(value or "").strip()
    if not text:
        return ""

    match = _ISO_DATE_RE.match(text)
    if match:
        try:
            return datetime.strptime(match.group(0), "%Y-%m-%d").date().isoformat()
        except ValueError:
            return ""

    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is not None:
        return parsed.date().isoformat()

    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue

    return ""


def safe_url(value):
    """Return a cleaned https URL, or ``""`` if it is missing or unsafe."""
    text = str(value or "").strip()
    if not text or len(text) > 2048:
        return ""

    try:
        parts = urllib.parse.urlsplit(text)
    except ValueError:
        return ""

    host = parts.hostname or ""
    # https only, a real dotted host, and no embedded credentials.
    if parts.scheme != "https" or "." not in host or "@" in parts.netloc:
        return ""

    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path or "/", parts.query, "")
    )


def summarize(value, title=""):
    """Turn a feed description into a short, human-readable excerpt.

    Some feeds repeat or merely truncate the headline as their description, so
    a description that adds nothing returns ``""`` (the UI handles no-dek
    cards). Nothing is ever padded with invented copy.
    """
    text = clean_text(value)
    text = _KICKER_RE.sub("", text, count=1)
    text = _DATELINE_RE.sub("", text, count=1)

    headline = clean_text(title).lower().strip(" .")
    candidate = text.lower().strip(" .")

    # Nothing but the headline (or a truncated copy of it): no summary at all.
    if not candidate or candidate == headline or headline.startswith(candidate):
        return ""

    # Many press feeds repeat the headline as the first line of the body.
    if headline and candidate.startswith(headline):
        remainder = text[len(headline):].lstrip(" |\u2014\u2013-:.")
        # Only drop the repeated headline when real body copy follows it.
        if len(remainder) >= 30:
            text = _DATELINE_RE.sub("", remainder, count=1)

    return clean_text(text, SUMMARY_CHARS)


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------
def is_routine_federal_register(title):
    """True for high-volume administrative notices with no policy substance."""
    low = (title or "").lower()
    return any(pattern in low for pattern in ROUTINE_FR_TITLE_PATTERNS)


def is_guidance(title, summary=""):
    """Detect supervisory-guidance language without over-classifying.

    A headline that calls itself guidance is reliable; body text is not (FDIC
    board-meeting descriptions embed agenda links whose labels mention rules
    and guidance). So the standalone word is checked in the headline, and the
    phrase list is checked against a short, cleaned lead-in only.
    """
    title_low = clean_text(title).lower()
    if _GUIDANCE_WORD_RE.search(title_low):
        return True
    if any(phrase in title_low for phrase in GUIDANCE_PHRASES):
        return True
    lead = clean_text(summary, 200).lower()
    return any(phrase in lead for phrase in GUIDANCE_PHRASES)


def classify_status(source, doc_type, title, summary=""):
    """Map a source record to one of DOCUMENT_STATUSES.

    Federal Register supplies an explicit document type. RSS press releases
    remain news even when announcing rules. Guidance is an inferred reading
    classification; the original Press release type is preserved separately.
    """
    if source == "Federal Register":
        status = FR_TYPE_STATUS.get((doc_type or "").strip(), "Notice")
        return status, (doc_type or "").strip()
    if source == "NIST":
        return "Standards Draft", "Draft publication"

    # A press release discussing a rule is still a press release.
    if is_guidance(title):
        return "Supervisory Guidance", "Press release"
    return "General News", "Press release"

def classify_category(source, status, title, summary=""):
    """Sort an article into one of CATEGORIES.

    Precedence is documented deliberately: for regulator documents the nature
    of the document wins (a cyber *rule* is a Regulation), then guidance, then
    subject matter. NIST drafts are standards, so they always live in the
    cybersecurity/privacy buckets.
    """
    text = ("%s %s" % (title or "", summary or "")).lower()

    if source == "NIST":
        if any(term in text for term in PRIVACY_TERMS):
            return "Privacy & Data Protection"
        return "Cybersecurity"

    if status in ("Proposed Rule", "Final Rule"):
        return "Regulations"
    if status == "Supervisory Guidance":
        return "Supervisory Guidance"
    if any(term in text for term in CYBER_TERMS):
        return "Cybersecurity"
    if any(term in text for term in PRIVACY_TERMS):
        return "Privacy & Data Protection"
    return "Banking & Finance"


# --------------------------------------------------------------------------
# Editorial ranking
# --------------------------------------------------------------------------
# Pulse's lead story is not simply the newest item. Every article gets one
# deterministic score from four documented signals, so a routine award notice
# published today cannot outrank a substantive rule published last week:
#
#   document significance (what kind of document it is)      0-34 points
#   subject relevance     (how close it sits to policy work)  0-22 points
#   source weight         (rulemaking feed vs press feed)     0-12 points
#   relative recency      (against the newest item in the feed) 0-24 points
#
# Recency is relative to the feed's own newest date, not to the server clock, so
# the ranking stays deterministic in tests and honest when an agency is quiet.
STATUS_WEIGHT = {
    "Final Rule": 34,
    "Proposed Rule": 30,
    "Supervisory Guidance": 28,
    "Standards Draft": 26,
    "Notice": 12,
    "General News": 8,
}

CATEGORY_WEIGHT = {
    "Regulations": 22,
    "Supervisory Guidance": 20,
    "Cybersecurity": 16,
    "Privacy & Data Protection": 15,
    "Banking & Finance": 12,
}

SOURCE_WEIGHT = {
    "Federal Register": 12,
    "NIST": 10,
    "Federal Reserve": 9,
    "FDIC": 8,
}

RECENCY_POINTS = 24.0
RECENCY_HORIZON_DAYS = 45


def relevance_score(article, newest=""):
    """Return the documented 0-100 editorial rank for one article."""
    status = STATUS_WEIGHT.get(article.get("status"), 0)
    category = CATEGORY_WEIGHT.get(article.get("category"), 0)
    source = SOURCE_WEIGHT.get(article.get("source"), 6)

    recency = 0.0
    published = article.get("published") or ""
    if newest and published:
        try:
            age = (datetime.strptime(newest, "%Y-%m-%d")
                   - datetime.strptime(published, "%Y-%m-%d")).days
            recency = RECENCY_POINTS * max(0.0, 1.0 - (max(age, 0) / RECENCY_HORIZON_DAYS))
        except ValueError:
            recency = 0.0

    return round(min(100.0, status + category + source + recency), 1)


def score_articles(articles):
    """Copy the feed with a ``score`` field; the cache itself is left untouched."""
    dates = [a.get("published") for a in articles if a.get("published")]
    newest = max(dates) if dates else ""
    return [dict(a, score=relevance_score(a, newest)) for a in articles]


def rank_articles(articles):
    """Order by editorial score, then date, then title (fully deterministic)."""
    return sorted(
        articles,
        key=lambda a: (a.get("score", 0), a.get("published", ""), a.get("title", "")),
        reverse=True,
    )


# "On the Radar" is a reading prompt for policy owners, not a legal conclusion.
# Each label describes the kind of document, never an obligation.
RADAR_LABELS = {
    "Final Rule": "Worth Monitoring",
    "Proposed Rule": "Potential Policy Review",
    "Supervisory Guidance": "Regulatory Awareness",
    "Standards Draft": "Standards Development",
}

# Notes are assembled only from fields the source supplied, and each one is
# hedged: the document itself carries the operative dates and scope.
RADAR_NOTES = {
    "Final Rule": "{agency} published a final rule. Effective dates and scope are stated in the rule itself.",
    "Proposed Rule": "{agency} published a proposed rule. It is a proposal, not an obligation; the notice carries the comment process.",
    "Supervisory Guidance": "{agency} shared an update referring to guidance. Review the original publication for its status and scope.",
    "Standards Draft": "{agency} opened a draft standard for comment. It is not final guidance.",
}


def _short_agency(article):
    """Use the lead agency only; FR sometimes lists four co-issuers."""
    agency = (article.get("agency") or article.get("source") or "").strip()
    return agency.split(",")[0].strip() or "The issuing agency"


def build_radar(articles, limit=4):
    """Curate up to one item per substantive document type, best ranked first."""
    picks = []
    seen = set()
    for article in rank_articles(articles):
        status = article.get("status")
        if status not in RADAR_LABELS or status in seen:
            continue
        seen.add(status)
        picks.append({
            "id": article.get("id", ""),
            "label": RADAR_LABELS[status],
            "note": RADAR_NOTES[status].format(agency=_short_agency(article)),
        })
        if len(picks) >= limit:
            break
    return picks


# --------------------------------------------------------------------------
# Article construction
# --------------------------------------------------------------------------
def make_article(source, title, url, date, summary="",
                 category="Banking & Finance", status="General News",
                 identifier="", agency="", doc_type="", classified_by="inferred"):
    """Validate and normalize one record; return None when it is unusable."""
    title = _TITLE_PREFIX_RE.sub("", clean_text(title))
    title = clean_text(title, TITLE_CHARS)
    url = safe_url(url)
    if len(title) < 4 or not url:
        return None

    meta = SOURCES.get(source, {})
    agency = clean_text(agency, 120) or meta.get("agency", source)
    published = parse_date(date)

    if category not in CATEGORIES:
        category = "Banking & Finance"
    if status not in DOCUMENT_STATUSES:
        status = "General News"

    # A stable, DOM-safe id: the source slug plus the source's own identifier.
    ident = re.sub(r"[^A-Za-z0-9._-]+", "-", str(identifier or "")).strip("-")
    article_id = "%s-%s" % (meta.get("slug", "pulse"), ident) if ident else url

    return {
        "id": article_id[:200],
        "title": title,
        "url": url,
        "published": published,
        "summary": summarize(summary, title),
        "source": source,
        "agency": agency,
        "category": category,
        "status": status,
        "doc_type": clean_text(doc_type, 40),
        # "source" means the feed supplied the document type; "inferred" means
        # Pulse derived it from a headline. The UI shows the difference.
        "classified_by": classified_by if classified_by in ("source", "inferred") else "inferred",
    }


def _xml_text(item, *tags):
    """Read the first present child text, including Atom/DC namespaces."""
    for tag in tags:
        for path in (
            tag,
            "{http://www.w3.org/2005/Atom}" + tag,
            "{http://purl.org/dc/elements/1.1/}" + tag,
        ):
            node = item.find(path)
            if node is not None and (node.text or "").strip():
                return node.text.strip()
    return ""


def _xml_link(item):
    """Return the item link from RSS text or an Atom href attribute."""
    text = _xml_text(item, "link")
    if text:
        return text

    for link in item.findall("{http://www.w3.org/2005/Atom}link"):
        rel = (link.get("rel") or "alternate").lower()
        href = (link.get("href") or "").strip()
        if href and rel in ("alternate", ""):
            return href
    return ""


# --------------------------------------------------------------------------
# Per-source normalization
# --------------------------------------------------------------------------
def normalize(source, payload):
    """Convert one source payload into a list of validated articles."""
    articles = []

    if source == "Federal Register":
        results = payload.get("results") if isinstance(payload, dict) else None
        for item in results or []:
            # One malformed record must not discard the rest of the source.
            try:
                if not isinstance(item, dict):
                    continue
                title = item.get("title") or ""
                if is_routine_federal_register(title):
                    continue

                status, doc_type = classify_status(
                    source,
                    item.get("type"),
                    title,
                    item.get("abstract") or "",
                )
                article = make_article(
                    source=source,
                    title=title,
                    url=item.get("html_url"),
                    date=item.get("publication_date"),
                    summary=item.get("abstract") or "",
                    category=classify_category(
                        source, status, title, item.get("abstract") or ""
                    ),
                    status=status,
                    identifier=item.get("document_number") or "",
                    agency=", ".join(
                        str(a.get("name"))
                        for a in item.get("agencies") or []
                        if isinstance(a, dict) and a.get("name")
                    ),
                    doc_type=doc_type,
                    # The Federal Register states the document type itself.
                    classified_by="source",
                )
                if article:
                    articles.append(article)
            except Exception:
                continue

    elif source == "NIST":
        entries = payload.get("entries") if isinstance(payload, dict) else None
        for item in entries or []:
            try:
                if not isinstance(item, dict):
                    continue
                title = item.get("title") or ""
                summary = item.get("summary") or ""
                status, doc_type = classify_status(source, "", title, summary)
                article = make_article(
                    source=source,
                    title=title,
                    url=item.get("link"),
                    date=item.get("published") or item.get("updated"),
                    summary=summary,
                    category=classify_category(source, status, title, summary),
                    status=status,
                    identifier=item.get("id") or "",
                    doc_type=doc_type,
                    # The NIST feed itself is "drafts open for comment".
                    classified_by="source",
                )
                if article:
                    articles.append(article)
            except Exception:
                continue

    else:
        # RSS 2.0 <item> or Atom <entry>.
        try:
            items = payload.findall(".//item")
            if not items:
                items = payload.findall(".//{http://www.w3.org/2005/Atom}entry")
        except AttributeError:
            return articles

        for item in items:
            try:
                title = _xml_text(item, "title")
                summary = (
                    _xml_text(item, "description")
                    or _xml_text(item, "summary")
                    or _xml_text(
                        item, "{http://purl.org/rss/1.0/modules/content/}encoded"
                    )
                )
                status, doc_type = classify_status(source, "", title, summary)
                article = make_article(
                    source=source,
                    title=title,
                    url=_xml_link(item),
                    date=(
                        _xml_text(item, "pubDate")
                        or _xml_text(item, "published")
                        or _xml_text(item, "updated")
                        or _xml_text(item, "date")
                    ),
                    summary=summary,
                    category=classify_category(source, status, title, summary),
                    status=status,
                    identifier=_xml_text(item, "guid"),
                    doc_type=doc_type,
                )
                if article:
                    articles.append(article)
            except Exception:
                continue

    return articles


# --------------------------------------------------------------------------
# Cache and combined feed
# --------------------------------------------------------------------------
def _describe_error(exc):
    """Translate an exception into a short, user-safe reason."""
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "Timed out"
    if isinstance(exc, urllib.error.HTTPError):
        return "HTTP %s" % exc.code
    if isinstance(exc, urllib.error.URLError):
        reason = str(getattr(exc, "reason", "") or "")
        return "Connection failed" + (": %s" % reason[:60] if reason else "")
    if isinstance(exc, (ET.ParseError, json.JSONDecodeError, UnicodeDecodeError)):
        return "Unreadable feed"
    if isinstance(exc, ValueError):
        return str(exc)[:80] or "Invalid response"
    return type(exc).__name__


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _load_source(name, now):
    """Return a fresh cached entry, or fetch one source and cache the result.

    A failed refresh keeps the last good articles but reports the source as
    unavailable (``ok: false``, ``stale: true``) so the UI can say so honestly.
    """
    with _cache_lock:
        cached = _cache.get(name)

    if cached and (now - cached["fetched_at"]) < CACHE_SECONDS:
        return cached

    try:
        articles = normalize(name, fetch_source(name))
        entry = {
            "articles": articles,
            "fetched_at": now,
            "fetched_iso": _utc_now_iso(),
            "status": {"ok": True, "count": len(articles), "error": None},
        }
    except Exception as exc:
        # Deliberately broad: any single-source failure degrades to a status.
        previous = cached["articles"] if cached else []
        entry = {
            "articles": previous,
            "fetched_at": now,
            "fetched_iso": cached["fetched_iso"] if cached else "",
            "status": {
                "ok": False,
                "count": len(previous),
                "error": _describe_error(exc),
                "stale": bool(previous),
            },
        }

    with _cache_lock:
        _cache[name] = entry
    return entry


def get_feed(limit=DEFAULT_LIMIT):
    """Return the combined, de-duplicated, newest-first Pulse feed."""
    now = time.monotonic()
    combined = []
    source_status = {}
    newest_fetch = ""

    # Each source is independent: a failure adds a status entry, not an error.
    for name in SOURCES:
        entry = _load_source(name, now)
        combined.extend(entry["articles"])
        source_status[name] = dict(entry["status"])
        if entry["status"]["ok"]:
            newest_fetch = max(newest_fetch, entry["fetched_iso"])

    # De-duplicate by canonical URL, then by identical headline on the same day
    # within one source (feeds occasionally repeat a bulletin).
    seen_urls = set()
    seen_titles = set()
    unique = []
    for article in combined:
        title_key = (article["source"], article["title"].lower(), article["published"])
        if article["url"] in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(article["url"])
        seen_titles.add(title_key)
        unique.append(article)

    # Newest first; undated articles sort last rather than pretending to be new.
    unique.sort(key=lambda a: (a["published"], a["title"]), reverse=True)

    # Editorial rank is computed over the full de-duplicated feed so a limit
    # truncation cannot change what counts as the most significant story.
    scored = score_articles(unique)

    try:
        limit = max(1, min(int(limit), MAX_ARTICLES))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT

    return {
        "articles": scored[:limit],
        "total_normalized": len(unique),
        "sources": source_status,
        "generated_at": newest_fetch or _utc_now_iso(),
        "checked_at": _utc_now_iso(),
        "categories": list(CATEGORIES),
        "statuses": list(DOCUMENT_STATUSES),
        # Curated reading prompts; each entry references an article by id.
        "radar": build_radar(scored[:limit]),
    }
