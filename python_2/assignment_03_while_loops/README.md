# Assignment 03 · Boolean-Controlled While Loops

## Objective and rubric

Demonstrate a while loop using a boolean condition.

## Reused implementation and necessary addition

**New bounded queue demonstration; original process-supervision loop is referenced only.** process_questions models a small in-memory list of pending policy questions. It copies the caller’s collection, initializes has_pending_questions with bool(pending_questions), and uses that explicitly Boolean variable as the while condition. Each iteration removes one pending question, strips its surrounding whitespace, records it and refreshes the Boolean flag.

## Source references

- [derexi-policy-pilot/backend/document_limits.py](../../derexi-policy-pilot/backend/document_limits.py) · `_supervise_mac`, lines **29–58**.
- [python_2/assignment_03_while_loops/demo.py](../../python_2/assignment_03_while_loops/demo.py) · `safe demonstration`, lines **1–24**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_03_while_loops/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 05, 06, 07.
The populated two-question input returns two processed strings, iterations = 2 and pending = []. The empty input returns no processed questions and iterations = 0. Unit tests 05–07 verify processing order, the initially false condition and preservation of the original input list. Both the console driver and the tests run without invoking any supervisor code.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
