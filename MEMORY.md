# MEMORY.md

## Last Updated
September 17, 2026

## Current Focus
DeRexi Week 3 (database design scheme + design doc) and Week 4 (FastAPI backend) COMPLETE and verified end-to-end against the live Supabase DB. The codebase now lives in the **canonical root folder `derexi-policy-pilot/`**. Ready for Week 5 — frontend/UI work.

## Where Kiona Stands (as of last update)

### DeRexi: Policy Pilot
- **SDLC Progress:** Week 5 of 12 (caught up on Week 3 + Week 4 deliverables)
- **Current phase:** Backend built → testing/running locally → frontend next
- **What's done:** Home screen mockup (Week 1); design docs (Week 2); full Supabase schema + design doc + seeded banking handbook (Week 3); FastAPI backend with all 5 components (Week 4); backend tested end-to-end against live DB (all endpoints green)
- **What's next:** Frontend/UI, incident-language detection, security hardening, testing, docs, release
- **Blockers:** none — `backend/.env` is set and the API runs
- **Monday board export:** Kiona offered to share — needs to be incorporated when provided
- **Key files:** `derexi-policy-pilot/` (canonical codebase at repo root), `derexi-policy-pilot/design/` + `semester_3/DeRexi_Week 2/` (design PDFs), `semester_4/DeRexi_Week 5/` (empty, current week)

### Supabase (DeRexi project)
- **Org:** DeRexi (`icljwbqrpcjhfnbkrhwr`)
- **Project:** DeRexi: Policy Pilot — ref `vnumvjamqtuxlctjdzoe`, region us-east-1, Postgres 17
- **Backend connection decision:** Direct DB / service role (RLS bypassed by backend; RLS still enabled + read policies for authenticated)
- **14 tables total** (3 pre-existing + 11 new), all RLS-enabled, all covered by migrations
- **Fictional bank seeded:** Aurum Capital Bank (Latin *aurum*, "gold") — federally chartered private bank with Lending + Wealth Management divisions. All user emails use `@aurumbank.com`
- **Seed:** 7 policy categories, 16 policies (17 versions), 6 incident categories, 7 departments, 11 users, demo conversations/citations/clarifications/incidents/feedback
- **Policies follow real federal banking regs:** GLBA/Reg P, GLBA Safeguards Rule, BSA/AML, CIP/KYC, SAR, OFAC, UDAAP, Reg Z (TILA), Reg B (ECOA), Reg E & CC, private banking suitability
- **Advisors:** clean except platform-managed `rls_auto_enable()` (safe, leave)

### Portfolio Site
- **Status:** Live at kawilson129-cpu.github.io/Kiona-629
- **Projects on site:** PhishCoach, Stay Data Stay, DeRexi Policy Pilot (placeholder)
- **Recent work:** Case study pages built for all 3 projects

### Coursework
- **Semester 3 active:** Prompt Engineering, Network Security, DeRexi project
- **Completed assignments:** CT+V (2), NS (4), Python basics, Unix, Design, Logic, Version Control, Figma, Markdown

## Decisions Made
- DeRexi design docs are PDFs (agent cannot parse — ask Kiona for summaries)
- `stay_data_stay.py` is duplicated across 7+ course folders (each is a separate submission)
- Portfolio site uses editorial luxury design system with champagne accents
- All links must use Liquid `{{ '/path' | relative_url }}` filter
- DeRexi is built for **financial institutions / banks** (not general enterprise) — policy content must follow federal banking regulations
- Fake handbook institution = **Aurum Capital Bank** (Latin *aurum* = gold); chose Latin over Greek mythology for faith reasons and to match "DeRexi". Emails `@aurumbank.com`
- Backend connects via direct DB / service role, so RLS is permissive for MVP and tightened when Auth is added
- `policy_versions` holds full policy text; current version = most recently created version (by `created_at`), not highest `version_no`
- Backend stack: FastAPI + SQLAlchemy 2.0 + psycopg2 + pydantic v2; run with `uvicorn main:app --reload`
- Search = `pg_trgm` blended score `0.6*word_similarity(q,body) + 0.4*similarity(q,title)`; confidence threshold 0.22 (matches score ≥0.27, non-matches ~0.17)
- **Canonical codebase = `derexi-policy-pilot/` at the repo root.** Semester folders are progress snapshots and must not be developed in
- Reorg used **copy, not move**, so `semester_3/DeRexi_Week 3/derexi-policy-pilot/` stays intact as the Sem 3 archive; root copy is now the source of truth
- Seeding rows with explicit IDs left identity sequences behind → fixed with migration `fix_identity_sequences`; also `departments.created_at` was missing (original dashboard table) → added via migration
- "Current version" resolution is **deterministic**: order by `created_at DESC, id DESC`. Applied in `policy_to_dict`, `SEARCH_SQL`, and the dashboard `reviews_due` CTE after seeded policy 11 had tied `created_at` timestamps (v1.0/v2.0)

## Conversation History
<!-- Append new entries below. Each session gets a timestamped block. -->

### September 4, 2026 — Initial Setup
- Read through all semester folders and course materials
- Identified DeRexi as the active project
- Created AGENTS.md with full repo context
- Created MEMORY.md (this file) for persistent workspace memory
- Set up auto-update convention: update MEMORY.md at end of every session
- Kiona will provide Monday board export for project status tracking

