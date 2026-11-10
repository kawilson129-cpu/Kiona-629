# Report-ready findings — Assignment 3

**Verdict: PARTIAL.** The official rubric has been located, transcribed and mapped.
Local campaign analysis, indicator management and two actor research profiles have
scoped evidence; enterprise deployment and platform fusion remain incomplete.

The lab extends DeRexi's existing threat-intelligence work without changing the
application. It reuses the prior indicator reconciliation code and historical
course reports, adds fixed-source public collection, correlates labelled scenario
events, tracks indicator review/expiry, compares actor context and reconciles stale
vulnerability findings with newer retained security evidence. No real compromise,
original malware execution or current vulnerability exploitation is claimed.

| Finding | Evidence-backed result | Meaning / remediation |
|---|---|---|
| Public collection works | Three sources retrieved and hashed: MITRE APT38/FIN7 layers and CISA FASTCash advisory | Preserve source timestamps; availability is point-in-time, not a continuous feed guarantee. |
| Historical duplicates are not independent evidence | Four records → two indicators, 50% duplicate ratio; one source family | Retain E02/E05 provenance without inflating confidence. |
| Infrastructure lead is stale | The historical URL is past its 14-day lab review deadline | Revalidate ownership/sightings before any operational use; keep defanged and non-enforcing. |
| Campaign rule works within its fixture | Nine simulated events, four hosts, one alert; TP=1/FP=0/FN=0/TN=3 | Expand with authorized real telemetry before treating these as detection rates. |
| ATT&CK overlap limits attribution | Scenario context overlaps both research profiles | DeRexi attribution remains unknown; require distinctive independent evidence. |
| Old policy-write claim is stale | Six newer isolated write-denial checks pass across Employee/Owner/Admin roles | Mark the old local finding superseded; do not claim production closure. Other historical findings need current validation. |
| Audit provenance drift | Two Pulse files changed concurrently after inspection; artifact checks 7 PASS / 1 FAIL | Keep original audit hashes and drift record; the new Pulse revisions are outside this assignment verification. |
| Enterprise TIP operation is missing | No local Docker CLI/OpenCTI listener; five acceptance checks blocked | Approve a separate isolated deployment and execute the prepared validation plan. |

**Tests:** 32 PASS, 0 FAIL, 0 BLOCKED in the offline suite; five additional platform
acceptance checks are BLOCKED and were not attempted. Live-source collection: 3/3
VERIFIED. Artifact checks: **7 PASS / 1 FAIL** due to concurrent Pulse source drift;
final pipeline/test hashes match. These counts are separate. [Actual local test results](../evidence/test-results-20261110T210129262284Z.json),
[run metrics](../evidence/runs/20261110T210046393348Z/metrics.json),
[platform blockers](../evidence/platform-acceptance-results.json).

Rubric coverage: 3 COMPLETE within explicit local/documentation scopes, 1 PARTIAL,
1 MISSING. The official binary criterion is **not claimed complete**. Immediate next
steps are approval/capacity for OpenCTI, native connector/import/reimport proof and
platform metrics. Authorized sensor data and operational monitoring follow after
that. No deployment, live Supabase/Auth/RBAC/user changes, commits or pushes occurred.
