# Evidence register

| ID | Artifact | Evidence type and scope |
|---|---|---|
| A2-01 | assets.json and assets-and-impact.md | Current local inventory with per-record provenance |
| A2-02 | program.md | Implemented local workflow and proposed enterprise governance |
| A2-03 | runs/20261109T124059033126Z/controls.log and controls.json | Current signed fixtures, expected/actual and write counts |
| A2-04 | runs/20261109T124059033126Z/results.json | Combined API, feed, dependency and static container assertions |
| A2-05 | runs/20261109T124059033126Z/findings.json and findings.md | Generated risk, priorities, metrics and actions |
| A2-06 | runs/20261109T124059033126Z/dependencies.json and dependency-consistency.log | Current installed package relationships and pip check |
| A2-07 | runs/20261109T124059033126Z/execution.json and source-hashes.json | Exact commands, return codes, timing, Python version and source hashes |
| A2-08 | inspector-validation.txt and test_inspector.py | Executed tool regression cases |
| A2-09 | runs/20261109T123409858968Z/ | Preserved incomplete sandbox attempt. ERROR, not passing control evidence |
| A2-10 | ../docker-evidence/container-inspect.json, container-checks.json and container-feeds.json | Reused November 9 Docker and publisher runtime evidence |
| A2-11 | ../control-bounded.txt, ../completion-matrix.md and ../sprint/authenticated-results.json | Historical legacy results, known test assumptions and earlier signed fixtures |
| A2-12 | ../../cyber_threats_and_vulnerabilities_1/CT+V Assignment 2/DeRexi_Vulnerability_Assessment_Report.pdf | Historical classroom Nmap report. Raw XML unavailable |
| A2-13 | ../../derexi-policy-pilot/docs/compliance/ | Prior C-01/C-02/C-03 audits, with original evidence and profiles |
| A2-14 | ../../derexi-policy-pilot/docs/database-design.md and ../../derexi-policy-pilot/docs/rbac-design-review.md | Architecture and access-control design evidence |

No screenshot was manufactured. Machine results, source hashes and exact commands are the evidence for this assessment. Existing Docker screenshots remain prior evidence in Assignment 5. Synthetic records and mock DB outputs are explicitly fixture evidence. Asset owners, SLAs and enterprise monitoring schedules are proposed organizational arrangements.

## Final closure evidence

- closure/README.md — current rubric matrix, metrics, limits and screenshot list.
- closure/assets-reconciled.json and .md — 13/13 asset reconciliation with evidence hashes.
- runs/20261109T125144008620Z/ — unchanged-suite retest, 27 PASS / 6 FAIL.
- closure/advisories/assessment.json and raw per-package JSON — 35 successful release-specific registry queries, timestamped.
- closure/advisories-triaged.json — analyst risk context and two deduplicated matches.
- closure/inspector/findings.json and .md — consolidated five-finding output.
- closure/inspector-regression-workspace.log — nine passed regression scenarios. Earlier failed temp-directory attempt retained separately.
- closure/commands.txt and cli-help.txt — exact commands and CLI usage.
- closure/workflow.json and remediation-baseline.csv — preserved progression and original tracker.
- remediation-tracking.csv — updated five-item OPEN queue.
