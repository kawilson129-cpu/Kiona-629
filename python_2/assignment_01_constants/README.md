# Assignment 01 · Descriptive Constants

## Objective and rubric

Define and apply a descriptively named constant in Python.

## Reused implementation and necessary addition

**Reused constant definition/value; new three-score display driver.** The demonstration obtains the original definition through the shared source adapter, binds the descriptively named constant and evaluates the synthetic scores 0.21, 0.22 and 0.30. A list comprehension applies the same comparison to each value, so the example demonstrates use as well as definition. The value is not separately hardcoded as a second configuration setting.

## Source references

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `CONFIDENCE_THRESHOLD`, lines **65–65**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [python_2/assignment_01_constants/demo.py](../../python_2/assignment_01_constants/demo.py) · `safe demonstration`, lines **1–19**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_01_constants/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 01, 02.
The actual output records value 0.22 and meets_numeric_gate = [false, true, true]. Unit tests 01–02 verify both the inherited value and its application at the boundary. The script exits with code 0 and returns parseable JSON, rather than relying on an unexecuted code listing.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
