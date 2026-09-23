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

  // Inner text nodes so the card chrome (eyebrow, glyph, retry button) survives.
  els['answer-body'] = document.getElementById('answer-body');
  els['clarification-body'] = document.getElementById('clarification-body');
  els['error-body'] = document.getElementById('error-body');
  els['ref-version'] = document.getElementById('ref-version');
  els['ref-title'] = document.getElementById('ref-title');
  els['ref-excerpt'] = document.getElementById('ref-excerpt');

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

  function setText(node, value, fallback) {
    if (node) node.textContent = trim(value) || (fallback || '');
  }

  function renderReference(data) {
    var cit = (Array.isArray(data.citations) && data.citations.length)
      ? data.citations[0]
      : null;
    if (!cit || typeof cit !== 'object') {
      els['reference'].hidden = true;
      return;
    }
    var title = trim(cit.title);
    var excerpt = trim(cit.excerpt);
    var version = trim(cit.version_no);
    if (!title && !excerpt) {
      // A citation object with no usable text is treated as absent.
      els['reference'].hidden = true;
      return;
    }
    setText(els['ref-title'], title, 'Aurum Capital Bank policy');
    setText(els['ref-excerpt'], excerpt, '');
    setText(els['ref-version'], version ? 'v' + version : '', '');
    // Hide the version chip entirely when the backend omits a version number.
    els['ref-version'].hidden = !version;
    els['reference'].hidden = false;
  }

  function render(data) {
    if (!data || typeof data !== 'object') {
      showError('DeRexi returned an empty response. Please try again in a moment.');
      return;
    }

    if (data.needs_clarification) {
      showRegion('clarification', function () {
        setText(els['clarification-body'], data.answer,
          'This question needs a little more context. DeRexi has routed it to a policy owner who will connect you with the right guidance.');
      });
      return;
    }

    var body = stripReference(data.answer);
    if (!body && !(Array.isArray(data.citations) && data.citations.length)) {
      showError('DeRexi did not find a confident answer for this question. Please try rephrasing, and a policy owner can help if it persists.');
      return;
    }

    showRegion('answer', function () {
      setText(els['answer-body'], data.answer,
        'DeRexi did not return a text answer for this question.');
    });

    renderReference(data);
  }

  function showError(message) {
    showRegion('error', function () {
      setText(els['error-body'], message,
        'DeRexi could not be reached. Please try again in a moment.');
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