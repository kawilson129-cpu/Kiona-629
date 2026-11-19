"""Offline verification of existing markup/evidence. Writes only html_1 results."""
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
NAMES = ['Assignment 1 - Semantic HTML', 'Assignment 2 - Web Elements',
         'Assignment 3 - HTML Attributes', 'Assignment 4 - Hyperlinks']
APP = 'derexi-policy-pilot/backend/static/index.html'
PAGE = 'docs/derexi-policy-pilot.md'


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append({'tag': tag, 'attrs': dict(attrs), 'line': self.getpos()[0]})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


app = Markup((REPO / APP).read_text())
case = Markup((REPO / PAGE).read_text())
all_checks = []
baseline = json.loads((ROOT / 'evidence/source-baseline.json').read_text())
outside_changes = subprocess.check_output(['git', 'status', '--porcelain', '-z'], cwd=REPO, text=True)
outside = [line[3:] for line in outside_changes.split('\0') if line and not line[3:].startswith('html_1/')]

for number, name in enumerate(NAMES, 1):
    folder = ROOT / name
    checks = []

    def check(label, condition, details=None):
        checks.append({'name': label, 'status': 'PASS' if condition else 'FAIL', 'details': details})

    source_map = json.loads((folder / 'evidence/source-map.json').read_text())
    failures = []
    for source in source_map['sources']:
        p = REPO / source['path']
        excerpt = '\n'.join(p.read_text().splitlines()[source['start_line']-1:source['end_line']]) + '\n'
        if sha(p) != source['source_sha256'] or excerpt != source['excerpt']:
            failures.append(source['path'])
    check('Exact original source hashes, line ranges and excerpt text match', not failures, failures)
    reused = json.loads((folder / 'evidence/reused-evidence.json').read_text())
    failures = [v['copy'] for v in reused['items'] if not (
        sha(folder / v['copy']) == v['sha256'] == sha(REPO / v['original_path']))]
    check('Existing images/test evidence copied byte-for-byte', not failures, failures)
    old = json.loads((folder / 'evidence/reused-browser-results.json').read_text())
    check('Historical browser evidence remains 7 PASS / 0 FAIL, not rerun',
          (old['passed'], old['failed']) == (7, 0) and all(v['status'] == 'PASS' for v in old['checks']),
          {'original_timestamp': old['timestamp'], 'scope': old['mode']})

    if number == 1:
        for tag in ['header', 'main', 'footer', 'nav']:
            matches = [v['line'] for v in app.elements if v['tag'] == tag]
            check(f'Literal <{tag}> exists in original DeRexi HTML', bool(matches), {'source': APP, 'lines': matches})
        check('Original HTML has one main landmark', sum(v['tag'] == 'main' for v in app.elements) == 1)
    elif number == 2:
        for tag in ['a', 'div']:
            check(f'DeRexi already contains literal <{tag}>', any(v['tag'] == tag for v in app.elements))
        for tag in ['a', 'div', 'img', 'ul']:
            check(f'Existing DeRexi case-study source contains literal <{tag}>', any(v['tag'] == tag for v in case.elements))
        static = REPO / 'derexi-policy-pilot/backend/static'
        found = [str(p.relative_to(REPO)) for p in static.iterdir()
                 if p.suffix in {'.html', '.js'} and re.search(r'<img\b|(?:createElement|h|el)\(\s*[\'\"]img[\'\"]', p.read_text())]
        check('Source-first search supports the image fallback (SVG not counted as img)', not found, found)
        image = next(v for v in case.elements if v['tag'] == 'img')
        check('Original image has alt text and correct existing Liquid asset',
              bool(image['attrs'].get('alt')) and '/assets/images/derexi-policy-pilot-hero.png' in image['attrs']['src']
              and 'relative_url' in image['attrs']['src'])
        check('Copied original image is an actual PNG asset',
              (folder / 'evidence/existing-derexi-project-image.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
        gov = (REPO / 'derexi-policy-pilot/backend/static/governance.js').read_text()
        check('Runtime ol is documented as JS-created, not literal source HTML',
              "el('ol',null,'gw-steps')" in gov and 'document.createElement(tag)' in gov)
    elif number == 3:
        inventory = json.loads((folder / 'evidence/attributes.json').read_text())
        check('At least seven distinct names (ten declared)', len({v['name'] for v in inventory['attributes']}) == 10)
        for item in inventory['attributes']:
            matching = [v for v in app.elements if v['tag'] == item['tag'] and v['line'] == item['line']
                        and item['name'] in v['attrs']]
            present = bool(matching) and (matching[0]['attrs'][item['name']] is None
                       if item['name'] == 'disabled' else matching[0]['attrs'][item['name']] == item['value'])
            check('Actual attribute ' + item['name'] + ' on its recorded element/line', present, item)
        check('Label for references actual select id', any(v['tag'] == 'label' and v['attrs'].get('for') == 'persona-select' for v in app.elements)
              and any(v['tag'] == 'select' and v['attrs'].get('id') == 'persona-select' for v in app.elements))
    elif number == 4:
        pulse = (REPO / 'derexi-policy-pilot/backend/static/pulse.js').read_text()
        check('Original Pulse helper creates actual DOM nodes and attributes',
              'document.createElement(tag)' in pulse and 'node.setAttribute(key, value)' in pulse)
        check('Original publication anchors use HTTPS destination, new context and safe rel',
              "title.appendChild(el('a', {" in pulse and 'href: article.url' in pulse
              and "target: '_blank'" in pulse and "rel: 'noopener noreferrer'" in pulse
              and 'return /^https:' in pulse)
        article = json.loads((folder / 'evidence/retained-article.json').read_text())
        destination = urlsplit(article['article']['url'])
        check('Actual retained publication destination is a separate HTTPS document',
              destination.scheme == 'https' and bool(destination.netloc) and '/documents/' in destination.path and not destination.fragment,
              {'source': article['original_path'], 'url': article['article']['url'], 'live_reachability': 'NOT TESTED'})
        check('SPA fragments explicitly distinguished from separate documents',
              any(v['tag'] == 'a' and v['attrs'].get('href') == '#assist' for v in app.elements)
              and 'excluded' in (folder / 'assignment_report.md').read_text())
        start = Markup((folder / 'index.html').read_text())
        target = Markup((folder / 'publication.html').read_text())
        a = next(v for v in start.elements if v['tag'] == 'a' and v['attrs'].get('id') == 'publication-link')
        href = urlsplit(a['attrs']['href'])
        check('Literal demo anchor leads to an existing distinct HTML document',
              href.path == 'publication.html' and not href.fragment and (folder / href.path).is_file()
              and (folder / href.path).resolve() != (folder / 'index.html').resolve())
        check('Destination is standalone HTML with return link and no script dependencies',
              any(v['tag'] == 'html' for v in target.elements)
              and any(v['tag'] == 'main' for v in target.elements)
              and any(v['tag'] == 'a' and v['attrs'].get('href') == 'index.html' for v in target.elements)
              and not any(v['tag'] in {'script', 'link'} for v in start.elements + target.elements))
        browser_path = ROOT / 'evidence/browser-verification.json'
        demo = json.loads(browser_path.read_text()) if browser_path.exists() else {}
        check('Actual local demo link click and return verified in Chromium',
              demo.get('failed') == 0 and demo.get('passed', 0) >= 4,
              'New coursework-demo check only; not a DeRexi API or publisher availability test')

    links, missing = 0, []
    for doc in [folder / 'README.md', folder / 'assignment_report.md']:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', doc.read_text()):
            if target.startswith(('http://', 'https://', '#')):
                continue
            p = doc.parent / unquote(target.split('#')[0])
            links += 1
            if p.resolve() == (folder / 'evidence/verification.json').resolve():
                continue
            if not p.exists():
                missing.append({'document': doc.name, 'target': target})
    check('Report and README source/evidence links resolve', not missing, {'links': links, 'missing': missing})
    result = {'timestamp': datetime.now(timezone.utc).isoformat(), 'assignment': number,
              'scope': 'New read-only source/markup/evidence checks; historical app tests reused, not rerun.',
              'passed': sum(v['status'] == 'PASS' for v in checks),
              'failed': sum(v['status'] == 'FAIL' for v in checks), 'checks': checks}
    result['completion_status'] = 'Complete' if not result['failed'] else 'Partial'
    (folder / 'evidence/verification.json').write_text(json.dumps(result, indent=2) + '\n')
    all_checks.extend([dict(v, assignment=number) for v in checks])

changed = [p for p, h in baseline['originals'].items() if sha(REPO / p) != h]
all_checks.append({'assignment': 'scope', 'name': 'Original app/Pages/evidence/root-memory/LMS screenshot hashes unchanged',
                   'status': 'PASS' if not changed else 'FAIL', 'details': changed})
all_checks.append({'assignment': 'scope', 'name': 'All working-tree writes confined to html_1',
                   'status': 'PASS' if not outside else 'FAIL', 'details': outside})
result = {'timestamp': datetime.now(timezone.utc).isoformat(),
          'scope': 'Offline markup/source/evidence audit, not a re-execution of existing app/API tests',
          'passed': sum(v['status'] == 'PASS' for v in all_checks),
          'failed': sum(v['status'] == 'FAIL' for v in all_checks), 'checks': all_checks}
(ROOT / 'evidence/verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'failed': result['failed'],
                  'failures': [v for v in all_checks if v['status'] == 'FAIL']}, indent=2))
raise SystemExit(bool(result['failed']))
