# Assignment 3 | Advanced Threat Intelligence Operations

## Intelligence requirements and tracking

Answer three questions: what behavior threatens banking operations, what observed artifacts can we hunt, and what evidence supports attribution? Use a source-provenance ledger to record campaign, indicator and linkage separately. The FASTCash case below represents public reporting. The Linux dropper represents a separate malware dossier.

| Case | Event window/source | Assessment | Next action |
|---|---|---|---|
| FASTCash 2.0 | 2020 public advisory, CISA joint reporting | BeagleBoyz bank-targeting/payment switch activity. High confidence in reporting-based association. | Hunt for altered switch process modules and abnormal approvals. |
| DeRexi vendor pathway | Fictional scenario E01 | ATT&CK-based threat model for policy service. No real compromise claimed. | Tabletop suspicious attachment → execution → service → share access. |
| k.php | First seen 2026-08-27 per E02 | High-confidence malicious verdict per dossier, uncertain family and actor. | Search full hash and defanged URL in separate telemetry. |

## Attribution and fusion

CISA reporting and MITRE G0082 align on the North Korean financially motivated banking threat. Treat ATT&CK as behavior context and inspect its references before counting corroboration, because it may derive from the same advisory. Compare distinctive switch manipulation, victimology and timeline with alternatives such as insider fraud or unrelated financial crime. Common PowerShell use and the Linux dossier alone carry little attribution weight. No direct k.php linkage to FASTCash was established. [CISA advisory](https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf), [MITRE G0082](https://attack.mitre.org/groups/G0082/)

## Indicator lifecycle

Ingest into a quarantine queue, validate type and value, normalize SHA-256 to lowercase and deduplicate by type/value while retaining source provenance. Keep URLs defanged in analyst exports. Record confidence, observed time, source, analyst and disposition. Assign hash review at 90 days and infrastructure review at 14 days. Expire stale IP blocking candidates unless verified. Escalate confirmed sightings only after confirming host, time, sensor and permitted business traffic. Preserve corrections and share evidence under source markings.

| Indicator | Scope | Operational pivot |
|---|---|---|
| `02aac4d201886e01abd2e3d42a20edcb4e6c2381549de19df0b9166607cd3f51` | E02 exact historical hash | EDR file sightings |
| `hxxp://160[.]119[.]69[.]4/x` | E02 historical URL | Time-bounded proxy request and process correlation |

The table manually fuses three evidence families: advisory narrative, ATT&CK context, and malware reporting. It preserves separate cases and two distinct observables. Proposed production metrics are deduplication ratio (duplicate records / received records), provenance completeness (records with source/date / accepted records), feed age, time to triage, confirmed sightings and false-positive rate. Actual enterprise rates are unavailable.

## OpenCTI configuration plan

Use an isolated OpenCTI deployment with a dedicated least-privilege connector credential per source, analyst and administrator groups, restricted ingress and persistent private data services. Add MITRE ATT&CK and an approved abuse.ch connector. Pin mutually compatible versions, follow upstream configuration, and apply marking and connector egress restrictions. Start ATT&CK first, verify actor and technique entities, then import malware intelligence and inspect type, external reference, dates and duplicate handling. Create a FASTCash report with explicit references and record a separate k.php indicator case. Verify import queues, repeated import, expiration workflow and analyst access. [OpenCTI installation](https://docs.opencti.io/latest/deployment/installation/)

**Exact rubric requirements satisfied:** documented indicator workflow and detailed actor profile with attribution reasoning and sources. Campaign tracking and manual fusion are demonstrated as an analyst workflow.

**Existing evidence reused:** E01, E02, E05, E06. Pulse is regulatory-feed infrastructure and provides a separate integration example in Assignment 5.

**New tests performed:** The [offline ledger](intel-ledger.py) reconciled four records into two indicators with provenance preserved on both. Duplicate ratio was 50% in this controlled input, and E05 derives from E02. Hash normalization, malformed-hash rejection and case separation passed. See [run results](intel-results.json). OpenCTI deployment checks remain pending.

**Missing evidence:** Deployed enterprise TIP, connector execution logs, campaign tracking effectiveness in the platform, automated fusion, and operational metrics.

**Evidence completion review:** See [failure classification, fresh evidence and manual requirements](completion-matrix.md). New results are preserved under followup/. JWT foundation passed 24/24 and five schema checks passed. Installed package metadata covers 35 local distributions. These checks apply to their stated local scope. Remaining limitations and overall PARTIAL status are retained.

**Status: PARTIAL.**


