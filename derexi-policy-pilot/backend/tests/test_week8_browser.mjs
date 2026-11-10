// Existing CDP approach; no browser dependency. Uses serve_week8_fixture.py only.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const base='http://127.0.0.1:8028';
const output=fileURLToPath(new URL('../../docs/week8/evidence/',import.meta.url));
fs.mkdirSync(output+'screenshots',{recursive:true});
const tabs=await(await fetch(process.env.CDP_URL||'http://127.0.0.1:9238/json/list')).json();
const tab=tabs.find(t=>t.url==='about:blank')||tabs.find(t=>t.url.startsWith(base));
if(!tab)throw Error('Dedicated fixture browser tab required');
const ws=new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let seq=0;const pending=new Map(),checks=[],errors=[];
ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);};
function send(method,params={}){return new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method));},15000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expr){for(let i=0;i<100;i++){try{if(await ev(expr))return;}catch{}await delay(100);}throw Error('Missing '+expr);}
function check(name,value){checks.push({name,pass:!!value});console.log((value?'PASS ':'FAIL ')+name);if(!value)throw Error(name);}
async function click(text){await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()===${JSON.stringify(text)}).click()`);}
async function navigate(uid,hash='governance'){
 await send('Page.navigate',{url:base+'/ui/?as='+uid+'&w8='+Date.now()+'#'+hash});
 await until(`document.readyState==='complete'&&document.querySelector('#persona-select')?.value==='${uid}'`);
 await until(`!!document.querySelector('#app .view')`);
}
async function screenshot(name){await ev(`document.querySelector('.js-recon-mode').textContent='LOCAL WEEK 8 FIXTURE · Illustrative data · No Supabase writes';Promise.all(document.querySelector('#app').getAnimations({subtree:true}).filter(a=>a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))`);const s=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(output+'screenshots/'+name+'.png',Buffer.from(s.data,'base64'));}
async function token(uid){return(await(await fetch(base+'/dev-auth/token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:uid})})).json()).access_token;}
async function api(path,uid,method='GET',body){const r=await fetch(base+path,{method,headers:{Authorization:'Bearer '+await token(uid),'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error('Fixture API '+r.status+' '+await r.text());return r.json();}
await send('Runtime.enable');await send('Page.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
try{
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
 await navigate(4);await until(`!!document.querySelector('.gov-metrics')`);
 check('Owner sees Dashboard and Governance',await ev(`[...document.querySelectorAll('.js-gov-link')].every(n=>!n.classList.contains('is-hidden'))`));
 check('Owner has no final approval queue',await ev(`!document.querySelector('.gov-metrics').textContent.includes('Final Approval Queue')`));
 await screenshot('01-owner-governance-overview');
 await click('Create a policy draft');await until(`!!document.querySelector('textarea[name=body]')`);
 await ev(`document.querySelector('[name=title]').value='Customer Safeguards — Week 8';document.querySelector('[name=body]').value='Protect customer records. Escalate uncertain handling to Compliance. Review exceptions before releasing information.';document.querySelector('[name=summary]').value='Controlled guidance with independent review.';document.querySelector('.gov-form').requestSubmit();`);
 await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);
 const id=Number((await ev('location.hash')).split('/')[1]);
 await click('Submit for peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending peer review')`);
 check('Author submits using same-department reviewer',true);
 // First eligible peer is user 9 in fixture ordering (user 7 is in another department).
 const d=await api('/governance/drafts/'+id,4);const peer=d.reviewer_id;
 await navigate(peer,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);
 await screenshot('02-independent-peer-review');
 await click('Request changes');check('Missing rejection/revision comment gets focused',await ev(`document.activeElement.name==='comment'`));
 await ev(`document.querySelector('[name=comment]').value='Specify how to document exceptions.'`);
 await click('Request changes');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('revisions requested')`);
 await navigate(4,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);await click('Edit working copy');
 await ev(`document.querySelector('[name=body]').value+=' Record exceptions with the department owner.';document.querySelector('.gov-form').requestSubmit();`);
 await until(`!!document.querySelector('.gov-review')`);await click('Submit for peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending peer review')`);
 await navigate(peer,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);await click('Approve peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending final approval')`);
 await navigate(1);await until(`!!document.querySelector('.gov-metrics')`);
 check('Administrator sees final approval queue',await ev(`document.querySelector('.gov-metrics').textContent.includes('Final Approval Queue')`));
 await screenshot('03-admin-approval-queue');
 await navigate(1,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);await click('Grant final approval');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('approved pending publication')`);
 await screenshot('04-ready-for-publication');await click('Publish approved version');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('published')`);
 check('Administrator publishes reviewed policy through UI',true);
 const published=await api('/governance/drafts/'+id,1);
 check('Approval history and comparison present',await ev(`document.querySelectorAll('.gov-history li').length>=8&&document.querySelectorAll('.gov-diff pre').length===2`));
 await ev(`document.querySelector('.gov-history').scrollIntoView({block:'end'})`);await screenshot('05-decision-audit-history');
 await navigate(4,'pulse');await until(`!!document.querySelector('.gov-pulse-start')`);await click('Propose policy action');await until(`!!document.querySelector('.gov-source')&&!!document.querySelector('.gov-form')`);
 check('Pulse transfers article context without auto-saving',await ev(`document.querySelector('.gov-source').textContent.includes('FDIC')&&document.querySelector('[name=body]').value===''`));
 await screenshot('06-pulse-source-working-copy');
 // Actual revision from published policy, compared with its live baseline.
 let revision=await api('/governance/drafts',4,'POST',{policy_id:published.policy_id,department_id:1,title:published.title,body:published.body+'\nProposed revision for department review.',version_no:'2.0',source:{url:'https://www.fdic.gov/news/financial-institution-letters/fixture',title:'Illustrative regulatory source',published:'2026-11-01',context:'FDIC · supervisory guidance · synthetic fixture'}});
 await navigate(4,'governance/'+revision.id);await until(`!!document.querySelector('.gov-diff')`);
 check('Revision comparison retains published base',await ev(`document.querySelector('.gov-diff').textContent.includes('Previous content')&&!!document.querySelector('.gov-added')`));
 await ev(`document.querySelector('.gov-comparison').scrollIntoView()`);await screenshot('07-version-comparison');
 for(const width of [1280,1024,820,390]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<500});
  await navigate(4,'governance/'+revision.id);await until(`!!document.querySelector('.gov-review')`);
  check('Governance no horizontal overflow at '+width,await ev('document.documentElement.scrollWidth<=innerWidth'));
  if(width===390){await ev(`document.querySelector('.gov-review').scrollIntoView({block:'start'})`);await screenshot('08-mobile-review-workspace');}
 }
 await navigate(8,'governance/'+id);await until(`!!document.querySelector('.ask-surface')||!!document.querySelector('.assist')||document.querySelector('#app')?.textContent.includes('How can')||document.querySelector('#app')?.textContent.includes('Ask')`);
 check('Employee direct governance URL renders no workspace',await ev(`!document.querySelector('.lifecycle')&&[...document.querySelectorAll('.js-gov-link')].every(n=>n.classList.contains('is-hidden'))`));
 await screenshot('09-employee-access-boundary');
 await navigate(8,'dashboard');await until(`!!document.querySelector('#app .view')`);check('Employee direct Dashboard URL renders no health data',await ev(`!document.querySelector('#app').textContent.includes('Health of the')&&!document.querySelector('.lifecycle')`));
 await navigate(8,'pulse');await until(`!!document.querySelector('.pulse-lead')`);check('Employee Pulse has no governance action',await ev(`!document.querySelector('.gov-pulse-start')`));
 await navigate(8,'library');await until(`document.querySelector('#app')?.textContent.includes('Customer Safeguards')`);check('Employee Library retains published policy',true);
 await navigate(4,'dashboard');await until(`document.querySelector('#app')?.textContent.includes('Health of the')`);check('Existing Policy Health Dashboard preserved',true);
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});await screenshot('10-policy-health-dashboard');
 await navigate(4);await until(`!!document.querySelector('.gov-metrics')`);await ev(`document.querySelector('.js-notify').click()`);await until(`!!document.querySelector('.js-notify-list .notify-item')`);await ev(`document.querySelector('.js-notify-list .notify-item').click()`);await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);check('Week 7 bell deep-links into governance review',true);await screenshot('11-governance-notification-destination');
 check('No browser runtime exceptions',errors.length===0);
}catch(error){checks.push({name:'Browser workflow completion',pass:false,detail:error.message});console.error(error);await screenshot('attempt-failure');process.exitCode=1;}
finally{fs.writeFileSync(output+'browser-results.json',JSON.stringify({checks,errors},null,2)+'\n');ws.close();}
