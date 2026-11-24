# Evidence · Assignment 02

**Status: VERIFIED** · Python 3.9.6 · execution recorded 2026-11-24T17:12:27.196167+00:00.

## Original source and executable demonstration

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [python_2/assignment_02_conditionals/demo.py](../../python_2/assignment_02_conditionals/demo.py) · `safe demonstration`, lines **1–30**.

**Provenance:** New reduced if/else wrapper using the original threshold and keyword function. The source adapter compiles only reviewed definitions,
not app/module startup; [adapter and audit](../course_support.py),
[source hashes](../evidence/source-review.json).

## Executed command and actual output

```sh
python3 -B python_2/assignment_02_conditionals/demo.py
```

**Exit code: 0** · stderr: empty.
The following is the captured payload, not proposed/sample output:

```json
{
  "matching_at_threshold": "Provide source-backed guidance",
  "below_threshold": "Request clarification",
  "high_score_without_evidence": "Request clarification",
  "empty_keywords": "Request clarification"
}
```

[Complete stdout/stderr record](../evidence/assignment_02_conditionals.json).

## Behavioral tests

Relevant unit tests: **03, 04**, all PASS. The first scenario produces the guidance label; the other three produce the clarification label. Unit tests 03–04 also check a value just below the threshold, absent evidence and an empty collection. These results verify the isolated execution decision using actual Python calls and the unchanged source helper.

```sh
python3 -B python_2/run_verification.py
```

The complete suite recorded **26 tests run, 0 failures, 0 errors, 0 skips**, plus
**8/8 successful standalone demo executions**. These are separate counts.
[Unit transcript](../evidence/unittest-transcript.txt) ·
[Machine results](../evidence/test-results.json).

## Limits

The labels describe a reduced decision exercise. No answer is generated, conversation stored or clarification assigned. Inputs are synthetic, and the original helper performs substring matching with a simple trailing-s fallback, not a full language-understanding or authorization check.

App integration, live database/authentication/provider and native parser-supervision
execution: **NOT TESTED in this coursework**. No such test is needed to establish
this language criterion. No screenshots, provider outputs or live metrics invented.
