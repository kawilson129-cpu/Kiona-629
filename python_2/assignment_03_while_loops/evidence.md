# Evidence · Assignment 03

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/document_limits.py](../../derexi-policy-pilot/backend/document_limits.py) · `_supervise_mac`, lines **29–58**.
- [python_2/assignment_03_while_loops/demo.py](../../python_2/assignment_03_while_loops/demo.py) · `safe demonstration`, lines **1–24**.

**Provenance:** New bounded queue demonstration; original process-supervision loop is referenced only. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_03_while_loops/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "populated": {
    "processed": [
      "Data handling?",
      "Remote access?"
    ],
    "iterations": 2,
    "pending": []
  },
  "initially_empty": {
    "processed": [],
    "iterations": 0,
    "pending": []
  }
}
```

[Complete stdout/stderr record](../evidence/assignment_03_while_loops.json).

## Behavioral tests

Relevant unit tests: **05, 06, 07**, all PASS. The populated two-question input returns two processed strings, iterations = 2 and pending = []. The empty input returns no processed questions and iterations = 0. Unit tests 05–07 verify processing order, the initially false condition and preservation of the original input list. Both the console driver and the tests run without invoking any supervisor code.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

This is a deliberately small classroom queue, not a new background worker or production service. Removing the first element of a Python list is suitable for these tiny examples, but it is not presented as an efficient large-queue design. No process, timeout or parser-resource assurance is claimed by this exercise.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
