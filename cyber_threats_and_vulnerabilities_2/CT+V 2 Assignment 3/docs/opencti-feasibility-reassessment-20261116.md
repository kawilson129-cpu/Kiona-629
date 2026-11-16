# OpenCTI feasibility reassessment — November 16, 2026

**Recommendation: do not deploy under the current workload. A reduced lab may
be technically possible, but safe operation within this Mac's capacity is not
established.** This is an assessment only; no containers, limits, dependencies,
deployment configuration or application files were changed.

Reviewed the [existing preflight](../evidence/opencti-preflight-20261116/preflight.json),
[capacity review](opencti-capacity-review.md), unchanged upstream configuration
(all six recorded source hashes still match), and current official documentation.
A fresh read-only `docker info` returned:

```text
Server=29.9.3 Architecture=aarch64 CPUs=10 MemoryBytes=8319438848 ContainersRunning=0
```

The initial sandbox socket denial was resolved by an approved read-only retry.
Docker therefore still reports **7.748 GiB usable**, consistent with the nominal
8 GiB allocation. The local Docker settings store was read without printing its
contents; no explicit entries for the selected memory/CPU/swap override keys were
found. No Docker swap setting or current host/VM resident-memory split was verified.
Activity Monitor values are **user-reported**, not independently measured here:
16 GB physical, 10.19 GB used, 2.45 GB swap, green pressure.

Green pressure indicates the existing workload is being handled efficiently.
Swap already used does not establish current swapping/thrashing; its rate and
trend matter. Neither number proves sufficient headroom for a new workload.
Do not add the full Docker allowance to Activity Monitor usage: existing Docker
resident memory can already be included. Equally, the allowance is not an extra
8 GiB of physical RAM. [Apple memory-pressure guidance](https://support.apple.com/en-ie/guide/activity-monitor/actmntr34865/10.14/mac/15.0),
[Docker VM resource settings](https://docs.docker.com/desktop/settings-and-maintenance/settings/#advanced).
Apple's indexed official guidance was reviewed; direct page retrieval returned
HTTP 429. No Activity Monitor screenshot or fresh host memory trace was captured.

The prior assessment needs one qualification: OpenCTI explicitly introduces its
infrastructure table as **production** minimums. Summing those values does not
prove that a tiny research lab cannot run below them. Node/JVM heap ceilings are
also not measured idle demand. However, no official reduced-lab minimum or measured
startup/import peak for this exact version and host has been established.

| Resource question | Evidence-backed answer |
|---|---|
| Smallest useful service set | Platform, search engine, Redis, RabbitMQ, S3-compatible storage, one worker and one connector at a time. Exclude XTM One, composer, Kibana and unused connectors. |
| Published production RAM floor for that set | About **18.024 GB (16.786 GiB)** using conservative decimal units, before overhead: 8 + 8 + 1 GB, plus 512 + 128 + 128 + 128 MB. |
| Verified reduced-lab RAM minimum | **Unknown.** No defensible claim that 6–8 GiB is sufficient for startup and MITRE ingestion. |
| Capacity for a deployment following published sizing | Separate host/VM with more than that service budget plus OS/import headroom; **24 GiB RAM** is a conservative planning allocation, not a proven lab minimum or vendor guarantee. |
| Published dependency storage floor | Approximately **50 GB** across search, Redis, S3 and RabbitMQ, plus images, VM and ingestion headroom; no fresh disk-capacity check performed. |

Sources: [OpenCTI production architecture and requirements](https://docs.opencti.io/latest/deployment/overview/#infrastructure-requirements),
[memory configuration guidance](https://docs.opencti.io/latest/deployment/installation/#additional-memory-information).

Main risks are host swap growth and responsiveness loss; container OOM termination;
slow search/index initialization; and connector/worker import bursts causing timeouts
or interrupted jobs. An idle login page would not establish ingestion capacity.
Hard container limits can bound the lab but cannot guarantee successful processing
or eliminate host memory pressure. Native ARM64 image support also remains unverified.

**Next action:** use a separate adequately sized isolated machine or approved
isolated OpenCTI instance. If pursuing this Mac instead, first close nonessential
apps and record a quieter baseline including Docker VM residency and swap trend;
then separately review a bounded, staged trial plan within the unchanged 8 GiB
Docker limit. Require aggregate service caps below usable VM RAM, VM headroom,
one worker/connector, limited data, native images and explicit stop conditions
(sustained yellow/red pressure, sustained swap growth, OOM or responsiveness loss).
That would be an unverified experiment needing separate execution authorization;
it is not a present safe-deployment recommendation. No trial was run, and the
existing platform acceptance statuses and historical Pulse drift remain unchanged.
