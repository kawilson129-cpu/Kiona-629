# FASTCash / BeagleBoyz campaign analysis

## Scope and source confidence

Research date: November 17, 2026. The historical case is the FASTCash bank-payment-switch campaign described in the August 26, 2020 joint US government advisory AA20-239A. It is a campaign composite, not a reconstruction of one victim. BeagleBoyz overlaps with APT38 and other vendor clusters; those labels do not establish identical membership. The advisory attributes the activity to North Korea. [CISA joint advisory](https://content.govdelivery.com/accounts/USDHSCISA/bulletins/29bf7dc)

MITRE identifies APT38 as G0082 and describes financial targeting, with overlapping North Korean group definitions. Confidence is high in the **published government attribution**, moderate in treating every vendor-labelled intrusion as the same operational team, and absent for any attribution to a fictional Aurum incident. This submission has no raw telemetry for independent actor attribution. [MITRE APT38](https://attack.mitre.org/groups/G0082/)

## Objectives and chronology

The criminal objective is unauthorized cash withdrawal by subverting payment authorization. Policy theft at DeRexi is a separate hypothetical intelligence objective: knowing approval chains could support social engineering, but DeRexi is not an ATM switch and has no demonstrated payment-network integration.

| Date | Documented milestone | Evidence distinction |
|---|---|---|
| Since 2016 | FASTCash retail payment infrastructure targeting | Historical campaign start reported retrospectively by CISA |
| October 2018 | Public FASTCash disclosure; AIX switch manipulation identified | Disclosure date is not the first intrusion date |
| February 2020 | Renewed bank targeting reported | No date assigned to an Aurum event |
| August 26, 2020 | FASTCash 2.0 advisory describes Windows support and interbank processor expansion | Campaign evolution, not proof of one continuous intrusion |

These dates and the switch/message-tampering behavior come from [AA20-239A](https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf).

## Attack chain and ATT&CK mapping

The CISA advisory explicitly combines incidents; the table orders documented capabilities into an analytical chain. It does not imply every technique occurred in a single intrusion. Technique references can be inspected through [MITRE G0082](https://attack.mitre.org/groups/G0082/).

| Stage | Reported procedure / tool | ATT&CK mapping | Aurum defensive interpretation (proposed) |
|---|---|---|---|
| Entry | Targeted attachments / job lures | T1566.001 Spearphishing Attachment | Filter attachments; Alex verifies unusual policy requests through a known channel |
| Execution | PowerShell and scripts | T1059.001 PowerShell | Alert on unusual parent/child chains and download behavior, not all administrator scripting |
| Credential and lateral access | Captured input; valid administrative accounts; SMB access | T1056 Input Capture; T1078 Valid Accounts; T1021.002 SMB/Windows Admin Shares | MFA, separate admin identities, segment staff and privileged servers |
| Collection | Local files and screenshots | T1005 Data from Local System; T1113 Screen Capture | Monitor bulk policy/directory access and protect audit retention |
| Remote control | CROWDEDFLOUNDER/HOPLIGHT RATs; ELECTRICFISH proxy | T1105 Ingress Tool Transfer; T1090 Proxy | Egress allow rules and module/process telemetry; a proxy alone is not attribution |
| Monetization | Injected switch code changes ISO 8583 financial messages | T1055 Process Injection; T1565.002 Transmitted Data Manipulation; T1565.003 Runtime Data Manipulation | Monitor switch integrity and issuer/acquirer reconciliation outside the compromised process |

Behavior/tool support: [CISA advisory](https://content.govdelivery.com/accounts/USDHSCISA/bulletins/29bf7dc). ATT&CK naming is an analyst mapping, not an assertion that DeRexi has these capabilities or logs. FASTCash hooking is expanded in [malware analysis](malware-analysis.md). No zero-day is necessary to explain this chain; authorized credentials and process tampering are distinct from exploitation of an unknown flaw.

## Indicator register

| Historical indicator | Type/context | Source / confidence | Use and limitation |
|---|---|---|---|
| `b484b0dff093f358897486b58266d069` | MD5, job-themed initial-access file in advisory | CISA AA20-239A / high source confidence | Retrospective file matching; MD5 is weak for integrity and not actor proof |
| `5cfa1c2cb430bec721063e3e2d144feb` | MD5, CROWDEDFLOUNDER sample | CISA AA20-239A / high | Historical hunt seed; renamed/rebuilt malware evades exact hash |
| `f34b532117b3431387f11e3d92dc9ff417ec5dcee38a0175d39e323e5fdb1d2c` | SHA-256, later Linux FASTCash variant | [Original haxrob research](https://haxrob.net/linux/fastcash-for-linux/) / moderate corroborative attribution | Extension context, not an IOC observed in the 2020 campaign or locally |

No indicator was contacted, detonated, submitted to a scanner, or found on a DeRexi host. CISA hash provenance: [official bulletin](https://content.govdelivery.com/accounts/USDHSCISA/bulletins/29bf7dc). Hashes are historical investigative leads, not a current exhaustive blocklist. No invented IP/domain fills missing campaign evidence.

## Complex pattern and mitigation analysis

The important trust failure is that a legitimate process can return an attacker-selected answer. A good TLS connection to that process does not prove the business answer is correct. Thus Aurum should independently reconcile payment approvals and require approved message authentication and chip cryptogram validation in any actual payment environment. These are bank controls proposed from the threat model; they are not implemented or tested here.

For DeRexi, the analogous integrity risk is a policy answer sourced from an unauthorized policy change or falsely labelled feed. Proposed layered controls: independent policy review/publication, least privilege, source binding, citations, content-free audit records and incident routing. Maya owns policy review; Chris coordinates incident triage; Lucy handles platform containment. They are fictional roles, not notified people. Prior [Assignment 1 scenario](../../../cyber_threats_and_vulnerabilities_1/CT+V%20Assignment%201/DeRexi_APT38_FASTCash_Incident_MITRE_Report.pdf) is reused only as a hypothetical model.

Detection plan: correlate unexpected modules or executable-memory changes, switch account misuse and transaction mismatches; for DeRexi correlate unusual policy-version publication, ownership changes, bulk retrieval and source-host rejection. Validate with approved telemetry and benign fixtures before deployment. Limitations include legitimate module hooks, missing logs and custom payment formats. A single PowerShell event, filename or hash is insufficient to infer the full campaign.
