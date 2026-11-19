# Assignment 1 finalization — November 19, 2026

**Four supplied rubric criteria supported. No application/API tests rerun.**

| Artifact | What it proves |
|---|---|
| [Two-page report](../../AI_API_Integration_1_Rubric_01_Report.pdf) | GET/POST behavior, actual retained JSON excerpts, authentication and distinct status outcomes |
| [Editable HTML](../../AI_API_Integration_1_Rubric_01_Report.html) | Matching ivory/champagne/deep-brown source; references actual original screenshots |
| [Prior HTTP results](../20261118-api/http-results.json) | November 18 actual 200 GET/POST, separate 401 authentication rejection and 422/403/404; 15 PASS |
| [Prior browser results](../20261118-api/browser-results.json) | November 18 original UI/network assertions; 7 PASS |
| [Prior Library screenshot](../20261118-api/screenshots/01-get-library.png) | Actual formatted GET result, synthetic records |
| [Prior Assistant screenshot](../20261118-api/screenshots/02-post-assistant.png) | Actual POST response displayed as guidance; search mocked, AI off |
| [Prior Pulse screenshot](../20261118-api/screenshots/03-get-pulse.png) | Actual point-in-time public-feed display |
| [Swagger availability](swagger-status.json) | User-referenced 401 images not located; not fabricated or counted as successful 200 evidence |
| [Before-edit baseline](baseline.json) | Hashes for original Assignment 1 files and every Assignment 2–4 file |
| [PDF page 1](report-page-1.png), [page 2](report-page-2.png) | Offline PDF layout renderings, **not new application screenshots** |
| [PDF text/page metadata](pdf-layout.json) | Native PDFKit page count and extracted content |
| [Final artifact audit](validation.json) | Offline rubric/content/hash/link/page/sanitization checks, separate from application tests |

The final report follows the existing cream/espresso/gold typography and scope
footer treatment. The first layout review caught footer overlap; spacing was
corrected and both final pages were rendered and visually reviewed. No original
app screenshot was edited or regenerated. PDF thumbnails are layout QA only.

## Evidence interpretation and remaining scope

- **Reused application result:** 22 PASS / 0 FAIL, November 18, not a fresh run.
- **Success evidence:** authenticated GET `/policies` and POST `/ask` returned 200;
  original body/response/status transcripts and UI assertions establish behavior.
- **Authentication rejection:** retained H02 returned 401 with Bearer challenge.
  A Swagger 401 image, if supplied later, can corroborate rejection only; it cannot
  be relabelled as a successful 200 fetch/submission.
- **Image availability:** existing Swagger images were not found in available
  coursework files. Only their saved location was requested, not a new capture.
  None was invented or silently substituted with a new Swagger simulation.
- **No mandatory rubric gap:** all four supplied criteria have complete written,
  machine-transcript and original UI evidence. Optional manual HTTP-detail captures
  are no longer a completion gate. Instructor grading remains separate.
- **Unverified:** production/Supabase authentication and external AI-provider output.
  Original fixture used synthetic SQLite, mocked PostgreSQL search and AI/email off.
- Existing Assignment 2–4 PDFs and supporting files remain byte-for-byte intact.
  Their historical “Item 1 deferred” text is superseded by Assignment 1's current
  documentation; those completed report folders are not edited.

## Authoring/QA commands actually used

From repository root:

```sh
python3 -B 'ai_api_intergration_1/AAI 1 Assignment 1/src/build_report.py'
```

The local HTML was printed with existing Chrome headless using `--no-pdf-header-footer`,
`--disable-background-networking`, a dedicated ignored profile and the output
`AI_API_Integration_1_Rubric_01_Report.pdf`. Only a `file://` report was opened;
no fixture, production app, login, public feed or API test server was started.

```sh
/usr/bin/swift -module-cache-path 'ai_api_intergration_1/AAI 1 Assignment 1/.runtime/swift-cache' 'ai_api_intergration_1/AAI 1 Assignment 1/src/render_pdf.swift' 'ai_api_intergration_1/AAI 1 Assignment 1/AI_API_Integration_1_Rubric_01_Report.pdf' 'ai_api_intergration_1/AAI 1 Assignment 1/evidence/finalization-20261119'
```

Native PDFKit/AppKit and existing Python/pypdf were used for document QA. No
packages installed. Dedicated static-print Chrome exited after writing the PDF;
no application service was touched. No commits or pushes.
