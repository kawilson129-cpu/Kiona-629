# Assignment 08 · Complete Exception Handling Lifecycle

## Objective and rubric

Demonstrate try, except, else and finally on successful and exception-producing paths.

## Reused implementation and necessary addition

**New four-clause exception example; existing session/parser cleanup patterns are referenced.** read_review_interval initializes its handle and result state, then enters try to open a synthetic text file, read it and convert its content to an integer. A nonpositive result deliberately raises ValueError. except handles expected OSError or ValueError outcomes, records only the exception type and clears the unusable value. else sets success only when the try suite completes without an exception.

## Source references

- [derexi-policy-pilot/backend/database.py](../../derexi-policy-pilot/backend/database.py) · `get_db`, lines **57–63**.
- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `parse_bounded`, lines **129–146**.
- [python_2/assignment_08_exception_handling/demo.py](../../python_2/assignment_08_exception_handling/demo.py) · `safe demonstration`, lines **1–51**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_08_exception_handling/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 20, 21, 22, 23, 24, 25.
The valid file returns 30 days and resource_state = closed. Invalid text and zero produce ValueError and closed; the missing-file case produces FileNotFoundError and not_opened. Unit tests 20–25 additionally check a negative interval, a directory passed instead of a file and disposal of every temporary directory. Both required outcomes were actually executed.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
