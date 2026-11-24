# Assignment 07 · File Reading and Writing

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Demonstrate both file reading and writing.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

DeRexi’s retain function writes an approved original document using private storage, exclusive creation and restrictive permissions. The governed original_document endpoint checks access and metadata before returning a FileResponse. Those paths depend on configured private storage, authenticated actors and feature state, so invoking them for a beginner file exercise would create unnecessary operational coupling.

## Isolated demonstration and reuse boundary

**New temporary UTF-8 read/write example; private retention/download paths are referenced only.** file_round_trip creates a disposable directory beneath the course’s ignored runtime area. A with block opens practice_policy.txt in text write mode with UTF-8 encoding and writes a synthetic note. A second with block opens the same file in read mode with the same encoding and recovers its contents. The exercise contains both operations explicitly instead of implying that a successful write proves a read.

writer.write returns the number of characters written, which is recorded separately from recovered_text. This matters for accented or non-ASCII text because character count is not necessarily encoded byte count. Both context managers close their handles, and TemporaryDirectory removes the exercise directory after the result has been assembled. The returned cleanup flag is measured with an actual existence check.

## Execution and observed results

```sh
python3 -B python_2/assignment_07_file_operations/demo.py
```

The driver reads back the exact synthetic note, including its accented characters and newline. writer_closed, reader_closed and temporary_directory_removed are true. Unit tests 18–19 verify a UTF-8 round trip and a completely empty file; test 25 confirms cleanup for the file and exception demonstrations. These tests use actual temporary filesystem operations without mocks.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `retain`, lines **219–236**.
- [derexi-policy-pilot/backend/governance.py](../../derexi-policy-pilot/backend/governance.py) · `original_document`, lines **366–379**.
- [python_2/assignment_07_file_operations/demo.py](../../python_2/assignment_07_file_operations/demo.py) · `safe demonstration`, lines **1–29**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

The example does not test production retention permissions, encryption, streaming downloads, backup recovery or live authentication. No policy record, configuration file or existing application document is opened or changed. Disposable exercise files are removed; only the sanitized execution transcript remains as submission evidence.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
