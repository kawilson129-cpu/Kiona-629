# Reconciliation of all 13 local ecosystem assets

All 13 have evidence, relationships, proposed ownership, impact and limitations. Direct control coverage remains 6/13 (46.15%). Reconciliation coverage is 13/13 (100%). Historical classroom host SSH stays outside this denominator.

| ID / owner | Evidence verified | Relationships | Business impact | Coverage / limitation |
|---|---|---|---|---|
| APP / Platform engineering | Signed endpoint tests and current main.py | DB, AUTH, PKGS, AI | Policy integrity and incident confidentiality | Current control assertions — Fake writes only; live transactions and deployment unverified |
| UI / Application engineering | Current UI source, API headers and prior Docker screenshot | APP | Employees may follow compromised guidance | Current control assertions — No new browser interaction or accessibility test |
| DB / Data platform | Schema design plus database.py and models.py inspected | External/root dependency | Policy, incident and identity record integrity | Reconciled evidence only — No live connection, row counts, RLS or recovery tested |
| AUTH / Identity engineering | Signed-token identity, roles and cross-user cases | DB, DEV_AUTH | Privilege and private-record access | Current control assertions — Local issuer only; production JWKS flow untested |
| DEV_AUTH / Identity engineering | Issuer source and real token generation used by fixtures | PKGS | Test credentials must remain confined to development | Reconciled evidence only — Dev endpoints, environment guards and expiry not comprehensively tested here |
| PULSE / Feed service owner | Current source and reserved-host negative check | FR, FDIC, NIST, FED | Trustworthy regulatory attribution | Current control assertions — Host-binding failure remains open |
| CONTAINER / Platform engineering | Current Compose declaration and prior container inspection | PULSE | Host isolation and service availability | Current control assertions — Runtime evidence reused with its original timestamp |
| FR / Feed service owner | Registry definition and prior Docker feed response with 38 records | External/root dependency | Regulatory monitoring completeness | Reconciled evidence only — Point-in-time reachability only; no current endpoint request |
| FDIC / Feed service owner | Registry definition and prior Docker RSS response with 25 records | External/root dependency | Banking supervisory context | Reconciled evidence only — Publisher ownership and future redirects not newly verified |
| NIST / Feed service owner | Registry definition and prior Docker JSON response with 9 records | External/root dependency | Draft security-standard awareness | Reconciled evidence only — Point-in-time content availability only |
| FED / Feed service owner | Registry definition and prior Docker RSS response with 15 records | External/root dependency | Bank regulatory monitoring | Reconciled evidence only — Point-in-time content availability only |
| AI / Platform and procurement | ai.py inspected, optional context-to-provider code path | PKGS | Potential disclosure or inaccurate policy guidance | Reconciled evidence only — Provider is configurable; no credentials read or provider contacted |
| PKGS / Platform engineering | Current 35-distribution snapshot, pip check and release advisories | External/root dependency | Executable dependency integrity | Current control assertions — Host environment only; container/OS and deployed versions differ |
