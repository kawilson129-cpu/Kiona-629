# Assignment 05 · Functions with Arguments and Computed Returns

## Objective and rubric

Use functions accepting arguments, including a function returning a computed value.

## Reused implementation and necessary addition

**Original Pulse relevance_score and its literal ranking constants executed unchanged.** The adapter selects the original function and all five literal weight/recency definitions needed by its body, providing only the standard-library datetime dependency. The driver builds one clearly synthetic article: Final Rule, Regulations, Federal Register and publication date 2026-01-01. It calls the same function with different date arguments and a second record whose date is deliberately invalid.

## Source references

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `relevance_score`, lines **399–415**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `STATUS_WEIGHT`, lines **371–378**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `RECENCY_POINTS`, lines **395–395**.
- [python_2/assignment_05_functions/demo.py](../../python_2/assignment_05_functions/demo.py) · `safe demonstration`, lines **1–24**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_05_functions/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 11, 12, 13, 14, 26.
Actual execution records 92.0, 84.0, 68.0, 68.0 and 6.0 for those five cases. Unit tests 11–14 check the arithmetic, argument/default behavior, invalid-date handling and unknown metadata. The values are genuinely computed return values from the original function; they are not newly fabricated performance metrics or public-feed observations.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
