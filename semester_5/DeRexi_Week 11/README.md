# Week 11 — Deployment Preparation

Prepared November 11, 2026 for the existing application. Documentation is prepared for review; production activation remains pending.

November 12 continuation: [implementation/results](final-integration-results.md), [incident/routing architecture](final-integration-architecture.md), [pinned-item status](pinned-readiness-status.md), [approval/recovery checklist](final-integration-approval-checklist.md), and [Week 12 demo](week12-demo-runbook.md). New evidence is isolated under `evidence/final-integration-20261112/`; older evidence remains unchanged.

- [Project README](../../derexi-policy-pilot/README.md): purpose, architecture, setup, configuration names, API and troubleshooting.
- [Deployment runbook](../../derexi-policy-pilot/docs/deployment.md): ordered activation, rollback and validation instructions only.
- [Employee guide](employee-guide.md).
- [Policy Owner guide](policy-owner-guide.md).
- [System Admin guide](system-admin-guide.md).
- [Demonstration script](demo-script.md): local-only personas, policy lifecycle, incident-to-triage flow and rehearsal checklist.
- [Focused 8–12 minute employee walkthrough](employee-messages-walkthrough.md): question → clarification → Messages, with speaker cues.
- [Focused 8–12 minute governance walkthrough](governance-library-walkthrough.md): Policy Owner review → System Admin approval → published Library.
- [Focused 8–12 minute Pulse walkthrough](pulse-revision-walkthrough.md): article → source-linked proposed policy revision.
- [Focused 8–12 minute feedback walkthrough](feedback-dashboard-walkthrough.md): saved answer rating → authorized Dashboard aggregate.
- [Presentation and existing screenshots](presentation.md).
- [Release checklist](release-checklist.md).
- [Validation evidence](evidence/documentation-validation.md).

## Evidence and limits

Reuse [Week 7 messaging](../../semester_4/DeRexi_Week%207/evidence/README.md), [Week 8 lifecycle](../../semester_4/DeRexi_Week%208/README.md) and [document workspace](../../semester_4/DeRexi_Week%208/governance-workspace/README.md), [Week 9 security/activation](../DeRexi_Week%209/production-activation.md), and [Week 10 test report](../DeRexi_Week%2010/test-report.md).

**VERIFIED DEVELOPMENT:** historical isolated checks, including Week 10's 379 PASS / 0 FAIL (37 browser checks). These are agent-executed simulations, not live human acceptance. Native Mac parser checks do not establish native Windows/Linux readiness.

**PENDING PRODUCTION:** Governance schema/owner coverage, real Auth, direct-client RLS/grants, HTTPS/internal transport, storage/backups/logging, PostgreSQL-specific verification, seven live workflows and stakeholder sign-off. No prior evidence was changed, no accounts created and no deployment performed. Screenshots are linked to their original labelled evidence rather than copied or presented as live.

The requested Week 11 path was absent after checking semester directories and repository file inventory. This exact folder was created; no alternative Week 11 folder or runtime copy was introduced.
