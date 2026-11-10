# Actor profiles and attribution assessment

Sources were reviewed November 10, 2026. The [collection manifest](../evidence/runs/20261110T210046393348Z/collection.json)
links timestamped MITRE layers and the CISA PDF. The narrative group pages below were
also reviewed directly. Reported historical attribution is not a DeRexi observation.

## APT38 / G0082

**Focus and motivation.** MITRE describes a North Korean state-sponsored cluster
focused on financial cyber operations, with banking and payment-system targeting.
Alias boundaries overlap with other North Korean clusters; labels are not unique
identities. [MITRE group profile](https://attack.mitre.org/groups/G0082/).

**Campaign and technical context.** The August 26, 2020 joint FASTCash advisory
attributes the BeagleBoyz banking activity to North Korea and describes manipulation
of payment-switch processing. This is a historical case, not a policy-service breach.
[CISA advisory](https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf),
[retrieved copy](../evidence/runs/20261110T210046393348Z/cisa-fastcash.pdf).

**Behavior links.** The retrieved G0082 layer includes the scenario's T1566.001,
T1059.001, T1543.003, T1135 and T1005. That makes them useful hunting context; it does
not make the fictional event chain attributable. Preserve attachment ancestry,
process trees, service changes and account/session context before escalation.

**Confidence and alternatives.** Confidence is high that the cited sources report
this public association. Confidence in attribution of the fictional DeRexi activity
is **unknown**: no real victim telemetry exists. FIN7, insider misuse, benign
administration and unrelated intrusion are alternatives. ATT&CK cites the joint
advisory, so those two publications are not automatically independent corroboration.

## FIN7 / G0046

**Focus and motivation.** MITRE describes a financially motivated group with broad
sector targeting, including financial services; reported operations span payment-card
crime and ransomware. FIN7 and Carbanak are tracked separately despite tool overlap.
[MITRE group profile](https://attack.mitre.org/groups/G0046/).

**Behavior and relevance.** The retrieved FIN7 layer overlaps four scenario behaviors:
attachment phishing, PowerShell, service creation and local collection. It provides
an alternative hypothesis to APT38. A fictional bank could face fraud or disruption,
but those motives alone cannot identify a group.

**Attribution assessment.** The profile reflects published research with moderate
analyst confidence for planning. No FIN7 association with Aurum Capital Bank or k.php
is established. Require distinctive infrastructure, malware lineage, timing and
independent incident evidence to strengthen any real attribution. Shared tools and
one matched technique are insufficient; preserve the unknown conclusion meanwhile.

## Separate unknown cluster: historical k.php dossier

The [existing dossier](<../../../cyber_threats_and_vulnerabilities_1/CT+V Assignment 1/Malware_Analysis_Threat_Dossier_k_php.pdf>)
provides a SHA-256, historical download URL and first-seen timestamp. Exact family and
actor are unresolved. Neither APT38 nor FIN7 is assigned. This is a separate malware
case rather than an invented named actor. No sample custody, execution or fresh
infrastructure ownership verification was performed.

## Analyst handoff

Chris Tanaka (fictional SOC role) would validate sensor sightings and source dates;
Maya Patel (fictional policy-owner role) would assess policy-process impact. These
are proposed responsibilities, not notifications sent or changes to seeded users.
Research sharing must include provenance, confidence, historical/simulated labels
and handling restrictions; obtain authorization before wider distribution.
