# Assignment 04 · For Loops over Collections

## Objective and rubric

Demonstrate a for loop iterating through a collection or range.

## Reused implementation and necessary addition

**Original contains_keyword function executed unchanged; new case-table driver.** The shared adapter compiles that original reviewed function definition without importing main.py. The assignment driver supplies a short case table and iterates through it with its own for loop, calling the original function for each case. Results are stored by descriptive case name so the console output identifies which collection behavior was exercised.

## Source references

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_04_for_loops/demo.py](../../python_2/assignment_04_for_loops/demo.py) · `safe demonstration`, lines **1–24**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_04_for_loops/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 08, 09, 10, 26.
The retained output is later_match = true, singular_match = true, no_match = false and empty_collection = false. Unit tests 08–10 additionally verify a first-element match and an empty haystack. Test 26 confirms that the executed function retains the original source filename, distinguishing real source reuse from a rewritten imitation.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
