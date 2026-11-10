"""Retain each offline test run inside the required Assignment 3 workspace."""
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
log_path = ROOT / 'evidence' / f'tests-{stamp}.txt'
with log_path.open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_intel_ops.py')
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
data = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'interpreter': sys.executable, 'platform': platform.platform(),
    'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
    'failed': len(result.failures) + len(result.errors), 'blocked': len(result.skipped),
    'log': str(log_path.relative_to(ROOT)),
    'mode': 'verified local functions; synthetic telemetry and mocked collection failures; no live API or database tests',
    'failures': [{'test': str(test), 'traceback': tb} for test, tb in result.failures + result.errors],
    'skipped': [{'test': str(test), 'reason': why} for test, why in result.skipped],
    'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [ROOT / 'src/intel_ops.py', ROOT / 'tests/test_intel_ops.py', ROOT / 'tests/scenario.json']},
}
target = ROOT / 'evidence' / f'test-results-{stamp}.json'
target.write_text(json.dumps(data, indent=2) + '\n')
(ROOT / 'evidence/latest-tests.json').write_text(json.dumps({'results': str(target.relative_to(ROOT))}, indent=2) + '\n')
print(json.dumps({k: data[k] for k in ('passed', 'failed', 'blocked', 'log')}))
sys.exit(0 if result.wasSuccessful() else 1)
