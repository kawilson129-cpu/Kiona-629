"""Check risk arithmetic, evidence integrity and local document links."""
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
checks = []


def check(name, actual):
    checks.append({'name': name, 'status': 'PASS' if actual else 'FAIL'})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


run_name = (ROOT / 'evidence/latest-run.txt').read_text().strip()
run = ROOT / 'evidence' / run_name
run.resolve().relative_to(ROOT)
summary = json.loads((run / 'summary.json').read_text())
before = json.loads((run / 'source-hashes-before.json').read_text())
for path, expected in before.items():
    check('Source fingerprint: '+path, sha(REPO / path) == expected)
check('Source integrity run result', json.loads((run / 'source-integrity.json').read_text())['unchanged'])
totals = dict(passed=0, failed=0, blocked=0)
for suite in summary['suites']:
    result = json.loads((ROOT / suite['results']).read_text())
    for key, state in [('passed','PASS'),('failed','FAIL'),('blocked','BLOCKED')]:
        count = sum(c['status'] == state for c in result['checks'])
        check(suite['suite']+' reconciles '+state, count == suite[key] == result[key])
        totals[key] += count
    check(suite['suite']+' has successful final process exit', suite['returncode'] == 0)
    check(suite['suite']+' safety check passes', result['checks'][-1]['status'] == 'PASS')
for item in summary['dependency_checks'] + summary['scope_blocks']:
    totals[{'PASS':'passed','FAIL':'failed','BLOCKED':'blocked'}[item['status']]] += 1
totals['passed'] += 1
check('Final outcome totals independently reconcile', totals == summary['totals'])
inventory = json.loads((run / 'inventory.json').read_text())['packages']
current = {(d.metadata['Name'], d.version) for d in importlib.metadata.distributions()}
check('Inventory matches current interpreter metadata', {(p['name'],p['version']) for p in inventory} == current)
historical = json.loads((REPO / 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/advisories/assessment.json').read_text())
for old in historical['packages']:
    if old.get('vulnerabilities'):
        record = next(c for c in summary['dependency_checks'] if c['name'].endswith(': '+old['name']))
        versions = [p['version'] for p in inventory if p['name'].lower() == old['name'].lower()]
        check('Exact historical version match: '+old['name'], record['actual']['current'] == versions)

with (ROOT / 'docs/risk-register.csv').open(encoding='utf-8', newline='') as stream:
    risks = list(csv.DictReader(stream))
check('Ten unique mapped risk IDs', len(risks) == len({r['risk_id'] for r in risks}) == 10)
for r in risks:
    value = lambda k: Decimal(r[k])
    for frequency, loss in [('inherent_aro','inherent_ale_usd'),('residual_aro','residual_ale_usd'),
                            ('residual_aro_low','residual_ale_low_usd'),('residual_aro_high','residual_ale_high_usd'),('target_aro','target_ale_usd')]:
        check(r['risk_id']+' arithmetic '+loss, value(frequency)*value('sle_usd') == value(loss))
    check(r['risk_id']+' treatment and uncertainty ordering', value('target_aro') <= value('residual_aro') <= value('inherent_aro') and value('residual_aro_low') <= value('residual_aro') <= value('residual_aro_high'))
    ale = value('residual_ale_usd')
    severity = 'Critical' if ale >= 250000 else 'High' if ale >= 50000 else 'Medium' if ale >= 10000 else 'Low'
    check(r['risk_id']+' severity threshold', r['residual_severity'] == severity)
    check(r['risk_id']+' ownership and closure fields', all(r[k] for k in ('asset','threat','vulnerability_or_gap','proposed_owner','closure_criteria','treatment','evidence_id')))

required = ['README.md','docs/rubric-checklist.md','docs/risk-assessment.md','docs/risk-register.csv','docs/audit-program.md','docs/framework-control-mapping.md','docs/control-validation.md','docs/audit-report.md','docs/final-summary.md','docs/progress.md']
for path in required:
    check('Required output: '+path, (ROOT / path).is_file())
for document in ROOT.rglob('*.md'):
    body = document.read_text(encoding='utf-8')
    for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', body):
        if link.startswith(('http://','https://','#')):
            continue
        target = unquote(link.split('#')[0].strip('<>'))
        check('Local link: '+document.name+' -> '+target, (document.parent / target).exists())

reuse = [
 'cyber_threats_and_vulnerabilities_2/Cyber Threats and Vulnerabilities 2 Tasks.pdf',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 1/docs/supply-chain-assessment.md',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 1/docs/final-summary.md',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/README.md',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/assets-reconciled.json',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/advisories/assessment.json',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 3/docs/final-summary.md',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 5/04-risk-audit.md',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 5/completion-matrix.md',
 'compliance_1/C 1 Assignment 3/rubric1_security_test_results.md',
 'compliance_1/C 1 Assignment 3/assignment3_c03_audit_results.md',
 'compliance_1/C 1 Assignment 3/assignment3_security_hardening_final.md',
 'semester_5/DeRexi_Week 11/pinned-readiness-status.md',
 'semester_5/DeRexi_Week 11/final-integration-approval-checklist.md',
 'semester_5/DeRexi_Week 11/evidence/final-integration-20261112/security-results.json',
 'semester_5/DeRexi_Week 11/evidence/final-integration-20261112/governance-results.json',
 'semester_5/DeRexi_Week 11/evidence/final-integration-20261112/pulse-results.json',
 'derexi-policy-pilot/docs/deployment.md']
manifest = [{'path': path, 'sha256': sha(REPO / path)} for path in reuse]
check('Official rubric identity matches visually reviewed rendering', manifest[0]['sha256'] == '5961118200fea38c10c2e9cf1d4aa6685c6f5750ddbcc44082c5ebcd9351f07b')
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
(ROOT / 'evidence/reuse-manifest.json').write_text(json.dumps({'captured_at': stamp, 'method': 'Validation-time hashes, not original publication attestation', 'files': manifest}, indent=2)+'\n', encoding='utf-8')
failed = [c for c in checks if c['status'] == 'FAIL']
report = {'generated_at': stamp, 'scope': 'Artifact arithmetic, source/link integrity and count reconciliation; not security effectiveness', 'collector_run':run_name, 'passed':len(checks)-len(failed), 'failed':len(failed), 'checks':checks}
(ROOT / ('evidence/package-validation-'+stamp+'.json')).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'passed': report['passed'], 'failed': report['failed'], 'failures': failed}, indent=2))
sys.exit(bool(failed))
