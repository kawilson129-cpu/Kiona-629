"""Dependency-free static + real Chrome/CDP checks, scoped to this course only.

Node's built-in WebSocket drives the browser from stdin. No second JS file is
created, loaded by the page, or shipped as application code.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / 'final_project'
EVIDENCE = ROOT / 'evidence'


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts, self.events, self.identifiers, self.labels = [], [], [], []
        self.script_text = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts.append(attrs)
            self.in_script = True
        self.events.extend(key for key in attrs if key.startswith('on'))
        if 'id' in attrs:
            self.identifiers.append(attrs['id'])
        if tag == 'label':
            self.labels.append(attrs.get('for'))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False

    def handle_data(self, text):
        if self.in_script and text.strip():
            self.script_text.append(text)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


# Browser automation is test instrumentation, not application JavaScript.
BROWSER_CHECKS = r'''
import fs from 'node:fs';
const checks = [], consoleEvents = [], errors = [], requests = [], matrix = [];
const [endpoint, base, output] = process.argv.slice(2);
const tabs = await (await fetch(endpoint + '/json/list')).json();
const websocket = new WebSocket(tabs.find(tab => tab.type === 'page').webSocketDebuggerUrl);
await new Promise((resolve, reject) => { websocket.onopen = resolve; websocket.onerror = reject; });
let sequence = 0;
const pending = new Map();
websocket.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id) {
    const job = pending.get(message.id);
    if (!job) return;
    pending.delete(message.id); clearTimeout(job.timer);
    message.error ? job.reject(Error(message.error.message)) : job.resolve(message.result);
  } else if (message.method === 'Runtime.consoleAPICalled') consoleEvents.push(message.params);
  else if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
  else if (message.method === 'Network.requestWillBeSent') requests.push(message.params.request.url);
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const identifier = ++sequence;
    const timer = setTimeout(() => { pending.delete(identifier); reject(Error(method + ' timed out')); }, 8000);
    pending.set(identifier, {resolve, reject, timer});
    websocket.send(JSON.stringify({id: identifier, method, params}));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true});
  if (result.exceptionDetails) throw Error(result.exceptionDetails.text);
  return result.result.value;
}
async function until(expression) {
  for (let attempt = 0; attempt < 80; attempt++) {
    if (await evaluate(expression)) return;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw Error('Condition did not become true: ' + expression);
}
function check(name, condition, detail = null) {
  checks.push({name, status: condition ? 'PASS' : 'FAIL', detail});
}
async function scenario(impact, likelihood, sensitive = false, ongoing = false) {
  await evaluate(`document.querySelector('#impact-level').value='${impact}';
    document.querySelector('#likelihood-level').value='${likelihood}';
    document.querySelector('#sensitive-data').checked=${sensitive};
    document.querySelector('#ongoing-incident').checked=${ongoing};
    document.querySelector('button[type=submit]').click()`);
  return await evaluate(`({score:document.querySelector('#calculation').textContent,
    priority:document.querySelector('#priority-label').textContent,
    tone:document.querySelector('#result').dataset.priority})`);
}
async function screenshot(name) {
  const capture = await send('Page.captureScreenshot', {format:'png', captureBeyondViewport:true});
  fs.writeFileSync(output + '/' + name + '.png', Buffer.from(capture.data, 'base64'));
}
async function key(key, code = key, virtualKeyCode = 0) {
  const nativeCodes = {Tab:48,Enter:36,Digit3:20};
  const text = key==='Enter' ? '\r' : key.length===1 ? key : '';
  await send('Input.dispatchKeyEvent', {type:'keyDown', key, code, text, unmodifiedText:text,
    windowsVirtualKeyCode:virtualKeyCode,nativeVirtualKeyCode:nativeCodes[code]||0});
  await send('Input.dispatchKeyEvent', {type:'keyUp', key, code, windowsVirtualKeyCode:virtualKeyCode,
    nativeVirtualKeyCode:nativeCodes[code]||0});
}
try {
  await Promise.all([send('Page.enable'), send('Runtime.enable'), send('Network.enable')]);
  await send('Emulation.setDeviceMetricsOverride', {width:1280,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate', {url:base});
  await until(`document.readyState==='complete' && typeof calculatePriority==='function'`);
  check('B01 Initial state has no fabricated calculated result', await evaluate(`
    document.querySelector('#calculation').hidden && document.querySelector('#result').dataset.priority==='empty'`));
  const initial = await scenario(2,2);
  check('B02 Submit renders 2 × 2 = 4 and Routine review', initial.score==='2 × 2 = 4' && initial.tone==='routine', initial);
  await until('true');
  const entry = consoleEvents.find(event => event.args[0]?.value==='DeRexi practice result');
  const logged = entry ? JSON.parse((await send('Runtime.callFunctionOn', {
    objectId:entry.args[1].objectId,functionDeclaration:'function(){ return JSON.stringify(this); }', returnByValue:true
  })).result.value) : null;
  check('B03 Real console.log matches displayed result', logged?.priorityScore===4 && logged?.priorityLabel===initial.priority, logged);
  check('B04 Live variables include String, integer Number and Boolean',
    typeof logged?.policyArea==='string' && Number.isInteger(logged?.impactLevel) && typeof logged?.sensitiveData==='boolean');
  const expectedScores = [[1,2,3,4,5],[2,4,6,8,10],[3,6,9,12,15],[4,8,12,16,20],[5,10,15,20,25]];
  const expectedTones = [
    ['routine','routine','routine','routine','routine'],
    ['routine','routine','review','review','review'],
    ['routine','review','review','review','high'],
    ['routine','review','review','high','high'],
    ['routine','review','high','high','high']
  ];
  for (let impact = 1; impact <= 5; impact++) {
    for (let likelihood = 1; likelihood <= 5; likelihood++) {
      for (const sensitive of [false,true]) for (const ongoing of [false,true]) {
        const actual = await evaluate(`calculatePriority(${impact},${likelihood},${sensitive},${ongoing})`);
        const expectedTone = ongoing || (sensitive && impact>=3) ? 'immediate' : expectedTones[impact-1][likelihood-1];
        matrix.push({impact,likelihood,sensitive,ongoing,expectedScore:expectedScores[impact-1][likelihood-1],expectedTone,
          actualScore:actual.priorityScore,actualTone:actual.priorityTone,
          status:actual.priorityScore===expectedScores[impact-1][likelihood-1] && actual.priorityTone===expectedTone ? 'PASS':'FAIL'});
      }
    }
  }
  check('B05 All 100 score/flag combinations match the reference matrix', matrix.every(row=>row.status==='PASS'), {cases:matrix.length});
  for (const [name,impact,likelihood,sensitive,ongoing,tone,score] of [
    ['B06 Lower threshold: score 5 is routine',1,5,false,false,'routine',5],
    ['B07 Upper threshold: score 6 is review',2,3,false,false,'review',6],
    ['B08 Score 12 remains review',3,4,false,false,'review',12],
    ['B09 Score 15 becomes high',3,5,false,false,'high',15],
    ['B10 Maximum score 25 is high without override',5,5,false,false,'high',25],
    ['B11 OR: ongoing event overrides minimum score',1,1,false,true,'immediate',1],
    ['B12 AND: sensitive data plus impact 3 overrides low score',3,1,true,false,'immediate',3],
    ['B13 Sensitive data alone below impact 3 does not override',2,1,true,false,'routine',2],
    ['B14 Both flags still select immediate priority',5,5,true,true,'immediate',25]
  ]) {
    const result=await scenario(impact,likelihood,sensitive,ongoing);
    check(name,result.tone===tone && result.score===`${impact} × ${likelihood} = ${score}`,result);
  }
  await scenario(3,5);
  await screenshot('desktop-high-priority');
  await evaluate(`document.querySelector('#likelihood-level').value='1';document.querySelector('#likelihood-level').dispatchEvent(new Event('change',{bubbles:true}))`);
  check('B15 Changed input recomputes displayed result', await evaluate(`document.querySelector('#calculation').textContent==='3 × 1 = 3' && document.querySelector('#result').dataset.priority==='routine'`));
  await evaluate(`document.querySelector('#policy-area').value='Remote work';document.querySelector('#policy-area').dispatchEvent(new Event('change',{bubbles:true}))`);
  check('B16 Policy area updates context without changing score', await evaluate(`document.querySelector('#result-context').textContent.includes('Remote work') && document.querySelector('#calculation').textContent==='3 × 1 = 3'`));
  check('B17 Invalid Number/Boolean inputs are rejected', await evaluate(`
    [[0,2,false,false],[6,2,false,false],[2.5,2,false,false],['2',2,false,false],[NaN,2,false,false],
    [Infinity,2,false,false],[2,2,'false',false],[2,2,false,null]].every(function(values){
      try { calculatePriority(...values);return false; } catch(error){return error instanceof RangeError;}
    })`));
  await evaluate(`const badOption=document.createElement('option');badOption.value='6';badOption.textContent='Invalid test value';
    document.querySelector('#impact-level').append(badOption);document.querySelector('#impact-level').value='6';
    document.querySelector('button[type=submit]').click()`);
  check('B18 Invalid UI input shows error and clears stale result', await evaluate(`!document.querySelector('#form-error').hidden && document.querySelector('#calculation').hidden && document.querySelector('#form-error').textContent.includes('1 to 5')`));
  await evaluate(`document.querySelector('#impact-level option[value="6"]').remove();document.querySelector('button[type=reset]').click()`);
  check('B19 Reset restores defaults, clears error/result and returns focus', await evaluate(`
    document.querySelector('#impact-level').value==='2' && document.querySelector('#likelihood-level').value==='2' &&
    document.querySelector('#policy-area').value==='Data handling' && !document.querySelector('#sensitive-data').checked &&
    !document.querySelector('#ongoing-incident').checked && document.querySelector('#calculation').hidden &&
    document.querySelector('#form-error').hidden && document.activeElement.id==='policy-area'`));
  await key('Tab','Tab',9);
  check('B20 Keyboard Tab reaches impact control',await evaluate(`document.activeElement.id==='impact-level'`));
  // Native select type-ahead: the option labels begin with their numeric value.
  await key('3','Digit3',51);
  check('B21 Keyboard changes native select value',await evaluate(`document.querySelector('#impact-level').value==='3'`),
    await evaluate(`({value:document.querySelector('#impact-level').value,focus:document.activeElement.id})`));
  await evaluate(`document.querySelector('button[type=submit]').focus()`);
  check('B22 Keyboard focus has visible outline',await evaluate(`parseFloat(getComputedStyle(document.activeElement).outlineWidth)>=2`));
  await key('Enter','Enter',13);
  check('B23 Keyboard Enter calculates result',await evaluate(`document.querySelector('#calculation').textContent==='3 × 2 = 6'`),
    await evaluate(`({result:document.querySelector('#calculation').textContent,focus:document.activeElement.outerHTML})`));
  await evaluate(`document.querySelector('#scoring-rules summary').click()`);
  check('B24 Native scoring-rules disclosure opens',await evaluate(`document.querySelector('#scoring-rules').open`));
  await evaluate(`document.querySelector('#scoring-rules').open=false`);
  check('B25 Runtime page has exactly one local external script',await evaluate(`
    document.scripts.length===1 && document.scripts[0].getAttribute('src')==='script.js' && document.scripts[0].defer`));
  check('B26 Controls have labels and results are announced politely',await evaluate(`
    [...document.querySelectorAll('select,input')].every(control=>control.labels.length>0) &&
    document.querySelector('#result').getAttribute('aria-live')==='polite' &&
    document.querySelector('#form-error').getAttribute('role')==='alert'`));
  check('B27 Desktop has no horizontal overflow',await evaluate(`document.documentElement.scrollWidth<=innerWidth`));
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await scenario(3,1,true,false);
  await evaluate(`scrollTo(0,0)`);
  check('B28 Mobile 390px has no overflow and stacks form/result',await evaluate(`
    innerWidth===390 && document.documentElement.scrollWidth<=390 &&
    document.querySelector('.result-panel').getBoundingClientRect().top >= document.querySelector('.scenario').getBoundingClientRect().bottom`));
  check('B29 Mobile controls retain 48px targets',await evaluate(`
    [...document.querySelectorAll('select,button,.check-row')].every(control=>control.getBoundingClientRect().height>=48)`));
  await screenshot('mobile-immediate-priority');
  await send('Emulation.setDeviceMetricsOverride',{width:320,height:780,deviceScaleFactor:1,mobile:true});
  check('B30 Narrow 320px viewport has no horizontal overflow',await evaluate(`document.documentElement.scrollWidth<=320`));
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  check('B31 Reduced-motion preference disables smooth scroll/transition',await evaluate(`
    getComputedStyle(document.documentElement).scrollBehavior==='auto' &&
    getComputedStyle(document.querySelector('.primary-button')).transitionDuration==='0s'`));
  check('B32 No external assets or API requests',requests.every(url=>url.startsWith(base)||url.startsWith('data:')),requests);
  check('B33 No browser runtime exceptions',errors.length===0,errors);
} catch(error) { check('Browser workflow completed',false,String(error)); }
finally {
  const result={timestamp:new Date().toISOString(),mode:'REAL local Chrome/CDP; actual standalone page and script; no DOM mocks or backend',
    passed:checks.filter(row=>row.status==='PASS').length,failed:checks.filter(row=>row.status==='FAIL').length,
    checks,consoleEvents:consoleEvents.map(event=>({type:event.type,args:event.args.map(arg=>({type:arg.type,value:arg.value,description:arg.description}))})),errors,requests};
  fs.writeFileSync(output+'/browser-results.json',JSON.stringify(result,null,2)+'\n');
  fs.writeFileSync(output+'/calculation-matrix.json',JSON.stringify(matrix,null,2)+'\n');
  try { await send('Browser.close'); } catch (error) { /* Python owns final cleanup. */ }
  websocket.close();
  console.log(`Browser: ${result.passed} PASS / ${result.failed} FAIL; ${matrix.length} matrix cases`);
  if(result.failed) process.exitCode=1;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true', help='Also launch isolated headless Chrome, test and capture screenshots')
    args = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    checks = []

    def check(name, condition, detail=None):
        checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

    html = (PROJECT / 'index.html').read_text()
    script = (PROJECT / 'script.js').read_text()
    page = PageParser()
    page.feed(html)
    syntax = subprocess.run(['node', '--check', str(PROJECT / 'script.js')], capture_output=True, text=True)
    check('S01 Node syntax check', syntax.returncode == 0, {'command':'node --check javascript_1/final_project/script.js','exit_code':syntax.returncode,'stdout':syntax.stdout,'stderr':syntax.stderr})
    check('S02 Exactly one JavaScript file in the course', [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.js')] == ['final_project/script.js'])
    check('S03 Exactly one external script, deferred, no inline handlers/code', page.scripts == [{'src':'script.js','defer':None}] and not page.events and not page.script_text)
    check('S04 Linked stylesheet exists and no remote asset references', 'href="styles.css"' in html and (PROJECT/'styles.css').is_file() and 'https://' not in html and 'http://' not in html)
    check('S05 Unique HTML IDs and every label targets an existing control', len(page.identifiers)==len(set(page.identifiers)) and all(identifier in page.identifiers for identifier in page.labels))
    check('S06 Core calculation, actual DOM and console output present', all(token in script for token in ['impactLevel * likelihoodLevel','if (ongoingIncident || (sensitiveData && impactLevel >= 3))','console.log(','.textContent =','Number(impactInput.value)']))
    check('S07 No backend calls, browser storage or dynamic HTML injection', all(token not in script for token in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', '.innerHTML', 'eval(']))
    manifest = json.loads((EVIDENCE/'source-review.json').read_text())
    check('S08 Reviewed DeRexi files, root memory and original rubric unchanged', all(
        hashlib.sha256((ROOT.parent/source['path']).read_bytes()).hexdigest()==source['sha256'] for source in manifest['sources']))
    rubric_path = EVIDENCE/'rubric-map.json'
    rubric = json.loads(rubric_path.read_text()) if rubric_path.exists() else []
    required_sections = ('## Objective and rubric requirement', '## Implementation and source references',
                         '## Demonstration', '## Actual test results and evidence', '## Completion status')
    check('S09 Eight separate reports and root documentation complete', len(rubric)==8 and all(
        (ROOT/row['folder']/'report.md').is_file() and all(
            section in (ROOT/row['folder']/'report.md').read_text() for section in required_sections)
        for row in rubric) and all((ROOT/name).is_file() for name in ('README.md','verification.md')))
    check('S10 All cited implementation line ranges exist and appear in reports', bool(rubric) and all(
        (ROOT/reference['path']).is_file() and 1 <= reference['start'] <= reference['end'] <= len((ROOT/reference['path']).read_text().splitlines())
        and f"{reference['start']}–{reference['end']}" in (ROOT/row['folder']/'report.md').read_text()
        for row in rubric for reference in row['references']))
    bad_links, local_links = [], 0
    for path in ROOT.rglob('*.md'):
        if '.browser-profile' in path.parts:
            continue
        for link in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', path.read_text()):
            url = urlsplit(link)
            if url.scheme:
                continue
            local_links += 1
            if not (path.parent/unquote(url.path)).exists():
                bad_links.append(str(path.relative_to(ROOT))+' -> '+link)
    check('S11 Documentation evidence/source links resolve', not bad_links,
          {'local_links':local_links,'broken_links':bad_links})
    identifiers = re.findall(r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)', script)
    for parameters in re.findall(r'function(?:\s+\w+)?\s*\(([^)]*)\)', script):
        identifiers.extend(parameter.strip() for parameter in parameters.split(',') if parameter.strip())
    check('S12 Application variables and parameters have descriptive multi-character names',
          bool(identifiers) and all(len(identifier)>1 for identifier in identifiers),sorted(set(identifiers)))
    result = {'timestamp':datetime.now(timezone.utc).isoformat(),'mode':'Static file/syntax checks only',
              'passed':sum(row['status']=='PASS' for row in checks),'failed':sum(row['status']=='FAIL' for row in checks),'checks':checks,
              'application_sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(PROJECT.iterdir()) if path.is_file()}}
    (EVIDENCE/'static-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Static: {result["passed"]} PASS / {result["failed"]} FAIL')
    if result['failed']:
        raise SystemExit(1)
    if not args.browser:
        return
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if not Path(chrome).is_file():
        raise SystemExit('BLOCKED: installed Chrome executable not found; static checks saved.')
    profile = EVIDENCE / '.browser-profile'
    if profile.exists():
        # Never attach to or kill an existing browser; caller can retry after closing it.
        lock = profile/'SingletonLock'
        if lock.is_symlink():
            lock_target = os.readlink(lock)
            hostname, separator, process_id = lock_target.rpartition('-')
            if not separator or not process_id.isdigit() or hostname != os.uname().nodename:
                raise SystemExit('BLOCKED: cannot establish course browser lock ownership.')
            try:
                os.kill(int(process_id), 0)  # Read-only liveness probe, not a signal.
            except ProcessLookupError:
                pass  # Stale lock belonging to our previous terminated course browser.
            except PermissionError:
                raise SystemExit('BLOCKED: cannot verify course browser process state.')
            else:
                raise SystemExit('BLOCKED: dedicated course browser profile is in use.')
        elif lock.exists():
            raise SystemExit('BLOCKED: unrecognized dedicated browser lock.')
        shutil.rmtree(profile)
    profile.mkdir()
    server = ThreadingHTTPServer(('127.0.0.1',0), partial(QuietHandler,directory=str(PROJECT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    browser = None
    try:
        with (profile/'chrome.log').open('w') as log:
            browser = subprocess.Popen([chrome,'--headless=new','--disable-gpu','--disable-background-networking',
                '--disable-component-update','--disable-extensions','--disable-sync','--no-first-run',
                '--no-default-browser-check','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
                '--user-data-dir='+str(profile),'about:blank'],stdout=log,stderr=log)
            active_port = profile/'DevToolsActivePort'
            for attempt in range(100):
                if active_port.exists():
                    break
                if browser.poll() is not None:
                    raise SystemExit('BLOCKED: isolated Chrome exited before CDP startup; see ignored runtime log.')
                time.sleep(.1)
            if not active_port.exists():
                raise SystemExit('BLOCKED: Chrome CDP startup timed out.')
            endpoint = 'http://127.0.0.1:'+active_port.read_text().splitlines()[0]
            base = f'http://127.0.0.1:{server.server_port}/'
            run = subprocess.run(['node','--input-type=module','-',endpoint,base,str(EVIDENCE)],
                                 input=BROWSER_CHECKS,text=True,capture_output=True,timeout=55)
            print(run.stdout.strip())
            if run.stderr:
                print(run.stderr[:1200])
            if run.returncode:
                raise SystemExit(run.returncode)
    finally:
        if browser is not None and browser.poll() is None:
            browser.terminate()
            try:
                browser.wait(timeout=8)
            except subprocess.TimeoutExpired:
                browser.kill()
                browser.wait(timeout=4)
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
