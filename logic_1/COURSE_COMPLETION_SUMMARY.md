# Logic 1 · Course completion summary

The four supplied grading criteria are organized as **four separate deliverables
for one Logic 1 final project**. Targeted inspection found an existing
`logic_1/stay_data_stay.py` submission and no conflicting course-specific instruction
file. That original submission is preserved. DeRexi supplies the actual workflows.

## Four assignments and rubric coverage

| Assignment | Deliverables | Coverage / verification |
|---|---|---|
| [A1 · Craft algorithms](assignment_1_algorithms/README.md) | [14-step algorithm](assignment_1_algorithms/algorithm.md), [source/test evidence](assignment_1_algorithms/evidence.md) | **PASS**: inputs, outputs, Boolean decisions, conditional/error/cleanup branches and source mapping |
| [A2 · Flowcharts](assignment_2_flowcharts/README.md) | [Detailed Mermaid](assignment_2_flowcharts/policy-assistance.mmd), [evidence](assignment_2_flowcharts/evidence.md) | **PASS**: matching algorithm, Start/Stop and six distinct symbol families; renderer limitation documented |
| [A3 · Boolean logic](assignment_3_boolean_logic/README.md) | Two truth-table CSVs, exact expressions, [role guard](assignment_3_boolean_logic/rbac-guard.mmd), [feedback guard](assignment_3_boolean_logic/feedback-access.mmd), [evidence](assignment_3_boolean_logic/evidence.md) | **PASS**: actual AND/OR/NOT, equivalent forms and 12 exhaustive source-expression cases |
| [A4 · Conditional logic](assignment_4_conditional_logic/README.md) | [Pseudocode](assignment_4_conditional_logic/pseudocode.txt), [Mermaid](assignment_4_conditional_logic/notification-kind.mmd), verbatim source, [six actual sample results](assignment_4_conditional_logic/sample-results.json), [evidence](assignment_4_conditional_logic/evidence.md) | **PASS**: actual notification if/elif/else, accurate order/preconditions and expected outputs |

**Rubric coverage: 4/4 supplied criteria supported.** This describes verified course
artifacts and isolated behavior, not an instructor grade or production acceptance.
Start/Stop are one terminator family; A2 also uses input/output, process, decision,
predefined process and data-store symbols. Symbol counts are not inflated by
counting Start and Stop separately.

## Evidence and actual verification

| Execution | Recorded result | Scope |
|---|---|---|
| [New decision cases](evidence/decision-results.json) | **23 PASS / 0 FAIL** | Original AST decisions with synthetic inputs; no app startup |
| [Existing Week 7 messaging suite](evidence/week7-results.json) | **73 PASS / 0 FAIL** | Actual in-process routes and isolated SQLite; existing fixture adapters |
| [Existing Week 10 integration suite](evidence/week10-results.json) | **42 PASS / 0 FAIL** | Assistant clarification/feedback/incident handoffs and offline source validation |
| [Artifact checks](evidence/artifact-results.json) | **53 PASS / 0 FAIL** | File completeness, source preservation, truth-table/diagram references and branch structure; 96 local links resolve |

[Regression summary](evidence/regression-summary.json) combines the two actual
reruns (115 assertions). Do not add historical overlapping totals. Exact commands,
run timestamps, mocking limitations and source locations are retained in each
assignment's evidence. [Source map](evidence/source-map.json) and
[protected-source hashes](evidence/source-manifest.json) identify original revisions.

## Reuse and implementation boundaries

A1 adapts the existing Design Documentation policy algorithm; A2 extends that
existing diagram for Logic's six-symbol requirement. A3 executes the existing
role/feedback predicates and verifies their equivalent decisions. A4 executes the
actual notification branch, without inventing an incident-escalation elif or an
automatic negative-feedback routing feature.

The regression wrapper imports the original tests in an isolated child with the
existing project virtual environment. No dependency is installed. The fixture
creates synthetic in-memory SQLite rows, forbids live PostgreSQL connections and
stubs trigram search to no matches. The dotenv loader is mocked so working .env
files are not read; AI/outbound are off and socket calls are forbidden. Actual route
code is unchanged. No external network attempt was observed.

## Remaining gaps / manual work

No mandatory supplied rubric gap remains. There is no installed Mermaid renderer
or official parser; therefore editable `.mmd` files are supplied, with structural
validation and source review. A Mermaid-capable environment can export them later
if an instructor additionally requests images. No rendered diagram or screenshot is
claimed. Full engine parsing is **NOT VERIFIED**.

Live PostgreSQL ranking, production JWT/provider onboarding, direct-client RLS,
SMTP delivery and human UAT are **NOT VERIFIED** by these exercises. No credentials,
real banking data, live writes or production claims are needed for the logic criteria.

## Reproduce and session record

```sh
python3 -B logic_1/verify_logic.py
python3 -B logic_1/verify_logic.py --regressions
python3 -B logic_1/verify_logic.py --documents-only
```

Only logic_1 is edited; original code, configuration, auth/RBAC, legacy coursework
and root MEMORY.md remain unchanged. This course-local summary records the session
without an unrelated root-memory edit. No final designer PDF, commit or push.
