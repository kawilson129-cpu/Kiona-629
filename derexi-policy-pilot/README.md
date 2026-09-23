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
- **Policy library:** 43 approved policies — original handbook (16) plus a
  post-audit Phase 2 expansion (27) across HR, Technology, InfoSec, and Lending for
  Compliance. The Regulation B / ECOA policy was expanded to v1.1 (2026-10-01).

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
    ├── ai.py                 # optional AI agent (OpenAI-compatible)
    ├── static/               # Week 6 employee UI (index.html, style.css, app.js)
    └── main.py               # FastAPI app and endpoints
```

This folder is the **single canonical copy** of the DeRexi codebase. The duplicate
project folder formerly kept in `semester_3/DeRexi_Week 3/` was removed after the
root folder was confirmed to be a complete superset.

## Setup

```bash
cd derexi-policy-pilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # optional, for the smoke tests

cp backend/.env.example backend/.env
# edit backend/.env and paste your Supabase connection string
# (optional) add OPENAI_API_KEY to enable plain-English AI answers
```

## Run

```bash
cd backend
uvicorn main:app --reload
```

- API base: http://127.0.0.1:8000
- Employee UI: http://127.0.0.1:8000/ui
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

## Employee UI (Week 6)

A lightweight single-page employee screen served by FastAPI from `backend/static/` at
`/ui` — no frontend build tooling. It is a thin vanilla HTML/CSS/JS client for
`POST /ask`, rendered in the DeRexi editorial style:

- Question composer → **Ask DeRexi** (with loading state)
- Employee-facing answer card
- **Policy Reference** card (policy title + version + excerpt) from `citations`
- Warm amber **clarification** card when `needs_clarification` is true
- Restrained error state for network / API failures

It defaults to demo employee **Sam Okonkwo (user 8)**; the API also exposes
`GET /users` if user selection is added later.

The Week 7 refresh re-branded the screen to the DeRexi espresso/champagne identity:
solid espresso header with the **DeRe·x·i** serif wordmark (gold `x`), an espresso
answer card with ivory text and a champagne kicker, a champagne-tinted ivory Policy
Reference card with a gold version chip, warm amber clarification, and a restrained
error state with the retry button intact. Rendering is defensive: missing, empty, or
non-array citations and absent answer text never break the UI.

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
- **Plain-English answers (optional AI agent):** with `OPENAI_API_KEY` set in
  `backend/.env`, `POST /ask` sends the retrieved policy context to an
  OpenAI-compatible Chat Completions endpoint (`ai.py`) and returns a plain-English
  rewrite. **Free tier:** Groq hosts OpenAI's open-weight `gpt-oss` models at $0 —
  set `OPENAI_BASE_URL=https://api.groq.com/openai/v1`, `OPENAI_MODEL=gpt-oss-120b`
  (key from https://console.groq.com, no credit card, phone verification). The paid
  OpenAI platform works too (`OPENAI_BASE_URL=https://api.openai.com/v1`,
  `OPENAI_MODEL=gpt-4o-mini`). Without a key (or on API error) the endpoint falls
  back to rule-based guidance, so the RAG flow always works offline.
