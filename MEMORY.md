# MEMORY.md

## Last Updated
September 24, 2026

## Current Focus
**UI REDESIGN PREVIEW ("The Ledger") BUILT in `ui-redesign-preview/` at repo root** — full interactive takeover of the DeRexi front end in an editorial-treasury style (paper/espresso/gold, Fraunces + Plus Jakarta Sans + JetBrains Mono, hairline rules, status stamps, ink "Ask" surface, persona roster gate). Serves seeded prod-snapshot data by default; `index.html?live=1` points the same adapter at `http://127.0.0.1:8000`. Awaiting Kiona's **visual sign-off** in the browser before anything is promoted into `backend/static/`. Nothing committed (Week 6 → Phase 2 UI + the new preview all still uncommitted per Kiona's approval gate). After sign-off: promote `style.css`/`app.js` into `backend/static/`, drop mock adapter, wire real auth user, then continue MVP components (incident-language detection), hardening, testing.

## Where Kiona Stands (as of last update)

### DeRexi: Policy Pilot
- **SDLC Progress:** Week 7 of 12 (caught up on Week 3 + 4 + 5 deliverables, Week 6 UI, Phase 2 corpus+UI staged)
- **Current phase:** Phase 2 policy/UI expansion (data + UI staged, uncommitted) → report findings → remaining MVP components, hardening, testing
- **What's done:** Home screen mockup (Week 1); design docs (Week 2); full Supabase schema + design doc + seeded banking handbook (Week 3); FastAPI backend with all 5 components (Week 4); backend tested end-to-end against live DB (all endpoints green); Week 5 validation report; plain-English AI answers via free Groq tier; **Week 6 employee UI at `/ui`**; **Phase 2: 27 new policies + Reg B v1.1 + owner-role normalization + UI re-brand (staged, uncommitted)**
- **What's next:** decide/fix the Reg B incomplete-application retrieval miss; incident-language detection (Component 4), security hardening, testing, docs, release
- **Blockers:** none — `backend/.env` is set and the API runs; DO NOT commit/push Phase 2 until Kiona approves
- **Monday board export:** Kiona offered to share — needs to be incorporated when provided
- **Key files:** `derexi-policy-pilot/` (canonical codebase at repo root — add `backend/static/` Week 6/Week 7 UI), `derexi-policy-pilot/design/` + `semester_3/DeRexi_Week 2/` (design PDFs), `semester_4/DeRexi_Week 5/` (validation report PDF)

