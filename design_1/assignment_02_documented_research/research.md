# Assignment 2 · Documented research

**Status: COMPLETE — secondary desk research, three distinct primary publishers.**
This is product/experience research, not a survey, market-size study or user interview.
URLs were opened and their relevant content reviewed during this execution; access
timestamps and scope are recorded in [research-sources.json](research-sources.json).

## Question and method

How can a traveler remember accounts used on accommodation devices and identify an
appropriate next action at checkout, without assuming automatic sign-out?

First reviewed the [existing program](../stay_data_stay.py), account-selection and
summary sections (180–205, 287–307), its [portfolio case study](../../docs/stay-data-stay.md),
and the [original FigJam archive](../../figma_1/Stay%20Data%20Stay.jam). These explain
the product intent and existing assets; they are not independent user research.
Supplemented the missing external basis with the three authoritative sources below.
No service login, device inspection or program execution was performed.

## Sources, findings and design influence

| ID / source | Verified finding, paraphrased | Credibility and scope | Design influence |
|---|---|---|---|
| R1 · [Netflix — How to use Netflix on your hotel TV](https://help.netflix.com/en/node/25814) | For the supported hotel offering described, Netflix says information is cleared at checkout and provides manual sign-out instructions. | Provider's own product documentation; describes selected hotel integrations, not every TV or rental. | D1: avoid universal “still signed in” claims; distinguish a recorded service from a confirmed sign-out. |
| R2 · [Google — See devices with account access](https://support.google.com/accounts/answer/3067630?hl=en) | Google documents session review/sign-out; multiple sessions can share a device name, and activity timestamps need interpretation. | Provider's own account help; applies to Google, not all services. | D2: offer provider-specific recovery guidance when the traveler has left; do not present the checklist as live session detection. |
| R3 · [Australian Government Smartraveller — Cyber security when travelling overseas](https://www.smartraveller.gov.au/while-overseas/protecting-yourself-crime/cyber-security-when-travelling-overseas) | Advises signing out after use, avoiding remembered logins, and avoiding sensitive personal logins on publicly shared computers. | Government travel-safety guidance; broad overseas-travel context, not a product efficacy study. | D3: make prevention/manual review primary; never request service passwords and do not encourage shared-device email or banking. |

These sources establish relevant account-management behaviors, not how often
travelers forget or whether they want this product. Those demand/usability questions
remain open. A CISA travel PDF returned 403 when opened and is **not counted**.

## Synthesis and traceability

| Insight / interpretation | Corresponding design choice | Current evidence or gap |
|---|---|---|
| R1 + existing summary: the list is useful even when a system clears access | Keep account names visible and clarify “Recorded” | Existing concept screen shows the list; wording comprehension is untested |
| R2: help differs by provider and situation | Keep official-help recovery separate from account recording | Recovery hub is a brainstormed proposal, not built functionality |
| R3 + existing reminder flow: support a small manual checkout routine | Review only services already used; avoid collecting extra secrets | Existing CLI has prompts; automated delivery and real device logout are not verified |

Design choices above are **our inferences**, not recommendations to install a
particular app. Existing source prints reminder prompts; this does not prove a
background scheduler, push notification service, durable saving or remote logout.

## Limitations / next validation

No interviews, participant counts, conversion rates or forgetting-rate statistics
are available. The hypothetical Casey persona and the three-idea preference are
design assumptions. Use the [conversational walkthrough](../assignment_05_conversational_prototype/walkthrough.md)
to test comprehension and collect actual feedback later; none has been collected.

- [x] Specific product/experience research question.
- [x] Three distinct, credible sources with URLs, findings and scope.
- [x] Findings connected to concrete design decisions and limitations.

[Course index](../README.md).
