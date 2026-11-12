# Pulse article → proposed policy revision

**Duration: 8-minute core; 10–12 minutes with optional discussion.** Reuse **Maya Patel (Policy Owner, ID 4)**. The goal is a saved, source-linked working revision, not approval or publication.

Use existing screenshots by default. Any interactive save must use the existing disposable fixture, never the ordinary Supabase-connected application. Follow the [local-only persona and isolated rehearsal instructions](demo-script.md). Create no accounts or policies in the live database. This is a prepared script, not newly executed UAT.

| Time | Show / do | Say |
|---|---|---|
| 0:00–1:00 | Introduce Maya and open **Pulse**. | “Maya monitors regulatory developments that may affect bank policy. Pulse helps identify an item for human review; a news article does not itself change our policy.” |
| 1:00–2:00 | Select a relevant article. Show publisher, title, publication date, category and status. | “We distinguish proposed rules, final rules, notices and guidance. The publication date is not automatically the policy's effective date.” |
| 2:00–3:00 | Point to the original publisher link. In a real review, verify the official publication and applicability before drafting. | “The summary is a starting point. We check the original source, scope, deadlines and relevance rather than assuming every article creates a new requirement.” |
| 3:00–4:00 | As Maya, choose **Propose policy action**. Show the Governance editor and **Pulse source · human review required** section. | “The handoff carries the source title, URL, date and context into the working copy. It does not generate an approved policy or bypass Governance.” |
| 4:00–5:00 | Select the correct existing policy as the revision baseline. Check its current published version/content. | “We are proposing a revision to this policy, not accidentally creating an unrelated new policy. The baseline tells reviewers exactly what is currently published.” |
| 5:00–6:00 | Review/edit the proposed body, summary, unique version, category and relevant dates. Confirm reviewed text/metadata before saving the draft. | “Maya writes the proposed changes based on verified applicability. Article text and summaries are not automatically authoritative policy wording.” |
| 6:00–7:00 | Show the saved working revision, retained source reference and comparison with its published baseline. | “We confirm that both the source and the intended baseline survived saving. A preview or unsaved form alone is not a stored revision.” |
| 7:00–8:00 | Open **Library** and verify that the existing published version remains unchanged. Explain the next review steps. | “Employees continue using the published policy. This proposal still needs an independent department peer, independent Admin approval and explicit eligible-date publication.” |

**Optional 8:00–9:00 — next handoff:** Explain submission to an eligible peer and the [independent approval/publication walkthrough](governance-library-walkthrough.md). Saved edits invalidate approvals. Do not approve or publish as part of this focused proposal demonstration.

**Optional 9:00–10:00 — stale feed/error:** Explain source-unavailable/stale notices and a Governance save error. Verify the official publication separately, preserve unsaved text, check whether a save succeeded before retrying, and contact Admin if the workspace remains unavailable. Do not seed users, apply schema or weaken access to continue the demo. Allow questions through minute 12.

## Existing demonstration evidence

- [Source-linked revision screenshot](../DeRexi_Week%2010/evidence/screenshots/09-pulse-revision-fixture.png).
- [Governance outage screenshot](../DeRexi_Week%2010/evidence/screenshots/10-workspace-outage-fixture.png).
- [Week 10 acceptance record](../DeRexi_Week%2010/uat-records.md): U21–U23 verified source handoff, saved source/baseline and unchanged published version; U24–U26 covered Library availability during workspace outage and retry.
- [Policy Owner guide](policy-owner-guide.md): Pulse use, drafting, review and escalation.

The existing fixture article is **“Customer safeguards policy review”** and is explicitly synthetic. Its FDIC-shaped fixture URL is not a real regulatory publication: do not open it as evidence of an official rule, claim applicability or replace it with an unverified live article. In screenshot mode, explain the source-verification step without claiming it occurred. Existing evidence demonstrates the application handoff, not regulatory accuracy.

## Presenter check

Confirm Maya's identity, the article's simulation context, source reference, intended policy baseline and saved draft state. Preserve screenshot labels/context. Local persona switching is development-only; production uses authorized individual sign-ins. Pulse may be readable without Governance permission, but **Propose policy action** is role-gated. No new accounts, live writes, screenshots or infrastructure verification are required. If the selected policy/baseline is unavailable, use prior evidence rather than rebuilding it.
