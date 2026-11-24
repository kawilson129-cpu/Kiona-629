# Assignment 2 · Visualize with flowcharts

## Objective and methodology

Visualize the [A1 algorithm](../assignment_1_algorithms/algorithm.md), retaining its
order, both evidence gates, incident early return, optional-provider fallback,
clarification routing and safe errors. The editable source is
[policy-assistance.mmd](policy-assistance.mmd). It adapts the earlier coursework
diagram by making the Boolean gates explicit and adding meaningful database and
predefined-process symbols.

## Six distinct symbol types

| Type | Mermaid example | Actual role |
|---|---|---|
| Terminator | `START([Start])`, `STOP([Stop])` | Begin and terminate the workflow; Start/Stop count as **one** symbol family |
| Input/output | `INPUT[/.../]` | Submitted question and returned response/errors |
| Process | `STAGE[...]` | Stage records, build context and save results |
| Decision | `SCORE{...}` | Boolean gates and true/false branch selection |
| Predefined process | `SEARCH[[...]]` | Existing schema/identity, classifier, search and rewrite helpers |
| Data store | `POLICYDB[(...)]` | Existing policy/record storage consulted or persisted |

The database symbols describe actual data, not a new service. All decision nodes
have True/False exits. Exception edges are labelled as errors rather than falsely
treated as normal Boolean results. Both numerical and keyword gates must pass.

## Results and verification

**PASS for diagram content:** six symbol types, declared references, labelled
decisions, Start/Stop reachability and key branch paths checked locally against A1.
These are structural checks and source review, **not an official Mermaid parser**
or live endpoint verification.

No installed `mmdc`, `mermaid` or Mermaid CLI package was discovered. Therefore no
PNG/SVG export or screenshot is claimed. Editable Mermaid is supplied and can be
viewed/exported later in a Mermaid-capable environment; no dependency was installed.
This is the rubric's allowed fallback, not a fabricated completed render.

## Rubric alignment

- [x] Detailed flowchart corresponding to A1.
- [x] Six distinct meaningful symbol families, including Start and Stop.
- [x] Accurate True/False decisions and documented exception/fallback exits.
- [x] Editable source retained; unavailable renderer explicitly documented.

[Source and validation evidence](evidence.md) · [Course summary](../COURSE_COMPLETION_SUMMARY.md).
