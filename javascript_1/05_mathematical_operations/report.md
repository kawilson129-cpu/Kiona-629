# Mathematical Operations

## Objective and rubric requirement

Perform mathematics using variables and store the result.

## Implementation and source references

const priorityScore = impactLevel * likelihoodLevel stores multiplication before any classification. The returned assessment carries the stored Number into the visible formula and console output. A score ranges from 1 to 25; the context override changes the priority, not the arithmetic.

- [final_project/script.js](../final_project/script.js), lines **29–31**.
- [final_project/script.js](../final_project/script.js), lines **85–85**.

## Demonstration

Calculate 3 × 5: the stored score is 15. Try 1 × 5 = 5, 2 × 3 = 6 and 5 × 5 = 25. Enable an escalation flag: the score stays the same even when the priority changes.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B02, B05, B06, B07, B09, B10.** Relevant named checks are recorded in the
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
