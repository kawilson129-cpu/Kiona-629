# Assignment 3 · Styling

**Requirement:** demonstrate colors, text/font styles and shapes; explain palette,
typography, hierarchy and decisions. **Status: PARTIAL — visible existing styling
and new editable specifications; native Design text/style properties UNVERIFIED.**

## Reused evidence and its limits

The [original board thumbnail](../evidence/stay-data-stay-original-thumbnail.png)
shows light/pink/green flowchart shapes, connectors and labels. The embedded
[account-log image](../assignment_2_images/evidence/embedded-account-log.png) shows
monospaced text visually, but raster lettering does not prove editable font layers.
Original native typeface identities, sizes and saved styles were not decoded.

The existing [project artwork](../../docs/assets/images/stay-data-stay-project.png)
provides the green/gold/ivory visual direction. The following are **new proposed
tokens**, not sampled exact colors or recovered Figma styles:

| Palette | Proposed role |
|---|---|
| Forest `#10291F` / ink `#17251C` | Brand headings / primary text |
| Ivory `#F7F4EC` / white `#FFFFFF` | Canvas / account-row surfaces |
| Gold `#B38B4B` | Decorative accent; not small body text |
| Muted green `#4D6446` / rule `#D8DFD2` | Supporting text / separators |

## Prepared styling and design decisions

[design-tokens.json](design-tokens.json) separates primitive colors/spacing from
semantic roles and account-row properties. [style-reference.svg](style-reference.svg)
is a local style reference, not a Figma screenshot. The screen uses these families:

| Proposed text style | Family / weight | Size / line height |
|---|---|---|
| Display | Georgia / regular | 48 / 56 px |
| Heading | Georgia / regular | 30 / 38 px |
| Body | Arial / regular | 18 / 28 px |
| Meta | Arial / regular | 14 / 20 px |

Large serif headings establish hierarchy; supporting text and repeated account rows
make the summary easy to scan. Rectangles, 12px rounded row surfaces, index circles
and 1px rules supply the shape vocabulary. No color-only status distinction is needed.

## Native Figma completion and evidence

Import the screen. Inspect whether text stays editable; if it is converted to
vectors, recreate representative heading/body labels with native Text layers.
Apply the documented fills, font family, weight and size; use available substitutes
if necessary and record actual values. Set native line heights from the table.
Optionally save `SDS/Display`, `SDS/Body` and named color styles for reuse. Capture
selected native text and shape properties as `text-style-in-figma.png` and
`shape-style-in-figma.png` here. No native style creation is claimed yet.

## Rubric checklist

- [x] Existing visual styling referenced without inventing font metadata.
- [x] Palette, type hierarchy, shapes and design intent specified in import assets.
- [ ] Native editable font properties and shape fills verified in Figma Design.

[Course index](../COURSE_INDEX.md).
