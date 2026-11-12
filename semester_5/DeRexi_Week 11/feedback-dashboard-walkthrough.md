# Feedback → Dashboard

**Duration: 8-minute core; 10–12 minutes with optional discussion.** Reuse **Sam Okonkwo (Employee, ID 8)** for answer feedback and **Lucy Chen (System Administrator, ID 2)** for organizational Dashboard visibility. **Maya Patel (Policy Owner, ID 4)** is optional for explaining departmental scope.

Use existing evidence by default. Any interactive rating must use the existing disposable fixture, never the normal Supabase-connected server. Follow the [local-only identity and isolated rehearsal instructions](demo-script.md). No accounts, production settings or live records need changing. This script is prepared, not a new rehearsal or live acceptance result.

| Time | Show / do | Say |
|---|---|---|
| 0:00–1:00 | Introduce Sam and show a DeRexi answer with **Was this helpful?** | “Employees can tell us whether an answer helped. This rating applies to the assistant's answer, not the employee's question or a policy approval decision.” |
| 1:00–2:00 | As Sam, select **Yes** or **No** on the answer. Point out the pending/saving state. | “We wait for the save to finish. A click or highlighted control by itself does not prove the feedback was recorded.” |
| 2:00–3:00 | Show saved confirmation and selected rating. | “This feedback is now on record. Each employee has one rating per answer; changing their choice updates that rating rather than adding another vote.” |
| 3:00–4:00 | Explain the handoff to Lucy. In the isolated fixture, change identity through its existing sign-in path; otherwise show the existing acceptance record. | “Employees do not gain Dashboard access by submitting feedback. We switch to an authorized administrator to review the aggregate.” |
| 4:00–5:00 | As Lucy, open **Dashboard** and its overview. Locate **Helpfulness** and the helpful/not-helpful counts. Reopen the view to fetch current data if necessary. | “The Dashboard summarizes saved ratings. We check the loaded result; this demonstration does not assume a live push update.” |
| 5:00–6:00 | Compare the saved choice with the aggregate counts, accounting for existing ratings. | “The helpfulness percentage is helpful ratings divided by all ratings, with UI rounding. Other ratings affect the result, so one No does not necessarily make the display zero percent.” |
| 6:00–7:00 | Explain Owner versus Admin scope and what the metric means. | “Admins see the organizational aggregate. Owners receive scoped departmental feedback associated with cited policy content. A low score is a signal to investigate, not automatic proof of a policy defect or regulatory noncompliance.” |
| 7:00–8:00 | Connect the result to human follow-up and close. | “The policy team can review confusing guidance, seek clarification and propose a reviewed revision. Feedback does not automatically rewrite policy or create an incident report.” |

**Optional 8:00–9:00 — failed save/retry:** Use the existing error screenshot. Explain that a failed new choice leaves the previous saved choice intact; retry after recovery and confirm the result. Do not treat an earlier success toast as proof the latest attempt saved. Do not induce an outage outside the disposable fixture.

**Optional 9:00–10:00 — changed vote:** Explain a Yes→No change: the total number of ratings stays constant while helpful decreases and not-helpful increases, provided no other ratings change. For an interactive comparison, establish the starting state first. Do not promise exact counts from an unrelated screenshot. Allow questions through minute 12.

## Existing evidence

- [Assistant with saved feedback](../DeRexi_Week%2010/evidence/screenshots/02-assistant-feedback-fixture.png).
- [Feedback save error](../DeRexi_Week%2010/evidence/screenshots/03-feedback-error-fixture.png): the older toast belongs to the previous successful save.
- [Week 10 test report](../DeRexi_Week%2010/test-report.md): I11–I18 verified persisted ratings, updates and departmental isolation; U19 checked the Admin Dashboard feedback aggregate.
- [Week 10 acceptance record](../DeRexi_Week%2010/uat-records.md): historical fixture context and screenshot limits.
- [Employee guide](employee-guide.md) and [System Admin guide](system-admin-guide.md).

There is no dedicated Week 10 overview screenshot proving the full feedback-to-Dashboard transition. The existing Admin triage screenshot shows the Incidents tab, so it must not be presented as a Helpfulness capture. Use the recorded U19 result for that step, or show the overview only in an authorized disposable rehearsal. Departmental fixture tests use a synthetic citation to verify scoping; they do not prove live retrieval quality. An uncited answer may not contribute to an Owner's departmental aggregate, so use Lucy for the main demonstration.

## Presenter check

Confirm the selected answer, saved rating, viewer identity and Dashboard scope. Keep simulation context explicit and credentials off screen. Local persona switching is development-only; production uses authorized individual sign-ins. A displayed zero without feedback is not evidence of dissatisfaction—check the counts. No live writes, new screenshots, accounts or infrastructure verification are required.
