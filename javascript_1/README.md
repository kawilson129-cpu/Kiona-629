# JavaScript 1 · DeRexi Priority Practice

One functional, standalone project demonstrates all eight rubric criteria.
The calculator uses impact × likelihood plus explicit context flags to produce an
explained priority. All inputs are synthetic; the scoring rules are illustrative
classroom rules. No account, backend, production data or API is involved.

## Launch

From the repository root, serve only the three project files:

```sh
python3 -m http.server 8061 --bind 127.0.0.1 --directory javascript_1/final_project
```

Open [http://127.0.0.1:8061](http://127.0.0.1:8061). Stop with Ctrl+C.
No install or build step. All styles, fonts and application code work without
remote assets. Select a scenario, choose Calculate priority, change inputs to
recompute, and Reset to start again. Open the browser console to inspect the same
result as structured output.

## Folder structure

```text
javascript_1/
├── final_project/
│   ├── index.html
│   ├── styles.css
│   └── script.js              # the only application JavaScript file
├── 01_centralized_javascript/report.md
├── 02_interactive_webpage/report.md
├── 03_descriptive_variables/report.md
├── 04_distinct_data_types/report.md
├── 05_mathematical_operations/report.md
├── 06_decision_structures/report.md
├── 07_logical_operators/report.md
├── 08_javascript_output/report.md
├── README.md
├── verification.md
├── PRODUCT.md                # scoped project/visual decisions
├── verify_project.py         # offline checks + actual browser automation
└── evidence/                 # results, source provenance and two screenshots
```

## Eight-point rubric checklist

| # | Criterion and separate report | Status |
|---|---|---|
| 1 | [Centralized JavaScript](01_centralized_javascript/report.md) | PASS |
| 2 | [Interactive Webpage](02_interactive_webpage/report.md) | PASS |
| 3 | [Descriptive Variables](03_descriptive_variables/report.md) | PASS |
| 4 | [Distinct Data Types](04_distinct_data_types/report.md) | PASS |
| 5 | [Mathematical Operations](05_mathematical_operations/report.md) | PASS |
| 6 | [Decision Structures](06_decision_structures/report.md) | PASS |
| 7 | [Logical Operators](07_logical_operators/report.md) | PASS |
| 8 | [JavaScript Output](08_javascript_output/report.md) | PASS |

**8/8 covered.** [Verification](verification.md) distinguishes real execution from
untested environments. Latest results: **12 static checks + 33 real browser checks,
0 failures**; B05 includes the separately retained 100-case calculation matrix.

## Reuse and boundaries

Inspected the canonical DeRexi [CSS](../derexi-policy-pilot/backend/static/style.css),
[HTML shell](../derexi-policy-pilot/backend/static/index.html) and
[JavaScript](../derexi-policy-pilot/backend/static/app.js). Reused the Ledger palette,
serif wordmark/hairline layout, native semantic controls, event listeners and safe
textContent output patterns. The small new calculator is the authorized coursework
implementation, not a duplicate of DeRexi's backend-dependent application.

The existing LMS screenshot contains only the assignment heading; the detailed
criteria come from the supplied brief. [Source hashes](evidence/source-review.json)
confirm the reviewed files, root memory and original screenshot remain unchanged.
All work stays in this course. No production features, credentials or other
coursework were changed; no commit or push.

## Reproduce verification

```sh
node --check javascript_1/final_project/script.js
python3 -B javascript_1/verify_project.py
python3 -B javascript_1/verify_project.py --browser
```

The last command requires the installed macOS Chrome and Node's built-in WebSocket
(tested with Node 26). It starts a temporary loopback-only static server, uses a
dedicated ignored course browser profile, saves real captures/results and closes
only its own browser/server. It never attaches to an existing browser or app.
Reruns replace the latest evidence; the initial failed keyboard attempts remain
separately retained. No browser/test dependency is installed.
