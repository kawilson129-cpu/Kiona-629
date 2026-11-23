"""Offline coursework validation only; never imports or contacts the application."""
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FOLDERS = [
    'assignment_01_design_document', 'assignment_02_project_summary',
    'assignment_03_problem_statement', 'assignment_04_use_case',
    'assignment_05_goals_objectives', 'assignment_06_key_features',
    'assignment_07_tech_stack', 'assignment_08_algorithm',
    'assignment_09_flowchart', 'assignment_10_timeline',
    'assignment_11_risk_mitigation', 'assignment_12_evaluation_criteria',
    'assignment_13_future_considerations',
]
checks = []


def check(name, condition, detail=''):
    checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL',
                   'detail': detail})


def read(path):
    return path.read_text(encoding='utf-8-sig')


def load(path):
    return json.loads(read(path))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(number):
    return read(ROOT / FOLDERS[number - 1] / 'DELIVERABLE.md')


def verify_mermaid(path, primary=False):
    """Check only this package's simple, one-edge-per-line Mermaid subset.

    This is deliberately not a full Mermaid parser or a rendering assertion.
    """
    diagram = read(path).strip()
    lines = diagram.splitlines()
    declarations, edges, errors = {}, [], []
    check(f'{path.name}: flowchart header',
          lines[0] in ('flowchart TD', 'flowchart LR'))
    for line in lines[1:]:
        match = re.fullmatch(r'\s*(.*?)\s*-->\s*(?:\|([^|]+)\|\s*)?(.*?)\s*', line)
        if not match:
            errors.append(line)
            continue
        endpoints = []
        for text in (match[1], match[3]):
            node = re.fullmatch(r'([A-Za-z][A-Za-z0-9_]*)(.*)', text.strip())
            if not node:
                errors.append(text)
                continue
            key, shape = node.groups()
            endpoints.append(key)
            if shape:
                allowed = (('([', '])'), ('[/', '/]'), ('[(', ')]'),
                           ('[', ']'), ('{', '}'))
                if not any(shape.startswith(a) and shape.endswith(b) for a, b in allowed):
                    errors.append(text)
                if key in declarations and declarations[key] != shape:
                    errors.append('Conflicting declaration: ' + key)
                declarations[key] = shape
        if len(endpoints) == 2:
            edges.append((endpoints[0], endpoints[1], match[2]))
    check(f'{path.name}: supported edge/shape subset', not errors, str(errors))
    missing = sorted({node for edge in edges for node in edge[:2]} - declarations.keys())
    check(f'{path.name}: all node references declared', not missing, str(missing))
    if primary:
        graph = defaultdict(list)
        for source, target, label in edges:
            graph[source].append((target, label))
        seen, pending = set(), ['S']
        while pending:
            node = pending.pop()
            if node not in seen:
                seen.add(node)
                pending.extend(target for target, _ in graph[node])
        check('Primary flow: every declared node reachable from Start', seen == set(declarations))
        check('Primary flow: every node can reach End', all(
            reaches_end(node, graph) for node in declarations))
        check('Primary flow: four rubric shape types',
              all(any(shape.startswith(prefix) for shape in declarations.values())
                  for prefix in ('([', '[/', '{')) and
              any(shape.startswith('[') and not shape.startswith(('[/', '[('))
                  for shape in declarations.values()))
        decisions = [node for node, shape in declarations.items() if shape.startswith('{')]
        check('Primary flow: decisions have labelled alternatives', bool(decisions) and all(
            len(graph[node]) >= 2 and all(label for _, label in graph[node])
            for node in decisions))
        check('Primary flow: exception paths retained', all(
            node in declarations for node in ('AE', 'VE', 'NF', 'IG', 'FB', 'ERR', 'CL')))
    return diagram


def reaches_end(start, graph):
    seen, pending = set(), [start]
    while pending:
        node = pending.pop()
        if node == 'E':
            return True
        if node not in seen:
            seen.add(node)
            pending.extend(target for target, _ in graph[node])
    return False


check('Exactly 13 requested assignment directories',
      sorted(p.name for p in ROOT.glob('assignment_*') if p.is_dir()) == sorted(FOLDERS))
for folder in FOLDERS:
    for name in ('README.md', 'DELIVERABLE.md'):
        path = ROOT / folder / name
        check(f'{folder}/{name}: substantive Markdown',
              path.is_file() and len(read(path).split()) >= 45)
for name in ('README.md', 'RUBRIC_CHECKLIST.md', 'EVIDENCE_MAP.md'):
    check(f'Course {name} exists', (ROOT / name).is_file())

