# Execution notes

Date: November 17, 2026. Working directory initially repository root; runner sets child cwd to Assignment 4. All artifacts and temporary directories stay here.

1. Read root MEMORY.md, official rubric rendering and prior coursework/SDLC files. No historical source copied or modified. The image-based official PDF's existing rendering is reused by reference.
2. Runtime command `derexi-policy-pilot/.venv/Scripts/python.exe -B <Assignment4>/src/run_audit.py` initially exited 1 with `Access is denied` for the existing interpreter path. Approved external runtime execution then succeeded; no dependency install or permissions setting change.
3. First full run `20261117T113049661426Z`: 100 PASS / 5 FAIL / 7 BLOCKED. Security/governance failed before assertions because socket guard blocked Windows TestClient wakeup. Focused adapter used `published` instead of current `date` argument. Three dependency conditions genuinely failed. No blocked network operation completed.
4. Second run `20261117T113646825834Z`: 296 PASS / 4 FAIL / 4 BLOCKED. All original suite assertions passed. Security safety guard still reported three blocked external-write attempts. Targeted `diagnostic-security/` established the paths were exactly Windows `\\.\NUL`, a discard device, not external artifact files.
5. Final run `20261117T114241633169Z`: narrow standard-library socketpair allowance, NUL allowance and corrected focused keyword. 297 PASS / 3 FAIL / 4 BLOCKED; all service connections and real external writes still guarded. Existing source files unchanged across 56 hashes. Return codes and timings are in summary.json; per-check logs retained. No source/fixture assertions weakened.

The diagnostic runs are preserved, superseded and excluded from final totals. Runtime stdout was kept brief; full test stdout/stderr is in assignment-local `suite.log` and `process.log`. Python audit hooks provide guarded-process evidence; they are not a claim of OS-level sandbox certification. The runner does not allow arbitrary third-party scripts as an alternative to reviewing fixture behavior.

No application server, browser, production access, Supabase transaction, malware/exploit, dependency upgrade, migration, real user/role edit, email, deployment, commit or push was performed. Source and historical evidence links are registered separately. Root memory was intentionally not edited because the user requires all Assignment 4 notes to stay inside this directory.
