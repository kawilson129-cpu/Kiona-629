# Evidence · Assignment 07

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `retain`, lines **219–236**.
- [derexi-policy-pilot/backend/governance.py](../../derexi-policy-pilot/backend/governance.py) · `original_document`, lines **366–379**.
- [python_2/assignment_07_file_operations/demo.py](../../python_2/assignment_07_file_operations/demo.py) · `safe demonstration`, lines **1–29**.

**Provenance:** New temporary UTF-8 read/write example; private retention/download paths are referenced only. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_07_file_operations/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "written_characters": 39,
  "read_text": "Practice policy: protéger les données.\n",
  "writer_closed": true,
  "reader_closed": true,
  "temporary_directory_removed": true
}
```

[Complete stdout/stderr record](../evidence/assignment_07_file_operations.json).

## Behavioral tests

Relevant unit tests: **18, 19, 25**, all PASS. The driver reads back the exact synthetic note, including its accented characters and newline. writer_closed, reader_closed and temporary_directory_removed are true. Unit tests 18–19 verify a UTF-8 round trip and a completely empty file; test 25 confirms cleanup for the file and exception demonstrations. These tests use actual temporary filesystem operations without mocks.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

The example does not test production retention permissions, encryption, streaming downloads, backup recovery or live authentication. No policy record, configuration file or existing application document is opened or changed. Disposable exercise files are removed; only the sanitized execution transcript remains as submission evidence.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
