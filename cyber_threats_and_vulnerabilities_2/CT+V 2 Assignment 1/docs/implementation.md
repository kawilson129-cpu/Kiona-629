# Implementation, repeatability and evidence handling

## Boundaries

All new Assignment 1 artifacts are beneath this assignment directory. Existing coursework is referenced in place; no backend, Auth/RBAC, seeded user, Supabase, production service, repository history or deployment was changed. The user's explicit directory confinement takes precedence over the general instruction to update root MEMORY.md; the session handoff is in [progress](progress.md). No root-memory write was made.

## Inspection and research

Read root memory for state, visually reviewed the official rubric using the existing Assignment 3 rendering, inspected CT+V 1 APT/k.php/vulnerability PDFs with installed `pdftotext -layout`, and reviewed CT+V 2 Assignment 2 methods/results/raw advisories. Extraction was a reading aid; the original PDFs remain authoritative and are linked, not copied. Reviewed existing Week 9 test code, current security/AI/Pulse/frontend sources and Week 11 result JSON without importing application modules. The existing test module writes outside this workspace, so it was intentionally not rerun.

Public research used vendor/government/upstream/primary researcher material. Exact source URLs, access date, publication anchors and retrieval failures are in [research ledger](../evidence/research-ledger.md). Published technical findings were interpreted statically. No downloads of samples, malware execution, packet injection, credential collection, intrusive scanning or exploit triggers occurred.

## Repeatable analysis

From this assignment folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File src/collect.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/validate.ps1
```

`ExecutionPolicy Bypass` applies to that child process only; it does not alter persistent policy. The collector reads metadata and selected files, writes a new UTC timestamp directory and updates `evidence/latest-run.txt`. It makes no network requests. Every output location is derived from its script directory; inputs are explicit repository-relative paths. It does not inspect `.env`, import packages, run application handlers or install dependencies. `git ls-files` searches tracked candidate sample extensions; ignored/untracked files, nested archives and arbitrary renamed binaries are not exhaustively searched.

Collector outputs: complete installed metadata inventory with relationship strings and metadata hashes; explicit input hashes; historical-advisory version comparison; sample-search scope/results; assessment outcomes. A FAIL is a security condition, not a script crash. A BLOCKED condition lacks verification. Prior PASS records are labelled reused, never aggregated as new tests. Script completion is separate from risk acceptance.

The validator checks evidence independently: package identities and distribution metadata hashes against disk, original rubric hash, exact advisory comparison inputs and results, prior-result totals, required report files and local Markdown link targets. It reads only; its sole write is its dated validation JSON here. It tests evidence consistency, not live security effectiveness or the truth of a published malware claim.

## Actual execution and limitations

Initial virtual-environment Python invocation was blocked by sandbox executable access (`Access is denied`). An approved elevated read-only availability check succeeded: pypdf available, fitz/PIL unavailable. No packages were installed. PDF reading then used existing Git-bundled pdftotext. No app suite was launched. The collector ran successfully under PowerShell: **37 distributions; 9 outcomes: 3 PASS / 3 FAIL / 3 BLOCKED**. Exact UTC dates and output paths are in [evidence index](../evidence/index.md).

Browser research could not retrieve the old CISA MAR routes (HTTP 403); this is not a negative malware finding. The CISA-hosted advisory PDF and government notification supplied campaign context, and published primary technical research supplied the static-analysis fallback. No inaccessible source is presented as inspected evidence.

Limits: no fresh complete online advisory scan, wheel signatures or clean install; no production/container/OS inventory, original malware disassembly, current attacker IOC validation, live workflow test, actual transaction or exploit trace. Changing current dependencies invalidates inventory assumptions; rerun collector and advisory review. Static source checks and historical isolated results cannot establish production security.
