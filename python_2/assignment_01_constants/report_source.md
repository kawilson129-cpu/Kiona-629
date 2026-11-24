# Assignment 01 · Descriptive Constants

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Define and apply a descriptively named constant in Python.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

DeRexi defines CONFIDENCE_THRESHOLD = 0.22 in main.py and applies it when deciding whether policy retrieval has sufficient numerical evidence. The descriptive name identifies the decision boundary, while the uppercase spelling follows Python’s constant naming convention. Python does not enforce immutability; treating the name as a constant is a deliberate coding convention.

## Isolated demonstration and reuse boundary

**Reused constant definition/value; new three-score display driver.** The demonstration obtains the original definition through the shared source adapter, binds the descriptively named constant and evaluates the synthetic scores 0.21, 0.22 and 0.30. A list comprehension applies the same comparison to each value, so the example demonstrates use as well as definition. The value is not separately hardcoded as a second configuration setting.

The comparison is inclusive: a score equal to 0.22 passes the numerical gate. A lower score fails and a higher score passes. Changing one named definition would identify the single concept being adjusted; this coursework intentionally leaves the production definition untouched. Recording the constant together with input scores makes the numerical boundary straightforward to inspect and reproduce.

## Execution and observed results

```sh
python3 -B python_2/assignment_01_constants/demo.py
```

The actual output records value 0.22 and meets_numeric_gate = [false, true, true]. Unit tests 01–02 verify both the inherited value and its application at the boundary. The script exits with code 0 and returns parseable JSON, rather than relying on an unexecuted code listing.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `CONFIDENCE_THRESHOLD`, lines **65–65**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [python_2/assignment_01_constants/demo.py](../../python_2/assignment_01_constants/demo.py) · `safe demonstration`, lines **1–19**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

Passing this numerical gate alone is not a successful policy answer. The production handler also checks returned records, substantive keyword evidence, publication state and persistence. The example does not test retrieval quality, calibrated probability, database connectivity or live authentication.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
