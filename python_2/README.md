# Python 2 Final Project · DeRexi

Eight language criteria are demonstrated using existing DeRexi source first,
with only small isolated teaching additions. The course uses **Python 3** despite
its curriculum name “Python 2”; verified interpreter: **3.9.6**.

## Assignment map

| # | Assignment | Submission files | Status |
|---|---|---|---|
| 01 | [Descriptive Constants](assignment_01_constants/README.md) | [Demo](assignment_01_constants/demo.py) · [Evidence](assignment_01_constants/evidence.md) · [Report](assignment_01_constants/report_source.md) | VERIFIED |
| 02 | [Conditional Execution](assignment_02_conditionals/README.md) | [Demo](assignment_02_conditionals/demo.py) · [Evidence](assignment_02_conditionals/evidence.md) · [Report](assignment_02_conditionals/report_source.md) | VERIFIED |
| 03 | [Boolean-Controlled While Loops](assignment_03_while_loops/README.md) | [Demo](assignment_03_while_loops/demo.py) · [Evidence](assignment_03_while_loops/evidence.md) · [Report](assignment_03_while_loops/report_source.md) | VERIFIED |
| 04 | [For Loops over Collections](assignment_04_for_loops/README.md) | [Demo](assignment_04_for_loops/demo.py) · [Evidence](assignment_04_for_loops/evidence.md) · [Report](assignment_04_for_loops/report_source.md) | VERIFIED |
| 05 | [Functions with Arguments and Computed Returns](assignment_05_functions/README.md) | [Demo](assignment_05_functions/demo.py) · [Evidence](assignment_05_functions/evidence.md) · [Report](assignment_05_functions/report_source.md) | VERIFIED |
| 06 | [List Access, Modification and Element Operations](assignment_06_lists/README.md) | [Demo](assignment_06_lists/demo.py) · [Evidence](assignment_06_lists/evidence.md) · [Report](assignment_06_lists/report_source.md) | VERIFIED |
| 07 | [File Reading and Writing](assignment_07_file_operations/README.md) | [Demo](assignment_07_file_operations/demo.py) · [Evidence](assignment_07_file_operations/evidence.md) · [Report](assignment_07_file_operations/report_source.md) | VERIFIED |
| 08 | [Complete Exception Handling Lifecycle](assignment_08_exception_handling/README.md) | [Demo](assignment_08_exception_handling/demo.py) · [Evidence](assignment_08_exception_handling/evidence.md) · [Report](assignment_08_exception_handling/report_source.md) | VERIFIED |

Every assignment contains README.md, evidence.md, report_source.md and one concise
demo.py. Detailed report sources are Markdown prepared for later PDF styling;
no PDF or screenshot is fabricated or required for these supplied criteria.

## Run and verify

From the repository root:

```sh
python3 -B python_2/run_verification.py
python3 -B python_2/run_verification.py --documents-only
```

The first command runs all eight scripts and the 26 behavioral tests. The second
checks documents, source hashes, line references, links, syntax and cleanup without
repeating the functional suite. Individual commands appear in each README.
No dependency installation, backend server, account or network/API access is needed.

## Reuse strategy

[course_support.py](course_support.py) reads reviewed source and selects only
literal constants and the original contains_keyword / relevance_score function
definitions. It compiles those definitions with their required standard-library
globals. It **does not import main.py, database.py, AI or authentication modules**,
so .env loading, engine/session creation and router startup never execute.
The source adapter is an implementation aid, not a general-purpose security sandbox.
A source-hash mismatch stops reuse until the evidence is reviewed again.

The constant, for-loop and computed ranking are directly reused. A reduced
conditional demonstrates the original numerical/keyword decision. Small new
examples make the boolean loop, indexed list edits, read/write operations and
four-clause exception lifecycle explicit and safe. Other coursework was unnecessary.

## Results and evidence

**8/8 criteria VERIFIED.** Actual results: **26 behavioral tests PASS, 8 demo
executions PASS, no failures/errors/skips**. **18/18 artifact checks PASS**, recorded separately;
consult [final summary](final_summary.md), [rubric checklist](rubric_checklist.md),
[evidence index](EVIDENCE_INDEX.md) and [source manifest](evidence/source-review.json).

Assignments 07/08 use self-cleaning temporary directories beneath
`python_2/evidence/.runtime/`; the directory is Git-ignored and no exercise files
remain. JSON transcripts contain only synthetic data, relative commands and outcomes.
Existing DeRexi code, database, RBAC, credentials and working configuration remain
unchanged. No install, commit or push.

The existing LMS screenshot contains the submission heading, not the full criterion
rows. This package maps the eight detailed requirements supplied in the task.
