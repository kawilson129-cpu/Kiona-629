# 02 / Web elements
### DeRexi first, its existing portfolio page second · Complete

**Criterion:** demonstrate `<a>`, `<div>`, `<img>` and `<ul>` or `<ol>`.

| Required element | Original evidence | Interpretation |
|---|---|---|
| `<a>` | [derexi-policy-pilot/backend/static/index.html:39](../../derexi-policy-pilot/backend/static/index.html#L39) | DeRexi's literal Policy Assistant anchor |
| `<div>` | [derexi-policy-pilot/backend/static/index.html:26](../../derexi-policy-pilot/backend/static/index.html#L26) | Existing app topbar wrapper |
| `<img>` | [docs/derexi-policy-pilot.md:25](../../docs/derexi-policy-pilot.md#L25)–27 | Literal image in the existing DeRexi portfolio case study |
| `<ul>` | [docs/derexi-policy-pilot.md:66](../../docs/derexi-policy-pilot.md#L66)–88 | Literal project-details list in that same case study |

## Why a fallback was needed

The canonical DeRexi HTML/JavaScript was searched first. Its wordmark uses inline
`<svg>`; SVG is **not** an `<img>` tag and is not counted as one. Governance does
create a real ordered list through `el('ol', ...)` at [derexi-policy-pilot/backend/static/governance.js:105](../../derexi-policy-pilot/backend/static/governance.js#L105), with
the helper's `document.createElement` at line 6. That is runtime-created DOM,
not a literal `<ol>` in the original HTML source.

For unambiguous literal HTML evidence, the existing GitHub Pages **DeRexi case-study
page** supplies the missing image and an explicit unordered list. This preserves
DeRexi as the subject rather than introducing an unrelated example. The page also
contains all four required tags together; no new feature was built.

## Image and Liquid details

The existing `<img>` has meaningful `alt="DeRexi Policy Pilot Project"` and a
`src` produced by Jekyll's `relative_url` filter. The referenced original PNG
exists at `docs/assets/images/derexi-policy-pilot-hero.png`; a byte-identical
[asset copy](evidence/existing-derexi-project-image.png) is supplied here. Liquid is
template source; it is not claimed executable by opening the Markdown as a raw HTML file.
No current GitHub Pages build or deployed page screenshot was fabricated.

## Evidence and result

[Verbatim excerpts](evidence/source-excerpts.md), [source map](evidence/source-map.json),
[copied-image provenance](evidence/reused-evidence.json), and
[literal-element/asset checks](evidence/verification.json) substantiate every tag.
The [reused DeRexi UI screenshot](evidence/reused-library-ui.png) and Nov 18 browser
results provide primary-project context only; they are not asserted to test a
portfolio image or list. **Complete for the supplied literal-element criterion.**
