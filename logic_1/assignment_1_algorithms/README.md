# Assignment 1 · Craft algorithms

## Objective

Represent an actual DeRexi workflow as an ordered algorithm with at least six steps,
inputs, outputs, Boolean decisions and conditional branches.

## Methodology and implementation

Reused the existing policy-assistance design notes and inspected the corresponding
backend handler, schema, identity, incident and cleanup code. The
[14-step algorithm](algorithm.md) describes question → evidence gate → guidance or
clarification, with incident and error exits. It is documentation of working code,
not a second implementation or a claim of production deployment.

## Results and verification

**PASS for the supplied algorithm criterion.** Five new executions of the original
two-stage confidence gate cover equality at 0.22, below threshold, absent evidence,
generic keywords and empty results. Existing isolated workflow regressions were
rerun separately; they exercise saved clarification, feedback and authorization.
PostgreSQL trigram ranking and live provider answers remain **NOT VERIFIED** by
those fixtures. See [source and execution evidence](evidence.md).

## Rubric alignment

- [x] Actual workflow, original source mapping and 14 numbered steps.
- [x] Explicit inputs/outputs and true/false branches.
- [x] Persistence/error boundaries and tested versus unverified behavior identified.

[Course completion summary](../COURSE_COMPLETION_SUMMARY.md).
