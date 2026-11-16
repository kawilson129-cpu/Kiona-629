# OpenCTI capacity review — November 16, 2026

**Decision: BLOCKED at the capacity safety gate.** Docker is operational and this
task authorizes an isolated lab. The previous missing-Docker/approval explanation
is superseded. Deployment was stopped before pulls, credential generation, volume
or network creation, or container launch. No working deployment is claimed.

## Verified environment and source

- Apple Silicon / aarch64, host RAM **17,179,869,184 bytes (16 GiB)**.
- Docker Engine **29.9.3**, Compose **5.7.0**, 10 Docker CPUs.
- Docker reports **8,319,438,848 bytes (7.748 GiB)** usable memory, below its
  nominal 8 GiB setting; **0 running containers** at inspection.
- Existing checkout reviewed in place: commit
  `60285adb360e3823a334333ae4744255d8ac1821`, October 16, 2026. No reclone/fetch.
- Current published OpenCTI release observed: **7.261116.0**,
  [official release](https://github.com/OpenCTI-Platform/opencti/releases/tag/7.261116.0).
  This is a release observation, not an installed version or verified image digest.
  The checkout uses `opencti/platform:latest`, worker/connector `latest`, and Silo
  `latest`; those are mutable references, not reproducible deployment pins.
- All three upstream Compose variants, README, `.env.sample`, and RabbitMQ
  configuration were read. The main file parses successfully with
  `docker compose ... config --no-interpolate --format json`. This verifies
  upstream syntax only; it does not validate a deployable isolated lab.

## Minimum useful service set and memory decision

The architecture requires a platform, search engine, Redis, RabbitMQ, S3-compatible
storage, a worker, and an appropriate connector. A STIX file-import connector can
run separately from MITRE to reduce concurrency; neither removes the core services.

The [official infrastructure table](https://docs.opencti.io/latest/deployment/overview/#infrastructure-requirements)
lists these RAM values. They are published sizing requirements, not measured idle
usage, and do not prove that every smaller experiment must fail.

| Component retained | Published RAM minimum |
|---|---:|
| OpenCTI Core | 8 GB |
| Elasticsearch / OpenSearch | 8 GB |
| Redis | 1 GB |
| RabbitMQ | 512 MB |
| S3 / Silo / MinIO | 128 MB |
| One worker | 128 MB |
| One connector | 128 MB |

Even interpreting GB/MB conservatively as decimal, this is **18,024,000,000 bytes
(16.786 GiB)** before Docker/VM overhead and import bursts: **9,704,561,152 bytes
more than Docker reports available**. The platform and search engine alone exceed
the current Docker allowance. These are calculated budget figures, not observed
platform metrics. Extra concurrent import/export connectors would add to them.

The checkout also sets Node's old-space ceiling to 8096 MiB and the search heap to
4G; the development variant sets the search heap to 8G and adds Kibana. These
ceilings are not idle allocations, but running them unconstrained provides no
safe aggregate budget. Upstream services have no aggregate hard memory cap.
[Installation memory guidance](https://docs.opencti.io/latest/deployment/installation/#additional-memory-information)
also describes Redis stream growth and RabbitMQ thresholds. Import peaks have not
been measured on this host. No official supported 8 GiB lab budget was established.

**A lower-memory experiment remains technically unproven, rather than proven
impossible.** It cannot be certified safe for this assignment's deployment and
MITRE/import workload from the available evidence. Reducing heaps and imposing
arbitrary caps would not verify viability. The user's instruction to stop when
resources block deployment takes precedence over forcing an undersized trial.
Raising Docker's allowance on this 16 GiB Mac cannot satisfy these published
requirements while retaining safe host headroom; no host limit was changed.

## Isolation review for a future adequately resourced lab

Exclude `xtm-one`, `xtm-one-worker`, `pgsql-xtm-one`, `xtm-composer`,
`rsa-key-generator`, Kibana, extra workers and unused connectors. The upstream
composer mounts the Docker socket and forces amd64; omit it. The main file exposes
MinIO on all host interfaces and OpenCTI with an unspecified bind; neither binding
is suitable unchanged. Upstream sample credentials are placeholders, not secure
credentials. XTM settings must also be removed from the platform configuration.

After capacity is available, prepare a separate file under this assignment with
project `derexi-a3-opencti`, loopback-only `127.0.0.1:8083:8080`, no published
dependency ports, dedicated project volumes and a private dependency network.
MITRE alone needs narrowly scoped public-source retrieval; do not connect this lab
to production networks or DeRexi. Pin compatible image versions/digests and verify
arm64 manifests before pulling; their availability was not tested here. Generate
unique lab credentials in ignored, mode-0600 files; create restricted connector
accounts inside this new OpenCTI lab. Assign explicit per-service memory/CPU
limits, worker concurrency and logging limits within the new budget. Docker-managed
volumes would be dedicated to this lab; any bind-mounted runtime files must stay
inside the Assignment 3 workspace and be ignored.

No ready-to-run Compose file or secrets were created because task step 3 is
conditional on viability. No image was pulled and no container, network or volume
was created, changed, stopped or removed. No platform UI/API, connector, import,
deduplication, lifecycle or fusion execution evidence exists from this session.
The five platform acceptance checks remain BLOCKED, not FAIL or PASS.

## Resume condition

Provide a separate isolated host/VM with RAM above the published minimums plus
operating-system and ingestion headroom; **24 GiB or more assigned to the lab** is
a planning allowance, not a vendor guarantee. Then reassess disk/CPU, exact release,
arm64 compatibility and workload before deployment. An approved existing isolated
OpenCTI instance is another option. No production credentials or real banking data
are needed. Execute the existing five checks only after the deployment passes this
gate; preserve historical timestamps, source families and explicit simulation
labels in a reviewed STIX 2.1 import, and record actual results.

Evidence: [preflight record](../evidence/opencti-preflight-20261116/preflight.json),
[command results](../evidence/opencti-preflight-20261116/commands.txt),
[acceptance results](../evidence/platform-acceptance-results.json).