master = body(1)
check('Master: all 13 numbered self-contained sections', all(
    re.search(rf'^## {i:02d} · ', master, re.M) for i in range(1, 14)))
check('Master: substantive supporting content embedded', all(
    body(i).split('\n\n---\n')[0].splitlines()[2].strip() in master
    for i in range(2, 14)))
check('Master: 12 supporting assignment links', all(
    f'../{FOLDERS[i - 1]}/DELIVERABLE.md' in master for i in range(2, 14)))
check('Summary: purpose, audience, importance and at least two sentences',
      len(re.findall(r'\.(?:\s|$)', body(2))) >= 2 and all(
          word in body(2) for word in ('employees', 'guidance', 'importance')))
check('Problem: banking context and defined governance problem', all(
    word.lower() in body(3).lower() for word in ('bank', 'problem', 'policy', 'owner')))
check('Use cases: three verified role workflows and fixture limits', all(
    word in body(4) for word in ('Employee', 'Policy Owner', 'System Administrator',
                                'UC-01', 'UC-02', 'UC-03', 'illustrative', 'unverified')))
check('Goals: at least two measurable targets with expected outcomes',
      len(re.findall(r'^\| G\d', body(5), re.M)) >= 2 and 'proposed' in body(5))
check('Features: all eight requested areas and status distinctions', all(
    word.lower() in body(6).lower() for word in ('search', 'feedback', 'routing',
    'Directory', 'Messages', 'Incident', 'Governance', 'Health', 'Pulse',
    'Implemented', 'tested', 'Planned', 'Unverified')))
check('Stack: verified choices, environments and proposal limits', all(
    word in body(7) for word in ('FastAPI', 'SQLAlchemy', 'PostgreSQL', 'HTML/CSS',
    'OpenAI', 'SQLite', 'proposals', 'not', 'schema drift')))
pseudocode = read(ROOT / FOLDERS[7] / 'policy-assistance-pseudocode.txt').strip()
check('Algorithm: editable pseudocode matches submission and master',
      pseudocode in body(8) and pseudocode in master)
check('Algorithm: decisions/error handling, thresholds and commit caveat', all(
    word in body(8) for word in ('0.22', 'keyword', '401', '403', '404', '422',
                                 '500', 'COMMIT', 'uncertainty', 'provider fails')))
flow = verify_mermaid(ROOT / FOLDERS[8] / 'policy-assistance.mmd', primary=True)
arch = verify_mermaid(ROOT / FOLDERS[6] / 'architecture.mmd')
check('Diagrams: editable source equals embedded Markdown/master',
      flow in body(9) and flow in master and arch in body(7) and arch in master)
check('Diagram scope: no false official-parser or render claim',
      'not** an official' in body(9) and 'optional tooling gap' in body(9))
plan = load(ROOT / 'evidence/original-plan-extract.json')
check('Original workbook: all twelve weeks extracted',
      [row['week'] for row in plan['weeks']] == [f'Week {n}' for n in range(1, 13)])
with (ROOT / FOLDERS[9] / 'timeline.csv').open(newline='') as handle:
    timeline = list(csv.DictReader(handle))
