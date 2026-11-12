# DeRexi: Policy Pilot

Full-stack MVP for **DeRexi: Policy Pilot**, a policy-governance and incident-assistance
assistant built for a fictional financial institution, **Aurum Capital Bank**.

DeRexi helps employees find trusted policy guidance, identifies the appropriate
policy owner when a question cannot be answered confidently, and supports
approved incident reporting and escalation.

## Stack and current MVP

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0, psycopg2, Pydantic; bounded DOCX/PDF parsing with pypdf and defusedxml.
- **Database:** Supabase PostgreSQL 17 with `pg_trgm` lexical retrieval and confidence/evidence gates. See [database design](../semester_3/DeRexi_Week%203/database-design.md).
- **Frontend:** existing vanilla HTML/CSS/JavaScript served by FastAPI at `/ui/`; no frontend build is required.
- **Identity:** Supabase JWT/JWKS, server-managed browser sessions and database-derived roles; signed loopback-only personas are an explicit development opt-in.
- **Policy Assistant/Library:** cited published policy guidance, optional AI rewrite with rule-based fallback, uncertainty routing and published-version browsing. AI fallback still requires the database; it does not make the app fully offline.
- **Messages/feedback:** participant-scoped clarification replies, unread markers, notifications and persisted Yes/No answer feedback.
- **Governance/Dashboard:** departmental Owner and organizational Admin visibility, DOCX/PDF intake, drafts, independent peer review, independent final approval, revisions, publication and history. Drafts stay separate from published guidance.
- **Incidents:** employee reporting and Admin-only management, handler assignment and escalation.
- **Reviewed support handoff:** actual-event detection, urgent guidance, follow-up questions, employee review/confirmation and durable delivery status. Technical Routing uses approved departmental destinations and narrow delegated permissions; SMTP and optional incident AI default OFF. SMTP acceptance never proves email delivery or ticket creation. See [integration architecture](../semester_5/DeRexi_Week%2011/final-integration-architecture.md).
- **Pulse:** government publication feed with source-linked draft/revision handoff; no automatic policy publication.

Browser -> FastAPI REST API -> SQLAlchemy/psycopg2 -> Supabase PostgreSQL. The privileged backend database connection bypasses RLS, making backend RBAC essential; RLS-enabled flags alone do not establish safe direct-client access. Search is lexical rather than embedding-based. Current version resolution uses creation time then ID, not version-string sorting. Historical inventory: 49 policies / 51 versions, not a newly verified live count.

## Release status and guides

**VERIFIED DEVELOPMENT:** existing isolated Week 7–10 evidence; Week 10 recorded 379 PASS / 0 FAIL, including 37 browser checks. **PENDING PRODUCTION:** Governance schema/owner capacity, real provider onboarding, direct-client RLS/grants, infrastructure, native-host/PostgreSQL validation, seven live workflows and human acceptance. No production readiness or live UAT claim is made.

The November 12 integration sprint adds isolated incident/routing, native Windows and browser evidence, plus a fresh read-only live readiness inventory. See the [current sprint results](../semester_5/DeRexi_Week%2011/final-integration-results.md) and [approval/recovery checklist](../semester_5/DeRexi_Week%2011/final-integration-approval-checklist.md). New support tables require a separately approved migration; startup does not create them.

- [Deployment preparation and rollback](docs/deployment.md).
- [Week 11 documentation, role guides and demo](../semester_5/DeRexi_Week%2011/README.md).
- [Employee guide](../semester_5/DeRexi_Week%2011/employee-guide.md), [Policy Owner guide](../semester_5/DeRexi_Week%2011/policy-owner-guide.md), [System Admin guide](../semester_5/DeRexi_Week%2011/system-admin-guide.md).

## Layout

```
derexi-policy-pilot/
├── README.md
├── requirements.txt
├── requirements-dev.txt      # adds httpx for the smoke tests
├── docs/
│   └── deployment.md         # activation / rollback instructions
├── design/                   # design artifacts + related security reports
│   ├── (Week 1 mockup, Week 2 design docs)
│   └── reports/              # NS + CT+V DeRexi assignment reports (copies)
└── backend/
    ├── .env.example          # copy to .env and add your connection string
    ├── database.py           # engine, session, Base
    ├── models.py             # SQLAlchemy ORM models
    ├── schemas.py            # Pydantic request models
    ├── ai.py                 # optional AI agent (OpenAI-compatible)
    ├── pulse/                # Pulse regulatory-intelligence module
    │   ├── sources.py        # government feed registry + download
    │   ├── service.py        # normalization, classification, cache
    │   └── routes.py         # /api/pulse endpoints
    ├── static/               # role-aware UI (index.html, style.css, app.js, pulse.js)
    ├── tests/                # standalone test scripts (no pytest needed)
    └── main.py               # FastAPI app and endpoints
```

