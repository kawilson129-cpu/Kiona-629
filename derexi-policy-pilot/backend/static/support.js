/* Human-reviewed support handoff; all destinations and identity bind server-side. */
(function () {
  'use strict';
  function el(tag, text, cls) { var n = document.createElement(tag); if (text) n.textContent = text; if (cls) n.className = cls; return n; }
  function button(text, fn, secondary) { var b = el('button', text, 'btn ' + (secondary ? 'btn-ghost' : 'btn-primary')); b.type = 'button'; b.onclick = fn; return b; }
  function field(parent, label, value, area) { var l = el('label', label, 'support-field'); var n = document.createElement(area ? 'textarea' : 'input'); n.value = value || ''; n.maxLength = area ? 2000 : 1000; if (area) n.rows = 4; l.appendChild(n); parent.appendChild(l); return n; }
  function status(parent) { var n = el('p', '', 'support-status'); n.setAttribute('role', 'status'); n.setAttribute('aria-live', 'polite'); parent.appendChild(n); return n; }
  function showError(node, error) { node.textContent = error.message || 'Unable to save. Preserve your details and try again.'; }
  function requestView(root, row, api) {
    root.replaceChildren(); root.appendChild(el('p', 'SUPPORT REQUEST', 'view-kicker'));
    root.appendChild(el('h2', row.state === 'draft' ? 'Review before sending' : 'Support handoff status', 'section-title'));
    var d = row.request;
    var summary = el('dl', '', 'support-summary');
    [['Employee', d.employee], ['Department', d.department], ['Type', d.incident_type.replaceAll('_', ' ')], ['Urgency', d.urgency], ['Destination', d.destination], ['Prepared', row.created_at], ['Details', d.details], ['Follow-up answers', d.answers.join('\n')]].forEach(function (pair) { summary.appendChild(el('dt', pair[0])); summary.appendChild(el('dd', pair[1])); });
    root.appendChild(summary); root.appendChild(el('p', row.state === 'draft' ? 'Check these details before explicitly confirming. Your existing IT/Security team handles investigation and resolution.' : 'These are the details you reviewed. Your existing IT/Security team handles investigation and resolution.', 'report-note'));
    var info = status(root);
    var labels = { draft: 'Ready for your review. Nothing has been submitted.', queued: 'Confirmed and recorded internally. Email has not yet been attempted.', disabled: 'Recorded internally. Outbound email is disabled; no email sent. Use your established IT/Security channel.', sending: 'An attempt is pending. Do not resend; ask IT/Security to verify using your reference.', accepted: 'The mail server accepted this request. Delivery and ticket creation are not confirmed.', retryable: 'Connection failed before sending. You may retry after the waiting period.', rejected: 'The mail server rejected the request. Contact IT/Security through your established channel.', unknown: 'Delivery outcome is unknown. Do not retry; contact IT/Security to avoid a duplicate.', configuration_error: 'Delivery configuration needs administrator attention. No successful send is confirmed.' };
    info.textContent = labels[row.state] || 'Check your request status with IT/Security.';
    root.appendChild(el('p', 'Reference: ' + row.id + ' · Attempts: ' + row.attempts, 'support-reference'));
    if (row.state === 'draft') {
      var check = el('label', '', 'support-confirm'); var checkbox = document.createElement('input'); checkbox.type = 'checkbox'; check.appendChild(checkbox); check.appendChild(document.createTextNode('I have reviewed the details and explicitly authorize submission to the approved destination.')); root.appendChild(check);
      var send = button('Confirm support request', function () { send.disabled = true; api('/support/requests/' + row.id + '/confirm', { method: 'POST', body: JSON.stringify({ confirmed: true }) }).then(function (confirmed) { requestView(root, confirmed, api); }).catch(function (e) { showError(info, e); send.disabled = !checkbox.checked; }); });
      send.disabled = true; checkbox.onchange = function () { send.disabled = !checkbox.checked; }; root.appendChild(send);
    } else if (['queued', 'disabled', 'retryable', 'configuration_error'].includes(row.state)) {
      var deliver = button(row.state === 'retryable' ? 'Retry delivery attempt' : 'Attempt approved handoff', function () { deliver.disabled = true; api('/support/requests/' + row.id + '/dispatch', { method: 'POST' }).then(function (updated) { requestView(root, updated, api); }).catch(function (e) { showError(info, e); deliver.disabled = false; }); }); root.appendChild(deliver);
    }
    root.appendChild(button('Refresh status', function () { api('/support/requests/' + row.id).then(function (updated) { requestView(root, updated, api); }).catch(function (e) { showError(info, e); }); }, true));
  }
  function intake(api, assessment, initial) {
    var root = el('section', '', 'support-desk');
    function editor(a, details) {
      root.replaceChildren(); root.appendChild(el('p', a.guidance, a.urgency === 'urgent' ? 'support-urgent' : 'report-note'));
      root.appendChild(el('h2', 'Let’s prepare the right request', 'section-title'));
      var typeLabel = el('label', 'Request type', 'support-field'); var types = document.createElement('select');
      ['phishing', 'compromise', 'lost_device', 'outage', 'technical'].forEach(function (k) { var o = el('option', k.replaceAll('_', ' ')); o.value = k; o.selected = k === a.incident_type; types.appendChild(o); }); typeLabel.appendChild(types); root.appendChild(typeLabel);
      var text = field(root, 'What happened? Edit before review.', details, true);
      var answersRoot = el('div'); root.appendChild(answersRoot); var answers = [];
      function questions(qs) { answersRoot.replaceChildren(); answers = qs.map(function (q) { return field(answersRoot, q, '', false); }); }
      questions(a.questions.length ? a.questions : ['Which work application or device is affected?', 'When did it start, and what work is blocked?']);
      var info = status(root);
      types.onchange = function () { var followups = { phishing: ['Did you click or enter credentials? Answer yes/no only.', 'When and in which work application?'], compromise: ['Unexpected sign-ins or MFA prompts? Do not share codes.', 'Which application or device, and when?'], lost_device: ['What device is missing and when was it last seen?', 'Could someone access the unlocked device? No unlock codes.'], outage: ['Which service and how many people are affected?', 'When did the disruption begin?'], technical: ['Which work device or application is affected?', 'When did it start and what is blocked?'] }; questions(followups[types.value]); };
      var review = button('Review support request', function () {
        review.disabled = true; info.textContent = 'Preparing your review…';
        var payload = { idempotency_key: crypto.randomUUID(), incident_type: types.value, details: text.value, answers: answers.map(function (n) { return n.value; }) };
        api('/support/prepare', { method: 'POST', body: JSON.stringify(payload) }).then(function (row) {
          var savedDetails = text.value; requestView(root, row, api);
          root.appendChild(button('Edit details before confirmation', function () { editor(a, savedDetails); }, true));
        }).catch(function (e) { showError(info, e); review.disabled = false; });
      }); root.appendChild(review);
      root.appendChild(el('p', 'Never include passwords, MFA/recovery codes or customer account numbers. Email routing may be unavailable; urgent reporting must not wait.', 'report-note'));
    }
    editor(assessment, initial || ''); return root;
  }
  function start(root, api) {
    var panel = el('section', '', 'support-desk'); panel.appendChild(el('h2', 'Tell us what happened', 'section-title')); panel.appendChild(el('p', 'DeRexi helps prepare a request for your existing IT/Security team. It does not replace the ticketing system.', 'view-sub'));
    var details = field(panel, 'Describe the issue without secrets', '', true); var info = status(panel);
    var assess = button('Continue', function () { assess.disabled = true; api('/support/assess', { method: 'POST', body: JSON.stringify({ text: details.value }) }).then(function (a) { panel.replaceWith(intake(api, a, details.value)); }).catch(function (e) { showError(info, e); assess.disabled = false; }); }); panel.appendChild(assess); root.appendChild(panel);
    api('/support/requests').then(function (rows) { var list = el('section', '', 'support-desk'); list.appendChild(el('h2', 'Your support references', 'section-title')); rows.forEach(function (row) { list.appendChild(button(row.request.incident_type.replaceAll('_', ' ') + ' · ' + row.state, function () { requestView(list, row, api); }, true)); }); root.appendChild(list); }).catch(function () { info.textContent = 'Request tracking may be unavailable. Use your established IT/Security channel for urgent issues.'; });
  }
  function routing(root, api) {
    var view = el('section', '', 'view support-routing'); root.appendChild(view); view.appendChild(el('p', 'ADMINISTRATION', 'view-kicker')); view.appendChild(el('h1', 'Technical Routing', 'view-title')); view.appendChild(el('p', 'Approved destinations. Clear responsibility. Your existing service desk remains the system of record.', 'view-sub')); var info = status(view);
    function load() { info.textContent = 'Loading approved routing…'; api('/technical-routing/config').then(function (config) {
      info.textContent = config.outbound_mode === 'off' ? 'Outbound delivery is OFF. Route validation sends no email.' : 'Outbound SMTP is configured. Acceptance is not proof of ticket creation.';
      var old = view.querySelector('.support-route-grid'); if (old) old.remove(); var grid = el('div', '', 'support-route-grid'); view.appendChild(grid);
      config.departments.forEach(function (dept) { var card = el('section', '', 'support-desk'); card.appendChild(el('h2', dept.name, 'section-title')); ['security', 'it'].forEach(function (channel) {
        var r = config.routes.find(function (x) { return x.department_id === dept.id && x.channel === channel; }); var label = el('label', channel === 'security' ? 'Security incidents' : 'IT assistance', 'support-field'); var select = document.createElement('select'); select.appendChild(el('option', 'Select approved destination')); select.options[0].value = '';
        config.mailboxes.filter(function (b) { return b.channel === channel; }).forEach(function (b) { var o = el('option', b.label); o.value = b.key; o.selected = r && r.mailbox_key === b.key; select.appendChild(o); }); label.appendChild(select); card.appendChild(label);
        var active = el('label', '', 'support-confirm'); var enabled = document.createElement('input'); enabled.type = 'checkbox'; enabled.checked = !!(r && r.enabled); active.appendChild(enabled); active.appendChild(document.createTextNode('Enable this routing rule')); card.appendChild(active); var message = status(card);
        var save = button('Save ' + channel + ' route', function () { save.disabled = true; api('/technical-routing/config', { method: 'POST', body: JSON.stringify({ department_id: dept.id, channel: channel, mailbox_key: select.value, enabled: enabled.checked, expected_revision: r ? r.revision : 0 }) }).then(load).catch(function (e) { showError(message, e); save.disabled = false; }); }); card.appendChild(save);
        card.appendChild(button('Validate ' + channel + ' route', function () { api('/technical-routing/test', { method: 'POST', body: JSON.stringify({ department_id: dept.id, channel: channel, confirmed: true }) }).then(function (v) { message.textContent = v.notice; }).catch(function (e) { showError(message, e); }); }, true));
      }); grid.appendChild(card); });
      if (!config.mailboxes.length) grid.appendChild(el('p', 'No operator-approved destinations are configured. Ask your deployment operator to review routing. No destination will be guessed.', 'support-urgent'));
      if (config.can_delegate) {
        var grants = el('section', '', 'support-desk'); grants.appendChild(el('h2', 'Delegated routing access', 'section-title')); grants.appendChild(el('p', 'Department-only routing permission; grants no policy approval or full administrator access.', 'report-note'));
        function choice(label, rows, title) { var wrap = el('label', label, 'support-field'); var sel = document.createElement('select'); rows.forEach(function (r) { var o = el('option', r[title]); o.value = r.id; sel.appendChild(o); }); wrap.appendChild(sel); grants.appendChild(wrap); return sel; }
        var uid = choice('Existing employee', config.people, 'name'); var did = choice('Department', config.departments, 'name'); var grantInfo = status(grants);
        function changeGrant(enabled) { api('/technical-routing/grants', { method: 'POST', body: JSON.stringify({ user_id: Number(uid.value), department_id: Number(did.value), enabled: enabled }) }).then(function () { grantInfo.textContent = 'Routing permission updated.'; }).catch(function (e) { showError(grantInfo, e); }); }
        grants.appendChild(button('Grant routing-only access', function () { changeGrant(true); })); grants.appendChild(button('Revoke routing-only access', function () { changeGrant(false); }, true)); config.grants.forEach(function (g) { var person = config.people.find(function (p) { return p.id === g.user_id; }); var dept = config.departments.find(function (d) { return d.id === g.department_id; }); grants.appendChild(el('p', (person ? person.name : 'Existing employee') + ' · ' + (dept ? dept.name : 'Assigned department'), 'support-reference')); }); grid.appendChild(grants);
      }
    }).catch(function (e) { showError(info, e); view.appendChild(button('Try again', load, true)); }); }
    load();
  }
  window.SupportDesk = { intake: intake, start: start, routing: routing };
}());
