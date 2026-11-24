# Evidence · Assignment 2

**Status: PASS for the supplied documentary/logic criterion.** New code consists
of course verification only; application source is unchanged.

## Source paths, functions and line references

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [derexi-policy-pilot/backend/database.py](../../derexi-policy-pilot/backend/database.py) · `get_db`, lines **57–63**.

## Actual results

Diagram uses six symbol families. New artifact checks compare declared references, labelled branches, source/algorithm paths and Start/Stop reachability.

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

No installed Mermaid renderer or official parser was found. Structural-subset validation is not official syntax parsing, a generated image or an executed policy workflow. No PNG/SVG export or screenshot is fabricated.

Counts represent this execution, not copied historical passes. No real banking data,
credential values, production mutation, auth/RBAC change, screenshot or PDF is
included. [Course completion summary](../COURSE_COMPLETION_SUMMARY.md).
