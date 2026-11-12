# Week 12 demo — 10 minutes

Use the existing fictional personas and disposable [support fixture](../../derexi-policy-pilot/backend/tests/serve_support_fixture.py). It imports earlier fixture setup without running older evidence-writing entry points. It uses SQLite and mocked provider/feed/email; no real account creation or provider integration. Existing ordinary persona switching remains loopback-development-only; this fixture uses its existing mocked sign-in path.

| Time | Demonstrate | Explain |
|---|---|---|
| 0–1 min | Introduce fictional Aurum and Sam | DeRexi assists the existing IT ticketing system; urgent reporting must not wait. |
| 1–2 min | Ask a normal policy question, then “I clicked a phishing link” | Actual event detection gives urgent guidance and concise secret-free questions, without auto-submitting. |
| 2–4 min | Answer questions, review bound identity/department/destination, edit, then explicitly confirm | The reviewed request becomes an internal reference; no email was sent by confirmation. |
| 4–5 min | Attempt handoff while outbound is OFF | Honest disabled state: no delivery/ticket claim. Use established IT/Security channel. |
| 5–6 min | As Lucy, open Technical Routing; show approved choices, department rules, route validation and scoped delegation | No arbitrary destinations, no SMTP credentials, no accidental live test-send. Routing-only delegates gain no policy approval access. |
| 6–7 min | Show existing isolated mock acceptance evidence | SMTP acceptance is not inbox delivery or ticket creation. Unknown outcomes never auto-retry; known pre-send failures use capped/cooldown retries. |
| 7–8 min | Show saved feedback/Dashboard and clarification Messages | Reuse the existing [feedback](feedback-dashboard-walkthrough.md) and [employee](employee-messages-walkthrough.md) evidence. |
| 8–9 min | Show independently reviewed Governance publication and Pulse revision | Reuse [governance](governance-library-walkthrough.md) and [Pulse](pulse-revision-walkthrough.md) evidence; drafts do not replace Library. |
| 9–10 min | Show mobile views and readiness checklist | Distinguish native Windows checks, isolated browser evidence and pending live production gates. |

Do not turn on SMTP or create real users to improve the presentation. Use the new labelled screenshots in `evidence/final-integration-20261112/screenshots/` with their result JSON. Prior screenshots remain in their original folders. The mock fixture's delivery-mode endpoint exists only in that fixture, requires an Admin, and must never be deployed with the application.

Setup from canonical project folder, using its existing virtual environment:

```text
python backend/tests/serve_support_fixture.py
```

Open `http://127.0.0.1:8041/ui/`. Stop only this fixture process after rehearsal. A demonstration recording/human sign-off is not claimed by preparing this script. Exact automated browser results and limits are recorded separately.
