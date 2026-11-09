(function () {
  'use strict';

  var qa = function (sel) { return document.querySelector(sel); };
  var qaa = function (sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); };

  function h(tag, props, kids) {
    var n = document.createElement(tag);
    if (props) {
      var keys = Object.keys(props);
      for (var i = 0; i < keys.length; i++) {
        var k = keys[i], v = props[k];
        if (v === null || v === undefined) continue;
        if (k === 'class') n.className = v;
        else if (k === 'text') n.textContent = v;
        else if (k === 'html') n.innerHTML = v;
        else if (k === 'dataset') { for (var dk in v) n.dataset[dk] = v[dk]; }
        else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), v);
        else if (k === 'value' || k === 'selected' || k === 'disabled') n[k] = v;
        else n.setAttribute(k, v);
      }
    }
    if (kids !== undefined && kids !== null) {
      if (typeof kids === 'string' || typeof kids === 'number') n.textContent = kids;
      else if (kids.forEach) kids.forEach(function (c) { if (c) n.appendChild(c); });
      else n.appendChild(kids);
    }
    return n;
  }

  var ICONS = {
    send: '<path d="M5 19L19 5M19 5H8M19 5v11"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>',
    close: '<path d="M6 6l12 12M18 6L6 18"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
    flag: '<path d="M6 21V4M6 6h10l-2 3.5L16 13H6"/>',
    chat: '<path d="M4 5h16v10H9l-5 4V5z"/>',
    book: '<path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H12v17H5.5A2.5 2.5 0 0 0 3 22.5V5.5zM12 3h6.5A2.5 2.5 0 0 1 21 5.5v17A2.5 2.5 0 0 0 18.5 20H12V3z"/>',
    seal: '<circle cx="16" cy="16" r="13.5" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="16" cy="16" r="9" fill="none" stroke="currentColor" stroke-width="0.7"/><path d="M16 10.5v11M10.5 16h11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>',
    clr: '<path d="M5 7h14M9 7V5h6v2M8 7l1 13h6l1-13"/>',
    route: '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 7v6M12 13l-4 4M12 13l4 4"/>'
  };
  function icon(name) {
    return '<svg viewBox="0 0 24 24" class="ic" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICONS[name] || '') + '</svg>';
  }

  function initials(name) {
    var parts = String(name || '').trim().split(/\s+/);
    return ((parts[0] || '')[0] || '') + ((parts[1] || '')[0] || '');
  }

  function titleRole(role) {
    return role === 'System Administrator' ? 'System Admin' : role;
  }

  function fmtDate(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function fmtToday() {
    var d = new Date();
    var mo = d.toLocaleDateString('en-US', { month: 'short' }).toUpperCase();
    return mo + ' ' + d.getDate().toString().padStart(2, '0') + ' ' + d.getFullYear();
  }

  /* ---------------------------------------------------------------- state */
  var state = {
    mode: 'live',
    users: [],
    roles: [],
    personaId: null,
    thread: [],
    lastAsk: null,
    assistMode: 'ask',
    openThreadId: null,
    // Week 7 identity. The token is verified server-side; personaId is only a
    // development convenience for choosing which seeded user to sign in as.
    authConfig: null,
    devAuth: false,
    devUsers: [],
    me: null,
    token: null,
    sessionVersion: 0,
    inbox: {
      folder: 'inbox',
      q: '',
      status: '',
      threadId: null,
      data: null,
      thread: null,
      loading: false,
      offset: 0,
      drafts: {}
    },
    notifications: { unread_total: 0, items: [], triage_count: 0 },
    notifyOpen: false
  };

  function setToken(token) {
    state.token = token || null;
    try {
      if (token) sessionStorage.setItem('derexi.accessToken', token);
      else sessionStorage.removeItem('derexi.accessToken');
    } catch (e) {}
  }

  function refreshDevToken() {
    if (!state.personaId) return Promise.reject(new Error('No persona selected'));
    var requestedId = state.personaId;
    return fetch('/dev-auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: state.personaId })
    }).then(function (r) {
      if (!r.ok) throw new Error('Session expired');
      return r.json();
    }).then(function (data) {
      if (requestedId !== state.personaId) throw new Error('Identity selection changed');
      setToken(data.access_token);
      return data;
    });
  }

  function api(path, opts, retried) {
    opts = opts || {};
    var sessionVersion = state.sessionVersion;
    var cfg = { method: opts.method || 'GET', headers: {}, credentials: 'same-origin' };
    if (state.token) cfg.headers.Authorization = 'Bearer ' + state.token;
    if (opts.body) { cfg.headers['Content-Type'] = 'application/json'; cfg.body = opts.body; }
    return fetch(path, cfg).then(function (r) {
      if (sessionVersion !== state.sessionVersion) throw new Error('Session changed');
      if (r.status === 401 && state.devAuth && state.personaId && !retried) {
        return refreshDevToken().then(function () { return api(path, opts, true); });
      }
      if (!r.ok) {
        return r.json().catch(function () { return {}; }).then(function (body) {
          var detail = body && body.detail;
          var err = new Error(typeof detail === 'string' ? detail : 'Request failed (' + r.status + ')');
          err.status = r.status;
          throw err;
        });
      }
      return r.json();
    });
  }

  function loadAll() {
    return Promise.all([api('/users'), api('/roles'), api('/me')]).then(function (r) {
      state.users = r[0] || [];
      state.roles = r[1] || [];
      state.me = r[2] || null;
    });
  }

  function currentUser() {
    if (state.me && state.me.id === state.personaId) {
      return { id: state.me.id, full_name: state.me.full_name, role: state.me.role };
    }
    for (var i = 0; i < state.users.length; i++) if (state.users[i].id === state.personaId) return state.users[i];
    for (var j = 0; j < state.devUsers.length; j++) {
      if (state.devUsers[j].id === state.personaId) return state.devUsers[j];
    }
    return null;
  }

  function isAdmin() {
    return !!(state.me && state.me.role === 'System Administrator');
  }

  function isGovernanceAllowed() {
    if (state.me && state.me.role) {
      return state.me.role === 'System Administrator' || state.me.role === 'Policy Owner';
    }
    var u = currentUser();
    if (!u) return false;
    var rid = u.role_id || u.roleId;
    if (rid > 1) return true;
    var rn = String(u.role || '').toLowerCase();
    return rn.indexOf('policy owner') !== -1 || rn.indexOf('system') !== -1;
  }

  /* ---------------------------------------------------------------- notify */
  var NOTIFY_KIND = { assigned: 'Assigned', reply: 'Reply', triage: 'Triage' };

  function paintBadges(n) {
    var total = Number(n || 0);
    ['.js-msg-badge', '.js-notify-count'].forEach(function (sel) {
      var el = qa(sel);
      if (!el) return;
      el.textContent = total > 99 ? '99+' : String(total);
      el.classList.toggle('is-hidden', total === 0);
    });
    var btn = qa('#notify-btn');
    if (btn) btn.classList.toggle('has-unread', total > 0);
  }

  function loadNotifications() {
    if (!state.token) return Promise.resolve();
    return api('/messages/notifications').then(function (data) {
      state.notifications = data || { unread_total: 0, items: [], triage_count: 0 };
      paintBadges(state.notifications.unread_total);
      renderNotificationPanel();
    }).catch(function () { /* notifications are not critical to the page */ });
  }

  function timeAgo(iso) {
    if (!iso) return '';
    var then = new Date(iso).getTime();
    if (isNaN(then)) return '';
    var mins = Math.round((Date.now() - then) / 60000);
    if (mins < 1) return 'now';
    if (mins < 60) return mins + 'm';
    if (mins < 1440) return Math.round(mins / 60) + 'h';
    if (mins < 10080) return Math.round(mins / 1440) + 'd';
    return fmtDate(iso);
  }

  function renderNotificationPanel() {
    var list = qa('.js-notify-list');
    if (!list) return;
    var data = state.notifications || {};
    list.innerHTML = '';
    if (!data.items || !data.items.length) {
      list.appendChild(h('div', { class: 'notify-empty', text: 'You are all caught up. Replies and assignments appear here.' }));
    } else {
      data.items.forEach(function (item) {
        var row = h('button', { type: 'button', class: 'notify-item' }, [
          h('span', { class: 'notify-kind kind-' + item.kind, text: NOTIFY_KIND[item.kind] || 'Reply' }),
          h('span', { class: 'notify-main' }, [
            h('span', { class: 'notify-subject', text: item.subject || 'Policy clarification' }),
            h('span', { class: 'notify-snippet', text: snippet(item.snippet || '', 92) })
          ]),
          h('span', { class: 'notify-time', text: timeAgo(item.at) })
        ]);
        row.addEventListener('click', function () { openThreadFromNotice(item.thread_id); });
        list.appendChild(row);
      });
    }

    var foot = qa('.js-notify-foot');
    if (!foot) return;
    foot.innerHTML = '';
    var triage = Number(data.triage_count || 0);
    foot.appendChild(h('span', { class: 'notify-foot-meta', text: triage ? triage + ' unassigned in triage' : 'No unassigned threads' }));
    foot.appendChild(h('button', { type: 'button', class: 'btn btn-ghost', text: 'Open Messages', onclick: function () { closeNotify(); goTo('#messages'); } }));
  }

  function goTo(hash) {
    if (location.hash === hash) render();
    else location.hash = hash;
  }

  function openThreadFromNotice(id) {
    closeNotify();
    state.inbox.threadId = id;
    history.replaceState(null, '', '#messages/' + id);
    render();
  }

  function toggleNotify(force) {
    var panel = qa('.js-notify-panel');
    var btn = qa('.js-notify');
    if (!panel) return;
    var show = typeof force === 'boolean' ? force : panel.classList.contains('is-hidden');
    panel.classList.toggle('is-hidden', !show);
    if (btn) btn.setAttribute('aria-expanded', show ? 'true' : 'false');
  }

  function closeNotify() {
    toggleNotify(false);
  }

  /* ---------------------------------------------------------------- toast */
  function toast(msg) {
    var region = qa('.js-toasts');
    if (!region) return;
    var t = h('div', { class: 'toast' }, [
      h('span', { class: 'ic-wrap', html: icon('check') }),
      h('span', { text: msg })
    ]);
    region.appendChild(t);
    setTimeout(function () { t.style.opacity = '0'; t.style.transition = 'opacity 300ms'; }, 3200);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 3600);
  }

  /* ---------------------------------------------------------------- topbar */
  function setRecon() {
    var el = qa('.js-recon-mode');
    if (el) el.textContent = 'Live register';
    var today = qa('.js-today');
    if (today) today.textContent = fmtToday();
  }

  function buildPersonaSelect() {
    var sel = qa('#persona-select');
    if (!sel) return;
    sel.innerHTML = '';
    (state.devAuth ? state.devUsers : state.users).forEach(function (u) {
      var o = document.createElement('option');
      o.value = u.id;
      o.textContent = u.full_name + ' · ' + titleRole(u.role);
      if (u.id === state.personaId) o.selected = true;
      sel.appendChild(o);
    });
    sel.disabled = !state.devAuth;
    qaa('.btn-recon').forEach(function (b) { b.classList.toggle('is-hidden', !state.devAuth); });
    sel.onchange = function () { choosePersona(parseInt(sel.value, 10), false); };
  }

  function refreshNav() {
    qaa('.js-gov-link').forEach(function (a) {
      a.classList.toggle('is-hidden', !isGovernanceAllowed());
    });
    if (!isGovernanceAllowed() && location.hash === '#governance') location.hash = '#assist';
  }

  function choosePersona(id, fromGate) {
    if (!state.devAuth) return;
    var previous = state.personaId;
    state.sessionVersion++;
    state.personaId = id;
    closeNotify();
    state.notifications = { unread_total: 0, items: [], triage_count: 0 };
    paintBadges(0);
    qa('#app').replaceChildren(h('div', { class: 'msgs-empty', role: 'status', text: 'Starting the selected test session…' }));
    try { localStorage.setItem('derexi.personaId', String(id)); } catch (e) {}

    // In development the server mints a short-lived token for the selected
    // seeded user. In production this branch is never shown; the bearer token
    // comes from the real Supabase session.
    var activate = state.devAuth
      ? refreshDevToken().then(function () { return loadAll(); })
      : Promise.resolve();

    activate.then(function () {
      var u = currentUser();
      buildPersonaSelect();
      refreshNav();
      if (fromGate) {
        var gate = qa('.js-gate');
        if (gate) gate.parentNode.removeChild(gate);
        qa('#app').classList.remove('is-hidden');
        document.body.style.overflow = '';
        toast('Signed in as ' + u.full_name + ' · ' + titleRole(u.role));
      } else if (previous !== id) {
        toast('Now viewing as ' + u.full_name + ' · ' + titleRole(u.role));
      }
      if (state.thread.length) state.thread = [];
      state.lastAsk = null;
      state.openThreadId = null;
      state.inbox.data = null;
      state.inbox.thread = null;
      state.inbox.folder = 'inbox';
      state.inbox.q = '';
      state.inbox.status = '';
      state.inbox.threadId = null;
      state.inbox.offset = 0;
      state.inbox.drafts = {};
      if (/^#messages\//.test(location.hash)) history.replaceState(null, '', '#messages');
      render();
      loadNotifications();
    }).catch(function (err) {
      toast('Could not start the session (' + err.message + ')');
    });
  }

  /* ---------------------------------------------------------------- render */
  function currentView() {
    if (!state.personaId) return null;
    var hash = location.hash || '#assist';
    if (hash === '#governance' && !isGovernanceAllowed()) return 'assist';
    if (hash === '#library') return 'library';
    if (hash.indexOf('#messages') === 0) return 'messages';
    if (hash === '#governance') return 'governance';
    if (hash === '#pulse') return 'pulse';
    return 'assist';
  }

  function render() {
    var app = qa('#app');
    var v = currentView();
    if (v === null) { app.innerHTML = ''; renderBoot(); return; }
    app.innerHTML = '';
    // The inbox needs three columns; every other surface keeps the editorial measure.
    app.classList.toggle('is-wide', v === 'messages');
    var fn = v === 'library' ? renderLibrary
      : v === 'governance' ? renderGovernance
      : v === 'messages' ? renderMessages
      : v === 'pulse' ? renderPulse
      : renderAssist;
    fn(app);
    qaa('.nav-link').forEach(function (a) {
      a.classList.toggle('is-current', a.dataset.view === v);
    });
    // On narrow widths the nav scrolls horizontally; keep the active item in view.
    var navBar = qa('.nav-links');
    var active = qa('.nav-link.is-current');
    if (navBar && active) {
      var barBox = navBar.getBoundingClientRect();
      var itemBox = active.getBoundingClientRect();
      if (itemBox.left < barBox.left) navBar.scrollLeft -= (barBox.left - itemBox.left) + 8;
      else if (itemBox.right > barBox.right) navBar.scrollLeft += (itemBox.right - barBox.right) + 8;
    }
  }

  function renderBoot() {
    qa('#app').classList.add('is-hidden');
    document.body.appendChild(renderGate(false));
    document.body.style.overflow = 'hidden';
  }

  /* ---------------------------------------------------------------- gate */
  function renderGate(closable) {
    var u = currentUser();
    var wrap = h('div', { class: 'gate-wrap js-gate', style: 'position:fixed;inset:0;z-index:80;background:var(--paper-0);overflow:auto' });
    var grid = h('div', { class: 'gate' });
    var head = h('div', { class: 'view-head' });
    head.appendChild(h('p', { class: 'view-kicker', text: 'DeRexi · Policy & Governance' }));
    head.appendChild(h('h1', { class: 'view-title', html: 'Choose whose desk <em>you sit at</em>' }));
    head.appendChild(h('p', { class: 'view-sub', text: 'The board changes with the role. Employees get Ask and Library; Policy Owners and System Administrators also get Governance.' }));

    if (closable) {
      var closeBtn = h('button', { type: 'button', class: 'gate-close', html: icon('close'), 'aria-label': 'Close roster' });
      closeBtn.addEventListener('click', closeGate);
      grid.appendChild(closeBtn);
      wrap.addEventListener('click', function (e) { if (e.target === wrap) closeGate(); });
    }

    var list = h('div', { class: 'gate-list' });
    var people = state.users.length ? state.users : state.devUsers;
    people.forEach(function (pers) {
      var roleName = (pers.role && pers.role.name) ? pers.role.name : (typeof pers.role === 'string' ? pers.role : '');
      var accessLabel = roleName ? roleName.toUpperCase() : 'EMPLOYEE';
      var row = h('button', { type: 'button', class: 'gate-row' + (u && pers.id === u.id ? ' is-cur' : ''), onclick: function () { choosePersona(pers.id, true); } }, [
        h('span', { class: 'gate-avatar', text: initials(pers.full_name) }),
        h('span', { class: 'gate-id' }, [
          h('span', { class: 'gate-name', text: pers.full_name }),
          h('span', { class: 'gate-sub', text: (pers.department || '') + ' · ' + accessLabel })
        ]),
        h('span', { class: 'gate-flag', text: accessLabel })
      ]);
      list.appendChild(row);
    });

    grid.appendChild(head);
    grid.appendChild(list);
    wrap.appendChild(grid);
    return wrap;
  }

  function closeGate() {
    var gate = qa('.js-gate');
    if (gate) gate.parentNode.removeChild(gate);
    document.body.style.overflow = '';
  }

  /* ---------------------------------------------------------------- assist */
  var SUGGESTS = [
    'How much paid time off do I get each year?',
    'What is the parental leave policy?',
    'I received a suspicious email. What should I do?',
    'A credit application is missing documents. What do I send the applicant?',
    'Can I use ChatGPT for work tasks?',
    'How should I report a lost work laptop?'
  ];

  function renderAssist(app) {
    var view = h('div', { class: 'view' });

    var head = h('div', { class: 'view-head' });
    head.appendChild(h('p', { class: 'view-kicker', text: 'Policy Assistant' }));
    head.appendChild(h('h1', { class: 'view-title', html: 'Ask in plain words, <em>get guidance in ink</em>' }));
    head.appendChild(h('p', { class: 'view-sub', text: 'Ask a policy question or report a security incident. DeRexi cites the governing policy, routes to its owner when it can\u2019t answer with confidence, and logs incident reports for the security desk.' }));

    var tabs = h('div', { class: 'tabs', role: 'tablist' }, [
      assistTab('Ask a question', 'ask'),
      assistTab('Report an incident', 'report')
    ]);

    view.appendChild(head);
    view.appendChild(tabs);
    if (state.assistMode === 'report') view.appendChild(buildReportSection());
    else buildAskSection(view);
    app.appendChild(view);

    qaa('.tabs .tab').forEach(function (t) {
      t.classList.toggle('is-current', t.dataset.tab === (state.assistMode || 'ask'));
    });

    function assistTab(label, key) {
      var t = h('button', { type: 'button', class: 'tab', role: 'tab', dataset: { tab: key }, text: label });
      t.addEventListener('click', function () {
        if (state.assistMode === key) return;
        state.assistMode = key;
        render();
      });
      return t;
    }

    function buildAskSection(view) {
      var ta = h('textarea', { rows: '2', placeholder: 'Example: How much paid time off do I get after my first year?', value: '' });
      ta.setAttribute('aria-label', 'Your policy question');
      var askBtn = h('button', { type: 'button', class: 'send-btn', html: icon('send') + '<span>Ask DeRexi</span>' });
      askBtn.setAttribute('aria-label', 'Ask DeRexi');
      var composer = h('div', { class: 'composer' }, [ta, askBtn]);

      function buildChip(label, fn) {
        return h('button', { type: 'button', class: 'chip', onclick: fn.bind(null, label), text: label });
      }

      function submitInto(value) {
        var q = String(value || '').trim();
        if (!q) return;
        ta.value = '';
        askBtn.disabled = true;
        state.thread.push({ sender: 'user', body: q });
        replay(view);
        showThinking(view);
        api('/ask', { method: 'POST', body: JSON.stringify({ user_id: state.personaId, question: q }) }).then(function (r) {
          state.lastAsk = r;
          removeThinking();
          state.thread.push({ sender: 'derexi', body: r.answer, result: r });
          replay(view);
          askBtn.disabled = false;
          safeFocus(ta);
        }).catch(function (err) {
          removeThinking();
          state.thread.push({ sender: 'derexi', body: 'DeRexi could not reach the policy engine (' + err.message + ').', result: null });
          replay(view);
          askBtn.disabled = false;
        });
      }

      ta.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitInto(ta.value); }
      });
      askBtn.addEventListener('click', function () { submitInto(ta.value); });

      var hints = h('div', { class: 'ask-hint' }, [
        h('span', { class: 'ask-hint-label', text: 'Try' }),
        buildChip('How much paid time off?', submitInto),
        buildChip('Parental leave details', submitInto),
        buildChip('Can I use ChatGPT for work tasks?', submitInto),
        buildChip('A credit application is missing documents', submitInto),
        buildChip('Lost laptop', submitInto)
      ]);

      var surface = h('section', { class: 'ask-surface' });
      var inner = h('div', { class: 'ask-inner' });
      inner.appendChild(composer);
      inner.appendChild(hints);
      surface.appendChild(inner);

      var sec = h('section', { class: 'section' });
      var secHead = h('div', { class: 'section-head' });
      secHead.appendChild(h('h2', { class: 'section-title', text: 'This conversation' }));
      var clr = h('button', { type: 'button', class: 'btn btn-ghost' + (state.thread.length ? '' : ' is-hidden'), onclick: function () { state.thread = []; state.lastAsk = null; render(); }, html: icon('clr') + '<span style="margin-left:7px">Clear</span>' });
      secHead.appendChild(h('span', null, [clr]));
      sec.appendChild(secHead);
      var threadRoot = h('div', { class: 'thread' });
      state.thread.forEach(function (m) { threadRoot.appendChild(buildMsg(m)); });
      sec.appendChild(threadRoot);

      var suggestsSec = h('section', { class: 'section' });
      suggestsSec.appendChild(h('div', { class: 'section-head' }, [
        h('h2', { class: 'section-title', text: 'Common questions' }),
        h('span', { class: 'section-meta', text: 'Curated' })
      ]));
      var sugRow = h('div', { class: 'suggests' });
      SUGGESTS.forEach(function (s) {
        sugRow.appendChild(h('button', { type: 'button', class: 'suggest', onclick: function () { askSuggested(s); }, text: s }));
      });
      suggestsSec.appendChild(sugRow);

      view.appendChild(surface);
      view.appendChild(sec);
      view.appendChild(suggestsSec);

      function replay(root) {
        var thr = qa('.thread', root);
        if (!thr) return;
        thr.innerHTML = '';
        state.thread.forEach(function (m) { thr.appendChild(buildMsg(m)); });
        thr.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function buildReportSection() {
      var wrap = h('div', null);

      var form = h('div', { class: 'report-form' });

      var catField = h('div', { class: 'field' });
      catField.appendChild(h('label', { for: 'inc-cat', text: 'Incident category' }));
      var catSel = h('select', { id: 'inc-cat', name: 'category' });
      catSel.appendChild(h('option', { value: '', text: 'Select a category\u2026' }));
      catField.appendChild(catSel);

      var descField = h('div', { class: 'field' });
      descField.appendChild(h('label', { for: 'inc-desc', text: 'What happened?' }));
      var ta = h('textarea', { id: 'inc-desc', rows: '4', placeholder: 'Describe the incident in your own words. Include what you saw and when.', value: '' });
      descField.appendChild(ta);

      var submit = h('button', { type: 'button', class: 'send-btn', html: icon('flag') + '<span>Report incident</span>' });
      submit.setAttribute('aria-label', 'Report incident');

      form.appendChild(catField);
      form.appendChild(descField);
      form.appendChild(h('div', { class: 'report-note', text: 'Severity is assigned by the security team from the category. Do not include passwords or card numbers.' }));
      form.appendChild(submit);
      wrap.appendChild(form);

      var out = h('div', { class: 'report-out' });
      wrap.appendChild(out);

      var mine = h('section', { class: 'section' });
      mine.appendChild(h('div', { class: 'section-head' }, [
        h('h2', { class: 'section-title', text: 'Your reports' }),
        h('span', { class: 'section-meta', text: 'Live' })
      ]));
      var mineRoot = h('div', null);
      mine.appendChild(mineRoot);
      wrap.appendChild(mine);

      api('/incident-categories').then(function (cats) {
        (cats || []).forEach(function (c) {
          catSel.appendChild(h('option', { value: String(c.id), text: c.name }));
        });
      }).catch(function () {});

      function loadMine() {
        api('/incidents?reporter_id=' + state.personaId).then(function (list) {
          mineRoot.innerHTML = '';
          var pane = h('div', { class: 'pane' });
          pane.appendChild(h('div', { class: 'pane-head' }, [
            h('h3', { text: 'Your reports' }),
            h('span', { class: 'badge', text: String((list || []).length) })
          ]));
          var body = h('div', { class: 'pane-body' });
          if (!list || !list.length) {
            body.appendChild(h('div', { class: 'empty' }, [h('div', { class: 'ok', text: 'You have not reported any incidents.' })]));
          } else {
            var rows = h('div', { class: 'my-reports' });
            list.forEach(function (inc) {
              rows.appendChild(h('div', { class: 'inc-row' }, [
                h('div', { class: 'inc-top' }, [
                  h('span', { class: 'id', text: '#I-' + String(inc.id).padStart(3, '0') }),
                  h('span', { class: 'stamp ' + stampCls(inc.status), html: '<span class="dot"></span>' + escText(inc.status) }),
                  inc.severity ? h('span', { class: 'stamp ' + stampCls(inc.severity), html: '<span class="dot"></span>' + escText(inc.severity) }) : null
                ]),
                h('div', { class: 'inc-q', text: inc.category || 'Uncategorized' }),
                h('div', { class: 'inc-desc', text: inc.description }),
                h('div', { class: 'inc-meta' }, [
                  h('span', { text: 'Reported ' + fmtDate(inc.created_at) }),
                  inc.assignee ? h('span', { text: 'Handler \u00b7 ' + inc.assignee }) : null
                ])
              ]));
            });
            body.appendChild(rows);
          }
          pane.appendChild(body);
          mineRoot.appendChild(pane);
        }).catch(function (err) {
          mineRoot.innerHTML = '';
          mineRoot.appendChild(h('div', { class: 'empty card' }, [
            h('div', { class: 'mark', text: 'Reports unavailable' }),
            h('div', { class: 'ok', text: err.message })
          ]));
        });
      }

      function renderConfirm(inc) {
        out.innerHTML = '';
        var card = h('div', { class: 'card card-pad report-confirm' });
        card.appendChild(h('div', { class: 'inc-top' }, [
          h('span', { class: 'id', text: '#I-' + String(inc.id).padStart(3, '0') }),
          h('span', { class: 'stamp ' + stampCls(inc.status), html: '<span class="dot"></span>' + escText(inc.status) }),
          inc.severity ? h('span', { class: 'stamp ' + stampCls(inc.severity), html: '<span class="dot"></span>' + escText(inc.severity) }) : null
        ]));
        card.appendChild(h('div', { class: 'inc-q', text: 'Report received' }));
        card.appendChild(h('div', { class: 'inc-desc', text: 'Your report is logged and will be reviewed by a security handler. Track its status under \u201cYour reports\u201d below.' }));
        if (inc.guidance) {
          card.appendChild(h('div', { class: 'report-guidance' }, [
            h('div', { class: 'g-title', text: inc.guidance.title + ' (v' + inc.guidance.version_no + ')' }),
            h('div', { class: 'g-excerpt', text: inc.guidance.excerpt }),
            h('button', { type: 'button', class: 'btn btn-ghost', text: 'Open policy', onclick: function () { openDrawer(inc.guidance.policy_id); } })
          ]));
        }
        out.appendChild(card);
      }

      submit.addEventListener('click', function () {
        var desc = ta.value.trim();
        if (!catSel.value) { toast('Choose an incident category first.'); return; }
        if (desc.length < 2) { toast('Describe the incident before submitting.'); return; }
        submit.disabled = true;
        api('/incidents', {
          method: 'POST',
          body: JSON.stringify({ reporter_id: state.personaId, category_id: parseInt(catSel.value, 10), description: desc })
        }).then(function (inc) {
          submit.disabled = false;
          ta.value = '';
          catSel.value = '';
          renderConfirm(inc);
          loadMine();
        }).catch(function (err) {
          submit.disabled = false;
          toast('Could not submit report (' + err.message + ')');
        });
      });

      loadMine();
      return wrap;
    }
  }

  function askSuggested(s) {
    render();
    var ta = qa('.composer textarea');
    if (ta) ta.value = s;
    var btn = qa('.send-btn');
    if (btn) btn.click();
  }

  function safeFocus(el) {
    try { el.focus(); } catch (e) {}
  }

  function showThinking(root) {
    var thr = qa('.thread', root);
    if (!thr) return;
    var m = h('div', { class: 'msg typing-wrap js-thinking' }, [
      h('span', { class: 'msg-avatar avatar-derexi', html: icon('seal') }),
      h('div', { class: 'msg-body typing' }, [h('span', { class: 'dot' }), h('span', { class: 'dot' }), h('span', { class: 'dot' })])
    ]);
    thr.appendChild(m);
  }

  function removeThinking() {
    qaa('.js-thinking').forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
  }

  function buildMsg(m) {
    var isUser = m.sender === 'user' || m.sender === 'Employee';
    var when = m.t ? fmtDate(m.t) : 'Just now';
    var avatar = isUser
      ? h('span', { class: 'msg-avatar avatar-user', text: initials(currentUser() ? currentUser().full_name : 'U') })
      : h('span', { class: 'msg-avatar avatar-derexi', html: icon('seal') });

    var bodyEl = h('div', { class: 'msg-body', text: m.body });
    var kids = [bodyEl];

    if (!isUser && m.result) {
      var r = m.result;
      if (!r.needs_clarification && r.confidence) {
        bodyEl.appendChild(h('div', { class: 'confidence' }, [
          h('span', { text: 'Confidence' }),
          h('span', { class: 'bar' }, [h('i', { style: 'width:' + Math.round(r.confidence * 100) + '%' })]),
          h('span', { text: r.confidence.toFixed(2) })
        ]));
      }
      if (r.citations && r.citations.length) {
        var cites = h('div', { class: 'cites' });
        r.citations.forEach(function (c, i) {
          cites.appendChild(buildCite(c, i + 1));
        });
        bodyEl.appendChild(cites);
      }
      if (r.needs_clarification) {
        bodyEl.appendChild(buildRouted(r));
      } else {
        bodyEl.appendChild(buildClarifyAction(r));
      }
      bodyEl.appendChild(buildFeedback(r));
    }

    var meta = h('div', { class: 'msg-meta', text: isUser ? (currentUser() ? currentUser().full_name : 'You') + ' · ' + when : 'DeRexi · Policy Engine · ' + when });

    var wrap = h('div', { class: 'msg' + (isUser ? ' msg-user' : '') });
    wrap.appendChild(avatar);
    var col = h('div', { class: 'msg-col' });
    kids.forEach(function (k) { col.appendChild(k); });
    col.appendChild(meta);
    wrap.appendChild(col);
    return wrap;
  }

  function buildCite(c, idx) {
    return h('button', { type: 'button', class: 'cite', onclick: function () { openDrawer(c.policy_id); } }, [
      h('span', { class: 'cite-idx', text: String(idx).padStart(2, '0') }),
      h('span', { class: 'cite-body' }, [
        h('span', { class: 'cite-head' }, [
          h('span', { class: 'cite-title', text: c.title })
        ]),
        h('span', { class: 'cite-meta' }, [
          h('span', { class: 'cite-version', text: 'v' + c.version_no }),
          h('span', { text: '· s ' + c.score.toFixed(4) })
        ])
      ]),
      h('span', { class: 'cite-score', text: 'policy ' + c.policy_id })
    ]);
  }

  function buildRouted(r) {
    var who = userName(r.assigned_to) || (r.triage ? 'the administrator triage queue' : 'a policy owner');
    var inner = h('div', null, [
      h('h4', { text: 'Routed to a policy owner' }),
      h('p', { text: 'This question needs a human judgment. It has been forwarded with a clarification request and will be answered there.' }),
      h('div', { class: 'who', text: 'Assigned · ' + who })
    ]);
    if (r.clarification_request_id) {
      inner.appendChild(h('button', {
        type: 'button',
        class: 'msgs-link',
        text: 'Open thread #C-' + String(r.clarification_request_id).padStart(4, '0'),
        onclick: function () { openThreadFromNotice(r.clarification_request_id); }
      }));
    }
    return h('div', { class: 'routed' }, [
      h('span', { class: 'ic-wrap', html: icon('route') }),
      inner
    ]);
  }

  /* A confident answer can still be incomplete. This lets the employee ask the
     cited policy's owner for further clarification without leaving the answer;
     the thread keeps the question, answer, citation, requester and timestamps. */
  function buildClarifyAction(r) {
    var wrap = h('div', { class: 'clarify-action' });
    var toggleBtn = h('button', { type: 'button', class: 'btn btn-ghost clarify-open', html: icon('route') + '<span>Ask the policy owner</span>' });
    toggleBtn.setAttribute('aria-expanded', 'false');
    wrap.appendChild(toggleBtn);

    var panel = h('div', { class: 'clarify-panel is-hidden' });
    var ta = h('textarea', { rows: '3', placeholder: 'Add the detail the owner needs in order to answer well.', 'aria-label': 'What is still unclear?' });
    var policySel = h('select', { class: 'clarify-select', 'aria-label': 'Policy to clarify' });
    var cites = (r.citations || []).filter(function (c) { return c.policy_id; });
    cites.forEach(function (c) {
      policySel.appendChild(h('option', { value: String(c.policy_id), text: c.title + (c.version_no ? ' · v' + c.version_no : '') }));
    });
    var sendBtn = h('button', { type: 'button', class: 'send-btn', html: icon('send') + '<span>Send request</span>' });
    sendBtn.setAttribute('aria-label', 'Send clarification request');
    var status = h('div', { class: 'clarify-status', role: 'status' });

    var field = h('label', { class: 'clarify-field' });
    field.appendChild(h('span', { class: 'k', text: 'What is still unclear?' }));
    field.appendChild(ta);

    var controls = h('div', { class: 'clarify-controls' });
    if (cites.length) controls.appendChild(policySel);
    controls.appendChild(sendBtn);

    panel.appendChild(field);
    panel.appendChild(controls);
    panel.appendChild(status);
    wrap.appendChild(panel);

    toggleBtn.addEventListener('click', function () {
      var hidden = panel.classList.contains('is-hidden');
      panel.classList.toggle('is-hidden', !hidden);
      toggleBtn.setAttribute('aria-expanded', hidden ? 'true' : 'false');
      if (hidden) { try { ta.focus(); } catch (e) {} }
    });

    sendBtn.addEventListener('click', function () {
      var note = ta.value.trim();
      status.innerHTML = '';
      if (note.length < 2) {
        status.appendChild(h('span', { class: 'err', text: 'Add a sentence so the owner has context.' }));
        return;
      }
      if (!r.conversation_id) {
        status.appendChild(h('span', { class: 'err', text: 'This answer is no longer linked to its conversation. Ask again to start a fresh thread.' }));
        return;
      }
      sendBtn.disabled = true;
      api('/clarifications', {
        method: 'POST',
        body: JSON.stringify({
          conversation_id: r.conversation_id,
          message_id: r.user_message_id,
          policy_id: policySel.value ? parseInt(policySel.value, 10) : null,
          context: note
        })
      }).then(function (t) {
        sendBtn.disabled = false;
        panel.classList.add('is-hidden');
        status.appendChild(h('span', { class: 'ok', text: 'Request #C-' + String(t.id).padStart(4, '0') + ' sent to ' + ((t.assignee && t.assignee.name) || 'the triage queue') + '.' }));
        status.appendChild(h('button', { type: 'button', class: 'msgs-link', text: 'Open thread', onclick: function () { openThreadFromNotice(t.id); } }));
        toast('Clarification request opened.');
        loadNotifications();
      }).catch(function (err) {
        sendBtn.disabled = false;
        status.appendChild(h('span', { class: 'err', text: err.message }));
      });
    });

    return wrap;
  }

  function buildFeedback(r) {
    var box = h('div', { class: 'feedback' }, [h('span', { class: 'fb-label', text: 'Was this helpful?' })]);
    function make(kind) {
      var b = h('button', { type: 'button', class: 'fb-btn', dataset: { fb: kind }, html: icon(kind === 'up' ? 'check' : 'close') + '<span>' + (kind === 'up' ? 'Yes' : 'No') + '</span>' });
      b.addEventListener('click', function () {
        qaa('.fb-btn').forEach(function (x) { if (x !== b) x.classList.remove('is-on'); });
        b.classList.add('is-on');
        toast('Thanks — your feedback is on record.');
      });
      return b;
    }
    box.appendChild(make('up'));
    box.appendChild(make('down'));
    return box;
  }

  function userName(id) {
    for (var i = 0; i < state.users.length; i++) if (state.users[i].id === id) return state.users[i].full_name;
    return '';
  }

  /* ---------------------------------------------------------------- messages
     Week 7 internal messaging. A thread is one clarification_request: the
     employee who asked is the requester, the policy owner is the assignee, the
     originating question is the linked assistant message and replies live in
     clarification_replies. Every call carries the bearer token minted for the
     selected persona, so the server -- never the browser -- decides who is
     acting and which threads are visible.
     ---------------------------------------------------------------------- */
  var ESCALATION = {
    open: { label: 'Open', cls: 'stamp-open' },
    triage: { label: 'Open · Unassigned', cls: 'stamp-triage' },
    awaiting_owner: { label: 'Awaiting Owner', cls: 'stamp-awaiting_owner' },
    awaiting_employee: { label: 'Awaiting Employee', cls: 'stamp-awaiting_employee' },
    resolved: { label: 'Resolved', cls: 'stamp-resolved' },
    closed: { label: 'Closed', cls: 'stamp-closed' }
  };
  var FOLDER_LABELS = {
    inbox: 'Inbox',
    requests: 'My requests',
    triage: 'Triage queue',
    resolved: 'Resolved',
    all: 'All threads'
  };
  var FOLDER_ORDER = ['inbox', 'requests', 'triage', 'resolved', 'all'];

  function escalationMeta(key) {
    return ESCALATION[key] || { label: String(key || '—'), cls: 'stamp-draft' };
  }

  function escalationStamp(key) {
    var meta = escalationMeta(key);
    return h('span', { class: 'stamp ' + meta.cls, html: '<span class="dot"></span>' + escText(meta.label) });
  }

  function snippet(text, max) {
    var body = String(text || '').replace(/\s+/g, ' ').trim();
    var limit = max || 96;
    return body.length > limit ? body.slice(0, limit).trim() + '\u2026' : body;
  }

  function myId() {
    return state.me ? state.me.id : state.personaId;
  }

  function threadQuestion(t) {
    return t.question || t.reason || 'Policy clarification request.';
  }

  function threadSubject(t) {
    return t.subject || (t.policy && t.policy.title) || 'Policy clarification';
  }

  function counterpart(t) {
    if (!t.requester) return { id: null, name: 'Employee' };
    if (t.requester.id === myId()) return t.assignee || { id: null, name: 'Unassigned' };
    return t.requester;
  }

  function fmtWhen(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' \u00b7 ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }

  function threadLabel(t) {
    return 'Thread #C-' + String(t.id).padStart(4, '0');
  }

  function msgsErrBlock(mark, message) {
    return h('div', { class: 'msgs-empty card' }, [
      h('div', { class: 'mark', text: mark }),
      h('div', { class: 'ok', text: message })
    ]);
  }

  function renderMessages(app) {
    var view = h('div', { class: 'view msgs-view' });
    var listRequest = 0;
    var detailRequest = 0;
    var pageSize = 25;

    // Header: title plus a single scoped search field.
    var head = h('div', { class: 'msgs-head' });
    var copy = h('div', { class: 'msgs-head-copy' });
    copy.appendChild(h('h1', { class: 'view-title', text: 'Messages' }));
    copy.appendChild(h('p', { class: 'view-sub', text: isAdmin()
      ? 'Organisation-wide correspondence and policy clarification oversight.'
      : 'Your policy questions, replies and decisions, together.' }));
    head.appendChild(copy);

    var search = h('div', { class: 'msgs-search' }, [
      h('span', { class: 'msgs-search-ic', html: icon('search') }),
      h('input', { type: 'search', maxlength: '100', placeholder: 'Search conversations', 'aria-label': 'Search conversations' })
    ]);
    var searchInput = search.querySelector('input');
    searchInput.value = state.inbox.q || '';
    head.appendChild(search);
    var refresh = h('button', { type: 'button', class: 'btn btn-ghost msgs-refresh', text: 'Refresh', 'aria-label': 'Refresh mailbox' });
    refresh.addEventListener('click', function () {
      refresh.disabled = true;
      loadList().finally(function () { refresh.disabled = false; });
      if (state.inbox.threadId) openThread(state.inbox.threadId, false);
    });
    head.appendChild(refresh);
    view.appendChild(head);

    var shell = h('div', { class: 'msgs-shell' });
    var foldersEl = h('nav', { class: 'msgs-folders', 'aria-label': 'Mail folders' });
    var listEl = h('section', { class: 'msgs-list', 'aria-label': 'Conversations' });
    var detailEl = h('section', { class: 'msgs-detail', 'aria-label': 'Conversation detail' });
    shell.appendChild(foldersEl);
    shell.appendChild(listEl);
    shell.appendChild(detailEl);
    view.appendChild(shell);
    app.appendChild(view);

    var debounce = null;
    searchInput.addEventListener('input', function () {
      if (debounce) clearTimeout(debounce);
      debounce = setTimeout(function () {
        state.inbox.q = searchInput.value.trim();
        state.inbox.offset = 0;
        loadList();
      }, 220);
    });

    renderFolders();
    listEl.appendChild(skeletonList());
    detailEl.appendChild(placeholder());

    // Deep link: #messages/<id> opens that thread directly (shareable URL).
    var deep = /^#messages\/(\d+)$/.exec(location.hash || '');
    if (deep) state.inbox.threadId = parseInt(deep[1], 10);

    loadList();
    if (state.inbox.threadId) openThread(state.inbox.threadId, false);

    /* --- folder rail --------------------------------------------------- */
    function renderFolders() {
      var data = state.inbox.data;
      foldersEl.innerHTML = '';
      foldersEl.appendChild(h('span', { class: 'msgs-rail-title', text: 'Mailbox' }));

      var folders = data
        ? data.folders
        : FOLDER_ORDER.filter(function (id) { return isAdmin() || (id !== 'triage' && id !== 'all'); })
          .map(function (id) { return { id: id, label: FOLDER_LABELS[id], count: null, unread: 0 }; });

      folders.forEach(function (f) {
        var btn = h('button', {
          type: 'button',
          class: 'msgs-folder' + (state.inbox.folder === f.id ? ' is-current' : ''),
          'aria-current': state.inbox.folder === f.id ? 'true' : null
        }, [
          h('span', { class: 'msgs-folder-name', text: f.label || FOLDER_LABELS[f.id] || f.id }),
          h('span', { class: 'msgs-folder-count', text: (f.count === null || f.count === undefined) ? '\u2014' : String(f.count) }),
          f.unread ? h('span', { class: 'msgs-folder-unread', text: String(f.unread) }) : null
        ]);
        btn.addEventListener('click', function () {
          if (state.inbox.folder === f.id) return;
          state.inbox.folder = f.id;
          state.inbox.offset = 0;
          state.inbox.threadId = null;
          history.replaceState(null, '', '#messages');
          render();
        });
        foldersEl.appendChild(btn);
      });

      var adminView = state.me && state.me.role === 'System Administrator';
      foldersEl.appendChild(h('div', { class: 'msgs-rail-note' }, [
        h('span', { class: 'k', text: 'Privacy' }),
        h('span', { class: 'v', text: adminView
          ? 'Organisation-wide oversight, scoped to your administrator role.'
          : 'Only threads you asked, own, or replied to are listed.' })
      ]));
    }

    /* --- conversation list --------------------------------------------- */
    function skeletonList() {
      var wrap = h('div', { class: 'msgs-skel' });
      for (var i = 0; i < 4; i++) wrap.appendChild(h('div', { class: 'skel', style: 'height:74px;border-radius:16px;margin-bottom:10px' }));
      return wrap;
    }

    function loadList() {
      var requestId = ++listRequest;
      var qs = '?folder=' + encodeURIComponent(state.inbox.folder);
      qs += '&limit=' + (pageSize + 1) + '&offset=' + state.inbox.offset;
      if (state.inbox.q) qs += '&q=' + encodeURIComponent(state.inbox.q);
      if (state.inbox.status) qs += '&status=' + encodeURIComponent(state.inbox.status);
      listEl.setAttribute('aria-busy', 'true');
      return api('/messages' + qs).then(function (data) {
        if (!view.isConnected || requestId !== listRequest) return;
        data.hasMore = data.threads.length > pageSize;
        data.threads = data.threads.slice(0, pageSize);
        state.inbox.data = data;
        renderFolders();
        renderList(data);
        loadNotifications();
      }).catch(function (err) {
        if (!view.isConnected || requestId !== listRequest) return;
        listEl.innerHTML = '';
        listEl.appendChild(msgsErrBlock('Messages unavailable', err.message));
        var retry = h('button', { type: 'button', class: 'btn btn-ghost', text: 'Try again' });
        retry.addEventListener('click', loadList);
        listEl.appendChild(retry);
      }).finally(function () {
        if (requestId === listRequest) listEl.removeAttribute('aria-busy');
      });
    }

    function renderList(data) {
      listEl.innerHTML = '';

      // Escalation filter row: the five product states on top of the DB state.
      var filters = h('div', { class: 'msgs-filters' });
      filters.appendChild(h('h2', { class: 'msgs-folder-heading', text: FOLDER_LABELS[state.inbox.folder] || 'Inbox' }));
      var statusSelect = h('select', { class: 'msgs-status-select', 'aria-label': 'Filter by escalation status' });
      var options = [['', 'All']].concat(Object.keys(ESCALATION).map(function (key) { return [key, ESCALATION[key].label]; }));
      options.forEach(function (pair) {
        statusSelect.appendChild(h('option', { value: pair[0], text: pair[0] ? pair[1] : 'All statuses', selected: (state.inbox.status || '') === pair[0] }));
      });
      statusSelect.addEventListener('change', function () {
        state.inbox.status = statusSelect.value;
        state.inbox.offset = 0;
        loadList();
      });
      filters.appendChild(statusSelect);
      listEl.appendChild(filters);

      listEl.appendChild(h('div', { class: 'msgs-list-meta' }, [
        h('span', { class: 'n', role: 'status', text: (state.inbox.offset ? (state.inbox.offset + 1) + '–' + (state.inbox.offset + data.threads.length) : String(data.threads.length)) + (data.threads.length === 1 ? ' conversation' : ' conversations') }),
        state.inbox.q ? h('span', { class: 'q', text: '\u201c' + state.inbox.q + '\u201d' }) : null
      ]));

      if (!data.threads.length) {
        listEl.appendChild(msgsErrBlock(
          state.inbox.q ? 'No matches' : 'Nothing here yet',
          state.inbox.q
            ? 'No conversation in this folder matched that search.'
            : 'When DeRexi opens a clarification for you, it appears here.'
        ));
        return;
      }

      var rows = h('div', { class: 'msgs-rows' });
      data.threads.forEach(function (t) { rows.appendChild(threadRow(t)); });
      listEl.appendChild(rows);
      if (state.inbox.offset || data.hasMore) {
        var pager = h('div', { class: 'msgs-pagination', 'aria-label': 'Mailbox pages' });
        [['Previous', -pageSize, !state.inbox.offset], ['Next', pageSize, !data.hasMore]].forEach(function (p) {
          var button = h('button', { type: 'button', class: 'btn btn-ghost', text: p[0], disabled: p[2] });
          button.addEventListener('click', function () { state.inbox.offset += p[1]; loadList(); });
          pager.appendChild(button);
        });
        listEl.appendChild(pager);
      }
    }

    function threadRow(t) {
      var peer = counterpart(t);
      var unread = Number(t.unread_count || 0) > 0;
      var row = h('button', {
        type: 'button',
        class: 'msgs-row' + (unread ? ' is-unread' : '') + (state.inbox.threadId === t.id ? ' is-active' : ''),
        dataset: { thread: String(t.id) },
        'aria-current': state.inbox.threadId === t.id ? 'true' : null,
        'aria-label': 'Open conversation: ' + threadSubject(t)
      }, [
        h('span', { class: 'msgs-row-avatar', text: initials(peer.name) }),
        h('span', { class: 'msgs-row-main' }, [
          h('span', { class: 'msgs-row-top' }, [
            h('span', { class: 'msgs-row-peer', text: peer.name }),
            h('span', { class: 'msgs-row-time', text: timeAgo(t.updated_at || t.created_at) })
          ]),
          h('span', { class: 'msgs-row-subject', text: threadQuestion(t) }),
          h('span', { class: 'msgs-row-snippet', text: snippet(t.last_reply ? t.last_reply.body : threadQuestion(t), 112) }),
          h('span', { class: 'msgs-row-stamps' }, [
            escalationStamp(t.escalation_status),
            t.is_triage ? h('span', { class: 'msgs-chip is-alert', text: 'Triage' }) : null,
            t.policy ? h('span', { class: 'msgs-chip', text: 'Policy #' + t.policy.id }) : null
          ])
        ]),
        unread ? h('span', { class: 'msgs-unread-dot', 'aria-label': 'Unread messages' }) : null
      ]);
      row.addEventListener('click', function () { openThread(t.id, true); });
      return row;
    }

    /* --- detail pane ---------------------------------------------------- */
    function placeholder() {
      return h('div', { class: 'msgs-placeholder' }, [
        h('span', { class: 'seal', html: icon('seal') }),
        h('div', { class: 'mark', text: 'Select a conversation' }),
        h('div', { class: 'ok', text: 'The full thread, the policy that raised it, and the owner to contact appear here.' })
      ]);
    }

    function openThread(id, selectRow) {
      var requestId = ++detailRequest;
      state.inbox.threadId = id;
      if (location.hash !== '#messages/' + id) history[selectRow ? 'pushState' : 'replaceState'](null, '', '#messages/' + id);
      if (selectRow) {
        var rows = listEl.querySelectorAll('.msgs-row');
        for (var i = 0; i < rows.length; i++) {
          rows[i].classList.toggle('is-active', rows[i].dataset.thread === String(id));
          rows[i].setAttribute('aria-current', rows[i].dataset.thread === String(id) ? 'true' : 'false');
        }
      }
      shell.classList.add('is-thread');
      detailEl.innerHTML = '';
      detailEl.appendChild(h('div', { class: 'msgs-placeholder' }, [h('div', { class: 'skel', style: 'height:320px;border-radius:18px' })]));

      // Reading the thread clears its unread watermark server-side first, so the
      // detail payload and the badge cannot disagree.
      api('/clarifications/' + id + '/read', { method: 'POST', body: JSON.stringify({}) })
        .catch(function () { /* a read failure must not hide the thread */ })
        .then(function () { return api('/clarifications/' + id); })
        .then(function (t) {
          if (!view.isConnected || requestId !== detailRequest) return;
          renderDetail(t);
          loadList();
          loadNotifications();
        })
        .catch(function (err) {
          if (!view.isConnected || requestId !== detailRequest) return;
          detailEl.innerHTML = '';
          detailEl.appendChild(backButton());
          detailEl.appendChild(msgsErrBlock('Thread unavailable', err.message));
        });
    }

    function backButton() {
      return h('button', { type: 'button', class: 'msgs-back', text: 'Back to conversations', onclick: function () {
        detailRequest++;
        state.inbox.threadId = null;
        history.pushState(null, '', '#messages');
        shell.classList.remove('is-thread');
        detailEl.replaceChildren(placeholder());
        var row = listEl.querySelector('.msgs-row.is-active');
        if (row) row.focus();
      } });
    }

    function contactCard(label, person, note) {
      var card = h('div', { class: 'msgs-contact' });
      card.appendChild(h('span', { class: 'k', text: label }));
      if (!person) {
        card.appendChild(h('span', { class: 'v', text: 'Unassigned' }));
        if (note) card.appendChild(h('span', { class: 'meta', text: note }));
        return card;
      }
      card.appendChild(h('span', { class: 'v', text: person.name }));
      var meta = [person.role, person.department].filter(Boolean).join(' \u00b7 ');
      if (meta) card.appendChild(h('span', { class: 'meta', text: meta }));
      card.appendChild(h('span', { class: 'email', text: person.email || 'Directory email restricted' }));
      return card;
    }

    function streamMsg(m) {
      var avatar = m.mine
        ? h('span', { class: 'msg-avatar avatar-user', text: initials(m.sender) })
        : h('span', { class: 'msg-avatar avatar-peer', text: initials(m.sender) });
      var meta = m.sender + (m.role ? ' \u00b7 ' + m.role : '') + ' \u00b7 ' + fmtWhen(m.at);
      return h('div', { class: 'msg' + (m.mine ? ' msg-user' : '') }, [
        avatar,
        h('div', { class: 'msg-col' }, [
          h('div', { class: 'msg-body', text: m.body }),
          h('div', { class: 'msg-meta', text: meta })
        ])
      ]);
    }

    function renderDetail(t) {
      detailEl.innerHTML = '';
      detailEl.appendChild(backButton());
      var perms = t.permissions || {};

      // Heading: thread identity, escalation state, originating question.
      var head = h('div', { class: 'msgs-detail-head' });
      var top = h('div', { class: 'msgs-detail-top' }, [
        h('div', { class: 'msgs-detail-titles' }, [
          h('span', { class: 'msgs-thread-id', text: threadLabel(t) }),
          h('h2', { class: 'msgs-detail-subject', text: threadSubject(t) })
        ]),
        escalationStamp(t.escalation_status)
      ]);
      head.appendChild(top);
      head.appendChild(h('p', { class: 'msgs-detail-question', text: threadQuestion(t) }));
      detailEl.appendChild(head);

      // Workflow actions, driven by server-computed permissions.
      var actions = h('div', { class: 'msgs-actions' });
      if (perms.can_resolve) {
        actions.appendChild(actionButton('Resolve thread', function () { threadAction(t.id, 'resolve', 'Thread resolved.'); }));
      }
      if (perms.can_close) {
        actions.appendChild(actionButton('Close thread', function () { threadAction(t.id, 'close', 'Thread closed.'); }));
      }
      if (perms.can_reopen) {
        actions.appendChild(actionButton('Reopen thread', function () { threadAction(t.id, 'reopen', 'Thread reopened.', { reason: 'Reopened from the inbox.' }); }));
      }
      if (perms.can_assign) actions.appendChild(assignControl(t));
      if (actions.childNodes.length) detailEl.appendChild(actions);

      // Participants: requester and the responsible policy owner.
      var contacts = h('div', { class: 'msgs-contacts' }, [
        contactCard('Requester', t.requester),
        contactCard('Policy owner', t.assignee, t.is_triage ? 'No owner on the policy — held in the administrator triage queue.' : '')
      ]);
      detailEl.appendChild(contacts);

      // A compact policy strip stays above the conversation; the full evidence
      // (citation excerpts and the assistant's answer) follows the thread.
      if (t.policy) {
        detailEl.appendChild(h('div', { class: 'msgs-policybar' }, [
          h('span', { class: 'k', text: 'Policy #' + t.policy.id }),
          h('span', { class: 'v', text: t.policy.title }),
          h('button', { type: 'button', class: 'msgs-link', text: 'Open policy', onclick: function () { openDrawer(t.policy.id); } })
        ]));
      }

      var context = h('section', { class: 'msgs-context' });
      context.appendChild(h('div', { class: 'msgs-section-head' }, [
        h('h3', { text: 'Contextual policy' }),
        t.policy ? h('button', { type: 'button', class: 'msgs-link', text: 'Open policy', onclick: function () { openDrawer(t.policy.id); } }) : null
      ]));
      if (t.policy) {
        context.appendChild(h('div', { class: 'msgs-context-card' }, [
          h('span', { class: 'k', text: 'Policy reference' }),
          h('span', { class: 'v', text: t.policy.title }),
          h('span', { class: 'meta', text: 'Policy #' + t.policy.id })
        ]));
      } else {
        context.appendChild(h('p', { class: 'msgs-muted', text: 'No policy is linked to this thread; it is held in triage.' }));
      }
      if (t.citations && t.citations.length) {
        t.citations.slice(0, 2).forEach(function (c) {
          context.appendChild(h('div', { class: 'msgs-citation' }, [
            h('span', { class: 'ct', text: (c.title || 'Cited policy') + (c.version_no ? ' \u00b7 v' + c.version_no : '') }),
            h('span', { class: 'cx', text: snippet(c.excerpt || '', 220) })
          ]));
        });
      }
      if (t.answer) {
        context.appendChild(h('div', { class: 'msgs-answer' }, [
          h('span', { class: 'k', text: 'Policy Assistant answered' }),
          h('div', { class: 'v', text: t.answer })
        ]));
      }

      // The conversation itself: question first, then every stored reply.
      var convo = h('section', { class: 'msgs-convo' });
      convo.appendChild(h('div', { class: 'msgs-section-head' }, [
        h('h3', { text: 'Conversation' }),
        h('span', { class: 'meta', text: (1 + (t.replies || []).length) + ((1 + (t.replies || []).length) === 1 ? ' message' : ' messages') })
      ]));
      var stream = h('div', { class: 'msgs-stream' });
      stream.appendChild(streamMsg({
        sender: t.requester ? t.requester.name : 'Employee',
        mine: !!(t.requester && t.requester.id === myId()),
        body: threadQuestion(t),
        at: t.created_at,
        role: t.requester ? t.requester.role : ''
      }));
      (t.replies || []).forEach(function (r) {
        stream.appendChild(streamMsg({ sender: r.sender, mine: r.mine, body: r.body, at: r.created_at, role: r.sender_role }));
      });
      convo.appendChild(stream);
      detailEl.appendChild(convo);

      // Reply box only while the thread is live.
      if (perms.can_reply) {
        detailEl.appendChild(composer(t));
      } else {
        detailEl.appendChild(h('div', { class: 'msgs-locked' }, [
          h('span', { class: 'k', text: t.status === 'closed' ? 'Thread closed' : t.status === 'resolved' ? 'Thread resolved' : 'Read-only history' }),
          h('span', { class: 'v', text: perms.can_reopen
            ? 'Reopen the thread to continue the conversation.'
            : (t.status === 'closed' || t.status === 'resolved') ? 'Only the requester or an administrator can reopen it.' : 'Replies are available to the requester, current assignee and administrators.' })
        ]));
      }

      detailEl.appendChild(context);
    }

    function actionButton(label, handler) {
      var btn = h('button', { type: 'button', class: 'btn btn-ghost', text: label });
      btn.addEventListener('click', handler);
      return btn;
    }

    function assignControl(t) {
      var wrap = h('div', { class: 'msgs-assign' });
      var sel = h('select', { class: 'msgs-assign-select', 'aria-label': 'Assign to a policy owner' });
      sel.appendChild(h('option', { value: '', text: 'Assign to…' }));
      state.users
        .filter(function (u) { return u.role === 'Policy Owner' || u.role === 'System Administrator'; })
        .forEach(function (u) {
          sel.appendChild(h('option', {
            value: String(u.id),
            text: u.full_name + ' \u00b7 ' + titleRole(u.role),
            selected: !!(t.assignee && t.assignee.id === u.id)
          }));
        });
      var btn = h('button', { type: 'button', class: 'btn btn-ghost', text: 'Assign' });
      btn.addEventListener('click', function () {
        var target = parseInt(sel.value, 10);
        if (!target) { toast('Choose a policy owner first.'); return; }
        btn.disabled = true;
        api('/clarifications/' + t.id + '/assign', { method: 'POST', body: JSON.stringify({ assignee_id: target }) })
          .then(function () {
            toast('Thread reassigned.');
            openThread(t.id, false);
            loadList();
          })
          .catch(function (err) {
            btn.disabled = false;
            toast('Could not reassign (' + err.message + ')');
          });
      });
      wrap.appendChild(sel);
      wrap.appendChild(btn);
      return wrap;
    }

    function threadAction(id, action, message, payload) {
      api('/clarifications/' + id + '/' + action, {
        method: 'POST',
        body: JSON.stringify(payload || {})
      }).then(function () {
        toast(message);
        openThread(id, false);
        loadList();
      }).catch(function (err) {
        toast('Could not update the thread (' + err.message + ')');
      });
    }

    function composer(t) {
      var wrap = h('div', { class: 'msgs-composer' });
      var ta = h('textarea', { rows: '3', maxlength: '4000', placeholder: 'Reply to ' + counterpart(t).name + '\u2026', 'aria-label': 'Your reply' });
      ta.value = state.inbox.drafts[t.id] || '';
      ta.addEventListener('input', function () { state.inbox.drafts[t.id] = ta.value; });
      var send = h('button', { type: 'button', class: 'send-btn', html: icon('send') + '<span>Send reply</span>' });
      send.setAttribute('aria-label', 'Send reply');

      function submit() {
        if (send.disabled) return;
        var body = ta.value.trim();
        if (!body) { toast('Write a reply first.'); return; }
        send.disabled = true;
        api('/clarifications/' + t.id + '/replies', {
          method: 'POST',
          body: JSON.stringify({ body: body })
        }).then(function () {
          toast('Reply sent.');
          ta.value = '';
          delete state.inbox.drafts[t.id];
          openThread(t.id, false);
          loadList();
        }).catch(function (err) {
          send.disabled = false;
          toast('Could not send reply (' + err.message + ')');
        });
      }

      send.addEventListener('click', submit);
      ta.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); submit(); }
      });

      wrap.appendChild(ta);
      wrap.appendChild(h('div', { class: 'msgs-composer-foot' }, [
        h('span', { class: 'msgs-hint', text: '\u2318 / Ctrl + Enter to send' }),
        send
      ]));
      return wrap;
    }
  }

  /* ---------------------------------------------------------------- library */
  function renderLibrary(app) {
    var view = h('div', { class: 'view' });

    var head = h('div', { class: 'view-head' });
    head.appendChild(h('p', { class: 'view-kicker', text: 'Policy Library' }));
    head.appendChild(h('h1', { class: 'view-title', html: 'The governing <em>ledger</em>' }));
    head.appendChild(h('p', { class: 'view-sub', text: 'Every policy that runs Aurum Capital Bank, tracked by version and next review date. Select a row for the full text and version history.' }));

    var layout = h('div', { class: 'lib-layout' });
    var catNav = h('nav', { class: 'cat-nav', 'aria-label': 'Policy categories' });
    var right = h('div', null);

    loadCats().then(function (cats) {
      var total = 0;
      cats.forEach(function (c) { total += c.count || 0; });
      catNav.appendChild(catButton('All policies', null, true, total));
      cats.forEach(function (c) {
        catNav.appendChild(catButton(c.name, c.id, false, c.count));
      });
      if (!state.cats) state.cats = cats;
    });

    var searchBar = h('div', { class: 'searchbar' }, [
      h('span', { html: icon('search') }),
      h('input', { type: 'search', placeholder: 'Search policies by title or keyword', value: '', 'aria-label': 'Search policies' })
    ]);
    var inputEl = searchBar.querySelector('input');

    var cache = {};
    api('/policies').then(function (ps) {
      ps.forEach(function (p) { cache[p.id] = p; });
    });

    var metaRow = h('div', { class: 'result-meta' }, [
      h('span', { class: 'n', text: '0 policies' }),
      h('span', { class: 'stamp stamp-approved js-status-line', text: 'Live register' })
    ]);
    var ledger = h('div', { class: 'ledger' }, [
      h('div', { class: 'ledger-head' }, [
        h('span', { text: 'Policy' }),
        h('span', { text: 'Category' }),
        h('span', { text: 'Version' }),
        h('span', { text: 'ID' })
      ])
    ]);

    right.appendChild(searchBar);
    right.appendChild(metaRow);
    right.appendChild(ledger);

    layout.appendChild(catNav);
    layout.appendChild(right);
    view.appendChild(head);
    view.appendChild(layout);
    app.appendChild(view);

    var active = { cat: null, term: '' };

    inputEl.addEventListener('input', function () {
      active.term = inputEl.value.trim();
      loadRows();
    });

    function catButton(label, id, cur, count) {
      var b = h('button', { type: 'button', class: 'cat-btn' + (cur ? ' is-current' : ''), dataset: { cat: id === null ? 'all' : id } }, [
        h('span', { text: label }),
        h('span', { class: 'cnt', text: String(count || 0) })
      ]);
      b.addEventListener('click', function () {
        qaa('.cat-btn').forEach(function (x) { x.classList.remove('is-current'); });
        b.classList.add('is-current');
        active.cat = id;
        loadRows();
      });
      return b;
    }

    function loadRows() {
      var p = active.term ? api('/policies/search?q=' + encodeURIComponent(active.term)) : api('/policies');
      p.then(function (rows) {
        if (active.term) {
          var enriched = rows.map(function (r) {
            var full = cache[r.policy_id];
            if (full) {
              var merged = {};
              for (var k in full) merged[k] = full[k];
              merged.policy_id = r.policy_id;
              merged.score = r.score;
              merged.excerpt = r.excerpt;
              return merged;
            }
            return r;
          });
          renderFrom(enriched);
        } else {
          renderFrom(rows.filter(function (r) { return active.cat === null || r.category_id === active.cat; }));
        }
      }).catch(function (err) {
        ledger.innerHTML = '';
        ledger.appendChild(h('div', { class: 'empty' }, [
          h('div', { class: 'mark', text: 'No ledger' }),
          h('div', { class: 'ok', text: 'Could not reach the policy engine (' + err.message + ').' })
        ]));
      });
    }

    function renderFrom(rows) {
      metaRow.querySelector('.n').textContent = rows.length + ' polic' + (rows.length === 1 ? 'y' : 'ies');
      ledger.innerHTML = '';
      ledger.appendChild(h('div', { class: 'ledger-head' }, [
        h('span', { text: 'Policy' }), h('span', { text: 'Category' }), h('span', { text: 'Version' }), h('span', { text: 'ID' })
      ]));
      if (!rows.length) {
        ledger.appendChild(h('div', { class: 'empty' }, [
          h('div', { class: 'mark', text: 'Nothing filed' }),
          h('div', { class: 'ok', text: 'No policy matches that search. Try a term like “phishing”, “leave”, or “disclosure”.' })
        ]));
        return;
      }
      rows.forEach(function (p) {
        ledger.appendChild(buildRow(p));
      });
    }

    function buildRow(p) {
      var pid = p.id !== undefined ? p.id : p.policy_id;
      var foot = h('div', { class: 'l-foot' }, [
        h('span', { class: 'stamp ' + stampCls(p.status || 'approved'), html: '<span class="dot"></span>' + escText((p.status || 'approved').replace(/_/g, ' ')) }),
        h('span', { class: 'l-rev', text: p.requires_review ? 'Review ' + fmtDate(p.review_date) : 'Next review ' + fmtDate(p.review_date) }),
        h('span', { class: 'l-own', text: p.owner || '' })
      ]);
      var titleCol = h('div', { class: 'l-first' }, [
        h('span', { class: 'l-title', text: p.title }),
        foot
      ]);
      var row = h('div', { class: 'ledger-row', tabindex: '0', 'aria-label': p.title + '. Open details.' }, [
        titleCol,
        h('span', { class: 'l-cat', text: p.category || '' }),
        h('span', { class: 'l-ver', text: p.latest_version || p.version_no || '' }),
        h('span', { class: 'l-id', text: 'P-' + String(pid).padStart(3, '0') })
      ]);
      row.addEventListener('click', function () { openDrawer(pid); });
      row.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openDrawer(pid); } });
      return row;
    }

    loadRows();
  }

  function loadCats() {
    return api('/categories').then(function (cats) { return cats; }).catch(function () {
      return api('/policies').then(function (ps) {
        var seen = {};
        var out = [];
        ps.forEach(function (p) {
          var key = p.category_id + ':' + p.category;
          if (seen[key] === undefined) {
            seen[key] = out.length;
            out.push({ id: p.category_id, name: p.category, count: 0 });
          }
          out[seen[key]].count += 1;
        });
        return out;
      });
    });
  }

  function stampCls(status) {
    var map = {
      approved: 'stamp-approved',
      in_review: 'stamp-in_review',
      draft: 'stamp-draft',
      open: 'stamp-open',
      in_progress: 'stamp-in_progress',
      resolved: 'stamp-resolved',
      triaged: 'stamp-triaged',
      escalated: 'stamp-escalated',
      high: 'stamp-high',
      critical: 'stamp-critical'
    };
    return map[status] || 'stamp-resolved';
  }

  function escText(s) {
    var d = document.createElement('span');
    d.textContent = s;
    return d.innerHTML;
  }

  /* ---------------------------------------------------------------- drawer */
  function openDrawer(policyId) {
    api('/policies/' + policyId).then(function (p) {
      drawDrawer(p);
    }).catch(function (err) {
      toast('Could not open policy (' + err.message + ')');
    });
  }

  function drawDrawer(p) {
    var backdrop = h('div', { class: 'backdrop' });
    var drawer = h('div', { class: 'drawer', role: 'dialog', 'aria-modal': 'true', 'aria-label': p.title });
    var hide = function () {
      backdrop.remove();
      drawer.remove();
      document.body.style.overflow = '';
    };

    backdrop.addEventListener('click', hide);

    var head = h('div', { class: 'drawer-head' }, [
      h('div', null, [
        h('div', { class: 'k', text: 'Policy ' + String(p.id).padStart(3, '0') + ' · ' + p.category }),
        h('h3', { text: p.title })
      ]),
      h('button', { type: 'button', class: 'drawer-close', html: icon('close'), onclick: hide, 'aria-label': 'Close' })
    ]);

    var body = h('div', { class: 'drawer-body' });
    body.appendChild(h('div', { class: 'dmeta' }, [
      metaRow('Status', stampCls(p.status), p.status.replace(/_/g, ' ')),
      metaRow('Version', '', p.latest_version),
      metaRow('Owner', '', p.owner),
      metaRow('Last updated', '', fmtDate(p.updated_at)),
      metaRow('Next review', '', p.requires_review ? 'Due ' + fmtDate(p.review_date) : fmtDate(p.review_date))
    ]));
    var latest = (p.versions || []).slice().sort(function (a, b) { return (b.version_no || '0').localeCompare(a.version_no || '0'); })[0] || {};
    body.appendChild(h('div', { class: 'dbody', text: latest.body || p.summary || 'Full text is shown in the live register.' }));

    var vl = h('div', { class: 'version-list' });
    (p.versions || []).forEach(function (ver) {
      vl.appendChild(h('div', { class: 'version-row' }, [
        h('div', { class: 'version-top' }, [
          h('span', { class: 'version-no', text: 'v' + ver.version_no }),
          h('span', { class: 'version-date', text: 'Effective ' + fmtDate(ver.effective_date) + ' · Review ' + fmtDate(ver.review_date) }),
          ver.requires_review ? h('span', { class: 'stamp stamp-needs', html: '<span class="dot"></span>review due' }) : null
        ]),
        h('div', { class: 'excerpt', text: (ver.body || '').slice(0, 180) + ((ver.body || '').length > 180 ? '…' : '') })
      ]));
    });
    body.appendChild(vl);

    drawer.appendChild(head);
    drawer.appendChild(body);
    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);
    document.body.style.overflow = 'hidden';
  }

  function metaRow(k, cls, v) {
    return h('div', { class: 'dmeta-row' }, [
      h('span', { class: 'k', text: k }),
      cls ? h('span', { class: 'stamp ' + cls, html: '<span class="dot"></span>' + escText(v) }) : h('span', { class: 'v', text: v })
    ]);
  }

  /* ---------------------------------------------------------------- governance */
  function renderGovernance(app) {
    var view = h('div', { class: 'view' });

    var head = h('div', { class: 'view-head' });
    head.appendChild(h('p', { class: 'view-kicker', text: 'Governance Board' }));
    head.appendChild(h('h1', { class: 'view-title', html: 'Health of the <em>house</em>' }));
    head.appendChild(h('p', { class: 'view-sub', text: 'A glance at how policies, clarifications, and incidents are holding up across Aurum Capital Bank.' }));

    var tabs = h('div', { class: 'tabs', role: 'tablist' }, [
      tab('Overview', 'overview'),
      tab('Clarifications', 'clar'),
      tab('Incidents', 'inc')
    ]);
    var panel = h('div', { class: 'gov-panel' });
    panel.appendChild(skelPanel());

    view.appendChild(head);
    view.appendChild(tabs);
    view.appendChild(panel);
    app.appendChild(view);
    go('overview');

    function tab(label, key) {
      var t = h('button', { type: 'button', class: 'tab', role: 'tab', dataset: { tab: key }, text: label });
      t.addEventListener('click', function () { go(key); });
      return t;
    }

    function setCurrent(key) {
      qaa('.tab').forEach(function (t) { t.classList.toggle('is-current', t.dataset.tab === key); });
    }

    function go(key) {
      setCurrent(key);
      panel.innerHTML = '';
      panel.appendChild(skelPanel());
      if (key === 'clar') return loadClar();
      if (key === 'inc') return loadInc();
      return loadOverview();
    }

    function skelPanel() {
      var s = h('div', { class: 'skel', style: 'height:260px;border-radius:16px;opacity:.7' });
      return s;
    }

    function loadOverview() {
      api('/dashboard/policy-health').then(function (d) {
        panel.innerHTML = '';
        var o = buildOverview(d);
        o.forEach(function (n) { panel.appendChild(n); });
      }).catch(function (err) {
        panel.innerHTML = '';
        panel.appendChild(errEl(err));
      });
    }

    function loadClar() {
      Promise.all([api('/clarifications'), api('/policies')]).then(function (r) {
        panel.innerHTML = '';
        panel.appendChild(buildClarQueue(r[0], r[1]));
      }).catch(function (err) {
        panel.innerHTML = '';
        panel.appendChild(errEl(err));
      });
    }

    function loadInc() {
      Promise.all([api('/incidents'), api('/incident-categories')]).then(function (r) {
        panel.innerHTML = '';
        panel.appendChild(buildIncidents(r[0]));
      }).catch(function (err) {
        panel.innerHTML = '';
        panel.appendChild(errEl(err));
      });
    }

    function errEl(err) {
      return h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'The register is unreachable' }),
        h('div', { class: 'ok', text: err.message })
      ]);
    }
  }

  function buildOverview(d) {
    var out = [];
    var nums = [
      { label: 'Policies', value: d.totals.policies, foot: statusLine(d.policies_by_status), pct: 100, hint: 'Approved' },
      { label: 'Conversations', value: d.totals.conversations, foot: 'Including ' + d.totals.messages + ' messages', pct: 100, hint: 'All-time' },
      { label: 'Reviews due', value: d.reviews_due, foot: 'Awaiting owner sign-off', pct: d.reviews_due > 0 ? 60 : 0, hint: 'Soon' },
      { label: 'Helpfulness', value: Math.round(d.feedback.helpful_rate * 100) + '%', foot: d.feedback.helpful + ' helpful · ' + d.feedback.not_helpful + ' not', pct: Math.round(d.feedback.helpful_rate * 100), hint: 'Feedback' }
    ];
    var grid = h('div', { class: 'kpi-grid' });
    nums.forEach(function (n) {
      grid.appendChild(h('div', { class: 'kpi' }, [
        h('span', { class: 'kpi-label', text: n.label }),
        h('div', { class: 'kpi-num', text: n.value }),
        h('div', { class: 'bar' }, [h('i', { style: 'width:' + n.pct + '%' })]),
        h('div', { class: 'kpi-foot', text: n.foot })
      ]));
    });
    out.push(grid);

    var pair = h('div', { class: 'gov-grid' });
    pair.appendChild(buildTopCited(d.top_cited_policies));
    pair.appendChild(buildQueueMini(d.clarifications_by_status, d.incidents_by_status, d.reviews_due));
    out.push(h('div', { class: 'section' }, [h('div', { class: 'section-head', style: 'margin-bottom:14px' }, [
      h('h2', { class: 'section-title', text: 'Health at a glance' }),
      h('span', { class: 'section-meta', text: 'Live register' })
    ]), pair]));

    return out;
  }

  function statusLine(rows) {
    var s = 'Approved';
    if (rows && rows.length) s = rows.map(function (r) { return r.status + ' ' + r.count; }).join(' · ');
    return s;
  }

  function buildTopCited(list) {
    var pane = h('div', { class: 'pane' });
    pane.appendChild(h('div', { class: 'pane-head' }, [
      h('h3', { text: 'Most-cited policies' }),
      h('span', { class: 'badge', text: 'Top 5' })
    ]));
    var body = h('div', { class: 'pane-body' });
    if (!list || !list.length) body.appendChild(h('div', { class: 'empty', 'data-void': '' }, [h('div', { class: 'ok', text: 'No citations on record yet.' })]));
    else {
      var max = list[0].citation_count;
      list.forEach(function (p) {
        body.appendChild(h('div', { class: 'tc-row' }, [
          h('div', null, [
            h('div', { class: 'tc-name', text: p.title }),
            h('div', { class: 'tc-track' }, [h('i', { style: 'width:' + Math.max(6, Math.round((p.citation_count / max) * 100)) + '%' })])
          ]),
          h('span', { class: 'tc-count', text: String(p.citation_count) })
        ]));
      });
    }
    pane.appendChild(body);
    return pane;
  }

  function buildQueueMini(csv, isv, reviewsDue) {
    var pane = h('div', { class: 'pane' });
    var openCount = 0;
    if (csv) csv.forEach(function (r) { if (r.status === 'open' || r.status === 'in_progress') openCount += r.count; });
    var incOpen = 0;
    if (isv) isv.forEach(function (r) { incOpen += r.count; });
    pane.appendChild(h('div', { class: 'pane-head' }, [
      h('h3', { text: 'Needs attention' }),
      h('span', { class: 'badge', text: String(openCount + incOpen) })
    ]));
    var body = h('div', { class: 'pane-body' });
    body.appendChild(kvi('Clarification requests', openCount, 'sent to policy owners'));
    body.appendChild(kvi('Incidents in flight', incOpen, 'triaged or escalated'));
    body.appendChild(kvi('Reviews due', reviewsDue || 0, 'versions past their review date'));
    pane.appendChild(body);
    return pane;
  }

  function kvi(label, count, sub) {
    return h('div', { class: 'queue-row' }, [
      h('span', { class: 'queue-who', text: String(count) }),
      h('div', { class: 'queue-info' }, [
        h('div', { class: 'queue-q', text: label }),
        h('div', { class: 'queue-meta', text: sub })
      ])
    ]);
  }

  function buildClarQueue(list, policies) {
    var titles = {};
    policies.forEach(function (p) { titles[p.id] = p.title; });
    var pane = h('div', { class: 'pane' });
    var open = list.filter(function (c) { return c.status !== 'resolved'; });
    pane.appendChild(h('div', { class: 'pane-head' }, [
      h('h3', { text: 'Clarification requests' }),
      h('span', { class: 'badge', text: String(open.length) + ' open' })
    ]));
    var body = h('div', { class: 'pane-body' });
    if (!open.length) {
      body.appendChild(h('div', { class: 'empty' }, [h('div', { class: 'ok', text: 'Nothing waiting. The queue is clear.' })]));
      pane.appendChild(body);
      return pane;
    }
    open.forEach(function (c) {
      var row = h('div', { class: 'queue-row' }, [
        h('span', { class: 'queue-who', text: initials(c.requester) }),
        h('div', { class: 'queue-info' }, [
          h('div', { class: 'queue-q', text: c.reason }),
          h('div', { class: 'queue-meta', text: c.requester + ' · ' + (titles[c.policy_id] || 'Policy ' + c.policy_id) + ' · ' + c.assignee })
        ]),
        h('span', { class: 'stamp ' + stampCls(c.status), html: '<span class="dot"></span>' + escText(c.status.replace(/_/g, ' ')) }),
        h('button', { type: 'button', class: 'queue-act', onclick: function () { resolveClar(c); }, text: c.status === 'in_progress' ? 'Resolve' : 'Take' })
      ]);
      body.appendChild(row);
    });
    pane.appendChild(body);
    return pane;
  }

  function resolveClar(c) {
    api('/clarifications/' + c.id + '/resolve', { method: 'POST', body: JSON.stringify({ id: c.id }) }).then(function () {
      toast('Request #' + c.id + ' marked resolved.');
      render();
    }).catch(function (err) {
      toast('Could not update request (' + err.message + ')');
    });
  }

  function buildIncidents(list) {
    var pane = h('div', { class: 'pane' });
    pane.appendChild(h('div', { class: 'pane-head' }, [
      h('h3', { text: 'Incident triage' }),
      h('span', { class: 'badge', text: String(list.length) })
    ]));
    var body = h('div', { class: 'pane-body' });
    if (!list.length) {
      body.appendChild(h('div', { class: 'empty' }, [h('div', { class: 'ok', text: 'No incidents on the books.' })]));
      pane.appendChild(body);
      return pane;
    }
    var rows = h('div', { class: 'inc-rows' });
    list.forEach(function (inc) {
      rows.appendChild(buildIncRow(inc));
    });
    body.appendChild(rows);
    pane.appendChild(body);
    return pane;
  }

  function buildIncRow(inc) {
    var acts = h('div', { class: 'inc-acts' });
    var note = h('button', { type: 'button', class: 'btn btn-ghost', onclick: function () { toast('Reassigned to ' + inc.assignee); }, text: 'Assign to ' + (inc.assignee.split(' ')[0] || '') });
    acts.appendChild(note);
    acts.appendChild(h('button', { type: 'button', class: 'btn btn-ghost', onclick: function () { toast('Escalated to the CISO desk.'); }, text: 'Escalate' }));

    return h('div', { class: 'inc-row' }, [
      h('div', { class: 'inc-top' }, [
        h('span', { class: 'id', text: '#I-' + String(inc.id).padStart(3, '0') }),
        h('span', { class: 'stamp ' + stampCls(inc.severity), html: '<span class="dot"></span>' + escText(inc.severity) }),
        h('span', { class: 'stamp ' + stampCls(inc.status), html: '<span class="dot"></span>' + escText(inc.status.replace(/_/g, ' ')) }),
        h('span', { class: 'queue-act', style: 'display:none', text: '' })
      ]),
      h('div', { class: 'inc-q', text: inc.category }),
      h('div', { class: 'inc-desc', text: inc.description }),
      h('div', { class: 'inc-meta' }, [
        h('span', { text: 'Lvl ' + inc.escalation_level }),
        h('span', { text: 'Reporter · ' + inc.reporter }),
        h('span', { text: 'SOC · ' + inc.assignee }),
        h('span', { text: fmtDate(inc.created_at) })
      ]),
      acts
    ]);
  }

  /* ---------------------------------------------------------------- pulse */
  // Pulse is its own view module (pulse.js) so this file stays focused on the
  // policy, message, and governance surfaces; the router only supplies the
  // mount point. Pulse is readable by every role, so no gating happens here.
  function renderPulse(app) {
    if (window.PulseView && typeof window.PulseView.render === 'function') {
      window.PulseView.render(app);
      return;
    }
    app.appendChild(h('div', { class: 'view' }, [
      h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'Pulse is unavailable' }),
        h('div', { class: 'ok', text: 'The Pulse module did not load. Reload the page to try again.' })
      ])
    ]));
  }

  /* ---------------------------------------------------------------- boot */
  document.addEventListener('DOMContentLoaded', function () {
    setRecon();
    wireChrome();
    startSession().catch(function (err) {
      var app = qa('#app');
      app.innerHTML = '';
      app.appendChild(h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'The register could not be opened' }),
        h('div', { class: 'ok', text: err.message })
      ]));
    });
  });

  /* Ask the server which sign-in path exists, obtain a session, then load the
     directory. The server decides everything: the browser never asserts a role. */
  function startSession() {
    return fetch('/auth/config', { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (cfg) {
        state.authConfig = cfg;
        state.devAuth = !!cfg.dev_auth;
        state.devUsers = cfg.identities || [];
        var recon = qa('.js-recon-mode');
        if (recon) recon.textContent = state.devAuth ? 'Local demonstration · verified test sessions' : 'Live register';
        if (!state.devAuth) { renderProductionGate(); return; }
        restorePersona();
        return refreshDevToken()
          .then(function () { return loadAll(); })
          .then(function () {
            buildPersonaSelect();
            refreshNav();
            render();
            return loadNotifications();
          })
          .then(function () {
            // ?notify=1 opens the notification drawer for screenshots/evidence.
            if (new URLSearchParams(location.search).get('notify') === '1') toggleNotify(true);
          });
      });
  }

  /* Production has no browser session yet: say so plainly instead of faking auth. */
  function renderProductionGate() {
    var app = qa('#app');
    app.classList.remove('is-hidden');
    app.innerHTML = '';
    app.appendChild(h('div', { class: 'view' }, [
      h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'Sign-in required' }),
        h('div', { class: 'ok', text: 'This deployment verifies Supabase sessions. Sign in through the identity provider to open the register.' })
      ])
    ]));
  }

  function wireChrome() {
    qaa('.btn-recon').forEach(function (b) { b.addEventListener('click', openGateForSwap); });

    var notifyBtn = qa('.js-notify');
    if (notifyBtn) notifyBtn.addEventListener('click', function (e) { e.stopPropagation(); toggleNotify(); });
    var notifyClose = qa('.js-notify-close');
    if (notifyClose) notifyClose.addEventListener('click', closeNotify);
    document.addEventListener('click', function (e) {
      var panel = qa('.js-notify-panel');
      if (!panel || panel.classList.contains('is-hidden')) return;
      if (panel.contains(e.target) || (notifyBtn && notifyBtn.contains(e.target))) return;
      closeNotify();
    });

    window.addEventListener('hashchange', function () {
      var deep = /^#messages\/(\d+)$/.exec(location.hash || '');
      state.inbox.threadId = deep ? parseInt(deep[1], 10) : null;
      if (!state.token) return;
      render();
    });
    setInterval(function () { if (state.token && !document.hidden) loadNotifications(); }, 60000);
    window.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var panel = qa('.js-notify-panel');
      if (panel && !panel.classList.contains('is-hidden')) { closeNotify(); return; }
      if (qa('.drawer')) {
        var d = qa('.drawer');
        d.remove();
        var bk = qa('.backdrop');
        if (bk) bk.remove();
        document.body.style.overflow = '';
      } else if (qa('.js-gate') && isSwapGate()) {
        closeGate();
      }
    });
  }

  function isSwapGate() {
    var gate = qa('.js-gate');
    return gate && gate.querySelector('.gate-close');
  }

  function restorePersona() {
    var people = state.devUsers.length ? state.devUsers : state.users;
    // ?as=<user id> is a development-only deep link used for screenshots and
    // role-by-role review; it selects a seeded persona, never a role.
    var requested = parseInt((new URLSearchParams(location.search).get('as') || ''), 10);
    if (requested) {
      for (var k = 0; k < people.length; k++) if (people[k].id === requested) { state.personaId = requested; return; }
    }
    var saved = parseInt(localStorage.getItem('derexi.personaId') || '', 10);
    if (saved) {
      for (var i = 0; i < people.length; i++) if (people[i].id === saved) { state.personaId = saved; return; }
    }
    // Sam Okonkwo (employee) is the default experience when the seed is present.
    for (var j = 0; j < people.length; j++) if (people[j].id === 8) { state.personaId = 8; return; }
    state.personaId = people.length ? people[0].id : 8;
  }

  function openGateForSwap() {
    if (!state.devAuth) return;
    var existing = qa('.js-gate');
    if (existing) { closeGate(); return; }
    document.body.appendChild(renderGate(true));
    document.body.style.overflow = 'hidden';
  }
})();
