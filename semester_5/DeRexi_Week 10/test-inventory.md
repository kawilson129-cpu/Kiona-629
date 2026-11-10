# Test inventory

Canonical tests: `derexi-policy-pilot/backend/tests/`. Existing Week 7–9 implementations, fixtures, parsers, JWT crypto, RBAC and lifecycle remain the foundation.

| Existing suite/evidence | Prior coverage | Week 10 decision |
|---|---|---|
| `test_week7_messaging.py` / Week 9 `evidence/test_week7_messaging.txt` | 73 passing request/reply/resolve/reassign/access checks | Historical; new 10-check Assistant-to-Messaging handoff targets the gap |
| `test_week7_edges.py` / Week 9 `evidence/test_week7_edges.txt` | 29 passing notification/count/participant/dev-boundary checks | Historical; notification handoffs checked in integration/UAT |
| `test_week7_auth.py` / Week 9 `evidence/parser-fix-regressions/test_week7_auth-results.json` | 24 passing synthetic JWT/JWKS checks | Historical; crypto unchanged |
| `test_week9_security.py` / Week 9 `evidence/week9-security-results.json` | 110 passing auth, HTTPS cookie, CSRF, permissions, redaction and TLS configuration checks | Historical; browser cookie login/logout and API role denials targeted this week |
| `test_week8_governance.py` | 102 lifecycle/independence/revision/history/atomicity checks | Rerun for publication integration; retained old evidence |
| `test_document_intake.py` | 47 parser/confirmation/provenance/private download/outage/compensation checks | Rerun for upload integration; real parser subprocesses |
| `test_document_limits.py` / Week 9 `evidence/parser-limit-results.json` | 14 passing macOS resource-limit checks | Historical; limits unchanged |
| `test_pulse.py` | 97 offline unit/normalization/cache/ranking checks | Rerun for confirmed publisher bug; two old synthetic hosts changed to valid FDIC hosts |
| `test_c03_audit.py` | 54 prior passes and one confirmed host-binding failure | Rerun: 54 executed passes; one historical XSS-browser result explicitly excluded |
| Week 9 `evidence/browser-results.json` | 15 passing BFF, roles, incident assignment and mobile sign-in checks | Historical; extended real-browser UAT this week |
| Prior Pulse live-feed/layout results in MEMORY | 109 live feed checks, 40 layout checks previously passing | Historical only; no fresh live feed or layout run needed |

Meaningful gaps identified and addressed:

1. An uncertain `/ask` response creating a usable Messaging thread, administrator triage, owner notification, reply and requester notification.
2. Actual UI feedback persistence, failed-save/retry behavior and repeat-rating semantics; department-scoped dashboard aggregation.
3. Uploaded bytes and Pulse source references reaching independent review/publication and revision workflows in the browser.
4. Desktop/mobile role navigation, denial paths, real cookie-session logout, simulated outages and touch-driven Messaging.
5. Publisher-label spoofing and non-answer feedback contamination, each pinned by regressions.

Remaining coverage gaps: real provider/HTTPS login, PostgreSQL-specific trigram ranking/locking/RLS, deployed storage/infrastructure, native Linux/Windows parser execution, physical-device Safari/Android and human UAT sign-off. Historical passing results are not evidence that these gaps are closed. No full accessibility, performance or penetration-test certification is claimed.
