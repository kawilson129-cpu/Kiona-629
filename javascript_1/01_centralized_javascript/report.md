# Centralized JavaScript

## Objective and rubric requirement

Exactly one external JavaScript file contains all application JavaScript.

## Implementation and source references

The HTML loads only script.js with defer. There are no inline script bodies, inline event handlers, imports, framework scripts or duplicate JavaScript assignment files. The Python verification harness is test instrumentation, not page-loaded application code.

- [final_project/index.html](../final_project/index.html), lines **10–10**.
- [final_project/script.js](../final_project/script.js), lines **1–134**.

## Demonstration

View page source: confirm the single script tag. Inspect the Network panel: script.js is the only JavaScript resource.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — S01, S02, S03, B25.** Relevant named checks are recorded in the
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
