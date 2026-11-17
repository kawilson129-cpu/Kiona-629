# Enterprise risk assessment

## Decision context and boundary

Assessment date November 17, 2026; horizon 12 months. Business objective: bank employees receive accurate policy guidance, approved policy changes and confidential incident routing. Aurum is a fictional federally chartered national bank; DeRexi is a policy/incident application, not a core banking transaction system. No direct ATM/SWIFT integration or real customer dataset is assumed. Customer-information safeguards are mapped conditionally where such information would enter policy/support workflows.

This assessment covers application/API, employee UI, policy library/governance, documents, identity, database, dependencies/build, Pulse, optional AI/email services, logging, recovery and audit governance. The [Assignment 2 asset register](../../CT+V%202%20Assignment%202/closure/assets-reconciled.json) is the historical starting point, not a fresh complete enterprise inventory. Production, network/physical infrastructure, OS/container package scans and vendor assurance were not accessed. The CT+V 1 classroom SSH host is a different population and does not establish current server exposure.

Method structure follows risk identification, analysis, response and maintenance described in [NIST SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final). The numerical model below is our explicit local planning method, not a NIST-mandated formula.

## Quantification method and assumptions

Use US dollars and annual loss-event frequency:

```text
SLE = response + restoration + interruption + legal/communication costs per loss event
ALE = ARO × SLE
ARO = assumed loss events per year (not probability of any attempted attack)
Inherent ALE: before the relevant safeguards
Conditional residual ALE: estimated effect of currently demonstrated local safeguards
Target ALE: scenario after proposed treatments have been verified
```

The CSV contains every numeric input and calculated output. Monetary inputs and frequencies are **illustrative analyst assumptions**, with no bank loss history, actuarial calibration or accepted risk appetite. Example R01 SLE $500,000 = $100,000 investigation + $150,000 restoration + $200,000 interruption + $50,000 legal/communication. No regulatory fine is presumed. Other SLEs are rounded scenario envelopes for the same cost categories, not invented invoices. Reassess them with business/finance owners before real decisions.

R01 example: inherent 0.8 × $500,000 = **$400,000/year**; conditional residual 0.2 × $500,000 = **$100,000/year**; target 0.05 × $500,000 = **$25,000/year**. The reduction is a planning judgment based on local denial tests, not a measured 75% control effectiveness rate. PASS counts are never used as a risk-reduction percentage.

Proposed severity thresholds: Low < $10,000 ALE; Medium $10,000–<$50,000; High $50,000–<$250,000; Critical ≥$250,000. Critical/High items receive priority review; production-access/recovery gates override a lower dollar score. These thresholds support relative triage only. Management acceptance is NOT recorded. For conditional controls, the conservative production bound remains the inherent ALE until deployed effectiveness is demonstrated.

Uncertainty: use residual ARO low/high values in the register; multiply both by SLE to obtain a range. Low is half the central estimate; high is the inherent ARO for R01–R05, and 1.5× central for R06–R10. R01 residual range is $50,000–$400,000/year. Sensitivity: doubling R01 SLE raises its central residual ALE to $200,000; doubling ARO does the same. Doubling both yields $400,000. These are sensitivity scenarios, not confidence intervals. Common causes (cloud compromise, identity failure) correlate risks, so **do not sum row ALEs** into a portfolio forecast.

## Assets, threats and control credit

| Risk | Asset / threat / vulnerability or uncertainty | Current-control basis |
|---|---|---|
| R01 | API/private incidents; stolen account or unauthorized user; authorization bypass | Fresh signed identities, anonymous denials, private-object and role tests; production chain unverified |
| R02 | Input/document boundary; malformed payload; validation/resource exhaustion | Fresh negative HTTP/schema and generic error checks; native parser/resource evidence reused, not rerun |
| R03 | Approved policies; insider/confused deputy; bypass of independent review or stale revision | Fresh governance publication, separation-of-duties, revision and rollback checks |
| R04 | Pulse source attribution; impersonated publisher; misleading source label/link | Fresh normalization/cache checks and reserved-domain hostile-host negatives |
| R05 | Security telemetry; attacker evasion/operator oversight; missing durable review/retention | Fresh redaction/event checks; no credit for unverified collector/retention |
| R06 | Dependencies/build; malicious index or trust compromise; affected versions/unlocked provenance | Fresh metadata comparison/requirements check; no improvement credited while findings persist |
| R07 | Database/Auth boundary; direct-client access or transport mistake; live RLS/ACL/schema/TLS acceptance missing | Historical readiness gaps, no production access; no reduction credited |
| R08 | Policy/database/original documents; outage/deletion; restore effectiveness unknown | Historical isolated atomic rollback is not disaster recovery; no reduction credited |
| R09 | AI/email/provider boundary; data disclosure/misrouting/outage; contracts and live handoff not validated | Existing code/mocked evidence by reference; supplier operating assurance unverified |
| R10 | Risk program and threat visibility; unmanaged changes or slow response; independent audit/recurring monitoring and deployed intel platform missing | Assignment 3 capacity block and absent operating records; written program not equivalent to operation |

## Treatment and residual decisions

[Risk register](risk-register.csv) is the authoritative row-level plan. All ten risks are proposed **MITIGATE**, with **AVOID production activation pending gates** additionally applied to R07/R08 and **TRANSFER through reviewed contracts only** as a possible supplement for R09. No insurance coverage or accepted exception is assumed. Retained risks require a named accountable executive, rationale, compensating measures, expiry and independent review; none was fabricated.

Priority 0: resolve R07 production identity/DB/transport acceptance before exposure. Priority 1: R06 supply-chain findings, R08 restore proof, R05 durable logging and R01/R03 deployment acceptance. Priority 2: residual input/feed controls, third-party review and audit adoption. Dates in CSV are proposed days from management intake; release gates remain earlier when applicable.

Review quarterly, after material code/provider/schema/permission change, new exploited advisory, significant incident or evidence drift. A new failed control invalidates related conditional credit. A closed finding requires correction plus independent retest and owner acceptance, not merely revised documentation. Preserve original tests and risk-intake dates in a future change ledger; this assessment does not rewrite earlier coursework risk scores.
