# Assignment 03 · Boolean-Controlled While Loops

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Demonstrate a while loop using a boolean condition.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

DeRexi’s macOS document-parser supervisor uses while True while observing a child process, a deadline and a memory ceiling. True is a Boolean condition, and termination is controlled by process completion or a break. Executing that entire function solely for a beginner loop demonstration would unnecessarily involve forking, operating-system probes and process termination.

## Isolated demonstration and reuse boundary

**New bounded queue demonstration; original process-supervision loop is referenced only.** process_questions models a small in-memory list of pending policy questions. It copies the caller’s collection, initializes has_pending_questions with bool(pending_questions), and uses that explicitly Boolean variable as the while condition. Each iteration removes one pending question, strips its surrounding whitespace, records it and refreshes the Boolean flag.

Progress toward termination is visible: the pending list loses exactly one item per iteration and never receives new items. Once empty, bool returns False and the loop stops. The iteration counter documents how many bodies actually ran. With an initially empty list, the condition is False before the first check, so the body is skipped safely without trying to pop a missing element.

## Execution and observed results

```sh
python3 -B python_2/assignment_03_while_loops/demo.py
```

The populated two-question input returns two processed strings, iterations = 2 and pending = []. The empty input returns no processed questions and iterations = 0. Unit tests 05–07 verify processing order, the initially false condition and preservation of the original input list. Both the console driver and the tests run without invoking any supervisor code.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/document_limits.py](../../derexi-policy-pilot/backend/document_limits.py) · `_supervise_mac`, lines **29–58**.
- [python_2/assignment_03_while_loops/demo.py](../../python_2/assignment_03_while_loops/demo.py) · `safe demonstration`, lines **1–24**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

This is a deliberately small classroom queue, not a new background worker or production service. Removing the first element of a Python list is suitable for these tiny examples, but it is not presented as an efficient large-queue design. No process, timeout or parser-resource assurance is claimed by this exercise.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
