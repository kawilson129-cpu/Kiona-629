# Evidence · Assignment 06

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `get_feed`, lines **748–798**.
- [derexi-policy-pilot/backend/pulse/service.py](../../derexi-policy-pilot/backend/pulse/service.py) · `score_articles`, lines **418–422**.
- [python_2/assignment_06_lists/demo.py](../../python_2/assignment_06_lists/demo.py) · `safe demonstration`, lines **1–23**.

**Provenance:** New explicit indexed-list example; source list construction/sorting/copy patterns are referenced. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_06_lists/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "original": [
    " data handling ",
    "ACCOUNT access"
  ],
  "first_before": " data handling ",
  "first_after": "Data Handling",
  "prepared": [
    "Data Handling",
    "Account Access",
    "Incident Response"
  ]
}
```

[Complete stdout/stderr record](../evidence/assignment_06_lists.json).

## Behavioral tests

Relevant unit tests: **15, 16, 17**, all PASS. The first value changes from a spaced lowercase title to Data Handling; the second becomes Account Access, and the appended third value is Incident Response. Unit tests 15–17 confirm indexed changes, append behavior, empty input, unchanged caller data and preserved duplicate entries. There is no claim that duplicate removal occurs; it is deliberately not part of this example.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

The titles are synthetic classroom display labels. Automatic title-casing would be inappropriate for arbitrary official policy text or specialized acronyms without human review, so the transformation is isolated from DeRexi’s database and content. The program illustrates list semantics rather than introducing a new normalization rule into production.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
