# Interactive Webpage

## Objective and rubric requirement

At least one HTML page links to the script and has working user interactions.

## Implementation and source references

The form submits a calculation, input changes refresh an existing assessment, and Reset clears the result and restores native form defaults. The scoring-rules disclosure is native HTML. Labels, keyboard operation, live announcements and responsive stacking support demonstration.

- [final_project/index.html](../final_project/index.html), lines **32–82**.
- [final_project/script.js](../final_project/script.js), lines **119–134**.

## Demonstration

Choose impact 3 and likelihood 5, then Calculate priority: High priority and 3 × 5 = 15 appear. Change likelihood to 1: the existing result becomes Routine review and 3 × 1 = 3. Reset restores the inputs. Keyboard: Tab to a select, type its numbered option, then focus Calculate priority and press Enter.

Launch instructions are in the [course README](../README.md).

## Actual test results and evidence

**PASS — B02, B15, B19, B20, B21, B23, B24, B28.** Relevant named checks are recorded in the
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
