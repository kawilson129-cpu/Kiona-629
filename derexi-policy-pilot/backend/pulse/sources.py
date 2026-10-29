
# backend/pulse/sources.py
import json
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = {
    "Federal Register": (
        "https://www.federalregister.gov/api/v1/documents.json"
        "?per_page=50&conditions[term]=banking"
    ),
    "FDIC": (
        "https://public.govdelivery.com/topics/"
        "USFDIC_26/feed.rss"
    ),
    "NIST": (
        "https://csrc.nist.gov/CSRC/media/feeds/pubs/"
        "drafts-open-for-comment.json"
    ),
    "Federal Reserve": (
        "https://www.federalreserve.gov/feeds/"
        "press_bcreg.xml"
    ),
}


def fetch_source(name):
    """Download and parse one government feed."""
    if name not in SOURCES:
        raise ValueError("Unknown source")

    request = urllib.request.Request(
        SOURCES[name],
        headers={
            "User-Agent": "DeRexi-Pulse-Development/0.1",
            "Accept": "application/json, application/rss+xml, "
                      "application/xml, text/xml",
        },
    )

    with urllib.request.urlopen(
        request, timeout=12
    ) as response:
        raw = response.read(2_000_001)

    if len(raw) > 2_000_000:
        raise ValueError("Source response too large")

    if name in ("Federal Register", "NIST"):
        return json.loads(raw.decode("utf-8-sig"))

    # RSS and Atom are XML formats.
    return ET.fromstring(raw)
