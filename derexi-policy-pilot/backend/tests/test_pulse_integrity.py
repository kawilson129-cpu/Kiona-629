"""New offline C-03 regressions; original 55-check assessment is unavailable."""
import io
import os
import sys
import unittest
import urllib.request
from urllib.error import HTTPError
from unittest.mock import Mock, patch
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pulse.integrity import approved_url, article_destination, open_source, SourceRedirectHandler
from pulse import service, sources


VALID = {
    "Federal Register": "https://www.federalregister.gov/documents/2026/11/03/example",
    "FDIC": "https://www.fdic.gov/news/financial-institution-letters/example",
    "Federal Reserve": "https://www.federalreserve.gov/newsevents/pressreleases/example.htm",
    "NIST": "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final",
}
FDIC_BULLETIN = "https://content.govdelivery.com/accounts/USFDIC/bulletins/3abcd12"


class HostTests(unittest.TestCase):
    def test_configured_sources_are_approved(self):
        for name, url in sources.SOURCES.items():
            self.assertTrue(approved_url(name, url["url"]), name)

    def test_legitimate_publication_hosts_and_fdic_account(self):
        for source, url in VALID.items():
            self.assertTrue(approved_url(source, url))
        self.assertTrue(approved_url("FDIC", FDIC_BULLETIN))
        self.assertTrue(approved_url("NIST", "https://nvlpubs.nist.gov/nistpubs/example.pdf"))

    def test_wrong_source_attribution(self):
        for source in VALID:
            for other, url in VALID.items():
                if source != other:
                    self.assertFalse(approved_url(source, url))

    def test_misleading_domains_credentials_ports_protocols_and_controls(self):
        for url in ("http://www.fdic.gov/a", "https://www.fdic.gov.evil.invalid/a",
                    "https://evilfdic.gov/a", "https://evil.invalid/www.fdic.gov",
                    "https://www.fdic.gov@evil.invalid/a", "https://evil@www.fdic.gov/a",
                    "https://www.fdic.gov:444/a", "https://www.fdic.gov\\@evil.invalid/a",
                    "https://www.fdic.gov\n/a", "https://www.fdic.gov /a",
                    "https://www.fdic.gov%2eevil.invalid/a", "//www.fdic.gov/a",
                    "file:///etc/passwd", "https://127.0.0.1/a", "https://[::1]/a",
                    "https://www.fdіc.gov/a", "https://www.fdic.gov:/a" + "x" * 4096):
            with self.subTest(url=url):
                self.assertFalse(approved_url("FDIC", url))

    def test_other_govdelivery_tenants_and_path_traversal_denied(self):
        for url in (FDIC_BULLETIN.replace("USFDIC", "OTHER"),
                    FDIC_BULLETIN + "/../../OTHER/", FDIC_BULLETIN + "%2f..%2fOTHER",
                    "https://content.govdelivery.com/accounts/USFDICevil/bulletins/123",
                    "https://public.govdelivery.com/topics/OTHER/feed.rss"):
            self.assertFalse(approved_url("FDIC", url))

    def test_unknown_source_fails_closed(self):
        self.assertFalse(approved_url("Unknown", VALID["FDIC"]))

    def test_invalid_url_types(self):
        for value in (None, 1, [], "", "https://[malformed"):
            self.assertFalse(approved_url("FDIC", value))


