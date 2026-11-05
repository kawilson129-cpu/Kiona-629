"""Source-specific HTTPS attribution and redirect validation for Pulse."""

import urllib.request
from urllib.error import HTTPError
import re
from urllib.parse import urlsplit


APPROVED_HOSTS = {
    "Federal Register": frozenset({"federalregister.gov", "www.federalregister.gov"}),
    "FDIC": frozenset({"fdic.gov", "www.fdic.gov", "public.govdelivery.com", "content.govdelivery.com"}),
    "Federal Reserve": frozenset({"federalreserve.gov", "www.federalreserve.gov"}),
    "NIST": frozenset({"nist.gov", "www.nist.gov", "csrc.nist.gov", "nvlpubs.nist.gov"}),
}


def approved_url(source, url):
    if not isinstance(url, str) or not url or len(url) > 4096:
        return False
    if "\\" in url or any(ord(c) <= 32 or ord(c) == 127 for c in url):
        return False
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        if (parsed.scheme != "https" or host not in APPROVED_HOSTS.get(source, ())
                or parsed.username is not None or parsed.password is not None
                or parsed.port not in (None, 443)):
            return False
        # GovDelivery is multi-tenant. Host approval alone would attribute other
        # agencies' bulletins to FDIC. Restrict to the publisher's account/feed.
        if host == "content.govdelivery.com":
            return re.fullmatch(r"/accounts/USFDIC/bulletins/[A-Za-z0-9]+/?", parsed.path) is not None
        if host == "public.govdelivery.com":
            return parsed.path == "/topics/USFDIC_26/feed.rss"
        return True
    except (ValueError, UnicodeError):
        return False


class SourceRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, source):
        self.source = source

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not approved_url(self.source, newurl):
            raise ValueError("Unapproved source redirect")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        # HEAD must remain HEAD when checking article links.
        if redirected is not None and req.get_method() == "HEAD":
            redirected.method = "HEAD"
        return redirected


def open_source(source, request, timeout=12):
    """Keep inherited proxy/CA trust; validate before contact and every hop."""
    if not approved_url(source, request.full_url):
        raise ValueError("Unapproved source URL")
    opener = urllib.request.build_opener(SourceRedirectHandler(source))
    response = opener.open(request, timeout=timeout)
    if not approved_url(source, response.geturl()):
        response.close()
        raise ValueError("Unapproved final source URL")
    return response


def article_destination(source, url):
    """Check final destination without consuming bodies; fail closed on errors."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DeRexi-Pulse/0.2"})
    try:
        response = open_source(source, request, timeout=5)
    except HTTPError as exc:
        # Some government publishers do not implement HEAD. A GET uses the same
        # validated redirect chain and TLS/proxy configuration; never retry a
        # policy denial or authentication error and never consume the body.
        if exc.code not in (405, 501):
            raise
        exc.close()
        request = urllib.request.Request(url, headers={"User-Agent": "DeRexi-Pulse/0.2"})
        response = open_source(source, request, timeout=5)
    with response:
        return response.geturl()
