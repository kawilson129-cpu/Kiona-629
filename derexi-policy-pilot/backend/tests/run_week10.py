"""Targeted Week 10 runner. Artifacts only in the existing coursework directory.

Each suite runs in a fresh process, importing existing checks without invoking
legacy __main__ evidence writers. No dependency installation or live verification.
"""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / 'semester_5/DeRexi_Week 10/evidence'
SUITES = {
    'integration': ('test_week10_integration', ['run'], 'checks'),
    'governance': ('test_week8_governance', ['run'], 'checks'),
    'documents': ('test_document_intake', ['run'], 'checks'),
    'pulse': ('test_pulse', ['test_date_parsing', 'test_text_helpers', 'test_classification', 'test_normalize', 'test_combined_feed', 'test_ranking', 'test_radar'], 'PASSED'),
    'publisher-audit': ('test_c03_audit', ['req1_registry_is_closed', 'req2_attribution', 'req3_url_safety', 'req4_hostile_content', 'req5_dates', 'req6_dedupe', 'req7_classification', 'req8_9_failure_and_stale', 'req10_api_limits', 'req11_no_fabrication'], 'RESULTS'),
}


def one(name):
    # Install the existing live PostgreSQL tripwire before importing any app.
    sys.path[:0] = [str(HERE), str(HERE.parent)]
    import messaging_fixture  # noqa: F401
    module_name, functions, attr = SUITES[name]
    captured = io.StringIO()
    error = None
    module = None
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        try:
            module = importlib.import_module(module_name)
            for function in functions:
                getattr(module, function)()
        except Exception:
            error = traceback.format_exc()
            print(error)
    records = getattr(module, attr, []) if module else []
    if module_name == 'test_pulse' and module:
        records = [{'name': n, 'pass': True} for n in module.PASSED] + [{'name': n, 'pass': False} for n in module.FAILED]
    if module_name == 'test_c03_audit':
        for record in records:
            if record.get('basis', '').startswith('executed'):
                record['basis'] = 'executed in Week 10; synthetic fixtures'
                record['evidence'] = 'publisher-audit-run.txt'
    historical = [r for r in records if isinstance(r, dict) and r.get('basis', '').startswith('prior evidence')]
    records = [r for r in records if r not in historical]
    def passed(r):
        return r.get('pass', r.get('status') == 'PASS') if isinstance(r, dict) else r[1]
    failures = sum(not passed(r) for r in records)
    result = {'suite': name, 'mode': 'isolated fixtures; SQLite/real handlers; no live Supabase',
              'passed': sum(bool(passed(r)) for r in records), 'failed': failures,
              'execution_error': error, 'checks': records, 'historical_checks_excluded': historical}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '-results.json')).write_text(json.dumps(result, indent=2) + '\n')
    (OUT / (name + '-run.txt')).write_text(captured.getvalue())
    print(f"{name}: {result['passed']} PASS / {failures} FAIL" + (' / INCOMPLETE' if error else ''))
    return int(bool(failures or error))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--suite':
        sys.exit(one(sys.argv[2]))
    names = sys.argv[1:] or list(SUITES)
    codes = [subprocess.run([sys.executable, __file__, '--suite', name], cwd=HERE.parent).returncode for name in names]
    sys.exit(int(any(codes)))
