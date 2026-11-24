# Evidence · Assignment 3

**Status: PASS for the supplied documentary/logic criterion.** New code consists
of course verification only; application source is unchanged.

## Source paths, functions and line references

- [derexi-policy-pilot/backend/security.py](../../derexi-policy-pilot/backend/security.py) · `require_owner_or_admin`, lines **223–226**.
- [derexi-policy-pilot/backend/security.py](../../derexi-policy-pilot/backend/security.py) · `Identity`, lines **46–66**.
- [derexi-policy-pilot/backend/main.py](../../derexi-policy-pilot/backend/main.py) · `create_feedback`, lines **770–807**.

The guard predicate is at security.py lines 224–225; the feedback conversation condition is at main.py lines 782–785. The CSV truth tables are expected Boolean outcomes; actual evaluations are preserved in the machine result.

## Actual results

Four role-guard rows plus eight feedback-access rows PASS, including both the original predicates and documented equivalent expressions.

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

Synthetic identity flags/conversation records exercise the exact original AST expressions without importing the app. The dual-role algebra row is not a real role assignment. Existing fixture HTTP regressions separately test actual route guards; real provider/JWKS onboarding, direct-client ACL/RLS and production grants remain NOT VERIFIED.

Counts represent this execution, not copied historical passes. No real banking data,
credential values, production mutation, auth/RBAC change, screenshot or PDF is
included. [Course completion summary](../COURSE_COMPLETION_SUMMARY.md).
