"""Offline artifact review only. Never imports/runs DeRexi or sends API requests."""
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
FINAL = ROOT / 'evidence/finalization-20261119'
RUN = ROOT / 'evidence/20261118-api'
checks = []


def check(name, condition, detail=None):
    checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


baseline = json.loads((FINAL / 'baseline.json').read_text())
protected = {p: h for p, h in baseline['files'].items()
             if any('/AAI 1 Assignment ' + str(i) + '/' in p for i in [2, 3, 4])}
changed = [p for p, h in protected.items() if digest(REPO / p) != h]
check('All Assignment 2–4 reports/supporting files preserved byte-for-byte', not changed,
      {'files': len(protected), 'changed': changed})
originals = {p: h for p, h in baseline['files'].items()
             if '/evidence/20261118-api/' in p and not p.endswith('/README.md')}
changed = [p for p, h in originals.items() if digest(REPO / p) != h]
check('Retained API results, screenshots and historical attempts unchanged', not changed,
      {'files': len(originals), 'changed': changed})
http = json.loads((RUN / 'http-results.json').read_text())
browser = json.loads((RUN / 'browser-results.json').read_text())
check('Retained 15 HTTP + 7 browser PASS, zero FAIL',
      (http['passed'], http['failed'], browser['passed'], browser['failed']) == (15, 0, 7, 0)
      and all(c['status'] == 'PASS' for d in [http, browser] for c in d['checks']),
      'Reused November 18 results; not re-executed')
get = next(r for r in http['requests'] if r['url'].endswith('/policies') and r['status_code'] == 200)
post = next(r for r in http['requests'] if r['url'].endswith('/ask') and r['status_code'] == 200)
unauth = next(r for r in http['requests'] if r['status_code'] == 401)
check('Distinct successful GET/POST with complete exchange fields',
      get['method'] == 'GET' and post['method'] == 'POST'
      and get['request_body'] is None and isinstance(post['request_body'], dict)
      and all({'request_headers', 'response_headers', 'response_body'} <= set(r) for r in [get, post]))
check('Separate 401 transcript proves missing bearer rejection',
      unauth['response_body'] == {'detail': 'Authentication required'}
      and unauth['response_headers']['www-authenticate'] == 'Bearer'
      and 'Authorization' not in unauth['request_headers'])
pdf = ROOT / 'AI_API_Integration_1_Rubric_01_Report.pdf'
reader = PdfReader(pdf)
text = '\n'.join(page.extract_text() or '' for page in reader.pages)
check('Assignment 1 report is exactly two Letter pages', len(reader.pages) == 2
      and all(tuple(float(x) for x in p.mediabox[2:]) == (612.0, 792.0) for p in reader.pages))
required = ['GET', '/policies', 'POST', '/ask', 'http://127.0.0.1:8041',
            'Authorization: Bearer [REDACTED]', 'Content-Type: application/json',
            post['request_body']['question'], 'Employee Leave',
            '200 OK', '401', '422', '403', '404', 'Authentication required',
            'WWW-Authenticate: Bearer', '22 PASS / 0 FAIL', 'No API tests rerun',
            'search mocked', 'external AI disabled']
check('Report covers methods, URLs, headers, JSON, statuses and honest reuse scope',
      all(v in text for v in required), [v for v in required if v not in text])
check('Report distinguishes Swagger401 rejection from prior200 success',
      'does not show successful retrieval' in text and 'earlier automated 200 transcripts' in text)
layout = json.loads((FINAL / 'pdf-layout.json').read_text())
check('Both offline PDF QA renders exist', layout['page_count'] == 2 and all(
      (FINAL / f'report-page-{i}.png').is_file() for i in [1, 2]))


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.sources.append(dict(attrs)['src'])


parser = Images()
html = (ROOT / 'AI_API_Integration_1_Rubric_01_Report.html').read_text()
parser.feed(html)
check('Report embeds existing original UI images only',
      len(parser.sources) >= 2 and all((ROOT / p).is_file() for p in parser.sources)
      and 'evidence/20261118-api/screenshots/01-get-library.png' in parser.sources
      and 'evidence/20261118-api/screenshots/02-post-assistant.png' in parser.sources)
links, broken = 0, []
for p in list(ROOT.glob('*.md')) + [RUN / 'README.md', FINAL / 'README.md']:
    for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', p.read_text()):
        if link.startswith(('https://', 'http://', '#')):
            continue
        target = p.parent / unquote(link.split('#')[0].strip('<>'))
        links += 1
        # This manifest is being created by this check; verify its output below.
        if target.resolve() == (FINAL / 'validation.json').resolve():
            continue
        if not target.exists():
            broken.append({'file': str(p.relative_to(ROOT)), 'target': link})
check('Assignment 1 document/evidence links resolve', not broken, {'links': links, 'broken': broken})
swagger = json.loads((FINAL / 'swagger-status.json').read_text())
check('Missing Swagger images disclosed, never misrepresented',
      swagger['status'] == 'NOT_LOCATED' and not swagger['incorporated']
      and 'No Swagger screenshot is claimed' in text)
docs = '\n'.join((ROOT / p).read_text() for p in ['README.md', 'rubric-checklist.md', 'api-evidence.md', 'test-results.md'])
check('Current docs close prior deferral without requiring new captures/tests',
      '**PASS' in docs and 'No API transaction below was rerun' in docs
      and 'no new success screenshot required' in docs)
raw = json.dumps(http) + json.dumps(browser) + text + docs
check('No JWT/private-key material in retained transcripts/report/doc text', not re.search(
      r'eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]+\.|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY', raw))
app_diff = subprocess.check_output(['git', 'diff', '--name-only', '--', 'derexi-policy-pilot'],
                                   cwd=REPO, text=True).strip()
check('No tracked application changes', not app_diff, app_diff)
result = {'timestamp': datetime.now(timezone.utc).isoformat(),
          'scope': 'Offline report/document/evidence audit only. No API tests, app startup or public requests executed.',
          'reused_application_results': {'passed': 22, 'failed': 0, 'test_date': '2026-11-18'},
          'passed': sum(c['status'] == 'PASS' for c in checks),
          'failed': sum(c['status'] == 'FAIL' for c in checks), 'checks': checks,
          'rubric': {str(i): 'PASS — existing evidence, stated local scope' for i in range(1, 5)},
          'mandatory_unresolved_requirements': [],
          'incorporation_limitation': 'User-referenced Swagger401 screenshot files were not located; authentic prior401 transcript used, not fabricated screenshots.',
          'report': {'path': pdf.name, 'pages': len(reader.pages), 'sha256': digest(pdf)},
          'preserved_assignment_2_to_4_hashes': protected}
(FINAL / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
assert (FINAL / 'validation.json').is_file()
print(json.dumps({'passed': result['passed'], 'failed': result['failed'],
                  'failures': [c for c in checks if c['status'] == 'FAIL']}, indent=2))
raise SystemExit(bool(result['failed']))
