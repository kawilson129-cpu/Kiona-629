# Verification · JavaScript 1 final project

## Verified results

| Evidence | Actual result | Scope |
|---|---|---|
| [Static/syntax results](evidence/static-results.json) | 12 PASS / 0 FAIL | Node syntax, single deferred script/no inline JS, local CSS, IDs/labels, source preservation, documentation/source-line/link checks, descriptive identifiers |
| [Browser results](evidence/browser-results.json) | 33 PASS / 0 FAIL | Real installed Chrome/CDP, actual local HTML/CSS/script; no DOM or calculation mocks |
| [Calculation matrix](evidence/calculation-matrix.json) | 100 PASS / 0 FAIL | Every 1–5 impact × 1–5 likelihood × four Boolean-flag combinations; one grouped browser check B05 |
| [Desktop screenshot](evidence/desktop-high-priority.png) | Captured | 1280px layout: High priority, 3 × 5 = 15 |
| [Mobile screenshot](evidence/mobile-immediate-priority.png) | Captured | Emulated 390px viewport: Immediate attention, sensitive-data override, 3 × 1 = 3 |

**45 check assertions pass; do not add the 100 B05 matrix cases again.** Real console
output is captured by Runtime.consoleAPICalled; B03 includes its resolved object and
matches it to the DOM. B04 verifies String/integer Number/Boolean values. B06–B14
exercise threshold and Boolean decisions. B15–B19 cover input changes, validation,
clear/reset and stale-result prevention. B20–B23 verify native keyboard selection,
focus and Enter calculation. B25/B32 establish one script and only local asset
requests. B28–B31 cover 390px/320px layout, targets and reduced motion.

No backend, network API, storage, credentials, customer data or production incident
process is involved. The test server serves only final_project on loopback and uses
an ephemeral port. Screenshot content consists of synthetic classroom inputs.

## Initial failures retained honestly

The [first browser run](evidence/browser-results-initial.json) and
[second keyboard attempt](evidence/browser-results-keyboard-attempt2.json) each
record **31 PASS / 2 FAIL**. B21 (native select keyboard change) and dependent B23
(Enter calculation) failed under incomplete CDP key-event synthesis; the 100-case
matrix and all other checks passed. An intermediate retry safely refused a stale
course-profile lock; a read-only PID check established the old browser had exited.

The test harness was corrected to include macOS native key codes and character text,
using the native select's numbered-option type-ahead. The final actual run passes
B21 and B23. **No application-code change was needed for those failures.** Initial
results remain evidence, not silently replaced successful claims.

## Reused implementation and visual review

The calculator inherits canonical DeRexi paper/ink/champagne tokens, serif headings,
hairlines, semantic controls and DOM/event/textContent patterns. Plum/cranberry are
pinned local accents, and system fonts preserve offline operation. Root DESIGN.md
is the separate portfolio identity and is unchanged. The design detector reported
palette/type/radius differences against that portfolio; these are intentional local
adaptations, not a reason to change production. A source/capture finish review found
no material visual/accessibility blocker within desktop1280/mobile390 evidence.
This review is not a screen-reader or WCAG certification.

## Reproduction and limits

Use the exact commands in the [README](README.md). Result JSON includes actual
execution timestamps. Source references and line ranges for every criterion are
recorded in [rubric-map.json](evidence/rubric-map.json) and validated locally.

Not tested: Safari/Firefox/Edge, physical mobile devices, screen-reader interaction,
real organizational incident scoring or production systems. Mobile results use
browser emulation. These are outside the eight supplied criteria; there is no
mandatory unresolved rubric requirement. No simulated value is represented as an
operational metric, banking risk assessment, successful ticket or API result.

## Session record and write boundary

All new files are inside javascript_1. The user's explicit no-unrelated-files boundary
supersedes the root-memory update convention; this record preserves the session
without changing MEMORY.md. Existing unrelated Design Documentation PDF movement
was left untouched. No dependency installed, production change, commit or push.
