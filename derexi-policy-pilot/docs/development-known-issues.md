# Existing issues outside RBAC Stage 1

Recorded November 3, 2026 at HEAD `dba7f8f`. No fixes are included in Stage 1.
Keep these issues separate from the new isolated permission/principal test results.

## MSG-001 — UI calls a missing Messages route

`backend/static/app.js` calls `GET /messages?user_id=...`, but `backend/main.py`
has no `/messages` route. MEMORY.md describes later messaging work that is absent
from this checkout. Confirm the intended contract before implementing it; do not
overwrite current source from historical notes. Current UI and routes stay unchanged.

## INC-001 — Existing incident suite has six failures

Last verified November 3 before Stage 1: 3 passed / 6 failed. Run from backend/:

```bash
DATABASE_URL=postgresql+psycopg2://offline:offline@127.0.0.1:1/offline \
  ../.venv/bin/python tests/test_week8_stage1.py
```

This runner uses fake sessions, never live Supabase. FastAPI TestClient requires
the local runtime capabilities unavailable inside this machine's restricted sandbox.

| Existing failed test | Observed mismatch |
| --- | --- |
| `test_get_incidents_reporter_scoped` | Reporter filter missing |
| `test_guidance_none_below_threshold` | `incident_guidance` missing |
| `test_guidance_none_when_no_results` | `incident_guidance` missing |
| `test_guidance_returns_best_policy` | `incident_guidance` missing |
| `test_post_incident_category_missing` | Expected category-not-found rejection missing |
| `test_post_incident_ok_default_severity_and_guidance` | Expected guidance response field missing |

These application/test mismatches predate the isolated RBAC modules. No assertions,
application code or incident behavior were changed. Route integration and incident
fixes need later authorization; passing RBAC tests does not resolve these issues.

## Subsequent hardening attempt — November 3

The user subsequently authorized integration/hardening, checkpoint commits and
development-branch pushes. The Stage 1 checkpoint is now `4eac30a` on
`codex/derexi-security-hardening`. MSG-001 remains open. INC-001 was rerun after
the C-02 validation changes: **4 passed / 5 failed**. The category-not-found
failure is resolved; reporter scope and four guidance-related failures remain.
No existing tests were changed. See `compliance/assignment3_security_hardening_final.md`
for current evidence and blockers; the earlier baseline above is retained.

## November 5 resume status

- **MSG-001 remains BLOCKED.** The current signed-browser run records the real
  missing `/messages` response and the existing Messages unavailable state.
- **INC-001 is now 5 passed / 4 failed.** Reporter filtering was fixed as part of
  scoped incident collections. The three missing `incident_guidance` tests and
  missing guidance response field still fail; their assertions are unchanged.
- Original audit files were found on newer origin/main and recovered. The
  secured profile now passes 15 C-01/26 C-02/55 C-03 checks, with updated
  signed-auth/private-schema C-01 assumptions documented in the final report.
- The ordinary `main:app` remains unguarded compatibility. Use the explicit
  secured entry point for RBAC; do not expose the legacy entry point publicly.
  Real employee demo migration awaits an approved local snapshot/Auth setup;
  no existing business records were replaced or modified.
