"""Pulse: feed registry and downloader.

Each government source is described once here (endpoint, wire format, issuing
agency). ``service.py`` owns normalization and classification, so this module
stays responsible for exactly two things: knowing where the data lives, and
fetching it safely.

No API keys, accounts, or paid services are involved: three sources are public
RSS/XML feeds and two are public JSON endpoints.
"""

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .integrity import open_source

# Hard limits so a slow or hostile endpoint cannot stall or exhaust the app.
TIMEOUT_SECONDS = 12
MAX_RESPONSE_BYTES = 2_000_000

# Identify the client honestly; some government hosts throttle blank agents.
USER_AGENT = "DeRexi-Pulse/1.0 (internal policy research; Aurum Capital Bank)"

# Federal Register: query the banking/fintech regulators directly instead of
# full-text searching for "banking", which returns unrelated agencies whose
# documents merely mention the word. This is a relevance decision, not a filter
# on the returned data.
FEDERAL_REGISTER_AGENCIES = (
    "federal-reserve-system",
    "federal-deposit-insurance-corporation",
    "comptroller-of-the-currency",
    "consumer-financial-protection-bureau",
    "national-credit-union-administration",
    "financial-crimes-enforcement-network",
    "federal-financial-institutions-examination-council",
)

_FR_QUERY = [
    ("per_page", "100"),   # fetch a generous page, then curate in service.py
    ("order", "newest"),   # relevance without recency buries this week's rules
    ("format", "json"),
] + [
    ("conditions[agencies][]", slug) for slug in FEDERAL_REGISTER_AGENCIES
]

FEDERAL_REGISTER_URL = (
    "https://www.federalregister.gov/api/v1/documents.json?"
    + urllib.parse.urlencode(_FR_QUERY)
)

# Registry order is the order shown in the UI's feed-status strip.
SOURCES = {
    "Federal Register": {
        "slug": "federal-register",
        "url": FEDERAL_REGISTER_URL,
        "format": "json",
        "agency": "Federal Register",
        "homepage": "https://www.federalregister.gov/",
    },
    "FDIC": {
        "slug": "fdic",
        # Official GovDelivery RSS feed used by fdic.gov for press releases.
        "url": "https://public.govdelivery.com/topics/USFDIC_26/feed.rss",
        "format": "rss",
        "agency": "Federal Deposit Insurance Corporation",
        "homepage": "https://www.fdic.gov/news/press-releases/",
    },
    "NIST": {
        "slug": "nist",
        "url": (
            "https://csrc.nist.gov/CSRC/media/feeds/pubs/"
            "drafts-open-for-comment.json"
        ),
        "format": "json",
        "agency": "National Institute of Standards and Technology",
        "homepage": "https://csrc.nist.gov/publications/drafts",
    },
    "Federal Reserve": {
        "slug": "federal-reserve",
        "url": "https://www.federalreserve.gov/feeds/press_bcreg.xml",
        "format": "rss",
        "agency": "Federal Reserve Board",
        "homepage": "https://www.federalreserve.gov/newsevents/pressreleases.htm",
    },
}


def fetch_source(name):
    """Download one source and return JSON data or an XML root element.

    Raises on any transport, size, or parse problem; ``service.py`` catches it
    per source so one dead feed never takes down the combined Pulse feed.
    """
    meta = SOURCES.get(name)
    if meta is None:
        raise ValueError("Unknown Pulse source: %s" % name)

    request = urllib.request.Request(
        meta["url"],
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, application/rss+xml, "
                      "application/atom+xml, application/xml, text/xml",
            # Ask for an uncompressed body: urllib does not decode gzip for us.
            "Accept-Encoding": "identity",
        },
    )

    with open_source(name, request, timeout=TIMEOUT_SECONDS) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise ValueError("Unexpected HTTP status %s" % status)

        # Read one byte past the cap so an oversized body is detectable.
        raw = response.read(MAX_RESPONSE_BYTES + 1)

    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Source response exceeded %d bytes" % MAX_RESPONSE_BYTES)

    # Strip a UTF-8 BOM; several government feeds emit one before the XML/JSON.
    raw = raw.lstrip(b"\xef\xbb\xbf")

    if meta["format"] == "json":
        return json.loads(raw.decode("utf-8"))

    # ElementTree does not resolve external entities, and the body size is
    # already capped, so parsing these official HTTPS feeds is contained.
    return ET.fromstring(raw)
