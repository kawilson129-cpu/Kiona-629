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
| 1 | The project must demonstrate successful deployment of an enterprise threat intelligence platform with evidence of proper configuration and operation. | MISSING deployment proof | **BLOCKED — capacity** | Docker/Compose verified operational; 7.748 GiB usable Docker RAM cannot accommodate published sizing. [Capacity review](opencti-capacity-review.md), [preflight](../evidence/opencti-preflight-20261116/preflight.json), [five blocked checks](../evidence/platform-acceptance-results.json). No runtime deployment or UI/API evidence. |
| 2 | Campaign tracking and analysis systems must be implemented with demonstrated effectiveness. | PARTIAL manual tracking | **VERIFIED — controlled local scope** | [Implemented tracker](../src/intel_ops.py), [three case records](../evidence/runs/20261110T210046393348Z/campaigns.json), [mapped events](../evidence/runs/20261110T210046393348Z/mapped-events.json), [benchmark](../evidence/runs/20261110T210046393348Z/metrics.json), [32 tests](../evidence/test-results-20261110T210129262284Z.json). Real bank telemetry untested. |
| 3 | Advanced indicator management processes must be developed and documented with clear workflows. | COMPLETE documented baseline | **VERIFIED — documented and locally tested** | [Lifecycle and review workflow](implementation.md), [indicators/expiry/provenance](../evidence/runs/20261110T210046393348Z/indicators.json), tested approval/revocation/false-positive transitions and source independence. No automatic blocking. |
| 4 | Detailed threat actor profiles must be created with attribution analysis and supporting evidence. | PARTIAL one brief profile | **VERIFIED — research profiles** | [APT38 and FIN7 profiles](actor-profiles.md), [fresh source manifests](../evidence/runs/20261110T210046393348Z/collection.json), [actor/technique comparison](../evidence/runs/20261110T210046393348Z/actor-context.json). Public attribution is separated from unknown local attribution. |
| 5 | Intelligence fusion operations must be configured with demonstrated integration capabilities and operational metrics. | PARTIAL manual fusion/offline ledger | **PARTIAL** | [Working local fusion](../src/intel_ops.py) joins existing IOC reconciliation, current public ATT&CK layers, labelled telemetry and prior vulnerability findings. [Metrics](../evidence/runs/20261110T210046393348Z/metrics.json), [temporal reconciliation](../evidence/runs/20261110T210046393348Z/prioritized-findings.json). Enterprise connectors, real sightings and OpenCTI metrics unverified. |

**Current review: November 16, 2026. Overall: PARTIAL**, with 3 VERIFIED
(scoped), 1 PARTIAL, 1 BLOCKED. Current local rerun: **32 PASS / 0 FAIL**;
platform acceptance: **0 PASS / 0 FAIL / 5 BLOCKED**.
[Latest test results](../evidence/test-results-20261116T185123544043Z.json).
The previously verified public collection remains 3/3 (November 10); it was not
repeated. The prior artifact audit remains 7 PASS / 1 FAIL for documented Pulse
integrity drift; [original record](../evidence/concurrent-source-drift.json) preserved. Do not claim the
binary assignment criterion complete until deployment/configuration/operation and
platform fusion evidence are validated. Local collection, analysis, prioritization,
ATT&CK mapping and reporting support the five requirements above; no separate
collection/scanning/penetration-testing criteria have been invented.