### Supabase (DeRexi project)
- **Org:** DeRexi (`icljwbqrpcjhfnbkrhwr`)
- **Project:** DeRexi: Policy Pilot — ref `vnumvjamqtuxlctjdzoe`, region us-east-1, Postgres 17
- **Backend connection decision:** Direct DB / service role (RLS bypassed by backend; RLS still enabled + read policies for authenticated)
- **14 tables total** (3 pre-existing + 11 new), all RLS-enabled, all covered by migrations
- **Fictional bank seeded:** Aurum Capital Bank (Latin *aurum*, "gold") — federally chartered private bank with Lending + Wealth Management divisions. All user emails use `@aurumbank.com`
- **Seed (after Phase 2):** 7 policy categories, **43 policies / 45 versions**, 6 incident categories, 7 departments, **12 users** (added Rachel Sampson, Operations Policy Owner), demo conversations/citations/clarifications/incidents/feedback
- **Policies follow real federal banking regs:** GLBA/Reg P, GLBA Safeguards Rule, BSA/AML, CIP/KYC, SAR, OFAC, UDAAP, Reg Z (TILA), Reg B (ECOA) v1.1, Reg E & CC, private banking suitability
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
- Reorg used **copy** so nothing was lost during consolidation, then the duplicate `semester_3/DeRexi_Week 3/derexi-policy-pilot/` copy was **deleted** after a diff confirmed the root folder was a complete superset (and that root `main.py` was newer). Root `derexi-policy-pilot/` is the single source of truth
- Seeding rows with explicit IDs left identity sequences behind → fixed with migration `fix_identity_sequences`; also `departments.created_at` was missing (original dashboard table) → added via migration
- "Current version" resolution is **deterministic**: order by `created_at DESC, id DESC`. Applied in `policy_to_dict`, `SEARCH_SQL`, and the dashboard `reviews_due` CTE after seeded policy 11 had tied `created_at` timestamps (v1.0/v2.0)
- Retrieval guard in `/ask` adds a **substantive-keyword evidence gate** on top of the 0.22 threshold (threshold stays fixed): `substantive_keywords()` (len>=4 minus `GENERIC_STOPWORDS`) must appear in the top candidate's title+body (`contains_keyword`, with singular fallback), else route to clarification. Non-confident message: "The policy library does not contain enough information..."
- Confident `/ask` answers are now guidance-first + citation-last via `make_guidance()` (best-matching complete sentence) — no longer a raw "Based on {title}: {excerpt}" dump
- **Phase 2 seed mechanics:** bulk seeds run through SQL `INSERT … SELECT` from a CTE (auto-generated ids — never explicit; keeps identity sequences ahead). Long single migrations risk tool-transmission corruption — keep batches small (≤6 policies) and verify after each. The HR batch's 15th policy was lost/mangled once and fixed by a repair migration
- **Phase 2 ownership:** new HR→Jordan Rivera, Lending→Marcus Webb (incl. Reg B owner), Wealth→Gabrielle Fontaine, platform/IT→Lucy Chen, InfoSec/SOC→Chris Tanaka, business continuity→Rachel Sampson (new Ops Policy Owner), AI→Alex Chen, data classification→Dana Brooks. Dana + Lucy stay System Administrators
- **Phase 2 RAG constraint:** retrieval (pg_trgm, 0.22 gate, evidence gate) must NOT be altered because policies were added. A full-sentence Reg B query was confidently mis-citing Incident Response (0.2246) because sentence length diluted the Reg B score below the gate. **Resolved content-only**: two Reg B v1.1 body-copy migrations (`improve_regb_v11_incomplete_application_wording`, `improve_regb_v11_all_required_information_wording`) added employee-facing phrasing; all three Reg B phrasings now retrieve Reg B v1.1 top (0.256/0.425/0.447) and the other five scenarios are unchanged. R3 needed a 2nd pass ("all required information" phrasing beat Appraisals' "provide information" overlap). Lesson: species-level near-ties under pg_trgm often resolve via natural policy wording, not score changes

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
- Diffed root vs Sem 3 copy before deletion: nothing was only-in-Sem-3; root `main.py` was ahead (tiebreaker + retrieval guards). Kiona removed `semester_3/DeRexi_Week 3/derexi-policy-pilot/`; references scrubbed from AGENTS.md/MEMORY.md/README
- Copied the DeRexi NS + CT+V assignment reports into `derexi-policy-pilot/design/reports/` (`network-security/`, `cyber-threats-and-vulnerabilities/`); originals untouched

### September 21, 2026 — Deterministic "current version" resolution
- Found seeded edge case: policy 11 had v1.0 (id 11) and v2.0 (id 12) with **identical `created_at`** timestamps; `policy_to_dict` ordered by `created_at DESC` only, so `GET /policies/11` nondeterministically reported `latest_version: 1.0`
- Fixed with secondary key `id DESC` in `policy_to_dict` (verified `GET /policies/11` → `latest_version 2.0`, `review_date 2026-10-01`)
- Same tiebug existed in `SEARCH_SQL` (`/policies/search`, `/ask`) and the dashboard `reviews_due` CTE; Kiona approved applying the same tiebreaker → both now `ORDER BY pv.created_at DESC, pv.id DESC`
- Verified via direct query: current-version CTE picks v2.0 (id 12) with tiebreaker vs v1.0 (id 11) without; dashboard + search endpoints still green; `py_compile` clean
- No schema changes

### September 21, 2026 (later) — Retrieval-quality guard + answer restructure
- Diagnosed why the gym question ("Does Aurum Capital Bank reimburse employees for gym memberships?") outscored the phishing question: `word_similarity(q, body)` is a best-local-alignment metric; generic tokens (Aurum/Capital/Bank/employees) present in every policy spike `ws_body` (0.3973) at the same time the true topic words (reimburse/membership — 0 policies contain them) never appear. Scores interleave (0.2427 vs 0.2402) so no single threshold can separate them
- Implemented in `/ask`: `GENERIC_STOPWORDS` + `substantive_keywords()` + `contains_keyword()` evidence gate (keyword must appear in top candidate title+body, plural-strip fallback); no evidence → `needs_clarification: true` with "policy library does not contain enough information..." message
- Rewrote confident answers: `make_guidance()` picks the best complete policy sentence → "Here's what you should do: {sentence}\nReference: {Title} (v{version}) — review the full policy..."
- Verified: gym→clarify (conf 0.2427 kept), phishing→answers with Report Phishing SOC guidance + citation, phished/report→answers, loan-records regression still answers; `/policies/search` untouched; `py_compile` clean; no schema changes

### September 22, 2026 — OpenAI/Groq AI agent + connection checks + cleanup
- Kiona deleted `semester_3/DeRexi_Week 3/derexi-policy-pilot/` (root was confirmed a superset); scrubbed its references from AGENTS.md, MEMORY.md, root README; committed by Kiona (87e4dae)
- Week 5 validation report PDF landed in `semester_4/DeRexi_Week 5/` (committed 3afdd63)
- Added optional AI agent for plain-English answers. First pass used the OpenAI **Responses API** (`ai.py`, wired into the confident `/ask` path with a rule-based fallback; `client.responses.create`); committed as 42d7e86
- Diagnosed a user-reported 500: exercised all 24 endpoints + simulated a bad API key — nothing reproduces a 500 in current code; flagged `POST /policies` and `PATCH /incidents/{id}` as the only craftable 500 sources (unguarded FK violations); advised restarting uvicorn to the latest code
- Kiona realized the OpenAI API is paid and wanted a free, close-to-OpenAI alternative. Researched Sept-2026 options (OpenAI/Anthropic/xAI have no free tier; Cerebras/Together went paid; free = Gemini, Groq, OpenRouter, Cloudflare, Mistral)
- Kiona chose **Groq**: `ai.py` switched from Responses API to universal **Chat Completions** (`chat.completions.create`) with an `OPENAI_BASE_URL` override so any OpenAI-compatible provider works. Verified against a stub endpoint (`/v1/chat/completions`, system+user messages, temperature 0.2, max_tokens 400) and re-verified the no-key fallback + zoom route-to-clarify
- `.env.example` + README now document the free Groq config (`OPENAI_BASE_URL=https://api.groq.com/openai/v1`, `OPENAI_MODEL=gpt-oss-120b`, key from console.groq.com, phone verify, no card). Kiona needs to paste her real Groq key into `backend/.env`
- Re-verified Supabase connection with the new password: app-level pooler connection OK (0.57s, PG 17.6), 14 tables, 16 policies, project reachable — no fixes needed
- Committed + pushed to GitHub main: `0ae1274 "Point DeRexi AI at free Groq tier"`

### September 22, 2026 (later) — Week 6: Employee UI shipped
- Kiona approved the Week 6 plan: **a polished, minimal vanilla HTML/CSS/JS employee screen** served by FastAPI at `/ui` — no build tooling, no backend redesign, no auth/dashboard/database/RAG changes
- Built `backend/static/index.html`, `style.css`, `app.js` in the DeRexi editorial style (ported the portfolio site's tokens: cream `#FAF9F6`, champagne `#C9B495`/`#E8D5B5`, ink `#1D1B17`; Fraunces serif display + Plus Jakarta Sans body; film-grain + warm glow overlays; double-bezel card shells; custom `cubic-bezier` motion; `prefers-reduced-motion` support). Marks the Compliant AI-slop-free checks: no generic chat UI, no default shadows/borders
- Screens: wordmark bar → hero ("Policy guidance, when you need it.") → double-bezel question composer with dark **Ask DeRexi** pill (nested icon circle, spinner state, Cmd/Ctrl+Enter submit) → states: loading card, answer card, **Policy Reference** card (title + v{n} chip + 3-line excerpt from `citations[0]`), warm amber **clarification** card ("Routed to a policy owner"), restrained error card with retry. Demos as Sam Okonkwo (user 8)
- `main.py`: added `StaticFiles` mount at `/ui` (`html=True`) + `from fastapi.staticfiles import StaticFiles` / `from pathlib import Path`; README updated (layout tree, Run URLs, new Employee UI section)
- Verified: `py_compile` + `node --check` clean; live boot test — `/ui`, `/ui/style.css`, `/ui/app.js` all 200; real `POST /ask` returns both answered (Phishing citation payload) and clarification shapes; bad user → 404 caught by the UI error state. No schema/DB changes
- Next for Week 7+: incident-language detection (Component 4 UI/workflow), then hardening/testing

### September 23, 2026 — Phase 2: policy corpus + UI (Week 7) expansion
- Kiona approved the Phase 1 audit outcome and Phase 2 plan (4 tasks: owner roles, 27-policy expansion, UI refresh, regression tests)
- **1) Roles:** migration `normalize_policy_owner_roles` — Chris Tanaka, Jordan Rivera, Gabrielle Fontaine → Policy Owner; created **Rachel Sampson (id 12, Operations Policy Owner)**; verified 12 users; Dana/Lucy stay SysAdmins
- **2) Corpus:** applied 4 seed migrations (HR 15, Technology 4, InfoSec 6, Lending 2 + Reg B v1.1). The HR batch was transmitted mangled (15th policy lost, Sick Leave body merged); repaired via `fix_hr_seed_holidays_sick_leave`. Verified: **43 policies / 45 versions**, 0 duplicate titles, 0 orphan versions/policies, per-category counts correct, Reg B current version = 1.1. New policies effective 2026-10-01, review 2027-09-30, v1.0, approved, auto ids only
- **3) UI (Week 7 refresh):** `index.html` — espresso `#221D17` opaque header + **DeRe·x·i** Fraunces wordmark with gold `x`; `style.css` — 70/20/10 cream/espresso/champagne palette, espresso answer card (ivory text, champagne kicker), champagne-tinted ivory reference card with gold `v`-chip, warm amber clarification, restrained error, reduced-motion preserved; `app.js` hardened — now targets `#answer-body`/`#clarification-body`/`#error-body` (fixes the wipe-chrome-if-textContent-set-on-section bug that also destroyed the retry button), null-safe citations (non-array/empty/missing fields), hides version chip when `version_no` absent, falls back gracefully when answer/citations missing
- **4) Regression sweep (user 8):** PTO → confident (PTO v1.0, 0.323) ✓; parental leave → confident (Parental Leave v1.0, 0.298, "16 weeks") ✓; unsupported wifi → routed (0.171) ✓ by design; phishing without keyword → routed (0.155) but WITH the word "phishing" → confident correct (0.237) ✓; AI-tool question → routed (0.186) ✓ safe but AI policy unreachable in natural phrasing (pg_trgm lexical gap; "What AI tools are approved for bank work?" ranks AI 2nd at 0.337) ✓ safe/by-design; **Reg B "missing document" → FAIL**: confidently answered from Incident Response & Breach Reporting (0.2246) — wrong policy for the question (Reg B v1.1 scored 0.201 with the full sentence, 0.269 with the short topic phrase)
- Docs updated: `README.md` (43-policy library + Week 7 UI), `docs/database-design.md` §8/§9 (seed counts + migrations 8–16), `MEMORY.md`. `.env` still ignored; only `backend/static/*` shows modified in git — **not committed (awaiting Kiona)**
- Reg B false-positive resolved **content-only** (option 2, RAG untouched): two body-copy migrations; reran all 3 Reg B phrasings + 5 other scenarios — Reg B v1.1 now top (0.256/0.425/0.447), answers cite it, no new false matches. Remaining open items: not committed; AI-tool question still routes (0.186) as a documented pg_trgm phrasing limitation

