# DeRexi — "The Ledger" UI Redesign Preview

Design preview only. **Nothing here touches production.** The live app stays in
`derexi-policy-pilot/backend/static/` until you look at this and decide.

Open it:

```
open ui-redesign-preview/index.html
```

## What this is

A complete redesign of DeRexi's front end, styled as a private-bank ledger:
cream paper, espresso ink, gold leaf, Fraunces serif + Plus Jakarta Sans,
hairline rules, status "stamps", film grain. Fully interactive, no build step,
no frameworks.

### Screens
1. **Persona roster** — a "choose your desk" gate. Pick any of the 12 seeded
   users (Sam Okonkwo · Employee, Maya Patel · Policy Owner, Lucy Chen ·
   System Admin jump out). Role changes what you can see.
2. **Policy Assistant** — ask in plain words. DeRexi answers "in ink" with a
   confidence strip, citation cards (click to open the drawer), and routes to a
   policy owner when it is unsure. Thumbs up/down feedback is wired up.
3. **Policy Library** — category rail + search + ledger rows with status
   stamps, version, next review. Click a row for the detail drawer with version
   history.
4. **Governance (Policy Owners + System Admins only)** — KPI columns
   (43 policies, 77 conversations, 2 reviews due, 67% helpfulness), most-cited
   policies bar chart, clarification queue (take/resolve), incident triage.

## Data

Two modes, same UI:

- **Default (mock):** `index.html` — served from `mock-data.js`, seeded to match
  the **production Supabase snapshot** (real policy titles, categories, counts,
  users, clarifications, incidents, dashboard totals from Sep 24, 2026).
- **Live API:** `index.html?live=1` — same adapter, pointed at
  `http://127.0.0.1:8000`. Requires `uvicorn main:app --reload` inside
  `derexi-policy-pilot/`. CORS must allow your origin for it to work.

## How promotion works (later, if you accept)

1. Copy `style.css` and `app.js` into `derexi-policy-pilot/backend/static/`,
   replacing the three current files.
2. Drop `mock-data` — the `app.js` API adapter already targets the real
   endpoints (`/ask`, `/policies`, `/policies/{id}`, `/dashboard/policy-health`,
   `/clarifications`, `/incidents`, `/feedback`, `/users`, `/roles`, `/categories`).
3. `renderGate` and the persona select are preview convenience only; replace
   `choosePersona` with the real auth user.

## Endpoint contract (both modes return the same shapes)

| UI action            | Mock                  | Live API                      |
| -------------------- | --------------------- | ----------------------------- |
| Ask a question       | local topic match     | `POST /ask`                   |
| Policy list/search   | seeded rows           | `GET /policies`, `/policies/search?q=` |
| Policy detail        | seeded + versions     | `GET /policies/{id}`          |
| Dashboard            | seeded totals         | `GET /dashboard/policy-health`|
| Clarification queue  | seeded                | `GET /clarifications`         |
| Incidents            | seeded                | `GET /incidents`, `/incident-categories` |
| Feedback             | local toast           | `POST /feedback`              |

## Files

```
ui-redesign-preview/
  index.html      shell + letterhead + topbar + footer
  style.css       full design system (tokens, ledger, inksurface, drawer, gates)
  app.js          routing, adapters, all view builders, micro-interactions
  mock-data.js    seeded dataset mirroring the production snapshot
  README.md       this file
```