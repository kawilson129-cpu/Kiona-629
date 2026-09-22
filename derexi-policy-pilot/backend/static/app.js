/* DeRexi · Employee Policy Assistant — thin vanilla-JS client for POST /ask */
(function () {
  'use strict';

  // Demo front-line employee (Sam Okonkwo) seeded in the handbook.
  var USER_ID = 8;

  var form = document.getElementById('ask-form');
  var input = document.getElementById('question');
  var askBtn = document.getElementById('ask-btn');
  var arrowIcon = askBtn.querySelector('.arrow');
  var spinner = askBtn.querySelector('.spin');

  var regions = ['loading', 'answer', 'reference', 'clarification', 'error'];
  var els = {};
  regions.forEach(function (id) { els[id] = document.getElementById(id); });

  var lastQuestion = null;

  function setBusy(busy) {
    askBtn.disabled = busy || trim(input.value).length < 2;
    arrowIcon.hidden = busy;
    spinner.hidden = !busy;
  }

  function trim(s) { return (s || '').replace(/^\s+|\s+$/g, ''); }

  function showRegion(id, fn) {
    regions.forEach(function (r) {
      els[r].hidden = (r !== id);
    });
    if (fn) fn();
  }

  function stripReference(answer) {
    var text = String(answer || '');
    var idx = text.search(/\n\s*Reference\s*:/i);
    return idx === -1 ? trim(text) : trim(text.slice(0, idx));
  }

  function render(data) {
    if (!data) return;

    if (data.needs_clarification) {
      showRegion('clarification', function () {
        els.clarification.textContent = data.answer || '';
      });
      return;
    }

    // Employee-facing answer
    var body = stripReference(data.answer);
    showRegion('answer', function () {
      els['answer'].textContent = body;
    });

    // Policy reference card when a citation exists
    var cit = (data.citations && data.citations.length) ? data.citations[0] : null;
    if (cit) {
      els['ref-version'].textContent = cit.version_no ? 'v' + cit.version_no : '';
      els['ref-title'].textContent = cit.title || '';
      els['ref-excerpt'].textContent = cit.excerpt || '';
      els['reference'].hidden = false;
    }
  }

  function showError(message) {
    showRegion('error', function () {
      els['error'].textContent =
        message || 'DeRexi could not be reached. Please try again in a moment.';
    });
  }

  function ask(question) {
    lastQuestion = question;
    setBusy(true);
    showRegion('loading');

    fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: USER_ID, question: question })
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().catch(function () { return {}; })
            .then(function (j) {
              var detail = j.detail;
              var msg = Array.isArray(detail) && detail.length
                ? detail[0].msg
                : (typeof detail === 'string' ? detail : '');
              throw new Error(msg || 'DeRexi could not be reached. Please try again in a moment.');
            });
        }
        return res.json();
      })
      .then(render)
      .catch(function (err) {
        showError(err && err.message ? err.message : null);
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  }

  function onKeydown(e) {
    // Cmd/Ctrl + Enter submits, mirroring the Ask DeRexi action.
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = trim(input.value);
    if (q.length < 2 || askBtn.disabled) return;
    ask(q);
  });

  input.addEventListener('input', function () {
    setBusy(false);
  });

  input.addEventListener('keydown', onKeydown);

  document.getElementById('retry-btn').addEventListener('click', function () {
    if (lastQuestion) ask(lastQuestion);
  });

  setBusy(false);
  input.focus();
})();