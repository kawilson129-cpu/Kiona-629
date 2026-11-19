# Verbatim source excerpts

Original code, not a newly implemented feature. Line ranges are 1-based, inclusive.
Excerpt text is UTF-8 decoded with normalized line endings; raw source hashes
are recorded separately. Omitted spans are separate fenced blocks.

## Document language and metadata

`derexi-policy-pilot/backend/static/index.html:1–5`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
```

## Class and accessible landmark name

`derexi-policy-pilot/backend/static/index.html:18–18`

```html
  <header class="letterhead" aria-label="Document letterhead">
```

## Link, data, button and state attributes

`derexi-policy-pilot/backend/static/index.html:38–48`

```html
      <nav class="nav-links" aria-label="Primary">
        <a href="#assist" data-view="assist" class="nav-link is-current">Policy Assistant</a>
        <a href="#library" data-view="library" class="nav-link">Policy Library</a>
        <a href="#messages" data-view="messages" class="nav-link">Messages<span class="nav-badge is-hidden js-msg-badge" aria-label="Unread messages">0</span></a>
        <a href="#dashboard" data-view="dashboard" class="nav-link js-gov-link is-hidden">Dashboard</a>
        <a href="#governance" data-view="governance" class="nav-link js-gov-link is-hidden">Governance</a>
        <a href="#pulse" data-view="pulse" class="nav-link">Pulse</a>
        <a href="#routing" data-view="routing" class="nav-link js-routing-link is-hidden">Technical Routing</a>
      </nav>

      <button type="button" class="notify-btn js-notify" id="notify-btn" aria-label="Notifications" aria-expanded="false">
```

## Labels, select, boolean disabled and title

`derexi-policy-pilot/backend/static/index.html:55–65`

```html
      <button type="button" id="signout-btn" class="btn btn-ghost is-hidden">Sign out</button>
      <div class="persona">
        <label class="persona-label" for="persona-select">Signed in as</label>
        <div class="select-shell">
          <select id="persona-select" class="select persona-select" aria-label="Signed-in employee" disabled>
            <option>Sign-in required</option>
          </select>
        </div>
        <button type="button" class="btn btn-ghost btn-recon is-hidden" title="Choose an authorized identity" aria-label="Choose a different identity">
          Change
        </button>
```

## Main focus attribute

`derexi-policy-pilot/backend/static/index.html:83–83`

```html
  <main id="app" tabindex="-1"></main>
```

## Script source attributes

`derexi-policy-pilot/backend/static/index.html:95–98`

```html
  <script src="governance.js"></script>
  <script src="support.js"></script>
  <script src="app.js"></script>
  <script src="pulse.js"></script>
```

