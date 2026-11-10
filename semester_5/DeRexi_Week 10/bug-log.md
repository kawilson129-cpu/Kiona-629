# Confirmed defects and retests

| ID / priority | Reproduction and impact | Focused fix | Retest / disposition |
|---|---|---|---|
| W10-01 / High | Click Yes after an Assistant answer; success toast appears but `/feedback/mine` stays unchanged. UI never calls `/feedback`, so dashboard metrics omit real user actions | `static/app.js` calls existing authenticated API; disables both buttons while pending; marks only confirmed saved rating; exposes pressed/live status; retains prior rating on error; retries update same row | Before: browser U03 FAIL, screenshot 00. After: U03–U06/U19 and mobile U29a PASS. FIXED |
| W10-02 / High | `make_article('FDIC', …, 'https://secure-fdic-verification.example/login', …)` returns an officially labelled article. C03-54 fails. HTTPS alone does not establish publisher identity | Per-source exact publication-host allowlists in existing registry; FDIC shared GovDelivery host restricted to its own bulletin path; rejects unknown sources, alternate/invalid ports and deceptive hosts. No source downloader or feed redesign | Before: C03-54 and seven new variants FAIL. After: C-03 54 executed PASS; Pulse 97 PASS; 17 publisher cases in integration PASS, including shared-account path traversal. FIXED |
| W10-03 / Medium | Rate the `user_message_id` returned by `/ask`; API returns 201 and pollutes answer-helpfulness aggregates | After existing ownership check, require `Message.sender == 'derexi'`; otherwise safe 422. No cleanup of old/live rows | Before: I18 returns 201. After: I18 returns 422; valid/repeated/foreign-message/strict-boolean and dashboard-scope cases PASS. FIXED |

No critical application defect was confirmed in the isolated scenarios. No unrelated feature was rebuilt. Changes preserve the existing architecture, palette, Governance state machine, RBAC, authentication and developer-access protections.

## Unresolved release limitations

| ID | Impact / status | Evidence and next requirement |
|---|---|---|
| L10-01 | Live Governance lifecycle BLOCKED | Week 9 observed missing Governance tables and owner coverage. No fresh live inspection and no migration/seed executed. Requires separately approved infrastructure setup |
| L10-02 | Live login BLOCKED | Week 9 observed zero Auth users and incomplete provider/subject-map/HTTPS-origin setup. No accounts created; real login/refresh/logout unverified |
| L10-03 | Direct-client authorization security BLOCKED | Week 9 found broad authenticated SELECT policies/grants and bypass-capable backend role. App tests cannot establish Supabase Data API isolation; no grant/RLS changes permitted |
| L10-04 | Production infrastructure UNVERIFIED | HTTPS, host-verified DB/internal TLS, encryption/backup controls, private storage and durable audit retention need external evidence; no operational changes made |
| L10-05 | Acceptance incomplete | Agent-driven fictional UAT passed; Kiona/business sign-off, physical iOS/Android and native Windows/Linux parser validation remain pending |
| L10-06 | Search/concurrency limits | SQLite translation and empty search adapter do not verify pg_trgm results or PostgreSQL race locking/RLS; live answer quality not claimed |
| L10-07 | Operational limits retained | Parser-preview worker affinity, process-crash original-file orphan reconciliation, JWT validity until expiry and per-process throttle/log retention remain as documented in Week 9 |
| L10-08 | Publisher allowlist maintenance | Legitimate future alternate publishing hosts will be dropped until explicitly reviewed/configured. Offline fixtures pass; no fresh government feed download or redirect-chain validation |

No approval is requested as part of this task; these limitations are recorded for a separate activation task.
