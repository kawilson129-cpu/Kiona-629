# DeRexi demonstration — 10–12 minutes

## Presenter setup and safety

For the focused employee question → clarification → Messages presentation, use the [8–12 minute walkthrough](employee-messages-walkthrough.md). This broader script remains available for the complete MVP demonstration.

For Policy Owner review → System Admin approval → Library, use the [matching governance walkthrough](governance-library-walkthrough.md), including the required separate publication step.

For Pulse article → proposed policy revision, use the [focused Pulse walkthrough](pulse-revision-walkthrough.md), ending with a saved proposal and unchanged published Library.

For Feedback → Dashboard, use the [focused feedback walkthrough](feedback-dashboard-walkthrough.md), showing persisted ratings, aggregate interpretation and viewer scope.

This is a prepared script, not a newly executed rehearsal or live UAT. Use the existing Week 10 screenshots as the default demonstration for write workflows. They are labelled isolated simulations. **Do not run writes against the configured Supabase database.** An ordinary local server may still connect to the live database: persona mode does not isolate storage.

For an interactive rehearsal, use only the existing isolated fixture described below, after confirming it uses disposable SQLite and mocked provider/feed data. Reuse existing fictional users; create no accounts or owners. If a prerequisite is missing, use screenshots and explain the limit. Never apply a schema/seed or change RBAC to make a demo succeed.

Existing demonstration identities from Week 10 (not real Auth accounts):

| Person | Business ID | Demonstration responsibility |
|---|---|---|
| Sam Okonkwo | 8 | Employee questions, Messages, feedback and incident report |
| Maya Patel | 4 | Policy Owner author/revision |
| Jordan Rivera | 9 | Independent peer Owner in the Week 10 fixture department |
| Lucy Chen | 2 | Independent System Administrator approval/publication and triage |

Fixture department eligibility does not prove live peer capacity. The historical live owner-capacity proposal remains unapplied.

## Local development persona switching only

1. Follow the [project setup](../../derexi-policy-pilot/README.md). Keep the server bound to loopback, direct and without forwarded headers; do not tunnel it or expose it on a LAN.
2. In private local configuration only, set `DEREXI_ENV` to development and explicitly enable `DEREXI_DEV_AUTH`. These are local mode choices, not credentials. Optionally limit existing business IDs with `DEREXI_DEV_USER_IDS`. Restart the local process.
3. Open `http://127.0.0.1:8000/ui/`. Choose an existing allowed identity from the entry chooser or **Signed in as** selector. Wait for the workspace/name/navigation to refresh before continuing.
4. Switch Sam → Maya → Jordan → Lucy at the relevant steps. The server issues signed short-lived identities and applies the same roles/department checks; changing an ID does not grant arbitrary permission. Expired/invalid selections must reauthenticate.
5. In production the selector is disabled and chooser hidden. Use separately authorized real accounts and sign out/sign in normally. Never enable developer personas to repair production sign-in.

**No-write option:** use these instructions to explain the mechanism while showing prior screenshots. No persona token or password needs to appear in a presentation.

## Optional isolated interactive rehearsal

The existing [Week 10 fixture server](../../derexi-policy-pilot/backend/tests/serve_week10_fixture.py) provides its own mocked browser sign-in rather than the ordinary local persona chooser. Do not confuse its accounts/credentials with Supabase Auth. Read its existing setup and [Week 10 UAT](../DeRexi_Week%2010/uat-records.md); use only its existing fictional fixture identities and fixture-specific settings. Do not invent credential values or paste them into coursework. If its known setup is unavailable, use the screenshot walkthrough.

From the canonical project folder, after verifying fixture isolation:

```text
python -m uvicorn serve_week10_fixture:fixture.main.app --app-dir backend/tests --host 127.0.0.1 --port 8031 --no-proxy-headers --no-access-log
```

