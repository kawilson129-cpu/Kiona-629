# OpenCTI continuation — capacity blocked

**Updated November 16, 2026.** Isolated Assignment 3 deployment is authorized.
Docker is operational. The previous missing-runtime/approval explanation is
superseded by the [capacity review](opencti-capacity-review.md). No deployment was
attempted because a safe lab within the current Docker allowance was not
established. Do not run upstream Compose unchanged. The existing checkout is
already present in `src/opencti-upstream/`; do not reclone.

Keep preparation and evidence inside Assignment 3. After adequate isolated resources
are provided, review a separate minimal Compose file, release/digest pins and ARM
support. Use dedicated project volumes, loopback-only UI access, private dependency
networking and unique ignored secrets. Exclude XTM One, composer/Docker socket,
Kibana, extra workers and unused connectors. Validate hard resource limits and
import headroom before launch. Preserve production/DeRexi/Supabase/auth and all
unrelated Docker resources.

These are acceptance procedures, **not executed platform results**:

1. **OPENCTI-HEALTH-VERSION** — record deployed image digests/version, resource
   limits, healthy services, actual loopback UI screenshot and authenticated API
   and health responses. Sanitize credentials and health keys.
2. **OPENCTI-ATTACK-CONNECTOR** — configure a restricted MITRE ATT&CK account inside
   the new lab, validate its permissions and run a connector job. Retain real
   timestamps/import counts, a representative actor/technique relation and
   queue/worker results. No production integration.
3. **OPENCTI-IOC-IMPORT** — map reviewed lab JSON into supported **STIX 2.1** for the
   compatible import-file-STIX connector (upstream declares INTERNAL_IMPORT_FILE,
   application/json,text/xml and validation enabled). The lab JSON is not a
   validated STIX bundle. Preserve historical dates, source IDs/attribution,
   source-family caveats, defanged presentation and simulation labels. Separate
   historical research from fictional cases; keep enforcement disabled. Verify
   actual processing and resulting objects before claiming success.
4. **OPENCTI-REIMPORT-DEDUPE** — repeat the reviewed import; compare actual unique
   IDs/counts and references before/after. Demonstrate stale-indicator review,
   revocation/expiry and duplicate handling without automatic blocking.
5. **OPENCTI-FUSION-METRICS** — keep cases distinct; link sourced actors/techniques
   without attributing the fictional incident. Show campaign chronology and fuse
   reviewed sources/scenario/prior findings. Reconcile actual platform job, object,
   processing and error counts with local metrics. Capture actual relationship,
   lifecycle and timeline views plus sanitized exports.

Current [results](../evidence/platform-acceptance-results.json):
**0 PASS / 0 FAIL / 5 BLOCKED**. Capacity preflight ran; platform runtime checks did
not. No connector/import success or screenshots may be inferred from this plan.
Stop/clean up only this lab's verified resources if later deployed.
