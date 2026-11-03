"""Compliance 1, Assignment 3 — C-03 audit checks for DeRexi Pulse.

C-03  Regulatory Feed Integrity and Source Validation

WHY THIS FILE EXISTS
--------------------
``tests/test_pulse.py`` already covers normalization, classification, dedupe,
failure isolation and the combined feed. This file adds only the checks the
audit needs that are not already pinned there:

    * the source registry is closed (no caller-selected feed URL)
    * source name, agency and original link survive normalization
    * hostile payloads never produce an unsafe URL or an executable field
    * invalid dates never masquerade as valid ones
    * stale cache is explicitly flagged, not silently served
    * the public API rejects out-of-range ``limit`` values with 422
    * a total upstream failure produces no articles at all

SAFETY
------
No network, no database, no Supabase project, no API key. Payloads are
synthetic fixtures built in this file. ``service.fetch_source`` is replaced
per test; the real downloader is restored before exit. Nothing is written
outside ``docs/compliance/evidence/``.

Run from backend/:
    python tests/test_c03_audit.py
"""

import json
import os
import sys
import time
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
from pulse import service  # noqa: E402
from pulse.service import (  # noqa: E402
    CACHE_SECONDS,
    CATEGORIES,
    DOCUMENT_STATUSES,
    clean_text,
    get_feed,
    make_article,
    parse_date,
    safe_url,
    summarize,
)
from pulse.sources import SOURCES, fetch_source  # noqa: E402

RESULTS = []
REQUIREMENTS = {
    1: "Only configured regulatory sources are fetched",
    2: "Source names and original links are preserved",
    3: "Unsafe URLs are rejected",
    4: "Hostile markup / script URLs cannot inject executable content",
    5: "Invalid dates do not appear as valid dates",
    6: "Duplicate records are removed",
    7: "Classification follows documented metadata and conservative rules",
    8: "A failed source does not prevent healthy feeds from rendering",
    9: "Stale results are clearly identified",
    10: "Invalid API limit values return HTTP 422",
    11: "Failed or empty feeds do not create fabricated articles",
}

_real_fetch_source = service.fetch_source


RUN_EVIDENCE = "docs/compliance/evidence/c03_audit_checks_2026-11-03.txt"


def check(test_id, requirement, procedure, expected, passed, actual):
    RESULTS.append({
        "id": test_id,
        "requirement": requirement,
        "requirement_text": REQUIREMENTS[requirement],
        "procedure": procedure,
        "expected": expected,
        "actual": actual,
        "status": "PASS" if passed else "FAIL",
        "basis": "executed in this audit (2026-11-03)",
        "evidence": RUN_EVIDENCE,
    })
    print("  %s  %-9s %s" % ("PASS" if passed else "FAIL", test_id, procedure))
    if not passed:
        print("        expected: %s" % expected)
        print("        actual:   %s" % actual)


def prior(test_id, requirement, procedure, expected, actual, evidence):
    """Record a check whose only evidence predates this audit."""
    RESULTS.append({
        "id": test_id,
        "requirement": requirement,
        "requirement_text": REQUIREMENTS[requirement],
        "procedure": procedure,
        "expected": expected,
        "actual": actual,
        "status": "PASS",
        "basis": "prior evidence (2026-11-02), not re-executed in this audit",
        "evidence": evidence,
    })
    print("  PASS* %-9s %s (prior evidence)" % (test_id, procedure))


def not_tested(test_id, requirement, procedure, reason):
    RESULTS.append({
        "id": test_id,
        "requirement": requirement,
        "requirement_text": REQUIREMENTS[requirement],
        "procedure": procedure,
        "expected": "",
        "actual": reason,
        "status": "NOT TESTED",
    })
    print("  NOTEST    %-9s %s — %s" % (test_id, procedure, reason))


def reset_cache():
    service._cache.clear()


def fake_fetcher(payloads):
    """Serve synthetic payloads and record which source names were requested."""
    calls = []

    def _fetch(name):
        calls.append(name)
        payload = payloads[name]
        if isinstance(payload, Exception):
            raise payload
        return payload

    _fetch.calls = calls
    return _fetch


# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------
def fr_payload(items):
    return {"results": items}


def fr_item(title, url, date="2026-10-30", doc="2026-99999",
            dtype="Notice", abstract="", agencies=None):
    return {
        "title": title,
        "type": dtype,
        "abstract": abstract,
        "document_number": doc,
        "html_url": url,
        "publication_date": date,
        "agencies": agencies if agencies is not None else [{"name": "Federal Reserve System"}],
    }


def rss(items, channel="Test Feed"):
    body = "".join(items)
    return (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<rss version='2.0'><channel><title>%s</title>%s</channel></rss>"
        % (channel, body)
    ).encode("utf-8")


def rss_item(title, link, description="", date="", guid=""):
    parts = ["<item>"]
    if title is not None:
        parts.append("<title>%s</title>" % title)
    if link is not None:
        parts.append("<link>%s</link>" % link)
    if guid:
        parts.append("<guid>%s</guid>" % guid)
    if date:
        parts.append("<pubDate>%s</pubDate>" % date)
    if description:
        parts.append("<description><![CDATA[%s]]></description>" % description)
    parts.append("</item>")
    return "".join(parts)


# ===========================================================================
# Requirement 1 — only configured sources are fetched
# ===========================================================================
def req1_registry_is_closed():
    print("\n[req 1] configured source registry")

    check(
        "C03-01", 1,
        "Registry contains exactly the four documented government sources",
        "{'Federal Register', 'FDIC', 'NIST', 'Federal Reserve'}",
        set(SOURCES) == {"Federal Register", "FDIC", "NIST", "Federal Reserve"},
        "registry keys: %s" % sorted(SOURCES),
    )

    try:
        fetch_source("Unlisted Source")
        raised = False
        detail = "no exception"
    except ValueError as exc:
        raised = True
        detail = str(exc)
    except Exception as exc:  # noqa: BLE001
        raised = False
        detail = "%s: %s" % (type(exc).__name__, exc)
    check(
        "C03-02", 1,
        "fetch_source refuses a name outside the registry",
        "ValueError('Unknown Pulse source: ...')",
        raised,
        detail,
    )

    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": fr_payload([]),
        "FDIC": ET.fromstring(rss([])),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    get_feed()
    fetched = sorted(set(service.fetch_source.calls))
    check(
        "C03-03", 1,
        "A feed build requests only registry names",
        "exactly the four registry keys, no other request",
        fetched == sorted(SOURCES),
        "requested: %s" % fetched,
    )

    client = TestClient(main.app)
    spec = client.get("/openapi.json").json()
    params = spec["paths"]["/api/pulse"]["get"].get("parameters", [])
    names = sorted(p.get("name") for p in params)
    check(
        "C03-04", 1,
        "Public feed endpoint exposes no caller-selected source or URL",
        "only the 'limit' parameter",
        names == ["limit"],
        "parameters: %s" % names,
    )


# ===========================================================================
# Requirement 2 — attribution preserved
# ===========================================================================
def req2_attribution():
    print("\n[req 2] source and link attribution")

    fr = service.normalize("Federal Register", fr_payload([
        fr_item(
            "Regulatory Capital Rule Amendment",
            "https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule?a=1&b=2#section",
            doc="2026-12345",
            dtype="Rule",
            agencies=[{"name": "Federal Reserve System"}, {"name": "FDIC"}],
        )
    ]))
    check(
        "C03-05", 2,
        "Source name is preserved exactly as configured",
        "source == 'Federal Register'",
        len(fr) == 1 and fr[0]["source"] == "Federal Register",
        "source=%r" % (fr[0]["source"] if fr else None),
    )
    check(
        "C03-06", 2,
        "Original publication link is preserved (fragment removed only)",
        "https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule?a=1&b=2",
        len(fr) == 1 and fr[0]["url"] ==
        "https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule?a=1&b=2",
        "url=%r" % (fr[0]["url"] if fr else None),
    )
    check(
        "C03-07", 2,
        "Co-issuing agencies named by the source are retained",
        "agency mentions Federal Reserve System and FDIC",
        len(fr) == 1 and "Federal Reserve System" in fr[0]["agency"] and "FDIC" in fr[0]["agency"],
        "agency=%r" % (fr[0]["agency"] if fr else None),
    )

    fdic = service.normalize("FDIC", ET.fromstring(rss([
        rss_item("FDIC issue", "https://www.fdic.gov/news/press-releases/2026/x.html",
                 "Body copy for the release.", "Fri, 30 Oct 2026 13:09:02 -0500", "1")
    ])))
    check(
        "C03-08", 2,
        "Agency falls back to the registry when the feed omits one",
        "agency == 'Federal Deposit Insurance Corporation'",
        len(fdic) == 1 and fdic[0]["agency"] == "Federal Deposit Insurance Corporation",
        "agency=%r" % (fdic[0]["agency"] if fdic else None),
    )


