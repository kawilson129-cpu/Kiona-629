---
version: alpha
name: Editorial Luxury
description: A champagne-ivory editorial luxury identity for the Kiona Wilson portfolio — oversized type, airy whitespace, restrained champagne accents.
colors:
  primary: "#121212"
  secondary: "#4A4A4A"
  tertiary: "#C9B495"
  accent: "#E8D5B5"
  neutral: "#FAF9F6"
typography:
  headline-display:
    fontFamily: Inter
    fontSize: 8rem
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 4rem
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: -0.03em
  headline-md:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: -0.03em
  body-lg:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  eyebrow:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.2em
  label-caps:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1
    letterSpacing: 0.1em
  nav-link:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1
rounded:
  sm: 4px
spacing:
  container: 1400px
  base: 16px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
  section-gap: 12rem
  padding-x: 6rem
components:
  page-surface:
    backgroundColor: "{colors.neutral}"
  eyebrow-label:
    typography: "{typography.eyebrow}"
    textColor: "{colors.tertiary}"
  headline-display:
    typography: "{typography.headline-display}"
    textColor: "{colors.primary}"
  body-copy:
    typography: "{typography.body-lg}"
    textColor: "{colors.secondary}"
  nav-item:
    typography: "{typography.nav-link}"
    textColor: "{colors.primary}"
  project-title:
    typography: "{typography.headline-md}"
    textColor: "{colors.primary}"
  project-meta:
    typography: "{typography.label-caps}"
    textColor: "{colors.secondary}"
  image-tile:
    backgroundColor: "{colors.accent}"
    rounded: "{rounded.sm}"
    size: 100%
---

# Editorial Luxury

A champagne-ivory editorial luxury design system for the Kiona Wilson portfolio. Oversized typography, airy horizontal space, and a structured, quiet confidence.

## Overview

The portfolio reads like a well-set editorial spread rather than a template site. The atmosphere is airy and restrained — cream canvas, champagne highlights, and oversized display type doing the heavy lifting. Sections are generously separated, the hero is left-aligned and calm, and every element occupies its own clean spatial zone. The work (cybersecurity, policy governance, AI-assisted tools) is presented with quiet authority: stripped of decoration, built on type, spacing, and a single warm accent.

## Colors

The palette is rooted in an ivory-cream neutral base with near-black ink and a single champagne accent family.

- **Primary (#121212):** The ink — near-black with a soft 6% lift off pure black. Used for all headline text, navigation, and critical content.
- **Secondary (#4A4A4A):** A warm charcoal used for body copy, captions, and metadata so prose never competes with headlines.
- **Tertiary (#C9B495):** Deep champagne — the darker end of the accent family. Reserved for eyebrow labels, hover states, and emphasized words.
- **Accent (#E8D5B5):** Pale champagne — the signature color. Used as the image-tile placeholder fill behind project imagery.
- **Neutral (#FAF9F6):** Warm ivory canvas. The page background — softer and more organic than pure white.

### Role

- Ink (`primary`) drives headlines and primary text.
- Champagne (`tertiary` + `accent`) is decorative and directional — never applied as large painted areas.
- Ivory (`neutral`) is the canvas; it appears behind everything, including fixed navigation.

## Typography

The typographic strategy is a single family — **Inter** — in two weights (400 and 500) driven by scale and spacing rather than weight contrast.

- **Display:** Oversized fluid headlines (`clamp(3.5rem, 10vw, 8rem)`) with tight tracking (`-0.03em`) and compressed leading (`1.1`). Hierarchy comes from scale, not weight.
- **Body:** Relaxed leading (`1.6`) with a `65ch` max measure for readability. Written in warm charcoal (`secondary`), never full ink.
- **Eyebrow & Labels:** Small uppercase micro-labels with generous tracking (`0.1em`–`0.2em`). Eyebrows run in deep champagne; project and footer metadata run in charcoal.

### Scale

The scale is fluid by design — every headline uses `clamp()` so type scales gracefully from mobile to desktop without breakpoints. Smallest readable text is `0.75rem` (eyebrows); body never drops below `1rem`.

## Layout & Spacing

The layout follows a **Free-Flow Editorial Grid**: max-width `1400px` containment, generous horizontal padding (`clamp(1.5rem, 5vw, 6rem)`), and section gaps of `clamp(6rem, 15vh, 12rem)`.

- **Foundation:** A base 8px spacing scale with 4px micro-steps.
- **Hero:** Left-aligned, vertically centered, min-height `80vh`. No center alignment, no clutter.
- **Project grid:** `auto-fit` with a `minmax(400px, 1fr)` column baseline and `4rem` gutters.
- **Split grids:** About and Contact pages use a strict `1fr 1fr` two-column split that collapses to a single column below `900px`.
- **Responsive:** All multi-column layouts collapse to a single column below `768px`; mobile navigation becomes a slide-in panel.

## Elevation & Depth

Depth is achieved through **Motion, Not Shadow**. The design is flat — no card shadows, no layered elevation. Hierarchy is communicated by:

- **Hover translation:** Project cards lift `-10px` on hover with an expressive `cubic-bezier(0.16, 1, 0.3, 1)` ease.
- **Image recline:** Project images scale to `1.05` on hover behind a `4:3` aspect-ratio frame.
- **Structural lines:** `1px` hairline borders (`rgba(18, 18, 18, 0.08)`) separate nav and footer from content.
- **Fade-in reveals:** Content enters with a `30px` translate + opacity fade, staggered by section.

## Shapes

The shape language is **Architectural Sharpness with a Single Softness**. Element corners are minimal — a `4px` radius on image tiles only. Buttons, links, and dividers are crisp and unrounded. Shape is used sparingly: the image tiles carry the only corner in the system, keeping the editorial pages quiet and seamless.

## Components

- **Navigation:** Fixed top bar on the ivory canvas with a hairline bottom border. Logo left, inline links right (opacity `0.8` → `1` on hover/active). Below `768px`, links collapse into a right-hand slide-in panel with full-size `2rem` links.
- **Project cards:** Trembling-image editorial cards — a champagne `4:3` image frame with `4px` corners over a title in headline scale with an uppercase tracked meta line. Card lifts on hover.
- **Eyebrow labels:** Uppercase deep-champagne micro-label introducing each section.
- **Inline text links:** Underline-stroked links (resume CTA, contact actions) that shift to deep champagne on hover with a slight `4px` right drift.
- **Contact rows:** Icon-plus-label-action rows that drift right and turn champagne on hover.

## Do's and Don'ts

- Do use champagne (`tertiary`/`accent`) sparingly — it is a directional accent, never a painted surface.
- Do keep headline hierarchy via scale and tracking, not weight or color.
- Do maintain `65ch` max-width on all body copy.
- Do collapse all multi-column layouts to a single column below `768px`.
- Don't add card shadows, glows, or layered elevation — motion conveys depth.
- Don't center the hero; the editorial look is left-aligned and asymmetric.
- Don't use more than two font weights on a single screen (400 and 500).
- Don't introduce a second accent or warm/cool gray mixing.
- Don't use images with text overlapped on top — every element keeps its own spatial zone.