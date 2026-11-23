"""Offline packaging checks, not database execution or an SQL grammar parser."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
checks = []


def check(name, value, details=None):
    checks.append({'name': name, 'status': 'PASS' if value else 'FAIL', 'details': details})


data = json.loads((ROOT / 'evidence/live-readonly-20261123.json').read_text())
check('Fresh read-only result is VERIFIED, 8 PASS/0 FAIL, rolled back',
      (data['status'], data['passed'], data['failed']) == ('VERIFIED', 8, 0)
      and data['transaction_read_only'] == 'on' and data['transaction_end'] == 'ROLLED BACK'
      and data['mutations_executed'] is False)
inventory = json.loads((ROOT / 'evidence/source-inventory.json').read_text())
changed = [p for p, h in inventory['sources'].items()
           if hashlib.sha256((REPO / p).read_bytes()).hexdigest() != h]
check('Reused implementation/migrations/seed/tests/original evidence unchanged', not changed, changed)
for original, copy in inventory['historical_copies'].items():
    check('Historical copy ' + copy, (REPO / original).read_bytes() == (ROOT / 'evidence' / copy).read_bytes())
tree = ast.parse((ROOT / 'verify_readonly.py').read_text())
queries = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'QUERIES' for t in n.targets))
check('Verifier fixed SQL allowlist contains SELECT only', all(v.lstrip().upper().startswith('SELECT ') for v in queries.values()))
names = ['Assignment_1_Database_Connection', 'Assignment_2_Schema_Design', 'Assignment_3_Data_Operations',
         'Assignment_4_Query_Filtering', 'Assignment_5_Relational_Queries']
for number, name in enumerate(names, 1):
    folder = ROOT / name
    check(f'A{number} required report/SQL/evidence/output files',
          all((folder / n).is_file() for n in ['README.md', 'example.sql', 'evidence.md', 'verified-output.json']))
    output = json.loads((folder / 'verified-output.json').read_text())
    check(f'A{number} saved outputs exactly match actual shared record', all(v == data['queries'][k] for k, v in output['queries'].items()))
    sql = (folder / 'example.sql').read_text()
    if number in (1, 4, 5):
        key = {1: 'connection', 4: 'filter_sort', 5: 'join'}[number]
        check(f'A{number} example includes exact server-executed SELECT', queries[key] in sql and 'BEGIN READ ONLY;' in sql and 'ROLLBACK;' in sql)
    elif number == 2:
        original = (REPO / 'derexi-policy-pilot/backend/migrations/2026-11-05_week7_messaging.sql').read_text().splitlines()
        check('A2 DDL is verbatim original migration excerpt and explicitly unexecuted', '\n'.join(original[18:26]) in sql and 'DOCUMENTED ONLY' in sql)
    else:
        check('A3 INSERT explicitly unexecuted/local-only, no invented output',
              'DOCUMENTED ONLY / NOT EXECUTED' in sql and 'Local disposable PostgreSQL' in sql
              and 'INSERT INTO public.departments (name)' in sql
              and 'identity sequences can still advance' in sql
              and 'DOCUMENTED ONLY' in (folder / 'README.md').read_text())

constraints = data['queries']['constraints']['rows']
expected = [('users', 'FOREIGN KEY (department_id) REFERENCES departments(id)'),
            ('users', 'FOREIGN KEY (role_id) REFERENCES roles(id)'),
            ('policies', 'FOREIGN KEY (owner_id) REFERENCES users(id)')]
check('JOIN/report relationships match actual public FK catalog', all(any(r['table_name'] == t and r['definition'] == d for r in constraints) for t, d in expected))
links, broken = 0, []
for doc in ROOT.rglob('*.md'):
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', doc.read_text()):
        if target.startswith(('https://', 'http://', '#')):
            continue
        path = doc.parent / unquote(target.split('#')[0].strip('<>'))
        links += 1
        if path.resolve() == (ROOT / 'evidence/artifact-validation.json').resolve():
            continue
        if not path.exists():
            broken.append({'document': str(doc.relative_to(ROOT)), 'target': target})
check('Course Markdown links resolve', not broken, {'links': links, 'broken': broken})
findings = []
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix not in {'.md', '.sql', '.json', '.py'}:
        continue
    text = p.read_text()
    if p.suffix == '.json':
        json.loads(text)
    if re.search(r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]+\.|postgres(?:ql)?(?:\+psycopg2)?://[^\s]+:[^\s]+@', text):
        findings.append(str(p.relative_to(ROOT)))
check('JSON parses; no JWT/credential-bearing DSN patterns', not findings, findings)
result = {'timestamp': datetime.now(timezone.utc).isoformat(),
          'scope': 'Offline artifact validation; not added to the eight live read-only checks.',
          'passed': sum(c['status'] == 'PASS' for c in checks),
          'failed': sum(c['status'] == 'FAIL' for c in checks), 'checks': checks,
          'sql_validation': {'A1_A4_A5': 'Exact SELECTs executed successfully by PostgreSQL 17.6 inside READ ONLY',
                             'A2': 'Existing DDL excerpt/catalog comparison; no new DDL execution/parser claim',
                             'A3': 'Source/metadata-reviewed documentation only; INSERT not executed or server-parsed'}}
(ROOT / 'evidence/artifact-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'failed': result['failed'],
                  'failures': [c for c in checks if c['status'] == 'FAIL']}, indent=2))
raise SystemExit(bool(result['failed']))
