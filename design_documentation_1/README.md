# Design Documentation 1 · DeRexi

**13 separate documentation deliverables completed**, using existing DeRexi work.
No duplicate course root, rebuilt feature or production change. Each folder has
`README.md` (purpose/rubric) and `DELIVERABLE.md` (submission content).

Start with the [self-contained Master Design Document](assignment_01_design_document/DELIVERABLE.md).
It covers all 13 criteria, including the full algorithm, diagrams, timeline, risks
and evaluation targets, and links all 12 supporting submissions.

| # | Separate assignment | Documentation status |
|---|---|---|
| 01 | [Design Document](assignment_01_design_document/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 02 | [Project Summary](assignment_02_project_summary/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 03 | [Problem Statement](assignment_03_problem_statement/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 04 | [Use Case](assignment_04_use_case/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 05 | [Goals & Objectives](assignment_05_goals_objectives/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 06 | [Key Features & Functions](assignment_06_key_features/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 07 | [Tech Stack & Tools](assignment_07_tech_stack/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 08 | [Algorithm](assignment_08_algorithm/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 09 | [Flowchart](assignment_09_flowchart/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 10 | [Timeline](assignment_10_timeline/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 11 | [Risk Mitigation](assignment_11_risk_mitigation/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 12 | [Evaluation Criteria](assignment_12_evaluation_criteria/DELIVERABLE.md) | Complete; scoped evidence limits retained |
| 13 | [Future Considerations](assignment_13_future_considerations/DELIVERABLE.md) | Complete; scoped evidence limits retained |

[Rubric checklist](RUBRIC_CHECKLIST.md) · [Evidence map](EVIDENCE_MAP.md) ·
[Original plan extraction](evidence/original-plan-extract.json) ·
[Offline validation](evidence/validation.json) · [Session notes](evidence/SESSION_NOTES.md).

**Important gaps are in runtime acceptance, not missing coursework:** production
identity/ACL/schema activation, real delivery/ticketing, representative retrieval
accuracy, performance benchmarks and human UAT remain unverified. No installed
Mermaid image renderer was found; editable `.mmd` and embedded diagrams are supplied,
with structural checks only (not official parser/image claims). No package installed.

Recheck documentation without touching the app/database:

```sh
python3 -B design_documentation_1/validate_documents.py
```

The original LMS screenshot was inspected and shows only the rubric heading; the
13 detailed criteria come from the supplied task. The screenshot stays unchanged. Historical test evidence is linked in place and never summed across overlapping
suites. No existing tests or public feeds were rerun for this course.
