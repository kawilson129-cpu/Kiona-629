# Actual preflight evidence — November 16, 2026

Deployment status: **BLOCKED at capacity gate**. No platform screenshot or runtime
log exists because OpenCTI was not launched. All records are sanitized; no secrets
were generated. This directory contains:

- `preflight.json`: actual Docker/host observations, decision, sizing arithmetic,
  upstream/source hashes, and preserved-original hashes.
- `commands.txt`: executed commands, successful outputs and resolved sandbox denials.
- `upstream-compose-uninterpolated.json`: parsed upstream syntax, with unresolved
  variables; not an isolated lab config and not runnable deployment evidence.
- `official-overview.html` / `official-installation.html`: downloaded official
  documentation snapshots. `*-excerpt.txt` contains the relevant sizing guidance.
- `prior-platform-acceptance-results.json` / `prior-verification-summary.json`:
  archived prior statuses, before refreshing the current evidence pointers.
- `verification.json`: final document/evidence validation results.

Current [platform checks](../platform-acceptance-results.json), [local rerun](../test-results-20261116T185123544043Z.json),
[capacity review](../../docs/opencti-capacity-review.md), and [summary](../../docs/final-summary.md).
