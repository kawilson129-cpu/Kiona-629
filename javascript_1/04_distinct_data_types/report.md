# Distinct Data Types

## Objective and rubric requirement

At least two variables have different types, including an integer Number.

## Implementation and source references

policyArea is a String. Number(select.value) converts the input string to an integer Number such as impactLevel = 2. sensitiveData and ongoingIncident are Booleans from checkbox.checked. Number.isInteger and range/type guards reject fractions, strings, non-finite numbers and invalid flags in the calculation function.

- [final_project/script.js](../final_project/script.js), lines **66–70**.
- [final_project/script.js](../final_project/script.js), lines **23–26**.

## Demonstration

Calculate the default scenario. Inspect the console object: policyArea is quoted text, impactLevel is numeric 2, and sensitiveData is false. In DevTools, Number.isInteger(2) returns true. B04 tests the types of the real logged values.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B04, B17.** Relevant named checks are recorded in the
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
