# JavaScript Output

## Objective and rubric requirement

Display actual results with both console.log() and DOM manipulation.

## Implementation and source references

The successful calculation updates textContent for context, priority, formula, explanation and next step, and changes the result data attribute. console.log records the same real calculation with descriptive input/output values. Invalid inputs clear stale results and show an alert; no success output is fabricated.

- [final_project/script.js](../final_project/script.js), lines **82–97**.

## Demonstration

Open DevTools Console, then Calculate priority with impact 2 and likelihood 2. The page shows 2 × 2 = 4 / Routine review. Expand DeRexi practice result: priorityScore is 4 and priorityLabel matches the page. Reset removes the displayed assessment.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B02, B03, B15, B18, B19.** Relevant named checks are recorded in the
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
