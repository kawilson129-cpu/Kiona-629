// Real UI + API against serve_week7_fixture.py. All records are illustrative.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const base='http://127.0.0.1:8027';
const output=fileURLToPath(new URL('../../docs/week7/evidence/',import.meta.url));
fs.mkdirSync(output+'screenshots',{recursive:true});
const tabs=await (await fetch(process.env.CDP_URL || 'http://[::1]:9222/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
let sequence=0;const pending=new Map(), errors=[], checks=[];
ws.onmessage=event=>{
  const message=JSON.parse(event.data);
  if(message.id){const job=pending.get(message.id);if(!job)return;pending.delete(message.id);clearTimeout(job.timer);message.error?job.reject(message.error):job.resolve(message.result)}
  else if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text);
};
function send(method,params={}){return new Promise((resolve,reject)=>{
  const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout: '+method))},12000);
  pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));
})}
async function evaluate(expression){const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw Error(result.exceptionDetails.text);return result.result.value}
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(expression){for(let i=0;i<100;i++){try{if(await evaluate(expression))return}catch{}await delay(100)}throw Error('Missing UI state: '+expression)}
function check(name,condition,detail){checks.push({name,status:condition?'PASS':'FAIL',detail});console.log((condition?'PASS  ':'FAIL  ')+name)}
async function screenshot(name){await evaluate(`document.querySelector('.js-recon-mode').textContent='LOCAL FIXTURE · Illustrative records · No Supabase writes';document.querySelector('.lh-class').textContent='LOCAL FIXTURE';document.querySelector('.lh-date').textContent='LOCAL FIXTURE';Promise.all(document.querySelector('#app').getAnimations({subtree:true}).filter(a=>a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))`);const result=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(output+'screenshots/'+name+'.png',Buffer.from(result.data,'base64'))}
async function navigate(uid,hash='messages'){
  await send('Page.navigate',{url:base+'/ui/?as='+uid+'&verify='+Date.now()+'#'+hash});
  await until(`document.readyState==='complete'&&document.querySelector('#persona-select')?.value==='${uid}'&&(!!document.querySelector('.msgs-rows')||!!document.querySelector('.msgs-list-meta'))`);
}
async function clickText(selector,text){return evaluate(`[...document.querySelectorAll(${JSON.stringify(selector)})].find(el=>el.textContent.trim()===${JSON.stringify(text)}).click()`)}
await send('Runtime.enable');await send('Page.enable');
await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
if(process.argv.includes('--tls-evidence')){
  await send('Emulation.setDeviceMetricsOverride',{width:1100,height:1500,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:new URL('../../docs/week7/evidence/readonly-diagnostics.json',import.meta.url).href});
  await until(`document.body.textContent.includes('TLSv1.3')&&document.body.textContent.includes('postgres_backend_connection')`);
  const capture=await send('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync(output+'screenshots/08-observed-tls-diagnostics.png',Buffer.from(capture.data,'base64'));
  console.log('Captured actual read-only TLS diagnostics, including unverified protections');
  ws.close();process.exit(0);
}
try {
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await navigate(8);
  check('three panels render on desktop',await evaluate(`getComputedStyle(document.querySelector('.msgs-shell')).gridTemplateColumns.split(' ').length===3`));
  await evaluate(`[...document.querySelectorAll('.msgs-folder')].find(el=>el.querySelector('.msgs-folder-name').textContent==='My requests').click()`);
  await until('document.querySelectorAll(".msgs-row").length===3');
  await screenshot('01-employee-inbox-fixture');
  await evaluate(`document.querySelector('[data-thread="1"]').click()`);
  await until('!!document.querySelector(".msgs-composer textarea")');
  check('selected conversation loads its real replies',await evaluate(`document.querySelector('.msgs-detail').textContent.includes('electronic signature workflow')`));
  await until(`!document.querySelector('[data-thread="1"] .msgs-unread-dot')`);
  check('reading clears the selected row unread dot',await evaluate(`!document.querySelector('[data-thread="1"] .msgs-unread-dot')`));
  await evaluate(`location.hash='#messages/2'`);
  await until(`document.querySelector('.msgs-thread-id')?.textContent.includes('0002')`);
  check('hash navigation selects the requested thread',await evaluate(`document.querySelector('.msgs-detail-question').textContent.includes('leave request')`));
  await evaluate(`document.querySelector('.msgs-composer textarea').value='Draft retained';document.querySelector('.msgs-composer textarea').dispatchEvent(new Event('input'));location.hash='#messages/1'`);
  await until(`document.querySelector('.msgs-thread-id')?.textContent.includes('0001')`);
  await evaluate(`location.hash='#messages/2'`);
  await until(`document.querySelector('.msgs-thread-id')?.textContent.includes('0002')`);
  check('draft survives navigation within the same test session',await evaluate(`document.querySelector('.msgs-composer textarea').value==='Draft retained'`));

  await navigate(9);
  await evaluate(`document.querySelector('.js-notify').click()`);
  await until(`!document.querySelector('.notify-panel').classList.contains('is-hidden')`);
  check('owner receives assignment notification',await evaluate(`document.querySelector('.notify-list').textContent.includes('Assigned')`));
  await screenshot('02-owner-notification-fixture');
  await evaluate(`document.querySelector('.js-notify-close').click();document.querySelector('[data-thread="2"]').click()`);
  await until('!!document.querySelector(".msgs-composer textarea")');
  await evaluate(`let ta=document.querySelector('.msgs-composer textarea');ta.value='Browser fixture reply: submit the request through the portal.';ta.dispatchEvent(new Event('input'));let send=document.querySelector('.msgs-composer .send-btn');send.click();send.click()`);
  await until(`document.querySelector('.msgs-stream').textContent.includes('Browser fixture reply:')`);
  check('double click sends only one stored reply',await evaluate(`[...document.querySelectorAll('.msgs-stream .msg-body')].filter(el=>el.textContent.startsWith('Browser fixture reply:')).length===1`));
  await clickText('.msgs-actions button','Resolve thread');
  await until(`!![...document.querySelectorAll('.msgs-actions button')].find(el=>el.textContent==='Close thread')`);
  check('resolve disables the reply composer',await evaluate(`!document.querySelector('.msgs-composer')`));
  await screenshot('03-owner-resolved-fixture');
  await navigate(8,'messages/2');
  await until(`!![...document.querySelectorAll('.msgs-actions button')].find(el=>el.textContent==='Reopen thread')`);
  await clickText('.msgs-actions button','Reopen thread');
  await until(`!!document.querySelector('.msgs-composer')`);
  check('employee reopens and sees persisted workflow history',await evaluate(`document.querySelector('.msgs-stream').textContent.includes('Reopened from the inbox.')`));
  await screenshot('04-employee-reopened-fixture');

  await navigate(2);
  await evaluate(`[...document.querySelectorAll('.msgs-folder')].find(el=>el.textContent.includes('All threads')).click()`);
  await until(`document.querySelectorAll('.msgs-row').length===5`);
  await evaluate(`document.querySelector('[data-thread="4"]').click()`);
  await until('!!document.querySelector(".msgs-assign-select")');
  check('administrator has organization oversight and assignment controls',await evaluate(`document.querySelector('.msgs-rail-note').textContent.includes('Organisation-wide')&&!!document.querySelector('.msgs-assign-select')`));
  await screenshot('05-admin-oversight-fixture');

  for(const width of [1440,1280,1024,820,390]){
    await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
    await evaluate('window.scrollTo(0,0)');await delay(100);
    check('no page overflow at '+width+'px',await evaluate('document.documentElement.scrollWidth===document.documentElement.clientWidth'));
  }
  await screenshot('06-mobile-thread-fixture');
  await evaluate(`document.querySelector('.msgs-back').click()`);
  check('mobile back restores the conversation list',await evaluate(`!document.querySelector('.msgs-shell').classList.contains('is-thread')&&getComputedStyle(document.querySelector('.msgs-list')).display!=='none'`));
  await navigate(12,'messages/1');
  await until(`document.querySelector('.msgs-detail').textContent.includes('Thread unavailable')`);
  check('unrelated owner receives an access-denied view',await evaluate(`document.querySelector('.msgs-detail').textContent.includes('Clarification request not found')`));
  await screenshot('07-unauthorized-thread-fixture');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await navigate(8);
  await evaluate(`(async()=>{const token=sessionStorage.getItem('derexi.accessToken');for(let i=0;i<26;i++){const r=await fetch('/ask',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({question:'Pagination fixture request '+i})});if(!r.ok)throw Error('Fixture creation failed')}})()`);
  await evaluate(`[...document.querySelectorAll('.msgs-folder')].find(el=>el.textContent.includes('My requests')).click()`);
  await until(`document.querySelectorAll('.msgs-row').length===25&&!!document.querySelector('.msgs-pagination')`);
  await clickText('.msgs-pagination button','Next');
  await until(`document.querySelector('.msgs-list-meta .n').textContent.startsWith('26–')`);
  check('pagination reaches threads beyond the first 25',await evaluate(`document.querySelectorAll('.msgs-row').length===4`));
  await clickText('.msgs-pagination button','Previous');
  await until(`document.querySelectorAll('.msgs-row').length===25`);
  check('previous page returns to the first 25',true);
  await evaluate(`document.querySelector('.msgs-search input').value='no-such-fixture';document.querySelector('.msgs-search input').dispatchEvent(new Event('input'))`);
  await until(`document.querySelector('.msgs-list').textContent.includes('No matches')`);
  check('search has a meaningful empty state',true);
  for(const hash of ['assist','library','pulse','messages']){
    await evaluate(`location.hash='#${hash}'`);await delay(200);
    check('navigation opens '+hash,await evaluate(`document.querySelector('.nav-link.is-current')?.dataset.view==='${hash}'`));
    if(hash==='pulse')check('Pulse view stays read-only',await evaluate(`!!document.querySelector('.pulse-view')&&!document.querySelector('.pulse-view form,.pulse-view textarea')`));
  }
  check('no runtime exceptions',errors.length===0,errors);
} catch(error){
  const page=await evaluate('document.body.innerText.slice(0,2400)');
  check('browser workflow completes',false,{error:String(error),page});
  console.log(page);
  await screenshot('browser-failure-fixture').catch(()=>{});
}
finally {
  fs.writeFileSync(output+'browser-results.json',JSON.stringify({mode:'Isolated real API + SQLite; illustrative records',checks,errors},null,2)+'\n');
  ws.close();
}
console.log(`${checks.filter(c=>c.status==='PASS').length} passed, ${checks.filter(c=>c.status==='FAIL').length} failed`);
process.exit(checks.some(c=>c.status==='FAIL')?1:0);
