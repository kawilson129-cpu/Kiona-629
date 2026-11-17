# Control validation and historical reconciliation

## Fresh execution

November 17, 2026 UTC, Windows / existing Python environment. Authoritative run: [20261117T114241633169Z](../evidence/20261117T114241633169Z/summary.json). Exact child commands, durations, return codes and Python version are in that summary. Inventory includes 37 installed distributions; this is local, not deployed inventory.

| Family | Fresh assertions | PASS | FAIL | BLOCKED | Evidence |
|---|---:|---:|---:|---:|---|
| Existing security suite | 88 | 88 | 0 | 0 | [checks/log](../evidence/20261117T114241633169Z/security/results.json), `security/suite.log` |
| Existing governance lifecycle | 102 | 102 | 0 | 0 | [checks/log](../evidence/20261117T114241633169Z/governance/results.json), `governance/suite.log` |
| Existing offline Pulse suite | 97 | 97 | 0 | 0 | [checks/log](../evidence/20261117T114241633169Z/pulse/results.json), `pulse/suite.log` |
| Focused host negatives/positive and DB tripwire | 5 | 5 | 0 | 0 | [checks](../evidence/20261117T114241633169Z/focused/results.json) |
| Per-child safety guard | 4 | 4 | 0 | 0 | Last check in each child's JSON |
| Application/test/harness source integrity | 1 | 1 | 0 | 0 | [56 unchanged files](../evidence/20261117T114241633169Z/source-integrity.json) |
| Dependency criteria | 3 | 0 | 3 | 0 | [dependency results](../evidence/20261117T114241633169Z/dependency-results.json) |
| Enterprise operating acceptance | 4 | 0 | 0 | 4 | `scope_blocks` in summary |
| **Total distinct current outcomes** | **304** | **297** | **3** | **4** | No historical check counts included |

PASS: assertion met its scoped criterion. FAIL: actual control condition fails the criterion. BLOCKED: no permitted/available evidence to perform the operating acceptance test. Harness exceptions are explicitly retained; they are not silently omitted or converted to application failures.

## Test design, expected/actual results and coverage

The runner imports existing `test_week9_security`, `test_week8_governance`, `test_pulse` and `messaging_fixture` by reference, without altering their files. Real FastAPI handlers, signed synthetic tokens and SQLite ORM execute. `security.OUT` and the test-evidence environment variable are process-local output adapters; source code, production settings and real seeded users are unchanged.

| Focus | Expected criterion | Actual fresh result / limit |
|---|---|---|
| Authorization | Anonymous denied; Employee cannot publish/escalate; Owner cannot view unrelated incidents; identity claims cannot elevate | Existing security assertions pass. Synthetic JWT cryptography is real; JWKS/provider transport is mocked |
| Input/safe errors | Invalid type/reference yields 422; prohibited workflow fields denied; rejected input/DB internals not leaked | Relevant authenticated negative checks pass. Includes valid requests and simulated failures; no live DB outage |
| Policy integrity | Legacy bypass denied; author cannot self-approve; valid independent approval; explicit publication; atomic failure rollback | All 102 governance assertions pass; SQLite translation does not validate PostgreSQL locks/RLS |
| Pulse integrity | Normalization, cache, dedupe, ranking and controlled sources work; spoof hosts rejected | 97 offline assertions plus three hostile-host rejections and valid-host positive control pass; URLs are synthetic fixtures, never fetched |
| Logging | Content-free actor/action/route events; denial/login/admin/approval recorded; query/token/private markers excluded | Local capture checks pass, [synthetic sanitized events](../evidence/20261117T114241633169Z/security/security-events-sanitized.json). Durable collection/retention/alerts not proven |
| Dependencies | Reviewed complete runtime hash lock; historical affected versions no longer present | All three criteria FAIL: lower-bound requirements; certifi 2026.7.22 and pip 26.1.2 persist. Version matches do not demonstrate successful exploitation |

Actual result names and values are in each JSON; per-assertion expected HTTP codes are encoded in check names or criteria in the unchanged source test modules. For deeper procedure review, [original security suite](../../../derexi-policy-pilot/backend/tests/test_week9_security.py) and [governance suite](../../../derexi-policy-pilot/backend/tests/test_week8_governance.py) are authoritative; source hashes freeze what ran. Focused reserved-domain tests provide negative and positive controls, avoiding a detector that rejects everything.

## Isolation and repeatability

From Assignment 4:

```powershell
& ../../derexi-policy-pilot/.venv/Scripts/python.exe -B src/run_audit.py
& ../../derexi-policy-pilot/.venv/Scripts/python.exe -B tests/validate_package.py
```

Each child has an assignment-local TEMP/TMP and log directory. `-B` disables bytecode writes. `.env` reads are blocked and dotenv loading disabled. SQLite is in-memory; the existing PostgreSQL tripwire rejects connections. Python audit hooks reject service socket connections/DNS and filesystem writes outside Assignment 4. The only permitted socket connects are Windows standard-library socketpair wakeups with a loopback destination and verified `socket.py` stack frame. The Windows NUL discard device is allowed because it stores no artifacts. No endpoint is started or scanned. Source hashes before/after match across 56 files.

The initial sandbox runtime launch was denied (`Access is denied`); approved runtime execution was used, retaining the internal guards. Initial complete attempt `20261117T113049661426Z` recorded 100 PASS / 5 FAIL / 7 BLOCKED: the broad network guard blocked Windows TestClient wakeups and the focused adapter used a wrong keyword. Second attempt `20261117T113646825834Z` recorded 296 PASS / 4 FAIL / 4 BLOCKED: all original application assertions passed, but the guard counted attempted opens of Windows NUL as external writes. A separate targeted diagnostic identified exactly `\\.\NUL`. Final run fixed only harness allowances/keyword; all prior attempts remain in evidence, are superseded and are not summed.

## Historical evidence, retained separately

| Source/date | Original result | Present interpretation |
|---|---|---|
| Compliance 1 November 3 C-01/C-02 | 16 PASS / 25 FAIL across 41 checks | Genuine baseline and harness/profile limits; not rewritten |
| Compliance 1 November 3 C-03 | 54/55 PASS; source-host binding failure | Historical failure. Browser/component scope retained |
| Compliance 1 November 5 secured profile | Reported 15/15, 26/26 and 55/55 | Historical separate bootstrap/profile; not assumed current production assembly |
| CT+V 2 Assignment 2 November 9 | 27 PASS / 6 FAIL; later two advisory issues | Old policy/feed negatives predate latest integrated source; fresh checks supersede those local conditions only |
| Assignment 5 November 9 | Legacy suite 23 PASS / 18 FAIL; JWT/schema follow-ups | [Failure classifications](../../CT+V%202%20Assignment%205/completion-matrix.md) separate stale authentication assumptions from genuine then-current gaps |
| SDLC Week 11 November 12 | Security 88, governance 102, Pulse 97 passing; broader 622/0 with platform skips | Prior records reused for chronology, not included in fresh totals; seven live handoffs and infrastructure controls remained unverified |
| Assignment 3 November 16 | 32 local PASS, 5 platform BLOCKED | Threat-intel platform capacity blocker; not exercised or resolved here |
| Assignment 1 November 17 | Inventory 37; lock plus two advisory matches unresolved | Fresh dependency comparison confirms same versions; no fresh comprehensive advisory scan |

Full references and hashes appear in [evidence index](../evidence/index.md). Native parser/browser testing was not repeated; neither live feed health nor actual browser rendering is inferred from a Python Pulse test. Current local design effectiveness is demonstrated for the sampled paths; operating duration, formal monitoring and independent acceptance remain outside the evidence.
