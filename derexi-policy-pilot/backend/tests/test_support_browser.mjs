// Real UI/API, isolated SQLite/mocked identity and outbound transport only.
import fs from 'node:fs';
const out=process.env.DEREXI_SPRINT_EVIDENCE;
const fallbackOnly=process.argv.includes('--fallback-only');
fs.mkdirSync(out+'/screenshots',{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9241/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((ok,no)=>{ws.onopen=ok;ws.onerror=no;});
let id=0;const pending=new Map(),checks=[],errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){clearTimeout(p.t);pending.delete(m.id);m.error?p.no(Error(m.error.message)):p.ok(m.result);}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);};
function send(method,params={}){return new Promise((ok,no)=>{const k=++id,t=setTimeout(()=>{pending.delete(k);no(Error('Timeout '+method));},15000);pending.set(k,{ok,no,t});ws.send(JSON.stringify({id:k,method,params}));});}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expr){for(let i=0;i<100;i++){if(await ev(expr))return;await delay(100);}throw Error('Missing '+expr);}
function check(name,pass){checks.push({name,pass:!!pass});console.log((pass?'PASS ':'FAIL ')+name);}
async function click(text){await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()===${JSON.stringify(text)}).click()`);}
async function login(uid){await until(`!!document.querySelector('#auth-email')`);await ev(`document.querySelector('#auth-email').value='fixture${uid}@example.invalid';document.querySelector('#auth-password').value='fixture-password';document.querySelector('.auth-form').requestSubmit()`);await until(`!document.querySelector('#auth-email')&&!!document.querySelector('#app .view')`);await ev(`location.hash='#assist'`);await until(`!!document.querySelector('.composer')||!!document.querySelector('.support-field')`);if(!await ev(`!!document.querySelector('.composer')`))await click('Ask a question');await until(`!!document.querySelector('.composer')`);}
async function logout(){await ev(`document.querySelector('#signout-btn').click()`);await until(`!!document.querySelector('#auth-email')`);}
async function api(path,method='GET',body){return ev(`fetch(${JSON.stringify(path)},{method:${JSON.stringify(method)},headers:{'Content-Type':'application/json','X-Derexi-Request':'1'},${body?'body:'+JSON.stringify(JSON.stringify(body))+',':''}}).then(async r=>({status:r.status,body:await r.json()}))`);}
async function shot(name){await ev(`(()=>{let label=document.getElementById('isolated-label');if(!label){label=document.createElement('div');label.id='isolated-label';label.style.cssText='position:fixed;bottom:0;left:0;right:0;padding:6px;z-index:99999;background:#251d18;color:#fff;font:11px monospace;text-align:center;pointer-events:none';document.body.appendChild(label);}label.textContent='ISOLATED DEMONSTRATION · Fictional SQLite records · Auth/feed/email mocked or OFF';})()`);await delay(250);const p=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(out+'/screenshots/'+name+'.png',Buffer.from(p.data,'base64'));}
async function route(hash,selector){await ev(`location.hash=${JSON.stringify(hash)}`);await until(`!!document.querySelector(${JSON.stringify(selector)})`);}
try{
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:'http://127.0.0.1:8041/ui/'});await until(`document.readyState==='complete'`);
 await api('/auth/logout','POST');await send('Page.reload');await login(2);await api('/__fixture/delivery/disabled','POST');await logout();await login(8);
 if(fallbackOnly){
  const incidentCount=(await api('/incidents?reporter_id=8')).body.length;
  const supportCount=(await api('/support/requests')).body.length;
  await click('Report an incident');await until(`document.querySelector('#inc-cat')?.options.length>1`);
  await ev(`document.querySelector('details.support-desk').open=true`);
  check('Internal fallback remains available',await ev(`!!document.querySelector('.report-form')`));
  check('Fallback requires explicit review consent',await ev(`document.querySelector('.report-form .send-btn').disabled`));
  await ev(`document.querySelector('#inc-cat').selectedIndex=1;document.querySelector('#inc-desc').value='Fictional internal reference: suspicious work document, no credentials shared';let checkbox=document.querySelector('.report-form .support-confirm input');checkbox.checked=true;checkbox.dispatchEvent(new Event('change'));`);
  await click('Report incident');await until(`!!document.querySelector('.report-confirm')`);
  check('Fallback preserves existing incident API',(await api('/incidents?reporter_id=8')).body.length===incidentCount+1);
  check('Fallback explicitly claims no email',await ev(`document.querySelector('.report-confirm').textContent.includes('No email was sent')`));
  check('Fallback creates no outbound request',(await api('/support/requests')).body.length===supportCount);
  await ev(`document.querySelector('.report-confirm').scrollIntoView({block:'center',behavior:'instant'})`);await shot('08-internal-only-fallback');
 }else{
 const beforeRequests=(await api('/support/requests')).body.length;
 await ev(`document.querySelector('.composer textarea').value='I clicked a phishing link';document.querySelector('.composer .send-btn').click()`);
 await until(`!!document.querySelector('.support-urgent')`);check('Urgent guidance appears in Assistant',await ev(`document.querySelector('.support-urgent').textContent.includes('immediately')`));
 check('No automatic report', (await api('/support/requests')).body.length===beforeRequests);
 await ev(`let nodes=document.querySelectorAll('.support-desk .support-field input');nodes[0].value='Clicked link; did not enter credentials';nodes[1].value='Today, work email';`);
 await click('Review support request');await until(`!!document.querySelector('.support-summary')`);
 check('Review shows verified identity and destination',await ev(`document.querySelector('.support-summary').textContent.includes('Sam Okonkwo')&&document.querySelector('.support-summary').textContent.includes('Security service desk')`));
 check('Explicit confirmation required',await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent==='Confirm support request').disabled`));await shot('01-reviewed-support-request');
 await click('Edit details before confirmation');await until(`!!document.querySelector('.support-field textarea')`);
 check('Employee can edit before confirming',true);
 await ev(`(()=>{let nodes=document.querySelectorAll('.support-desk .support-field input');nodes[0].value='No credentials entered';nodes[1].value='Today in email';})()`);await click('Review support request');await until(`!!document.querySelector('.support-summary')`);
 await ev(`let n=document.querySelector('.support-confirm input');n.checked=true;n.dispatchEvent(new Event('change'));`);await click('Confirm support request');await until(`document.querySelector('.support-status')?.textContent.includes('recorded internally')`);
 await click('Attempt approved handoff');await until(`document.querySelector('.support-status')?.textContent.includes('disabled')`);check('OFF mode states no email sent',await ev(`document.querySelector('.support-status').textContent.includes('no email sent')`));await shot('02-outbound-disabled');
 const rid=(await api('/support/requests')).body.find(r=>r.state==='disabled').id;
 await logout();await login(2);await route('#routing','.support-route-grid');
 check('Admin approved-route panel loads',await ev(`document.querySelector('#app').textContent.includes('Outbound delivery is OFF')`));
 await click('Validate security route');await until(`document.querySelector('#app').textContent.includes('no email sent')`);check('Route validation honestly sends no email',true);await shot('03-technical-routing-desktop');
 await api('/__fixture/delivery/accepted','POST');const dispatched=await api('/support/requests/'+rid+'/dispatch','POST');check('Mock adapter accepts handoff',dispatched.body.state==='accepted');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await delay(350);
 check('Routing mobile has no horizontal overflow',await ev(`document.documentElement.scrollWidth<=window.innerWidth+1`));await shot('04-technical-routing-mobile');
 await logout();await login(8);await route('#assist','.composer');await click('Report an incident');await until(`document.querySelector('#app').textContent.includes('Your support references')`);
 const rowText=await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.includes('accepted'))?.textContent`);await click(rowText);await until(`!!document.querySelector('.support-summary')`);
 check('Acceptance never claims delivery/ticket creation',await ev(`[...document.querySelectorAll('.support-status')].some(n=>n.textContent.includes('not confirmed'))`));
 check('Mobile support review has no overflow',await ev(`document.documentElement.scrollWidth<=window.innerWidth+1`));await ev(`[...document.querySelectorAll('.support-status')].find(n=>n.textContent.includes('not confirmed')).scrollIntoView({block:'center'})`);await shot('05-support-accepted-mobile');
 check('Employee routing API denied',(await api('/technical-routing/config')).status===403);
 for(const [hash,selector] of [['#library','.view'],['#messages','.view'],['#pulse','.view']]){await route(hash,selector);check('Existing navigation '+hash,await ev(`location.hash===${JSON.stringify(hash)}`));}
 await logout();check('Signed-out support reads denied',(await api('/support/requests')).status===401);
 }
 check('No browser runtime exceptions',errors.length===0);
}catch(e){checks.push({name:'Browser scenario completion',pass:false,error:String(e)});console.error(String(e));}
finally{fs.writeFileSync(out+(fallbackOnly?'/fallback-browser-results.json':'/support-browser-results.json'),JSON.stringify({checks,passed:checks.filter(c=>c.pass).length,failed:checks.filter(c=>!c.pass).length,errors},null,2));ws.close();}
process.exitCode=checks.some(c=>!c.pass)?1:0;
