"""Author the two-page report from retained evidence only; no API/app imports.

Uses the standard library. Print the resulting local HTML to PDF with Chrome.
Optional evidence/finalization-20261119/swagger-images.json must describe actual
visually reviewed existing images; this script never creates API screenshots.
"""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'evidence/20261118-api'
FINAL = ROOT / 'evidence/finalization-20261119'
data = json.loads((RUN / 'http-results.json').read_text())
browser = json.loads((RUN / 'browser-results.json').read_text())
assert (data['passed'], data['failed']) == (15, 0)
assert (browser['passed'], browser['failed']) == (7, 0)
get = next(r for r in data['requests'] if r['url'].endswith('/policies') and r['status_code'] == 200)
post = next(r for r in data['requests'] if r['url'].endswith('/ask') and r['status_code'] == 200)
unauth = next(r for r in data['requests'] if r['status_code'] == 401)


def json_block(value):
    return '<pre>' + escape(json.dumps(value, indent=2)) + '</pre>'


def footer(page):
    return f'''<footer><div class="footer-line"><b>VERIFICATION SCOPE</b><b>01 / 04 &nbsp; | &nbsp; {page} / 2</b></div>
      <p>Existing local HTTP / synthetic SQLite / search mocked / external AI disabled.</p>
      <p>22 PASS / 0 FAIL retained from Nov 18, 2026. No API tests rerun for this report.</p></footer>'''


def header(title, subtitle):
    return f'''<header><div class="brand">AURUM CAPITAL BANK &nbsp;/&nbsp; DeRexi</div>
      <div class="badge">VERIFIED / LOCAL</div><div class="course">AI API INTEGRATION 1 &nbsp; / &nbsp; ASSIGNMENT 1</div>
      <h1>{title}</h1><div class="subtitle">{subtitle}</div></header>'''


swagger = json.loads((FINAL / 'swagger-images.json').read_text()) if (FINAL / 'swagger-images.json').exists() else []
manual_html = ''
if swagger:
    blocks = []
    for item in swagger:
        path = ROOT / item['path']
        assert path.is_file() and path.resolve().is_relative_to(ROOT.resolve())
        assert item['observed_status'] == 401
        blocks.append(f'''<figure><img src="{escape(item['path'])}" alt="Existing Swagger capture of HTTP 401">
          <figcaption>{escape(item['caption'])}</figcaption></figure>''')
    manual_html = '<div class="swagger-images">' + ''.join(blocks) + '</div>'
else:
    manual_html = '''<p class="small muted"><b>Image availability:</b> the user-referenced Swagger 401 files were not located. No Swagger screenshot is claimed; the authentic H02 transcript below independently proves rejection.</p>'''

get_example = {k: get['response_body'][1][k] for k in ['id', 'title', 'latest_version']}
post_example = {k: post['response_body'][k] for k in ['conversation_id', 'needs_clarification', 'triage']}

