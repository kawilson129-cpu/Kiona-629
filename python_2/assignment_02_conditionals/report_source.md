# Assignment 02 · Conditional Execution

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Use if-else logic to control execution based on a condition.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

The Policy Assistant handler builds a confidence decision from the retrieval score and substantive keyword evidence. Its higher-confidence path prepares guidance and citations; insufficient evidence leads to an uncertainty answer and owner or triage routing. The application also contains an explicit if/else around optional AI output and deterministic guidance. These are business decisions, not merely comparisons whose results are ignored.

## Isolated demonstration and reuse boundary

**New reduced if/else wrapper using the original threshold and keyword function.** choose_response accepts a synthetic score, policy text and a keyword list. It combines the original numerical threshold with a nonempty keyword check and the original contains_keyword function. A functioning if returns “Provide source-backed guidance”; the explicit else returns “Request clarification”. The wrapper is new teaching code, not an extracted copy of the full endpoint.

The first scenario reaches the if branch at exactly 0.22 with matching text. The second keeps the text match but lowers the score to 0.21. The third supplies a high score with unrelated text. The fourth supplies no keywords. Those distinct inputs show why score alone is insufficient and establish that the alternative path is reachable rather than decorative.

## Execution and observed results

```sh
python3 -B python_2/assignment_02_conditionals/demo.py
```

The first scenario produces the guidance label; the other three produce the clarification label. Unit tests 03–04 also check a value just below the threshold, absent evidence and an empty collection. These results verify the isolated execution decision using actual Python calls and the unchanged source helper.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_02_conditionals/demo.py](../../python_2/assignment_02_conditionals/demo.py) · `safe demonstration`, lines **1–30**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

The labels describe a reduced decision exercise. No answer is generated, conversation stored or clarification assigned. Inputs are synthetic, and the original helper performs substring matching with a simple trailing-s fallback, not a full language-understanding or authorization check.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
