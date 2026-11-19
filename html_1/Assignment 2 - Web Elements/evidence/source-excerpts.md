# Verbatim source excerpts

Original code, not a newly implemented feature. Line ranges are 1-based, inclusive.
Excerpt text is UTF-8 decoded with normalized line endings; raw source hashes
are recorded separately. Omitted spans are separate fenced blocks.

## DeRexi div containers and anchor tags

`derexi-policy-pilot/backend/static/index.html:26–46`

```html
  <div class="topbar-wrap">
    <div class="topbar">
      <div class="wordmark" role="presentation">
        <svg class="wm-seal" viewBox="0 0 32 32" aria-hidden="true">
          <circle cx="16" cy="16" r="14.5" fill="none" stroke="currentColor" stroke-width="1"/>
          <circle cx="16" cy="16" r="10.5" fill="none" stroke="currentColor" stroke-width="0.6"/>
          <path d="M16 9.5v13M9.5 16h13" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>
        </svg>
        <span class="wm-name"><i>De</i><b>Rexi</b></span>
        <span class="wm-region">Policy &amp; Governance</span>
      </div>

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

## Original DOM element helper

`derexi-policy-pilot/backend/static/governance.js:5–9`

```javascript
  function el(tag, text, cls) {
    var n = document.createElement(tag);
    if (text !== null && text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    return n;
```

## DeRexi creates an ordered list at runtime

`derexi-policy-pilot/backend/static/governance.js:100–105`

```javascript
      var templates=el('section',null,'gw-template-card');templates.appendChild(el('p','A structured beginning','view-kicker'));
      templates.appendChild(el('h3','Create from a template'));
      templates.appendChild(el('p','A consistent foundation for new policies, security requirements and operating procedures.'));
      var templateAction=button('Create from Template',chooseTemplate,'btn btn-ghost');templates.appendChild(templateAction);
      templates.appendChild(button('Write a policy',function(){editor(null);},'gw-text-action'));
      var steps=el('ol',null,'gw-steps');['Draft with purpose','Independent peer review','Final approval','Controlled publication'].forEach(function(x){steps.appendChild(el('li',x));});templates.appendChild(steps);creation.appendChild(templates);
```

## Literal image on the existing DeRexi case-study page

`docs/derexi-policy-pilot.md:24–28`

```html
  <div class="project-image-wrap" style="aspect-ratio: 16/9;">
    <img
      src="{{ '/assets/images/derexi-policy-pilot-hero.png' | relative_url }}"
      alt="DeRexi Policy Pilot Project">
  </div>
```

## Literal unordered project-details list

`docs/derexi-policy-pilot.md:63–88`

```html
    <div>
      <span class="eyebrow">Project Details</span>

      <ul style="list-style: none; font-size: 0.875rem; color: var(--text-secondary);">

        <li style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          Focus: Information Security
        </li>

        <li style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          Area: Policy Governance
        </li>

        <li style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          Security Component: Incident Assistance
        </li>

        <li style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          Status: MVP In Development
        </li>

        <li style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          Year: 2026
        </li>

      </ul>
```

## Case-study anchor back to Projects

`docs/derexi-policy-pilot.md:327–331`

```html
  <a href="{{ '/projects.html' | relative_url }}"
     style="text-decoration: none; color: var(--text-color); font-weight: 500;
     border-bottom: 1px solid var(--text-color);">
    ← Back to Projects
  </a>
```

