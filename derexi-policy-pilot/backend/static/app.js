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
    msgTab: 'inbox',
    openThreadId: null,
    messagesData: { inbox: [], sent: [] },
    threadData: null
  };

  function api(path, opts) {
    opts = opts || {};
    var cfg = { method: opts.method || 'GET' };
    if (opts.body) { cfg.headers = { 'Content-Type': 'application/json' }; cfg.body = opts.body; }
    return fetch(path, cfg).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }

  function loadAll() {
    return Promise.all([api('/users'), api('/roles')]).then(function (r) {
      state.users = r[0] || [];
      state.roles = r[1] || [];
    });
  }

  function currentUser() {
    for (var i = 0; i < state.users.length; i++) if (state.users[i].id === state.personaId) return state.users[i];
    return null;
  }

  function isGovernanceAllowed() {
    var u = currentUser();
    if (!u) return false;
    var rid = u.role_id || u.roleId;
    if (rid > 1) return true;
    var rn = String(u.role || '').toLowerCase();
    return rn.indexOf('policy owner') !== -1 || rn.indexOf('system') !== -1;
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
    state.users.forEach(function (u) {
      var o = document.createElement('option');
      o.value = u.id;
      o.textContent = u.full_name + ' · ' + titleRole(u.role);
      if (u.id === state.personaId) o.selected = true;
      sel.appendChild(o);
    });
    sel.onchange = function () { choosePersona(parseInt(sel.value, 10), false); };
  }

  function refreshNav() {
    qaa('.js-gov-link').forEach(function (a) {
      a.classList.toggle('is-hidden', !isGovernanceAllowed());
    });
    if (!isGovernanceAllowed() && location.hash === '#governance') location.hash = '#assist';
  }

  function choosePersona(id, fromGate) {
    var previous = state.personaId;
    state.personaId = id;
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
    state.msgTab = 'inbox';
    render();
  }

  /* ---------------------------------------------------------------- render */
  function currentView() {
    if (!state.personaId) return null;
    var hash = location.hash || '#assist';
    if (hash === '#governance' && !isGovernanceAllowed()) return 'assist';
    if (hash === '#library') return 'library';
    if (hash === '#messages') return 'messages';
    if (hash === '#governance') return 'governance';
    return 'assist';
  }

  function render() {
    var app = qa('#app');
    var v = currentView();
    if (v === null) { app.innerHTML = ''; renderBoot(); return; }
    app.innerHTML = '';
    var fn = v === 'library' ? renderLibrary : v === 'governance' ? renderGovernance : v === 'messages' ? renderMessages : renderAssist;
    fn(app);
    qaa('.nav-link').forEach(function (a) {
      a.classList.toggle('is-current', a.dataset.view === v);
    });
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
    state.users.forEach(function (pers) {
      var flag = pers.role_id === 2 ? 'Policy Owner' : pers.role_id === 3 ? 'System Admin' : pers.role_id === 1 ? 'Employee' : '';
      var accessLabel = (function(){
        if (pers.role && pers.role.name) {
          var rn = pers.role.name.toUpperCase().replace(/_/g, ' ');
          if (rn === 'SYSTEM ADMIN') return 'SYSTEM ADMIN';
          if (rn === 'POLICY OWNER') return 'POLICY OWNER';
          if (rn === 'EMPLOYEE') return 'EMPLOYEE';
          return rn;
        }
        return flag.toUpperCase();
      })();
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
    var who = userName(r.assigned_to) || 'Policy Owner';
    return h('div', { class: 'routed' }, [
      h('span', { class: 'ic-wrap', html: icon('route') }),
      h('div', null, [
        h('h4', { text: 'Routed to a policy owner' }),
        h('p', { text: 'This question needs a human judgment. It has been forwarded with a clarification request and will be answered there.' }),
        h('div', { class: 'who', text: 'Assigned · ' + who })
      ])
    ]);
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
     Internal Messages -- persisted clarification correspondence.

     Each thread is one clarification_request: the employee who asked
     (clarification_requests.user_id) and the policy owner it was routed to
     (clarification_requests.assigned_to). Replies are stored in
     clarification_replies and the originating question is the linked
     messages.body. Persona switching is a LOCAL DEMO affordance only -- the
     selected user_id is supplied by the client and is NOT authentication; when
     JWT auth is wired in the sender must come from the verified token.
     ---------------------------------------------------------------------- */
  function messagesApi(userId) {
    return api('/messages?user_id=' + encodeURIComponent(userId));
  }

  function snippet(text) {
    var body = String(text || '').replace(/\s+/g, ' ').trim();
    return body.length > 96 ? body.slice(0, 96).trim() + '\u2026' : body;
  }

  function threadQuestion(t) {
    return t.question || t.reason || 'Policy clarification request.';
  }

  function threadSubject(t) {
    if (t.subject) return t.subject;
    if (t.policy_title) return 'Clarification \u00b7 ' + t.policy_title;
    return 'Policy clarification';
  }

  function threadCounterpart(t) {
    var me = currentUser();
    if (me && t.user_id === me.id) return t.assignee || 'Policy Owner';
    return t.requester || 'Employee';
  }

  function threadLastBody(t) {
    if (t.last_reply && t.last_reply.body) return snippet(t.last_reply.body);
    return snippet(threadQuestion(t));
  }

  function isAssignee(t) {
    var me = currentUser();
    return !!(me && t.assigned_to === me.id);
  }

  function fmtWhen(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' \u00b7 ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }

  function threadStamp(status) {
    return h('span', { class: 'stamp ' + stampCls(status), html: '<span class="dot"></span>' + escText(String(status || '').replace(/_/g, ' ')) });
  }

  function renderMessages(app) {
    var view = h('div', { class: 'view' });

    var head = h('div', { class: 'view-head' });
    head.appendChild(h('p', { class: 'view-kicker', text: 'Internal Messages' }));
    head.appendChild(h('h1', { class: 'view-title', html: 'Inbox &amp; <em>correspondence</em>' }));
    head.appendChild(h('p', { class: 'view-sub', text: 'Clarification requests DeRexi routed to a policy owner, and the replies that follow. Every thread here is stored in the policy register.' }));
    view.appendChild(head);
    app.appendChild(view);

    if (state.openThreadId) {
      loadConversation(view, state.openThreadId);
      return;
    }
    loadThreads(view);
  }

  function skelMessages() {
    return h('div', { class: 'skel', style: 'height:260px;border-radius:16px;opacity:.7' });
  }

  function loadThreads(view) {
    var host = h('div', null);
    host.appendChild(skelMessages());
    view.appendChild(host);

    messagesApi(state.personaId).then(function (data) {
      state.messagesData = { inbox: data.inbox || [], sent: data.sent || [] };
      host.innerHTML = '';
      host.appendChild(buildMessageTabs());
      host.appendChild(buildThreadList(state.messagesData));
    }).catch(function (err) {
      host.innerHTML = '';
      host.appendChild(h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'Messages unavailable' }),
        h('div', { class: 'ok', text: err.message })
      ]));
    });
  }

  function buildMessageTabs() {
    var tabs = h('div', { class: 'tabs', role: 'tablist' });
    [['inbox', 'Inbox'], ['sent', 'Sent']].forEach(function (pair) {
      var b = h('button', { type: 'button', class: 'tab' + (state.msgTab === pair[0] ? ' is-current' : ''), role: 'tab', dataset: { tab: pair[0] }, text: pair[1] });
      b.addEventListener('click', function () {
        if (state.msgTab === pair[0]) return;
        state.msgTab = pair[0];
        state.openThreadId = null;
        render();
      });
      tabs.appendChild(b);
    });
    return tabs;
  }

  function buildThreadList(data) {
    var isSent = state.msgTab === 'sent';
    var list = isSent ? data.sent : data.inbox;
    var pane = h('div', { class: 'pane' });
    pane.appendChild(h('div', { class: 'pane-head' }, [
      h('h3', { text: isSent ? 'Sent' : 'Inbox' }),
      h('span', { class: 'badge', text: String(list.length) + (isSent ? ' sent' : ' threads') })
    ]));
    var body = h('div', { class: 'pane-body thread-list' });
    if (!list.length) {
      body.appendChild(h('div', { class: 'empty' }, [
        h('div', { class: 'mark', text: isSent ? 'Nothing sent' : 'Inbox clear' }),
        h('div', { class: 'ok', text: isSent ? 'Questions DeRexi routes to a policy owner will appear here.' : 'No clarification requests have been routed to you.' })
      ]));
    } else {
      list.forEach(function (t) { body.appendChild(buildThreadRow(t)); });
    }
    pane.appendChild(body);
    return pane;
  }

  function buildThreadRow(t) {
    var row = h('button', { type: 'button', class: 'thread-row', 'aria-label': 'Open thread: ' + threadSubject(t) }, [
      h('span', { class: 'thread-avatar', text: initials(threadCounterpart(t)) }),
      h('div', { class: 'thread-main' }, [
        h('div', { class: 'thread-top' }, [
          h('span', { class: 'thread-subject', text: threadSubject(t) }),
          t.reply_count ? h('span', { class: 'badge', text: String(t.reply_count) + (t.reply_count === 1 ? ' reply' : ' replies') }) : null
        ]),
        h('div', { class: 'thread-people', text: t.requester + '  \u2192  ' + (t.assignee || 'Unassigned') }),
        h('div', { class: 'thread-snippet', text: threadLastBody(t) })
      ]),
      h('div', { class: 'thread-side' }, [
        h('span', { class: 'thread-time', text: fmtWhen(t.updated_at || t.created_at) }),
        threadStamp(t.status)
      ])
    ]);
    row.addEventListener('click', function () { state.openThreadId = t.id; render(); });
    return row;
  }

  function loadConversation(view, id) {
    var host = h('div', null);
    host.appendChild(skelMessages());
    view.appendChild(host);

    api('/clarifications/' + id).then(function (t) {
      state.threadData = t;
      host.innerHTML = '';
      host.appendChild(buildConversation(t));
    }).catch(function (err) {
      host.innerHTML = '';
      host.appendChild(h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'Thread unavailable' }),
        h('div', { class: 'ok', text: err.message })
      ]));
    });
  }

  function convField(k, v) {
    return h('div', { class: 'conv-field' }, [
      h('span', { class: 'k', text: k }),
      h('span', { class: 'v', text: v })
    ]);
  }

  function buildConversation(t) {
    var wrap = h('div', null);

    var back = h('button', { type: 'button', class: 'back-link', text: '\u2190 Back to ' + (state.msgTab === 'sent' ? 'Sent' : 'Inbox') });
    back.addEventListener('click', function () { state.openThreadId = null; render(); });
    wrap.appendChild(back);

    var head = h('div', { class: 'conv-head card card-pad' });
    head.appendChild(h('div', { class: 'conv-top' }, [
      h('div', { class: 'conv-title-row' }, [
        h('h2', { class: 'conv-subject', text: threadSubject(t) })
      ]),
      threadStamp(t.status)
    ]));
    head.appendChild(h('div', { class: 'conv-fields' }, [
      convField('From', t.requester || 'Employee'),
      convField('To', t.assignee || 'Unassigned'),
      convField('Related policy', t.policy_title || (t.policy_id ? 'Policy ' + t.policy_id : 'None on file')),
      convField('Opened', fmtWhen(t.created_at)),
      convField('Clarification status', String(t.status).replace(/_/g, ' '))
    ]));
    if (t.policy_id) {
      head.appendChild(h('div', { style: 'margin-top:14px' }, [
        h('button', { type: 'button', class: 'btn btn-ghost', text: 'Open policy', onclick: function () { openDrawer(t.policy_id); } })
      ]));
    }
    wrap.appendChild(head);

    var events = threadEvents(t);
    var sec = h('section', { class: 'section' });
    sec.appendChild(h('div', { class: 'section-head' }, [
      h('h2', { class: 'section-title', text: 'Conversation' }),
      h('span', { class: 'section-meta', text: events.length + ' ' + (events.length === 1 ? 'message' : 'messages') })
    ]));
    var thread = h('div', { class: 'thread' });
    events.forEach(function (m) { thread.appendChild(buildThreadMsg(m)); });
    sec.appendChild(thread);
    wrap.appendChild(sec);

    if (t.status === 'resolved' || t.status === 'closed') {
      wrap.appendChild(h('div', { class: 'empty card' }, [
        h('div', { class: 'ok', text: 'This thread is ' + t.status + '. Ask a new question through DeRexi to reopen the discussion.' })
      ]));
    } else {
      wrap.appendChild(buildReplyComposer(t));
    }
    return wrap;
  }

  function threadEvents(t) {
    var events = [{
      id: 'question',
      sender: t.requester || 'Employee',
      mine: t.user_id === state.personaId,
      body: threadQuestion(t),
      at: t.created_at
    }];
    (t.replies || []).forEach(function (r) {
      events.push({
        id: 'reply-' + r.id,
        sender: r.sender || 'Participant',
        mine: r.sender_id === state.personaId,
        body: r.body,
        at: r.created_at
      });
    });
    return events;
  }

  function buildThreadMsg(m) {
    var avatar = m.mine
      ? h('span', { class: 'msg-avatar avatar-user', text: initials(m.sender) })
      : h('span', { class: 'msg-avatar avatar-peer', text: initials(m.sender) });
    return h('div', { class: 'msg' + (m.mine ? ' msg-user' : '') }, [
      avatar,
      h('div', { class: 'msg-col' }, [
        h('div', { class: 'msg-body', text: m.body }),
        h('div', { class: 'msg-meta', text: m.sender + ' \u00b7 ' + fmtWhen(m.at) })
      ])
    ]);
  }

  function buildReplyComposer(t) {
    var sec = h('section', { class: 'section' });
    sec.appendChild(h('div', { class: 'section-head' }, [
      h('h2', { class: 'section-title', text: 'Reply' })
    ]));

    var field = h('div', { class: 'reply-field' });
    var ta = h('textarea', { rows: '3', placeholder: 'Write a reply to ' + threadCounterpart(t) + '. It is saved to the policy register.', value: '' });
    ta.setAttribute('aria-label', 'Your reply');
    var send = h('button', { type: 'button', class: 'send-btn', html: icon('send') + '<span>Send reply</span>' });
    send.setAttribute('aria-label', 'Send reply');
    var acts = h('div', { class: 'reply-actions' }, [send]);

    if (isAssignee(t)) {
      var resolveBtn = h('button', { type: 'button', class: 'btn btn-ghost', text: 'Mark resolved' });
      resolveBtn.addEventListener('click', function () { resolveThread(t); });
      acts.appendChild(resolveBtn);
    }
    field.appendChild(ta);
    field.appendChild(acts);
    sec.appendChild(field);

    send.addEventListener('click', function () {
      var v = ta.value.trim();
      if (!v) { toast('Write a reply first.'); return; }
      send.disabled = true;
      api('/clarifications/' + t.id + '/replies', {
        method: 'POST',
        body: JSON.stringify({ sender_id: state.personaId, body: v })
      }).then(function () {
        toast('Reply sent.');
        render();
      }).catch(function (err) {
        send.disabled = false;
        toast('Could not send reply (' + err.message + ')');
      });
    });
    return sec;
  }

  function resolveThread(t) {
    api('/clarifications/' + t.id + '/resolve', { method: 'POST', body: JSON.stringify({}) }).then(function () {
      toast('Request #' + t.id + ' marked resolved.');
      render();
    }).catch(function (err) {
      toast('Could not resolve request (' + err.message + ')');
    });
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

  /* ---------------------------------------------------------------- boot */
  document.addEventListener('DOMContentLoaded', function () {
    setRecon();
    loadAll().then(function () {
      qaa('.btn-recon').forEach(function (b) {
        b.addEventListener('click', openGateForSwap);
      });
      window.addEventListener('hashchange', function () { render(); });
      window.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          if (qa('.drawer')) {
            var d = qa('.drawer');
            d.remove();
            var bk = qa('.backdrop');
            if (bk) bk.remove();
            document.body.style.overflow = '';
          } else if (qa('.js-gate') && isSwapGate()) {
            closeGate();
          }
        }
      });
      restorePersona();
      buildPersonaSelect();
      refreshNav();
      render();
    }).catch(function (err) {
      var app = qa('#app');
      app.innerHTML = '';
      app.appendChild(h('div', { class: 'empty card' }, [
        h('div', { class: 'mark', text: 'The register could not be opened' }),
        h('div', { class: 'ok', text: err.message })
      ]));
    });
  });

  function isSwapGate() {
    var gate = qa('.js-gate');
    return gate && gate.querySelector('.gate-close');
  }

  function restorePersona() {
    var saved = localStorage.getItem('derexi.personaId');
    if (saved) {
      var id = parseInt(saved, 10);
      for (var i = 0; i < state.users.length; i++) if (state.users[i].id === id) { state.personaId = id; return; }
    }
    state.personaId = 8;
  }

  function openGateForSwap() {
    var existing = qa('.js-gate');
    if (existing) { closeGate(); return; }
    document.body.appendChild(renderGate(true));
    document.body.style.overflow = 'hidden';
  }
})();