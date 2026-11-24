# Assignment 04 · For Loops over Collections

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Demonstrate a for loop iterating through a collection or range.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

contains_keyword is a compact, strong DeRexi example because its explicit for keyword in keywords loop examines a real collection used by policy assistance. It returns True when a keyword is found, also tries a simple singular form for a trailing-s keyword, and returns False after exhausting the collection. No database, provider or HTTP dependency is needed by this function body.

## Isolated demonstration and reuse boundary

**Original contains_keyword function executed unchanged; new case-table driver.** The shared adapter compiles that original reviewed function definition without importing main.py. The assignment driver supplies a short case table and iterates through it with its own for loop, calling the original function for each case. Results are stored by descriptive case name so the console output identifies which collection behavior was exercised.

The later-match input puts an absent keyword before a matching keyword, proving that the loop can proceed beyond its first element. The singular case supplies safeguards against text containing safeguard. The no-match case exhausts its collection, while the empty-list case never enters the body and reaches the final False return. This demonstrates both iteration and the significance of early return.

## Execution and observed results

```sh
python3 -B python_2/assignment_04_for_loops/demo.py
```

The retained output is later_match = true, singular_match = true, no_match = false and empty_collection = false. Unit tests 08–10 additionally verify a first-element match and an empty haystack. Test 26 confirms that the executed function retains the original source filename, distinguishing real source reuse from a rewritten imitation.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_04_for_loops/demo.py](../../python_2/assignment_04_for_loops/demo.py) · `safe demonstration`, lines **1–24**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

The helper expects prepared text and keyword inputs from its caller. It uses substring checks and a simple singular fallback; these examples do not establish linguistic accuracy, exact word-boundary matching or the correctness of every policy retrieval. Only the selected original function and synthetic cases are executed.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
