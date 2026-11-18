// Real DeRexi UI/network evidence. No intercepted responses or mocked browser fetch.
// API server: api_integration_evidence.py serve; dedicated Chrome CDP port 9241.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const repo = fileURLToPath(new URL('../../../', import.meta.url));
const course = path.resolve(repo, 'ai_api_intergration_1');
const output = path.resolve(process.argv[2] || '');
if (!output.startsWith(course + path.sep) || !fs.existsSync(path.join(output, 'fixture.json')))
  throw Error('Output must be an existing evidence fixture run inside the course folder');
if (fs.existsSync(path.join(output, 'browser-results.json'))) throw Error('Use a fresh run');
const base = 'http://127.0.0.1:8041';
const question = 'How should I handle a hypothetical policy exception?';
const tabs = await (await fetch('http://127.0.0.1:9241/json/list')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let sequence = 0;
const pending = new Map(), requests = new Map(), errors = [], checks = [], captures = [];
const bodyJobs = [];
ws.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id) {
    const job = pending.get(message.id);
    if (!job) return;
    pending.delete(message.id); clearTimeout(job.timer);
    message.error ? job.reject(Error(message.error.message)) : job.resolve(message.result);
  } else if (message.method === 'Runtime.exceptionThrown') {
    errors.push(message.params.exceptionDetails.text);
  } else if (message.method === 'Network.requestWillBeSent') {
    const {requestId, request} = message.params;
    if (!request.url.startsWith(base)) return;
    const url = new URL(request.url);
    if (!['/policies', '/ask', '/api/pulse'].includes(url.pathname)) return;
    const headers = {};
    for (const [key, value] of Object.entries(request.headers)) {
      if (key.toLowerCase() === 'content-type') headers[key] = value;
      if (key.toLowerCase() === 'authorization') headers[key] = '[REDACTED]';
    }
    requests.set(requestId, {method: request.method, url: request.url,
      request_headers: headers, request_body: request.postData ? JSON.parse(request.postData) : null});
  } else if (message.method === 'Network.responseReceived' && requests.has(message.params.requestId)) {
    const record = requests.get(message.params.requestId), r = message.params.response;
    record.status_code = r.status;
    record.content_type = r.mimeType;
  } else if (message.method === 'Network.loadingFinished' && requests.has(message.params.requestId)) {
    const requestId = message.params.requestId;
    bodyJobs.push(send('Network.getResponseBody', {requestId}).then(r => {
      requests.get(requestId).response_body = JSON.parse(r.base64Encoded ? Buffer.from(r.body, 'base64').toString() : r.body);
    }).catch(error => { requests.get(requestId).capture_error = String(error); }));
  }
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {pending.delete(id); reject(Error('CDP timeout: ' + method));}, 20000);
    pending.set(id, {resolve, reject, timer});
    ws.send(JSON.stringify({id, method, params}));
  });
}
async function evaluate(expression) {
  const r = await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) throw Error(r.exceptionDetails.text);
  return r.result.value;
}
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function until(expression) {
  for (let i = 0; i < 150; i++) {
    if (await evaluate(expression)) return;
    await sleep(100);
  }
  throw Error('UI state not reached: ' + expression);
}
function check(name, condition, detail) {
  checks.push({name, status: condition ? 'PASS' : 'FAIL', detail});
}
async function screenshot(name, label) {
  // Capture after real entry animations settle; do not alter product styles.
  await evaluate(`Promise.all(document.getAnimations().filter(a=>a.effect?.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))`);
  await evaluate('document.fonts.ready.then(()=>window.scrollTo(0,0))');
  await sleep(300);
  await evaluate(`(() => { let label=document.getElementById('api-course-evidence');
    if(!label){label=document.createElement('div');label.id='api-course-evidence';
      label.style.cssText='position:fixed;bottom:0;left:0;right:0;padding:8px;z-index:2147483647;background:#201b16;color:white;font:12px monospace;text-align:center;pointer-events:none';document.body.appendChild(label)}
    label.textContent=${JSON.stringify(label)}; })()`);
  const result = await send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: false});
  fs.mkdirSync(path.join(output, 'screenshots'), {recursive: true});
  fs.writeFileSync(path.join(output, 'screenshots', name + '.png'), Buffer.from(result.data, 'base64'));
  captures.push({path: 'screenshots/' + name + '.png', label,
    displayed_text: await evaluate(`document.querySelector('#app').innerText`)});
}