This folder is the **single canonical copy** of the DeRexi codebase. The duplicate
project folder formerly kept in `semester_3/DeRexi_Week 3/` was removed after the
root folder was confirmed to be a complete superset.

## Installation and local startup

Use Python 3.10 or newer and an approved reachable PostgreSQL database with the existing schema and `pg_trgm`. Recreate the virtual environment on each machine; do not copy `.venv` across operating systems. Native Windows/Linux document resource controls remain unverified; validate the intended deployment host. Dependencies declare ranges, so capture exact approved versions before release.

### macOS Terminal

From the repository root:

```bash
cd derexi-policy-pilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Optional test dependencies:
python -m pip install -r requirements-dev.txt
# First setup only; preserve an existing private configuration:
cp -n backend/.env.example backend/.env
```

### Windows PowerShell

From the repository root:

```powershell
cd derexi-policy-pilot
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Optional test dependencies:
python -m pip install -r requirements-dev.txt
if (!(Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
```

If activation is blocked, use `.\.venv\Scripts\python.exe` in place of `python`; no execution-policy change is needed. cmd.exe activation is `.venv\Scripts\activate.bat`.

Edit ignored `backend/.env` privately with approved configuration. For local personas only, explicitly choose development mode and enable developer auth, then restart. See names below and the [local persona instructions](../semester_5/DeRexi_Week%2011/demo-script.md). Missing Governance tables leave that workspace unavailable; setup does not authorize applying schema/seed scripts.

From `derexi-policy-pilot/` with the environment activated:

```text
python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload --no-proxy-headers
```

Subsequent sessions: enter the project folder, activate this machine's environment, then run that command. Stop with Ctrl+C. Bind only loopback for development; do not expose personas through a tunnel/proxy.

- UI: http://127.0.0.1:8000/ui/
- Health: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

### Environment variables — names only

| Purpose | Names |
|---|---|
| Database / CA trust | `DATABASE_URL`, `PGSSLROOTCERT` |
| Runtime / local identities | `DEREXI_ENV`, `DEREXI_DEV_AUTH`, `DEREXI_DEV_USER_IDS`, `DEREXI_DEV_AUTH_SECRET` |
| Supabase JWT verification | `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISS`, `SUPABASE_JWT_AUD`, `SUPABASE_JWT_ALGS`, `SUPABASE_JWT_LEEWAY`, `SUPABASE_JWKS_TIMEOUT` |
| Browser sessions | `SUPABASE_PUBLISHABLE_KEY`, legacy fallback `SUPABASE_ANON_KEY`, `DEREXI_PUBLIC_ORIGIN`, `DEREXI_AUTH_SUBJECT_MAP` |
| Optional AI | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` |
| Optional private original retention | `DEREXI_DOCUMENT_STORAGE_DIR` |
| Approved support destinations / delivery / optional classifier | `DEREXI_APPROVED_MAILBOXES`, `DEREXI_OUTBOUND_EMAIL`, `DEREXI_INCIDENT_AI` |
| Private outbound transport | `DEREXI_SMTP_HOST`, `DEREXI_SMTP_FROM`, `DEREXI_SMTP_USERNAME`, `DEREXI_SMTP_PASSWORD` |

Use the ignored environment file or host secret store, never frontend files. JWT defaults derive from the Supabase project. Production requires real approved subject bindings, matching verified emails, database roles and HTTPS; disable development auth. Never use a service-role key as the publishable key. External AI requires institutional approval for sending policy context; without a key/on provider failure the app uses rule-based guidance.

## API endpoints and access

Use the running `/docs` schema for exact methods, fields and response models. Most business endpoints require authentication. Arbitrary user-ID fields do not confer identity. Use authorized browser sessions or the documented bearer mechanism without copying secrets into shared Swagger sessions or evidence.

| Component | Routes |
|---|---|
| Authentication | `/auth/config`, `/auth/login`, `/auth/session`, `/auth/refresh`, `/auth/logout`, `/me` |
| Published policies / Assistant | `GET /policies`, `/policies/{id}`, `/policies/search`; `POST /ask`; `GET /conversations/{id}` |
| Clarification and inbox | `/clarifications`, detail/reply/resolve actions; `/messages`, `/messages/notifications` (see OpenAPI for subroutes) |
| Governance | `/governance/availability`, `/governance/owners`, `/governance/drafts`, detail/actions and document preview/original routes |
| Incidents / feedback | `GET/POST /incidents`, Admin-only `PATCH /incidents/{id}`, `POST /feedback`, `GET /feedback/mine` |
| Dashboard / reference | `/dashboard/policy-health`, `/departments`, `/roles`, `/users`, `/categories`, `/incident-categories` |
| Operations / feed | `/health`, `/api/pulse`, `/api/pulse/health` |
| Reviewed support / routing | `/support/assess`, `/support/prepare`, `/support/requests`, request confirmation/dispatch/status; `/technical-routing/capabilities`, `/technical-routing/config`, `/technical-routing/grants`, `/technical-routing/test`, Admin-only `/technical-routing/readiness` |

Legacy `POST /policies` and `POST /policies/{id}/versions` deliberately return 409: use independently reviewed Governance publication. Health proves database reachability, not full schema or release readiness.

## Pulse — Regulatory Intelligence

A read-only feed of federal banking, privacy, and cybersecurity publications,
surfaced as an editorial newsfeed inside the app at **`/ui/#pulse`** (nav item
**Pulse**, after Governance). It is a live integration with four free government
feeds — no API key, account, or paid service:

