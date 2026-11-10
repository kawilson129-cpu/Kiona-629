# Week 9 targeted parser resource-limit fix

Only runtime change: `derexi-policy-pilot/backend/document_limits.py`.
Recoverable source copy: `/private/tmp/derexi-parser-portability-checkpoint/document_limits.py`.
Added focused tests: `backend/tests/test_document_limits.py`; source hashes saved in
`evidence/parser-fix-source-hashes.json`. No dependencies installed or upgraded.

- POSIX CPU/memory targets are the minimum of the requested ceiling and existing
  finite soft/hard limits. Linux retains RLIMIT_AS; unsupported platforms fail closed.
  [Python resource limit contract](https://docs.python.org/3/library/resource.html).
- Darwin's AS/RSS alias cannot supply the existing allocation cap here. The worker
  forks before reading/extracting input; the original process becomes a supervisor.
  It queries libproc resident size and physical footprint every 10 ms and kills/reaps
  extraction above the stricter 256 MiB/inherited ceiling, on measurement failure,
  or at 10 seconds. ABI checked against the installed macOS SDK and
  [Apple's rusage definitions](https://github.com/apple/darwin-xnu/blob/main/bsd/sys/resource.h).
- CPU stays at at most 8 seconds; the API's 12-second subprocess timeout, input size,
  XML security, archive validation, output bound and concurrency limit are unchanged.
- Windows Job Object memory/CPU setup is unchanged and still fails closed on API errors.

| Checks executed on Mac | PASS | FAIL | BLOCKED | Evidence |
|---|---:|---:|---:|---|
| Full existing document parser suite | 47 | 0 | 0 | `evidence/parser-fix-results.json`, `parser-fix-run.txt` |
| Resource selection/native Mac enforcement | 14 | 0 | 0 | `evidence/parser-limit-results.json`, `parser-limit-run.txt` |
| Essential Week 9 security | 110 | 0 | 0 | `evidence/parser-fix-regressions/test_week9_security-results.json` |
| Existing JWT crypto | 24 | 0 | 0 | `evidence/parser-fix-regressions/test_week7_auth-results.json` |

Real DOCX/PDF extraction, malformed documents, XML entities, archive traversal/bombs,
oversized requests, permissions and persistence regressions all pass with SQLite
fixtures and a PostgreSQL connection tripwire. Native tests also demonstrate memory
termination, monitor-failure termination and sleeping-worker timeout. Linux ceiling
selection is tested using mocks, not a native Linux kernel. No live provider/database
requests, migrations, Auth/RBAC/Governance/UI changes, commits or pushes.

Limitations: native Windows/Linux execution remains unverified. Mac sampling is
reactive and can permit transient overshoot between polls; it does not impose a
kernel allocation ceiling. A strict instantaneous allocation guarantee requires a
validated stronger deployment sandbox. Fork/libproc or measurement failure denies
parsing; unknown POSIX platforms deny parsing. Production blockers in the main Week 9
report are unchanged. Earlier failed runs and root-cause evidence remain preserved.

Reproduce from `derexi-policy-pilot/backend/` with the project Mac `.venv`:

```python
# Import avoids the existing script's canonical-docs evidence writer.
import sys
sys.path.insert(0, 'tests')
import test_document_intake
try:
    test_document_intake.run()
finally:
    print(test_document_intake.checks)
```

Run that snippet with `../.venv/bin/python`; save output and check JSON in this Week 9
folder. Resource tests: `../.venv/bin/python -m unittest discover -s tests -p test_document_limits.py -v`.
Security: `../.venv/bin/python tests/test_week9_security.py` and
`../.venv/bin/python tests/test_week7_auth.py`; keep any new evidence in this folder.
The new regression run redirected the Week 9 suite's `OUT` to `evidence/parser-fix-regressions/`
to preserve prior evidence. An initial JWT wrapper mistakenly expected `run()`;
`jwt-runner-initial-error.txt` records the tooling error. The corrected wrapper ran
all 24 existing `test_*` functions successfully; no test/application edits were needed.
