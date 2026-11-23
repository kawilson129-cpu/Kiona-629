# Descriptive Variables

## Objective and rubric requirement

Use descriptive variable names longer than one character.

## Implementation and source references

policyArea, impactLevel, likelihoodLevel, sensitiveData, ongoingIncident and priorityScore describe domain values. priorityForm, resultContainer and calculationOutput describe DOM references. Every declared application variable and function parameter has more than one character.

- [final_project/script.js](../final_project/script.js), lines **4–19**.
- [final_project/script.js](../final_project/script.js), lines **66–70**.

## Demonstration

Open script.js and locate the names above. Calculate a result and expand the DeRexi practice result console object to see the descriptive data keys.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — S12, B03, B04.** Relevant named checks are recorded in the
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
