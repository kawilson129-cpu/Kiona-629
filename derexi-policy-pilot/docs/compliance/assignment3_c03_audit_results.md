# Compliance 1 — Assignment 3: C-03 Control Audit Results

**Project:** DeRexi: Policy Pilot — Aurum Capital Bank
**Control under test:** C-03 Regulatory Feed Integrity and Source Validation
**Feature assessed:** DeRexi Pulse (public, read-only regulatory intelligence feed)
**Audit date:** 3 November 2026
**Commit tested:** `95163d7` (branch `main`)
**Control owner / auditor role:** Security / Technical Lead
**Result:** C-03 **PARTIALLY VERIFIED** — 54 of 55 audit checks pass, 1 fails.
The pre-existing Pulse suite also passes in full: 97/97 offline and 109/109 with live
endpoints. The partial verdict is caused by one reproducible gap: a feed item's link is
never bound to the host of the source it is attributed to (finding F-03-01).

---

## 1. Audit date and environment

| Item | Value |
| --- | --- |
| Audit date | 3 November 2026 |
| Host | macOS 26.3.1 (arm64), local development machine |
| Python | 3.9.6 (`derexi-policy-pilot/.venv`) |
| FastAPI / Starlette | 0.128.8 / 0.49.3 |
| Pydantic | 2.13.5 |
| SQLAlchemy | 2.0.54 |
| HTTP client (tests) | httpx 0.28.1 (FastAPI `TestClient`) |
| Backend entry point | `derexi-policy-pilot/backend/main.py` |
| Pulse modules under test | `pulse/sources.py`, `pulse/service.py`, `pulse/routes.py` |
| Live Supabase data touched | **None** |
| Packages installed | **None** |
| Application code changed | **None** (one new test file only) |

### How isolation and safety were enforced

1. **Synthetic fixtures only for hostile input.** Every malformed, spoofed, or
   hostile payload in this audit was constructed in
   `backend/tests/test_c03_audit.py` and served by replacing
   `service.fetch_source` in-process. No hostile payload was ever sent to
   `federalregister.gov`, `fdic.gov`, `csrc.nist.gov`, or
   `federalreserve.gov`.
2. **Read-only live checks.** The live pass issued ordinary `GET` requests for
   the four published feeds (the same requests the running application makes)
   plus one `HEAD` request on a public FDIC bulletin link to confirm where that
   link resolves. Nothing was submitted, posted, or modified.
3. **No database contact.** Pulse never reads or writes Supabase; the audit
   suite imports only `main`, `pulse.service`, and `pulse.sources`. No
   connection string was read, no migration run, no RLS policy or grant
   changed, and no user, incident, policy, or feedback record was touched.
4. **No authentication surface touched.** `auth.py`, roles, personas, and
   permissions were not modified or exercised. C-01 and C-02 were not
   re-assessed.
5. **Fetcher restored.** `service.fetch_source` and the module cache are
   restored in a `finally` block so the suite leaves the process as it found it.

### What "live" means here

The live pass is a read-only reachability and shape check of four public
endpoints. It is not a legal verification of any document and not a
substitute for the agencies' own publication records. Results reflect what the
agencies happened to be publishing on 3 November 2026 (81 normalized items
across the four feeds).

---

## 2. Audit objective and scope

### Objective

Determine, on the basis of executed tests, whether DeRexi Pulse satisfies
control C-03: that regulatory information it displays comes only from
configured sources, is normalized safely, and preserves accurate source
attribution and document classification.

### In scope

| # | Requirement tested |
| --- | --- |
| 1 | Only configured regulatory sources are fetched |
| 2 | Source names and original links are preserved |
| 3 | Unsafe URLs are rejected |
| 4 | Malformed HTML, JavaScript URLs, and invalid feed records cannot inject executable content |
| 5 | Invalid dates do not appear as valid dates |
| 6 | Duplicate records are removed |
| 7 | Classification follows documented source metadata and conservative rules |
| 8 | A failed source does not prevent healthy feeds from rendering |
| 9 | Stale results are clearly identified |
| 10 | Invalid API `limit` values return HTTP 422 |
| 11 | Failed or empty feeds do not create fabricated regulatory articles |

### Out of scope

* C-01 (Role-Based Access Control) and C-02 (Input Validation and Safe Error
  Handling). Their reports are unchanged and were not re-run.
* Any determination of GLBA compliance. C-03 is one technical control and
  cannot establish institutional compliance on its own.
* Legal or factual verification of an agency publication's content. Pulse
  displays what an agency publishes; it does not attest that the publication
  is accurate, current, or applicable to Aurum Capital Bank.
* Authentication, authorization, database schema, migrations, RLS, personas,
  and Pulse visual design. None were touched.
* Load, performance, penetration, or fuzz testing.

---

## 3. Control C-03 and NIST CSF 2.0 mapping

### 3.1 Control definition

| Field | Value |
| --- | --- |
| Control ID | **C-03** |
| Control name | Regulatory Feed Integrity and Source Validation |
| Control objective | Ensure regulatory information displayed by DeRexi Pulse comes from configured sources, is normalized safely, and maintains accurate source attribution and document classification. |
| Control owner | Security / Technical Lead |
| Business process | Regulatory intelligence monitoring |
| Framework | NIST Cybersecurity Framework (CSF) 2.0 |
| Implementation | `pulse/sources.py` (closed registry, HTTPS endpoints, size/time limits), `pulse/service.py` (normalization, validation, classification, cache), `pulse/routes.py` (public read-only API with bounded `limit`), `static/pulse.js` (text-only rendering) |
| Evidence of operation | 55 audit checks (this report) + 97 offline and 109 live checks in `tests/test_pulse.py` |