check('Timeline: twelve weeks mapped into three relative months',
      [int(row['week']) for row in timeline] == list(range(1, 13)) and
      all(int(row['relative_month']) == (int(row['week']) - 1) // 4 + 1 for row in timeline))
check('Timeline: monthly milestones, original targets and delays separated', all(
    word in body(10) for word in ('W4:', 'W8:', 'W12:', 'Original target',
                                  'later', 'not invented', 'pending')))
with (ROOT / FOLDERS[10] / 'risk-register.csv').open(newline='') as handle:
    risks = list(csv.DictReader(handle))
risk_fields = ('qualitative_likelihood', 'impact', 'mitigation', 'proposed_owner_role',
               'validation_method', 'observed_status')
check('Risks: at least one complete assessed risk with role/validation',
      len(risks) >= 1 and all(all(row.get(field) for field in risk_fields) for row in risks))
check('Evaluation: at least three indicators, measurement and targets',
      len(re.findall(r'^\| [^|]+ \| [^|]+ \| [^|]+ \|', body(12), re.M)) >= 5 and all(
          word in body(12) for word in ('Measurement method', 'Proposed target',
                                        'Observed', 'not previously', 'not measured')))
check('Future: maintenance plus proposed feature rationale/implementation', all(
    word in body(13) for word in ('Ongoing maintenance', 'Rationale',
                                  'Proposed future features', 'implementation', 'not currently')))

markdown = sorted(ROOT.rglob('*.md'))
bad_links, bad_fences, placeholders = [], [], []
link_count = 0
for path in markdown:
    text = read(path)
    if sum(line.startswith('```') for line in text.splitlines()) % 2:
        bad_fences.append(str(path.relative_to(ROOT)))
    if re.search(r'\{\{S\d+\}\}|\bTODO\b|\bTBD\b', text):
        placeholders.append(str(path.relative_to(ROOT)))
    for link in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text):
        link = link.strip('<>')
        url = urlsplit(link)
        if url.scheme:
            continue
        link_count += 1
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if not target.exists() and target != ROOT / 'evidence/validation.json':
            bad_links.append(f'{path.relative_to(ROOT)} -> {link}')
        if url.fragment:
            bad_links.append('Unexpected anchor requiring manual check: ' + link)
check('Markdown: all local evidence/navigation links resolve', not bad_links,
      f'{link_count} local links; failures={bad_links}')
check('Markdown: code fences balanced', not bad_fences, str(bad_fences))
check('Markdown: no unresolved citation tokens or placeholders', not placeholders, str(placeholders))

manifest = load(ROOT / 'evidence/source-manifest.json')
for sid, source in manifest['sources'].items():
    path = REPO / source['path']
    check(f'{sid}: inspected evidence exists and hash unchanged',
          path.is_file() and digest(path) == source['sha256'], source['path'])
check('Protected root MEMORY.md unchanged',
      digest(REPO / 'MEMORY.md') == manifest['protected_root_memory_sha256'])
original_image = next(ROOT.glob('Screenshot*.png'))
check('Original LMS screenshot unchanged',
      digest(original_image) == manifest['original_course_screenshot_sha256'])
check('Original plan extraction matches hashed workbook',
      plan['source_sha256'] == manifest['sources']['S02']['sha256'])
historical = load(REPO / manifest['sources']['S19']['path'])
check('Retained summary: 622/0/14 reconciles to suites, UAT/delivery pending',
      (historical['passed'], historical['failed'], historical['blocked']) == (622, 0, 14)
      and sum(row['passed'] for row in historical['suites']) == 622
      and historical['live_uat'] == 'PENDING' and not historical['real_email_sent'])
http = load(REPO / manifest['sources']['S28']['path'])
browser = load(REPO / manifest['sources']['S29']['path'])
check('Retained API evidence: 15 + 7 passes, mocked search/AI-off scope',
      (http['passed'], browser['passed'], http['failed'], browser['failed']) == (15, 7, 0, 0)
      and 'MOCKED' in http['mode'] and 'AI disabled' in http['mode'])
postgres = load(REPO / manifest['sources']['S21']['path'])
check('Retained PostgreSQL observation: eight read-only passes, no mutations',
      (postgres['passed'], postgres['failed']) == (8, 0)
      and postgres['transaction_read_only'] == 'on' and not postgres['mutations_executed'])
git = subprocess.run(['git', 'status', '--porcelain', '-z', '--untracked-files=all'],
                     cwd=REPO, check=True, text=True, capture_output=True)
changed = [entry[3:] for entry in git.stdout.split('\0') if entry]
check('Working tree: changes confined to this course', all(
    path.startswith('design_documentation_1/') for path in changed),
    f'{len(changed)} changed/untracked paths; no commit or push')

passed = sum(row['status'] == 'PASS' for row in checks)
failed = len(checks) - passed
result = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'scope': 'OFFLINE coursework artifact, source-hash and simple Mermaid-subset checks ONLY',
    'application_tests_executed': False, 'network_calls': False,
    'passed': passed, 'failed': failed, 'markdown_files': len(markdown),
    'local_links_checked': link_count, 'source_files_hashed': len(manifest['sources']),
    'checks': checks,
    'mermaid': {'structural_subset': 'checked', 'official_parser': 'UNAVAILABLE',
                'rendered_image': 'NOT GENERATED; no installed renderer; conditional requirement'},
    'coursework_coverage': {folder: 'COMPLETE' if failed == 0 else 'REVIEW VALIDATION FAILURES'
                            for folder in FOLDERS},
    'remaining_evidence_gaps': [
        'No new application verification: retained tests are dated, scoped observations.',
        'Real production identity/schema/ACL/RLS, delivery, human UAT, representative retrieval accuracy and latency remain unverified.',
        'Mermaid image export/full engine parsing unavailable; editable diagrams supplied.',
    ],
}
(ROOT / 'evidence/validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(f'Offline documentation validation: {passed} PASS / {failed} FAIL; '
      f'{len(markdown)} Markdown files; {link_count} local links; '
      f'{len(manifest["sources"])} source hashes.')
for row in checks:
    if row['status'] == 'FAIL':
        print('FAIL:', row['name'], row['detail'])
raise SystemExit(bool(failed))
