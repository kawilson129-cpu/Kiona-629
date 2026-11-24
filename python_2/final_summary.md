# Python 2 Final Project · Final summary

## Completion and verification

**All eight supplied rubric criteria are VERIFIED.** Eight assignment folders each
contain a standalone demo, README, evidence record and detailed PDF-ready report
source. Execution timestamp: **2026-11-24T17:12:27.196167+00:00** · Python **3.9.6**.

- **26/26 behavioral tests PASS**; 0 failures, 0 errors, 0 skips.
- **8/8 standalone demo processes PASS**; every exit code is 0 with actual JSON output.
- **18/18 artifact checks PASS**; documentation/syntax/hash/cleanup checks are stored separately in
  [artifact-results.json](evidence/artifact-results.json).

[Rubric checklist](rubric_checklist.md) · [Evidence index](EVIDENCE_INDEX.md) ·
[Functional results](evidence/test-results.json) · [Unit transcript](evidence/unittest-transcript.txt).
The multiple assertions/subtests inside a unittest method are not inflated into
additional test-count claims. No historical DeRexi suite counts were added.

## Existing functionality reused

The review covered policy processing and database operations in main.py, connection
and cleanup in database.py, entity/schema definitions, identity/role enforcement in
security.py, optional-provider/configuration behavior, document intake/retention,
macOS parser supervision, transport protection and Pulse collection/ranking.
Existing source was read; actual credentials or .env files were not opened.

Direct runtime reuse is deliberately narrow: CONFIDENCE_THRESHOLD, contains_keyword,
relevance_score and its five ranking constants. Definitions are selected from their
unchanged original AST and compiled without importing the app. These are actual
original function calls, not mocks or copied reimplementations.

The production routes include session/query/commit behavior, but **none was executed
here**. Authentication/provider wiring and full DB integration are NOT TESTED in this
course. Pulse ranking verification does not establish feed integrity or clear the
[historical source-drift record](../cyber_threats_and_vulnerabilities_2/CT%2BV%202%20Assignment%203/evidence/concurrent-source-drift.json).

## Necessary new teaching examples

A reduced confidence decision supplies an explicit safe if/else. An in-memory queue
shows a changing Boolean while condition without OS process control. A list exercise
adds indexed reads/assignments with per-element transformations. Temporary-file
examples demonstrate UTF-8 read/write and try/except/else/finally, including successful
conversion, invalid/nonpositive values, missing file and directory errors. These
examples are new coursework, not production features or applied banking rules.

Temporary handles/directories are genuinely closed/removed and verified. No
application file/data/schema, user/role, key, setting, API, dependency or other
coursework was changed. Original source and the course screenshot are hash-checked.
No commit or push.

## Reproduce and remaining limitations

```sh
python3 -B python_2/run_verification.py
python3 -B python_2/run_verification.py --documents-only
```

No mandatory rubric gap remains. Execution is verified on the recorded local Python
interpreter; other OS/interpreter versions, live app/auth/database/API paths and
production storage/resource controls remain NOT TESTED. The exercise claims language
behavior only. A PDF conversion is optional; no PDF output is claimed.

## Session record

Permanent changes are confined to python_2. In keeping with the explicit no-unrelated-
changes instruction, root MEMORY.md is unchanged; this final summary records the
session instead. The original LMS screenshot is preserved. The repository was clean
at the start; final scope validation checks that additions remain course-local.
