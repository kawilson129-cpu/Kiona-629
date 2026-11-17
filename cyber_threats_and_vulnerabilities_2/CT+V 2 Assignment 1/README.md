# Advanced Threat Analysis — DeRexi / Aurum Capital Bank

Prepared November 17, 2026. Aurum Capital Bank and its DeRexi deployment are fictional. Historical campaigns and vulnerabilities are real; no intrusion at Aurum or DeRexi is claimed.

Start with [rubric checklist](docs/rubric-checklist.md), then [final summary](docs/final-summary.md). The submission contains:

- [APT campaign](docs/apt-campaign-analysis.md): FASTCash / BeagleBoyz, objectives, chronology, attack chain, ATT&CK, indicators and defensive application.
- [Malware analysis](docs/malware-analysis.md): static secondary analysis of published FASTCash technical evidence; separate review of the existing k.php dossier.
- [Historical zero-day](docs/zero-day-research.md): CVE-2023-4863, source triangulation and patch analysis, without an APT38 attribution claim.
- [Supply chain](docs/supply-chain-assessment.md): local inventory, historical advisory applicability, provenance, services, boundaries and prioritized treatment.
- [Implementation](docs/implementation.md), [progress](docs/progress.md), and [evidence index](evidence/index.md): methods, exact commands, dates and limitations.

Run from this directory in PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File src/collect.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/validate.ps1
```

Both scripts write only beneath this directory. Collection reads package metadata and selected existing files without importing DeRexi, reading `.env`, running malware, installing dependencies, or contacting services. The execution-policy flag applies only to the child process. Existing test evidence is referenced, not rerun; its old runners have output paths outside this assignment.

Overall evidence status: **documented analysis complete within the permitted secondary-source scope; original sample reverse engineering and production assurance remain unverified**. The official binary rubric's final grade belongs to the instructor.