html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>DeRexi — Assignment 1 HTTP Methods</title>
<style>
@page{size:letter;margin:0}*{box-sizing:border-box}html,body{margin:0;background:#F8F5EF;color:#2D251F;font-family:Arial,sans-serif}
.page{width:612pt;height:792pt;position:relative;padding:30pt 43pt 85pt;break-after:page;overflow:hidden;border-top:9pt solid #2D251F}
.page:last-child{break-after:auto}header{position:relative;padding-bottom:15pt;border-bottom:.6pt solid #E4D7C5;margin-bottom:15pt}
.brand{font-size:9pt;font-weight:bold;color:#A5783D}.course{font-size:8.5pt;color:#776D63;margin-top:15pt;letter-spacing:.3pt}
.badge{position:absolute;right:0;top:0;background:#E1ECE5;color:#426951;padding:8pt 12pt;border-radius:9pt;font-size:8pt;font-weight:bold}
h1{font:27pt/1.2 Georgia,serif;margin:12pt 0 8pt;letter-spacing:-.5pt}.subtitle{font:italic 11pt/1.3 Georgia,serif;color:#A5783D}
h2{font-size:9pt;line-height:1.3;letter-spacing:.3pt;margin:13pt 0 8pt}p{font-size:9.2pt;line-height:1.45;margin:6pt 0}
.muted{color:#776D63}.small{font-size:8pt;line-height:1.4}.pair{display:grid;grid-template-columns:1fr 1fr;gap:15pt}
.method{border-bottom:.6pt solid #E4D7C5;padding-bottom:9pt}.method b{font-size:12pt}.method p{font-size:8.5pt;margin:4pt 0}
code{font-family:Courier,monospace;font-size:8.5pt}pre{font:8.6pt/1.42 Courier,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:5pt 0}
.code-pair{background:#EEE6DA;padding:10pt 12pt;margin-top:8pt}.code-pair b{font-size:8pt}.question{font-size:8.7pt;margin:9pt 0 6pt}
.answer{border-left:2pt solid #C9B495;padding-left:10pt;font-size:9pt;margin:8pt 0}
.shots{margin-top:10pt}.shots img{width:100%;height:110pt;object-fit:contain;background:#EEE6DA;border-radius:7pt}
figure{margin:0}figcaption{font-size:7.7pt;line-height:1.35;color:#776D63;margin-top:5pt}
.band{background:#2D251F;color:#F8F5EF;border-radius:8pt;padding:10pt 13pt;margin:12pt 0}.band b{font-size:9pt;color:#E8D5B5}.band p{font-size:9pt;margin-bottom:0}
table{width:100%;border-collapse:collapse;margin:8pt 0;font-size:8.4pt}th,td{text-align:left;padding:5pt 7pt;border-bottom:.5pt solid #E4D7C5;vertical-align:top;line-height:1.4}th{background:#EEE6DA;font-size:8pt}
.status{white-space:nowrap;font-weight:bold}.availability{padding:9pt 12pt;background:#EEE6DA;margin:10pt 0}.availability>b{font-size:9pt}.availability p{font-size:8.6pt}
.swagger-images{display:flex;gap:12pt;margin:10pt 0}.swagger-images figure{flex:1;min-width:0}.swagger-images img{width:100%;height:150pt;object-fit:contain}
.auth-code{display:grid;grid-template-columns:1.2fr 1fr;gap:15pt;border-left:2pt solid #C9B495;padding:5pt 0 5pt 10pt;margin:10pt 0}.auth-code p{font-size:8.5pt}
.references{font-size:7.8pt;line-height:1.4;margin-top:10pt;color:#776D63}
section.page:nth-of-type(2) p{font-size:8.6pt;line-height:1.4}footer{position:absolute;left:43pt;right:43pt;bottom:25pt;border-top:.6pt solid #E4D7C5;padding-top:8pt}.footer-line{display:flex;justify-content:space-between;font-size:7.5pt;color:#A5783D}footer p{font-size:7.7pt;line-height:1.3;color:#776D63;margin:4pt 0 0}
</style></head><body>'''
html += '<section class="page">' + header('Two methods. One workflow.', 'Fetch a policy. Send a question. Display the result.')
html += '''<h2>TWO EXISTING RESTFUL HTTP METHODS</h2><div class="pair">
<div class="method"><b>GET &nbsp;/policies</b><p><code>http://127.0.0.1:8041/policies</code></p>
<p>Retrieves the approved-policy collection; no request body. The Library formats its JSON array as rows.</p>
<p><b style="font-size:9pt">200 OK</b> &nbsp; authenticated, retained result H04</p></div>
<div class="method"><b>POST &nbsp;/ask</b><p><code>http://127.0.0.1:8041/ask</code></p>
<p>Sends JSON and creates fixture conversation, message and clarification records; returns guidance and IDs.</p>
<p><b style="font-size:9pt">200 OK</b> &nbsp; retained results H07–H09</p></div></div>
<p class="small"><b>Both:</b> <code>Accept: application/json</code>; <code>Authorization: Bearer [REDACTED]</code>.<br>
<b>POST also:</b> <code>Content-Type: application/json</code>. Responses are JSON with <code>Cache-Control: no-store</code>.</p>'''
html += '<p class="question"><b>Actual POST request body</b></p>' + json_block(post['request_body'])
html += '<div class="pair code-pair"><div><b>GET 200 / ONE OF TWO RECORDS¹</b>' + json_block(get_example) + '</div><div><b>POST 200 / SELECTED FIELDS¹</b>' + json_block(post_example) + '</div></div>'
html += '<p class="answer">' + escape(post['response_body']['answer']) + '</p>'
html += '''<div class="pair shots"><figure><img src="evidence/20261118-api/screenshots/01-get-library.png"><figcaption>Existing Library capture, Nov 18. GET data displayed as readable policy rows.</figcaption></figure>
<figure><img src="evidence/20261118-api/screenshots/02-post-assistant.png"><figcaption>Existing Assistant capture, Nov 18. POST answer displayed as guidance.</figcaption></figure></div>
<div class="references">¹ Excerpts intentionally select fields. Complete sanitized requests/responses: api-evidence.md and evidence/20261118-api/http-results.json. UI proof: browser-results.json (B01–B04/B06). Existing results only; screenshots are not Swagger 200 captures.</div>'''
html += footer(1) + '</section><section class="page">' + header('Identity before access.', 'Authentication failures and successful requests prove different things.')
html += '''<div class="band"><b>401 ≠ 200</b><p>A Swagger 401 response demonstrates rejection of missing/invalid credentials. It does not show successful retrieval, a saved question, or a returned policy answer. Success is established separately by the earlier automated 200 transcripts and UI captures.</p></div>'''
html += manual_html
html += '<h2>AUTHENTIC RETAINED 401 / TRANSCRIPT H02</h2><div class="auth-code"><div><p><b>GET</b> <code>http://127.0.0.1:8041/policies</code><br>Accept: application/json<br>Authorization: absent · Body: none</p></div><div><p><b>401 Unauthorized</b><br>WWW-Authenticate: Bearer<br>Content-Type: application/json</p>' + json_block(unauth['response_body']) + '</div></div>'
html += '''<p><b>Authentication:</b> the successful local requests used the existing development-only, loopback signed-token provider. The server resolves identity and enforces role/ownership checks; a body-supplied user ID cannot override the token. This does not verify production Supabase sign-in.</p>
<table><thead><tr><th>Status</th><th>What the retained evidence demonstrates</th></tr></thead><tbody>
<tr><td class="status">200 OK</td><td>Authenticated GET returns policy JSON; POST processes the question. Existing POST contract uses 200, not 201. H04/H07–H09.</td></tr>
<tr><td class="status">401 Unauthorized</td><td>Missing bearer credentials rejected; authentication challenge returned. H02.</td></tr>
<tr><td class="status">422 / 403 / 404</td><td>Invalid question fields / identity mismatch / another employee's private conversation denied. H10–H12.</td></tr></tbody></table>
<h2>ALL FOUR SUPPLIED CRITERIA / SUPPORTED</h2>
<p class="small"><b>1.</b> GET + POST: H04/H07–H09, B02/B06. &nbsp;<b>2.</b> Formatted display: B01/B03–B05.<br>
<b>3.</b> Structured exchanges: api-evidence.md + retained JSON. &nbsp;<b>4.</b> Secured API and friendly output: H02/H03/H11/H12 + B01–B07; public JSON source observations are also retained.</p>
<p class="small muted">PostgreSQL search was mocked to no matches; this answer is deterministic clarification, not a live LLM result. Production data, authentication and external AI remain unverified. No mandatory new screenshot or runtime test is required by the supplied rubric.</p>
<div class="references">Kiona Wilson · Finalized Nov 19, 2026 · Existing DeRexi application. Evidence paths are relative to this Assignment 1 folder. Assignment 2–4 reports are preserved unchanged; instructor grading is separate.</div>'''
html += footer(2) + '</section></body></html>'
path = ROOT / 'AI_API_Integration_1_Rubric_01_Report.html'
path.write_text(html)
print(path)
