# Logical Operators

## Objective and rubric requirement

Use &&, || or ! in a meaningful conditional expression.

## Implementation and source references

ongoingIncident || (sensitiveData && impactLevel >= 3) expresses two meaningful override routes. OR allows any ongoing event to override. AND requires both sensitive data and sufficient impact. NOT is also used by the validation guard. A single sensitive-data flag at impact 2 does not trigger the override.

- [final_project/script.js](../final_project/script.js), lines **23–25**.
- [final_project/script.js](../final_project/script.js), lines **37–37**.

## Demonstration

Test 1/1 with only ongoing enabled: Immediate attention. Test 3/1 with only sensitive data: Immediate attention. Test 2/1 with only sensitive data: Routine review. This distinguishes OR from the two-part AND condition.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B05, B11, B12, B13, B14, B17.** Relevant named checks are recorded in the
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
