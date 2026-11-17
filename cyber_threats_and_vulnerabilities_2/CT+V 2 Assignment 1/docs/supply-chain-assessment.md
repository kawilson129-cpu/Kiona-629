# DeRexi software supply-chain assessment

Assessment date: November 17, 2026. Scope is the canonical repository, its Windows virtual-environment distribution metadata and referenced prior evidence. No application import, network probe, credential read, backend change or dependency install was needed. The fictional business context is policy integrity and incident routing at Aurum Capital Bank; this is not an audit of a real bank.

## Inventory and dependency relationships

The collector reads `METADATA`, `INSTALLER` and presence of `RECORD`/`direct_url.json`, retaining declared `Requires-Dist` relationships and metadata SHA-256. It found **37 installed distributions**, compared with 35 in the November 9 Assignment 2 snapshot. A snapshot is not a lockfile, a deployed SBOM, a complete dependency resolver or proof that a distribution is imported at runtime. Extras, platform markers and unused packages remain visible in metadata.

| Direct runtime declaration | Observed installed version | Role |
|---|---|---|
| fastapi >=0.110 | 0.143.0 | API, Starlette/Pydantic integration |
| uvicorn[standard] >=0.29 | 0.54.0 | ASGI server; optional event/network/watch dependencies |
| SQLAlchemy >=2.0 | 2.1.4 | Database ORM |
| psycopg2-binary >=2.9 | 2.9.13 | PostgreSQL driver / native binary trust |
| pydantic >=2.6 | 2.14.0 | Input/schema validation, compiled core dependency |
| python-dotenv >=1.0 | 1.2.4 | Local configuration loading |
| openai >=1.30 | 3.26.1 | Compatible AI-provider client, HTTP/TLS dependencies |
| PyJWT[crypto] >=2.10 | 2.15.1 | Signed identity, cryptography dependencies |
| pypdf >=6.19,<7 | 6.21.4 | Document intake |
| defusedxml >=0.7.1,<1 | 0.7.1 | XML safety support |

Development declarations add httpx >=0.27 and cryptography >=42.0; installed versions are 0.28.1 and 50.0.2. This is not an exclusive runtime/dev partition because runtime extras can require the same package. Full direct/transitive/installed-tool inventory and declared relationship strings are in the [dated inventory](../evidence/index.md). Notable transitive layers include Starlette/AnyIO, pydantic_core, HTTPX/httpcore/h11, certifi, cffi and native parser/driver components. Installed httpx2/httpcore2 and pip are inventoried without claiming that application requests use them.

## Provenance, distribution and trust boundaries

Repository requirements use broad lower bounds and some major-version caps, with no complete reviewed version/hash lock. `INSTALLER` reports installation tooling; `RECORD` presence is an integrity metadata signal, not a verified publisher signature. Local metadata hashes enable later drift checks but cannot prove the original index, artifact authenticity or build-chain integrity. Original wheel hashes, signed attestations, source-to-build traceability and a deployed image digest were not established.

```text
maintainer/source -> package registry/wheel/build -> local Python environment
browser + external font hosts -> DeRexi HTTP/API -> authorization -> PostgreSQL/Supabase
uploaded documents -> bounded parser -> reviewed policy workflow
government feeds -> Pulse normalization/source checks -> proposed policy action
optional compatible AI endpoint -> advisory answer/classification -> human workflow
optional SMTP -> approved routing recipient -> external delivery/ticket workflow
```

| Third party / boundary | What crosses it | Risk and observed control / missing evidence |
|---|---|---|
| Package ecosystem / native wheels | Executable dependency code into server | Arbitrary install/build code, dependency confusion and compromised maintainer; original artifact provenance unverified |
| Supabase/PostgreSQL and Auth | Policy, user, incident data; JWT/JWKS and database traffic | Backend privileged connection makes application authorization critical; live ACL/RLS/TLS readiness is not proven by local metadata |
| Optional AI providers | Context sent through OpenAI-compatible client; Groq/OpenRouter references in ai.py | Privacy, provider availability and untrusted output; actual enabled provider/model/retention not inspected |
| Public regulatory publishers | RSS/XML/JSON and article links into Pulse | Source spoofing/parser risk; current service.py checks exact configured article hosts and FDIC tenant paths; redirects and upstream compromise still need validation |
| Google Fonts | Browser requests to fonts.googleapis.com/fonts.gstatic.com | External availability/privacy and remote stylesheet trust; no self-hosted asset assurance claimed |
| Document intake | Employee-provided DOCX/PDF to parser | Resource exhaustion/malformed documents; preserve parser sandbox/limits and keep parser advisories under review |
| SMTP / downstream ticketing | Confirmed incident summary to approved recipients | Wrong destination/provider compromise; existing routing controls need real delivery acceptance, not assumed from SMTP success |
| Repository / CI / container base | Source and build configuration into release | Review workflow, action pinning and image/OS packages need separate provenance and deployed inventory; not covered by Python metadata |

