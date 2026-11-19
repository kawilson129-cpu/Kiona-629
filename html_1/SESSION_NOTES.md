# Session notes · 2026-11-19

- Read repository memory before inspection; initial working tree was clean.
- Preserved the existing `html_1/` folder and its original LMS screenshot.
- Searched canonical DeRexi first. A1/A3 already meet literal requirements.
  A2 uses its existing portfolio page only for missing literal image/list markup.
  A4 distinguishes real external publication anchors from SPA fragments.
- Copied prior UI/test evidence with exact original paths and byte hashes; did not
  rerun historical app/API tests or fabricate screenshots.
- Added only a minimal static, explicitly labelled two-page coursework demo to
  demonstrate separate-document navigation; no app functionality was rebuilt.
- Current verification files record actual source, asset, link and demo checks.
- All writes are confined to this course folder. The user's current write boundary
  takes precedence over the earlier root-memory update convention; root MEMORY.md,
  DeRexi, GitHub Pages, configs, database and other coursework remain untouched.
- No commit or push. No supplied-rubric gaps remain after the recorded checks.

## Executed outcomes

- New source/evidence verification: **52 PASS / 0 FAIL** (A1 9, A2 14, A3 16,
  A4 11, plus 2 source/write-scope checks).
- New local static-demo browser verification: **5 PASS / 0 FAIL**. These are not
  production/API tests; all original historical results retain their old scope.
- Viewed the actual demo capture and checked its explicit demonstration labels.
- Dedicated browser exited successfully and only its created profile was removed.
- [Full created-file index](evidence/file-index.json) and [commands](evidence/commands.txt).
