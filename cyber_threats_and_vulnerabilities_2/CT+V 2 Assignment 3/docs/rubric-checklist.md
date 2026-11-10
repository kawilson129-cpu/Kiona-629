# Exact rubric and gap analysis

Source: [official course PDF, page 1](<../../Cyber Threats and Vulnerabilities 2 Tasks.pdf>),
section **Advanced Threat Intelligence Operations**. The image-based PDF contains no
extractable text. Its [rendered page](../evidence/official-rubric-page1.png),
[visual transcription](../evidence/assignment3-rubric-transcription.txt), and
[SHA-256/source record](../evidence/rubric-source.json) are preserved. Wording below
is transcribed exactly; numbered rows are the five sentences, not invented criteria.
Official grading: **1 Complete / 0 Incomplete** for the assignment. PARTIAL below
expresses evidence coverage, not partial credit or a submitted grade.

| # | Exact requirement | Before | Current coverage | Evidence / remaining gap |
|---|---|---|---|---|
| 1 | The project must demonstrate successful deployment of an enterprise threat intelligence platform with evidence of proper configuration and operation. | MISSING deployment proof | **MISSING** verified deployment | [Local discovery](../evidence/environment-discovery.json), [blocked acceptance checks](../evidence/platform-acceptance-results.json). Prior OpenCTI plan and Windows Pulse container are not deployed OpenCTI. [Approval-dependent plan](opencti-validation-plan.md). |
| 2 | Campaign tracking and analysis systems must be implemented with demonstrated effectiveness. | PARTIAL manual tracking | **COMPLETE — controlled local scope** | [Implemented tracker](../src/intel_ops.py), [three case records](../evidence/runs/20261110T210046393348Z/campaigns.json), [mapped events](../evidence/runs/20261110T210046393348Z/mapped-events.json), [benchmark](../evidence/runs/20261110T210046393348Z/metrics.json), [32 tests](../evidence/test-results-20261110T210129262284Z.json). Real bank telemetry untested. |
| 3 | Advanced indicator management processes must be developed and documented with clear workflows. | COMPLETE documented baseline | **COMPLETE — documented and locally tested** | [Lifecycle and review workflow](implementation.md), [indicators/expiry/provenance](../evidence/runs/20261110T210046393348Z/indicators.json), tested approval/revocation/false-positive transitions and source independence. No automatic blocking. |
| 4 | Detailed threat actor profiles must be created with attribution analysis and supporting evidence. | PARTIAL one brief profile | **COMPLETE — research profiles** | [APT38 and FIN7 profiles](actor-profiles.md), [fresh source manifests](../evidence/runs/20261110T210046393348Z/collection.json), [actor/technique comparison](../evidence/runs/20261110T210046393348Z/actor-context.json). Public attribution is separated from unknown local attribution. |
| 5 | Intelligence fusion operations must be configured with demonstrated integration capabilities and operational metrics. | PARTIAL manual fusion/offline ledger | **PARTIAL** | [Working local fusion](../src/intel_ops.py) joins existing IOC reconciliation, current public ATT&CK layers, labelled telemetry and prior vulnerability findings. [Metrics](../evidence/runs/20261110T210046393348Z/metrics.json), [temporal reconciliation](../evidence/runs/20261110T210046393348Z/prioritized-findings.json). Enterprise connectors, real sightings and OpenCTI metrics unverified. |

**Overall: PARTIAL**, with 3 COMPLETE (scoped), 1 PARTIAL, 1 MISSING. Do not claim the
binary assignment criterion complete until deployment/configuration/operation and
platform fusion evidence are validated. Local collection, analysis, prioritization,
ATT&CK mapping and reporting support the five requirements above; no separate
collection/scanning/penetration-testing criteria have been invented.
