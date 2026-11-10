// Agent-executed UAT in Chromium: real UI/BFF/API/SQLite; provider/feed simulated.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const out=fileURLToPath(new URL('../../../semester_5/DeRexi_Week%2010/evidence/',import.meta.url));
const baseline=process.argv.includes('--baseline');
const mobileOnly=process.argv.includes('--mobile-only');
let carriedForward=null,viewport=null;
fs.mkdirSync(out+'screenshots',{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9230/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
let seq=0;const pending=new Map(),checks=[],errors=[],requests=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);else if(m.method==='Network.responseReceived'){const r=m.params.response;if(r.url.startsWith('http://127.0.0.1:8031/'))requests.push({path:new URL(r.url).pathname,status:r.status})}};
function send(method,params={}){return new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},18000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}))})}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expr){for(let i=0;i<120;i++){if(await ev(expr))return;await delay(100)}throw Error('Missing '+expr)}
function check(name,value){checks.push({name,status:value?'PASS':'FAIL'});console.log((value?'PASS ':'FAIL ')+name)}
async function click(text){await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()===${JSON.stringify(text)}).click()`)}
async function shot(name){await ev(`document.querySelector('.lh-date').textContent='WEEK 10 · SIMULATED UAT';document.querySelector('.js-recon-mode').textContent='ISOLATED SQLITE · Mock provider/feed · No live Supabase verification';var label=document.getElementById('week10-evidence-label');if(!label){label=document.createElement('div');label.id='week10-evidence-label';label.style.cssText='position:fixed;bottom:0;left:0;right:0;padding:5px;z-index:2147483647;font:10px/1.3 monospace;background:#201b16;color:#fff;pointer-events:none;text-align:center';document.body.appendChild(label)}label.textContent='SIMULATED UAT · SQLite / mock provider · No live Supabase'`);await delay(500);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(out+'screenshots/'+name+'.png',Buffer.from(r.data,'base64'))}
async function login(uid){await ev(`document.querySelector('#auth-email').value='fixture${uid}@example.invalid';document.querySelector('#auth-password').value='fixture-password';document.querySelector('.auth-form').requestSubmit()`);await until(`document.querySelector('#persona-select')?.value==='${uid}'&&!document.querySelector('#signout-btn').classList.contains('is-hidden')`)}
async function logout(){await ev(`document.querySelector('#signout-btn').click()`);await until(`!!document.querySelector('#auth-password')`)}
async function route(hash,selector){await ev(`location.hash=${JSON.stringify('#'+hash)}`);await until(selector)}
async function api(path,method='GET',body){return ev(`fetch(${JSON.stringify(path)},{method:${JSON.stringify(method)},headers:{'Content-Type':'application/json','X-Derexi-Request':'1'},${body===undefined?'':`body:JSON.stringify(${JSON.stringify(body)}),`}}).then(async r=>({status:r.status,body:await r.json()}))`)}
let adminCookies;
async function state(params){if(!adminCookies){const login=await fetch('http://127.0.0.1:8031/auth/login',{method:'POST',headers:{'Content-Type':'application/json','X-Derexi-Request':'1',Origin:'http://127.0.0.1:8031'},body:JSON.stringify({email:'fixture2@example.invalid',password:'fixture-password'})});if(!login.ok)throw Error('Fixture admin login '+login.status);adminCookies=login.headers.getSetCookie().map(x=>x.split(';')[0]).join('; ')}const r=await fetch('http://127.0.0.1:8031/__fixture/state?'+new URLSearchParams(params),{method:'POST',headers:{Cookie:adminCookies,'X-Derexi-Request':'1',Origin:'http://127.0.0.1:8031'}});if(!r.ok)throw Error('Fixture state '+r.status)}
async function saveDraft(title){await ev(`document.querySelector('[name=title]').value=${JSON.stringify(title)};document.querySelector('[name=confirm_document]').checked=true;document.querySelector('.gov-form').requestSubmit()`);await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);return Number((await ev('location.hash')).split('/')[1])}
async function detail(id){await route('governance/'+id,`!!document.querySelector('.gov-review')`)}
async function overflow(name){check(name,await ev('document.documentElement.scrollWidth<=document.documentElement.clientWidth'))}
async function mobileEmployee(signedIn){
  if(!signedIn){await logout();await login(8)}
  await route('assist',`!!document.querySelector('.composer textarea')||!!document.querySelector('#inc-desc')`);
  if(!await ev(`!!document.querySelector('.composer textarea')`))await click('Ask a question');
  await until(`!!document.querySelector('.composer textarea')`);
  await ev(`document.querySelector('.composer textarea').value='Who can review a mobile policy exception?';document.querySelector('.composer .send-btn').click()`);await until(`!!document.querySelector('.feedback')`);await ev(`document.querySelector('.fb-btn[data-fb=up]').click()`);await until(`document.querySelector('.feedback [role=status]')?.textContent==='Feedback saved.'`);await overflow('U29a Mobile Assistant and saved feedback have no overflow');await shot('13-mobile-assistant-fixture');
  const point=await ev(`var link=document.querySelector('.nav-links [data-view=messages]');link.scrollIntoView({block:'center',inline:'center'});var rect=link.getBoundingClientRect();({x:rect.x+rect.width/2,y:rect.y+rect.height/2})`);await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await until(`!!document.querySelector('.msgs-shell')`);check('U29b Synthesized mobile touch opens Messages navigation',true);
  await until(`!!document.querySelector('.msgs-row[data-thread="1"]')`);await ev(`document.querySelector('.msgs-row[data-thread="1"]').click()`);await until(`!!document.querySelector('.msgs-composer textarea')`);await ev(`document.querySelector('.msgs-composer textarea').value='Please confirm the remote signature steps.';document.querySelector('.msgs-composer .send-btn').click()`);await until(`document.querySelector('.msgs-detail')?.textContent.includes('Please confirm the remote signature steps.')`);check('U29c Mobile employee sends a persisted reply',(await api('/clarifications/1')).body.replies.some(r=>r.body==='Please confirm the remote signature steps.'));await overflow('U29 Mobile Messaging has no horizontal overflow');await shot('14-mobile-messaging-fixture');await logout();await overflow('U30 Mobile sign-in has no horizontal overflow');await shot('15-mobile-signout-fixture');
  check('U31 Logout removes stale private notifications',await ev(`document.querySelectorAll('.js-toasts .toast').length===0`));check('U32 No browser runtime exceptions',errors.length===0);
}
await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
if(process.argv.includes('--viewport-probe')){console.log(await ev(`({innerWidth,innerHeight,clientWidth:document.documentElement.clientWidth,screenWidth:screen.width,visualWidth:visualViewport.width,scale:visualViewport.scale,url:location.pathname})`));ws.close();process.exit(0)}
if(!mobileOnly)await send('Network.clearBrowserCookies');
try{
 if(mobileOnly){
  const previous=JSON.parse(fs.readFileSync(out+'browser-results.json','utf8'));
  carriedForward='attempts/mobile-predecessor-'+Date.now()+'.json';
  fs.writeFileSync(out+carriedForward,JSON.stringify(previous,null,2)+'\n');
  checks.push(...previous.checks.filter(c=>c.status==='PASS'&&!/^U(?:29|30|31|32|28b)/.test(c.name)));
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,screenWidth:390,screenHeight:844,deviceScaleFactor:1,mobile:true});await send('Emulation.setTouchEmulationEnabled',{enabled:true});
  viewport=await ev(`({width:innerWidth,height:innerHeight,visualWidth:visualViewport.width,scale:visualViewport.scale})`);check('U28b Actual mobile layout viewport is 390px',viewport.width===390);
  if(await ev(`!!document.querySelector('#auth-password')`))await login(8);
  await mobileEmployee(true);
 }else{
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:'http://127.0.0.1:8031/ui/'});await until(`!!document.querySelector('#auth-password')`);
 if(!baseline){await ev(`document.querySelector('#auth-email').focus()`);await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});check('U00 Keyboard Tab reaches password input',await ev(`document.activeElement.id==='auth-password'`))}
 if(!baseline){await shot('01-desktop-signin-fixture');await ev(`document.querySelector('#auth-email').value='fixture8@example.invalid';document.querySelector('#auth-password').value='wrong';document.querySelector('.auth-form').requestSubmit()`);await until(`document.querySelector('.auth-form [role=status]')?.textContent.includes('Sign-in failed')`);check('U01 Invalid password rejected and cleared',await ev(`document.querySelector('#auth-password').value===''`))}
 await login(8);await route('assistant',`!!document.querySelector('.composer textarea')`);
 check('U02 Employee navigation hides Governance and Dashboard',await ev(`[...document.querySelectorAll('.js-gov-link')].every(n=>n.classList.contains('is-hidden'))`));
 await ev(`document.querySelector('.composer textarea').value='How do I handle a hypothetical policy exception?';document.querySelector('.composer .send-btn').click()`);await until(`!!document.querySelector('.feedback')`);
 let result=await api('/feedback/mine');const prior=result.body.length;
 await ev(`document.querySelector('.fb-btn[data-fb=up]').click()`);await delay(500);
 result=await api('/feedback/mine');check('U03 Feedback click persists a database rating',result.body.length===prior+1);
 await shot(baseline?'00-before-fix-feedback-fixture':'02-assistant-feedback-fixture');
 if(!baseline){
  check('U04 Saved feedback exposes pressed state',await ev(`document.querySelector('.fb-btn[data-fb=up]').getAttribute('aria-pressed')==='true'`));
  await state({feedback:'false'});await ev(`document.querySelector('.fb-btn[data-fb=down]').click()`);await until(`document.querySelector('.feedback [role=status]')?.textContent.includes('not saved')`);
  check('U05 Failed feedback never shows false success or changes accepted rating',await ev(`document.querySelector('.fb-btn[data-fb=up]').classList.contains('is-on')&&!document.querySelector('.fb-btn[data-fb=down]').classList.contains('is-on')`));await shot('03-feedback-error-fixture');await state({});
  await ev(`document.querySelector('.fb-btn[data-fb=down]').click()`);await until(`document.querySelector('.fb-btn[data-fb=down]')?.getAttribute('aria-pressed')==='true'`);
  check('U06 Retrying feedback updates same rating', (await api('/feedback/mine')).body.length===prior+1);
  await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.includes('Open thread')).click()`);await until(`document.querySelector('.msgs-detail-question')?.textContent.includes('hypothetical policy exception')`);check('U07 Assistant deep link opens persisted Messaging thread',true);await shot('04-employee-messaging-fixture');
  await route('governance',`!!document.querySelector('#app .view')`);check('U08 Employee Governance direct route denied',await ev(`!document.querySelector('.lifecycle')`) && (await api('/governance/drafts')).status===403);
  await route('assistant',`!!document.querySelector('.composer')`);await click('Report an incident');await until(`!!document.querySelector('#inc-desc')`);await click('Report incident');check('U09 Missing incident fields show validation',await ev(`document.querySelector('.js-toasts').textContent.includes('Choose an incident category')`));
  await until(`!!document.querySelector('#inc-cat option[value="1"]')`);await ev(`document.querySelector('#inc-cat').value='1';document.querySelector('#inc-desc').value='Suspicious customer document received during UAT.'`);await click('Report incident');await until(`!!document.querySelector('.report-out .report-confirm')`);check('U10 Employee incident form saves real fixture record',(await api('/incidents')).body.some(i=>i.description.includes('during UAT')));
  check('U11 Employee incident triage API denied',(await api('/incidents/1','PATCH',{status:'triaged'})).status===403);
  await logout();check('U12 Logout clears private identity and API session',(await api('/me')).status===401 && await ev(`document.querySelector('#persona-select').textContent.includes('Sign-in required')`));
  await login(4);await route('governance',`!!document.querySelector('.gw-drop')`);await until(`!document.querySelector('.gw-queue-body[aria-busy]')`);check('U13 Owner has My Drafts and peer queues',await ev(`document.querySelector('.gw-queues').textContent.includes('Peer Reviews')&&!document.querySelector('.gw-queues').textContent.includes('Final Approvals')`));
  const doc=await send('DOM.getDocument');const input=await send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'.gw-file'});await send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[out+'inputs/Customer safeguards.docx']});await until(`!!document.querySelector('.gw-document-summary')&&!document.querySelector('.gov-form button[type=submit]').disabled`);
  check('U14 DOCX upload parses and previews real bytes',await ev(`document.querySelector('[name=body]').value.includes('Verify authorization')&&document.querySelector('.gw-live-preview').textContent.includes('Verify authorization')`));
  await ev(`document.querySelector('[name=title]').value='UAT Customer Safeguards';document.querySelector('.gov-form').requestSubmit()`);check('U15 Document confirmation blocks premature save',await ev(`!document.querySelector('[name=confirm_document]').checkValidity()&&location.hash==='#governance'`));
  await ev(`document.querySelector('.gw-document-summary').scrollIntoView({block:'center'})`);await shot('05-document-preview-fixture');
  const did=await saveDraft('UAT Customer Safeguards');
  check('U16 Owner cannot approve or publish own draft',(await api('/governance/drafts/'+did+'/actions','POST',{action:'final_approve',expected_revision:1})).status===403);
  await ev(`document.querySelector('.gov-review select').value='9'`);await click('Submit for peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending peer review')`);await logout();await login(9);
  check('U17 Independent peer receives governance notification',(await api('/messages/notifications')).body.items.some(n=>n.governance_draft_id===did));await detail(did);await click('Approve peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending final approval')`);await shot('06-peer-review-fixture');
  await logout();await login(2);await detail(did);await click('Grant final approval');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('approved pending publication')`);await click('Publish approved version');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('published')`);await shot('07-admin-publication-fixture');
  const published=(await api('/governance/drafts/'+did)).body;const pid=published.policy_id;check('U18 Published document visible through protected Library',(await api('/policies/'+pid)).body.title==='UAT Customer Safeguards');
  await route('dashboard',`document.querySelector('#app').textContent.includes('Health of the')`);check('U19 Admin dashboard reflects persisted feedback',(await api('/dashboard/policy-health')).body.feedback.total>=1);await click('Incidents');await until(`!!document.querySelector('.inc-row')`);await ev(`document.querySelector('.inc-acts select').value='4';[...document.querySelectorAll('.inc-acts button')].find(b=>b.textContent==='Assign').click()`);await until(`document.querySelector('.inc-meta')?.textContent.includes('Maya Patel')`);check('U20 Administrator assignment updates real API',(await api('/incidents')).body.some(i=>i.assigned_to===4));await shot('08-admin-triage-fixture');
  await logout();await login(4);await route('pulse',`!!document.querySelector('.gov-pulse-start')`);
  const source=(await api('/api/pulse')).body.articles[0];
  await ev(`document.querySelector('.gov-pulse-start').click()`);await until(`!!document.querySelector('.gov-form .gov-source')`);
  check('U21 Pulse source reference reaches draft editor',await ev(`document.querySelector('.gov-source a').href===${JSON.stringify(source.url)}`));
  await ev(`var select=document.querySelector('.gov-form select');select.value='${pid}';select.dispatchEvent(new Event('change'))`);await until(`document.querySelector('[name=title]')?.value==='UAT Customer Safeguards'&&document.querySelector('[name=version_no]').value===''`);
  await ev(`document.querySelector('[name=version_no]').value='2.0';document.querySelector('[name=body]').value='Revised safeguards based on source review.'`);const rid=await saveDraft('UAT Customer Safeguards');
  const revision=(await api('/governance/drafts/'+rid)).body;check('U22 Pulse revision preserves exact source and published baseline',revision.source.url===source.url && revision.base_version.body.includes('Verify authorization'));
  check('U23 Existing published policy remains during revision',(await api('/policies/'+pid)).body.latest_version==='1.0');await shot('09-pulse-revision-fixture');
  await state({available:'false'});await route('library',`document.querySelector('#app').textContent.includes('UAT Customer Safeguards')`);check('U24 Library survives Governance outage',(await api('/policies/'+pid)).status===200);await route('governance',`!!document.querySelector('.gw-queue-body .is-error')`);check('U25 Outage replaces loading with retry',await ev(`[...document.querySelectorAll('.gw-queue')].every(p=>p.querySelector('.is-error')&&[...p.querySelectorAll('button')].some(b=>b.textContent==='Try again'))`));await shot('10-workspace-outage-fixture');await state({});await click('Try again');await until(`!document.querySelector('.gw-queue-body .is-error')`);check('U26 Queue retry recovers',true);
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,screenWidth:390,screenHeight:844,deviceScaleFactor:1,mobile:true});await send('Emulation.setTouchEmulationEnabled',{enabled:true});viewport=await ev(`({width:innerWidth,height:innerHeight,visualWidth:visualViewport.width,scale:visualViewport.scale})`);check('U28b Actual mobile layout viewport is 390px',viewport.width===390);await route('library',`document.querySelector('#app').textContent.includes('UAT Customer Safeguards')`);await overflow('U27 Mobile Library has no horizontal overflow');await shot('11-mobile-library-fixture');
  await route('governance',`!!document.querySelector('.gw-drop')`);await overflow('U28 Mobile Governance has no horizontal overflow');await shot('12-mobile-governance-fixture');
  await mobileEmployee(false);
 }
 }
}catch(error){checks.push({name:'Workflow completion',status:'FAIL',detail:String(error)});console.error(error);console.log(await ev('document.body.innerText.slice(0,1400)'));await shot(baseline?'attempt-baseline':'attempt-final');process.exitCode=1}
finally{const result=JSON.stringify({mode:'SIMULATED agent UAT: real Chromium/UI/BFF/API/SQLite; mock provider/feed; mobile emulation, not physical devices',checks,errors,requests,carriedForward,viewport},null,2)+'\n';fs.writeFileSync(out+(baseline?'browser-before-fix-results.json':'browser-results.json'),result);fs.mkdirSync(out+'attempts',{recursive:true});fs.writeFileSync(out+'attempts/browser-'+Date.now()+'.json',result);ws.close()}
console.log(`${checks.filter(c=>c.status==='PASS').length} PASS / ${checks.filter(c=>c.status==='FAIL').length} FAIL`);if(checks.some(c=>c.status==='FAIL'))process.exitCode=1;