| Source | Feed | Format |
|---|---|---|
| Federal Register | `/api/v1/documents.json` (7 banking regulators, newest first) | JSON |
| FDIC | GovDelivery RSS for FDIC press releases | RSS |
| NIST | CSRC draft publications open for comment | JSON |
| Federal Reserve | Banking & consumer regulatory policy press releases | RSS |

Endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/pulse?limit=40` | Combined, de-duplicated, newest-first articles (max 60) |
| `GET /api/pulse/health` | Module check: sources + cache window |

Each article carries `title`, `url` (original publication, https), `published`
(ISO date), `summary` (plain text), `source`, `agency`, `category`, and `status`.
Statuses are limited to **Proposed Rule, Final Rule, Notice, Supervisory Guidance,
Standards Draft, General News**; categories to **Banking & Finance, Regulations,
Cybersecurity, Privacy & Data Protection, Supervisory Guidance**. Failures are
per source: `sources` in the response reports `ok`, `count`, `error`, and `stale`
while the rest of the feed still renders.

Pulse can be publicly readable; feed access does not establish a signed-in business identity. Local persona switching is development-only and server verified.

Background, architecture, and evidence: [existing Pulse documentation](../compliance_1/C%201%20Assignment%203/README.md).

## Frontend and troubleshooting

The existing frontend supports Assistant, Library, Messages, role-gated Dashboard/Governance, Pulse, notifications and incident reporting. It preserves DeRexi's espresso/ivory/champagne visual system. Production sign-in uses the configured provider; there is no automatic default-employee identity or public persona switcher.

| Symptom | Action |
|---|---|
| Missing DB configuration / connection failure | Check private `backend/.env`, approved network/credentials and CA trust; never print its contents. |
| Cannot import `main` | Run the startup command from the project folder with the correct environment and `--app-dir backend`. |
| Missing parser / dependency | Install declared runtime requirements in the correct environment; verify pypdf/defusedxml and native resource controls. |
| No local persona switcher | Check explicit development mode/auth opt-in, restart, and use direct loopback with no forwarded headers. Production intentionally disables it. |
| 401 | Sign in again; have Admin check approved Auth bindings without disabling authentication. |
| 403 / 404 | Check role, department, participant or assignment. Private resources may intentionally appear absent. |
| 409 | Refresh stale work, use a fresh published baseline/unique version, renew review after edits, or wait for effective date. |
| 413 / 415 / 422 intake | Use DOCX/text PDF below 5 MB, extracted text within 20,000 characters; correct fields and confirm preview. OCR is not provided. |
| 429 / expired preview | Wait or finish/discard existing previews; re-upload expired work. Login throttles also require waiting. |
| 503 Governance | Retry later, preserve text and contact Admin. Schema/storage/dependency preparation may be pending. |
| Pulse stale/unavailable | Check source statuses and original publishers; retry later. Published Library remains separate. |
| Port in use | Reuse the known service or stop only your own process; preserve unrelated services. |

## Development versus production

Development uses one loopback worker, explicit opt-in personas and synthetic/approved data. Production needs real Auth, closed direct-client grants, reviewed schema, HTTPS/trusted proxy and DB transport, encrypted private storage/backups, restore tests, durable restricted logs and acceptance. No `--reload` or public developer identities. In-memory previews need a single worker or validated affinity; login throttles are per process. The Python backend cannot run on GitHub Pages, which hosts the separate portfolio.

Production remote database configuration now requires certificate and hostname verification (`verify-full`); configure trusted CA material before activation. Outbound email stays OFF until separately approved. Technical Routing validation sends no mail. Existing ticketing handles investigation/resolution; DeRexi keeps a limited reference and handoff status.

Follow the [deployment runbook](docs/deployment.md) before activation. It contains ordered review, backup, schema/owner, Auth/RLS, host startup, validation and rollback steps; none is applied by this documentation. Previous evidence is retained in [Week 7](../semester_4/DeRexi_Week%207/evidence/README.md), [Week 8](../semester_4/DeRexi_Week%208/README.md), [Week 9](../semester_5/DeRexi_Week%209/README.md) and [Week 10](../semester_5/DeRexi_Week%2010/README.md). Documentation changes do not warrant full regression reruns.
