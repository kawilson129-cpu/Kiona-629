# Assignment 3 · Incorporate Boolean logic

## Objective and methodology

Use actual DeRexi authorization expressions to show **AND**, **OR**, **NOT**,
equivalent decisions and exhaustive expected outcomes. Expressions were extracted
from the original AST and executed with synthetic Boolean inputs; application
authorization code was not rewritten. [Verbatim expressions](source-expressions.txt).

## 1 · Coarse Owner/Admin guard: OR and NOT

`security.require_owner_or_admin` denies when
`not (identity.is_admin or identity.is_policy_owner)`.
Let A = Admin and O = Policy Owner. Deny = **NOT (A OR O)** = **NOT A AND NOT O**;
allow = A OR O, by De Morgan's law.

| A | O | Deny | Coarse role guard passes |
|---|---|---|---|
| False | False | True | False |
| False | True | False | True |
| True | False | False | True |
| True | True | False | True |

[CSV truth table](owner-admin-truth-table.csv) · [Equivalent flowchart](rbac-guard.mmd).
The final row is an algebraic case; current `Identity.role` is a single role string,
so it is not evidence of a real dual-role user. Passing this guard does not bypass
department, ownership, independent-review or other endpoint rules.

## 2 · Feedback conversation access: AND, OR and NOT

`main.create_feedback` denies on
`not conversation or (conversation.user_id != identity.user_id and not identity.is_admin)`.
Let C = conversation exists, S = self/requester, A = Admin.

**Deny = NOT C OR (NOT S AND NOT A)**. Its complement is
**allow-to-continue = C AND (S OR A)**. Python short-circuiting avoids dereferencing
a missing conversation. These expressions cover this guard only: message existence,
legacy identity agreement, sender type and persistence remain separate checks.

| C | S | A | Deny | Continue |
|---|---|---|---|---|
| 0 | 0 | 0 | 1 | 0 |
| 0 | 0 | 1 | 1 | 0 |
| 0 | 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 1 | 0 |
| 1 | 0 | 0 | 1 | 0 |
| 1 | 0 | 1 | 0 | 1 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 0 | 1 |

When C=0, S is an unused algebraic input, not an assertion that a missing record has
an owner. [CSV](feedback-access-truth-table.csv) · [Equivalent diagram](feedback-access.mmd).
The two diagrams represent **independent endpoint guards**, not a sequence requiring
an Employee to pass the governance guard before rating their own answer.

## Results and rubric alignment

**PASS: 12/12 exhaustive source-expression cases.** Actual existing route regressions
also verify role/privacy boundaries within isolated fixtures. This does not establish
live JWT onboarding, direct-client RLS or production grants.

- [x] Real AND/OR/NOT expressions, exact source references and equivalent forms.
- [x] Complete truth tables and explicit expected outcomes.
- [x] Equivalent, source-aligned Boolean flowcharts.

[Evidence](evidence.md) · [Course summary](../COURSE_COMPLETION_SUMMARY.md).
