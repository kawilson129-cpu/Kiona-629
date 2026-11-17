# Evidence index

All new evidence remains here. Dates use UTC; the run occurred November 17, 2026 (America/New_York as well). [Latest run pointer](latest-run.txt) identifies the most recent collector execution. Earlier runs are retained.

Initial run: [20261117T054916Z results](20261117T054916Z/results.json): 37 packages, 3 PASS / 3 FAIL / 3 BLOCKED. Files include:

- [Installed inventory](20261117T054916Z/inventory.json): exact versions, Requires-Dist, installer metadata and hashes.
- [Source SHA-256](20261117T054916Z/source-hashes.json): authoritative rubric, existing reports, source and prior evidence fingerprints.
- [Historical comparison](20261117T054916Z/historical-advisory-comparison.json): two exact current-version matches, aliases retained.
- [Sample search](20261117T054916Z/sample-search.json): no tracked sample candidates; scope limitations explicit.
- [Research ledger](research-ledger.md): public sources and failed retrievals.
- `kphp-extraction.txt`, `apt-prior-extraction.txt`, `vulnerability-prior-extraction.txt`: pdftotext reading aids from original reports, not original malware analysis; originals linked in reports.

The two prior result checks inspect 88 security / 97 Pulse PASS records from November 12, with no application rerun. This submission does not claim 185 new application tests. Three FAIL outcomes are the current lock gap and two affected-version matches. Three BLOCKED outcomes concern original malware sample work, live verification and publisher provenance. No binary download, exploit or live scan evidence exists because those actions were not performed.

`validation-*.json` records independent artifact consistency checks. Counts are separate from security findings. See [final summary](../docs/final-summary.md) for the verified final validation count.
