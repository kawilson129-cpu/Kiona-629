# AGENTS.md

> **FIRST THING EVERY SESSION:** Read `MEMORY.md` at repo root. It has current project state, what we last worked on, and pending items. At the END of every session, update `MEMORY.md` with what happened.

## What this repo is

GitHub Pages portfolio site for Kiona Wilson (DAE Cybersecurity student, Graduating Dec 3, 2026) plus all semester coursework files. Live site: `kawilson129-cpu.github.io/Kiona-629`.

## Repo structure

The Jekyll site lives in `docs/`. The **canonical DeRexi codebase lives in `derexi-policy-pilot/` at the repo root** — develop the project there. Everything else is coursework artifacts and semester-week progress snapshots.

```
derexi-policy-pilot/           # CANONICAL DeRexi codebase — edit HERE
  backend/                     # FastAPI: database.py, models.py, schemas.py, main.py
  docs/database-design.md      # Week 3 design deliverable
  design/                      # Week 1 mockup + Week 2 design docs (copies)
  README.md                    # setup / run / endpoint map
  requirements.txt             # runtime deps
  requirements-dev.txt         # + httpx (smoke tests)

docs/                          # Jekyll site (Markdown, SCSS, images)
  _config.yml                  # Jekyll config, baseurl: /Kiona-629
  _layouts/default.html        # Single layout template
  assets/css/style.scss        # Full design system
  assets/images/               # Project images, headshot, logo
  assets/files/                # Resume PDF
  index.md                     # Home page
  about.md                     # About page
  projects.md                  # Project grid (PhishCoach, Stay Data Stay, DeRexi)
  phishcoach.md                # PhishCoach case study page
  stay-data-stay.md            # Stay Data Stay case study page
  derexi-policy-pilot.md       # DeRexi case study page (in development)
  contact.md                   # Contact page

semester_1/                    # Sem 1: Keynote status updates
semester_2/                    # Sem 2: Project design doc, career exploration, Keynote updates
semester_3/                    # Sem 3 ARCHIVE (progress snapshot — do NOT develop here)
  DeRexi_Week 1/               # DeRexi home screen mockup
  DeRexi_Week 2/               # Design docs: personas, data maps, system components
  DeRexi_Week 3/               # Snapshot of the codebase as it stood in Sem 3
semester_4/                    # Sem 4: DeRexi_Week 5 (in progress), status updates

cyber_threats_and_vulnerabilities_1/  # CT+V: malware reports, APT38/MITRE report, vuln assessment
network_security _1/                 # NS: topologies, core components, network fundamentals, access control
prompt_engineering_1/                # PE: contains stay_data_stay.py submission
python_1/                            # Python basics: login systems, weather app, functions, stay_data_stay.py
unix_1/                              # Unix: contains stay_data_stay.py submission
unix_2/                              # Unix 2: contains stay_data_stay.py submission
design_1/                            # Design: contains stay_data_stay.py submission
logic_1/                             # Logic: contains stay_data_stay.py submission
version_control_1/                   # Version Control: contains stay_data_stay.py submission
figma_1/                             # Figma: jam files (VirtualCloset, Stay Data Stay, Baby's First Algorithm)
markdown_learning/                   # Markdown learning demo
```

## Active project: DeRexi: Policy Pilot

**Status:** Week 3 database design scheme COMPLETE; Week 4 backend COMPLETE. Now in Week 5 of 12-week SDLC, catching up on Week 4 deliverables.

**What it is:** A policy-governance and incident-assistance assistant for employees. When someone has a policy question or suspects a security incident, DeRexi connects them with the right guidance and the right person.

**Built for:** financial institutions / banks. Fictional institution is **Aurum Capital Bank** (Latin *aurum*, "gold"), a federally chartered private bank with Lending and Wealth Management divisions. Policy content follows federal banking regulations (GLBA/Reg P, GLBA Safeguards Rule, BSA/AML, CIP/KYC, SAR, OFAC, UDAAP, Reg Z, Reg B/ECOA, Reg E & CC).

**Supabase:** project "DeRexi: Policy Pilot", ref `vnumvjamqtuxlctjdzoe`, org `icljwbqrpcjhfnbkrhwr`, region us-east-1, Postgres 17. 14 tables, all migrations-backed, all RLS-enabled. Schema + seed fully documented.

