# Policy Owner review → System Admin approval → Library

**Duration: 8-minute core; 10–12 minutes with optional discussion.** Use the existing fictional identities: **Maya Patel (author, ID 4)**, **Jordan Rivera (independent peer Policy Owner, ID 9)** and **Lucy Chen (independent System Administrator, ID 2)**. **Sam Okonkwo (Employee, ID 8)** demonstrates the published Library view.

Present the existing screenshots by default. Any interactive approval/publication must occur only in the existing disposable fixture, never the normal Supabase-connected server. Follow the [local-only identity and isolated rehearsal instructions](demo-script.md). No new accounts, schema changes or owner seeding are needed. This is a prepared script, not a new rehearsal or live acceptance result.

| Time | Show / do | Say |
|---|---|---|
| 0:00–1:00 | Introduce Maya's saved working draft in Governance. Show its title, version and status. | “Maya has prepared a policy working copy. It is not yet employee guidance. The current published Library content stays separate while review takes place.” |
| 1:00–2:00 | Show submission to Jordan, another eligible Owner in the same fixture department. Point out author versus reviewer. | “The author cannot peer-review their own draft. We confirm reviewer eligibility and assignment rather than assuming a name grants permission.” |
| 2:00–3:00 | As Jordan, open **Peer Reviews**. Inspect the body, metadata, dates and history; compare against the published baseline for a revision. | “The peer checks whether the proposed guidance is clear, accurate and supported. They can approve, request changes or reject; changes and rejection require a comment.” |
| 3:00–4:00 | Show peer approval and **Pending final approval**. Open the item as Lucy under **Final Approvals**. | “Peer approval advances the draft, but does not publish it. Final approval belongs to an independent System Administrator who is neither the author nor the peer.” |
| 4:00–5:00 | As Lucy, review the content, peer decision and history, then show final approval. | “The item is now approved pending publication. Approval and publication are separate actions. A saved content edit would reset both approvals and require fresh review.” |
| 5:00–6:00 | Open **Publication**, check unique version, baseline and effective date, then show explicit publication of an eligible item. | “The administrator publishes on or after the effective date. DeRexi does not automatically publish when the date arrives. Conflicting versions or changed baselines must be resolved first.” |
| 6:00–7:00 | As Sam, open **Library**, locate the published title and check its version/body against the approved draft. | “Employees can now read the published policy. They do not receive access to draft queues or approval controls. We verify the actual Library result rather than treating an approval message as proof of publication.” |
| 7:00–8:00 | Return to Governance history and summarize the distinct author, peer, final approver and publication steps. | “The handoff preserves independent review and a traceable publication history. This evidence comes from isolated development verification; production activation and human acceptance remain pending.” |

**Optional 8:00–9:00 — revision branch:** Explain that a request for changes returns the item to its author. Saving edits clears the reviewer and approvals; choose an eligible peer and repeat review. The existing Library version remains available until a replacement is published. Do not alter an approved item merely to demonstrate this outside a disposable fixture.

**Optional 9:00–10:00 — errors:** Explain future effective date, stale revision/baseline and workspace outage. Preserve unsaved work, refresh/compare and retry appropriately. Do not bypass independent review, invent reviewers or change permissions. Allow audience questions through minute 12.

## Existing materials

- [Document preview](../DeRexi_Week%2010/evidence/screenshots/05-document-preview-fixture.png): optional context for Maya's draft preparation.
- [Independent peer review](../DeRexi_Week%2010/evidence/screenshots/06-peer-review-fixture.png).
- [Administrator publication](../DeRexi_Week%2010/evidence/screenshots/07-admin-publication-fixture.png).
- [Library example](../DeRexi_Week%2010/evidence/screenshots/11-mobile-library-fixture.png): existing mobile Library evidence, not proof that this capture shows the same newly published policy.
- [Week 10 acceptance record](../DeRexi_Week%2010/uat-records.md): historical fixture verification of independent publication and Library checking.
- [Policy Owner guide](policy-owner-guide.md) and [System Admin guide](system-admin-guide.md).

Existing screenshots illustrate selected states, not an uninterrupted recording. Narrate uncaptured transitions as workflow explanation, or show them only in the disposable fixture. Confirm the same policy/version across interactive steps; do not imply unrelated captures form a continuous live transaction. Preserve the screenshots' simulation context.

## Presenter check

Confirm the author, eligible department peer and independent Admin before each handoff. Persona switching is local-development-only; the fixture's mocked login differs from the ordinary local selector. Production requires separately authorized individual sign-ins. Do not show credentials, make live writes or claim schema/Auth/infrastructure readiness. Missing live peer capacity remains a deployment blocker, not permission to create a reviewer.
