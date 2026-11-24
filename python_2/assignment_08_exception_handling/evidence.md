# Evidence · Assignment 08

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/database.py](../../derexi-policy-pilot/backend/database.py) · `get_db`, lines **57–63**.
- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `parse_bounded`, lines **129–146**.
- [python_2/assignment_08_exception_handling/demo.py](../../python_2/assignment_08_exception_handling/demo.py) · `safe demonstration`, lines **1–51**.

**Provenance:** New four-clause exception example; existing session/parser cleanup patterns are referenced. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_08_exception_handling/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "valid": {
    "status": "success",
    "interval_days": 30,
    "error_type": null,
    "events": [
      "try",
      "else",
      "finally"
    ],
    "resource_state": "closed"
  },
  "invalid_number": {
    "status": "error",
    "interval_days": null,
    "error_type": "ValueError",
    "events": [
      "try",
      "except",
      "finally"
    ],
    "resource_state": "closed"
  },
  "nonpositive": {
    "status": "error",
    "interval_days": null,
    "error_type": "ValueError",
    "events": [
      "try",
      "except",
      "finally"
    ],
    "resource_state": "closed"
  },
  "missing_file": {
    "status": "error",
    "interval_days": null,
    "error_type": "FileNotFoundError",
    "events": [
      "try",
      "except",
      "finally"
    ],
    "resource_state": "not_opened"
  },
  "temporary_directory_removed": true
}
```

[Complete stdout/stderr record](../evidence/assignment_08_exception_handling.json).

## Behavioral tests

Relevant unit tests: **20, 21, 22, 23, 24, 25**, all PASS. The valid file returns 30 days and resource_state = closed. Invalid text and zero produce ValueError and closed; the missing-file case produces FileNotFoundError and not_opened. Unit tests 20–25 additionally check a negative interval, a directory passed instead of a file and disposal of every temporary directory. Both required outcomes were actually executed.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

The exercise is a synthetic review-interval parser, not a production validation change or an authentication test. It catches expected operational/conversion exceptions rather than every possible failure. The finally claim applies to the executed Python paths; abrupt process termination or hardware failure is not tested or implied.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
