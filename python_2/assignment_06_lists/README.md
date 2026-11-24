# Assignment 06 · List Access, Modification and Element Operations

## Objective and rubric

Access and modify list elements and process individual elements using loops.

## Reused implementation and necessary addition

**New explicit indexed-list example; source list construction/sorting/copy patterns are referenced.** normalize_titles first makes a separate list so the caller’s collection remains intact. A for loop uses enumerate to obtain each index and title. The assignment normalized_titles[index] = title.strip().title() performs string operations on each individual element and writes the transformed value back into that indexed position. No official policy body is modified.

## Source references

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `get_feed`, lines **748–798**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `score_articles`, lines **418–422**.
- [python_2/assignment_06_lists/demo.py](../../python_2/assignment_06_lists/demo.py) · `safe demonstration`, lines **1–23**.

## Execute from the repository root

```sh
python3 -B python_2/assignment_06_lists/demo.py
```

Python 3; standard library only. The command prints the actual JSON result and
requires no account, application startup or dependency installation.

## Verification and submission files

**VERIFIED.** The demo exited 0; relevant unit tests: 15, 16, 17.
The first value changes from a spaced lowercase title to Data Handling; the second becomes Account Access, and the appended third value is Incident Response. Unit tests 15–17 confirm indexed changes, append behavior, empty input, unchanged caller data and preserved duplicate entries. There is no claim that duplicate removal occurs; it is deliberately not part of this example.

- [Actual evidence and output](evidence.md)
- [Detailed PDF-ready report source](report_source.md)
- [Root evidence index](../EVIDENCE_INDEX.md)
- [Course verification results](../evidence/test-results.json)

The result is an isolated language demonstration, not a claim of live application
or API/database verification. No production file or configuration is changed.
