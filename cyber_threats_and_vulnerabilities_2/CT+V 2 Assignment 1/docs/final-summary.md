# Final summary

Prepared November 17, 2026. All four requested analyses and the official-rubric evidence map are delivered. Aurum/DeRexi compromise scenarios remain fictional. Historical FASTCash and CVE-2023-4863 evidence are separated, with no invented APT38/zero-day association.

| Deliverable | Evidence status |
|---|---|
| APT objectives, chronology, chain, tools, ATT&CK, IOCs, attribution and mitigation | Documented historical campaign analysis; hypothetical Aurum implications labelled |
| Safe malware technical analysis | Published FASTCash static technical evidence interpreted; existing k.php dossier reviewed; no original specimen disassembly claimed |
| Historical zero-day methodology and findings | Vendor report, exploitation acknowledgement, upstream fix and version boundaries traced |
| Supply-chain assessment | 37 installed distributions; relationship/provenance limitations, service boundaries, advisory applicability and prioritized risk register |
| Repeatable analysis and evidence | Read-only PowerShell collector and independent artifact validator; dated JSON and source hashes |
| Official rubric mapping | Every phrase mapped in [checklist](rubric-checklist.md); no grade self-awarded |

Collector: **3 PASS / 3 FAIL / 3 BLOCKED** across 9 assessment outcomes. FAIL: no complete hash lock, certifi and pip affected-version matches persist. These are unresolved findings, not proof of successful exploitation. PASS includes inventory and inspection of reused November 12 result records (88 security / 97 Pulse passing checks); no application tests were rerun.

Artifact validation: **122 PASS / 0 FAIL**, recorded separately in `evidence/validation-*.json`. An initial validator array-handling defect produced 119 PASS / 2 FAIL; that attempt is preserved and superseded. These counts verify artifact consistency, not production security.

Blockers/limits: original malware specimen unavailable; publisher/wheel/build provenance unverified; complete fresh advisory scan and deployed OS/container/browser/service acceptance not performed. Instructor acceptance of secondary reverse engineering remains a grading question. These limits do not prevent completion of the authorized safe analysis.

Recommended next actions: review certifi/pip updates and lock/provenance controls through the normal change process; validate actual deployed trust stores, dependency graph and authorization/transport controls before activation. No changes were applied. All new files are confined to this Assignment 1 workspace; no deployment, backend/Supabase/auth/seed modification, commit or push occurred.
