// Isolated real BFF + browser UI with mocked Supabase provider; never live login.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const out=fileURLToPath(new URL('../../../semester_5/DeRexi_Week%209/evidence/',import.meta.url));
fs.mkdirSync(out+'screenshots',{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9230/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map(),checks=[],errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
function send(method,params={}){return new Promise((resolve,reject)=>{const current=++id,timer=setTimeout(()=>reject(Error('CDP timeout')),15000);pending.set(current,{resolve,reject,timer});ws.send(JSON.stringify({id:current,method,params}))})}
async function ev(expression){const x=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(x.exceptionDetails)throw Error(x.exceptionDetails.text);return x.result.value}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(exp){for(let i=0;i<150;i++){try{if(await ev(exp))return}catch{}await delay(100)}throw Error('Missing state: '+exp)}
function check(name,value){checks.push({name,status:value?'PASS':'FAIL'});console.log((value?'PASS ':'FAIL ')+name)}
async function shot(name){await ev(`document.querySelector('.lh-date').textContent='AUTH FIXTURE';document.querySelector('.js-recon-mode').textContent='ISOLATED FIXTURE · Provider mocked · No live Auth or database writes'`);await delay(800);const x=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(out+'screenshots/'+name+'.png',Buffer.from(x.data,'base64'))}
async function login(uid){await ev(`document.querySelector('#auth-email').value='fixture${uid}@example.invalid';document.querySelector('#auth-password').value='fixture-password';document.querySelector('.auth-form').requestSubmit()`);await until(`document.querySelector('#persona-select').value==='${uid}'&&!document.querySelector('#signout-btn').classList.contains('is-hidden')`)}
async function logout(){await ev(`document.querySelector('#signout-btn').click()`);await until(`!!document.querySelector('.auth-form input')`)}
await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
await send('Network.clearBrowserCookies');
await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
try{
 await send('Page.navigate',{url:'http://127.0.0.1:8029/ui/'});await until(`!!document.querySelector('#auth-password')`);
 check('Sign-in form is available without a persona bypass',await ev(`document.querySelector('#persona-select').disabled&&document.querySelector('.btn-recon').classList.contains('is-hidden')`));await shot('01-signin-fixture');
 await ev(`document.querySelector('#auth-email').value='fixture8@example.invalid';document.querySelector('#auth-password').value='wrong';document.querySelector('.auth-form').requestSubmit()`);
 await until(`document.querySelector('.auth-form [role=status]').textContent.includes('Sign-in failed')`);
 check('Failed login is generic and password is cleared',await ev(`document.querySelector('#auth-password').value===''`));
 await login(8);
 check('Employee signs in through a verified cookie session',await ev(`document.querySelector('#persona-select').value==='8'`));
 check('Authentication credentials are unavailable to browser JavaScript',await ev(`!document.cookie.includes('derexi_')&&!sessionStorage.getItem('derexi.accessToken')`));
 check('Production-style session cannot switch identities',await ev(`document.querySelector('#persona-select').disabled&&document.querySelector('.btn-recon').classList.contains('is-hidden')`));
 check('Direct employee Governance bypass is denied',await ev(`fetch('/governance/drafts').then(r=>r.status===403)`));
 await ev(`location.hash='#library'`);await until(`!!document.querySelector('.lib-grid')||!!document.querySelector('.lib-list')||document.querySelector('#app').textContent.includes('Unrelated fixture policy')`);
 check('Cookie session opens protected policy library',await ev(`document.querySelector('#app').textContent.includes('Employee Leave')`));await shot('02-employee-session-fixture');
 await logout();check('Logout clears visible identity data',await ev(`document.querySelector('#persona-select').textContent.trim()==='Sign-in required'`));
 check('Logged-out cookie cannot read APIs',await ev(`fetch('/me').then(r=>r.status===401)`));
 await login(4);await ev(`location.hash='#dashboard'`);await until(`document.querySelector('#app').textContent.includes('Policy health for your department')`);
 check('Policy Owner sees department-scoped dashboard',await ev(`fetch('/dashboard/policy-health').then(r=>r.json()).then(d=>d.scope==='department')`));await shot('03-owner-dashboard-fixture');
 await logout();await login(2);await ev(`location.hash='#dashboard'`);await until(`document.querySelector('#app').textContent.includes('Incident')`);
 await ev(`[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Incidents').click()`);
 await until(`!!document.querySelector('.inc-row')`);
 await ev(`document.querySelector('.inc-acts select').value='4';[...document.querySelectorAll('.inc-acts button')].find(b=>b.textContent==='Assign').click()`);
 await until(`document.querySelector('.inc-meta').textContent.includes('Maya Patel')`);
 check('Admin assignment control makes a real authorized API change',await ev(`fetch('/incidents').then(r=>r.json()).then(rows=>rows[0].assigned_to===4)`));
 await shot('04-admin-incident-fixture');
 const cookies=await send('Network.getCookies',{urls:['http://127.0.0.1:8029/','http://127.0.0.1:8029/auth']});
 const attributes=cookies.cookies.filter(c=>c.name.startsWith('derexi_')).map(({name,httpOnly,secure,sameSite,path})=>({name,httpOnly,secure,sameSite,path}));
 fs.writeFileSync(out+'browser-cookie-attributes.json',JSON.stringify({mode:'HTTP loopback test fixture; production Secure cookies verified separately in HTTPS API tests',attributes},null,2));
 check('Browser session cookies are HttpOnly and SameSite Strict',attributes.length===2&&attributes.every(c=>c.httpOnly&&c.sameSite==='Strict'));
 await logout();check('Logout removes stale activity notices',await ev(`document.querySelectorAll('.js-toasts .toast').length===0`));await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});await shot('05-mobile-signin-fixture');
 check('Sign-in has no mobile page overflow',await ev(`document.documentElement.scrollWidth===document.documentElement.clientWidth`));
 check('Browser workflow has no runtime errors',errors.length===0);
}catch(error){checks.push({name:'Browser workflow completion',status:'FAIL',detail:String(error)});console.log(String(error));console.log(await ev('document.body.innerText.slice(0,1800)'))}
finally{fs.writeFileSync(out+'browser-results.json',JSON.stringify({mode:'Isolated real BFF + SQLite + mocked provider; HTTP loopback, no production login',checks,errors},null,2));ws.close()}
console.log(`${checks.filter(c=>c.status==='PASS').length} passed, ${checks.filter(c=>c.status==='FAIL').length} failed`);process.exit(checks.some(c=>c.status==='FAIL')?1:0);
