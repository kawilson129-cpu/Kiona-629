# Evidence · Assignment 1

**Status: PASS for the supplied documentary/logic criterion.** New code consists
of course verification only; application source is unchanged.

## Source paths, functions and line references

- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `ask`, lines **423–575**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `contains_keyword`, lines **210–217**.
- [derexi-policy-pilot/backend/schemas.py](../../derexi-policy-pilot/backend/schemas.py) · `AskRequest`, lines **49–56**.
- [derexi-policy-pilot/backend/security.py](../../derexi-policy-pilot/backend/security.py) · `get_identity`, lines **142–158**.
- [derexi-policy-pilot/backend/incident_assistance.py](../../derexi-policy-pilot/backend/incident_assistance.py) · `classify`, lines **65–88**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `add_security_headers`, lines **106–133**.
- [derexi-policy-pilot/backend/database.py](../../derexi-policy-pilot/backend/database.py) · `get_db`, lines **57–63**.

Earlier materials reused: [algorithm notes](../../design_documentation_1/assignment_08_algorithm/DELIVERABLE.md) and [earlier diagram](../../design_documentation_1/assignment_09_flowchart/policy-assistance.mmd). Their original hashes remain unchanged; the new Logic diagram adds the required symbols and explicit gates.

## Actual results

Five policy gate cases P1–P5 PASS; existing Week 10 I01–I10 exercise the isolated Assistant/clarification handoff.

- [New source-decision executions](../evidence/decision-results.json): **23 PASS / 0 FAIL** total (5 policy + 12 Boolean + 6 conditional cases).
- [Existing messaging suite](../evidence/week7-results.json): **73 PASS / 0 FAIL**; [full transcript](../evidence/week7-transcript.txt).
- [Existing integration suite](../evidence/week10-results.json): **42 PASS / 0 FAIL**; [full transcript](../evidence/week10-transcript.txt).
- [Artifact/diagram validation](../evidence/artifact-results.json): structural checks only, separately counted.
- [Source manifest](../evidence/source-manifest.json): unchanged originals and exact reviewed revisions.

## Reproduce

```sh
python3 -B logic_1/verify_logic.py
python3 -B logic_1/verify_logic.py --regressions
python3 -B logic_1/verify_logic.py --documents-only
```

The first uses only Python's standard library and executes selected original
expressions/fragments. The second runs existing suites using the already-installed
project interpreter in **separate child processes**. Their actual in-process routes
use synthetic identities and isolated SQLite. SQL adaptation/no-match retrieval and
a mocked dotenv loader are explicitly recorded. AI/outbound are off; socket connections
are blocked. No external connection was attempted. No tests were installed.

## Scope and limitations

The five cases execute original confidence assignments with synthetic query rows; they do not query PostgreSQL. The existing fixture adapts PostgreSQL syntax to SQLite and deliberately returns no trigram matches. Native ranking, live provider answers and real identity onboarding are NOT VERIFIED.

Counts represent this execution, not copied historical passes. No real banking data,
credential values, production mutation, auth/RBAC change, screenshot or PDF is
included. [Course completion summary](../COURSE_COMPLETION_SUMMARY.md).
