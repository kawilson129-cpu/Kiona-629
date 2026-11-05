/* Loaded only by the isolated local entry point. No JWT is exposed to JavaScript. */
(function () {
  'use strict';
  var csrf = '';
  var identity = {
    userId: null,
    fetch: function (url, options) {
      options = Object.assign({}, options || {});
      options.credentials = 'same-origin';
      options.headers = Object.assign({}, options.headers || {});
      if (options.method && !/^(GET|HEAD)$/.test(options.method)) options.headers['X-CSRF-Token'] = csrf;
      return window.fetch(url, options);
    },
    switchPersona: function (id) {
      return identity.fetch('/__dev/switch', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({user_id: id})
      }).then(function (r) {
        if (!r.ok) throw new Error('Identity switch was denied.');
        return r.json();
      }).then(function (s) { csrf = s.csrf; identity.userId = s.user_id; });
    }
  };
  identity.ready = window.fetch('/__dev/session', {credentials: 'same-origin'}).then(function (r) {
    if (!r.ok) throw new Error('Activate a local developer session first.');
    return r.json();
  }).then(function (s) { csrf = s.csrf; identity.userId = s.user_id; });
  window.DeRexiIdentity = identity;
})();