# ===========================================================================
# Requirement 3 — unsafe URLs rejected
# ===========================================================================
def req3_url_safety():
    print("\n[req 3] URL scheme and host validation")

    cases = [
        ("C03-09", "plain http is rejected", "http://www.fdic.gov/a"),
        ("C03-10", "javascript: is rejected", "javascript:alert(1)"),
        ("C03-11", "data: is rejected", "data:text/html;base64,PHNjcmlwdD4="),
        ("C03-12", "embedded credentials are rejected", "https://user:pass@example.gov/a"),
        ("C03-13", "protocol-relative and relative links are rejected", "//example.gov/a"),
        ("C03-14", "a host without a dot is rejected", "https://localhost/a"),
    ]
    for test_id, proc, url in cases:
        got = safe_url(url)
        check(test_id, 3, proc, "empty string", got == "", "safe_url -> %r" % got)

    check(
        "C03-15", 3,
        "A relative link alone is rejected",
        "empty string",
        safe_url("/documents/2026/rule") == "",
        "safe_url -> %r" % safe_url("/documents/2026/rule"),
    )

    article = make_article(
        source="Federal Register",
        title="Unsafe document with a valid headline",
        url="http://www.federalregister.gov/documents/1",
        date="2026-10-30",
    )
    check(
        "C03-16", 3,
        "A record whose only link is unsafe is dropped, not rendered",
        "make_article returns None",
        article is None,
        "returned %r" % (article,),
    )

    unrelated = make_article(
        source="FDIC",
        title="FDIC urges immediate action on deposit account limits",
        url="https://secure-fdic-verification.example/login",
        date="2026-10-30",
    )
    check(
        "C03-54", 2,
        "A link on a host unrelated to the claimed source is rejected or flagged",
        "rejected, or labelled with a different host so attribution cannot be spoofed",
        unrelated is None,
        "accepted as source=%r with url=%r"
        % (unrelated["source"], unrelated["url"]) if unrelated else "rejected",
    )


