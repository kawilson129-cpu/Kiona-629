# Evidence · Assignment 4

**Status: PASS for the supplied documentary/logic criterion.** New code consists
of course verification only; application source is unchanged.

## Source paths, functions and line references

- [derexi-policy-pilot/backend/messaging.py](../../derexi-policy-pilot/backend/messaging.py) · `list_notifications`, lines **518–579**.
- [derexi-policy-pilot/backend/messaging.py](../../derexi-policy-pilot/backend/messaging.py) · `_unread_count`, lines **143–152**.

The original literal classification chain is at messaging.py lines 547–555. [Verbatim fragment](source-conditional.txt), [pseudocode](pseudocode.txt), [flowchart](notification-kind.mmd), and [actual synthetic case results](sample-results.json) are retained locally.

## Actual results

Six notification classification/actor-fallback cases N1–N6 PASS. The literal original if/elif/else AST fragment is executed unchanged.

- [New source-decision executions](../evidence/decision-results.json): **23 PASS / 0 FAIL** total (5 policy + 12 Boolean + 6 conditional cases).
- [Existing messaging suite](../evidence/week7-results.json): **73 PASS / 0 FAIL**; [full transcript](../evidence/week7-transcript.txt).
- [Existing integration suite](../evidence/week10-results.json): **42 PASS / 0 FAIL**; [full transcript](../evidence/week10-transcript.txt).
- [Artifact/diagram validation](../evidence/artifact-results.json): structural checks only, separately counted.
- [Source manifest](../evidence/source-manifest.json): unchanged originals and exact reviewed revisions.

## Reproduce

```sh
python3 -B logic_1/verify_logic.py
python3 -B logic_1/verify_logic.py --regressions
python3 -B logic_1/verify_logic.py --documents-only
```

The first uses only Python's standard library and executes selected original
expressions/fragments. The second runs existing suites using the already-installed
project interpreter in **separate child processes**. Their actual in-process routes
use synthetic identities and isolated SQLite. SQL adaptation/no-match retrieval and
a mocked dotenv loader are explicitly recorded. AI/outbound are off; socket connections
are blocked. No external connection was attempted. No tests were installed.

## Scope and limitations

Sample input rows are synthetic and assume a caller-scoped unread item. Results are extracted-branch assignments, not live HTTP response examples. The surrounding source skips non-unread rows and limits items separately. Existing messaging regressions exercise the complete route in isolated SQLite, not production.

Counts represent this execution, not copied historical passes. No real banking data,
credential values, production mutation, auth/RBAC change, screenshot or PDF is
included. [Course completion summary](../COURSE_COMPLETION_SUMMARY.md).
