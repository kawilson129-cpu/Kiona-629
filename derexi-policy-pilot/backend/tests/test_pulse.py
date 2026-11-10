"""Pulse — isolated tests for the regulatory-intelligence module.

Offline by default: every source payload is synthetic, so no network, database,
Supabase project, or API key is touched. Pass ``--live`` to additionally hit the
four real government endpoints and validate the combined feed.

Run from backend/:
    python tests/test_pulse.py
    python tests/test_pulse.py --live
"""

import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pulse import service
from pulse.service import (
    CACHE_SECONDS,
    DOCUMENT_STATUSES,
    RADAR_LABELS,
    build_radar,
    classify_category,
    classify_status,
    clean_text,
    get_feed,
    make_article,
    normalize,
    parse_date,
    rank_articles,
    relevance_score,
    safe_url,
    score_articles,
    summarize,
)

PASSED = []
FAILED = []


def check(label, condition, detail=""):
    """Record one assertion so the run ends with a readable tally."""
    if condition:
        PASSED.append(label)
        print("  PASS  %s" % label)
    else:
        FAILED.append(label)
        print("  FAIL  %s %s" % (label, detail))


def reset_cache():
    service._cache.clear()


# ---------------------------------------------------------------------------
# Synthetic payloads
# ---------------------------------------------------------------------------
FR_PAYLOAD = {
    "results": [
        {
            "title": "Regulatory Capital Rule: Category I and II Banking Organizations",
            "type": "Proposed Rule",
            "abstract": "The agencies propose amendments to the capital rule.",
            "document_number": "2026-12345",
            "html_url": "https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule",
            "publication_date": "2026-10-30",
            "agencies": [{"name": "Federal Reserve System"}],
        },
        {
            "title": "Proposed Third-Party Risk Management Guidance",
            "type": "Notice",
            "abstract": "The agencies request comment on proposed guidance.",
            "document_number": "2026-22222",
            "html_url": "https://www.federalregister.gov/documents/2026/09/15/2026-22222/guidance",
            "publication_date": "2026-09-15",
            "agencies": [{"name": "Federal Deposit Insurance Corporation"}],
        },
        {
            # Routine paperwork notice: must be curated out of the editorial feed.
            "title": "Agency Information Collection Activities: Comment Request",
            "type": "Notice",
            "abstract": "Paperwork reduction act notice.",
            "document_number": "2026-33333",
            "html_url": "https://www.federalregister.gov/documents/2026/10/30/2026-33333/icr",
            "publication_date": "2026-10-30",
            "agencies": [{"name": "Federal Reserve System"}],
        },
        {
            # Unsafe link: must be rejected rather than passed to the UI.
            "title": "Unsafe document",
            "type": "Notice",
            "abstract": "",
            "document_number": "2026-44444",
            "html_url": "http://example.com/insecure",
            "publication_date": "2026-10-29",
            "agencies": [],
        },
    ]
}

NIST_PAYLOAD = {
    "entries": [
        {
            "id": "https://csrc.nist.gov/pubs/sp/800/100/r1/ipd",
            "title": "SP 800-100 Rev. 1, Information Security Handbook",
            "summary": "Draft guidance on information security programs.",
            "published": "2026-10-21T00:00:00",
            "updated": "2026-10-21T00:00:00",
            "link": "https://csrc.nist.gov/pubs/sp/800/100/r1/ipd",
        }
    ]
}

FDIC_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>FDIC</title>
<item>
  <pubDate>Fri, 30 Oct 2026 13:09:02 -0500</pubDate>
  <title>Press Release: FDIC Board of Directors Approve New Action</title>
  <guid>70314918</guid>
  <link>https://content.govdelivery.com/accounts/USFDIC/bulletins/430eba6</link>
  <description><![CDATA[PRESS RELEASE | OCTOBER 30, 2026 FDIC Board of Directors Approve New Action
    <p>WASHINGTON &mdash; By notational vote, the Board approved the following matter.
    The agenda references a proposed rule and guidance in linked materials.</p>]]></description>
