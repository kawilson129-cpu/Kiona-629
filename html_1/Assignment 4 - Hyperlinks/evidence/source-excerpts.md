# Verbatim source excerpts

Original code, not a newly implemented feature. Line ranges are 1-based, inclusive.
Excerpt text is UTF-8 decoded with normalized line endings; raw source hashes
are recorded separately. Omitted spans are separate fenced blocks.

## SPA hash anchors explicitly excluded from separate-page proof

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

## Original anchor creation and attribute helper

`derexi-policy-pilot/backend/static/pulse.js:71–92`

```javascript
  function el(tag, props, kids) {
    var node = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (key) {
        var value = props[key];
        if (value === null || value === undefined) return;
        if (key === 'class') node.className = value;
        else if (key === 'text') node.textContent = value;
        // innerHTML is used only for constant icon markup, never feed content.
        else if (key === 'html') node.innerHTML = value;
        else if (key === 'on') Object.keys(value).forEach(function (evt) {
          node.addEventListener(evt, value[evt]);
        });
        else node.setAttribute(key, value);
      });
    }
    if (kids !== undefined && kids !== null) {
      if (typeof kids === 'string' || typeof kids === 'number') node.textContent = kids;
      else if (kids.forEach) kids.forEach(function (child) { if (child) node.appendChild(child); });
      else node.appendChild(kids);
    }
    return node;
```

## Existing HTTPS destination guard

`derexi-policy-pilot/backend/static/pulse.js:128–131`

```javascript
  function externalLink(url) {
    // Defence in depth: the API already guarantees https, but never trust it.
    return /^https:\/\//i.test(String(url || ''));
  }
```

## Featured publication hyperlink

`derexi-policy-pilot/backend/static/pulse.js:243–253`

```javascript
    var title = el('h2', { class: 'lead-title' });
    if (externalLink(article.url)) {
      title.appendChild(el('a', {
        href: article.url,
        target: '_blank',
        rel: 'noopener noreferrer',
        text: article.title
      }));
    } else {
      title.textContent = article.title;
    }
```

## Read the original publication anchor

`derexi-policy-pilot/backend/static/pulse.js:264–272`

```javascript
    var cta = el('div', { class: 'lead-cta-row' });
    if (externalLink(article.url)) {
      cta.appendChild(el('a', {
        class: 'lead-cta',
        href: article.url,
        target: '_blank',
        rel: 'noopener noreferrer',
        html: 'Read the original publication' + ARROW
      }));
```

