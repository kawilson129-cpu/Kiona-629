# Evidence · Assignment 05

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `relevance_score`, lines **399–415**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `STATUS_WEIGHT`, lines **371–378**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `RECENCY_POINTS`, lines **395–395**.
- [python_2/assignment_05_functions/demo.py](../../python_2/assignment_05_functions/demo.py) · `safe demonstration`, lines **1–24**.

**Provenance:** Original Pulse relevance_score and its literal ranking constants executed unchanged. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_05_functions/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "same_day": 92.0,
  "fifteen_days_old": 84.0,
  "without_date_argument": 68.0,
  "invalid_date": 68.0,
  "unknown_metadata": 6.0
}
```

[Complete stdout/stderr record](../evidence/assignment_05_functions.json).

## Behavioral tests

Relevant unit tests: **11, 12, 13, 14, 26**, all PASS. Actual execution records 92.0, 84.0, 68.0, 68.0 and 6.0 for those five cases. Unit tests 11–14 check the arithmetic, argument/default behavior, invalid-date handling and unknown metadata. The values are genuinely computed return values from the original function; they are not newly fabricated performance metrics or public-feed observations.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

No feed is downloaded, cache populated or publication authenticated. The exercise verifies this pure ranking calculation only. Historical Pulse source-integrity findings and drift records remain unchanged, and this local function result must not be described as a fresh feed-integrity or live-platform acceptance test.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
