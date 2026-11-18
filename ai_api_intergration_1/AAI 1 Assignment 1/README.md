# AI API Integration 1 — DeRexi final project

**PASS for all four supplied rubric items, within the verified scope below.**
This is the existing DeRexi application, not a second app. The original course
folder spelling `ai_api_intergration_1/` is preserved. No application feature
changes were necessary; the missing work was course-specific verification and
structured evidence. Instructor grading remains separate.

Read the [before/after rubric analysis](rubric-checklist.md),
[structured API evidence and examples](api-evidence.md), and
[test outcomes](test-results.md). Actual labelled screenshots and sanitized JSON
are in [the evidence run](evidence/20261118-api/README.md).

The primary demonstration is authenticated **GET `/policies`** → Library rows and
**POST `/ask`** → Assistant guidance. These use actual loopback HTTP, existing
FastAPI handlers, real development bearer verification/RBAC and disposable SQLite.
PostgreSQL search is **MOCKED to no matches**; AI and email are disabled. Public
Pulse calls also verified two real JSON APIs plus two RSS sources. RSS alone is
not counted as two REST methods. Production auth, Supabase and external AI are
**UNVERIFIED by this coursework**, not claimed live successes.

## Reproduce the focused verification

From the repository root, use the existing `.venv`, Node and Chrome; no installs
are needed on the verified Mac. Use a new, unused output name on every rerun.
Port **8041** is exclusively the disposable fixture; do not substitute the normal
DeRexi server on 8000 or a production URL. Public sources may change or fail later;
such failures must remain visible in the new results.

Terminal 1 — start the actual application with the existing isolated test fixture:

```sh
derexi-policy-pilot/.venv/bin/python -B derexi-policy-pilot/backend/tests/api_integration_evidence.py serve --output ai_api_intergration_1/evidence/recheck-01 --live-public
```

Terminal 2 — real socket HTTP checks (15 checks, including public sources):

```sh
derexi-policy-pilot/.venv/bin/python -B derexi-policy-pilot/backend/tests/api_integration_evidence.py http --output ai_api_intergration_1/evidence/recheck-01 --live-public
```

For a fully offline secured-API demonstration, omit `--live-public` from both
commands: 12 core HTTP checks run; do not claim fresh public-feed verification.
The browser suite below expects the live-public fixture.

Terminal 3 — dedicated headless Chrome; leave other browser profiles alone:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --disable-background-networking --disable-sync --no-first-run --no-default-browser-check --remote-debugging-address=127.0.0.1 --remote-debugging-port=9241 --user-data-dir="$PWD/ai_api_intergration_1/.runtime/chrome-recheck-01" about:blank
```

Terminal 2 — seven checks using the original UI, actual responses and screenshot
capture after entry animations finish:

```sh
node derexi-policy-pilot/backend/tests/test_api_integration_browser.mjs ai_api_intergration_1/evidence/recheck-01
```

Stop only these dedicated fixture/browser processes with Ctrl+C in their own
terminals when done. SQLite records disappear; evidence persists in the course
folder. Browser profiles stay in ignored `.runtime/`; do not publish them.

## Reproducible curl demonstration

Run only while the disposable fixture above is running. The token stays in shell
memory and is not printed. Do not use verbose curl output, copy Authorization
headers into evidence, or take unsanitized HAR captures.

```sh
API_BASE='http://127.0.0.1:8041'
DEMO_TOKEN=$(curl --fail --silent --show-error "$API_BASE/dev-auth/token" \
  --header 'Content-Type: application/json' \
  --data '{"user_id":8}' | derexi-policy-pilot/.venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

curl --silent --show-error --write-out '\nHTTP %{http_code}\n' \
  --header 'Accept: application/json' \
  --header "Authorization: Bearer $DEMO_TOKEN" "$API_BASE/policies"

curl --silent --show-error --write-out '\nHTTP %{http_code}\n' \
  --header 'Accept: application/json' --header 'Content-Type: application/json' \
  --header "Authorization: Bearer $DEMO_TOKEN" \
  --data '{"question":"How should I handle a hypothetical policy exception?"}' "$API_BASE/ask"

curl --silent --show-error --write-out '\nHTTP %{http_code}\n' \
  --header 'Content-Type: application/json' \
  --header "Authorization: Bearer $DEMO_TOKEN" \
  --data '{"question":"   "}' "$API_BASE/ask"

curl --silent --show-error --write-out '\nHTTP %{http_code}\n' "$API_BASE/policies"
curl --silent --show-error --max-time 70 --write-out '\nHTTP %{http_code}\n' \
  --header 'Accept: application/json' "$API_BASE/api/pulse?limit=5"
unset DEMO_TOKEN
```

Expected statuses in order after token acquisition: **200, 200, 422, 401, 200**.
Check Pulse's per-source `ok` fields too; its local 200 can include source errors.
POST creates only synthetic fixture conversations; record IDs/timestamps will vary.

## Exact screenshot capture instructions by rubric item

Start the dedicated fixture. Open `http://127.0.0.1:8041/ui/?as=8#library` at
1440×1000 and confirm **Sam Okonkwo · Employee**. Wait for animations to settle.
All coursework screenshots must be labelled **local fixture / synthetic SQLite /
search mocked / AI off** where relevant. The automated captures already carry
these labels; for manual captures include this scope in the screenshot caption.

| Rubric item | Exact capture steps | Existing evidence |
|---|---|---|
| 1. GET and POST | Open DevTools → Network, enable Preserve log, filter to Fetch/XHR. Reload Library; confirm GET `/policies` 200. Select Policy Assistant, enter `How should I handle a hypothetical policy exception?`, click **Ask DeRexi**, confirm POST `/ask` 200. Capture the Network table showing Name, Method and Status; hide request headers/tokens. | Actual Network JSON in `browser-results.json`; UI captures 01/02. A combined DevTools screenshot was not captured. |
| 2. Formatted display | In Library capture the two rows including Employee Leave, version 1.0 and owner. Then open Assistant, submit the question above, scroll to the answer and capture its plain-English guidance and routing card. | `screenshots/01-get-library.png`, `02-post-assistant.png` |
| 3. Structured exchange | Open `api-evidence.md` in an editor/preview beside `http-results.json`. Show one GET and POST method, full URL, redacted headers, request body, status and response JSON. Capture only these sanitized files. | Complete written evidence exists; a documentation-panel screenshot was not captured. |
| 4. Working API/friendly output | Capture the Assistant answer after POST. Also open Pulse, wait for source indicators, and capture its source counts and titled/date-labelled article cards. For security proof, show the sanitized 401 transcript separately. | `02-post-assistant.png`, `03-get-pulse.png`; H02/H11/H12 security checks |

Actual screenshots are browser captures, not generated mockups. The Library's
unchanged “Live register” UI badge describes its UI mode; the evidence label makes
clear that its policy records are synthetic. Public-feed screenshots contain real
retrieved articles. No screenshot of production login or an AI-provider response
is supplied. Optional additional submission captures above remain for the user.