Open http://127.0.0.1:8031/ui/ after confirming that port belongs to this fixture, not an unrelated running service. This import-based launch skips the legacy script entry point that rewrites a Week 10 input file; do not run that entry point during Week 11. Original retention is optional and is not needed for this walkthrough. Stop only this rehearsal process with Ctrl+C. The fixture is development evidence and may display simulation labels; those labels must never be injected into the normal application. Running the fixture or a write rehearsal was not part of Week 11 documentation validation.

## Timed walkthrough and spoken cues

| Time | Action and narration | Expected result / existing evidence |
|---|---|---|
| 0:00–1:00 | “DeRexi connects bank employees to published guidance, policy owners and incident responders. Aurum Capital Bank and these people are fictional.” Explain isolated demonstration versus pending live acceptance. | Sign-in screenshot 01; no account creation. |
| 1:00–2:00 | As Sam, ask about loan application record retention. Read the policy reference and browse Library. “The source/version lets the employee check the guidance.” | Assistant/feedback 02 and mobile Library 11. A prepared query is illustrative; do not promise a specific live rank. |
| 2:00–3:15 | Ask a question the library cannot confidently answer. Follow the clarification link to Messages; show Owner reply and unread notification. Choose answer feedback and wait for saved state. | Messages 04 and feedback 02/03. Explain failed save/retry retains prior rating. |
| 3:15–5:00 | As Maya, show DOCX preview and reviewed confirmation. Save a working draft; explain PDF support, 5 MB/20,000-character limits and no OCR. Select eligible independent Jordan for peer review. | Preview 05; use the existing [fictional input](../DeRexi_Week%2010/evidence/inputs/Customer%20safeguards.docx), not a customer document. Preview alone is not saved. |
| 5:00–6:30 | As Jordan, review comparison/history and peer-approve. As Lucy, independently final-approve and explicitly publish an eligible effective-date version. | Peer 06, publication 07. Self-approval is denied; saved edits reset approvals. |
| 6:30–7:30 | Return to Library to show published version. As Maya, open Pulse and start a source-linked revision. “News informs drafting; it does not automatically change policy.” | Pulse revision 09; Library baseline stays intact while draft/outage 10 exists. |
| 7:30–9:00 | As Sam, report: “Demonstration only: a suspicious email requested a password; no link opened.” Choose a category and confirm submission. As Lucy, open Dashboard → Incidents, find report, assign an existing eligible handler and confirm; demonstrate escalation only in disposable fixture. | Admin triage 08. Explain employee cannot assign/manage incidents, and reports require human follow-up. Existing screenshot proves fixture triage, not a new live submission. |
| 9:00–10:00 | Show mobile Messages/Assistant and sign out. Explain protected access after logout and unresolved deployment gates. | Mobile 13–15; previous results are emulation, not physical-phone acceptance. |

All screenshot numbers refer to the linked [presentation index](presentation.md). If time is limited, retain Assistant→Messages, independent publication, and incident→Admin triage; narrate other evidence.

## Rehearsal checklist

- [ ] Presenter has reviewed this script; no Week 11 rehearsal execution is claimed.
- [ ] Existing screenshots and input open locally; all simulation labels/context remain visible or explained.
- [ ] Correct fictional user/role is stated before each handoff; no real accounts created.
- [ ] Any interactive writes are confirmed disposable; otherwise use screenshot mode.
- [ ] No real `.env`, password, JWT, cookie, private mapping or customer material is on screen.
- [ ] Draft versus published baseline and peer versus final approval are explained.
- [ ] Incident report and Admin triage are shown as separate responsibilities.
- [ ] Error fallback is ready: show screenshot 10 for workspace outage, preserve work, retry later; never weaken permissions.
- [ ] Finish by stating real Auth/RLS/infrastructure/live UAT are pending, then close only rehearsal resources.

## Likely questions

**Does Pulse prove a policy is compliant?** No. Verify the original publication and complete the review process.

**Can an Admin approve their own draft?** No. Final approval is independent of author and peer.

**Is it deployed to the portfolio?** The portfolio is on GitHub Pages; the Python application requires a separate approved runtime host.

**Is it production-ready?** Development evidence is prepared. The [release checklist](release-checklist.md) lists unresolved production gates; live human acceptance has not happened.