Source inspection references: [requirements](../../../derexi-policy-pilot/requirements.txt), [AI](../../../derexi-policy-pilot/backend/ai.py), [Pulse sources](../../../derexi-policy-pilot/backend/pulse/sources.py), [source-host validation](../../../derexi-policy-pilot/backend/pulse/service.py), [security boundary](../../../derexi-policy-pilot/backend/security.py), [frontend external assets](../../../derexi-policy-pilot/backend/static/index.html). No `.env` values were read.

## Advisory applicability and prior finding reconciliation

Historical [Assignment 2 release-specific advisory responses](../../CT+V%202%20Assignment%202/closure/advisories/assessment.json) were matched by exact installed name/version. Both matches persist in the current metadata. Four registry records represent **two issues**, not four independent vulnerabilities. The current browser research also checked these advisory records; no fresh full-environment advisory scan is claimed.

| Issue | Current applicability evidence | Qualification and treatment |
|---|---|---|
| certifi GHSA-6q48-6c7w-9gw2 / PYSEC-2026-4320 | Local certifi 2026.7.22 equals prior matched version; upstream identifies a trust-root removal in 2026.10.18 | Affected-version match; actual client trust-store selection, compromised-chain acceptance and on-path position not tested. Review upgrade to supported release containing removal and run TLS compatibility checks. [Maintainer advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2) |
| pip CVE-2026-13346 / GHSA-qwm4-qh6w-59xr / PYSEC-2026-3721 | Local pip 26.1.2 equals prior matched version; fixed at 26.2 | Requires malicious index URL handling during package operations; not proof of API exploitability. Review tooling upgrade, approved index and artifact validation. [OSV record](https://osv.dev/vulnerability/PYSEC-2026-3721) |
| Historical unguarded policy writes | Assignment 2 had four failed negative requests | Later [security evidence](../../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/security-results.json) records 88 passing isolated checks; current main.py has identity/role dependencies. Do not assert the November 9 failure is current or mark production closure without a relevant retest |
| Historical FDIC source-host spoof | Assignment 2 accepted unrelated host | Later [Pulse evidence](../../../semester_5/DeRexi_Week%2011/evidence/final-integration-20261112/pulse-results.json) records 97 passing isolated checks; current source binds hosts/tenant path. No live publisher integrity proof |
| Version drift / lock | Current requirements still use lower bounds | Still applicable reproducibility finding; package snapshot does not resolve it |
| Historical classroom SSH exposure | CT+V 1 host 10.11.2.144 had TCP/22 open, no confirmed target-specific CVE | Different authorized classroom host; not the current DeRexi server or an OS advisory match |

No newly discovered CVE is assigned to every package with an empty historical advisory list. The extra pypdf/defusedxml packages and all 37 current versions need a fresh comprehensive advisory review before release. The supplied records and this targeted comparison cannot certify vulnerability absence.

## Risk scoring and remediation priorities

Method: analyst-estimated likelihood (1 rare–5 likely) × business impact (1 negligible–5 severe); 1–4 Low, 5–9 Medium, 10–16 High, 17–25 Critical. This is a local decision scale, not CVSS or a measured probability. Scores assume Aurum's policy integrity matters to incident escalation. Owners and deadlines below are proposals from acceptance of findings, not approved commitments.

| Priority / finding | L × I | Reason / status | Proposed owner, target and closure evidence |
|---|---|---|---|
| P1: production authorization/DB boundary assurance | 3×5=15 High | Privileged backend and historical live-readiness gaps; current deployed effectiveness BLOCKED | Platform + security, before activation: scoped production identities, ACL/RLS/TLS acceptance and negative role tests |
| P1: certifi affected-version match | 3×4=12 High | TLS trust relevant, exploit prerequisites unverified; OPEN | Platform, 7 days: reviewed update, actual trust-store evidence and benign endpoint TLS regression |
| P1: unreviewed artifact provenance | 3×4=12 High | Python/native artifacts become server code; provenance BLOCKED | Release engineering, before release: approved index, hashes/attestations where available, clean isolated build |
| P2: no complete hash lock | 3×3=9 Medium | Repeatability gap directly observed; OPEN | Platform, 14 days: reviewed resolved dependency graph and hash-locked clean install/test |
| P2: pip affected-version match | 2×3=6 Medium | Installation-time malicious-index condition, not request-time RCE; OPEN | Developer tooling, 14 days: approved pip update/index policy and package workflow validation |
| P2: external context/feed/font/service trust | 2×4=8 Medium | Content, data egress and availability exposure; PARTIAL | Service owners, 30 days: provider data-flow review, feed/redirect fixtures, font hosting decision and vendor incident process |

Immediate recommendations do not authorize changes in this assignment. Maintain a dependency owner, weekly advisory review and release-time rescans, alias deduplication, signed source review and tested recovery to the previous approved build. Avoid blanket upgrades without compatibility testing. Compare deployed SBOM with the lock; retain artifact digests, build logs and exceptions with expiration.

## Results and limits

Collector outcomes: **3 PASS / 3 FAIL / 3 BLOCKED**. PASS includes successful inventory and inspection of two prior result records; those are not 185 newly executed application tests. FAIL records the unresolved lock and two affected-version conditions. BLOCKED records live verification, original malware sample work and provenance. The reports remain valid even when controls fail. See [implementation](implementation.md) and [evidence index](../evidence/index.md).
