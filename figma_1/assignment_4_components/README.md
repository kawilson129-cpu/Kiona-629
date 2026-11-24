# Assignment 4 · Components

**Requirement:** create a reusable Figma component from grouped elements/layers and
document its structure and reuse. **Status: PARTIAL — grouped asset/specification
prepared; native component and instances UNVERIFIED.**

## Existing source and missing proof

[Stay Data Stay](../../python_1/stay_data_stay.py), lines 206–237 and 313–327,
defines account choices and displays selected accounts. That repeating item is the
source for a reusable account-summary row. Existing FigJam shapes/groups and
repeated screenshot rows do **not** prove a Figma Design component. No verified
main-component/instance relationship was found in the available evidence.

## Prepared candidate and structure

[account-row.svg](account-row.svg) is a new **600×88 SVG group**, not a native
component. It shares the screen's proposed style tokens and fictional account data.

```text
SDS / Account row                 proposed native component name
  Background                     rounded surface + border
  Marker                         circle + numbered text
  Content
    AccountName                  editable account name
    Supporting text              “Selected for this stay”
  Status                         surface + “Recorded” text
```

Reusability goal: one source for padding, background, marker and status styling;
each instance keeps its own account label/index. “Recorded” is sample design text,
not a live account status or assertion that an account was automatically signed out.

## Native Figma implementation and verification

1. Import the SVG beside the screen. Ensure account/index labels are native Text
   layers; recreate them if import outlines the text.
2. Select the whole row group and choose **Create component**, naming it
   `SDS / Account row`. Confirm the native Component icon/type.
3. Insert three **instances** from Assets into the frame at the three row positions,
   replacing the standalone copied SVG row groups. Override labels to Netflix,
   YouTube and Amazon Prime Video; keep instance links intact.
4. Change the main component's background temporarily and verify that all instances
   update; revert it. Capture the main component and selected instance properties,
   including the main-component relationship, as `component-in-figma.png` and
   `instance-in-figma.png` here. Record the actual result and file/node link.

[Official component instructions](https://help.figma.com/hc/en-us/articles/360038663154-Create-components-to-reuse-in-designs).
No component creation or propagation test above has been executed.

## Rubric checklist

- [x] Cohesive reusable item, layer structure and grouped import asset supplied.
- [ ] Actual Figma component created and editor properties evidenced.
- [ ] Linked instances and a real propagation check verified.

[Course index](../COURSE_INDEX.md).
