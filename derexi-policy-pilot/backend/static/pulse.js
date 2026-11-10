/* ==========================================================================
   Pulse — Regulatory Intelligence (view module)
   --------------------------------------------------------------------------
   Read-only editorial surface for /api/pulse. All feed text is written with
   textContent, never innerHTML, so a compromised or malformed feed cannot
   inject markup into DeRexi. No data is ever invented: if a source is down or
   an article has no summary, the UI says so or omits the field.
   ========================================================================== */
(function () {
  'use strict';

  var governanceContext = {};
  function startDraft(article) {
    if (!governanceContext.canGovern) return null;
    var b = el('button', { type: 'button', class: 'btn btn-ghost gov-pulse-start', text: 'Propose policy action' });
    b.addEventListener('click', function () { if (governanceContext.canGovern) governanceContext.fromPulse(article); });
    return b;
  }

  var ALL = 'All Updates';
  var FILTERS = [
    ALL,
    'Banking & Finance',
    'Regulations',
    'Cybersecurity',
    'Privacy & Data Protection',
    'Supervisory Guidance'
  ];

  // Document type -> stamp styling. Unknown types fall back to neutral news.
  var STATUS_CLASS = {
    'Proposed Rule': 'st-proposed',
    'Final Rule': 'st-final',
    'Notice': 'st-notice',
    'Supervisory Guidance': 'st-guidance',
    'Standards Draft': 'st-draft',
    'General News': 'st-news'
  };

  var TYPES = ['All Types', 'Final Rules', 'Proposed Rules', 'Notices', 'Guidance', 'Standards Drafts', 'General News'];
  var TYPE_STATUS = { 'Final Rules': 'Final Rule', 'Proposed Rules': 'Proposed Rule',
    Notices: 'Notice', Guidance: 'Supervisory Guidance', 'Standards Drafts': 'Standards Draft', 'General News': 'General News' };

  // Topics can overlap: a banking rule belongs to both Banking and Regulations.
  function topicMatches(a, topic) {
    if (topic === ALL || a.category === topic) return true;
    if (topic === 'Banking & Finance') return a.source === 'FDIC' || a.source === 'Federal Reserve' ||
      /bank|financial|reserve|currency|credit union/i.test(a.agency || '');
    if (topic === 'Supervisory Guidance') return /guidance/i.test(a.title || '');
    return false;
  }
  function typeMatches(a, type) { return type === 'All Types' || a.status === TYPE_STATUS[type]; }
  function rankArticles(articles) {
    return articles.slice().sort(function (a, b) {
      return (b.score || 0) - (a.score || 0) || String(b.published).localeCompare(String(a.published)) ||
        String(b.title).localeCompare(String(a.title)) || String(a.id).localeCompare(String(b.id));
    });
  }
  function classification(article) {
    var inferred = article.classified_by !== 'source';
    return el('span', { class: 'pulse-classification', text: inferred
      ? 'Source: ' + (article.doc_type || 'Unspecified') + ' · Reading category inferred by Pulse'
      : 'Source classification: ' + (article.doc_type || article.status) });
  }

  var CLIENT_CACHE_MS = 60000;
  var REQUEST_TIMEOUT_MS = 30000;
  var clientCache = { at: 0, data: null };

  /* ---------------------------------------------------------------- dom */
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
  }

  var ARROW = '<svg viewBox="0 0 24 24" class="arw" fill="none" stroke="currentColor" ' +
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M7 17L17 7M9 7h8v8"/></svg>';

  /* -------------------------------------------------------------- format */
  function formatDate(iso) {
    if (!iso) return 'Undated';
    var parts = String(iso).split('-');
    if (parts.length !== 3) return String(iso);
    var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (isNaN(d.getTime())) return String(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function formatLongDate(iso) {
    if (!iso) return 'Not stated by the source';
    var parts = String(iso).split('-');
    if (parts.length !== 3) return String(iso);
    var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (isNaN(d.getTime())) return String(iso);
    return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }

  function formatTimestamp(iso) {
    if (!iso) return 'Just now';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return 'Just now';
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit'
    });
  }

  function externalLink(url) {
    // Defence in depth: the API already guarantees https, but never trust it.
    return /^https:\/\//i.test(String(url || ''));
  }

  /* ----------------------------------------------------------------- api */
  function loadFeed(force) {
    if (!force && clientCache.data && (Date.now() - clientCache.at) < CLIENT_CACHE_MS) {
      return Promise.resolve(clientCache.data);
    }

    var controller = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT_MS) : null;

    return fetch('/api/pulse?limit=60', {
      headers: { Accept: 'application/json' },
      signal: controller ? controller.signal : undefined
    }).then(function (response) {
      if (!response.ok) throw new Error('Pulse returned HTTP ' + response.status + '.');
      return response.json();
    }).then(function (data) {
      if (!data || !Array.isArray(data.articles)) {
        throw new Error('Pulse returned an unexpected response.');
      }
      clientCache = { at: Date.now(), data: data };
      return data;
    }).catch(function (err) {
      if (err && err.name === 'AbortError') {
        throw new Error('Pulse took too long to respond.');
      }
      throw err;
    }).then(function (data) {
      if (timer) clearTimeout(timer);
      return data;
    }, function (err) {
      if (timer) clearTimeout(timer);
      throw err;
    });
  }

  /* --------------------------------------------------------------- pieces */
  function masthead(data) {
    var head = el('section', { class: 'pulse-masthead' });

    head.appendChild(el('p', { class: 'pulse-kicker', text: 'Regulatory Intelligence · Aurum Capital Bank' }));
    head.appendChild(el('h1', { class: 'pulse-title', text: 'Pulse' }));
    head.appendChild(el('p', { class: 'pulse-tagline', text: 'What\u2019s changing. What matters. What comes next.' }));
    head.appendChild(el('p', {
      class: 'pulse-intro',
      text: 'Federal banking, privacy, and cybersecurity developments. Direct from the issuing agencies.'
    }));

    var meta = el('div', { class: 'pulse-meta' });
    var stamp = el('span', { class: 'pulse-updated', role: 'status' });
    var refresh = el('button', {
      type: 'button',
      class: 'pulse-refresh',
      text: 'Refresh',
      'aria-label': 'Reload Pulse from the government feeds'
    });

    if (data) {
      stamp.textContent = 'Last updated ' + formatTimestamp(data.generated_at);
    } else {
      stamp.textContent = 'Checking the federal feeds\u2026';
    }

    meta.appendChild(stamp);
    meta.appendChild(refresh);
    head.appendChild(meta);
    head.appendChild(el('div', { class: 'pulse-underrule' }));
    return { head: head, stamp: stamp, refresh: refresh };
  }

  function sourceStrip(data) {
    var strip = el('div', { class: 'pulse-sources', 'aria-label': 'Feed status' });
    var sources = data && data.sources ? data.sources : {};

    Object.keys(sources).forEach(function (name) {
      var s = sources[name] || {};
      var down = s.ok === false;
      var item = el('span', { class: 'pulse-src' + (down ? ' is-down' : '') });
      item.appendChild(el('span', { class: 'pdot' }));
      item.appendChild(el('span', { class: 'pname', text: name }));

      if (down) {
        var reason = s.error ? ' \u00b7 ' + s.error : '';
        var stale = s.stale ? ' \u00b7 showing last good fetch' : '';
        item.appendChild(el('span', { class: 'pcnt', text: 'unavailable' + reason + stale }));
        item.setAttribute('title', name + ' could not be reached' + (s.error ? ': ' + s.error : ''));
      } else {
        item.appendChild(el('span', { class: 'pcnt', text: String(s.count || 0) + ' items' }));
        item.setAttribute('title', name + ' responded normally');
      }
      strip.appendChild(item);
    });

    return strip;
  }

  function statusStamp(status) {
    var cls = STATUS_CLASS[status] || 'st-news';
    return el('span', { class: 'pulse-stamp ' + cls, text: status || 'General News' });
  }

  function featured(article) {
    var lead = el('article', { class: 'pulse-lead' });

    var main = el('div', { class: 'lead-main' });
    main.appendChild(el('p', { class: 'lead-kicker' }, [
      el('span', { class: 'lead-flag', text: 'Featured' }),
      el('span', { class: 'lead-dot', text: '\u00b7' }),
      el('span', { text: article.category || 'Banking & Finance' })
    ]));

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
    main.appendChild(title);

    if (article.summary) main.appendChild(el('p', { class: 'lead-dek', text: article.summary }));

    main.appendChild(el('div', { class: 'lead-meta' }, [
      el('span', { text: article.agency || article.source }),
      el('span', { class: 'sep', text: '\u2014' }),
      el('span', { text: formatLongDate(article.published) })
    ]));

    var cta = el('div', { class: 'lead-cta-row' });
    if (externalLink(article.url)) {
      cta.appendChild(el('a', {
        class: 'lead-cta',
        href: article.url,
        target: '_blank',
        rel: 'noopener noreferrer',
        html: 'Read the original publication' + ARROW
      }));
    }
    cta.appendChild(statusStamp(article.status));
    main.appendChild(cta);
    main.appendChild(classification(article));
    var draftButton = startDraft(article); if (draftButton) main.appendChild(draftButton);
    lead.appendChild(main);

    // A factual docket, not an inference: only fields the source supplied.
    var docket = el('aside', { class: 'lead-docket', 'aria-label': 'Publication details' });
    docket.appendChild(el('p', { class: 'docket-label', text: 'At a glance' }));

    function row(label, value) {
      if (!value) return;
      docket.appendChild(el('dl', { class: 'docket-row' }, [
        el('dt', { text: label }),
        el('dd', { text: value })
      ]));
    }
    row('Issuing body', article.agency || article.source);
    row('Document type', article.status);
    row('Published', formatLongDate(article.published));
    row('Source feed', article.source);
    docket.appendChild(el('p', { class: 'pulse-classification', text: 'Selection weighs document significance, subject relevance, source and recency. No urgency is implied.' }));
    lead.appendChild(docket);

    return lead;
  }

  function storyCard(article) {
    var card = el('article', { class: 'pulse-story' });

    var rail = el('div', { class: 'ps-rail' });
    rail.appendChild(el('span', { class: 'ps-date', text: formatDate(article.published) }));
    rail.appendChild(el('span', { class: 'ps-source', text: article.source }));
    card.appendChild(rail);

    var body = el('div', { class: 'ps-body' });
    var tags = el('div', { class: 'ps-tags' });
    tags.appendChild(el('span', { class: 'ps-cat', text: article.category || 'Banking & Finance' }));
    tags.appendChild(statusStamp(article.status));
    body.appendChild(tags);
    body.appendChild(classification(article));

    var title = el('h3', { class: 'ps-title' });
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
    body.appendChild(title);

    // No summary in the feed means no summary here — never filler copy.
    if (article.summary) body.appendChild(el('p', { class: 'ps-dek', text: article.summary }));

    var foot = el('div', { class: 'ps-foot' });
    foot.appendChild(el('span', { class: 'ps-agency', text: article.agency || article.source }));
    if (externalLink(article.url)) {
      foot.appendChild(el('a', {
        class: 'ps-link',
        href: article.url,
        target: '_blank',
        rel: 'noopener noreferrer',
        html: 'Read original' + ARROW
      }));
    }
    body.appendChild(foot);
    var draftButton = startDraft(article); if (draftButton) body.appendChild(draftButton);

    card.appendChild(body);
    return card;
  }

  /* ------------------------------------------------------- bento layout */
  /*
     Content-aware packing for the lower article feed only ("The Intelligence
     Desk"). A plain row grid makes every row as tall as its tallest card, which
     is what produced the large gaps under short cards. Instead each card is
     measured once and given an explicit grid row span, so columns fill from the
     top with no holes; `grid-auto-flow: dense` (in style.css) backfills the
     space beside taller cards. Card text is never clipped: heights are measured
     from the real rendered card, and no max-height or line clamp is applied.
     The DOM is never reordered, so reading, tab and screen-reader order stay
     exactly as ranked by the feed.
  */
  var BENTO_ROW = 2;       // row unit in px — must match grid-auto-rows in style.css
  var BENTO_GUTTER = 18;   // gutter in px — matches the column gap and card margin
  var bentoObserver = null;

  function columnCount(feed) {
    var template = getComputedStyle(feed).gridTemplateColumns || '';
    var repeat = /repeat\(\s*(\d+)/.exec(template);
    if (repeat) return Number(repeat[1]);
    var tracks = template.trim().split(/\s+/).filter(Boolean);
    return tracks.length && tracks[0] !== 'none' ? tracks.length : 1;
  }

  // Content opener: the first desk card is the highest-ranked remaining story,
  // so it becomes the full-width feature tile on the widest layout. The span is
  // decided here, before any card is measured, so no card is ever re-widened
  // after its height is known (which would leave a stale row span).
  function opensDesk(index) {
    return index === 0;
  }

  // Pack one feed. Idempotent: every pass clears the previous placement first,
  // so filtering, refreshing and resizing all converge on the same layout.
  function layoutFeed(feed) {
    if (!feed || !feed.isConnected) return;
    var cards = [];
    Array.prototype.forEach.call(feed.children, function (child) {
      if (child.classList.contains('pulse-story')) cards.push(child);
    });
    if (!cards.length) return;

    // Back to the plain grid so heights are measured at their natural size.
    feed.classList.remove('is-bento');
    cards.forEach(function (card) {
      card.style.gridRowStart = '';
      card.style.gridRowEnd = '';
      card.style.gridColumnStart = '';
      card.style.gridColumnEnd = '';
    });

    // One column needs no packing: a normal stack already has exact gutters.
    var columns = columnCount(feed);
    if (columns < 2) return;

    // The feature card spans every column, and only on the widest layout. Pin
    // its width before measuring so its height is measured at its real width.
    var feature = cards.length > 1 && cards[0].classList.contains('is-wide') && columns >= 3;
    if (feature) {
      cards[0].style.gridColumnStart = '1';
      cards[0].style.gridColumnEnd = 'span ' + columns;
    }

    // Single measurement pass: column widths are already final for every card.
    var spans = cards.map(function (card) {
      return Math.max(1, Math.ceil((card.offsetHeight + BENTO_GUTTER) / BENTO_ROW));
    });
    var widths = cards.map(function (card, index) {
      return feature && index === 0 ? columns : 1;
    });

    // Shortest-column packing. Each card starts exactly where its column (or,
    // for the feature card, every column) finished, so a column never contains a
    // vertical hole and the columns stay balanced. A two-column tile was tried
    // and rejected: it always leaves a gap under the shorter of the two columns.
    var next = [];
    for (var c = 0; c < columns; c++) next.push(1);
    cards.forEach(function (card, index) {
      var width = widths[index];
      var bestColumn = 0;
      var bestRow = Infinity;
      for (var start = 0; start + width <= columns; start++) {
        var row = Math.max.apply(null, next.slice(start, start + width));
        if (row < bestRow) { bestRow = row; bestColumn = start; }
      }
      card.style.gridColumnStart = String(bestColumn + 1);
      card.style.gridColumnEnd = 'span ' + width;
      card.style.gridRowStart = String(bestRow);
      card.style.gridRowEnd = String(bestRow + spans[index]);
      for (var k = bestColumn; k < bestColumn + width; k++) next[k] = bestRow + spans[index];
    });
    feed.classList.add('is-bento');
  }

  // Re-pack when the feed's width *or* the viewport changes. Viewport width
  // matters on its own: card headlines use vw-relative type, so their heights
  // change even when the capped content column keeps the same width.
  // One window-level hook and one observer are reused, so re-mounting the view
  // (or re-importing this module in tests) never stacks listeners.
  function watchFeed(feed) {
    window.__derexiPulseBento = { feed: feed, layout: layoutFeed };
    if (!window.__derexiPulseBentoBound) {
      window.__derexiPulseBentoBound = true;
      var queued = 0;
      window.addEventListener('resize', function () {
        if (queued) return;
        queued = window.requestAnimationFrame(function () {
          queued = 0;
          var bento = window.__derexiPulseBento;
          if (bento && bento.feed.isConnected) bento.layout(bento.feed);
        });
      }, { passive: true });
    }
    if (typeof ResizeObserver !== 'function') return;
    if (bentoObserver) { bentoObserver.disconnect(); bentoObserver = null; }
    // Height-only notifications are ignored: they come from our own placement
    // and would otherwise loop.
    var lastWidth = feed.clientWidth;
    bentoObserver = new ResizeObserver(function () {
      var width = feed.clientWidth;
      if (width === lastWidth) return;
      lastWidth = width;
      layoutFeed(feed);
    });
    bentoObserver.observe(feed);
  }

  // Webfonts (Fraunces / Plus Jakarta Sans) change measured heights after first
  // paint, so the feed is packed again once they have settled.
  function watchFonts(feed) {
    if (!document.fonts || !document.fonts.ready || !document.fonts.ready.then) return;
    document.fonts.ready.then(function () { layoutFeed(feed); });
  }

  function skeleton() {
    var wrap = el('div', { class: 'pulse-loading', 'aria-busy': 'true' });
    wrap.appendChild(el('div', { class: 'skel pulse-skel-lead' }));
    for (var i = 0; i < 4; i++) {
      var row = el('div', { class: 'pulse-skel-row' });
      row.appendChild(el('div', { class: 'skel', style: 'height:14px;width:90px' }));
      var body = el('div', { class: 'pulse-skel-body' });
      body.appendChild(el('div', { class: 'skel', style: 'height:18px;width:70%' }));
      body.appendChild(el('div', { class: 'skel', style: 'height:12px;width:92%;margin-top:10px' }));
      row.appendChild(body);
      wrap.appendChild(row);
    }
    wrap.appendChild(el('p', { class: 'pulse-loading-note', text: 'Reading the federal register feeds\u2026' }));
    return wrap;
  }

  function notice(mark, copy, actionLabel, action) {
    var card = el('div', { class: 'empty card pulse-notice' });
    card.appendChild(el('div', { class: 'mark', text: mark }));
    card.appendChild(el('div', { class: 'ok', text: copy }));
    if (action) {
      card.appendChild(el('button', {
        type: 'button',
        class: 'btn btn-ghost pulse-retry',
        text: actionLabel,
        on: { click: action }
      }));
    }
    return card;
  }

  /* ---------------------------------------------------------------- view */
  function render(app, context) {
    governanceContext = context || {};
    var view = el('div', { class: 'view' });
    var headParts = masthead(null);
    var body = el('div', { class: 'pulse-body' });
    view.appendChild(headParts.head);
    view.appendChild(body);
    app.appendChild(view);

    var state = { data: null, filter: ALL, type: 'All Types', strip: null };
    view.classList.add('pulse-view');

    headParts.refresh.addEventListener('click', function () {
      headParts.refresh.disabled = true;
      headParts.refresh.textContent = 'Refreshing\u2026';
      start(true);
    });

    function start(force) {
      body.innerHTML = '';
      body.appendChild(skeleton());
      loadFeed(force).then(function (data) {
        state.data = data;
        headParts.stamp.textContent = 'Last updated ' + formatTimestamp(data.generated_at);
        headParts.refresh.disabled = false;
        headParts.refresh.textContent = 'Refresh';
        if (state.strip && state.strip.parentNode) state.strip.parentNode.removeChild(state.strip);
        state.strip = sourceStrip(data);
        view.insertBefore(state.strip, body);
        paint();
      }).catch(function (err) {
        headParts.stamp.textContent = 'Feed unavailable';
        headParts.refresh.disabled = false;
        headParts.refresh.textContent = 'Refresh';
        body.innerHTML = '';
        body.appendChild(notice(
          'Pulse could not be reached',
          'The regulatory feed did not respond (' + String(err && err.message ? err.message : 'unknown error').replace(/\.$/, '') + '). No articles are shown rather than showing stale or invented ones.',
          'Try again',
          function () { start(true); }
        ));
      });
    }

    function paint() {
      var data = state.data;
      var articles = data.articles || [];
      body.innerHTML = '';

      if (!articles.length) {
        body.appendChild(notice(
          'No updates are available',
          'The sources responded but returned no articles. This page never substitutes placeholder stories for real ones.',
          'Check again',
          function () { start(true); }
        ));
        return;
      }

      // Facet counts apply the other active filter; focus survives repaint.
      function filters(names, dimension, label) {
        var group = el('div', { class: 'pulse-filter-group' });
        group.appendChild(el('p', { class: 'pulse-filter-label', text: label }));
        var bar = el('div', { class: 'pulse-filters', role: 'group', 'aria-label': label });
        names.forEach(function (name) {
          var count = articles.filter(function (a) {
            return dimension === 'filter' ? topicMatches(a, name) && typeMatches(a, state.type)
              : topicMatches(a, state.filter) && typeMatches(a, name);
          }).length;
          var chip = el('button', { type: 'button', class: 'pulse-chip' + (state[dimension] === name ? ' is-current' : ''),
            'aria-pressed': String(state[dimension] === name), 'data-facet': dimension, 'data-value': name }, [
            el('span', { text: name }), el('span', { class: 'pchip-count', text: String(count) })
          ]);
          chip.addEventListener('click', function () {
            state[dimension] = name;
            paint();
            var buttons = body.querySelectorAll('[data-facet]');
            Array.prototype.forEach.call(buttons, function (button) {
              if (button.dataset.facet === dimension && button.dataset.value === name) button.focus();
            });
          });
          bar.appendChild(chip);
        });
        group.appendChild(bar);
        body.appendChild(group);
      }
      filters(FILTERS, 'filter', 'Explore by topic');
      filters(TYPES, 'type', 'Document type');
      var scoped = articles.filter(function (a) { return topicMatches(a, state.filter) && typeMatches(a, state.type); });
      var results = el('div', { class: 'pulse-results' });
      results.appendChild(el('p', { role: 'status', 'aria-live': 'polite', text: scoped.length + ' updates · ' + state.filter + ' / ' + state.type }));
      if (state.filter !== ALL || state.type !== 'All Types') {
        results.appendChild(el('button', { type: 'button', class: 'pulse-refresh', text: 'Reset filters', on: { click: function () {
          state.filter = ALL; state.type = 'All Types'; paint(); body.querySelector('.pulse-chip').focus();
        } } }));
      }
      body.appendChild(results);
      if (!scoped.length) {
        body.appendChild(el('p', { class: 'pulse-river-empty', text: 'No updates match this combination. Reset filters or try another document type.' }));
        return;
      }
      var ranked = rankArticles(scoped);
      var mosaic = el('section', { class: 'pulse-mosaic', 'aria-label': 'Editorial selection' });
      mosaic.appendChild(featured(ranked[0]));
      ranked.slice(1, 3).forEach(function (a, index) {
        var card = storyCard(a); card.classList.add('pulse-spotlight', 'spotlight-' + index); mosaic.appendChild(card);
      });
      body.appendChild(mosaic);

      // Radar is read-only, uses API-curated prompts, and follows both facets.
      var radar = el('section', { class: 'pulse-radar', 'aria-label': 'On the Radar' });
      radar.appendChild(el('h2', { text: 'On the Radar' }));
      radar.appendChild(el('p', { class: 'radar-intro', text: 'Developments for closer reading. These suggestions are informational, not verified legal obligations.' }));
      var radarGrid = el('div', { class: 'radar-grid' });
      (data.radar || []).forEach(function (entry) {
        var a = scoped.find(function (a) { return a.id === entry.id; });
        if (!a) return;
        var item = el('article', { class: 'radar-entry' });
        item.appendChild(el('p', { class: 'radar-label', text: entry.label }));
        var title = el('h3');
        if (externalLink(a.url)) title.appendChild(el('a', { href: a.url, target: '_blank', rel: 'noopener noreferrer', text: a.title }));
        else title.textContent = a.title;
        item.appendChild(title);
        item.appendChild(el('p', { class: 'radar-meta', text: a.source + ' · ' + formatDate(a.published) }));
        item.appendChild(statusStamp(a.status));
        item.appendChild(classification(a));
        if (entry.note) item.appendChild(el('p', { class: 'radar-note', text: entry.note }));
        radarGrid.appendChild(item);
      });
      if (!radarGrid.childNodes.length) radarGrid.appendChild(el('p', { text: 'No curated reading prompts match these filters.' }));
      radar.appendChild(radarGrid);
      body.appendChild(radar);

      var rest = scoped.filter(function (a) { return !ranked.slice(0, 3).some(function (pick) { return a.id === pick.id; }); });
      var desk = el('section', { class: 'pulse-river' });
      desk.appendChild(el('div', { class: 'pulse-river-head' }, [
        el('h2', { class: 'pulse-river-title', text: 'The Intelligence Desk' }),
        el('span', { class: 'pulse-river-count', text: rest.length + ' more updates' })
      ]));
      var feed = el('div', { class: 'pulse-feed' });
      rest.forEach(function (a, index) {
        var card = storyCard(a);
        if (opensDesk(index)) card.classList.add('is-wide');
        feed.appendChild(card);
      });
      if (!rest.length) feed.appendChild(el('p', { text: 'All matching updates appear in the editorial selection above.' }));
      desk.appendChild(feed); body.appendChild(desk);
      // Pack only now that the feed is in the document and heights are real.
      layoutFeed(feed);
      watchFeed(feed);
      watchFonts(feed);
      body.appendChild(el('p', { class: 'pulse-source-note', text: 'From four government feeds. Counts describe the loaded selection of up to 60 updates, not the complete agency archives. Decorative treatments are typography and color only.' }));
    }

    // First paint: cached data renders instantly, otherwise skeletons show.
    start(false);
  }

  window.PulseView = { render: render };
})();
