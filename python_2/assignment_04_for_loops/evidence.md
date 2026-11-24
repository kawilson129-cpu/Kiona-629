# Evidence · Assignment 04

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_04_for_loops/demo.py](../../python_2/assignment_04_for_loops/demo.py) · `safe demonstration`, lines **1–24**.

**Provenance:** Original contains_keyword function executed unchanged; new case-table driver. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_04_for_loops/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "later_match": true,
  "singular_match": true,
  "no_match": false,
  "empty_collection": false
}
```

[Complete stdout/stderr record](../evidence/assignment_04_for_loops.json).

## Behavioral tests

Relevant unit tests: **08, 09, 10, 26**, all PASS. The retained output is later_match = true, singular_match = true, no_match = false and empty_collection = false. Unit tests 08–10 additionally verify a first-element match and an empty haystack. Test 26 confirms that the executed function retains the original source filename, distinguishing real source reuse from a rewritten imitation.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

The helper expects prepared text and keyword inputs from its caller. It uses substring checks and a simple singular fallback; these examples do not establish linguistic accuracy, exact word-boundary matching or the correctness of every policy retrieval. Only the selected original function and synthetic cases are executed.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
