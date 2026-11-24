# Assignment 1 · Frames

**Requirement:** demonstrate a Figma Design frame and document its dimensions,
purpose, layout and source. **Status: PARTIAL — import kit complete; native frame
creation/type/dimensions UNVERIFIED.**

## Existing evidence and source

- [Stay Data Stay.jam](../Stay%20Data%20Stay.jam) is the original **FigJam** archive.
  [Original thumbnail](../evidence/stay-data-stay-original-thumbnail.png) shows its
  process board. A board, section or image is not proof of a Design frame.
- [Archive metadata](../evidence/archive-inventory.json) records a 400×372 thumbnail
  and a 7081.873046875×6580 export envelope. Neither is a native-frame dimension.
- [Program](../../python_1/stay_data_stay.py), lines 97–136 and 206–237, supplies stay
  fields/account selection; lines 313–327 supply the account-summary pattern.

## Prepared design and decisions

[stay-data-stay-frame.svg](stay-data-stay-frame.svg) is a **new SVG design study**,
not a Figma export or proof of a frame. [frame-spec.json](frame-spec.json) records:

| Property | Proposed value / purpose |
|---|---|
| Name / size | `SDS / Account summary` · **1440×960 px** |
| Purpose | Show a fictional stay's recorded accounts and checkout reminder |
| Layout | 64px outer margin; story/artwork left, account checklist right |
| Columns | Left x=64, width=568; right x=712, width=600 |
| Image | x=64, y=374, 568×355.2686; preserve original aspect ratio |
| Repeated rows | x=712; y=308/412/516; 600×88 each |

The calm green/ivory/gold direction follows existing Stay Data Stay artwork.
All selections are fictional. No account status, scheduler or working GUI is claimed.

## Native Figma implementation and evidence still needed

1. In a **Figma Design** draft, use the Frame tool (`F`), create the frame and set
   width/height to 1440/960. Name it as above.
2. Drag the SVG onto the canvas; put its imported layers inside that native frame
   at relative x=0/y=0. An imported SVG group alone does not satisfy this criterion.
3. Confirm the Frame icon/type, dimensions and child layers. Capture the selected
   frame with the Layers and properties panels visible; save an actual
   `frame-in-figma.png` here and record the real file/node link.

[Official frame instructions](https://help.figma.com/hc/en-us/articles/360041539473-Frames-in-Figma-Design).
No import or capture above has been performed in this session.

## Rubric checklist

- [x] Purpose, source, explicit dimensions and layout documented.
- [x] Import-ready SVG/spec prepared and locally validated.
- [ ] Native Figma frame and properties verified in the editor.

[Course index and shared evidence](../COURSE_INDEX.md).
