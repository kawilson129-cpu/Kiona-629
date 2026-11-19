# 04 / Hyperlinks
### A separate document, not just a different view · Complete

**Criterion:** at least one hyperlink leading to a separate page.

## Original DeRexi implementation

Pulse creates a real `<a>` through `document.createElement` in its helper at
[derexi-policy-pilot/backend/static/pulse.js:71](../../derexi-policy-pilot/backend/static/pulse.js#L71)–92. The publication anchor at [derexi-policy-pilot/backend/static/pulse.js:245](../../derexi-policy-pilot/backend/static/pulse.js#L245)–250 sets
`href: article.url`, `target: '_blank'` and `rel: 'noopener noreferrer'`. A second
explicit “Read the original publication” anchor is at lines 266–272. The destination
is an HTTPS publisher document, a separate page from DeRexi's `/ui/` document.

One actual retained article URL is recorded in [retained-article.json](evidence/retained-article.json),
from the Nov 18 browser response. The [existing Pulse capture](evidence/reused-pulse-ui.png)
and B05 show real article rendering at that time. They do **not** prove a publisher
link was clicked or that its current remote destination is reachable.

In contrast, the literal `href="#assist"`, `#library` and other anchors at
[derexi-policy-pilot/backend/static/index.html:38](../../derexi-policy-pilot/backend/static/index.html#L38)–46 remain within the SPA document. They are intentionally
excluded from the separate-page criterion. DeRexi's publication links already
provide the appropriate implementation; no GitHub Pages fallback was necessary.

## Portable literal-HTML demonstration

[index.html](index.html) and [publication.html](publication.html) are two small,
offline coursework pages based on the verified DeRexi semantic structure, Pulse
link behavior and retained article metadata. They are **new demonstrations**, not
original source or a rebuilt application. Styles are inline; no scripts, APIs,
login, external assets or database are required.

The decisive literal anchor in `index.html` is:

```html
<a id="publication-link" href="publication.html">Read the publication brief on a separate page</a>
```

Its destination exists as a distinct HTML file and has an ordinary return anchor.
[Static checks](evidence/verification.json) verify the exact href, destination
document, different pathname and absence of fragment-only navigation. The
[course browser verification](../evidence/browser-verification.json) records an
actual local-file click to that separate page and back. This is a new **demo-only**
navigation check, not a DeRexi API test or verification of live publisher availability.

**Outcome:** Complete. Original Pulse supplies the existing separate-page link
implementation; the coursework bundle makes literal markup and actual independent
document navigation reproducible without altering any existing project.