### 3.2 What the control does and does not claim

**Does:** restricts ingestion to four hard-coded government sources, rejects
non-HTTPS and malformed links, strips markup from text fields, refuses
impossible dates, removes duplicates, constrains category and status values to
documented allow-lists, isolates per-source failures, flags stale cache, bounds
the API parameter, and never invents an article when a feed fails or is empty.

**Does not:** establish GLBA compliance; verify the authenticity, legality, or
accuracy of an agency publication; detect a compromised upstream agency or a
DNS/TLS interception; cryptographically sign or verify feed content; or replace
human editorial review of regulatory obligations.

### 3.3 NIST CSF 2.0 mapping

Subcategory outcomes below are paraphrased from the CSF 2.0 Core. Each row
states which C-03 requirements and checks support it, and what it does not
prove.

| Subcategory | CSF 2.0 outcome (paraphrased) | Why it applies to C-03 | Supported by | Not shown by this evidence |
| --- | --- | --- | --- | --- |
| **ID.AM-04** | Inventories of suppliers' services are maintained. | The four feeds are third-party information services. `SOURCES` is their inventory, and the public API accepts no caller-selected source or URL. | C03-01 to C03-04 | Nothing about the agencies' own service inventory or contractual terms. |
| **GV.SC-07** | Risks from suppliers and their services are understood, recorded, prioritized, assessed, responded to, and monitored across the relationship. | Runtime monitoring of each information supplier: per-source status, failure isolation, stale flagging, health endpoint, and no silent substitution of content. | C03-38 to C03-43, C03-49 to C03-53 | No due-diligence, contractual, or periodic-review evidence; monitoring is runtime only. |
| **PR.DS-02** | The confidentiality, integrity, and availability of data in transit are protected. | All four endpoints are HTTPS; every link rendered must be `https`; `http`, `data:`, `javascript:`, credential-bearing, and relative URLs are rejected. | C03-09 to C03-16, C03-19; live check "URLs are https" | Transport protection only. No certificate pinning, no content signature verification. |
| **PR.DS-06** | Integrity-checking mechanisms verify the integrity of information. | Dates, links, record shape, duplicates, categories, and statuses are validated before display; unsafe or malformed records are dropped rather than repaired. | C03-17 to C03-37, C03-50 to C03-53 | Checks internal consistency of the feed record, not whether the agency's document is authentic or legally accurate. |
| **PR.DS-10** | The confidentiality, integrity, and availability of data in use are protected. | Feed-derived text must remain inert when displayed. Text is normalized to plain text and the UI writes it with `textContent`. | C03-17 to C03-21 and prior browser evidence C03-55 | Browser behaviour was not re-executed in this audit; it rests on prior evidence plus source inspection. |

---

## 4. Methodology and test commands

### Phase A — review of existing evidence (no execution)

The prior Pulse package was read before anything was run:
`derexi-policy-pilot/docs/compliance-assignment-2/README.md`,
`integration-notes.md`, `testing-results.md`, `phase-3-editorial-mosaic.md`,
and `phase-3-browser-results.json`. Each of the 11 requirements was mapped to
existing coverage; only genuinely uncovered behaviour was added. The prior
package reported 76 checks on 2 November; the suite has since grown to 97
offline checks, so it was re-executed rather than cited from the old count.

### Phase B — re-execution of the standing suite

```bash
cd derexi-policy-pilot/backend

# Offline: synthetic payloads, no network, no database
../.venv/bin/python tests/test_pulse.py \
  > ../../docs/compliance/evidence/c03_pulse_suite_offline_2026-11-03.txt 2>&1

# Live: read-only GETs against the four published feeds
../.venv/bin/python tests/test_pulse.py --live \
  > ../../docs/compliance/evidence/c03_pulse_suite_live_2026-11-03.txt 2>&1
```

### Phase C — new C-03 audit checks

```bash
cd derexi-policy-pilot/backend

../.venv/bin/python tests/test_c03_audit.py \
  > ../../docs/compliance/evidence/c03_audit_checks_2026-11-03.txt 2>&1
# exits 1 while C03-54 fails, by design
```

The file is additive: `tests/test_pulse.py` was not edited, so the established
suite keeps its original meaning and history. The new file writes
`docs/compliance/evidence/c03_audit_results.json` on every run.

### Status definitions

| Status | Meaning |
| --- | --- |
| **PASS** | The observed behaviour met the stated expectation in an executed check, or (for C03-55 only) in preserved prior evidence. |
| **FAIL** | The observed behaviour did not meet the expectation. A FAIL describes the application, not a broken test. |
| **BLOCKED** | The check could not be executed for an environmental reason. |
| **NOT TESTED** | Deliberately excluded; the reason is recorded. |

### Evidence basis

Two bases are distinguished throughout:

* **This audit** — executed on 3 November 2026; console output is preserved in
  `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt`.
* **Prior (2026-11-02)** — preserved browser evidence from the Phase 3 run, not
  re-executed. Exactly one check (C03-55) has this basis.

No check is marked PASS on the basis of code reading alone. Source inspection is
used only as supporting context and is labelled as such.

---

## 5. Evidence inventory