### September 24, 2026 — Week 6/7 UI refinement + "The Ledger" redesign preview
- Finished the Week 6/7 UI refinement in `backend/static/` (cream header, gold-x wordmark, role-aware nav/persona bar, Policy Health view) — **written + verified, still uncommitted**
- User passed off `uipro` (`ui-ux-pro-max-cli` v2.15.0 at `/usr/local/lib/node_modules`); 26 skills inventoried (23 shared SKILL.md in `/Users/Shared/opencode-skills` + supabase trio + built-in `customize-opencode`)
- User: "use all your skills and plan a complete UI redesign takeover — don't touch live code, show me how it looks first." Plan mode: mapped all 19 endpoints + exact shapes, pulled real seed (43 policies/7 cats, 12 users, clarifications, 2 incidents, dashboard totals 43/77/153/2, top_cited 5), **server :8000 was down** during planning
- Kiona chose: Direction **A "The Ledger"** (editorial private-bank treasury) · full takeover · **mock + `?live=1`** toggle · folder **`ui-redesign-preview/` at repo root**; approved with "go"
- **Built `ui-redesign-preview/`** (5 files ~1.4x of current UI): `mock-data.js` (prod-snapshot seed, mirrors API shapes 1:1 incl. search rows `policy_id`), `index.html` (letterhead + sticky topbar + role-gated nav + persona roster gate + footer), `style.css` (full design system: paper `#F3EEE4`/espresso `#211C15`/gold `#9D7C43`, hairline rules, 3-font stack, pill+card+input radius system, tinted shadows, `cubic-bezier(0.22,1,0.36,1)` motion, film grain, skeleton/typing loaders, reduced-motion), `app.js` (hash router, MOCK/live adapter via `fetch`, all 4 surfaces + detail drawer + queue act/resolve + incidents triage, XSS-safe `textContent` only, toasts, ESC closes, `?auto=1` skips gate), `README.md` (open steps, endpoint contract, promotion path)
- **Design decisions:** rejected ui-ux-pro-max's generic security-blue default — **brand-locked override** (Aurum=gold heritage, Fraunces/Plus Jakarta already in prod, brief chose editorial); added JetBrains Mono for ledger IDs/kickers; remedial dot/kicker scale bumped to 11px floor, grain to 10% opacity after the impeccable detector pass
- **Verification:** `node --check` clean ×2; wrote a headless stub-DOM smoke harness (`/tmp/opencode/derexi-smoke.js`) — boots app as Maya (auto), routes Assist/Library/Governance (0 runtime errors), asserts all mock data paths (ask PTO→citations+conf 0.323, AI→routed+assignee, policy 8 versions, search finds 17, dashboard 43/0.667, incidents, resolve); found+fixed 2 real bugs: mock adapter returned raw values (now always Promises), search-row enrich from policy cache
- `impeccable` context + detector run: fixed text floor + footer uppercase; rejected overused-font (brand-locked) + typing-pulse (live state) as documented; stopped after one confirmation round
- Opened in browser for Kiona's review — **promotion to `backend/static/` only after visual sign-off** (copy 2 files, drop mock, wire real auth user; `?live=1` path already exercises the real API shapes)
- **Design review delivered (taste skill + impeccable, honest pass).** Verdict: 70% execution — concept strong, Operate-vs-editorial tension is the real gap. Delivered 13 findings, incl.: palette/fonts are the banlisted AI defaults (override documented, needs a differentiator); **italic descender clipping** in `.view-title` (line-height 1.08 w/ italic em descenders, style.css:286); **AA contrast fails inside ink surface** (`.ask-hint-label` 50% champ on ink style.css:375, `.confidence` 55% :388, placeholder 45% :355); duplicate suggestion intent (Try chips + Common questions card); empty conversation well on first load; one skeleton per view (kicker+serif title+banks identical); Governance KPIs read as generic dashboard cards, not ledger; stamp noise (42/43 approved = wallpaper); micro-uppercase overload; `.view` motion replays on every nav switch; light-only is a defensible-but-unconfirmed choice; impeccable detector flags cramped topbar padding + buried grain. **No changes made — waiting on Kiona's personal list of mistakes/changes before editing.**

