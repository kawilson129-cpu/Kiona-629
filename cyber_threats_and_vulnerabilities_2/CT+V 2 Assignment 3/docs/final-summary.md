# Report-ready findings — Assignment 3

**November 16, 2026: PARTIAL. Deployment stopped safely at the capacity gate.**
The official binary assignment criterion is not claimed complete.

| Official deliverable | Status | Verified scope / outstanding work |
|---|---|---|
| Enterprise threat intelligence platform deployment | **BLOCKED** | Docker operational; safe sizing within the present allowance not established. No deployed UI/API evidence. |
| Campaign tracking and analysis | **VERIFIED — local scope** | Three historical/scenario cases; nine labelled simulated events, four hosts, one alert. Platform demonstration blocked. |
| Advanced indicator management | **VERIFIED — local/documented scope** | Four observations reconcile to two indicators; provenance, source independence, review, expiry and approval/revocation workflows tested. Platform lifecycle proof blocked. |
| Threat actor profiles with attribution analysis | **VERIFIED — research scope** | Evidence-backed APT38/FIN7 profiles and technique overlap; fictional scenario attribution remains unknown. Platform relationships blocked. |
| Intelligence fusion and operational metrics | **PARTIAL** | Local IOC/public-source/scenario/prior-finding fusion works. Connector/import/reimport and platform metrics blocked. |

Docker Engine **29.9.3**, Compose **5.7.0**, aarch64 and **0 running containers**
were verified. Docker reports **8,319,438,848 bytes (7.748 GiB)** usable RAM on a
16 GiB Mac. The conservative decimal sum of the official minimums for the necessary
services is **18,024,000,000 bytes (16.786 GiB)** before overhead. This is sizing
arithmetic, not measured utilization. A smaller safe lab was not established;
this does not assert that every smaller experiment is technically impossible.

The existing checkout was inspected without recloning: commit
`60285adb360e3823a334333ae4744255d8ac1821`. Published release **7.261116.0**
was observed on the official release page; it was not installed. Upstream Compose
syntax parses. No isolated deployment config, image digests, UI/API health,
MITRE jobs, successful imports, screenshots or platform metrics are claimed.
No Docker resources or host settings were changed. [Capacity and isolation
review](opencti-capacity-review.md), [preflight](../evidence/opencti-preflight-20261116/preflight.json).

| Check family | PASS / verified | FAIL | BLOCKED | Evidence |
|---|---:|---:|---:|---|
| Current local functional tests | 32 | 0 | 0 | [November 16 run](../evidence/test-results-20261116T185123544043Z.json) |
| Platform acceptance checks | 0 | 0 | 5 | [Current statuses](../evidence/platform-acceptance-results.json); preflight ran, runtime checks did not |
| Retained public collection (November 10) | 3 | 0 | 0 | [Manifest](../evidence/runs/20261110T210046393348Z/collection.json); not recollected |
| Historical artifact audit (November 10) | 7 | 1 | 0 | [Original audit](../evidence/artifact-validation.json); not rerun or folded into functional counts |

The historical artifact failure records concurrent Pulse source changes; the
[original drift record](../evidence/concurrent-source-drift.json) and audit are
preserved. This continuation does not assert those revisions verified.

Retained findings remain bounded: the infrastructure lead is expired; E02/E05
belong to one source family; fixture TP=1/FP=0/FN=0/TN=3 is not a production rate;
generic ATT&CK overlap cannot attribute the fictional incident. Prior isolated
write-denial checks supersede an old local finding, not production remediation.
See [metrics](../evidence/runs/20261110T210046393348Z/metrics.json),
[implementation](implementation.md), and [actor profiles](actor-profiles.md).

**User action needed:** provide a separate isolated host/VM sized above the
published requirements with ingestion/OS headroom, or an approved isolated OpenCTI
instance. A 24 GiB lab allocation is a planning allowance requiring reassessment,
not a vendor guarantee. Raising the allowance on this 16 GiB Mac is insufficient
for the documented budget plus safe host headroom. Then prepare/pin/review the
configuration and execute the five [acceptance checks](opencti-validation-plan.md).
Capacity is the present blocker; deployment approval for the original isolated
scope is already supplied. No production connections, DeRexi backend, Supabase,
auth/RBAC/users, commits or pushes were changed.
