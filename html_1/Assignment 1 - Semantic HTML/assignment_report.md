# 01 / Semantic HTML
### Existing DeRexi structure · Complete

**Criterion:** demonstrate literal `header`, `main`, `footer` and `nav` tags.
All four already exist in DeRexi's actual HTML shell; no production edit or
replacement application was needed.

| Required element | Exact existing source | Purpose |
|---|---|---|
| `<header>` | [derexi-policy-pilot/backend/static/index.html:18](../../derexi-policy-pilot/backend/static/index.html#L18); closes at line 23 | Institution/division letterhead |
| `<nav>` | [derexi-policy-pilot/backend/static/index.html:38](../../derexi-policy-pilot/backend/static/index.html#L38); closes at line 46 | Named primary navigation landmark |
| `<main>` | [derexi-policy-pilot/backend/static/index.html:83](../../derexi-policy-pilot/backend/static/index.html#L83) | Single main content mount point for the existing app |
| `<footer>` | [derexi-policy-pilot/backend/static/index.html:86](../../derexi-policy-pilot/backend/static/index.html#L86); closes at line 90 | Institution, regulation context and mode label |

The `main` element is empty in the initial source because existing JavaScript
renders its content; this does not remove its semantic role. The navigation's
`aria-label="Primary"` names the landmark. Its hash links switch SPA views;
they are not counted as separate-page links for Assignment 4.

## Verified evidence

- [Literal code excerpts](evidence/source-excerpts.md) and [source hashes](evidence/source-map.json).
- [Existing Library screenshot](evidence/reused-library-ui.png): actual Nov 18 UI,
  synthetic fixture. It provides rendered context, not proof of tag names.
- [Existing browser results](evidence/reused-browser-results.json), B01: Library
  display passed previously. No browser/API checks rerun or invented.
- [Current verification](evidence/verification.json): standard-library HTML parsing
  confirms all four literal elements and the single main element in the original file.

**Outcome:** Complete. DeRexi alone satisfies this criterion. No supplemental demo
or GitHub Pages fallback was necessary.
