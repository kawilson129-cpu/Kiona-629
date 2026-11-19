# Finalization review - November 18, 2026

## Reports found and checked

| Item | File | Review result |
|---|---|---|
| 2 | Existing Assignment 2 / AI_API_Integration_1_Rubric_02_Report.pdf | One page; cream/espresso/gold, readable headings/body, actual Library screenshot and correct local/AI-off limits. Claims agree with B01/B03-B05 and existing API-to-screen evidence. COMPLETE |
| 3 | Assignment 3 / AI_API_Integration_1_Rubric_03_Report.pdf | Two pages; matching typography/palette, lifecycle table, actual methods/URLs/headers/body, selected JSON and exact error details. Full transcript linked. COMPLETE |
| 4 | Existing Assignment 4 / AI_API_Integration_1_Rubric_04_Report.pdf | One page; readable, actual Pulse screenshot, 401/403 results and separately recorded four public 200 responses. No production or AI assurance. COMPLETE within stated scope |

Supplied Item 2/4 PDFs were already in the requested directory and were not copied,
relocated or regenerated. SHA-256 hashes and page counts are recorded in the final
validation JSON. Review PNGs are PDF renderings for layout QA, not new app screenshots.
The available LMS screenshot contains a header only; no unseen rubric text is asserted.

## Reused evidence and source integrity

Existing November 18 results: 15 HTTP + 7 browser = **22 PASS / 0 FAIL**. The four
public upstream 200 responses are source records, not added checks. No runtime
tests or network requests were repeated for finalization. Initial browser attempts
and the old 12-check document audit retain their original scopes and filenames.

All 11 source hashes in fixture.json match current source after CRLF-to-LF
normalization. Raw hashes differ on Windows, so equivalence is explicitly limited
to newline normalization; no other differences were accepted. Existing screenshot
and transcript hashes are checked against the earlier validation manifest.

Current artifact QA is in `finalization-validation.json`: page limits, report text
against transcript fields, JSON/error/security coverage, sanitization, links and
source fingerprints. It is separate from application tests. No live authentication,
database writes, AI responses or provider availability are newly verified.

## Visual review and execution notes

Used existing bundled Python/ReportLab/Pillow and Poppler. No packages installed.
An availability check of the project virtual environment required approved interpreter
access but showed no authoring/render libraries; the existing bundled runtime supplied
them without installation. Node REPL was unavailable; it was not used to create evidence.
The first Item 3 layout guard caught page-2 overflow before saving; shortened the
explicitly selected response excerpt, retained full JSON in original evidence, and
rendered/inspected both final pages. Poppler emitted display-font warnings for Symbol
and ArialUnicode; final embedded-font content rendered legibly with no missing glyphs.

Manual inspection: supplied reports and both Item 3 pages have clear hierarchy,
no clipping/overlap, readable body text, footer scope labels and correct pagination.
Existing Assistant and Pulse originals were viewed; supplied Item 2's Library capture
was reviewed in its rendered PDF. No screenshot was invented or altered.

## Before submission

- Submit Items 2/3/4 PDFs with their linked evidence if requested by the instructor.
- Confirm any expanded LMS wording beyond the supplied criteria; the local screenshot
  does not expose rubric rows.
- Item 1 final report remains deferred. Complete its Network/POST Payload/Response
  screenshots using the brief checklist in Assignment 1 README, only in the disposable fixture.
- Optional Item 3 documentation screenshot instructions are in Assignment 3 README;
  no required written request/response field is missing.