### September 24, 2026 (later still) — "The Ledger" promoted to backend/static + OpenRouter AI
- Kiona gave **visual sign-off** on the Ledger redesign ("I like everything… applause on the policy health dashboard. There are a few tweaks we'll get to later, but seed all the updates"). Per the preview README's promotion path, promoted `ui-redesign-preview/` → live app:
  - Copied `style.css` → `derexi-policy-pilot/backend/static/style.css`
  - Promoted `index.html` (dropped `<script mock-data.js>`, footer now "Live register", aria-label "Choose role")
  - Promoted + adapted `app.js`: removed mock adapter + `LIVE_BASE`/`MODE`/`AUTO` entirely (always live, same-origin `fetch`), `/ask` now sends real `user_id: state.personaId` (the preview omitted it — would 422), boot no longer forces the persona roster gate (defaults Sam user 8 via localStorage `derexi.personaId`, "Change" button still opens it), gate copy no longer says "Preview"/"seeded snapshot"
  - Added **`GET /categories`** to `main.py` → `[{id, name, count}]` (UI's `loadCats()` expected it; backend previously 404'd and fell back to `/policies`)
- Verified live: server booted, `/ui`+`style.css`+`app.js` 200, `mock-data.js` 404, all UI endpoints green (12 users, 3 roles, 7 categories, 43 policies, ask PTO conf 0.3754/3 cites, gym→routed, dashboard 43/81/161/2 reviews_due 2 helpful 0.667 top 5, 26 clarifications, 2 incidents, policy detail w/ versions). **Not committed** (Kiona's approval gate — she may commit separately)
- **AI provider switched Groq → OpenRouter** (Kiona pasted the standard REST curl; no code change needed since `ai.py` uses OpenAI-compatible chat completions via `OPENAI_BASE_URL`):
  - `backend/.env`: `OPENAI_BASE_URL=https://openrouter.ai/api/v1`, `OPENAI_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free`, key `sk-or-v1-…` (set by Kiona)
  - Updated `.env.example` + README AI section: OpenRouter now the recommended provider; Groq/OpenAI still documented as alternatives
  - Verified: uvicorn restarted; live `/ask` "How much paid time off" returns a genuine Nemotron answer (reasoned over all 3 cited policies, then Reference: Paid Time Off & Vacation v1.0). Note: `:free` Nemotron is verbose (long reasoning-style answers) vs Groq gpt-oss — fine for now, may want a paid/lighter model later or tighten max_tokens
  - Server currently running in background (uvicorn pid reflects latest, port 8000)

### September 24, 2026 — DESIGN.md added and linted clean
- Kiona ran `npx @google/design.md lint DESIGN.md`; file didn't exist → created **`DESIGN.md` at repo root**, documenting the **portfolio site's "Editorial Luxury" system** (name: Editorial Luxury). Format: YAML frontmatter tokens + markdown prose per the Google design.md spec v0.3 (`spec --rules` used to confirm rules before authoring)
- Tokens: 5 colors (primary `#121212` ink, secondary `#4A4A4A`, tertiary `#C9B495` deep champagne, accent `#E8D5B5`, neutral `#FAF9F6`), 8 typography scales (Inter, mirroring prod), 1 rounding level (`sm: 4px`), 9 spacing tokens (incl. `container: 1400px`), 8 components (all token references resolve)
- Body sections in canonical order: Overview, Colors, Typography, Layout & Spacing, Elevation & Depth, Shapes, Components, Do's and Don'ts
- Lint: had to fix 2 errors (fontSize can't be `clamp()` → fixed rem values; fluid behavior stays documented in prose). Final: **0 errors, 0 warnings** (only info = token-summary). No other files touched; not committed