| File | Contents | Basis |
| --- | --- | --- |
| `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` | Full console output of the 55 C-03 audit checks, including the failing assertion detail | Executed 2026-11-03 |
| `docs/compliance/evidence/c03_audit_results.json` | Machine-readable record of all 55 checks: id, requirement, procedure, expected, actual, status, evidence basis, evidence path, plus run summary | Produced by the run |
| `docs/compliance/evidence/c03_pulse_suite_offline_2026-11-03.txt` | Standing Pulse suite, offline: 97 passed, 0 failed | Executed 2026-11-03 |
| `docs/compliance/evidence/c03_pulse_suite_live_2026-11-03.txt` | Standing Pulse suite with live endpoints: 109 passed, 0 failed, plus per-source counts | Executed 2026-11-03 |
| `docs/compliance/evidence/c03_live_link_hosts_2026-11-03.txt` | Read-only link-host distribution per source, with one `HEAD` check on an FDIC bulletin link | Executed 2026-11-03 |
| `derexi-policy-pilot/backend/tests/test_c03_audit.py` | The 55-check audit suite (re-runnable, isolated, exits non-zero on failure) | New in this audit |
| `derexi-policy-pilot/backend/tests/test_pulse.py` | Standing suite, re-run unchanged | Pre-existing |
| `derexi-policy-pilot/docs/compliance-assignment-2/testing-results.md` | Prior results, including the §4 browser XSS row | Prior, 2026-11-02 |
| `derexi-policy-pilot/docs/compliance-assignment-2/phase-3-browser-results.json` | Prior browser run detail supporting C03-55 | Prior, 2026-11-02 |

No prior evidence file was modified, moved, or deleted.

---

## 6. Detailed results

### 6.1 Totals

| Suite | Checks | Passed | Failed | Blocked / not tested |
| --- | --- | --- | --- | --- |
| C-03 audit (this assessment) | 55 | **54** | **1** | 0 / 0 |
| Standing Pulse suite — offline | 97 | 97 | 0 | 0 / 0 |
| Standing Pulse suite — live | 109 | 109 | 0 | 0 / 0 |

The audit suite's single failure is C03-54, which is a real gap in the
application and is reported as finding F-03-01. Of the 54 passes, 53 were
executed today and 1 (C03-55) rests on preserved prior browser evidence.

### 6.2 Result by control requirement

| Req | Requirement | Checks | Pass | Fail | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | Only configured sources are fetched | C03-01 to C03-04 | 4 | 0 | **Met** |
| 2 | Source names and original links are preserved | C03-05 to C03-08, C03-54 | 4 | 1 | **Partial** |
| 3 | Unsafe URLs are rejected | C03-09 to C03-16 | 8 | 0 | **Met** |
| 4 | Hostile content cannot execute | C03-17 to C03-21, C03-55 | 6 | 0 | **Met** |
| 5 | Invalid dates are not shown as valid | C03-22 to C03-27 | 6 | 0 | **Met** |
| 6 | Duplicate records are removed | C03-28 to C03-31 | 4 | 0 | **Met** |
| 7 | Classification is documented and conservative | C03-32 to C03-37 | 6 | 0 | **Met** |
| 8 | One failed source does not block healthy feeds | C03-38, C03-39 | 2 | 0 | **Met** |
| 9 | Stale results are clearly identified | C03-40 to C03-43 | 4 | 0 | **Met** |
| 10 | Invalid `limit` values return 422 | C03-44 to C03-49 | 6 | 0 | **Met** |
| 11 | No fabricated articles | C03-50 to C03-53 | 4 | 0 | **Met** |
| | **Total** | **55** | **54** | **1** | **10 of 11 requirements met; 1 partial** |

### 6.3 Full results table

`PASS*` marks the one check supported by prior evidence rather than re-executed
today.