**5 User Personas:**
1. Alex Chen — IT Help Desk Analyst (front-line, triage)
2. Jordan Rivera — HR Generalist (policy interpretation, employee situations)
3. Sam Okonkwo — Remote Employee (needs clear guidance from anywhere)
4. Maya Patel — Policy Compliance Manager (owns policies, needs visibility)
5. Chris Tanaka — SOC Analyst (incident response, escalation)

**5 MVP Components:**
1. Policy Management — store/approve/maintain policies
2. Policy Search & Retrieval — natural language questions to policy answers
3. Clarification & Routing — connect to policy owner when unsure
4. Incident Assistance — detect incident language, trigger reporting/escalation
5. Policy Health Dashboard — admin visibility into policy status/feedback

**Code location (canonical):** `derexi-policy-pilot/`
- `docs/database-design.md` — full schema design (Week 3 deliverable)
- `backend/` — FastAPI + SQLAlchemy 2.0: `database.py`, `models.py`, `schemas.py`, `main.py`
- `backend/.env.example` — copy to `backend/.env`, add Supabase `DATABASE_URL` (git-ignored)
- `README.md`, `requirements.txt`, `requirements-dev.txt` — setup/run instructions
- Archive snapshot (do NOT edit): `semester_3/DeRexi_Week 3/derexi-policy-pilot/`

**Design docs:** `derexi-policy-pilot/design/` (copies; originals live in `semester_3/DeRexi_Week 2/`)
- DeRexi Conceptual Data Map
- DeRexi Core System Components (V.2, V.3)
- DeRexi's Internal Application Structure
- Meet the DeRexi Users (personas)
- DeRexi Week 1 home-screen mockup

**Security reports:** `derexi-policy-pilot/design/reports/` (copies; originals stay in course folders)
- `network-security/` — NS Assignment 2 (Core System Components V.1/V.2/V.3), NS Assignment 4 (Access Control Measures)
- `cyber-threats-and-vulnerabilities/` — CT+V Assignment 1 (APT38 FASTCash MITRE report), CT+V Assignment 2 (Vulnerability Assessment)

**Portfolio page:** `docs/derexi-policy-pilot.md` (already live on site)

## Completed projects (on portfolio site)

- **PhishCoach** — Python phishing awareness tool, VirusTotal API integration
- **Stay Data Stay** — Python CLI privacy app for travelers, tracks logged-in accounts

## Portfolio site (Jekyll/GitHub Pages)

- Push to `main` triggers GitHub Pages build. No local build command needed.
- `baseurl` in `_config.yml` is `/Kiona-629`
- All internal links must use Liquid: `{{ '/path' | relative_url }}`
- Design: editorial luxury theme, Inter font, champagne accent (`#E8D5B5`/`#C9B495`), cream background (`#FAF9F6`)
- Key CSS patterns: `<span class="eyebrow">` for labels, `<span class="champagne-accent">` for accent text
- Layout classes: `.hero-section`, `.project-grid`, `.project-card`, `.about-grid`, `.contact-grid`
- Lenis smooth scroll loaded from CDN

## Adding new pages/projects

1. Create `docs/new-page.md` with `layout: default` and `title`
2. Use `{{ '/path' | relative_url }}` for all links/assets
3. Add nav in `docs/_layouts/default.html` (both `.nav-links` and `.mobile-menu-links`)
4. For projects: add card in `docs/projects.md` inside `.project-grid`, add image to `docs/assets/images/`

## Coursework context

These folders contain assignment submissions — they are NOT shared code. The `stay_data_stay.py` file is duplicated across 7+ course folders as separate submissions. Each course folder is independent.

## Gotchas

- No build/test/lint commands — static site with no toolchain
- Image paths must use Liquid filter, not raw paths
- The `network_security _1/` folder has a trailing space in the name
- Binary files (.key, .pptx, .pages, .xlsx) cannot be read by the agent — ask Kiona for summaries if needed
- PDFs and PNGs in semester_3/DeRexi_Week 2/ contain critical design docs the agent cannot parse directly

## Memory system

- `MEMORY.md` at repo root is the persistent workspace memory
- It tracks: current focus, project state, conversation history, and decisions
- **Every new session, read MEMORY.md first** to understand where we left off
- **At end of every session, update MEMORY.md** with what was discussed/decided/done
- Kiona will also provide updates (Monday board exports, course progress) to keep MEMORY.md current
