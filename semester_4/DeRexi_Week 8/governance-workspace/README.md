# Governance document workspace repair

## Observed failure and repair

The actual Windows service returned **200** for `/auth/config`, `/me` (Policy Owner), and `/governance/owners`, but **503** for `/governance/drafts`. An explicit read-only PostgreSQL transaction confirmed `governance_drafts` and `governance_events` are absent; existing user, policy-version and messaging tables exist. No live write or migration was attempted. `evidence/diagnosis.json` retains the original response; `browser-results.json` includes the actual browser response statuses.

The previous UI waited for shared reference requests before mounting its workspace. Its queue error handler wrote an error above the pane but never replaced the queue's loading placeholder. The repaired landing page mounts immediately, independently loads references, availability and real queues, bounds each request to 15 seconds, and replaces every loading state on success or failure. Missing data is never replaced with sample records or zero counts. Save and decision actions remain unavailable when persistence is unavailable. Backend responses use natural product copy; database diagnostics are logged server-side.

## Document intake and editing

- Browse and drag/drop send real binary DOCX/PDF files to authenticated `POST /governance/documents/preview`. Employees and anonymous callers are denied before processing. No file upload endpoint bypasses the existing identity/department/role checks.
- Extension, MIME and signatures must agree. Limits: 5 MiB input, 50 PDF pages, 20,000 policy characters, bounded DOCX archive count/expansion, two concurrent parser children, 12-second wall clock, eight CPU seconds and 256 MiB process memory. Windows Job Objects and POSIX resource limits are used in the child. Child environment omits application credentials. DOCX entities/macros/embedded content and PDF encryption/actions/attachments are rejected; text extraction executes neither document code nor links. Image-only PDFs require a text-based export; OCR is not provided.
- `pypdf` and `defusedxml` are the only added dependencies. PDF extraction follows the [official pypdf reader API](https://pypdf.readthedocs.io/en/latest/modules/PdfReader.html). Structural checks and resource bounds are not antivirus certification.
- Unstructured text is placed under the established Purpose, Scope, Policy requirements, Responsibilities, Exceptions and Related guidance headings. Missing sections are visibly marked for the author to complete; no policy facts are invented. Already structured source text is preserved.
- Authors can inspect extracted text, edit metadata/content, view the Policy Library preview, and explicitly confirm the document. Choosing an existing policy preserves uploaded replacement content and creates a proposed version. Three real templates provide editable starting content.
- Confirmation saves using the existing authenticated `/governance/drafts` implementation. Original-document metadata (name, hash and retention key) is recorded in its existing creation-event snapshot. Drafts still require a different same-department Policy Owner, independent administrator final approval and controlled publication. No lifecycle routes, Dashboard or messaging infrastructure were rebuilt.
- Previews are user-bound, single-use, in memory for at most 20 minutes of validity, with bounded cache capacity. Restarts or another worker can require a fresh upload; deployment should use one worker or session affinity for preview/confirmation. No upload is called saved until database commit succeeds.

## Private originals and setup

No storage setting was changed. When original retention is not configured, preview and policy-text saving remain available where the database supports them, and the UI explicitly states originals are not retained. When configured storage is inaccessible or public, intake is disabled. A retention failure prevents draft saving. Failed database saves compensate by deleting newly staged originals. A process crash between filesystem write and database commit can leave a private orphan; production operations should reconcile unattached files.

Optional `DEREXI_DOCUMENT_STORAGE_DIR` must name an existing absolute, private directory outside `backend/static` and the public `docs` site. Provision Windows ACLs for only the application service account and required administrators, or equivalent POSIX permissions. A local `.private-documents` directory is gitignored. Originals use random names and restrictive file modes, never a static URL. `GET /governance/drafts/{id}/original` reuses role/department authorization and sends an attachment with `no-store` and `nosniff`.

Required database setup is unchanged: review/approve the existing [governance schema](../../backend/migrations/2026-11-10_week8_governance.sql) and [missing-owner seed](../../backend/migrations/2026-11-10_week8_owner_seed.sql), then execute only after separate authorization. Neither ran in this repair. No new document table/migration is needed. All existing Supabase records and user-organized coursework files were preserved.

The two parser packages are installed in the existing Windows environment and declared in `requirements.txt`. For another environment install that file. Restart from `derexi-policy-pilot/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000 --no-proxy-headers
```

Open `http://127.0.0.1:8000/ui/#governance`. Until approved database setup, document preview/templates/editing work; saved queues and draft persistence truthfully remain unavailable.

## Verification and evidence

```powershell
# Ephemeral SQLite, PostgreSQL connection tripwire, temporary private files:
.\.venv\Scripts\python.exe backend/tests/run_workspace_checks.py
# Dedicated server, port 8030, synthetic records only:
.\.venv\Scripts\python.exe backend/tests/serve_document_workspace.py
# Separate headless Edge/Chromium profile with CDP port 9240:
node backend/tests/test_document_workspace_browser.mjs
node backend/tests/test_document_revision_browser.mjs
```

`run_workspace_checks.py` retains new logs separately and does not overwrite earlier coursework evidence. The lifecycle suite accepts `DEREXI_TEST_EVIDENCE_DIR` for this purpose. Browser suites use localhost:8000 for **GET-only diagnosis** and port 8030 for all draft/review/publication writes. Those writes touch only ephemeral SQLite. Private-file tests use temporary directories.

PostgreSQL migration syntax, locks, direct-client RLS/grants, live seed idempotency and production sign-in remain unverified. This repair deliberately does not apply or weaken them. No push or commit occurred.

Screenshot index (01 is the actual Windows service with unavailable governance tables; 02–10 use isolated synthetic records):

1. Actual landing, real upload/template actions and professional unavailable state.
2. Available document intake with honest empty queues.
3. Imported DOCX, metadata editing and private-original disclosure.
4. Policy Library preview with section hierarchy.
5. Administrator Final Approvals and review queues.
6. Three editable policy templates.
7. Real PDF preview with disabled save during persistence outage.
8. Mobile document intake at 390px.
9. Imported replacement-version preview after selecting an existing policy.
10. Published baseline versus uploaded replacement and audit workspace.

For the final report, reproduce 02–10 against an approved database after setup, add completed peer/admin decisions and audit timestamps, and include Employee API denial evidence. Keep tokens, connection strings and original private files out of screenshots. Historical failed checks under `evidence/attempts/` are explicitly superseded by final JSON results.

Final results: **406 PASS / 0 FAIL** — 47 document-intake checks, 102 lifecycle, 73 messaging, 29 messaging/RBAC edges, 24 JWT, 97 Pulse, 30 workspace browser checks and four imported-revision browser checks. Ten final screenshots were captured; desktop and mobile layouts were visually inspected. The current UI intentionally remains in unavailable mode on the real database until separately approved setup is completed.
