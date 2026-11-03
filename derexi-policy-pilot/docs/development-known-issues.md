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
