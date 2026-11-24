# Evidence · Assignment 01

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `CONFIDENCE_THRESHOLD`, lines **65–65**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [python_2/assignment_01_constants/demo.py](../../python_2/assignment_01_constants/demo.py) · `safe demonstration`, lines **1–19**.

**Provenance:** Reused constant definition/value; new three-score display driver. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_01_constants/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "constant": "CONFIDENCE_THRESHOLD",
  "value": 0.22,
  "scores": [
    0.21,
    0.22,
    0.3
  ],
  "meets_numeric_gate": [
    false,
    true,
    true
  ]
}
```

[Complete stdout/stderr record](../evidence/assignment_01_constants.json).

## Behavioral tests

Relevant unit tests: **01, 02**, all PASS. The actual output records value 0.22 and meets_numeric_gate = [false, true, true]. Unit tests 01–02 verify both the inherited value and its application at the boundary. The script exits with code 0 and returns parseable JSON, rather than relying on an unexecuted code listing.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

Passing this numerical gate alone is not a successful policy answer. The production handler also checks returned records, substantive keyword evidence, publication state and persistence. The example does not test retrieval quality, calibrated probability, database connectivity or live authentication.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
