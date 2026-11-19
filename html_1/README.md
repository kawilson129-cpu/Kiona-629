# HTML 1 · Existing-project evidence

The existing course folder is `html_1/`; it is preserved as the requested **HTML1**
course root. No duplicate directory, source relocation or production edit.

| Assignment directory | Status | Primary evidence |
|---|---|---|
| [Assignment 1 - Semantic HTML](Assignment%201%20-%20Semantic%20HTML/README.md) | **Complete** | DeRexi literal semantic landmarks |
| [Assignment 2 - Web Elements](Assignment%202%20-%20Web%20Elements/README.md) | **Complete** | DeRexi tags plus its existing portfolio case-study image/list |
| [Assignment 3 - HTML Attributes](Assignment%203%20-%20HTML%20Attributes/README.md) | **Complete** | Ten distinct DeRexi HTML attributes |
| [Assignment 4 - Hyperlinks](Assignment%204%20-%20Hyperlinks/README.md) | **Complete** | Pulse publisher anchors + checked two-document coursework demo |

Each assignment contains `README.md`, `assignment_report.md`, verbatim source
excerpts, source-line/hash mapping, copied original UI/test context and new offline
verification results. The source-first search found no literal image in the DeRexi
app; only Assignment 2 therefore uses GitHub Pages source, still about DeRexi.

The original course screenshot remains untouched. The four criteria are supplied
by the user; no unseen LMS requirements are assumed. The prior UI evidence is
dated Nov 18 and uses synthetic SQLite, mocked search and disabled AI. It is copied
with original provenance and **not rerun or represented as HTML rubric tests**.

New checks are source/markup/attribute/asset/link checks plus local demo navigation.
They do not verify production data/authentication, deployed GitHub Pages, live
publisher reachability or application behavior. See [static verification](evidence/verification.json),
[browser navigation](evidence/browser-verification.json) and [session notes](SESSION_NOTES.md).

Recheck the static evidence from repository root:

```sh
python3 -B html_1/verify_coursework.py
```

The browser-only demo check and its prerequisites are recorded by `verify_demo.mjs`.
No application/API server is required. No commit or push.

## Delivery index

**Current results: 52 source/evidence checks PASS; 5 local demo-navigation checks PASS.**
All four assignments are Complete, with no supplied-rubric gaps. Live publisher
reachability and the deployed Pages build were not tested or claimed.

See [all created files](evidence/file-index.json) and [actual commands/cleanup](evidence/commands.txt).
The exact source lines and copied evidence are documented separately inside each assignment.
