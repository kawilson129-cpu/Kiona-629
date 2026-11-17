# Official rubric and evidence checklist

Reviewed November 17, 2026. Authority: [official course tasks PDF](../../Cyber%20Threats%20and%20Vulnerabilities%202%20Tasks.pdf), page 1, **Advanced Threat Analysis** row. The image-based PDF has no useful text layer. Its existing [page rendering](../../CT+V%202%20Assignment%203/evidence/official-rubric-page1.png) was visually read; [source metadata](../../CT+V%202%20Assignment%203/evidence/rubric-source.json) supplies the original SHA-256, independently checked in this assignment's source-hashes record. No new copy of the rubric was made.

Faithful transcription of the applicable row:

> The project must demonstrate advanced APT campaign analysis including malware reverse engineering with detailed technical documentation. Complex attack patterns must be analyzed with demonstrated zero-day research methodology and findings. A comprehensive supply chain vulnerability assessment must be completed with clear documentation of methods and results. All analysis must include detailed methodology documentation, technical findings, indicators of compromise, and mitigation recommendations. Evidence must include reverse engineering outputs, attack pattern analysis, and vulnerability assessment results.

Scale: **1 Complete / 0 Incomplete**. The other four rows concern Assignments 2–5 and are outside this submission. COMPLETE/PARTIAL/BLOCKED below describe evidence, not awarded marks.

| Official requirement | Evidence | Status and remaining qualification |
|---|---|---|
| Advanced APT campaign analysis | [campaign](apt-campaign-analysis.md), chronological and chain tables | COMPLETE documented campaign-level analysis; composite advisory is not a single-victim forensic timeline |
| Malware reverse engineering, detailed technical documentation | [malware](malware-analysis.md), published function/control-flow evidence and analysis-output table | COMPLETE secondary technical analysis under the user's fallback; PARTIAL if instructor requires original binary disassembly |
| Complex attack pattern analysis | [campaign](apt-campaign-analysis.md), boundary and detection analysis | COMPLETE analysis, no emulation/exploitation claim |
| Demonstrated zero-day research methodology and findings | [zero-day](zero-day-research.md), vendor notice → bug ID → patch → version → exploitation evidence | COMPLETE historical research; exploit not reproduced |
| Comprehensive supply-chain assessment, methods/results | [supply chain](supply-chain-assessment.md), [inventory and result records](../evidence/index.md) | COMPLETE local Python/application assessment; PARTIAL deployed OS/container/provenance assurance |
| Methods, findings, IOCs, mitigations throughout | All four reports; [implementation](implementation.md) | COMPLETE within named scope; historical indicators have no assumed current malicious ownership |
| Reverse-engineering outputs | [secondary analysis outputs](malware-analysis.md) | Published findings interpreted; no original Ghidra/IDA output or specimen hash verification |
| Vulnerability assessment results | [supply chain](supply-chain-assessment.md), dated collector JSON | COMPLETE read-only version/control assessment; negative findings retained |

Unresolved requirements: instructor acceptance of published reverse-engineering evidence instead of original sample work; original publisher/build provenance; deployed inventory and service controls. No permitted safe work depends on resolving these gaps. Original malware execution and exploit reproduction are not required by the supplied rubric and were not performed.
