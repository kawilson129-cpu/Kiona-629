# Assignment 4 · Apply conditional logic

## Objective and methodology

Document the literal **if / elif / else** chain in `messaging.list_notifications`
that classifies unread clarification notifications as `triage`, `assigned` or `reply`.
It is part of DeRexi's human clarification/routing experience. The source fragment
is retained in [source-conditional.txt](source-conditional.txt); the algorithm is
[pseudocode.txt](pseudocode.txt) and its diagram is [notification-kind.mmd](notification-kind.mmd).

## Actual implementation

**Preconditions:** a row came from the caller-scoped query, and `_unread_count` is
greater than zero. Earlier loop logic skips read rows; later logic caps displayed
items at 20. The query considers at most 100 rows; the total unread count is computed
separately. This deliverable visualizes the classification fragment, not every
query, counter or authorization step in the endpoint.

1. **if** unassigned **AND** caller is Admin: kind `triage`; actor requester name.
2. **elif** assigned to this caller **AND** `int(reply_count or 0) == 0`: kind
   `assigned`; actor requester name.
3. **else**: kind `reply`; actor is the first truthy last-reply-sender, assignee or
   requester name. Python's `or` returns that value, not a Boolean label.

Order matters. An unassigned Admin row takes the first branch even with replies.
An Admin assigned their own new thread can instead take the second branch. A
negative feedback rating is a separate operation and is not automatic email or
clarification creation.

## Synthetic inputs and verified outputs

| Case | Key inputs | Actual extracted-branch output |
|---|---|---|
| N1 | Admin, unassigned, 3 replies | `triage`, Requester |
| N2 | Non-Admin, assigned to caller, null count treated as 0 | `assigned`, Requester |
| N3 | Assigned elsewhere, 2 replies, sender available | `reply`, Responder |
| N4 | Sender absent, assignee available | `reply`, Assignee |
| N5 | Sender/assignee absent | `reply`, Requester |
| N6 | Admin, assigned to self, 0 replies | `assigned`, Requester |

[sample-results.json](sample-results.json) contains actual executions of the
unchanged original branch AST and its synthetic inputs. These are **not** invented
HTTP responses or claims that a live platform generated those rows. Existing
isolated route tests separately cover notification behavior/privacy.

## Results and rubric alignment

**PASS: 6/6 branch/actor-fallback cases.** The five policy-confidence cases in A1
are separate, bringing the new course decision checks to 23 with A3's 12 cases.

- [x] Actual if, elif and else, preserving precedence and input preconditions.
- [x] Pseudocode, corresponding flowchart and traceable source fragment.
- [x] Synthetic sample inputs with actually verified classification outputs.

[Evidence](evidence.md) · [Course summary](../COURSE_COMPLETION_SUMMARY.md).
