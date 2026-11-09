# Assignment 1 | Advanced Threat Analysis

**Analyst:** Kiona Wilson · November 9, 2026

## Campaign and attack pattern

The public FASTCash 2.0 advisory describes North Korean BeagleBoyz targeting banks and manipulating payment-switch responses. The switch receives ISO 8583 requests and an injected component can generate apparently valid affirmative responses, permitting fraudulent ATM withdrawals. Platform-specific implementations differ. Correlate switch process/module changes with abnormal approvals, issuer ledger mismatches and geographically dispersed ATM withdrawals. Enforce application integrity, isolate payment infrastructure and reconcile authorization with settlement. [CISA joint advisory](https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf)

DeRexi is a policy service. In the fictional scenario E01, a client-themed attachment (T1566.001) leads to PowerShell (T1059.001), Windows service persistence (T1543.003), network share discovery (T1135) and local collection (T1005). Centrally preserve 4104 and 7045 telemetry and correlate with abnormal share enumeration on the same endpoint within 30 minutes. Isolate and revoke sessions on corroboration, then compare policy version hashes and review privileged changes. The described vendor compromise and downstream risk are a scenario. [MITRE APT38](https://attack.mitre.org/groups/G0082/)

## Malware artifact analysis

E02 associates k.php with shell-script content and a 50,071-byte file. The extension mismatch is a masquerading lead. Vendor sandbox reports associate the sample with download utilities, temporary staging, Base64 command execution, cron/startup changes, password file access, and log deletion. The inferred sequence is staging → retrieval → persistence/credential activity → evasion. Sandbox verdicts disagree about family, and there is no defensible link to APT38. Inspect endpoint command lineage, newly created scheduled tasks, account changes and proxy records. Use the full hash for an exact-match hunt. Scope any IP rule by time and path because infrastructure can change hands.

| Indicator | Value | Interpretation |
|---|---|---|
| File SHA-256 | `02aac4d201886e01abd2e3d42a20edcb4e6c2381549de19df0b9166607cd3f51` | Sample identity per dossier |
| Download location | `hxxp://160[.]119[.]69[.]4/x` | Historical lead, corroborate against proxy logs |
| YARA label | `SUSP_LNX_Base64_Exec_Apr24` | Prior vendor match, broad behavior cue |

A reproducible reverse-engineering continuation requires authorized sample custody. In a disposable disconnected VM verify SHA-256, identify MIME and shebang, preserve original bytes, enumerate strings, decode static literals as data and annotate source offsets for download, persistence and deletion. Correlate with existing sandbox results. Preserve command/version, output hashes and any interpretation uncertainty. Sample execution and new artifact-level reverse engineering were not performed.

## Zero-day methodology and supply-chain assessment

Reconstruct CVE-2024-3094 from the original discovery disclosure: investigate abnormal SSH latency/CPU, compare affected and trusted builds with the same workload, trace library loading, compare release tarball versus repository and isolate build-time changes before attempting to reproduce the fault in a disposable offline environment. Retain before/after traces, file hashes and exact platform. Report privately to maintainers before publishing reproducible security details. Published findings tie compromised XZ 5.6.0/5.6.1 releases to a build-time backdoor with conditional SSH exposure. This is an analytical reconstruction of published research. [Original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4)

| DeRexi trust boundary | Method and result | Mitigation |
|---|---|---|
| Python dependencies | Compare declarations and local metadata via [assessment output](assessment.json). Runtime declarations use lower bounds and have no reviewed transitive lock in the scanned source. | Lock and hash artifacts, produce transitive SBOM, check advisories, verify CI install provenance. |
| OS and image | XZ applicability requires OS package version, build lineage and SSH linkage. Classroom port evidence supplies none of those. | Collect deployed OS/image SBOM and compare vendor advisories before rating. |
| Hosted DB and AI | Design/code imply external trust boundaries. Supplier configuration and data-retention controls were not verified. | Restrict service roles and outbound data, review provider retention, pin approved endpoints. |
| Feeds | Pulse consumes third-party content. E07 demonstrated source-label confusion historically. | Source-specific HTTPS origin enforcement, redirect validation and stale-source monitoring. |

**Exact rubric requirements satisfied:** campaign and complex attack-pattern analysis, documented methodology, technical findings, indicators and mitigations. Zero-day findings and supply-chain assessment are limited to published and local static evidence.

**Existing evidence reused:** E01, E02, E03, E07, E09, E10.

**New tests performed:** Static dependency/route inventory. See [local validation](local-validation.txt).

**Missing evidence:** Original RE outputs, controlled zero-day reproduction, deployed OS/transitive SBOM and verified advisory scan.

**Evidence completion review:** See [failure classification, fresh evidence and manual requirements](completion-matrix.md). New results are preserved under followup/. JWT foundation passed 24/24 and five schema checks passed. Installed package metadata covers 35 local distributions. These checks apply to their stated local scope. Remaining limitations and overall PARTIAL status are retained.

**Status: PARTIAL.**