| Test ID | Req | Test procedure | Expected result | Actual result | Status | Evidence basis | Evidence path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C03-01 | 1 | Registry contains exactly the four documented government sources | {'Federal Register', 'FDIC', 'NIST', 'Federal Reserve'} | registry keys: ['FDIC', 'Federal Register', 'Federal Reserve', 'NIST'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-02 | 1 | fetch_source refuses a name outside the registry | ValueError('Unknown Pulse source: ...') | Unknown Pulse source: Unlisted Source | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-03 | 1 | A feed build requests only registry names | exactly the four registry keys, no other request | requested: ['FDIC', 'Federal Register', 'Federal Reserve', 'NIST'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-04 | 1 | Public feed endpoint exposes no caller-selected source or URL | only the 'limit' parameter | parameters: ['limit'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-05 | 2 | Source name is preserved exactly as configured | source == 'Federal Register' | source='Federal Register' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-06 | 2 | Original publication link is preserved (fragment removed only) | https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule?a=1&b=2 | url='https://www.federalregister.gov/documents/2026/10/30/2026-12345/rule?a=1&b=2' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-07 | 2 | Co-issuing agencies named by the source are retained | agency mentions Federal Reserve System and FDIC | agency='Federal Reserve System, FDIC' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-08 | 2 | Agency falls back to the registry when the feed omits one | agency == 'Federal Deposit Insurance Corporation' | agency='Federal Deposit Insurance Corporation' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-54 | 2 | A link on a host unrelated to the claimed source is rejected or flagged | rejected, or labelled with a different host so attribution cannot be spoofed | accepted as source='FDIC' with url='https://secure-fdic-verification.example/login' | **FAIL** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-09 | 3 | plain http is rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-10 | 3 | javascript: is rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-11 | 3 | data: is rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-12 | 3 | embedded credentials are rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-13 | 3 | protocol-relative and relative links are rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-14 | 3 | a host without a dot is rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-15 | 3 | A relative link alone is rejected | empty string | safe_url -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-16 | 3 | A record whose only link is unsafe is dropped, not rendered | make_article returns None | returned None | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-17 | 4 | Literal script and img tags are removed from text fields | no '<script', no '<img', no 'onerror=' | t1='alert(1) Lost laptop reported' t2='Phishing email received' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-18 | 4 | Event-handler attributes cannot survive into a summary | summary contains no 'onclick=' and no '<p ' | summary='Real body copy about a ransomware incident.' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-19 | 4 | A javascript: document link is dropped while its sibling survives | 1 article, https only | 1 article(s), urls=['https://www.federalregister.gov/documents/2'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-20 | 4 | Entity-encoded markup is emitted as text, not parsed into a tag server-side | no HTML parsing occurs; the string stays inert JSON content | returned text='Notice <img src=x onerror=alert(1)>'; renderer safety covered by C03-55 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-21 | 4 | Malformed records are skipped without discarding valid siblings | exactly 1 article survives | 1 article(s) | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-55 | 4 | A hostile feed payload is executed in the browser without injecting content | no injected nodes, no javascript: href, no alert | Phase 3 browser run: stub article with <img onerror>, <script>, javascript: URL produced no injected nodes and no javascript: link; markup rendered as text | **PASS\*** | Prior (2026-11-02) | `derexi-policy-pilot/docs/compliance-assignment-2/testing-results.md` §4; `phase-3-browser-results.json` |
| C03-22 | 5 | Invalid date (month 13) is not shown as valid | empty string | parse_date('2026-13-45') -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-23 | 5 | Invalid date (31 February) is not shown as valid | empty string | parse_date('2026-02-30') -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-24 | 5 | Invalid date (free text) is not shown as valid | empty string | parse_date('not a date') -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-25 | 5 | Invalid date (empty value) is not shown as valid | empty string | parse_date('') -> '' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-26 | 5 | An impossible date becomes an empty published field, not a guess | published == '' | published='' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-27 | 5 | A valid RFC 822 date is still normalized to ISO | 2026-10-30 | parse_date -> '2026-10-30' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-28 | 6 | Identical URLs are collapsed to one article | one 'Repeated bulletin' article | count=1 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-29 | 6 | Same-source, same-day duplicate headlines are collapsed | one 'Duplicate press release' article | count=1 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-30 | 6 | Distinct records are not over-collapsed | the different-day headline is retained | titles=['Repeated bulletin', 'Duplicate press release', 'Same headline, different day'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-31 | 6 | total_normalized reports the de-duplicated count | total_normalized equals len(articles) when under the limit | 3 vs 3 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-32 | 7 | Federal Register document type is treated as source-declared metadata | classified_by == 'source' for both articles | classified_by=['source', 'source'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-33 | 7 | Presidential documents are reported as Notices, not rules | status == 'Notice' | status='Notice' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-34 | 7 | Body-only mention of 'guidance' does not reclassify a press release | status == 'General News' | status='General News' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-35 | 7 | A guidance headline is classified as supervisory guidance | status == 'Supervisory Guidance' | status='Supervisory Guidance' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-36 | 7 | Inferred classifications are labelled as inferred | classified_by == 'inferred' for RSS press releases | classified_by=['inferred', 'inferred'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-37 | 7 | Every emitted category and status is inside the documented allow-list | category in CATEGORIES and status in DOCUMENT_STATUSES | categories=['Banking & Finance', 'Regulations', 'Supervisory Guidance'] statuses=['Final Rule', 'General News', 'Notice', 'Supervisory Guidance'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-38 | 8 | A failing source is reported without breaking the request | HTTP-equivalent response with sources[FDIC].ok == False | ok=False error='OSError' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-39 | 8 | Healthy sources still report ok while one source fails | Federal Register, NIST, Federal Reserve ok == True | statuses={'Federal Register': True, 'FDIC': False, 'NIST': True, 'Federal Reserve': True} | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-40 | 9 | A failure with no cached copy is not labelled stale | stale == False and count == 0 | stale=False count=0 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-41 | 9 | An expired cache refresh failure is explicitly flagged stale | stale == True, ok == False, error set | stale=True ok=False error='Timed out' | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-42 | 9 | Stale articles are the last good copies, not invented replacements | the cached release is still present and unchanged | titles=['Cached FDIC release'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-43 | 9 | A stale source does not mark healthy sources stale | other sources ok == True and stale absent/false | statuses={'Federal Register': (True, None), 'FDIC': (False, True), 'NIST': (True, None), 'Federal Reserve': (True, None)} | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-44 | 10 | limit zero (limit=0) is rejected with 422 | HTTP 422 | HTTP 422 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-45 | 10 | limit above maximum (limit=61) is rejected with 422 | HTTP 422 | HTTP 422 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-46 | 10 | limit non-numeric (limit=abc) is rejected with 422 | HTTP 422 | HTTP 422 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-47 | 10 | limit negative (limit=-3) is rejected with 422 | HTTP 422 | HTTP 422 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-48 | 10 | A valid limit still returns 200 and honours the cap | HTTP 200 and at most 1 article | HTTP 200, articles=1 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-49 | 10 | Health endpoint reports the configured sources without fetching | HTTP 200 and the four registry names | HTTP 200, sources=['Federal Register', 'FDIC', 'NIST', 'Federal Reserve'] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-50 | 11 | Total upstream failure yields zero articles | articles == [] and total_normalized == 0 | articles=0 total=0 | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-51 | 11 | Total upstream failure is reported per source, not as a crash | all four sources ok == False with an error string | statuses={'Federal Register': (False, 'OSError'), 'FDIC': (False, 'OSError'), 'NIST': (False, 'Unreadable feed'), 'Federal Reserve': (False, 'Unreadable feed')} | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-52 | 11 | No radar prompts are invented when nothing loaded | radar == [] | radar=[] | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |
| C03-53 | 11 | Empty feeds are not errors and produce no placeholder articles | articles == [] and every source ok == True | articles=0 ok={'Federal Register': True, 'FDIC': True, 'NIST': True, 'Federal Reserve': True} | **PASS** | This audit | `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` |

### 6.4 Standing suite coverage (re-executed today)

The pre-existing suite was not rewritten. Its 97 offline checks were re-run and
grouped as follows; the live pass adds 12 checks on real feed data.

| Group | Checks | C-03 relevance |
| --- | --- | --- |
| `[dates]` | 11 | Requirement 5 — RFC 822, ISO, month-name, empty, `None`, garbage, and impossible dates |
| `[text]` | 11 | Requirements 3 and 4 — tag stripping, entity handling, `safe_url` scheme/credential rejection, summary hygiene |
| `[classification]` | 16 | Requirement 7 — Federal Register document types, NIST drafts, FDIC headline versus body-only signals, Fed press releases |
| `[normalize]` | 25 | Requirements 2, 3, 4 and 7 — per-source field mapping, missing fields, malformed records, agency and link handling |
| `[feed]` | 20 | Requirements 1, 6, 8, 9 and 11 — de-duplication, ordering, per-source failure isolation, cache behaviour, limit clamping, radar derivation |
| `[ranking]` | 7 | Supporting only — editorial ordering; not a C-03 requirement |
| `[radar]` | 7 | Requirement 11 — prompts are derived from loaded articles, never invented |
| `[live]` | 12 | Requirements 1, 2, 3, 5 and 7 on real data — reachability, https URLs, ISO dates, plain text, known categories and statuses, ordering |

**Live pass detail (3 November 2026):**

| Source | Items normalized | ok |
| --- | --- | --- |
| Federal Register | 34 | true |
| FDIC | 25 | true |
| NIST | 7 | true |
| Federal Reserve | 15 | true |
| **Total** | **81** | all reachable |

The combined feed returned 60 articles (the `MAX_ARTICLES` cap). Categories:
Banking & Finance 29, Regulations 23, Cybersecurity 3, Privacy & Data
Protection 3, Supervisory Guidance 2. Statuses: Proposed Rule 15, Final Rule 8,
Notice 11, Supervisory Guidance 2, Standards Draft 4, General News 20. Every
value was inside the documented allow-lists, every URL was `https`, every date
was ISO or empty, and every title and summary was plain text.

### 6.5 Prior evidence versus tests executed in this assessment

| Evidence | Date | What it establishes | C-03 use | Re-executed? |
| --- | --- | --- | --- | --- |
| Phase 3 browser run (XSS row, `phase-3-browser-results.json`) | 2026-11-02 | A stub article carrying `<img onerror>`, `<script>`, and a `javascript:` URL produced no injected nodes and no `javascript:` link; markup rendered as inert text | C03-55 (Requirement 4) | **No** — recorded as prior evidence |
| Standing suite, 76 checks | 2026-11-02 | Baseline reported in `testing-results.md` | Context only | Superseded by today's 97-check run |
| Standing suite, 97 / 109 checks | 2026-11-03 | All normalization, classification, dedupe, failure-isolation and live checks still pass on the current commit | Requirements 1–11 | **Yes** |
| 54 new audit checks | 2026-11-03 | Registry closure, attribution, hostile fixtures, stale flagging, API validation, total-failure behaviour | Requirements 1–11 | **Yes** |

The 2 November report recorded 76 checks; the suite now contains 97 offline
checks because editorial ranking and radar checks were added during the Phase 3
work. The old count was therefore not restated — the current suite was executed
and its output preserved.

### 6.6 Supporting observations (not counted as C-03 checks)

These were inspected to interpret the results. They are not PASS rows.

1. **Link-host distribution on live data.** Each feed currently emits links on a
   single host: Federal Register 34/34 on `www.federalregister.gov`, FDIC 25/25
   on `content.govdelivery.com`, NIST 7/7 on `csrc.nist.gov`, Federal Reserve
   15/15 on `www.federalreserve.gov`. A `HEAD` request to the first FDIC
   bulletin returned HTTP 200 with no redirect
   (`docs/compliance/evidence/c03_live_link_hosts_2026-11-03.txt`). This is upstream behaviour,
   **not** enforcement in Pulse — C03-54 shows the code would accept any host.
2. **Renderer contract.** `static/pulse.js` writes feed text with `textContent`
   (13 call sites). `innerHTML` appears only to clear a container
   (`body.innerHTML = ''`, three sites) or to insert constant markup — the two
   `html:` call sites pass fixed labels plus a constant arrow, never feed data
   (`static/pulse.js` lines 255–268, 325–336). This is source inspection
   supporting C03-55, not a new browser test.
3. **Stale labelling in the UI.** The feed-status strip appends
   `· showing last good fetch` when `stale` is true
   (`static/pulse.js` line 207), so the API flag from C03-41 has a visible
   counterpart. Not exercised in a browser during this audit.

### 6.7 The failing check in detail

```
FAIL  C03-54  A link on a host unrelated to the claimed source is rejected or flagged
      expected: rejected, or labelled with a different host so attribution cannot be spoofed
      actual:   accepted as source='FDIC' with url='https://secure-fdic-verification.example/login'
```

The fixture is synthetic:

```python
make_article(
    source="FDIC",
    title="FDIC urges immediate action on deposit account limits",
    url="https://secure-fdic-verification.example/login",
    date="2026-10-30",
)
```

`safe_url()` accepted it because it is `https`, has a dotted host, carries no
credentials, and is under 2048 characters. `make_article()` then copied the
`source` value it was given. `.example` is a reserved TLD, so no real site was
contacted and no phishing page exists at that address. The failure is about the
missing binding between label and destination, not about the fixture's
realism.

---

## 7. Findings and severity

| Severity | Meaning in this report |
| --- | --- |
| Critical | Untrusted input can execute or exfiltrate without precondition |
| High | A control objective is defeated in a realistic scenario |
| Medium | A control objective is degraded; exploitation needs an upstream precondition |
| Low | Defence-in-depth weakness with a mitigating control in place |
| Info | Observation, documentation item, or accepted design trade-off |

No fixes were implemented. Everything below is a recommendation awaiting
approval.

### F-03-01 (Medium) — Feed links are not bound to the source they are attributed to

*Evidence: C03-54; `pulse/service.py` `safe_url()` lines 238–256 and
`make_article()` lines 481–518.*

`safe_url()` validates the *shape* of a URL (https, dotted host, no embedded
credentials, length) but never compares the hostname with the configured
source. `make_article()` accepts whatever `source` string it is given and
publishes it unchanged alongside whatever https link arrived. A synthetic FDIC
record pointing at `https://secure-fdic-verification.example/login` was returned
as a normal article with `source: "FDIC"`.

**Impact:** a compromised, hijacked, or carelessly added feed could present a
credential-harvesting link under a trusted agency label. For a bank audience
that is a credible phishing vector, and the label is the part users trust.

**Likelihood:** low — it requires upstream feed compromise or a future
integration mistake, and the current four feeds emit a single host each. That
is why the severity is Medium rather than High.

**Why it matters for the verdict:** Requirement 2 asks that source attribution
be preserved. Preserving the label while accepting an unrelated destination
preserves the appearance of attribution without its substance.

### F-03-02 (Low) — Entity-encoded markup is returned as literal text

*Evidence: C03-20; `clean_text()` lines 182–199.*

`clean_text("Notice &lt;img src=x onerror=alert(1)&gt;")` returns
`Notice <img src=x onerror=alert(1)>`. Stripping runs before entity decoding, so
encoded tags become live-looking text in the JSON payload. Nothing executes
server-side, and the UI writes it with `textContent`, which is why C03-17 to
C03-20 and prior C03-55 all pass. The residual risk is a future change of
renderer, or a second consumer (export, email digest, another client) that
interprets the string as HTML.

**Recommendation:** either decode-then-strip in `clean_text()`, or record the
text-only rendering contract as a tested invariant of the Pulse UI. See
CA-03-03.

### F-03-03 (Low, observation) — Normalization helpers do not validate the source name

*Evidence: source inspection of `make_article()` (line 491:
`meta = SOURCES.get(source, {})`) and `normalize()` (line 625: unknown names
fall through to the RSS branch).*

`make_article()` tolerates an unregistered source name: the agency falls back to
the raw string and the id prefix becomes `pulse-`. `normalize()` treats any
unrecognised name as RSS. This is **not reachable through the HTTP API** — the
feed loop iterates `SOURCES` (proved by C03-03) and the endpoint exposes only
`limit` (C03-04) — so it is a robustness observation, not a vulnerability. It
matters because it is the same missing invariant that produces F-03-01.

### F-03-04 (Info) — FDIC items are hosted on GovDelivery, not fdic.gov

*Evidence: `docs/compliance/evidence/c03_live_link_hosts_2026-11-03.txt`; `pulse/sources.py`
lines 60–67.*

All 25 FDIC items in the live snapshot resolved to
`https://content.govdelivery.com/accounts/USFDIC/bulletins/...`, and a `HEAD`
request returned 200 with no redirect. This is expected: FDIC distributes its
press-release RSS through GovDelivery. It is recorded because any per-source
host allowlist must include `content.govdelivery.com` for FDIC, or legitimate
articles would be discarded. The UI gives no indication that the destination is
a mailing-platform host rather than `fdic.gov`.

### F-03-05 (Info) — RSS classification is heuristic and is labelled as such

*Evidence: C03-32 to C03-37; `classify_status()` and the `classified_by` field.*

Federal Register and NIST statuses come from the source's own document type
(`classified_by: "source"`). FDIC and Federal Reserve statuses are inferred from
headline signals and marked `classified_by: "inferred"`. C03-34 confirms a body
mention of "guidance" does not reclassify a press release, and C03-37 confirms
only allow-listed values are emitted. This is honest and conservative; it is
still a heuristic and should not be read as a legal designation of the
document.

### F-03-06 (Info) — Staleness is flagged per source, not per article

*Evidence: C03-41 to C03-43; `static/pulse.js` line 207.*

When a refresh fails and a cached copy exists, the source is marked
`stale: true`, `ok: false`, with the error string, and the UI appends
`· showing last good fetch` to that source's status. Articles themselves carry
no "as of" timestamp. This meets Requirement 9 as written; the observation is
that a reader who looks only at an article card cannot tell it came from a
stale fetch.

---

## 8. Gap analysis

| Req | Status | Gap | Residual risk |
| --- | --- | --- | --- |
| 1 | Met | None observed. Registry is closed; the API exposes only `limit`; unknown names raise `ValueError`. | A future source added without review would inherit C-03's trust without its own validation. |
| 2 | **Partial** | Labels and links survive normalization (C03-05 to C03-08), but the link's host is never checked against the label (C03-54). | A spoofed or compromised feed item can carry a trusted agency label to an unrelated host (F-03-01). |
| 3 | Met | Scheme, credentials, relative links, and hostless URLs are rejected; a record with only an unsafe link is dropped. | Host allow-listing is a separate concern, tracked under Requirement 2. |
| 4 | Met | Literal tags and handlers are stripped; encoded markup stays text; `javascript:` links are dropped without losing siblings; malformed records are skipped. | Encoded text becomes risky only if the renderer changes (F-03-02). Browser proof is prior evidence, not today's. |
| 5 | Met | Impossible and unparseable dates become `""`; valid formats normalize to ISO. | None observed. Empty date means "not shown", which is the intended behaviour. |
| 6 | Met | Identical URLs and same-source/same-day headlines collapse; distinct records survive; the count reflects the de-duplicated set. | Cross-day syndication of the same release would still appear twice; not required by C-03. |
| 7 | Met | Source-declared types are used where available; inference is conservative, allow-listed, and labelled. | Heuristic labels can occasionally be imprecise (F-03-05), but they are disclosed. |
| 8 | Met | A failing source reports `ok: false` with an error; healthy sources still render; the request does not fail. | None observed. |
| 9 | Met | An expired-cache failure sets `stale: true` with the last good articles and does not mark other sources stale. | Staleness is per source, not per article (F-03-06). |
| 10 | Met | `limit=0`, `61`, `abc`, and `-3` all return 422; a valid limit returns 200; health reports registry names without fetching. | None observed. |
| 11 | Met | Total failure and empty feeds both produce zero articles, zero radar prompts, and per-source status instead of placeholders. | None observed. |

**Summary:** the control is genuinely implemented at the application layer, and
ten of eleven requirements are fully met on the evidence recorded here
(executed today, plus one prior browser check for Requirement 4). The single
systemic gap is trust binding: Pulse verifies that a link is *safe* but not that
it belongs to the source it is filed under. Two hardening items (source-name
assertion, renderer contract) share the same root cause — invariants that hold
today by construction rather than by explicit validation.

---

## 9. Recommended corrective actions

| ID | Action | Addresses | Priority | Verification |
| --- | --- | --- | --- | --- |
| CA-03-01 | Add a per-source host allowlist checked inside `make_article()` (or a new `validate_source_url()`), e.g. `Federal Register: federalregister.gov`, `FDIC: fdic.gov, content.govdelivery.com`, `NIST: csrc.nist.gov`, `Federal Reserve: federalreserve.gov`. Reject the record, or relabel it with the actual host, when the host does not match. | F-03-01, Requirement 2 | High | C03-54 passes; new cases for subdomain matching, `http`, and a lookalike host (`fdic.gov.evil.example`) drop correctly; live feeds still return 34/25/7/15 items. |
| CA-03-02 | Assert `source in SOURCES` at the top of `make_article()` and reject unregistered names in `normalize()` rather than falling through to RSS. | F-03-03 | Medium | A unit check that `make_article(source="Unlisted", ...)` raises or returns `None`; existing 97 checks unchanged. |
| CA-03-03 | Choose one: decode entities before tag stripping in `clean_text()`, or keep the current order and pin the text-only renderer with a regression test that fails if Pulse UI starts assigning feed text to `innerHTML`. | F-03-02 | Medium | Encoded-markup fixture returns no `<img`/`onerror=` text, or a renderer test fails on any `innerHTML` assignment fed by article data. |
| CA-03-04 | Show the destination host on article cards when it differs from the agency's primary domain, and disclose that FDIC items are delivered via GovDelivery. | F-03-01, F-03-04 | Low | Visual check plus a UI assertion for the host label. |
| CA-03-05 | Surface the last-successful-fetch time on stale source status, not just the words "showing last good fetch". | F-03-06 | Low | Stale fixture renders a timestamp derived from `fetched_iso`. |
| CA-03-06 | Fold the 55 audit checks into the standing suite (or CI) once C03-54 is fixed, so the host-allowlist invariant cannot regress. Keep the explicit expected-fail until then. | All | Medium | `test_c03_audit.py` exits 0; `test_pulse.py` still 97/109. |
| CA-03-07 | Record the FDIC GovDelivery dependency and the current per-source hosts in `docs/compliance-assignment-2/integration-notes.md` so a future maintainer does not "fix" the allowlist by removing the FDIC feed. | F-03-04 | Low | Documentation review. |

**Re-test criteria for a VERIFIED verdict:** CA-03-01 merged with a regression
test that fails on an unrelated host; `tests/test_c03_audit.py` reports 55/55;
the standing suite reports 97 offline and 109 live; the live item counts remain
comparable to the 34/25/7/15 baseline.

---

## 10. Testing limitations

1. **No hostile payload was sent to a government endpoint.** Malformed and
   hostile records were exercised only through in-process synthetic fixtures.
   This is deliberate: probing a public agency feed with attack payloads would
   be both ineffective — Pulse normalizes records after retrieval, so the
   fixture path is the correct test surface — and inappropriate.
2. **Fixtures prove code paths, not upstream authenticity.** A genuinely
   compromised agency feed, a DNS hijack, or a TLS interception would be
   processed as valid input. Pulse performs no signature verification and no
   certificate pinning; that is outside C-03 as defined.
3. **Live results are a snapshot.** The 81 items, per-source counts, and host
   distribution reflect what the four agencies published on 3 November 2026.
   Re-running on another day will produce different counts; the checks are
   shaped to be count-independent.
4. **Browser XSS proof is prior evidence.** C03-55 rests on the 2 November 2026
   Phase 3 run. No browser automation was executed in this audit, so a change to
   `static/pulse.js` after that date would not be caught here. Source inspection
   was used to confirm the rendering approach is unchanged, which is weaker than
   a fresh browser run.
5. **Staleness was simulated, not waited out.** Cache entries had their
   `fetched_at` rewound past `CACHE_SECONDS` (1800 s) to force a refresh failure.
   This exercises the same code path as a real 30-minute outage without an
   actual wait.
6. **Classification was not measured against a labelled corpus.** C03-32 to
   C03-37 verify the documented rules and the allow-lists; they do not compute
   precision or recall for heuristic statuses. F-03-05 records this as an
   accepted, disclosed limitation.
7. **No load, fuzz, or penetration testing.** `MAX_RESPONSE_BYTES` (2 MB) and
   `TIMEOUT_SECONDS` (12 s) were read in `sources.py` but their behaviour under a
   slow or oversized endpoint was not exercised.
8. **Pulse is public and read-only.** No Supabase/Postgres interaction occurs on
   this path, so database constraints, RLS, and role permissions are irrelevant
   to C-03 and were not tested. Findings from C-01/C-02 remain open and
   unaffected by this report.

---

## 11. Final verification verdict

### C-03 Regulatory Feed Integrity and Source Validation — **PARTIALLY VERIFIED**

**Basis:**

* 54 of 55 audit checks passed; 1 failed (C03-54).
* 10 of 11 control requirements are fully met on the evidence recorded here
  (executed today, plus one prior browser check for Requirement 4).
* Requirement 2 is partial: source labels and original links are preserved
  (C03-05 to C03-08), but the destination host is not validated against the
  label (C03-54), so attribution can be spoofed at the link level.
* The standing suite passes in full — 97 offline and 109 live — and live source
  behaviour on 3 November 2026 was consistent with the control's intent.
* One check (C03-55, browser XSS) rests on preserved prior evidence rather than
  execution today; it is recorded as such and does not affect the verdict.

**Why not VERIFIED:** a single reproducible failure in a requirement that the
control explicitly owns. The failure is narrow (host binding, not scheme or
sanitization) and the precondition is upstream compromise, but the audit
standard is what the tests show, not what is likely. It can be closed and
re-tested quickly (CA-03-01 + CA-03-06).

**Why not UNVERIFIED:** the control is implemented and demonstrably operating.
Ingestion is registry-closed, unsafe URLs and impossible dates are rejected,
hostile markup stays inert, duplicates are removed, classification is
conservative and labelled, one failing source cannot blank the feed, stale data
is flagged, the API parameter is bounded, and nothing is fabricated when feeds
fail or are empty. This is materially different from a control that exists only
on paper.

**Compliance note:** this verdict is a technical assessment of one control. It
does not establish GLBA compliance, does not certify the accuracy or legal
effect of any agency publication, and does not close the open C-01 and C-02
findings.

---

## 12. Files created or changed

| Path | Change |
| --- | --- |
| `derexi-policy-pilot/backend/tests/test_c03_audit.py` | **New.** Isolated 55-check C-03 suite; synthetic fixtures, fetcher restored in `finally`, exits non-zero on failure, writes JSON evidence. |
| `docs/compliance/assignment3_c03_audit_results.md` | **New.** This report. |
| `docs/compliance/evidence/c03_audit_checks_2026-11-03.txt` | **New.** Console output of the audit run (54 passed, 1 failed). |
| `docs/compliance/evidence/c03_audit_results.json` | **New.** Machine-readable results for all 55 checks. |
| `docs/compliance/evidence/c03_pulse_suite_offline_2026-11-03.txt` | **New.** Standing suite, offline (97 passed). |
| `docs/compliance/evidence/c03_pulse_suite_live_2026-11-03.txt` | **New.** Standing suite with live endpoints (109 passed). |
| `docs/compliance/evidence/c03_live_link_hosts_2026-11-03.txt` | **New.** Read-only link-host distribution and one `HEAD` check. |
| `MEMORY.md` | Updated with this audit's state (project memory only). |

No application code, test assertion, schema, migration, RLS policy, role,
persona, Pulse design element, or regulatory classification was modified. No
package was installed. No Supabase data was read or written. No commit was
created and nothing was pushed to GitHub.
