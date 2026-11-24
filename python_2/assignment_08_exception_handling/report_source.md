# Assignment 08 · Complete Exception Handling Lifecycle

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Demonstrate try, except, else and finally on successful and exception-producing paths.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

DeRexi’s get_db dependency uses try/finally to close a request session. Its bounded document parser catches a timeout and releases its semaphore in finally. These examples show real resource lifecycle concerns, but the selected blocks do not combine all four rubric clauses with an easy-to-reproduce success path. A small isolated file conversion makes each clause visible without opening a database connection.

## Isolated demonstration and reuse boundary

**New four-clause exception example; existing session/parser cleanup patterns are referenced.** read_review_interval initializes its handle and result state, then enters try to open a synthetic text file, read it and convert its content to an integer. A nonpositive result deliberately raises ValueError. except handles expected OSError or ValueError outcomes, records only the exception type and clears the unusable value. else sets success only when the try suite completes without an exception.

finally explicitly closes any opened reader and appends its lifecycle event before the function returns. A missing file leaves no handle to close, but finally still runs. The returned event sequence is therefore observable evidence: success yields try → else → finally; a handled conversion or filesystem error yields try → except → finally. No return inside finally suppresses an earlier result or exception.

## Execution and observed results

```sh
python3 -B python_2/assignment_08_exception_handling/demo.py
```

The valid file returns 30 days and resource_state = closed. Invalid text and zero produce ValueError and closed; the missing-file case produces FileNotFoundError and not_opened. Unit tests 20–25 additionally check a negative interval, a directory passed instead of a file and disposal of every temporary directory. Both required outcomes were actually executed.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/database.py](../../derexi-policy-pilot/backend/database.py) · `get_db`, lines **57–63**.
- [derexi-policy-pilot/backend/document_intake.py](../../derexi-policy-pilot/backend/document_intake.py) · `parse_bounded`, lines **129–146**.
- [python_2/assignment_08_exception_handling/demo.py](../../python_2/assignment_08_exception_handling/demo.py) · `safe demonstration`, lines **1–51**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

The exercise is a synthetic review-interval parser, not a production validation change or an authentication test. It catches expected operational/conversion exceptions rather than every possible failure. The finally claim applies to the executed Python paths; abrupt process termination or hardware failure is not tested or implied.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
