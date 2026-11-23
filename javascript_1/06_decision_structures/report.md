# Decision Structures

## Objective and rubric requirement

Implement a functioning if/else statement.

## Implementation and source references

The if / else if / else chain first considers an immediate-attention override, then score ≥ 15 (High priority), score ≥ 6 (Review soon), and the final else (Routine review). Every branch sets the label, tone, reason and suggested practice response. These thresholds are classroom rules, not a production risk model.

- [final_project/script.js](../final_project/script.js), lines **37–59**.

## Demonstration

With flags off, test impact/likelihood 1/5 (Routine), 2/3 (Review soon) and 3/5 (High). Then enable the ongoing-event flag at 1/1: Immediate attention overrides the low score.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B05, B06, B07, B09, B11.** Relevant named checks are recorded in the
[static results](../evidence/static-results.json) and
[real Chrome browser results](../evidence/browser-results.json).
The browser suite passes **33/33** checks, including **100/100** calculation/flag
cases inside B05; these cases are not added again to the suite-check total.
[Reference matrix](../evidence/calculation-matrix.json).

[Desktop capture](../evidence/desktop-high-priority.png) shows 3 × 5 = 15 / High
priority. [Mobile capture](../evidence/mobile-immediate-priority.png) shows the
sensitive-data override at 3 × 1 = 3. These are actual local-page captures.
See [verification and limitations](../verification.md) for the retained initial
keyboard-test failures and subsequent passing instrumentation correction.

## Completion status

**COMPLETE.** This criterion is demonstrated by the same standalone final project;
no JavaScript is duplicated into this assignment folder.
