# Assignment 3 — Advanced Threat Intelligence Operations

**Status: PARTIAL.** This local lab works; enterprise OpenCTI deployment is not verified.
Aurum Capital Bank and the DeRexi incident scenario are fictional. No real compromise
or production detection is claimed.

The [official rubric](<../Cyber Threats and Vulnerabilities 2 Tasks.pdf>) was read
visually from its image-based page. [Exact checklist](docs/rubric-checklist.md):
three requirements are complete within their stated local/documentation scope,
one is partial, and enterprise platform deployment is missing. These labels are
not instructor-awarded points; the official scale is Complete/Incomplete.

## Setup and usage

From the repository root, use Python 3.9+; the lab itself uses only the standard
library. No installs, API keys, Docker changes or database connections are needed.
The existing project `.venv` is usable, but the lab does not import the application.

```sh
A3='cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 3'
python3 -B "$A3/tests/run_tests.py"
python3 -B "$A3/src/intel_ops.py"
# Optional read-only collection from three fixed MITRE/CISA HTTPS URLs:
python3 -B "$A3/src/intel_ops.py" --collect
# Repeat historical expiry calculations at a fixed review time:
python3 -B "$A3/src/intel_ops.py" --as-of 2026-11-10T21:00:00Z
```

Every pipeline run creates a new UTC-named directory under `evidence/runs/`.
Tests save timestamped text/JSON and update `evidence/latest-tests.json` as a pointer.
`--output` must name a new directory inside this assignment. Offline mode labels
collection UNTESTED; it never fabricates a successful download. Network failure is
recorded as BLOCKED while local analysis continues. No indicator URLs are visited.

## Results

- **32 PASS / 0 FAIL / 0 BLOCKED** in offline functional/safety tests.
- **Five OpenCTI acceptance checks BLOCKED**, not attempted: missing runtime and
  deployment approval. These are separate from the passing local tests.
- Artifact audit: **7 PASS / 1 FAIL**. The failure detected concurrent edits to two
  Pulse source files after inspection, not an Assignment 3 code defect. Original
  hashes and the [drift record](evidence/concurrent-source-drift.json) are preserved;
  later Pulse revisions were not verified here.
- Latest [collection/analysis run](evidence/runs/20261110T210046393348Z/metrics.json):
  three public sources retrieved; four historical indicator observations reconcile
  into two indicators, with 50% duplication and complete source references.
- One historical infrastructure indicator is expired. Two reports derive from the
  same underlying dossier, so they count as one independent source family.
- Three separate campaign/case records; nine simulated events across four labelled
  hosts produce one alert (TP=1, FP=0, FN=0, TN=3). Tiny fixture precision/recall of
  1.0 is **not** a production detection or false-positive-rate claim.
- [Actor profiles](docs/actor-profiles.md) distinguish APT38 and FIN7; common behavior
  does not attribute the fictional incident to either. k.php remains unattributed.

Read [implementation](docs/implementation.md), [report-ready findings](docs/final-summary.md),
[progress/blockers](docs/progress.md), and the [OpenCTI validation plan](docs/opencti-validation-plan.md).
All new coursework, code and evidence is here. Prior coursework is referenced in place
in [the reuse inventory](evidence/reuse-inventory.json). Existing DeRexi, Supabase,
Auth/RBAC, users and functionality were not modified by this assignment. Concurrent
Week 10 changes were left untouched. No deployment, commit or push.
