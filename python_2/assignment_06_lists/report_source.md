# Assignment 06 · List Access, Modification and Element Operations

**DeRexi: Policy Pilot · Python 2 Final Project**  
**Rubric:** Access and modify list elements and process individual elements using loops.  
**Verification:** VERIFIED — actual offline Python 3.9.6 execution.

## Purpose and existing DeRexi implementation

Pulse builds combined and unique article lists, extends them from each source, appends accepted entries and sorts the resulting collection. score_articles creates scored copies rather than mutating cached source records. Those are useful existing list operations, but they do not provide as clear a beginner example of reading and assigning a particular list index.

## Isolated demonstration and reuse boundary

**New explicit indexed-list example; source list construction/sorting/copy patterns are referenced.** normalize_titles first makes a separate list so the caller’s collection remains intact. A for loop uses enumerate to obtain each index and title. The assignment normalized_titles[index] = title.strip().title() performs string operations on each individual element and writes the transformed value back into that indexed position. No official policy body is modified.

The fixed demonstration reads original_titles[0] before processing, then reads prepared_titles[0] afterward. It also appends the fictional display title Incident Response to demonstrate collection growth. The original list is included in the result, making the copy boundary visible. The normalization function itself safely handles an empty collection because its for loop simply runs zero times.

## Execution and observed results

```sh
python3 -B python_2/assignment_06_lists/demo.py
```

The first value changes from a spaced lowercase title to Data Handling; the second becomes Account Access, and the appended third value is Incident Response. Unit tests 15–17 confirm indexed changes, append behavior, empty input, unchanged caller data and preserved duplicate entries. There is no claim that duplicate removal occurs; it is deliberately not part of this example.

The full test run recorded 26 successful behavioral tests and eight successful
standalone executions, without failures, errors or skipped tests. These totals are
not added to historical DeRexi test counts. The [assignment evidence](evidence.md)
contains the actual captured output and relevant test numbers; the
[complete transcript](../evidence/unittest-transcript.txt) preserves the run.

## Source traceability

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `get_feed`, lines **748–798**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `score_articles`, lines **418–422**.
- [python_2/assignment_06_lists/demo.py](../../python_2/assignment_06_lists/demo.py) · `safe demonstration`, lines **1–23**.

Production references describe inspected code. Only the adapter’s selected pure
functions/constants are executed; database, provider, authentication and storage
startup paths remain inactive. New teaching code is explicitly identified above.

## Evaluation and limitations

The titles are synthetic classroom display labels. Automatic title-casing would be inappropriate for arbitrary official policy text or specialized acronyms without human review, so the transformation is isolated from DeRexi’s database and content. The program illustrates list semantics rather than introducing a new normalization rule into production.

**Rubric conclusion:** the supplied criterion is supported by executable code,
observed outputs and named tests. This conclusion covers the Python concept and
its documented edge cases, not untested production behavior.
