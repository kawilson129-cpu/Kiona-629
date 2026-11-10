# CTI lab run

As of 2026-11-10T20:59:43.063399+00:00. Local research/simulation; no production sightings.

Indicators: 4 observations → 2 unique; 1 expired. Campaigns: 3; scenario alerts: 1.

Priorities below are historical finding scores, not current vulnerability claims.

- DVI-ADVISORY-CERTIFI: requires_current_validation; Upgrade the local certifi bundle to a reviewed fixed release (registry recommends 2026.10.19 or later), then verify which application clients use it. Preserve TLS validation.
- DVI-FEED-INTEGRITY: requires_current_validation; Bind article URLs to approved publisher hosts and validate redirects before following them.
- DVI-DEPENDENCY: requires_current_validation; Create a reviewed version/hash lock and deployed SBOM, then perform advisory triage.
- DVI-ADVISORY-PIP: requires_current_validation; Upgrade pip to a reviewed fixed release 26.2.0 or later and restrict installs/downloads to approved indexes.
- DVI-POLICY-WRITE: superseded_in_newer_isolated_tests; Review current isolated write-denial evidence; do not claim production closure

OpenCTI operation and real sensor detections remain unverified.
