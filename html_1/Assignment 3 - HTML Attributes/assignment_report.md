# 03 / HTML attributes
### Ten distinct original attributes · Complete

**Criterion:** demonstrate at least seven distinct HTML attributes. DeRexi's
literal `backend/static/index.html` supplies **ten named attributes** below,
exceeding the minimum without counting repeated values as new attributes.

| Attribute | Literal element/value | Source line | Purpose |
|---|---|---|---|
| `lang` | `html` / `en` | [derexi-policy-pilot/backend/static/index.html:2](../../derexi-policy-pilot/backend/static/index.html#L2) | Declares the document language |
| `class` | `header` / `letterhead` | [derexi-policy-pilot/backend/static/index.html:18](../../derexi-policy-pilot/backend/static/index.html#L18) | Connects markup to existing CSS |
| `href` | `a` / `#assist` | [derexi-policy-pilot/backend/static/index.html:39](../../derexi-policy-pilot/backend/static/index.html#L39) | Specifies the anchor destination |
| `type` | `button` / `button` | [derexi-policy-pilot/backend/static/index.html:48](../../derexi-policy-pilot/backend/static/index.html#L48) | Specifies button behavior |
| `id` | `button` / `notify-btn` | [derexi-policy-pilot/backend/static/index.html:48](../../derexi-policy-pilot/backend/static/index.html#L48) | Uniquely identifies the control |
| `for` | `label` / `persona-select` | [derexi-policy-pilot/backend/static/index.html:57](../../derexi-policy-pilot/backend/static/index.html#L57) | Associates the label with its select |
| `disabled` | `select` / `present (boolean)` | [derexi-policy-pilot/backend/static/index.html:59](../../derexi-policy-pilot/backend/static/index.html#L59) | Disables the initial unselected control |
| `title` | `button` / `Choose an authorized identity` | [derexi-policy-pilot/backend/static/index.html:63](../../derexi-policy-pilot/backend/static/index.html#L63) | Adds advisory information |
| `tabindex` | `main` / `-1` | [derexi-policy-pilot/backend/static/index.html:83](../../derexi-policy-pilot/backend/static/index.html#L83) | Allows programmatic focus without sequential tab entry |
| `src` | `script` / `governance.js` | [derexi-policy-pilot/backend/static/index.html:95](../../derexi-policy-pilot/backend/static/index.html#L95) | Names the existing script resource |

These are attributes on actual HTML elements, not JavaScript object properties
or SVG-only settings. `disabled` is a boolean attribute whose presence is meaningful;
it is not the text value `"false"`. `for="persona-select"` matches the existing
select's `id`. Additional real `aria-*`/`data-*` attributes exist, but the ten
listed names alone satisfy the criterion.

## Verification

[Source excerpts](evidence/source-excerpts.md), [attribute inventory](evidence/attributes.json)
and [current parser checks](evidence/verification.json) verify each attribute at
its exact original element/line, its value/presence, and the label/select association.
The [existing UI capture](evidence/reused-library-ui.png) and original Nov 18
browser results provide context only, not a new accessibility certification or
attribute test. DeRexi is the sole source; GitHub Pages was unnecessary.

**Outcome:** Complete, 10 distinct attributes against a minimum of 7. No original
HTML, script, authentication setting or interface was changed.
