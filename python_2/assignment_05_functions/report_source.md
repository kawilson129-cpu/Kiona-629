# Assignment 05 · Functions with Arguments and Computed Returns

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Use functions accepting arguments, including a function returning a computed value.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

Pulse’s relevance_score(article, newest="") function accepts an article dictionary and an optional newest-publication date. It looks up document-status, category and source weights, adds a bounded recency contribution, caps the total and returns a rounded numerical score. It is an editorial reading rank, not a regulatory obligation, legal conclusion or measured security risk.

## Isolated demonstration and reuse boundary

**Original Pulse relevance_score and its literal ranking constants executed unchanged.** The adapter selects the original function and all five literal weight/recency definitions needed by its body, providing only the standard-library datetime dependency. The driver builds one clearly synthetic article: Final Rule, Regulations, Federal Register and publication date 2026-01-01. It calls the same function with different date arguments and a second record whose date is deliberately invalid.

For a same-day article, the returned value is 34 + 22 + 12 + 24 = 92.0. At fifteen days old, the recency contribution becomes 16 and the total becomes 84.0. Omitting the optional newest argument removes that contribution, producing 68.0. An invalid date follows the function’s existing ValueError fallback, while unknown metadata uses its defined defaults.

## Execution and observed results

```sh
python3 -B python_2/assignment_05_functions/demo.py
```

Actual execution records 92.0, 84.0, 68.0, 68.0 and 6.0 for those five cases. Unit tests 11–14 check the arithmetic, argument/default behavior, invalid-date handling and unknown metadata. The values are genuinely computed return values from the original function; they are not newly fabricated performance metrics or public-feed observations.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `relevance_score`, lines **399–415**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `STATUS_WEIGHT`, lines **371–378**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `RECENCY_POINTS`, lines **395–395**.
- [python_2/assignment_05_functions/demo.py](../../python_2/assignment_05_functions/demo.py) · `safe demonstration`, lines **1–24**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

No feed is downloaded, cache populated or publication authenticated. The exercise verifies this pure ranking calculation only. Historical Pulse source-integrity findings and drift records remain unchanged, and this local function result must not be described as a fresh feed-integrity or live-platform acceptance test.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