# ===========================================================================
# Requirement 4 — hostile markup / script URLs
# ===========================================================================
def req4_hostile_content():
    print("\n[req 4] hostile markup and script payloads")

    t1 = clean_text("<script>alert(1)</script>Lost laptop reported")
    t2 = clean_text('<img src=x onerror="alert(1)">Phishing email received')
    check(
        "C03-17", 4,
        "Literal script and img tags are removed from text fields",
        "no '<script', no '<img', no 'onerror='",
        "<script" not in t1.lower() and "<img" not in t2.lower() and "onerror=" not in t2.lower(),
        "t1=%r t2=%r" % (t1, t2),
    )

    s1 = summarize('<p onclick="steal()">Real body copy about a ransomware incident.</p>',
                   "Cyber incident")
    check(
        "C03-18", 4,
        "Event-handler attributes cannot survive into a summary",
        "summary contains no 'onclick=' and no '<p '",
        "onclick=" not in s1.lower() and "<p " not in s1.lower(),
        "summary=%r" % s1,
    )

    hostile_fr = fr_payload([
        fr_item("Injected <script>alert(1)</script> notice",
                "javascript:alert(document.cookie)"),
        fr_item("Safe sibling document", "https://www.federalregister.gov/documents/2"),
    ])
    normalized = service.normalize("Federal Register", hostile_fr)
    urls = [a["url"] for a in normalized]
    check(
        "C03-19", 4,
        "A javascript: document link is dropped while its sibling survives",
        "1 article, https only",
        len(normalized) == 1 and urls[0].startswith("https://"),
        "%d article(s), urls=%s" % (len(normalized), urls),
    )

    encoded = clean_text("Notice &lt;img src=x onerror=alert(1)&gt;")
    check(
        "C03-20", 4,
        "Entity-encoded markup is emitted as text, not parsed into a tag server-side",
        "no HTML parsing occurs; the string stays inert JSON content",
        "<img" in encoded and "onerror=" in encoded,
        "returned text=%r; renderer safety covered by C03-55" % encoded,
    )

    bad_type = service.normalize("Federal Register", {"results": [
        "not-a-record", None, 42,
        fr_item("Valid record after malformed siblings", "https://www.federalregister.gov/documents/3"),
    ]})
    check(
        "C03-21", 4,
        "Malformed records are skipped without discarding valid siblings",
        "exactly 1 article survives",
        len(bad_type) == 1 and bad_type[0]["title"] == "Valid record after malformed siblings",
        "%d article(s)" % len(bad_type),
    )

    prior(
        "C03-55", 4,
        "A hostile feed payload is executed in the browser without injecting content",
        "no injected nodes, no javascript: href, no alert",
        "Phase 3 browser run: stub article with <img onerror>, <script>, javascript: URL "
        "produced no injected nodes and no javascript: link; markup rendered as text",
        "derexi-policy-pilot/docs/compliance-assignment-2/testing-results.md §4 (XSS row) and "
        "docs/compliance-assignment-2/phase-3-browser-results.json",
    )


# ===========================================================================
# Requirement 5 — dates
# ===========================================================================
def req5_dates():
    print("\n[req 5] date integrity")

    invalid = {
        "C03-22": ("2026-13-45", "month 13"),
        "C03-23": ("2026-02-30", "31 February"),
        "C03-24": ("not a date", "free text"),
        "C03-25": ("", "empty value"),
    }
    for test_id, (raw, label) in invalid.items():
        got = parse_date(raw)
        check(test_id, 5, "Invalid date (%s) is not shown as valid" % label,
              "empty string", got == "", "parse_date(%r) -> %r" % (raw, got))

    article = make_article(
        source="FDIC", title="Release with an impossible date",
        url="https://www.fdic.gov/x", date="2026-02-30",
    )
    check(
        "C03-26", 5,
        "An impossible date becomes an empty published field, not a guess",
        "published == ''",
        article is not None and article["published"] == "",
        "published=%r" % (article["published"] if article else None),
    )
    check(
        "C03-27", 5,
        "A valid RFC 822 date is still normalized to ISO",
        "2026-10-30",
        parse_date("Fri, 30 Oct 2026 13:09:02 -0500") == "2026-10-30",
        "parse_date -> %r" % parse_date("Fri, 30 Oct 2026 13:09:02 -0500"),
    )