</item>
<item>
  <pubDate>Thu, 11 Sep 2026 10:00:00 -0500</pubDate>
  <title>Agencies Seek Comment on Proposed Third-Party Risk Management Guidance</title>
  <guid>71000001</guid>
  <link>https://content.govdelivery.com/accounts/USFDIC/bulletins/abc123</link>
  <description><![CDATA[<p>Agencies Seek Comment on Proposed Third-Party Risk Management Guidance and Issue Statement
    on Community Bank Engagement with Core Service Providers.</p>]]></description>
</item>
</channel></rss>"""

FED_RSS = b"""<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0"><channel><title>FRB</title>
<item>
  <title>Federal Reserve Board announces final rule that establishes data standards</title>
  <link>https://www.federalreserve.gov/newsevents/pressreleases/bcreg20260611a.htm</link>
  <guid>https://www.federalreserve.gov/newsevents/pressreleases/bcreg20260611a.htm</guid>
  <description>Federal Reserve Board announces final rule that establishes data standards</description>
  <pubDate>Thu, 11 Jun 2026 16:00:00 GMT</pubDate>
</item>
</channel></rss>"""

EMPTY_RSS = b'<?xml version="1.0"?><rss version="2.0"><channel><title>Empty</title></channel></rss>'


def fake_fetcher(payloads):
    """Return a fetch_source replacement that serves the given payloads."""
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
# Unit tests
# ---------------------------------------------------------------------------
def test_date_parsing():
    print("\n[dates] RSS and ISO date parsing")
    cases = [
        ("Fri, 30 Oct 2026 13:09:02 -0500", "2026-10-30"),
        ("Fri, 2 Oct 2026 20:00:00 GMT", "2026-10-02"),
        ("2026-10-30", "2026-10-30"),
        ("2026-10-21T00:00:00", "2026-10-21"),
        ("2026-10-21T00:00:00Z", "2026-10-21"),
        ("Wed, 05 Aug 2026 11:00:00 -0400", "2026-08-05"),
        ("October 30, 2026", "2026-10-30"),
        ("", ""),
        (None, ""),
        ("not a date", ""),
        ("2026-13-45", ""),
    ]
    for raw, expected in cases:
        got = parse_date(raw)
        check("parse_date(%r) -> %r" % (raw, expected), got == expected, "got %r" % got)


def test_text_helpers():
    print("\n[text] markup stripping, URLs, summaries")
    check(
        "clean_text strips tags and entities",
        clean_text("<p>Hello &amp; <b>welcome</b></p>") == "Hello & welcome",
    )
    check(
        "clean_text leaves escaped angle brackets as text",
        clean_text("&lt;script&gt;alert(1)&lt;/script&gt;") == "<script>alert(1)</script>",
    )
    check("safe_url keeps https", safe_url("https://www.fdic.gov/a?b=1#frag")
          == "https://www.fdic.gov/a?b=1")
    check("safe_url rejects http", safe_url("http://www.fdic.gov/a") == "")
    check("safe_url rejects javascript:", safe_url("javascript:alert(1)") == "")
    check("safe_url rejects credentials", safe_url("https://user:pass@example.com/x") == "")
    check("safe_url rejects relative", safe_url("/documents/1") == "")

    check(
        "summarize strips feed kicker",
        summarize("PRESS RELEASE: The FDIC today published a list of enforcement actions.",
                  "FDIC Publishes Enforcement Orders")
        .startswith("The FDIC today"),
    )
    check(
        "summarize drops a duplicated headline",
        summarize(
            "FDIC Publishes Enforcement Orders for September 2026 WASHINGTON \u2014 "
            "The FDIC today published a list of orders.",
            "FDIC Publishes Enforcement Orders for September 2026",
        ).startswith("The FDIC today"),
    )
    check(
        "summarize returns '' when description is only a truncated headline",
        summarize(
            "Federal Reserve Board announces it will extend, until November 4, the comment",
            "Federal Reserve Board announces it will extend, until November 4, the comment period on its proposal",
        ) == "",
    )
    check("summarize handles None", summarize(None, "Title") == "")


def test_classification():
    print("\n[classification] document status and category")
    status, _ = classify_status("Federal Register", "Rule", "A final rule")
    check("FR Rule -> Final Rule", status == "Final Rule", status)
    status, _ = classify_status("Federal Register", "Proposed Rule", "A proposal")
    check("FR Proposed Rule -> Proposed Rule", status == "Proposed Rule", status)
    status, _ = classify_status("Federal Register", "Notice", "Agency update")
    check("FR Notice -> Notice", status == "Notice", status)
    status, _ = classify_status("Federal Register", "Presidential Document", "Determination")
    check("FR Presidential Document -> Notice", status == "Notice", status)
    status, _ = classify_status(
        "Federal Register", "Notice", "Proposed Third-Party Risk Management Guidance"
    )
    check("FR guidance notice preserves source Notice type",
          status == "Notice", status)
    status, _ = classify_status("NIST", "", "SP 800-53 draft")
    check("NIST -> Standards Draft", status == "Standards Draft", status)

    # Regressions: body HTML must not promote a press release to a rule/guidance.
    status, _ = classify_status(
        "FDIC",
        "",
        "FDIC Board of Directors Approve New Action",
        "By notational vote the Board approved the matter. Linked materials reference a "
        "proposed rule and guidance on community bank engagement.",
    )
    check("FDIC board notice with rule words in body -> General News",
          status == "General News", status)
    status, _ = classify_status(
        "FDIC", "", "FDIC Launches New Office of Supervisory Appeals",
        "The FDIC announced a new panel of independent officials to hear appeals.",
    )
    check("FDIC supervisory-appeals release -> General News",
          status == "General News", status)
    status, _ = classify_status(
        "FDIC", "", "Agencies Seek Comment on Proposed Third-Party Risk Management Guidance",
        "Agencies seek comment on the proposed guidance.",
    )
    check("FDIC guidance headline -> Supervisory Guidance",
          status == "Supervisory Guidance", status)
    status, _ = classify_status("Federal Reserve", "", "Board announces final rule on data standards")
    check("Fed final-rule press release stays news", status == "General News", status)

    check("All statuses are from the allowed set",
          all(s in DOCUMENT_STATUSES for s in ("Proposed Rule", "Final Rule", "Notice",
                                               "Supervisory Guidance", "Standards Draft",
                                               "General News")))

    cat = classify_category("Federal Register", "Final Rule", "Cybersecurity rule", "")
    check("A cyber rule still files under Regulations", cat == "Regulations", cat)
    cat = classify_category("NIST", "Standards Draft", "SP 800-53 security controls", "")
    check("NIST draft -> Cybersecurity", cat == "Cybersecurity", cat)
    cat = classify_category("Federal Register", "Notice", "Privacy Act of 1974; System of Records", "")
    check("Privacy notice -> Privacy & Data Protection",
          cat == "Privacy & Data Protection", cat)
    cat = classify_category("FDIC", "General News", "FDIC announces senior leadership appointments", "")
    check("Unrelated press release -> Banking & Finance", cat == "Banking & Finance", cat)
    cat = classify_category("FDIC", "Supervisory Guidance", "Third-party risk guidance", "")
    check("Guidance -> Supervisory Guidance", cat == "Supervisory Guidance", cat)


def test_normalize():
    print("\n[normalize] per-source shaping")
    reset_cache()
    fr = normalize("Federal Register", FR_PAYLOAD)
    check("FR keeps substantive documents only", len(fr) == 2, "got %d" % len(fr))
    check("FR drops routine paperwork notices",
          all("Information Collection" not in a["title"] for a in fr))
    check("FR drops unsafe http links", all(a["url"].startswith("https://") for a in fr))
    check("FR carries the issuing agency",
          fr[0]["agency"] == "Federal Reserve System", fr[0]["agency"])
    check("FR publishes ISO dates", fr[0]["published"] == "2026-10-30", fr[0]["published"])
    check("FR keeps the document number id", fr[0]["id"] == "federal-register-2026-12345",
          fr[0]["id"])

    nist = normalize("NIST", NIST_PAYLOAD)
    check("NIST draft normalized", len(nist) == 1)
    check("NIST uses Standards Draft", nist[0]["status"] == "Standards Draft")
    check("NIST files under Cybersecurity", nist[0]["category"] == "Cybersecurity")
    check("NIST date normalized", nist[0]["published"] == "2026-10-21", nist[0]["published"])

    fdic = normalize("FDIC", ET.fromstring(FDIC_RSS))
    check("FDIC RSS items parsed", len(fdic) == 2, "got %d" % len(fdic))
    check("FDIC title prefix removed",
          fdic[0]["title"] == "FDIC Board of Directors Approve New Action", fdic[0]["title"])
    check("FDIC RSS date parsed correctly", fdic[0]["published"] == "2026-10-30",
          fdic[0]["published"])
    check("FDIC body markup removed from summary",
          "<" not in fdic[0]["summary"] and "&mdash;" not in fdic[0]["summary"])
    check("FDIC duplicate headline not repeated in summary",
          not fdic[0]["summary"].startswith("FDIC Board of Directors Approve New Action"),
          fdic[0]["summary"][:60])
    check("FDIC board notice is General News", fdic[0]["status"] == "General News",
          fdic[0]["status"])
    check("FDIC guidance headline is Supervisory Guidance",
          fdic[1]["status"] == "Supervisory Guidance", fdic[1]["status"])

    fed = normalize("Federal Reserve", ET.fromstring(FED_RSS))
    check("Fed RSS parsed", len(fed) == 1)
    check("Fed headline-only description becomes empty summary", fed[0]["summary"] == "",
          fed[0]["summary"])
    check("Fed press release remains news", fed[0]["status"] == "General News", fed[0]["status"])
    check("Fed date normalized", fed[0]["published"] == "2026-06-11", fed[0]["published"])

    check(
        "article shape contains no unexpected fields",
        set(make_article("FDIC", "Title", "https://www.fdic.gov/x", "2026-01-01").keys())
        == {"id", "title", "url", "published", "summary", "source", "agency",
            "category", "status", "doc_type", "classified_by"},
    )
    check(
        "RSS classification is marked inferred",
        make_article("FDIC", "Board approves action", "https://www.fdic.gov/x",
                     "2026-01-01")["classified_by"] == "inferred",
    )
    check(
        "Federal Register classification is marked source-supplied",
        fr[0]["classified_by"] == "source",
        fr[0]["classified_by"],
    )
    check(
        "NIST classification is marked source-supplied",
        nist[0]["classified_by"] == "source",
        nist[0]["classified_by"],
    )


def test_combined_feed():
    print("\n[feed] de-duplication, ordering, failure isolation, cache")
    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": FR_PAYLOAD,
        "FDIC": ET.fromstring(FDIC_RSS),
        "NIST": NIST_PAYLOAD,
        "Federal Reserve": ET.fromstring(FED_RSS),
    })

    feed = get_feed()
    dates = [a["published"] for a in feed["articles"]]
    check("combined feed returns articles", len(feed["articles"]) == 6,
          "got %d" % len(feed["articles"]))
    check("combined feed is newest first", dates == sorted(dates, reverse=True), dates)
    check("all four sources reported",
          set(feed["sources"]) == {"Federal Register", "FDIC", "NIST", "Federal Reserve"})
    check("all sources ok", all(s["ok"] for s in feed["sources"].values()))
    check("no duplicate URLs",
          len({a["url"] for a in feed["articles"]}) == len(feed["articles"]))
    check("generated_at is ISO UTC", feed["generated_at"].endswith("Z"),
          feed["generated_at"])
    check("limit clamps to available articles", len(get_feed(limit=2)["articles"]) == 2)
    check("every article carries an editorial score",
          all(isinstance(a.get("score"), float) for a in feed["articles"]))
    check("radar is returned with the feed", isinstance(feed.get("radar"), list))
    check("radar is drawn from the returned articles",
          all(any(a["id"] == entry["id"] for a in feed["articles"])
              for entry in feed["radar"]),
          str(feed.get("radar")))

    small = get_feed(limit=1)
    check("limited feed radar references only returned articles",
          all(entry["id"] in {a["id"] for a in small["articles"]} for entry in small["radar"]))

    # Cache: a second call inside the window must not re-download.
    calls_before = len(service.fetch_source.calls)
    get_feed()
    check("second call served from cache",
          len(service.fetch_source.calls) == calls_before,
          "calls %d -> %d" % (calls_before, len(service.fetch_source.calls)))
    check("cache window is 30 minutes", CACHE_SECONDS == 1800)

    # One source failing must not blank the feed.
    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": FR_PAYLOAD,
        "FDIC": OSError("connection reset"),
        "NIST": NIST_PAYLOAD,
        "Federal Reserve": ET.fromstring(FED_RSS),
    })
    feed = get_feed()
    check("feed survives one failing source", len(feed["articles"]) == 4,
          "got %d" % len(feed["articles"]))
    check("failed source flagged", feed["sources"]["FDIC"]["ok"] is False)
    check("failed source explains itself",
          isinstance(feed["sources"]["FDIC"]["error"], str)
          and feed["sources"]["FDIC"]["error"] != "")
    check("healthy sources still ok",
          feed["sources"]["NIST"]["ok"] and feed["sources"]["Federal Register"]["ok"])

    # Empty results are not an error and produce no invented content.
    reset_cache()
    service.fetch_source = fake_fetcher({
        "Federal Register": {"results": []},
        "FDIC": ET.fromstring(EMPTY_RSS),
        "NIST": {"entries": []},
        "Federal Reserve": ET.fromstring(EMPTY_RSS),
    })
    feed = get_feed()
    check("empty sources yield an empty feed", feed["articles"] == [])
    check("empty sources are not errors",
          all(s["ok"] for s in feed["sources"].values()))
    check("empty feed still reports structure",
          "generated_at" in feed and "categories" in feed)

    reset_cache()
    service.fetch_source = _real_fetch_source


# ---------------------------------------------------------------------------
# Phase 3: editorial ranking and On the Radar
# ---------------------------------------------------------------------------
def _article(title, status, category, source, published,
             agency="Federal Reserve System"):
    """Minimal article fixture for ranking tests (no network, no DB)."""
    return {
        "id": source.lower().replace(" ", "-") + "-" + str(abs(hash(title)) % 100000),
        "title": title,
        "url": "https://example.gov/" + str(abs(hash(title)) % 100000),
        "published": published,
        "summary": "",
        "source": source,
        "agency": agency,
        "category": category,
        "status": status,
        "doc_type": "Press release",
        "classified_by": "inferred",
    }


def test_ranking():
    print("\n[ranking] editorial score and lead selection")

    notice = _article("Routine recognition notice", "General News",
                      "Banking & Finance", "FDIC", "2026-10-30")
    rule = _article("Regulatory capital rule", "Final Rule",
                    "Regulations", "Federal Register", "2026-10-10")
    scored = score_articles([notice, rule])
    check("substantive rule outranks a newer general-news item",
          rank_articles(scored)[0]["title"] == "Regulatory capital rule",
          str([(a["title"], a["score"]) for a in scored]))
    check("every score is a bounded number",
          all(isinstance(a["score"], float) and 0 <= a["score"] <= 100 for a in scored),
          str([a["score"] for a in scored]))
    check("scoring does not mutate the cached articles",
          "score" not in notice and "score" not in rule)

    older = _article("Same type, older", "Final Rule", "Regulations",
                     "Federal Register", "2026-06-01")
    newer = _article("Same type, newer", "Final Rule", "Regulations",
                     "Federal Register", "2026-10-01")
    ranked = rank_articles(score_articles([older, newer]))
    check("among comparable documents the newer one leads",
          ranked[0]["title"] == "Same type, newer",
          str([(a["title"], a["score"]) for a in ranked]))
    check("recency stops helping past the 45-day horizon",
          relevance_score(older, "2026-10-01") < relevance_score(newer, "2026-10-01"),
          "%s vs %s" % (relevance_score(older, "2026-10-01"),
                        relevance_score(newer, "2026-10-01")))

    undated = _article("Undated rule", "Final Rule", "Regulations",
                       "Federal Register", "")
    check("an undated article receives no recency points",
          relevance_score(undated, "2026-10-01")
          == relevance_score(undated, ""),
          str(relevance_score(undated, "2026-10-01")))

    tied = score_articles([rule, dict(rule)])
    check("ranking is deterministic on identical items",
          [a["id"] for a in rank_articles(tied)]
          == [a["id"] for a in rank_articles(list(reversed(tied)))])


def test_radar():
    print("\n[radar] curated reading prompts")

    articles = score_articles([
        _article("Final rule A", "Final Rule", "Regulations", "Federal Register",
                 "2026-10-20", "Federal Reserve System"),
        _article("Final rule B (older)", "Final Rule", "Regulations",
                 "Federal Register", "2026-08-01", "Federal Reserve System"),
        _article("Proposed rule", "Proposed Rule", "Regulations",
                 "Federal Register", "2026-10-19", "Federal Deposit Insurance Corporation"),
        _article("Supervisory guidance", "Supervisory Guidance",
                 "Supervisory Guidance", "FDIC", "2026-10-18",
                 "Federal Deposit Insurance Corporation"),
        _article("Draft standard", "Standards Draft", "Cybersecurity", "NIST",
                 "2026-10-17", "National Institute of Standards and Technology"),
        _article("Award notice", "Notice", "Banking & Finance", "FDIC", "2026-10-30"),
        _article("Leadership news", "General News", "Banking & Finance", "FDIC",
                 "2026-10-30"),
    ])
    radar = build_radar(articles)
    ids = {a["id"] for a in articles}

    check("radar has at most one entry per document type", len(radar) == 4,
          str(len(radar)))
    check("radar excludes notices and general news",
          all(entry["label"] in RADAR_LABELS.values() for entry in radar))
    check("radar references articles that exist",
          all(entry["id"] in ids for entry in radar))
    expected_final = _article("Final rule A", "Final Rule", "Regulations",
                              "Federal Register", "2026-10-20")["id"]
    finals = [entry for entry in radar if entry["label"] == "Worth Monitoring"]
    check("radar keeps the best-ranked rule of a type",
          len(finals) == 1 and finals[0]["id"] == expected_final,
          str(finals))
    check("radar labels are the documented nonbinding prompts",
          {entry["label"] for entry in radar}
          == {"Worth Monitoring", "Potential Policy Review",
              "Regulatory Awareness", "Standards Development"})
    check("radar notes avoid legal conclusions",
          all("must" not in entry["note"].lower().split()
              and "requires" not in entry["note"].lower()
              and "is required" not in entry["note"].lower()
              for entry in radar),
          str([e["note"] for e in radar]))
    check("radar notes name an issuer", all(entry["note"][:1].isupper() for entry in radar))


# ---------------------------------------------------------------------------
# Optional live check
# ---------------------------------------------------------------------------
_real_fetch_source = service.fetch_source


def test_live():
    print("\n[live] real government endpoints (network)")
    reset_cache()
    feed = get_feed(limit=60)
    check("live feed returned articles", len(feed["articles"]) > 0,
          "got %d" % len(feed["articles"]))

    for name, status in feed["sources"].items():
        check("source reachable: %s" % name, status["ok"], status.get("error") or "")
        print("        %-18s count=%d ok=%s" % (name, status["count"], status["ok"]))

    articles = feed["articles"]
    check("live dates are ISO or empty",
          all(a["published"] == "" or len(a["published"]) == 10 for a in articles))
    check("live URLs are https",
          all(a["url"].startswith("https://") for a in articles))
    check("live titles are plain text",
          all("<" not in a["title"] for a in articles))
    check("live summaries are plain text",
          all("<" not in a["summary"] for a in articles))
    check("live every article has a known category",
          all(a["category"] in service.CATEGORIES for a in articles))
    check("live every article has a known status",
          all(a["status"] in DOCUMENT_STATUSES for a in articles))
    check("live feed is newest first",
          [a["published"] for a in articles] == sorted(
              [a["published"] for a in articles], reverse=True))

    print("\n        category counts: %s" % {
        c: sum(1 for a in articles if a["category"] == c) for c in service.CATEGORIES
    })
    print("        status counts: %s" % {
        s: sum(1 for a in articles if a["status"] == s) for s in DOCUMENT_STATUSES
    })


if __name__ == "__main__":
    print("Pulse test suite")
    print("=" * 70)
    test_date_parsing()
    test_text_helpers()
    test_classification()
    test_normalize()
    test_combined_feed()
    test_ranking()
    test_radar()
    if "--live" in sys.argv:
        test_live()

    print("\n" + "=" * 70)
    print("RESULT: %d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        for name in FAILED:
            print("  failed: %s" % name)
        sys.exit(1)
