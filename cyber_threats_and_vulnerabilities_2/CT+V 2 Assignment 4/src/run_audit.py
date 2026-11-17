"""Run existing isolated suites with assignment-local evidence and safety guards."""
import contextlib
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import socket
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BACKEND = REPO / 'derexi-policy-pilot/backend'
sys.dont_write_bytecode = True


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def child(suite, folder):
    folder = Path(folder).resolve()
    folder.relative_to(ROOT)
    temporary = folder / 'tmp'
    temporary.mkdir(exist_ok=True)
    os.environ.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary),
                      PYTHON_DOTENV_DISABLED='1', DATABASE_URL='postgresql+psycopg2://offline:offline@127.0.0.1:1/offline',
                      DEREXI_ENV='test', DEREXI_DEV_AUTH='1', OPENAI_API_KEY='',
                      DEREXI_TEST_EVIDENCE_DIR=str(folder), DEREXI_SMTP_ENABLED='0')
    tempfile.tempdir = str(temporary)
    violations = []
    internal_transport = []

    def guard(event, args):
        if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo'}:
            frames = []
            frame = sys._getframe(1)
            while frame:
                frames.append((frame.f_code.co_filename, frame.f_code.co_name))
                frame = frame.f_back
            address = args[1] if event.startswith('socket.connect') else None
            if (isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1') and
                    any(filename == socket.__file__ and name in ('socketpair', '_fallback_socketpair') for filename, name in frames)):
                internal_transport.append({'event': event, 'purpose': 'stdlib Windows socketpair wakeup only'})
                return
            violations.append({'event': event, 'kind': 'network'})
            raise PermissionError('Network is disabled in Assignment 4')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if str(path).casefold() == r'\\.\nul':
                return
            if path.name == '.env':
                violations.append({'event': event, 'kind': 'credential-file'})
                raise PermissionError('Credential files are excluded')
            mode, flags = args[1], args[2]
            write = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
                isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
            if write and not path.is_relative_to(ROOT):
                violations.append({'event': event, 'kind': 'external-write', 'path': str(path)})
                raise PermissionError('Writes must stay inside Assignment 4')
        if event in {'os.mkdir', 'os.remove', 'os.rmdir', 'os.rename', 'os.replace'}:
            paths = args[:2] if event in {'os.rename', 'os.replace'} else args[:1]
            for value in paths:
                if isinstance(value, (str, bytes, os.PathLike)) and not Path(os.fsdecode(value)).resolve().is_relative_to(ROOT):
                    violations.append({'event': event, 'kind': 'external-mutation'})
                    raise PermissionError('Filesystem mutation outside Assignment 4')

    sys.addaudithook(guard)
    sys.path[:0] = [str(BACKEND / 'tests'), str(BACKEND)]
    started = now()
    checks = []
    error = None
    with (folder / 'suite.log').open('w', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            try:
                if suite == 'security':
                    module = importlib.import_module('test_week9_security')
                    module.OUT = folder
                    module.run()
                    checks = [{'name': c['name'], 'status': c['status'], 'actual': c.get('actual')} for c in module.checks]
                elif suite == 'governance':
                    module = importlib.import_module('test_week8_governance')
                    try:
                        module.run()
                    finally:
                        checks = [{'name': c['name'], 'status': 'PASS' if c['pass'] else 'FAIL'} for c in module.checks]
                elif suite == 'pulse':
                    module = importlib.import_module('test_pulse')
                    for name in ('test_date_parsing', 'test_text_helpers', 'test_classification',
                                 'test_normalize', 'test_combined_feed', 'test_ranking', 'test_radar'):
                        getattr(module, name)()
                    checks = ([{'name': n, 'status': 'PASS'} for n in module.PASSED] +
                              [{'name': n, 'status': 'FAIL'} for n in module.FAILED])
                elif suite == 'focused':
                    import messaging_fixture
                    from pulse.service import make_article
                    for label, url in [
                        ('FDIC unrelated host rejected', 'https://unrelated.example/notice'),
                        ('FDIC suffix spoof rejected', 'https://fdic.gov.unrelated.example/notice'),
                        ('FDIC shared-host wrong tenant rejected', 'https://content.govdelivery.com/accounts/USOTHER/bulletins/abc')]:
                        article = make_article(title='Bank policy', url=url, date='2026-11-17', summary='A banking policy notice', source='FDIC')
                        checks.append({'name': label, 'status': 'PASS' if article is None else 'FAIL', 'actual': 'rejected' if article is None else 'accepted'})
                    article = make_article(title='Bank policy', url='https://www.fdic.gov/news/financial-institution-letters/2026/example', date='2026-11-17', summary='A banking policy notice', source='FDIC')
                    checks.append({'name': 'FDIC approved host positive control', 'status': 'PASS' if article else 'FAIL'})
                    try:
                        messaging_fixture.blocked_connect()
                    except RuntimeError:
                        checks.append({'name': 'Existing PostgreSQL tripwire refuses connection', 'status': 'PASS'})
                else:
                    raise ValueError(suite)
            except BaseException as exc:
                error = type(exc).__name__ + ': ' + str(exc)
                traceback.print_exc()
                if 'module' in locals() and hasattr(module, 'checks') and not checks:
                    checks = [{'name': c['name'], 'status': c.get('status', 'PASS' if c.get('pass') else 'FAIL')} for c in module.checks]
    if error:
        checks.append({'name': 'Suite completed without harness/runtime error', 'status': 'BLOCKED', 'actual': error})
    checks.append({'name': 'Safety guard: no unexpected network/credential/external write attempts',
                   'status': 'PASS' if not violations else 'FAIL', 'actual': violations})
    result = {'suite': suite, 'started_at': started, 'ended_at': now(), 'internal_transport': internal_transport, 'checks': checks,
              'passed': sum(c['status'] == 'PASS' for c in checks),
              'failed': sum(c['status'] == 'FAIL' for c in checks),
              'blocked': sum(c['status'] == 'BLOCKED' for c in checks), 'error': error}
    save(folder / 'results.json', result)
    return int(bool(error) or any(c['status'] == 'FAIL' for c in checks))
    return bool(result['failed'] or result['blocked'])


def parent():
    run = ROOT / 'evidence' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run.mkdir(parents=True)
    source_paths = list((BACKEND / 'tests').glob('*.py')) + list(BACKEND.glob('*.py')) + list((BACKEND / 'pulse').glob('*.py'))
    source_paths += [REPO / 'derexi-policy-pilot/requirements.txt', REPO / 'derexi-policy-pilot/requirements-dev.txt', Path(__file__).resolve()]
    before = {str(p.relative_to(REPO)): digest(p) for p in source_paths}
    save(run / 'source-hashes-before.json', before)
    packages = sorted([{'name': d.metadata['Name'], 'version': d.version} for d in importlib.metadata.distributions()], key=lambda p: p['name'].lower())
    save(run / 'inventory.json', {'generated_at': now(), 'packages': packages, 'scope': 'Local Python distributions; no imports or online advisory scan'})
    summary = []
    for suite in ('security', 'governance', 'pulse', 'focused'):
        folder = run / suite
        folder.mkdir()
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', suite, str(folder)]
        started = time.monotonic()
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHON_DOTENV_DISABLED': '1'}
        with (folder / 'process.log').open('w', encoding='utf-8') as output:
            try:
                completed = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=150)
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code = 'TIMEOUT'
        path = folder / 'results.json'
        result = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'passed': 0, 'failed': 0, 'blocked': 1, 'error': 'Child produced no results; inspect process.log'}
        summary.append({'suite': suite, 'command': command, 'returncode': code, 'seconds': round(time.monotonic()-started, 3),
                        **{k: result[k] for k in ('passed', 'failed', 'blocked')}, 'results': str(path.relative_to(ROOT))})
    dependency = []
    req = (REPO / 'derexi-policy-pilot/requirements.txt').read_text()
    dependency.append({'name': 'Complete reviewed runtime hash lock', 'status': 'PASS' if '--hash=sha256:' in req and 'fastapi==' in req else 'FAIL', 'actual': 'Inspect requirements.txt; bounds are not a reproducible lock'})
    previous = json.loads((REPO / 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/advisories/assessment.json').read_text())
    for item in previous['packages']:
        if item.get('vulnerabilities'):
            current = [p['version'] for p in packages if p['name'].lower() == item['name'].lower()]
            dependency.append({'name': 'Historical affected-version condition: '+item['name'], 'status': 'FAIL' if current == [item['version']] else 'BLOCKED',
                               'actual': {'current': current, 'historical': item['version'], 'ids': [v['id'] for v in item['vulnerabilities']]},
                               'limit': 'Version match only; live trust store or malicious index prerequisites untested'})
    save(run / 'dependency-results.json', {'generated_at': now(), 'checks': dependency})
    after = {str(p.relative_to(REPO)): digest(p) for p in source_paths}
    save(run / 'source-integrity.json', {'unchanged': before == after, 'changed_paths': [k for k in before if before[k] != after[k]], 'files_checked': len(before)})
    blocked = [{'name': n, 'status': 'BLOCKED'} for n in ('Production Auth/RBAC/RLS and transport acceptance', 'Durable monitoring and independent operating review', 'Witnessed production recovery and RTO/RPO acceptance', 'Full current deployed dependency/OS/container advisory and provenance review')]
    totals = {k: sum(s[k] for s in summary) for k in ('passed', 'failed', 'blocked')}
    totals['passed'] += sum(c['status'] == 'PASS' for c in dependency) + int(before == after)
    totals['failed'] += sum(c['status'] == 'FAIL' for c in dependency) + int(before != after)
    totals['blocked'] += sum(c['status'] == 'BLOCKED' for c in dependency) + len(blocked)
    save(run / 'summary.json', {'generated_at': now(), 'python': sys.version, 'suites': summary, 'dependency_checks': dependency, 'scope_blocks': blocked, 'totals': totals,
                               'source_integrity': 'source-integrity.json', 'historical_result_files_overwritten': False,
                               'note': 'Existing suite code executed freshly; historical result files only referenced, never overwritten'})
    (ROOT / 'evidence/latest-run.txt').write_text(run.name+'\n')
    print(json.dumps({'run': run.name, 'totals': totals, 'suites': [{k: s[k] for k in ('suite','passed','failed','blocked','returncode')} for s in summary]}, indent=2))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        sys.exit(child(sys.argv[2], sys.argv[3]))
    parent()