class RedirectTests(unittest.TestCase):
    def test_publishers_without_head_use_same_validated_get_without_body_read(self):
        for code in (405, 501):
            response = Mock()
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            response.geturl.return_value = VALID["FDIC"]
            error = HTTPError(VALID["FDIC"], code, "HEAD not supported", {}, io.BytesIO())
            with patch("pulse.integrity.open_source", side_effect=[error, response]) as open_:
                self.assertEqual(article_destination("FDIC", VALID["FDIC"]), VALID["FDIC"])
                self.assertEqual(open_.call_args_list[0].args[1].get_method(), "HEAD")
                self.assertEqual(open_.call_args_list[1].args[1].get_method(), "GET")
                response.read.assert_not_called()

    def test_policy_denials_are_not_retried(self):
        error = HTTPError(VALID["FDIC"], 403, "Forbidden", {}, io.BytesIO())
        with patch("pulse.integrity.open_source", side_effect=error) as open_:
            with self.assertRaises(HTTPError):
                article_destination("FDIC", VALID["FDIC"])
            open_.assert_called_once()

    def test_each_redirect_status_checks_destination_before_contact(self):
        handler = SourceRedirectHandler("FDIC")
        request = urllib.request.Request(VALID["FDIC"], method="HEAD")
        for code in (301, 302, 303, 307, 308):
            with self.assertRaises(ValueError):
                handler.redirect_request(request, None, code, "", {}, "https://evil.invalid/a")
            redirected = handler.redirect_request(request, None, code, "", {}, FDIC_BULLETIN)
            self.assertEqual(redirected.full_url, FDIC_BULLETIN)
            self.assertEqual(redirected.get_method(), "HEAD")

    def test_initial_unapproved_url_never_opens(self):
        with patch("urllib.request.build_opener") as build:
            with self.assertRaises(ValueError):
                open_source("FDIC", urllib.request.Request("https://evil.invalid/a"))
            build.assert_not_called()

    def test_final_destination_revalidated_and_closed(self):
        response = Mock()
        response.geturl.return_value = "https://evil.invalid/a"
        opener = Mock()
        opener.open.return_value = response
        with patch("urllib.request.build_opener", return_value=opener):
            with self.assertRaises(ValueError):
                open_source("FDIC", urllib.request.Request(VALID["FDIC"]))
        response.close.assert_called_once()

    def test_article_returns_actual_verified_destination(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.geturl.return_value = FDIC_BULLETIN
        with patch("pulse.integrity.open_source", return_value=response) as open_:
            self.assertEqual(article_destination("FDIC", VALID["FDIC"]), FDIC_BULLETIN)
        self.assertEqual(open_.call_args.args[1].get_method(), "HEAD")


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.previous = service._cache
        service._cache = {}

    def tearDown(self):
        service._cache = self.previous

    def test_make_article_keeps_editorial_fields(self):
        article = service.make_article("FDIC", "<b>New guidance</b>", FDIC_BULLETIN,
                                       "2026-11-03", "<p>Summary</p>")
        self.assertEqual(article["title"], "New guidance")
        self.assertEqual(article["source"], "FDIC")
        self.assertEqual(article["category"], "Banking & Finance")
        self.assertEqual(article["status"], "General News")

    def test_article_rejects_empty_titles_and_unapproved_links(self):
        self.assertIsNone(service.make_article("FDIC", "<p> </p>", VALID["FDIC"], ""))
        self.assertIsNone(service.make_article("FDIC", "Title", "https://evil.invalid/a", ""))

    def test_all_source_normalizers_preserve_classification(self):
        fr = service.normalize("Federal Register", {"results": [{"title": "Rule", "html_url": VALID["Federal Register"], "type": "Rule"}]})
        nist = service.normalize("NIST", {"entries": [{"title": "Standard", "link": VALID["NIST"]}]})
        self.assertEqual(fr[0]["status"], "Final Rule")
        self.assertEqual(nist[0]["category"], "Cybersecurity")
        for source in ("FDIC", "Federal Reserve"):
            xml = ET.fromstring(f"<rss><channel><item><title>News</title><link>{VALID[source]}</link></item></channel></rss>")
            self.assertEqual(len(service.normalize(source, xml)), 1)

    def test_normalizer_rejects_wrong_source(self):
        data = {"results": [{"title": "False attribution", "html_url": VALID["NIST"]}]}
        self.assertEqual(service.normalize("Federal Register", data), [])

    def test_feed_checks_source_hosts_and_preserves_per_source_cache(self):
        fixture = {"results": [{"title": "Valid", "html_url": VALID["Federal Register"], "publication_date": "2026-11-03"}]}
        with patch.object(service, "SOURCES", {"Federal Register": service.SOURCES["Federal Register"]}), \
             patch.object(service, "fetch_source", return_value=fixture) as fetch:
            first = service.get_feed()
            self.assertEqual(len(first["articles"]), 1)
            self.assertEqual(service.get_feed()["articles"], first["articles"])
            fetch.assert_called_once()

    def test_unverified_feed_redirect_or_transport_failure_omitted(self):
        for failure in (ValueError("Unapproved source redirect"), OSError("offline")):
            service._cache = {}
            with patch.object(service, "fetch_source", side_effect=failure):
                self.assertEqual(service.get_feed()["articles"], [])

    def test_total_failure_does_not_overwrite_successful_cache(self):
        article = service.make_article("FDIC", "Previous verified", VALID["FDIC"], "2026-11-03")
        old = {"articles": [article], "fetched_at": -10000, "fetched_iso": "2026-11-03T00:00:00Z", "status": {"ok": True}}
        service._cache = {"FDIC": old}
        with patch.object(service, "fetch_source", side_effect=OSError("offline")):
            result = service.get_feed()
            self.assertEqual(result["articles"][0]["url"], article["url"])
            self.assertTrue(result["sources"]["FDIC"]["stale"])

    def test_feed_fetch_uses_validated_transport(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.status = 200
        response.read.return_value = b'{"results":[]}'
        with patch.object(sources, "open_source", return_value=response) as open_:
            self.assertEqual(sources.fetch_source("Federal Register"), {"results": []})
        self.assertEqual(open_.call_args.args[0], "Federal Register")

    def test_feed_response_size_limit_remains(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.status = 200
        response.read.return_value = b"x" * 2000001
        with patch.object(sources, "open_source", return_value=response):
            with self.assertRaises(ValueError):
                sources.fetch_source("NIST")


if __name__ == "__main__":
    unittest.main(verbosity=2)
