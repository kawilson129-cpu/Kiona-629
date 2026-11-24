# Figma 1 · Coursework evidence and handoff

Four assignment packages are prepared around **Stay Data Stay**. The prompt calls
it “State Data Stay”; repository files consistently use “Stay Data Stay”, which is
preserved. No final polished report/PDF, application rewrite, commit or push.

## Rubric coverage

| Assignment | Evidence / prepared material | Verification status |
|---|---|---|
| [1 · Frames](assignment_1_frames/README.md) | Proposed 1440×960 [screen SVG](assignment_1_frames/stay-data-stay-frame.svg) + [layout spec](assignment_1_frames/frame-spec.json) | **PARTIAL**: native Design frame type/dimensions not verified |
| [2 · Images](assignment_2_images/README.md) | Archived board thumbnail, two byte-identical embedded PNGs, provenance, reused portfolio artwork | **VERIFIED** for existing FigJam image incorporation; new Design placement unverified |
| [3 · Styling](assignment_3_styling/README.md) | Existing visual direction, [tokens](assignment_3_styling/design-tokens.json) + [style SVG](assignment_3_styling/style-reference.svg) | **PARTIAL**: proposed styling documented; native font/style properties not verified |
| [4 · Components](assignment_4_components/README.md) | [600×88 grouped row SVG](assignment_4_components/account-row.svg), layer structure and reuse test instructions | **PARTIAL**: no verified native component/instances |

**Evidence score: 1/4 criteria verified, 3/4 partial.** This is documentary coverage,
not an instructor grade. If the instructor requires every item specifically in
**Figma Design**, confirmed Design-file coverage is **0/4** until the handoff is
executed; the single verified item is explicitly existing **FigJam** evidence.
All four packages are prepared, but preparation is not native-platform completion.

## Sources reviewed, in priority order

1. [Python program](../python_1/stay_data_stay.py): stay inputs (97–136), account menu
   (206–237), account summary (313–327), reminder preferences (368 onward). Reviewed
   as source only; no CLI execution, real account access or notification test.
   Six other coursework copies are byte-identical to one another and differ from
   the selected Python 1 copy; no version age is inferred from hashes.
2. Original [Stay Data Stay.jam](Stay%20Data%20Stay.jam),
   [VirtualCloset.jam](VirtualCloset.jam) and
   [Baby's First Algorithm.jam](Baby%27s%20First%20Algorithm.jam) are unchanged FigJam
   archives. The first is the cohesive primary evidence. July 20, 2026 metadata is
   **export time**, not an invented creation or completion date.
3. [Portfolio case study](../docs/stay-data-stay.md) and
   [project artwork](../docs/assets/images/stay-data-stay-project.png) supply context
   and visual identity. Artwork is not proof of a functioning mobile app. The new
   assets avoid claims of automated sign-out, background scheduling or live state.
4. DeRexi/other project assets were unnecessary: the higher-priority Stay Data Stay
   sources supply a coherent design subject. No new unrelated design was introduced.

No project Figma URL was found in searched repository text; archive metadata has no
developer-related links. A live file's object types cannot be inferred from exports.

## Evidence index

| Evidence | What it verifies / limits |
|---|---|
| [Original board thumbnail](evidence/stay-data-stay-original-thumbnail.png) | Untouched archive preview; not a newly captured Figma editor screenshot |
| [Account-log PNG](assignment_2_images/evidence/embedded-account-log.png) / [diagram PNG](assignment_2_images/evidence/embedded-flowchart-reference.png) | Exact original archive bytes; source attribution in Assignment 2 |
| [Archive inventory](evidence/archive-inventory.json) | Original members, file names, thumbnail sizes, export bounds/times; no native node-type proof |
| [Image provenance](evidence/extracted-image-provenance.json) | Original archive member → extracted file/hash |
| [Source manifest](evidence/source-manifest.json) | Preserved originals, program/artwork and root memory hashes |
| [Tool discovery](evidence/tool-availability.json) | No Figma-specific editing tool or connected document session available |
| [Local validation](evidence/validation.json) | Offline file/link/XML/PNG/hash/coordinate checks only; not a Figma import test |
| [Concurrent worktree observation](evidence/concurrent-worktree-observation.json) | Unrelated Python 2 PDF relocation appeared during validation; original/new bytes match and were left untouched |
| [One-file implementation handoff](FIGMA_HANDOFF.md) | Remaining native frame, image, editable styles and component verification |

## Remaining manual actions

Open one authorized Figma Design file and follow [FIGMA_HANDOFF.md](FIGMA_HANDOFF.md):
create the native frame, import/inspect imagery, confirm native text/shape styling,
create the row component plus linked instances and verify propagation. Save actual
editor captures and the real Design-file link before marking those items verified.
No additional screenshots are requested during this run; the named captures are
the future evidence needed to close the documented native-platform gaps.

Run local artifact checks with `python3 -B figma_1/validate_course.py`.
All new work is course-local; original project files remain unchanged. This index
records the session without modifying unrelated root memory or production code.

## Latest recheck

Repeated request: existing assignments/assets were reused without duplication. A fresh
tool discovery again found no Figma-specific tool or connected document session. No
new project link, native `.fig` file or Figma editor capture was found in the repository
search. Native rubric statuses therefore remain unchanged; local validation was rerun.
The original source files and unrelated Python 2 PDF relocation remain untouched.
