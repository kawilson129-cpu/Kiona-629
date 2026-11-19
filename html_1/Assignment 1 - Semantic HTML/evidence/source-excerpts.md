# Verbatim source excerpts

Original code, not a newly implemented feature. Line ranges are 1-based, inclusive.
Excerpt text is UTF-8 decoded with normalized line endings; raw source hashes
are recorded separately. Omitted spans are separate fenced blocks.

## Header letterhead

`derexi-policy-pilot/backend/static/index.html:18–23`

```html
  <header class="letterhead" aria-label="Document letterhead">
    <span>AURUM&nbsp;CAPITAL&nbsp;BANK</span>
    <span class="lh-sub">Policy &amp; Governance Division</span>
    <span class="lh-date js-today">—</span>
    <span class="lh-class">INTERNAL</span>
  </header>
```

## Primary navigation

`derexi-policy-pilot/backend/static/index.html:38–46`

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
```

## Main mount point and footer

`derexi-policy-pilot/backend/static/index.html:82–90`

```html
  <!-- App ------------------------------------------------------------------->
  <main id="app" tabindex="-1"></main>

  <!-- Letterhead footer ----------------------------------------------------->
  <footer class="foot" aria-label="Page footer">
    <span>AURUM&nbsp;CAPITAL&nbsp;BANK</span>
    <span class="regs">Policy content follows federal banking regulation: GLBA / Reg&nbsp;P, Safeguards Rule, BSA/AML, CIP, SAR, OFAC, UDAAP, Reg&nbsp;Z, Reg&nbsp;B, Reg&nbsp;E&nbsp;&amp;&nbsp;CC.</span>
    <span class="js-recon-mode">Live register</span>
  </footer>
```

