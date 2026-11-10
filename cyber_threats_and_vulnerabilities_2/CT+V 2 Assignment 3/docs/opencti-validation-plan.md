# OpenCTI continuation — deployment approval required

**Prepared procedure only. Nothing below was deployed.** Current discovery shows
no Docker CLI and no loopback listener on 8080; prior Windows Pulse evidence cannot
stand in for a threat intelligence platform. A different port or remote instance is
not ruled out; none was configured or verified in this assignment.

Use an isolated free/community OpenCTI lab after explicit approval. Begin with the
[official installation procedure](https://docs.opencti.io/latest/deployment/installation/)
and [upstream Docker configuration](https://github.com/OpenCTI-Platform/docker).
Select and record a reviewed commit and compatible image digests; this work does
not invent a tested version pin or a ready-to-run Compose file. Keep all downloaded
lab source/configuration/evidence under this assignment. No canonical application
or Supabase configuration is needed.

Proposed layout: loopback `127.0.0.1:8083` → OpenCTI; worker, search index, Redis,
message queue and object storage on an internal network. Publish no dependency
ports. Verify host capacity against [official requirements](https://docs.opencti.io/latest/deployment/overview/).
Use separate lab volumes and a dedicated project name. Do not reuse production
credentials or records. Configure private credentials in an ignored local file;
never include values in screenshots, resolved Compose output or logs. Use restricted
connector/analyst accounts and verify their permissions within the lab only.

## Proposed commands after approval

From the repository root, prepare the upstream checkout inside the workspace:

```sh
A3='cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 3'
git clone --no-checkout https://github.com/OpenCTI-Platform/docker.git "$A3/src/opencti-upstream"
# Review and check out the agreed commit before configuring credentials or running services.
git -C "$A3/src/opencti-upstream" checkout APPROVED_COMMIT
```

`APPROVED_COMMIT` is deliberately unresolved; do not run as-is. Review the actual
upstream Compose services, dependency versions, resource budgets, health checks,
local bind and secrets before deciding the exact deployment command. Docker
installation, pulls, host kernel changes and `compose up` require approval. Do not
run upstream host-level setup commands merely to close this checklist.

## Acceptance checks to close the remaining rubric gaps

1. Record Docker/Compose and OpenCTI version, image digests, healthy services and
   sanitized loopback/internal-network configuration. Capture the actual UI and
   health response, not a mock screenshot.
2. Configure a restricted ATT&CK connector. Save a successful job, timestamp,
   import count, representative actor/technique relation and queue/worker logs.
3. Manually map reviewed lab JSON to the platform's supported import format. It is
   not a validated STIX bundle. Import historical IOCs into a research-only case;
   keep dates, provenance and independent-source caveats. Never visit the indicators.
4. Repeat the import and record before/after unique counts and source references.
   Demonstrate duplicate handling and stale-indicator review without enabling blocks.
5. Create separate historical/scenario cases, link source-backed context, and compare
   platform import/processing/error counts with local metrics. Capture the actor
   profile, relationship graph, expired indicator, campaign timeline and metrics.

Save sanitized screenshots, logs, export and test JSON to a new `evidence/` run.
Do not claim platform fusion complete until these checks pass. Real sensor detection,
production performance and durable enterprise operations need separate authorization
and representative data. Stop only the newly approved lab project when finished;
never remove unrelated containers or existing volumes.
