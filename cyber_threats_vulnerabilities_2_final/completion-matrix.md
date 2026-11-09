# Evidence completion review

Review date November 9, 2026. Original results remain intact. New artifacts are under followup/.

## Classification of all 18 legacy failures

| Check | Classification | Evidence and consequence |
|---|---|---|
| C01-01 | Mixed static-test assumption and genuine gap | Detector fails to recognize get_identity on protected routes. Policy creation/version handlers still lack identity guards and accepted requests in the original fake-session run. Public reference routes require a declared access policy before being called defects. |
| C01-02 | Outdated import assumption | security.py imports auth inside _supabase_verifier. Direct import in main.py is unnecessary. Fresh JWT foundation suite passed 24/24, without proving the complete production chain. |
| C01-08, C01-09 | Genuine authorization weaknesses | Original isolated requests returned 201 for creation/publication with fake writes. Unsigned role headers establish anonymous reachability, not authenticated Employee identity. |
| C01-14 | Harness identity assumption | X-Demo-Role does not authenticate. Two 401 responses do not establish equal authenticated authority. |
| C01-15 | Genuine contract/documentation gap | Header-based authentication does not declare a security scheme. Missing scheme alone does not prove missing enforcement. |
| C02-01 | Authentication gate and stale contract | 401 precedes schema tests. user_id is now optional. Fresh model check rejects whitespace question. |
| C02-05 | Authentication gate and stale contract | user_id now optional. Fresh model check rejects non-boolean rating. |
| C02-07 | Authentication gate | Missing-message existence validation remains untested for an authenticated caller. |
| C02-08 | Authentication gate | Fresh schema check rejects 50,000-character feedback. |
| C02-09 | Authentication gate and stale contract | reporter_id now optional. Authenticated incident validation remains only partly tested. |
| C02-11 | Authentication gate | Fresh schema check rejects 50,000-character incident text. |
| C02-12 | Authentication gate and stale contract | sender_id now optional, body limit now 4,000. Fresh check rejects 4,001 characters. The legacy 2,001 case is outdated. |
| C02-17 | Authentication gate | Authenticated invalid-assignee existence check remains unverified. |
| C02-21 | Genuine usability gap | Original simulated failure returns generic Internal Server Error without actionable retry text. Response does not leak SQL. |
| C02-22 | Authentication gate | Fresh StrictBool schema test rejects yes. Original failure text incorrectly suggests coercion despite no write. |
| C02-25 | Authentication gate | Authenticated cross-record consistency remains unverified. |
| C02-26 | Authentication gate and stale identity contract | Identity is server-derived. Test should check authenticated actor resolution and mismatched legacy identity, not assume body user_id owns feedback. |

Several original PASS checks also prove only anonymous denial, including cross-user and non-participant scenarios. They cannot establish authenticated object ownership. Retain original counts as runner outputs, with these limitations.

## Executed additions

- Existing test_week7_auth.py ran locally, 24 passed and 0 failed. Output in followup/jwt-results.txt. This uses synthetic credentials and mocked verification dependencies.
- Five direct Pydantic negative checks passed. Exact inputs and output in followup/inspect_local.py and schema-results.json. No application import or database needed.
- Captured 35 installed distributions with versions and declared dependency relationships in followup/package-inventory.json. This expands direct dependency evidence to the local installed environment. It does not identify deployed packages or establish CVE applicability.
- Read security.py and schemas.py to trace indirect authentication, optional actor fields, StrictBool and current limits.
- Docker CLI discovery returned no command. Container runtime proof remains blocked on a Docker-capable environment.

## Remaining work, prioritized

| Assignment | Safely attainable evidence added or already available | Requirement still requiring action |
|---|---|---|
| 4 | Current failure triage, JWT and schema validation, prior risk register | Signed-role route/ownership checks in disposable DB, dated monitoring records, restore drill |
| 2 | Installed package relationships and additional control assessment | Authorized enterprise host/owner reconciliation, credentialed scan, remediation operating metrics |
| 1 | Local installed dependency inventory | Original sample static RE outputs in isolated lab, research reproduction, OS/deployment SBOM and advisory assessment |
| 3 | Existing tested indicator reconciliation and provenance | Deploy TIP, run connectors, demonstrate campaign graph and operational metrics |
| 5 | Existing HTTP dashboard and fixture feed tests | Docker build/run and security inspection, current live feed data flow |

## Screenshots and manual evidence to collect

Screenshots supplement logs and underlying artifacts.

1. Assignment 1. In an authorized isolated lab, capture sample hash/type and annotated static reverse-engineering output. Save decoded text, offsets and tool logs. Capture controlled research comparison and save reproducible inputs/results. Provide deployed OS and dependency inventory for advisory assessment.
2. Assignment 2. Capture approved discovery/scan scope and results, asset relationships, assessment execution and remediation queue. Export raw scan files, owner inventory and dated closure/retest records.
3. Assignment 3. Capture OpenCTI version/health, connector settings with secrets hidden, successful imports, campaign-to-actor/indicator relationships, duplicate handling and metrics. Export connector logs and representative records with provenance.
4. Assignment 4. Provide approved control/owner mapping, dated monitoring records, signed-role negative tests and a witnessed disposable restore with integrity comparison and recovery timing. Capture failed/denied requests and restored records alongside raw logs.
5. Assignment 5. On Docker-capable lab infrastructure, execute the report's build/self-test/run commands. Capture docker version, running container, non-root/read-only/capability settings and dashboard. Save image digest and sanitized inspection. Capture live feed health and normalized data with timestamps.

## Completion matrix

| Assignment | Status | Blocking completion evidence |
|---|---|---|
| 1 Advanced Threat Analysis | PARTIAL | Original RE, research reproduction and deployed supply-chain assessment |
| 2 Enterprise Vulnerability Management | PARTIAL | Enterprise discovery, operating program and authenticated control coverage |
| 3 Advanced Threat Intelligence Operations | PARTIAL | Running enterprise TIP and connector/campaign/fusion evidence |
| 4 Risk Management & Audit Implementation | PARTIAL | Operating monitoring, authenticated control validation and recovery evidence |
| 5 Platform Development & Integration | COMPLETE (isolated Pulse scope) | Verified Docker build, healthy container, runtime security, live feeds and dashboard. See docker-evidence/README.md. |

Individual runtime and lab requirements are BLOCKED pending appropriate infrastructure or artifacts. No complete rubric criterion is claimed based solely on these additions.

