# User acceptance records

**Agent-executed simulation, November 10, 2026; stakeholder acceptance PENDING.** Fictional personas reuse existing business-user IDs/roles in a disposable fixture. Emails are `example.invalid`; provider login, feed data and any banking guidance are synthetic. These are not real bank approvals.

| Persona | Scenario and expected acceptance | Result |
|---|---|---|
| Sam Okonkwo, Employee (8) | Invalid password rejected/cleared; login opens authorized navigation; denied Governance/dashboard/incident management; logout denies API reads and clears notices | PASS, U00–U02/U08–U12/U31, I25 |
| Sam, Employee | Ask uncertain question; open actual linked Messaging thread; see owner reply/notification; rate answer; save error preserves prior choice; retry updates one row | PASS, I01–I18, U03–U07 |
| Maya Patel, Policy Owner (4) | Upload real DOCX; preview extracted text; mandatory confirmation; save draft; select Jordan as independent reviewer; self-approval denied | PASS, U13–U17; 47 parser/intake checks |
| Jordan Rivera, Policy Owner (9) | Receive governance notice; approve Maya's submission; receive assigned clarification and send reply | PASS, U17 and I05–I09; reused lifecycle permissions tests |
| Lucy Chen, System Administrator (2) | Independently approve/publish; verify Library; see saved feedback; assign employee incident through authorized real API | PASS, U18–U20; I19–I24; 102 lifecycle checks |
| Maya, Policy Owner | Open Pulse policy action; create revision with exact source reference and published baseline; old Library version survives draft/outage | PASS, U21–U26 |
| Maya/Sam on mobile | Owner Library/Governance fit 390px; Employee Assistant feedback fits; synthesized touch opens Messages; reply persists; sign-out fits and clears state | PASS, U27–U32, including U28b/U29a–c |

Desktop: Chromium, 1440×1000. Mobile: Chromium device metrics **390×844**, touch emulation enabled; actual layout width is asserted and final screenshot dimensions verified. No physical handset, Safari/iOS, Android browser or screen-reader test is claimed. Keyboard Tab from email to password was exercised. Other button clicks/forms use browser DOM actions; U29b specifically uses CDP synthesized touch start/end.

Invalid/error/denied cases also include blank Assistant input, strict boolean feedback, private-answer access, non-answer ratings, incident assignment permissions, missing incident category, premature document save, unsafe/malformed uploads, missing Governance tables, outage retry and independent-review restrictions. Expected 401/403/404/409/422 responses are passing denial tests, not test failures.

## Screenshot index and requirements

All final captures are **fixture** evidence. Baseline image 00 shows the old false success. Names 01–15 show successful or intentionally rejected/error states. The mobile continuation adds a fixed simulation label; other captures have fixture filenames and simulation text in letterhead/footer, which may fall outside the scrolled viewport. Context here always governs interpretation.

| File in `evidence/screenshots/` | Evidence |
|---|---|
| `00-before-fix-feedback-fixture.png` | Confirmed old UI success without database rating; API evidence is in `browser-before-fix-results.json` |
| `01-desktop-signin-fixture.png` | Password entry, existing visual identity |
| `02-assistant-feedback-fixture.png` | Real fixture Assistant result and saved feedback |
| `03-feedback-error-fixture.png` | Failure status retains Yes; previous toast is from the immediately preceding successful save |
| `04-employee-messaging-fixture.png` | Assistant deep link opens actual persisted thread |
| `05-document-preview-fixture.png` | Real parsed DOCX, metadata and confirmation |
| `06-peer-review-fixture.png` | Independent peer decision |
| `07-admin-publication-fixture.png` | Independent administrator publication |
| `08-admin-triage-fixture.png` | Administrator assignment through real fixture API |
| `09-pulse-revision-fixture.png` | Source URL and published/working revision context |
| `10-workspace-outage-fixture.png` | Honest queue outage and retry |
| `11-mobile-library-fixture.png` | 390×844 protected Library |
| `12-mobile-governance-fixture.png` | 390×844 Owner workspace |
| `13-mobile-assistant-fixture.png` | 390×844 saved feedback and routed answer |
| `14-mobile-messaging-fixture.png` | 390×844 reply/navigation flow |
| `15-mobile-signout-fixture.png` | 390×844 signed-out state |

`attempt-final.png` is diagnostic harness-attempt evidence, not final acceptance. Preserve it separately in interpretation.

Required future live screenshots, after a separately authorized activation: real HTTPS sign-in and signed-out API denial; independently reviewed/published policy and preserved revision baseline; actual administrator incident triage; safe cookie **attributes only**, encryption/retention and direct-client permission evidence. Never capture passwords, JWT values, refresh cookies, connection strings or private employee/incident content. **These live captures remain unavailable.**

## Scoped UI quality review

The actual DeRexi ivory/espresso/champagne UI was used as visual authority; root `DESIGN.md` describes the separate portfolio. No redesign or new CSS was introduced. The Impeccable detector reported three advisory radius mismatches in unchanged skeleton styles; they are outside this functional fix and not confirmed MVP defects. Feedback now exposes `aria-pressed`, pending/disabled states and a live status; desktop error and final mobile screenshots were visually inspected. Responsive overflow and synthesized touch were checked. Full contrast, screen-reader, performance profiling and cross-browser audits were not performed, so no broad accessibility or UI score is asserted.