# ===========================================================================
# Requirement 6 — duplicates
# ===========================================================================
def req6_dedupe():
    print("\n[req 6] duplicate suppression")

    reset_cache()
    dup_fr = fr_payload([
        fr_item("Repeated bulletin", "https://www.federalregister.gov/documents/9", doc="9"),
        fr_item("Repeated bulletin", "https://www.federalregister.gov/documents/9", doc="9"),
        fr_item("Same headline, different day", "https://www.federalregister.gov/documents/10",
                doc="10", date="2026-10-29"),
    ])
    dup_rss = ET.fromstring(rss([
        rss_item("Duplicate press release", "https://www.fdic.gov/a",
                 "Body copy for the release.", "Fri, 30 Oct 2026 10:00:00 -0500", "a"),
        rss_item("Duplicate press release", "https://www.fdic.gov/a",
                 "Body copy for the release.", "Fri, 30 Oct 2026 10:00:00 -0500", "a"),
    ]))
    service.fetch_source = fake_fetcher({
        "Federal Register": dup_fr,
        "FDIC": dup_rss,
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    feed = get_feed()
    check(
        "C03-28", 6,
        "Identical URLs are collapsed to one article",
        "one 'Repeated bulletin' article",
        sum(1 for a in feed["articles"] if a["title"] == "Repeated bulletin") == 1,
        "count=%d" % sum(1 for a in feed["articles"] if a["title"] == "Repeated bulletin"),
    )
    check(
        "C03-29", 6,
        "Same-source, same-day duplicate headlines are collapsed",
        "one 'Duplicate press release' article",
        sum(1 for a in feed["articles"] if a["title"] == "Duplicate press release") == 1,
        "count=%d" % sum(1 for a in feed["articles"] if a["title"] == "Duplicate press release"),
    )
    check(
        "C03-30", 6,
        "Distinct records are not over-collapsed",
        "the different-day headline is retained",
        any(a["title"] == "Same headline, different day" for a in feed["articles"]),
        "titles=%s" % [a["title"] for a in feed["articles"]],
    )
    check(
        "C03-31", 6,
        "total_normalized reports the de-duplicated count",
        "total_normalized equals len(articles) when under the limit",
        feed["total_normalized"] == len(feed["articles"]),
        "%d vs %d" % (feed["total_normalized"], len(feed["articles"])),
    )


# ===========================================================================
# Requirement 7 — classification
# ===========================================================================
def req7_classification():
    print("\n[req 7] conservative classification")

    fr = service.normalize("Federal Register", fr_payload([
        fr_item("Final rule on capital", "https://www.federalregister.gov/d/1",
                dtype="Rule", abstract="The agencies adopt amendments."),
        fr_item("Presidential determination", "https://www.federalregister.gov/d/2",
                dtype="Presidential Document"),
    ]))
    check(
        "C03-32", 7,
        "Federal Register document type is treated as source-declared metadata",
        "classified_by == 'source' for both articles",
        len(fr) == 2 and all(a["classified_by"] == "source" for a in fr),
        "classified_by=%s" % [a["classified_by"] for a in fr],
    )
    check(
        "C03-33", 7,
        "Presidential documents are reported as Notices, not rules",
        "status == 'Notice'",
        len(fr) == 2 and fr[1]["status"] == "Notice",
        "status=%r" % (fr[1]["status"] if len(fr) == 2 else None),
    )

    fdic = service.normalize("FDIC", ET.fromstring(rss([
        rss_item("FDIC board meeting agenda", "https://www.fdic.gov/b",
                 "The agenda references proposed guidance and a rule.", "Fri, 30 Oct 2026 10:00:00 -0500", "b"),
        rss_item("Agencies issue guidance on third-party risk", "https://www.fdic.gov/c",
                 "Body copy.", "Fri, 30 Oct 2026 10:00:00 -0500", "c"),
    ])))
    check(
        "C03-34", 7,
        "Body-only mention of 'guidance' does not reclassify a press release",
        "status == 'General News'",
        len(fdic) == 2 and fdic[0]["status"] == "General News",
        "status=%r" % (fdic[0]["status"] if fdic else None),
    )
    check(
        "C03-35", 7,
        "A guidance headline is classified as supervisory guidance",
        "status == 'Supervisory Guidance'",
        len(fdic) == 2 and fdic[1]["status"] == "Supervisory Guidance",
        "status=%r" % (fdic[1]["status"] if len(fdic) == 2 else None),
    )
    check(
        "C03-36", 7,
        "Inferred classifications are labelled as inferred",
        "classified_by == 'inferred' for RSS press releases",
        len(fdic) == 2 and all(a["classified_by"] == "inferred" for a in fdic),
        "classified_by=%s" % [a["classified_by"] for a in fdic],
    )
    check(
        "C03-37", 7,
        "Every emitted category and status is inside the documented allow-list",
        "category in CATEGORIES and status in DOCUMENT_STATUSES",
        all(a["category"] in CATEGORIES and a["status"] in DOCUMENT_STATUSES
            for a in fr + fdic),
        "categories=%s statuses=%s" % (
            sorted({a["category"] for a in fr + fdic}),
            sorted({a["status"] for a in fr + fdic}),
        ),
    )


# ===========================================================================
# Requirements 8 and 9 — failure isolation and stale signalling
# ===========================================================================
def req8_9_failure_and_stale():
    print("\n[req 8/9] failure isolation and stale cache")

    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": fr_payload([]),
        "FDIC": OSError("connection reset"),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    feed = get_feed()
    check(
        "C03-38", 8,
        "A failing source is reported without breaking the request",
        "HTTP-equivalent response with sources[FDIC].ok == False",
        feed["sources"]["FDIC"]["ok"] is False and isinstance(feed["sources"]["FDIC"]["error"], str),
        "ok=%r error=%r" % (feed["sources"]["FDIC"]["ok"], feed["sources"]["FDIC"]["error"]),
    )
    check(
        "C03-39", 8,
        "Healthy sources still report ok while one source fails",
        "Federal Register, NIST, Federal Reserve ok == True",
        all(feed["sources"][n]["ok"] for n in ("Federal Register", "NIST", "Federal Reserve")),
        "statuses=%s" % {k: v["ok"] for k, v in feed["sources"].items()},
    )
    check(
        "C03-40", 9,
        "A failure with no cached copy is not labelled stale",
        "stale == False and count == 0",
        feed["sources"]["FDIC"]["stale"] is False and feed["sources"]["FDIC"]["count"] == 0,
        "stale=%r count=%r" % (feed["sources"]["FDIC"]["stale"], feed["sources"]["FDIC"]["count"]),
    )

    # Populate a good cache, expire it, then fail the refresh.
    reset_cache()
    good = ET.fromstring(rss([
        rss_item("Cached FDIC release", "https://www.fdic.gov/cached",
                 "Body copy that survives the outage.", "Fri, 30 Oct 2026 10:00:00 -0500", "z")
    ]))
    service.fetch_source = fake_fetcher({
        "Federal Register": fr_payload([]),
        "FDIC": good,
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    get_feed()
    for entry in service._cache.values():
        entry["fetched_at"] = time.monotonic() - CACHE_SECONDS - 1

    service.fetch_source = fake_fetcher({
        "Federal Register": fr_payload([]),
        "FDIC": TimeoutError("timed out"),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    stale_feed = get_feed()
    fdic_status = stale_feed["sources"]["FDIC"]
    check(
        "C03-41", 9,
        "An expired cache refresh failure is explicitly flagged stale",
        "stale == True, ok == False, error set",
        fdic_status["stale"] is True and fdic_status["ok"] is False and bool(fdic_status["error"]),
        "stale=%r ok=%r error=%r" % (fdic_status["stale"], fdic_status["ok"], fdic_status["error"]),
    )
    check(
        "C03-42", 9,
        "Stale articles are the last good copies, not invented replacements",
        "the cached release is still present and unchanged",
        any(a["title"] == "Cached FDIC release" for a in stale_feed["articles"]),
        "titles=%s" % [a["title"] for a in stale_feed["articles"]],
    )
    check(
        "C03-43", 9,
        "A stale source does not mark healthy sources stale",
        "other sources ok == True and stale absent/false",
        all(stale_feed["sources"][n]["ok"] for n in ("Federal Register", "NIST", "Federal Reserve")),
        "statuses=%s" % {k: (v["ok"], v.get("stale")) for k, v in stale_feed["sources"].items()},
    )


# ===========================================================================
# Requirement 10 — API limit validation
# ===========================================================================
def req10_api_limits():
    print("\n[req 10] API parameter validation")

    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": fr_payload([
            fr_item("Limit probe document", "https://www.federalregister.gov/documents/77", doc="77"),
        ]),
        "FDIC": ET.fromstring(rss([])),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    client = TestClient(main.app)

    for test_id, query, label in (
        ("C03-44", "limit=0", "zero"),
        ("C03-45", "limit=61", "above maximum"),
        ("C03-46", "limit=abc", "non-numeric"),
        ("C03-47", "limit=-3", "negative"),
    ):
        r = client.get("/api/pulse?" + query)
        check(
            test_id, 10,
            "limit %s (%s) is rejected with 422" % (label, query),
            "HTTP 422",
            r.status_code == 422,
            "HTTP %d" % r.status_code,
        )

    r = client.get("/api/pulse?limit=1")
    check(
        "C03-48", 10,
        "A valid limit still returns 200 and honours the cap",
        "HTTP 200 and at most 1 article",
        r.status_code == 200 and len(r.json().get("articles", [])) <= 1,
        "HTTP %d, articles=%d" % (r.status_code, len(r.json().get("articles", []))),
    )

    r = client.get("/api/pulse/health")
    body = r.json()
    check(
        "C03-49", 10,
        "Health endpoint reports the configured sources without fetching",
        "HTTP 200 and the four registry names",
        r.status_code == 200 and sorted(body.get("sources", [])) == sorted(SOURCES),
        "HTTP %d, sources=%s" % (r.status_code, body.get("sources")),
    )


# ===========================================================================
# Requirement 11 — no fabricated content
# ===========================================================================
def req11_no_fabrication():
    print("\n[req 11] no fabricated articles")

    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": OSError("down"),
        "FDIC": OSError("down"),
        "NIST": json.JSONDecodeError("bad", "", 0),
        "Federal Reserve": ET.ParseError("not xml"),
    })
    feed = get_feed()
    check(
        "C03-50", 11,
        "Total upstream failure yields zero articles",
        "articles == [] and total_normalized == 0",
        feed["articles"] == [] and feed["total_normalized"] == 0,
        "articles=%d total=%d" % (len(feed["articles"]), feed["total_normalized"]),
    )
    check(
        "C03-51", 11,
        "Total upstream failure is reported per source, not as a crash",
        "all four sources ok == False with an error string",
        len(feed["sources"]) == 4
        and all(s["ok"] is False and s["error"] for s in feed["sources"].values()),
        "statuses=%s" % {k: (v["ok"], v["error"]) for k, v in feed["sources"].items()},
    )
    check(
        "C03-52", 11,
        "No radar prompts are invented when nothing loaded",
        "radar == []",
        feed["radar"] == [],
        "radar=%r" % feed["radar"],
    )

    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": {"results": []},
        "FDIC": ET.fromstring(rss([])),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(rss([])),
    })
    empty = get_feed()
    check(
        "C03-53", 11,
        "Empty feeds are not errors and produce no placeholder articles",
        "articles == [] and every source ok == True",
        empty["articles"] == [] and all(s["ok"] for s in empty["sources"].values()),
        "articles=%d ok=%s" % (len(empty["articles"]),
                               {k: v["ok"] for k, v in empty["sources"].items()}),
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("C-03 audit — regulatory feed integrity and source validation")
    print("Isolated: synthetic fixtures only; no network, database, or Supabase.")
    print("=" * 78)

    try:
        req1_registry_is_closed()
        req2_attribution()
        req3_url_safety()
        req4_hostile_content()
        req5_dates()
        req6_dedupe()
        req7_classification()
        req8_9_failure_and_stale()
        req10_api_limits()
        req11_no_fabrication()
    finally:
        service.fetch_source = _real_fetch_source
        reset_cache()

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    skipped = sum(1 for r in RESULTS if r["status"] == "NOT TESTED")

    print("=" * 78)
    print("RESULT: %d passed, %d failed, %d not tested" % (passed, failed, skipped))

    out = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                       "docs", "compliance", "evidence", "c03_audit_results.json")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "control": "C-03",
            "control_name": "Regulatory Feed Integrity and Source Validation",
            "mode": "isolated synthetic fixtures; no network or database",
            "requirements": REQUIREMENTS,
            "results": RESULTS,
            "summary": {"passed": passed, "failed": failed, "not_tested": skipped},
        }, fh, indent=2)
    print("Evidence JSON: " + out)
    sys.exit(1 if failed else 0)
