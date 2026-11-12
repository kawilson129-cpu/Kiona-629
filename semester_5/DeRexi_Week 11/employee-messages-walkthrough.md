# Employee question → clarification → Messages

**Duration: 10 minutes** (8-minute core, with two optional 1-minute extensions). Presenter actions and speaker cues are below. Reuse fictional **Sam Okonkwo (Employee, ID 8)** and **Jordan Rivera (Policy Owner, ID 9)**; create no accounts.

Use existing screenshots by default. Interactive submission/replies must use the existing disposable fixture, never the normal Supabase-connected server. See [local-only persona switching and isolated rehearsal setup](demo-script.md). The ordinary local selector and mocked fixture login are different sign-in paths; neither is production login. This script is prepared, not newly rehearsed or live UAT.

| Time | Show / do | Say |
|---|---|---|
| 0:00–1:00 | Introduce Aurum Capital Bank and Sam. Show Assistant and the signed-in identity. | “DeRexi helps employees find policy guidance and reach the responsible person when the policy does not fully answer their question. Aurum and these users are fictional.” |
| 1:00–2:00 | As Sam, enter **“How do I handle a hypothetical policy exception?”** This is the existing Week 10 demonstration question. | “Sam needs help with an exception. The assistant should recognize when the available policy evidence is insufficient rather than invent permission.” |
| 2:00–3:00 | Show the clarification response and any policy reference. Point out **Open thread**. | “This is a request for human clarification, not an approved exception. A policy reference gives context; it does not authorize an action outside the policy.” |
| 3:00–4:00 | Select **Open thread**. In Messages, show the original question, routing/assigned owner and thread status. | “The question carries into Messages, preserving context so Sam does not have to start again. We check the actual assigned owner rather than assuming who received it.” |
| 4:00–5:00 | Show an employee follow-up in the same thread. For example: **“Which approval steps should I follow before proceeding?”** Wait for the saved reply. | “Sam adds the missing context here. A saved message is different from text still sitting in the composer.” |
| 5:00–6:00 | Show Jordan's existing assigned clarification thread and reply. In an isolated interactive rehearsal, switch to the actual assigned eligible Owner; use Jordan only when that assignment is confirmed. | “Only an authorized participant can respond. The policy owner explains the next steps; a message is not a substitute for the institution's formal exception approval.” |
| 6:00–7:00 | Return to Sam. Show the notification/unread indicator, reopen the thread and read the response. | “Sam returns to the same conversation and can ask a follow-up. Reading a message does not automatically mean the request is resolved.” |
| 7:00–8:00 | Show thread status and explain resolution by the authorized participant when the question is addressed. Close the core walkthrough. | “We have followed one question from uncertainty to a traceable human conversation. Production authentication, access controls and live acceptance still require the deployment checks.” |

**Optional extension A, 8:00–9:00:** Show the [existing mobile Messages capture](../DeRexi_Week%2010/evidence/screenshots/14-mobile-messaging-fixture.png). Explain that the original fixture's remote-signature question is a separate example, not the exception thread above. Previous mobile evidence is browser emulation, not a physical-device test.

**Optional extension B, 9:00–10:00:** Explain a failed send/session expiry: preserve the text, verify whether it saved before retrying, and sign in again if required. If routing is missing or the owner does not respond, contact the responsible policy team/Admin through the established escalation process. Do not change roles, create users or bypass access restrictions. Allow questions through minute 12 if needed.

## Existing evidence to open beforehand

- [Assistant response](../DeRexi_Week%2010/evidence/screenshots/02-assistant-feedback-fixture.png): includes answer/feedback context.
- [Question opened in Messages](../DeRexi_Week%2010/evidence/screenshots/04-employee-messaging-fixture.png): Week 10 U07 verified that **Open thread** opened the persisted exception question.
- [Week 10 acceptance records](../DeRexi_Week%2010/uat-records.md): existing Owner reply and mobile messaging evidence, with scope limits.
- [Employee guide](employee-guide.md): permissions, error handling and escalation.

The screenshots do not capture every step of one uninterrupted conversation. Narrate uncaptured steps as the intended workflow, or demonstrate them only in the disposable fixture. Do not imply that the exception screenshot and the separate remote-signature thread are the same conversation. If a new question does not route as expected, use the existing evidence and explain lexical-retrieval variability; do not fabricate routing or alter the application.

## Presenter check

Open the evidence before presenting; confirm the role and thread at each handoff. Keep simulation context explicit and credentials off screen. Local persona switching is development-only; production uses authorized individual sign-ins. No live writes, accounts, new screenshots or application changes are needed for this walkthrough.