try {
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', {cacheDisabled: true});
  await send('Emulation.setDeviceMetricsOverride', {width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false});
  await send('Page.navigate', {url: base + '/ui/?as=8&verify=' + Date.now() + '#library'});
  await until(`document.querySelector('#persona-select')?.value==='8'&&document.querySelectorAll('.ledger-row').length===2`);
  check('B01 Existing Library displays GET policy titles and versions', await evaluate(`document.querySelector('#app').innerText.includes('Employee Leave')&&document.querySelector('#app').innerText.includes('1.0')`));
  await screenshot('01-get-library', 'ACTUAL UI + HTTP GET /policies | Synthetic SQLite data | Local dev auth | No production');
  await evaluate(`location.hash='#assist'`);
  await until(`!!document.querySelector('.composer textarea')`);
  await evaluate(`document.querySelector('.composer textarea').value=${JSON.stringify(question)};document.querySelector('.composer .send-btn').click()`);
  await until(`document.querySelector('#app').innerText.includes('routed it to a policy owner')`);
  // A DOM condition alone can observe an older answer during repeated runs.
  // Wait for this run's actual POST response body before correlating it to UI.
  for (let i=0; i<100; i++) {
    if ([...requests.values()].some(r=>r.method==='POST'&&new URL(r.url).pathname==='/ask'&&r.response_body)) break;
    await sleep(100);
  }
  await Promise.all(bodyJobs);
  const post = [...requests.values()].find(r => r.method === 'POST' && new URL(r.url).pathname === '/ask');
  check('B02 Original Assistant sends actual POST JSON and receives 200', post?.status_code === 200 && post.request_body?.question === question);
  check('B03 POST JSON answer equals displayed text', !!post?.response_body?.answer && await evaluate(`document.querySelector('#app').innerText.includes(${JSON.stringify(post.response_body.answer)})`));
  check('B04 Friendly uncertainty controls render', await evaluate(`!!document.querySelector('.feedback')&&/open thread/i.test(document.querySelector('#app').innerText)`));
  await screenshot('02-post-assistant', 'ACTUAL UI + HTTP POST /ask | Search MOCKED (no matches), AI DISABLED | SQLite only');
  await evaluate(`location.hash='#pulse'`);
  await until(`!!document.querySelector('.pulse-view')&&!document.querySelector('.pulse-loading')`);
  // Wait for the observed JSON response, without fabricating a feed on failure.
  for (let i=0; i<100; i++) {
    await Promise.all(bodyJobs);
    if ([...requests.values()].some(r => new URL(r.url).pathname === '/api/pulse' && r.response_body)) break;
    await sleep(100);
  }
  const pulse = [...requests.values()].find(r => new URL(r.url).pathname === '/api/pulse');
  const titles = pulse?.response_body?.articles?.map(a => a.title) || [];
  const text = await evaluate(`document.querySelector('#app').innerText`);
  check('B05 Pulse formats real API article titles into its original UI', pulse?.status_code === 200 && titles.some(t => text.includes(t)));
  await screenshot('03-get-pulse', 'ACTUAL UI + public Pulse GET | Real public feeds; inspect source-status evidence | No AI call');
  check('B06 Browser observed successful GET and POST independently', [...requests.values()].some(r => r.method === 'GET' && r.status_code === 200) && !!post && post.status_code === 200);
  check('B07 No browser runtime exceptions', errors.length === 0, errors);
} catch (error) {
  check('Browser verification completed', false, String(error));
} finally {
  await Promise.all(bodyJobs);
  fs.writeFileSync(path.join(output, 'browser-results.json'), JSON.stringify({timestamp: new Date().toISOString(),
    mode: 'REAL Chromium + unmodified DeRexi UI + loopback HTTP; synthetic SQLite, mocked PostgreSQL search, AI disabled; live Pulse sources',
    checks, requests: [...requests.values()], captures, errors,
    passed: checks.filter(c => c.status === 'PASS').length,
    failed: checks.filter(c => c.status === 'FAIL').length}, null, 2) + '\n');
  ws.close();
}
console.log(JSON.stringify({passed: checks.filter(c => c.status === 'PASS').length, failed: checks.filter(c => c.status === 'FAIL').length}));
if (checks.some(c => c.status === 'FAIL')) process.exitCode = 1;
