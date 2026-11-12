# Week 11 documentation validation

Scope: documentation and source inspection only, November 11, 2026. No server launch, live Supabase access, write rehearsal, migration, dependency installation, production change or full regression run. Mac/Windows commands were reviewed against repository layout; native setup execution is not claimed.

## Reproduction

From repository root in PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\semester_5\DeRexi_Week 11\evidence\validate-documentation.ps1'
git diff --check
```

The script reads only scoped docs/source and writes [documentation-checks.json](documentation-checks.json) here. It checks local Markdown targets, code fences, parses PowerShell examples without executing them, verifies setup/proposal paths and inspects health/persona/HTML boundaries. External URL reachability is not checked. Test/check counts are documentation checks, not application tests.

## Source review

- README retains purpose/layout/Pulse details; replaces obsolete unauthenticated curl, direct-write routes, default employee, old policy counts and early UI claims. Current notification path is `/messages/notifications`.
- Setup uses canonical `--app-dir backend` from the project folder, machine-local environments and loopback/no-proxy development startup. Source uses modern union annotations, so the README baseline is Python 3.10+. Requirements include parser/JWT dependencies. No packages were installed.
- Week 7 evidence and Pulse documentation had moved; links were corrected to their actual coursework locations. No previous evidence was edited.
- The old Week 10 fixture script's `__main__` rewrites its historical input. The demo instead documents Uvicorn's import-based app target, bypassing that entry point. Existing fixture construction uses isolated SQLite/mocked provider/feed; no import or rehearsal was executed this week.
- Normal HTML and dynamic source were inspected for classroom/SDLC/fixture terms. `app.js` matches are comments; `governance.js` matches belong to its error-sanitizing regular expression. CSS matches are comments. No displayed normal-mode classroom/fixture label was found. No visual redesign or runtime edit was needed. This is source review, not new screenshot/browser evidence.
- Production identity, department/participant RBAC and loopback/same-origin/forwarded-header persona guards were left unchanged. No new users/accounts or fixture indicators were added to normal pages.

## Limits

Existing Week 10 evidence remains 379 PASS / 0 FAIL, not rerun or added to Week 11 totals. Real Auth, schema/owner activation, direct-client access boundaries, infrastructure/backup/logging, native Windows/Linux, PostgreSQL concurrency/retrieval, seven live handoffs and human acceptance remain pending. The demonstration is prepared, not newly executed. See [release checklist](../release-checklist.md).

Final documentation counts and any corrected findings are recorded in the JSON results and session outcome below.

## Initial findings and corrections

Direct script invocation was blocked by the machine's PowerShell execution policy. Validation used a process-only policy override; no persistent execution-policy setting changed. The first executed run recorded 91 PASS / 2 FAIL: the original database-design link was stale, and the results JSON did not yet exist when its own link was checked. The database design was found in its actual Week 3 coursework location, the README layout now names the actual deployment document, and the generated JSON now exists. The initial results are preserved in [documentation-checks-initial.json](documentation-checks-initial.json). Final rerun results are authoritative for documentation checks only.

## Final outcome

Final executed run: **94 PASS / 0 FAIL**, covering 10 Markdown documents and 70 local links. PowerShell examples parse and required setup/proposal paths exist. Initial 2 findings were corrected as recorded above. Source-level normal-page copy review found no displayed classroom/SDLC/fixture labels. No runtime edit was required. Native Mac/Windows installation, production process launch and interactive rehearsal were not executed. No new application-test count or live/infrastructure verification is claimed.

### Focused walkthrough follow-up

Added employee-messages-walkthrough.md with an 8-minute core and two optional 1-minute extensions, allowing questions through minute 12. Reuses the actual Week 10 exception question and distinguishes its screenshot from the separate remote-signature thread. Targeted check: 6 local links checked, 0 broken. Existing Week 11 aggregate counts above remain the earlier documentation run, not rerun totals. No application tests, live activity or rehearsal executed.

### Governance walkthrough follow-up

Added governance-library-walkthrough.md: 8-minute core with optional revision/error discussion through 10–12 minutes. Separates independent peer review, independent Admin approval, explicit eligible-date publication and employee Library verification. Targeted validation: 8 local links / 0 broken. Reuses existing screenshots with continuity limits. Earlier aggregate results remain historical. No application tests, live changes or rehearsal executed.

### Pulse walkthrough follow-up

Added pulse-revision-walkthrough.md with an 8-minute core and optional discussion through 12 minutes. Reviewed existing Pulse button/source handoff and Week 10 U21–U26. Explicitly identifies the fixture article/URL as synthetic, carries source context to a saved revision and preserves the published baseline. Targeted check: 6 local links, 0 broken. Earlier aggregate counts remain historical. No runtime tests, live activity or rehearsal executed.

### Feedback walkthrough follow-up

Added feedback-dashboard-walkthrough.md with an 8-minute core and optional discussion through 12 minutes. Reviewed saved rating/update behavior, Admin overview Helpfulness and historical U19/I11–I18. Explicitly documents the missing dedicated Dashboard screenshot and department/synthetic-citation limits. Targeted validation: 7 local links / 0 broken. Earlier aggregate counts remain historical; no runtime tests, live activity or rehearsal executed.
