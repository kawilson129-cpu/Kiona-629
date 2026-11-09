"""Read-only Pulse lab dashboard. Default mode uses synthetic source input."""
import argparse
from collections import Counter
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "derexi-policy-pilot/backend"
if source.is_dir():
    sys.path.insert(0, str(source))

from pulse import service

def fixture(name):
    if name != "Federal Register":
        raise RuntimeError("Synthetic publisher outage")
    return {"results": [{
        "title": "Synthetic capital rule test fixture",
        "type": "Proposed Rule",
        "document_number": "fixture-1",
        "html_url": "https://www.federalregister.gov/documents/fixture-1",
        "publication_date": "2026-11-09",
        "agencies": [{"name": "Federal Reserve System"}],
    }]}

def render(feed, live):
    mode = "Live configured publishers" if live else "Synthetic fixture — no publisher contacted"
    bars = []
    for name, status in feed["sources"].items():
        count = status["count"]
        state = "healthy" if status["ok"] else ("stale" if status.get("stale") else "unavailable")
        bars.append(f"<li>{escape(name)}: {state}, {count} items "
                    f"<meter min='0' max='{max(1, count, feed['total_normalized'])}' value='{count}'>{count}</meter></li>")
    topics = Counter(article["category"] for article in feed["articles"])
    categories = "".join(f"<li>{escape(name)}: {count}</li>" for name, count in topics.items())
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>DeRexi Pulse Lab</title>"
            f"<h1>DeRexi Pulse Lab</h1><p>{mode}</p>"
            f"<p>Checked {escape(feed['checked_at'])}. "
            f"{feed['total_normalized']} unique normalized items. "
            f"{len(feed['articles'])} in display window.</p>"
            f"<h2>Sources before cross-source deduplication</h2><ul>{''.join(bars)}</ul>"
            f"<h2>Categories in display window</h2><ul>{categories}</ul></html>")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--bind", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.live and args.self_test:
        parser.error("--self-test requires fixture mode")
    if not args.live:
        service.fetch_source = fixture
    if args.self_test:
        feed = service.get_feed()
        assert feed["total_normalized"] == 1, feed
        assert sum(row["ok"] for row in feed["sources"].values()) == 1, feed
        assert len(feed["sources"]) == 4, feed
        html = render(feed, False)
        assert "Synthetic fixture" in html and "<meter" in html, html
        assert "&lt;" in render({**feed, "sources": {"<test>": {"ok": True, "count": 1}}}, False)
        print("PASS: normalization, partial outage, metrics, HTML escaping")
        return

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/healthz":
                body = b"ok"
                content_type = "text/plain"
            elif self.path == "/":
                body = render(service.get_feed(), args.live).encode("utf-8")
                content_type = "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with HTTPServer((args.bind, args.port), Handler) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()

