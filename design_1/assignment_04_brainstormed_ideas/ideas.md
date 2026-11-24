# Assignment 4 · Three brainstormed ideas

**Status: COMPLETE.** These are newly documented alternatives synthesized from
existing work and A2 desk research, not an invented historical brainstorming meeting
or a participant preference result.

| Idea | Explanation / problem addressed | Potential benefits | Limitations and evidence |
|---|---|---|---|
| I1 · Trip-linked account shortlist — **preferred** | Record only the services used during a stay, then review a compact checklist at checkout. It addresses remembering which accounts need attention. | Directly reuses CLI account selection/summary and the existing account-row screen; keeps the workflow small. | Depends on user entry and follow-through; cannot know real session state. Demand, comprehension and reminder effectiveness are untested. |
| I2 · Physical departure cue | A door-hanger or packing-card prompt asks the traveler to review account access before leaving. It addresses noticing the task amid departure activities. | No account connection or app setup; can complement an existing personal checklist. | Can be ignored or unavailable; cannot remember which services were used. Inspired by the door-hanger concept visible in existing project artwork, not a manufactured/tested product. |
| I3 · Provider-specific recovery guide | A small directory points to official session-management guidance after the traveler has left the device. It addresses uncertainty about recovery actions. | Useful after departure; does not require the product to hold third-party credentials. | Provider instructions and session visibility differ and can change; guide links do not perform logout or guarantee complete coverage. Newly inferred from A2, not implemented. |

## Preferred solution and rationale

Choose **I1** as the prototype focus because it has the strongest existing evidence:
the [Design 1 program](../stay_data_stay.py), lines 180–205 and 287–307, already records
service selections and presents a summary. The existing
[account-checklist visual](../assignment_05_conversational_prototype/prototype-screen.svg)
provides a reusable presentation surface. This is a feasibility/reuse judgment,
not proof that users prefer I1 or that it reduces incidents.

I2 is a genuinely different, physical intervention. Its visual seed is the existing
[Stay Data Stay hero artwork](../../docs/assets/images/stay-data-stay-hero.png);
the door-hanger illustration is conceptual imagery, not field evidence.
I3 is a recovery-focused alternative informed by the provider documentation in
[A2](../assignment_02_documented_research/research.md). It may later complement I1,
but the prototype does not claim it is implemented.

## Decision criteria and next questions

Use minimal input burden, clarity about real account state, reuse of existing assets
and feasibility without third-party credentials. No numeric scoring or measured
preference is invented. Ask travelers which approach they would notice and use;
test whether I1's “Recorded” wording is confused with confirmed sign-out. Reconsider
the preferred approach if actual feedback shows the assumed departure routine is wrong.

- [x] Three distinct solutions with problems, benefits and limitations.
- [x] Existing program, visual iterations and research reused with attribution.
- [x] Preferred solution identified with a reasoned, explicitly untested rationale.

[Course index](../README.md).
