# Progress, decisions and pending work

## November 10, 2026 — completed local work

- Read repository memory/instructions and located the actual official course PDF.
  Text extraction was empty. Rendered with macOS `sips`, read visually and preserved
  an exact five-sentence transcription plus source hash. No criteria invented.
- Audited original CT+V 1 PDFs, CT+V 2 analysis/ledger/vulnerability evidence, canonical
  Pulse source, retained Week 9 controls and historical Docker results. Referenced
  originals in place. This assignment made no changes to existing records or source.
- Docker/OpenCTI discovery: neither CLI found; loopback 8080 closed. This does not
  prove no other installation exists; no usable runtime configuration was found.
- Added only assignment-local code, fixture, test runner, reports and evidence.
  The old ledger is imported rather than copied or rewritten. Bytecode writes are
  disabled; temporary test data stays within this assignment.
- First public collection run was BLOCKED by sandbox DNS resolution. That actual
  run is retained at `evidence/runs/20261110T205900245347Z/`. After permission to read
  outside the network sandbox, collection succeeded for all three fixed sources.
  Final source-binding checks were validated in `20261110T210046393348Z`.
- Browser-based CISA retrieval returned 403, while the approved local HTTPS collector
  retrieved the PDF successfully. The manifest/hash and PDF establish the actual
  successful local collection; no failed browser response is presented as success.
- System Python lacked pypdf during exploration, and project pypdf image extraction
  lacked optional Pillow. No packages were installed; `sips` supplied the rubric
  render. These were tooling limitations, not application or final lab-test failures.
- Initial offline suite: 30 PASS. Added actor/domain and malformed-technique checks;
  final suite: 32 PASS / 0 FAIL / 0 BLOCKED. Both runs are retained. Three public
  collections verified separately. Five platform acceptance checks remain blocked.

- Final artifact checks: 7 PASS / 1 FAIL. Concurrent Week 10 changes appeared in
  the working tree; two Pulse source hashes changed after the audit. Preserved the
  initial failed check and saved `evidence/concurrent-source-drift.json`. Pipeline/test
  source hashes still match. No unrelated edits were reverted or incorporated.

## Decisions

- No enterprise-platform deployment: the user's guardrail explicitly requires approval.
  Local operations can be demonstrated without changing host services or DeRexi.
- Local JSON is not labelled STIX/OpenCTI compatible without an actual validated import.
- Research, historical artifacts, scenario events and untested platform outcomes are
  kept distinct. Duplicate sources never become independent corroboration.
- A past finding is not a current vulnerability claim. Newer isolated tests supersede
  the earlier policy-write result locally; no live production closure is inferred.
- Numeric confidence and expiry windows are training policy choices. No automated
  blocking, IOC requests, malware execution, active scanning or external sharing.

## Pending / blockers

1. Approve and provision an isolated Docker/OpenCTI lab with reviewed versions,
   resources, local ingress and separate private storage. No deployment was attempted.
2. Run the five [platform acceptance checks](opencti-validation-plan.md); retain
   screenshots, connector jobs, duplicate imports, relationship exports and metrics.
3. Obtain separately authorized representative sensor data to evaluate detection
   coverage and false positives beyond this tiny fixture.
4. Revalidate historical vulnerability/advisory applicability against current deployed
   inventory before prioritizing remediation. Existing Supabase/production blockers
   remain outside this coursework implementation and were not changed.

All Assignment 3 work, WIP, logs and session notes are inside this directory. The
current task's mandatory write boundary takes precedence over the earlier root-memory
update convention; root MEMORY.md is unchanged. No commit, push, reset, unrelated-file
changes or deployment occurred.

## November 16, 2026 — authorized deployment capacity review

- Read existing rubric, implementation, 32-test suite, public collection, acceptance
  plan and original Pulse drift evidence before continuing; no completed analysis
  or collection repeated. Existing upstream checkout reviewed in place.
- Docker Engine 29.9.3 / Compose 5.7.0 operational, aarch64, 10 CPUs, zero running
  containers, 8,319,438,848 usable bytes (7.748 GiB). Host RAM 16 GiB. Initial
  read-only socket/sysctl sandbox denials resolved by approved read-only retries.
- Published core-service minimums exceed the budget even without XTM One, composer,
  extra workers or optional connectors. Smaller safe workload unproven. Stopped
  before any pull/launch, secrets, volumes, networks or host changes, as instructed.
- Main upstream Compose parses; no isolated deployment configuration validated.
  Current release observed: 7.261116.0, not installed. Mutable upstream image tags
  do not establish deployed versions/digests or ARM compatibility.
- Local rerun **32 PASS / 0 FAIL / 0 BLOCKED**. Five platform runtime checks remain
  BLOCKED after refreshed preflight; no UI/API, connector/import/fusion claims.
  Prior acceptance/summary records archived before updating current pointers.
- Added capacity review, command/evidence records and assignment-local secret/data
  ignore rules; refreshed README, rubric, final summary, validation plan and summary.
  Original Pulse drift and artifact-audit failure retained byte-for-byte.
- Resume needs a separate adequately resourced isolated host/VM or approved isolated
  OpenCTI instance. Details: [capacity review](opencti-capacity-review.md). No DeRexi,
  Supabase, users/Auth/RBAC, unrelated Docker changes, commits or pushes.
