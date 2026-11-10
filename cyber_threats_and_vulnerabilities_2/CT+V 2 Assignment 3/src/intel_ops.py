"""Read-only CTI lab: reuse prior evidence; write only inside Assignment 3."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PRIOR = ROOT.parent / 'CT+V 2 Assignment 5'
MAX_BYTES = 2_000_000
PUBLIC_SOURCES = {
    'apt38': 'https://attack.mitre.org/groups/G0082/G0082-enterprise-layer.json',
    'fin7': 'https://attack.mitre.org/groups/G0046/G0046-enterprise-layer.json',
    'cisa-fastcash': 'https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf',
}
TECHNIQUES = {
    'attachment': ('T1566.001', 'Spearphishing Attachment'),
    'powershell': ('T1059.001', 'PowerShell'),
    'service': ('T1543.003', 'Windows Service'),
    'share': ('T1135', 'Network Share Discovery'),
    'collection': ('T1005', 'Data from Local System'),
}


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must include a timezone')
    return result.astimezone(timezone.utc)


def confined(path):
    result = Path(path).resolve()
    result.relative_to(ROOT)
    return result


def save(path, value):
    confined(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Redirect refused; review source configuration')


def fetch_public(key, opener=None):
    url = PUBLIC_SOURCES[key]
    request = Request(url, headers={'User-Agent': 'DeRexi-Coursework-CTI/1.0', 'Accept-Encoding': 'identity'})
    with (opener or build_opener(NoRedirect())).open(request, timeout=12) as response:
        if response.status != 200 or response.geturl() != url:
            raise ValueError('Unexpected source response')
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError('Source exceeds size ceiling')
    if key == 'cisa-fastcash':
        if not body.startswith(b'%PDF-'):
            raise ValueError('Expected PDF')
    else:
        data = json.loads(body)
        expected = 'APT38 (G0082)' if key == 'apt38' else 'FIN7 (G0046)'
        if data.get('name') != expected or data.get('domain') != 'enterprise-attack':
            raise ValueError('ATT&CK layer does not match the configured actor/domain')
        if not isinstance(data.get('techniques'), list) or not data['techniques']:
            raise ValueError('Expected nonempty ATT&CK Navigator layer')
        if any(not re.fullmatch(r'T\d{4}(?:\.\d{3})?', t.get('techniqueID', '')) for t in data['techniques']):
            raise ValueError('Malformed ATT&CK technique identifier')
    return body


def historical_indicators(now):
    prior = runpy.run_path(str(PRIOR / 'intel-ledger.py'), run_name='prior_ledger')
    rows = [(kind, value, source, 'k.php') for source in ('E02', 'E05')
            for kind, value in (('sha256', prior['HASH']), ('url', prior['URL']))]
    records = prior['reconcile'](rows)
    for record in records:
        value = record['value']
        if record['type'] == 'url':
            parsed = urlsplit(value.replace('hxxp', 'http', 1).replace('[.]', '.'))
            if not value.startswith(('hxxp://', 'hxxps://')) or not parsed.hostname or parsed.username or re.search(r'\s', value):
                raise ValueError('Unsafe indicator representation')
        observed = utc('2026-08-27T10:04:48Z')
        review = observed + timedelta(days=90 if record['type'] == 'sha256' else 14)
        record.update(observed_at=observed.isoformat(), review_at=review.isoformat(),
                      state='expired' if now >= review else 'research_only',
                      confidence=70, independent_source_families=['E02'],
                      evidence_kind='historical course dossier; E05 derives from E02',
                      actor_attribution='unknown', enforcement_allowed=False)
    return rows, records


def review_indicator(record, action, analyst, reason, at):
    if not analyst.strip() or not reason.strip():
        raise ValueError('Analyst and reason are required')
    states = {'approve_hunt': 'approved_for_hunt', 'revoke': 'revoked', 'false_positive': 'false_positive'}
    if action not in states:
        raise ValueError('Unsupported review action')
    if action == 'approve_hunt' and (record['state'] in ('revoked', 'false_positive') or at >= utc(record['review_at'])):
        raise ValueError('Stale or suppressed indicators require new evidence before hunting')
    result = deepcopy(record)
    result['state'] = states[action]
    result.setdefault('review_history', []).append({'at': at.isoformat(), 'action': action, 'analyst': analyst, 'reason': reason})
    result['enforcement_allowed'] = False
    return result


def track(events, window_minutes=30):
    unique = {}
    for event in events:
        if event.get('simulation') is not True or event['kind'] not in TECHNIQUES:
            raise ValueError('Only explicitly labelled scenario events are supported')
        utc(event['time'])
        if not event.get('host') or not event.get('case'):
            raise ValueError('Host and case are required')
        if event['id'] in unique and event != unique[event['id']]:
            raise ValueError('Conflicting event identifier')
        unique[event['id']] = event
    mapped = [{**event, 'technique': TECHNIQUES[event['kind']][0]}
              for event in sorted(unique.values(), key=lambda x: utc(x['time']))]
    alerts = []
    for host, case in sorted({(e['host'], e['case']) for e in mapped}):
        local = [e for e in mapped if (e['host'], e['case']) == (host, case)]
        for start in local:
            finish = next((e for e in local if e['kind'] == 'service' and
                           0 <= (utc(e['time']) - utc(start['time'])).total_seconds() <= window_minutes * 60), None)
            if start['kind'] == 'powershell' and finish:
                alerts.append({'host': host, 'case': case, 'event_ids': [start['id'], finish['id']],
                               'techniques': ['T1059.001', 'T1543.003'], 'simulation': True,
                               'actor_attribution': 'unknown', 'priority': 'high',
                               'reason': 'Same host/case: PowerShell followed by service within 30 minutes'})
                break
    return mapped, alerts


def benchmark(alerts, expected):
    actual = {a['host'] for a in alerts}
    if not actual <= set(expected):
        raise ValueError('Benchmark does not label all detected hosts')
    tp = sum(label and host in actual for host, label in expected.items())
    fp = sum(not label and host in actual for host, label in expected.items())
    fn = sum(label and host not in actual for host, label in expected.items())
    tn = len(expected) - tp - fp - fn
    return {'scope': 'controlled scenario labels only; not production detection rates',
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None}


def reconcile_findings():
    old_path = ROOT.parent / 'CT+V 2 Assignment 2/closure/inspector/findings.json'
    fresh_path = REPO / 'semester_5/DeRexi_Week 9/evidence/parser-fix-regressions/test_week9_security-results.json'
    old, fresh = json.loads(old_path.read_text()), json.loads(fresh_path.read_text())
    required = {f'Direct {kind} bypass blocked {uid}' for kind in ('policy creation', 'version') for uid in (8, 4, 2)}
    passed = {c['name'] for c in fresh['checks'] if c['status'] == 'PASS'}
    newer = utc(fresh['timestamp']) > utc(old['generated_at'])
    findings = []
    for finding in old['findings']:
        superseded = finding['id'] == 'DVI-POLICY-WRITE' and newer and required <= passed
        findings.append({'id': finding['id'], 'historical_severity': finding['severity'],
                         'historical_score': finding['score'],
                         'disposition': 'superseded_in_newer_isolated_tests' if superseded else 'requires_current_validation',
                         'evidence_kind': 'historical finding reconciled against retained Week 9 evidence',
                         'action': 'Review current isolated write-denial evidence; do not claim production closure' if superseded else finding['corrective_action'],
                         'source': str(old_path.relative_to(REPO)),
                         'newer_context': str(fresh_path.relative_to(REPO)) if superseded else None})
    return sorted(findings, key=lambda f: (f['disposition'] == 'superseded_in_newer_isolated_tests', -f['historical_score']))


def run(collect=False, output=None, as_of=None):
    start = time.perf_counter()
    now = utc(as_of) if as_of else datetime.now(timezone.utc)
    out = confined(output or ROOT / 'evidence/runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    out.mkdir(parents=True, exist_ok=False)
    collection = []
    for key, url in PUBLIC_SOURCES.items():
        result = {'source': key, 'url': url, 'attempted_at': datetime.now(timezone.utc).isoformat(),
                  'status': 'UNTESTED', 'evidence_kind': 'not collected in offline mode'}
        if collect:
            try:
                body = fetch_public(key)
                name = key + ('.pdf' if key == 'cisa-fastcash' else '.json')
                (out / name).write_bytes(body)
                result.update(status='VERIFIED', evidence_kind='fresh public-source collection',
                              bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), artifact=name)
            except Exception as exc:
                result.update(status='BLOCKED', evidence_kind='attempted public-source collection; failed',
                              error=f'{type(exc).__name__}: {exc}')
        collection.append(result)
    rows, indicators = historical_indicators(now)
    scenario = json.loads((ROOT / 'tests/scenario.json').read_text())
    events, alerts = track(scenario['events'])
    findings = reconcile_findings()
    coverage = []
    for source in collection:
        if source['status'] == 'VERIFIED' and source['source'] != 'cisa-fastcash':
            techniques = {t['techniqueID'] for t in json.loads((out / source['artifact']).read_text())['techniques']}
            coverage.append({'actor': source['source'], 'context_techniques': sorted(techniques & {e['technique'] for e in events}),
                             'relationship': 'shared behavior context only; no attribution of scenario'})
    campaigns = [
        {'id': 'FASTCASH-2020', 'kind': 'historical public reporting', 'actor': 'APT38/BeagleBoyz per referenced reporting', 'local_sightings': None},
        {'id': 'DEREXI-TABLETOP', 'kind': 'simulated', 'actor': 'unknown', 'alerts': alerts},
        {'id': 'KPHP-HISTORICAL', 'kind': 'historical malware dossier', 'actor': 'unknown', 'indicator_count': len(indicators)},
    ]
    metrics = {'as_of': now.isoformat(), 'input_indicator_records': len(rows), 'unique_indicators': len(indicators),
               'duplicate_ratio': (len(rows) - len(indicators)) / len(rows),
               'provenance_completeness': sum(bool(i['sources']) for i in indicators) / len(indicators),
               'expired_indicators': sum(i['state'] == 'expired' for i in indicators),
               'independent_indicator_source_families': 1, 'campaigns': len(campaigns),
               'events': len(events), 'alerts': len(alerts), 'benchmark': benchmark(alerts, scenario['expected_hosts']),
               'collection_verified': sum(c['status'] == 'VERIFIED' for c in collection),
               'collection_blocked': sum(c['status'] == 'BLOCKED' for c in collection),
               'elapsed_ms': round((time.perf_counter() - start) * 1000, 3)}
    for name, value in [('collection', collection), ('indicators', indicators), ('campaigns', campaigns),
                        ('mapped-events', events), ('actor-context', coverage), ('prioritized-findings', findings), ('metrics', metrics)]:
        save(out / f'{name}.json', value)
    manifest = {}
    for path in [PRIOR / 'intel-ledger.py', ROOT / 'src/intel_ops.py', ROOT / 'tests/scenario.json',
                 ROOT.parent / 'CT+V 2 Assignment 2/closure/inspector/findings.json',
                 REPO / 'semester_5/DeRexi_Week 9/evidence/parser-fix-regressions/test_week9_security-results.json']:
        manifest[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    save(out / 'source-hashes.json', manifest)
    (out / 'report.md').write_text(
        '# CTI lab run\n\n' + f"As of {now.isoformat()}. Local research/simulation; no production sightings.\n\n"
        + f"Indicators: {len(rows)} observations → {len(indicators)} unique; {metrics['expired_indicators']} expired. "
        + f"Campaigns: {len(campaigns)}; scenario alerts: {len(alerts)}.\n\n"
        + 'Priorities below are historical finding scores, not current vulnerability claims.\n\n'
        + '\n'.join(f"- {f['id']}: {f['disposition']}; {f['action']}" for f in findings)
        + '\n\nOpenCTI operation and real sensor detections remain unverified.\n')
    return out, metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true', help='Read only the three fixed public-source URLs')
    parser.add_argument('--as-of', help='Timezone-aware review time; does not change observation dates')
    parser.add_argument('--output', help='New output directory inside Assignment 3 only')
    args = parser.parse_args()
    directory, results = run(args.collect, args.output, args.as_of)
    print(json.dumps({'evidence': str(directory.relative_to(ROOT)), 'metrics': results}, indent=2))
