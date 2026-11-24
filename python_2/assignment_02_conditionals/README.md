# Assignment 02 · Conditional Execution

## Objective and rubric

Use if-else logic to control execution based on a condition.

## Reused implementation and necessary addition

**New reduced if/else wrapper using the original threshold and keyword function.** choose_response accepts a synthetic score, policy text and a keyword list. It combines the original numerical threshold with a nonempty keyword check and the original contains_keyword function. A functioning if returns “Provide source-backed guidance”; the explicit else returns “Request clarification”. The wrapper is new teaching code, not an extracted copy of the full endpoint.

## Source references

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_02_conditionals/demo.py](../../python_2/assignment_02_conditionals/demo.py) · `safe demonstration`, lines **1–30**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_02_conditionals/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 03, 04.
The first scenario produces the guidance label; the other three produce the clarification label. Unit tests 03–04 also check a value just below the threshold, absent evidence and an empty collection. These results verify the isolated execution decision using actual Python calls and the unchanged source helper.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
