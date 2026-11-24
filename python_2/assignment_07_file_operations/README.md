# Assignment 07 · File Reading and Writing

## Objective and rubric

Demonstrate both file reading and writing.

## Reused implementation and necessary addition

**New temporary UTF-8 read/write example; private retention/download paths are referenced only.** file_round_trip creates a disposable directory beneath the course’s ignored runtime area. A with block opens practice_policy.txt in text write mode with UTF-8 encoding and writes a synthetic note. A second with block opens the same file in read mode with the same encoding and recovers its contents. The exercise contains both operations explicitly instead of implying that a successful write proves a read.

## Source references

- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `retain`, lines **219–236**.
- [derexi-policy-pilot/backend/governance.py](../../derexi-policy-pilot/backend/governance.py) · `original_document`, lines **366–379**.
- [python_2/assignment_07_file_operations/demo.py](../../python_2/assignment_07_file_operations/demo.py) · `safe demonstration`, lines **1–29**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_07_file_operations/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 18, 19, 25.
The driver reads back the exact synthetic note, including its accented characters and newline. writer_closed, reader_closed and temporary_directory_removed are true. Unit tests 18–19 verify a UTF-8 round trip and a completely empty file; test 25 confirms cleanup for the file and exception demonstrations. These tests use actual temporary filesystem operations without mocks.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
