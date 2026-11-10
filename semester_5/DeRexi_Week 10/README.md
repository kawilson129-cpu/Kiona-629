# DeRexi SDLC Week 10 — Testing & Quality Assurance

**Fixture-tested MVP: 379 PASS / 0 FAIL / 0 automated checks blocked. Production acceptance remains BLOCKED.**
Seven requested integration paths passed isolated checks; their seven **live** counterparts were not run. This is agent-executed UAT using fictional personas, not stakeholder sign-off or live Supabase verification.

No live Supabase access, writes, migrations, Auth users, fictional owner seeds, RLS/grant changes, dependency installation, commit or push occurred. Existing untracked CT+V coursework was preserved. Application and executable test source remain in `derexi-policy-pilot/`.

| Executed this week; latest result per check | PASS | FAIL |
|---|---:|---:|
| New cross-component integration/security checks | 42 | 0 |
| Reused Week 8 Governance lifecycle | 102 | 0 |
| Reused real document parser/intake | 47 | 0 |
| Reused Pulse unit/normalization/cache checks | 97 | 0 |
| Reused C-03 publisher audit, executed checks only | 54 | 0 |
| Desktop/mobile browser UAT | 37 | 0 |
| **Total** | **379** | **0** |

Browser results retain 29 passing steps from the completed desktop/initial mobile pass and 8 final mobile steps. The final mobile pass explicitly reinstated and checked the 390px CDP viewport; emulation resets on debugger disconnect. See `evidence/browser-results.json` and its `carriedForward` predecessor. Duplicate executions and historical checks are not added to the total. Earlier failing attempts remain evidence, not current failures.

Three confirmed defects fixed: feedback buttons falsely claimed a save without calling the API (high); Pulse accepted unrelated publishers under official source labels (high, prior C03-54); feedback accepted employee questions as DeRexi answers (medium). See [bug log](bug-log.md).

- [Test inventory and gaps](test-inventory.md)
- [Integration results, safety and reproduction](test-report.md)
- [UAT records and screenshot requirements](uat-records.md)
- [Final MVP checklist and blockers](final-mvp-checklist.md)
- `evidence/summary.json`, per-suite JSON/logs, `source-manifest.json`, `file-index.json`

Suggested commit: `Complete Week 10 MVP QA and fix feedback persistence and Pulse source validation`
