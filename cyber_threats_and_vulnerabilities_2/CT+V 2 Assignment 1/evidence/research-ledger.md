# Research ledger

Access date for all entries: November 17, 2026. Browser retrieval was read-only. Links identify the inspected publications; no binaries were fetched. Reports paraphrase supported findings and label analyst inference. Publication date anchors are distinguished from access dates.

| ID | Source / publication anchor | Evidence used and reliability |
|---|---|---|
| R1 | [CISA/Treasury/FBI/USCYBERCOM AA20-239A](https://content.govdelivery.com/accounts/USDHSCISA/bulletins/29bf7dc), August 26, 2020 | Government notification containing composite campaign, tools and technical behavior; government attribution, not independent attribution by this analyst |
| R2 | [CISA FASTCash 2.0 PDF](https://www.cisa.gov/sites/default/files/publications/AA20-239A_FASTCash2.0_508.pdf), August 26, 2020 | Campaign timeline/expansion; same advisory as R1, not a second independent source |
| R3 | [MITRE G0082](https://attack.mitre.org/groups/G0082/), page version 4.0 / modified October 9, 2026 | Actor terminology, overlap, ATT&CK technique names; curated knowledge base |
| R4 | [haxrob FASTCash for Linux](https://haxrob.net/linux/fastcash-for-linux/), October 13, 2024 | Primary technical researcher, symbols/control flow and published reverse-engineering evidence; not independent specimen verification here |
| R5 | [FortiGuard Labs technical summary](https://www.fortinet.com/blog/threat-research/joint-technical-alert-fastcash-2-0-north-koreas-beagleboyz-robbing-banks), August 27, 2020 | Windows hooks/configuration comparison; partly summarizes government MAR, so not fully independent operational corroboration |
| R6 | [Chrome release notice](https://chromereleases.googleblog.com/2023/09/stable-channel-update-for-desktop_11.html), September 11, 2023 | Primary vendor: report date, reporter credit, fixed versions, exploited-in-wild acknowledgement |
| R7 | [Upstream fix 902bc919](https://chromium.googlesource.com/webm/libwebp/+/902bc9190331343b2017211debcec8d2ab87e17a), September 7, 2023 | Primary source change and bug linkage; validates technical root cause |
| R8 | [The WebP 0day](https://blog.isosceles.com/the-webp-0day/), September 2023 | Primary technical research; trigger discussion read but no trigger retrieved/run; speculative Apple connection not adopted as fact |
| R9 | [NVD CVE-2023-4863](https://nvd.nist.gov/vuln/detail/CVE-2023-4863) | Version and KEV cross-check; database enrichment is not independent exploitation observation |
| R10 | [Debian CVE tracker](https://security-tracker.debian.org/tracker/CVE-2023-4863) | Distribution backport/version caveat |
| R11 | [certifi maintainer advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2), October 20, 2026 | Current source corroborates historical trust-root advisory and patched release |
| R12 | [OSV pip record](https://osv.dev/vulnerability/PYSEC-2026-3721), published July 29 / modified September 10, 2026 | Alias/fix/precondition check; links upstream pip change; not exploit execution |

Retrieval limitations retained: CISA `/news-events/analysis-reports/ar18-275a` and `/ar20-239a` returned HTTP 403. A guessed Google Project Zero WebP article and guessed Black Hat paper URL were inaccessible, so neither is evidence. One haxrob image link returned cache miss; textual technical sections were accessible. No inaccessible page content was invented. Searches also returned secondary news and mirrors; they were discovery aids, not the report's technical authority.

Local reuse (hashes in the dated source-hashes JSON): official tasks PDF; original CT+V 1 APT scenario, k.php dossier and vulnerability report; CT+V 2 Assignment 2 assessment/raw advisory JSON; canonical requirements/source/test code; Week 11 isolated security and Pulse results. Original coursework remains in place. Text extraction files are derived reading evidence, not new reverse-engineering outputs or independent sources.