### September 17, 2026 — DeRexi Supabase database design scheme
- Connected to Supabase org "DeRexi" / project "DeRexi: Policy Pilot" (`vnumvjamqtuxlctjdzoe`)
- Found 3 pre-existing dashboard-created tables: `departments` (5 rows), `roles` (3), `users` (5); RLS on but zero policies; no migrations
- Kiona confirmed: build directly in live project; seed a **banking** policy handbook (DeRexi is for financial institutions); backend uses direct DB/service role
- Built full schema via 6 migrations (baseline → policy mgmt → conversations → clarification+incident → feedback+search → seed), then a 7th advisor-fix migration
- New tables: `policy_categories`, `policies`, `policy_versions`, `conversations`, `messages`, `policy_citations`, `clarification_requests`, `clarification_replies`, `incident_categories`, `incident_reports`, `feedback`
- Added Lending + Wealth Management departments; extended users to 11 (all 5 personas: Alex Chen, Jordan Rivera, Sam Okonkwo, Maya Patel, Chris Tanaka)
- Seeded "Sterling Capital Bank" handbook: 16 policies across 7 categories citing GLBA, BSA/AML, CIP, SAR, OFAC, UDAAP, Reg Z, Reg B, Reg E/CC; plus demo conversations/citations/escalation/incidents/feedback
- Removed security advisor warnings (RLS policies on baseline tables; moved pg_trgm to `extensions` schema)
- Not yet done at end of that block: design doc markdown, backend models/API code

### September 17, 2026 (later) — Bank rename, design doc, Week 4 backend
- Kiona decided against Greek mythology (Seventh-day Adventist); chose a Latin name consistent with DeRexi → **Aurum Capital Bank**
- Migration `rename_bank_to_aurum_capital`: replaced "Sterling Capital Bank" in policy text; changed all emails `@derexi.com` → `@aurumbank.com`
- Wrote `docs/database-design.md` — full Week 3 design deliverable (principles, ERD, table reference, enums, indexes/search, security, seed, migration history)
- Wrote Week 4 backend in `backend/`:
  - `database.py` — engine/session/Base, reads `DATABASE_URL` from `.env` (raises clear error if missing)
  - `models.py` — SQLAlchemy 2.0 ORM for all 14 tables; mapper configuration verified
  - `schemas.py` — pydantic v2 request models
  - `main.py` — 24 routes: policy CRUD/versions, `/policies/search`, `/ask` (retrieval + citations + auto-routing), conversations, clarifications, incidents, feedback, `/dashboard/policy-health`
  - `requirements.txt`, `README.md`, `backend/.env.example`
- Added Python/`.env`/`.DS_Store` entries to root `.gitignore` (keeps `.env.example`)
- Verified: `py_compile` clean; SQLAlchemy `configure_mappers()` clean; all routes register; search ranking calibrated (threshold 0.22 routes the "$1.2M wire" question to a policy owner as intended)
- Known limitation: trigram retrieval is lexical, not semantic; embeddings/LLM answer generation are future work. "Loan application records" question ranks Reg Z first (correct retention facts are in ECOA + Data Retention policies)
- Cleaned up verification venv; **Kiona still needs to create `backend/.env` with her Supabase connection string to run the API**

### September 17, 2026 (later still) — Bug fixes, E2E green, canonical root folder
- Ran full end-to-end test against live Supabase; found and fixed two real bugs:
  1. `UniqueViolation` on `conversations_pkey` — seeding with explicit IDs left identity sequences at 1; fixed all affected tables via migration `fix_identity_sequences`
  2. `column departments.created_at does not exist` — original dashboard table lacked the column the ORM expected; added via migration `add_departments_created_at`
- After fixes: full endpoint suite green (health, policies, search, ask answerable + routing, conversations, clarifications, incidents, categories, users, dashboard)
- Kiona asked to consolidate the codebase into a single canonical project folder at the repo root, keeping semester folders as semester-by-semester progress records
- Created root `derexi-policy-pilot/` (copy of the Sem 3 codebase): `backend/`, `docs/database-design.md`, `design/` (copied Week 1 mockup + Week 2 design docs), `README.md`, `requirements.txt`, `requirements-dev.txt`, `.gitignore`
- Created fresh `.venv` at the root project and installed deps (+ httpx); verified the canonical project runs end-to-end from its new location
- Updated `README.md` setup paths, `AGENTS.md` (repo structure + code location), and `MEMORY.md`
- Left `semester_3/DeRexi_Week 3/derexi-policy-pilot/` untouched as the Sem 3 archive (copy, not move)
- Copied the DeRexi NS + CT+V assignment reports into `derexi-policy-pilot/design/reports/` (`network-security/`, `cyber-threats-and-vulnerabilities/`); originals untouched

### September 21, 2026 — Deterministic "current version" resolution
- Found seeded edge case: policy 11 had v1.0 (id 11) and v2.0 (id 12) with **identical `created_at`** timestamps; `policy_to_dict` ordered by `created_at DESC` only, so `GET /policies/11` nondeterministically reported `latest_version: 1.0`
- Fixed with secondary key `id DESC` in `policy_to_dict` (verified `GET /policies/11` → `latest_version 2.0`, `review_date 2026-10-01`)
- Same tiebug existed in `SEARCH_SQL` (`/policies/search`, `/ask`) and the dashboard `reviews_due` CTE; Kiona approved applying the same tiebreaker → both now `ORDER BY pv.created_at DESC, pv.id DESC`
- Verified via direct query: current-version CTE picks v2.0 (id 12) with tiebreaker vs v1.0 (id 11) without; dashboard + search endpoints still green; `py_compile` clean
- No schema changes
