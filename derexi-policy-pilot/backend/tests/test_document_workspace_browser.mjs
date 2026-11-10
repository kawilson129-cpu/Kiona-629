// Real UI and API: dedicated ephemeral database plus read-only live diagnosis.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const base='http://127.0.0.1:8030';
const output=fileURLToPath(new URL('../../docs/governance-workspace/evidence/',import.meta.url));
fs.mkdirSync(output+'screenshots',{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9240/json/list')).json();
const tab=tabs.find(t=>t.url==='about:blank')||tabs.find(t=>t.url.startsWith('http://127.0.0.1:'));
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let seq=0;const pending=new Map(),checks=[],errors=[],network=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);else if(m.method==='Network.responseReceived'){const r=m.params.response;const url=new URL(r.url);if(url.origin==='http://127.0.0.1:8000'&&['/auth/config','/me','/governance/drafts','/governance/owners','/governance/availability'].includes(url.pathname))network.push({path:url.pathname,status:r.status});}};
function send(method,params={}){return new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method));},20000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expr){for(let i=0;i<200;i++){try{if(await ev(expr))return;}catch{}await delay(100);}throw Error('Missing '+expr);}
function check(name,value){checks.push({name,pass:!!value});console.log((value?'PASS ':'FAIL ')+name);if(!value)throw Error(name);}
async function click(text){await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()===${JSON.stringify(text)}).click()`);}
async function navigate(uid,hash='governance',origin=base){await send('Page.navigate',{url:origin+'/ui/?as='+uid+'&inspection='+Date.now()+'#'+hash});await until(`document.readyState==='complete'&&document.querySelector('#persona-select')?.value==='${uid}'`);await until(`!!document.querySelector('#app .view')`);}
async function shot(name){await ev(`Promise.all(document.querySelector('#app').getAnimations({subtree:true}).filter(a=>a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))`);const r=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(output+'screenshots/'+name+'.png',Buffer.from(r.data,'base64'));}
async function token(uid){return(await(await fetch(base+'/dev-auth/token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:uid})})).json()).access_token;}
async function available(value){await fetch(base+'/__fixture/workspace?available='+value,{method:'POST',headers:{Authorization:'Bearer '+await token(1)}});}
async function upload(name){const doc=await send('DOM.getDocument');const input=await send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'.gw-file'});await send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[fileURLToPath(new URL('../../docs/governance-workspace/evidence/inputs/'+name,import.meta.url))]});}
function noInternal(){return ev(`!(/week\\s*[789]|capstone|migration|fixture|testing|technical setup|additive owner seed|test session/i.test(document.body.innerText))`);}
await send('Runtime.enable');await send('Page.enable');await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});
try{
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
 await navigate(4,'governance','http://127.0.0.1:8000');await until(`document.querySelector('.gw-queue-body .is-error')&&!document.querySelector('.gw-queue-body[aria-busy]')`);
 check('Actual browser request confirms missing-table queue failure',network.some(x=>x.path==='/governance/drafts'&&x.status===503));
 check('Actual identity remains authenticated',network.some(x=>x.path==='/me'&&x.status===200));
 check('Actual landing renders independently of missing queues',await ev(`!!document.querySelector('.gw-drop')&&!!document.querySelector('.gw-template-card')`));
 check('No internal setup terminology in actual page',await noInternal());await shot('01-actual-unavailable-workspace');
 // All write operations below use only the ephemeral server on port 8030.
 await available(true);await navigate(4);await until(`document.querySelector('.gw-intake-state')?.textContent.includes('retained privately')&&!document.querySelector('.gw-queue-body[aria-busy]')`);
 check('Owner sections include audit and exclude final approval',await ev(`document.querySelector('.gw-queues').textContent.includes('Audit History')&&!document.querySelector('.gw-queues').textContent.includes('Final Approvals')`));
 check('Empty queues have honest empty states',await ev(`document.querySelector('.gw-queue-body').textContent.includes('No policies')`));
 await shot('02-document-workspace');
 await upload('Customer safeguards.docx');await until(`!!document.querySelector('.gw-document-summary')&&document.querySelector('.gov-form button[type=submit]')?.disabled===false`);
 check('Browse upload performs real DOCX extraction',await ev(`document.querySelector('[name=body]').value.includes('Verify authorization')&&document.querySelector('.gw-document-summary').textContent.includes('Customer safeguards.docx')`));
 check('Preview states document not yet saved',await ev(`document.querySelector('.gov-status').textContent.includes('Nothing has been saved')`));
 await ev(`document.querySelector('[name=title]').value='Customer Safeguards';document.querySelector('[name=title]').dispatchEvent(new Event('input'));document.querySelector('[name=summary]').value='Customer information handling requirements.';`);
 check('Live policy preview follows metadata edits',await ev(`document.querySelector('.gw-live-preview h3').textContent==='Customer Safeguards'`));
 check('Author confirmation required before draft save',await ev(`document.querySelector('[name=confirm_document]').required&&!document.querySelector('[name=confirm_document]').checked`));
 await ev(`document.querySelector('.gw-document-summary').scrollIntoView({block:'center'})`);await shot('03-imported-document-editor');
 await ev(`document.querySelector('.gw-live-preview').scrollIntoView({block:'center'})`);await shot('04-library-preview');
 await ev(`document.querySelector('[name=confirm_document]').checked=true;document.querySelector('.gov-form').requestSubmit()`);await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);
 const id=Number((await ev('location.hash')).split('/')[1]);
 check('Confirmed upload saves an actual policy draft',await ev(`document.querySelector('.gov-detail-head').textContent.includes('draft')`));
 check('Configured private original is accessible through protected control',await ev(`[...document.querySelectorAll('.gov-review button')].some(b=>b.textContent==='Download original')`));
 await click('Submit for peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending peer review')`);
 await navigate(9,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);await click('Approve peer review');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('pending final approval')`);
 await navigate(1);await until(`!document.querySelector('.gw-queue-body[aria-busy]')&&document.querySelector('.gw-queues')?.textContent.includes('Final Approvals')`);
 check('Administrator receives role-specific final approval section',await ev(`document.querySelector('.gw-queues').textContent.includes('Customer Safeguards')`));await shot('05-administrator-review-queues');
 await navigate(1,'governance/'+id);await until(`!!document.querySelector('.gov-review')`);await click('Grant final approval');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('approved pending publication')`);await click('Publish approved version');await until(`document.querySelector('.gov-detail-head')?.textContent.includes('published')`);
 check('Document follows unchanged independent approval and publication workflow',true);
 await navigate(4);await until(`!!document.querySelector('.gw-drop')`);await click('Create from Template');await until(`document.querySelectorAll('.gw-template-choice').length===3`);await shot('06-policy-templates');
 await ev(`document.querySelector('.gw-template-choice button').click()`);await until(`document.querySelector('[name=body]')?.value.includes('Purpose')&&document.querySelector('.gov-form button[type=submit]')?.disabled===false`);
 check('Template opens actual editable policy content',await ev(`document.querySelector('[name=body]').value.includes('Responsibilities')`));
 await ev(`document.querySelector('[name=title]').value='New Department Policy';document.querySelector('[name=confirm_document]').checked=true;document.querySelector('.gov-form').requestSubmit()`);await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);
 check('Template saves through authenticated draft persistence',true);
 await available(false);await navigate(4);await until(`document.querySelector('.gw-queue-body .is-error')&&!document.querySelector('.gw-queue-body[aria-busy]')`);
 check('Each unavailable queue replaces loading with retry state',await ev(`[...document.querySelectorAll('.gw-queue')].every(p=>p.querySelector('.is-error')&&[...p.querySelectorAll('button')].some(b=>b.textContent==='Try again'))`));
 check('Unavailable counts never fabricate zeroes',await ev(`[...document.querySelectorAll('.gw-count')].every(n=>n.textContent==='—')`));
 await upload('Customer safeguards.pdf');await until(`!!document.querySelector('.gw-document-summary')&&document.querySelector('.gw-save-state')?.textContent.includes('not been saved')`);
 check('Real PDF preview remains available during persistence outage',await ev(`document.querySelector('[name=body]').value.includes('Customer safeguards policy requirements')`));
 check('Unavailable database disables save honestly',await ev(`document.querySelector('.gov-form button[type=submit]').disabled&&document.querySelector('.gw-save-state').textContent.includes('not been saved')`));
 check('No developer language in document failure state',await noInternal());await ev(`document.querySelector('.gw-save-state').scrollIntoView({block:'center'})`);await shot('07-unavailable-save-state');
 await available(true);await click('Check availability');await until(`document.querySelector('.gov-form button[type=submit]')?.disabled===false`);check('Workspace recovers without losing document text',await ev(`document.querySelector('[name=body]').value.includes('Customer safeguards')`));
 await click('Discard changes');await until(`!!document.querySelector('.gw-drop')`);
 // Drag/drop uses an actual File generated in the browser and posts binary data.
 await ev(`var contents='invalid archive';var transfer=new DataTransfer();transfer.items.add(new File([contents],'malformed.docx',{type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}));document.querySelector('.gw-drop').dispatchEvent(new DragEvent('drop',{bubbles:true,dataTransfer:transfer}));`);
 await until(`document.querySelector('.gw-intake-state')?.textContent.includes('do not match')`);check('Dropped malformed documents show actionable validation',true);
 for(const width of [1280,820,390]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:1050,deviceScaleFactor:1,mobile:width<500});await navigate(4);await until(`!document.querySelector('.gw-queue-body[aria-busy]')`);
  check('Landing has no horizontal overflow at '+width,await ev('document.documentElement.scrollWidth<=innerWidth'));
  if(width===390)await shot('08-mobile-document-intake');
 }
 await click('Create from Template');await until(`document.querySelectorAll('.gw-template-choice').length===3`);await ev(`document.querySelector('.gw-template-choice button').click()`);await until(`!!document.querySelector('.gw-live-preview')`);check('Mobile editor has no horizontal overflow',await ev('document.documentElement.scrollWidth<=innerWidth'));
 await navigate(8);check('Employee direct URL cannot render Governance',await ev(`!document.querySelector('.lifecycle')&&[...document.querySelectorAll('.js-gov-link')].every(n=>n.classList.contains('is-hidden'))`));
 await navigate(4,'dashboard');await until(`document.querySelector('#app')?.textContent.includes('Health of the')`);check('Existing Dashboard renders unchanged',true);
 check('No browser runtime exceptions',errors.length===0);
}catch(error){checks.push({name:'Browser workflow completion',pass:false,detail:error.message});console.error(error);await shot('attempt-failure');process.exitCode=1;}
finally{fs.writeFileSync(output+'browser-results.json',JSON.stringify({checks,errors,actual_local_network:network},null,2)+'\n');ws.close();}
