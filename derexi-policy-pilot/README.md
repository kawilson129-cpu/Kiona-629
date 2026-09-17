# DeRexi: Policy Pilot

Backend for **DeRexi: Policy Pilot**, a policy-governance and incident-assistance
assistant built for a fictional financial institution, **Aurum Capital Bank**.

DeRexi helps employees find trusted policy guidance, identifies the appropriate
policy owner when a question cannot be answered confidently, and supports
approved incident reporting and escalation.

## Stack

- **Database:** Supabase Postgres 17 (project ref `vnumvjamqtuxlctjdzoe`)
- **Backend:** FastAPI + SQLAlchemy 2.0 + psycopg2
- **Search:** Postgres `pg_trgm` trigram similarity (see `docs/database-design.md`)

## Layout

```
derexi-policy-pilot/
├── README.md
├── requirements.txt
├── requirements-dev.txt      # adds httpx for the smoke tests
├── docs/
│   └── database-design.md    # full schema / design scheme
├── design/                   # design artifacts + related security reports
│   ├── (Week 1 mockup, Week 2 design docs)
│   └── reports/              # NS + CT+V DeRexi assignment reports (copies)
└── backend/
    ├── .env.example          # copy to .env and add your connection string
    ├── database.py           # engine, session, Base
    ├── models.py             # SQLAlchemy ORM models (14 tables)
    ├── schemas.py            # Pydantic request models
    └── main.py               # FastAPI app and endpoints
```

This folder is the **canonical codebase** for DeRexi. Semester-week snapshots
(e.g. `semester_3/DeRexi_Week 3/`) are kept as progress history and are not
where development should continue.

## Setup

```bash
cd derexi-policy-pilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # optional, for the smoke tests

cp backend/.env.example backend/.env
# edit backend/.env and paste your Supabase connection string
```

## Run

```bash
cd backend
uvicorn main:app --reload
```

- API base: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs

## Endpoints by MVP component

| Component | Endpoints |
|---|---|
| 1. Policy Management | `GET /policies`, `GET /policies/{id}`, `POST /policies`, `POST /policies/{id}/versions` |
| 2. Search & Retrieval | `GET /policies/search?q=`, `POST /ask`, `GET /conversations/{id}` |
| 3. Clarification & Routing | `GET /clarifications`, `POST /clarifications`, `GET /clarifications/{id}`, `POST /clarifications/{id}/replies`, `POST /clarifications/{id}/resolve` |
| 4. Incident Assistance | `GET /incident-categories`, `GET /incidents`, `POST /incidents`, `PATCH /incidents/{id}` |
| 5. Health Dashboard | `POST /feedback`, `GET /dashboard/policy-health` |

Reference data: `GET /departments`, `GET /roles`, `GET /users`, `GET /health`.

## Quick test

```bash
# Ask DeRexi a policy question (Sam Okonkwo is user 8)
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id": 8, "question": "How long do we keep loan application records?"}'

# Policy health dashboard
curl -s http://127.0.0.1:8000/dashboard/policy-health
```

## Notes

- The backend connects directly to Postgres with the service role, so RLS does not
  block it. RLS stays enabled for future client-side access.
- `backend/.env` holds the database password and is git-ignored.
- Policy answers are retrieved from the latest approved `policy_versions`; every
  answer records its source in `policy_citations`.
