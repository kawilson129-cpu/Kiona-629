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
 await available(true);await navigate(4);await until(`document.querySelector('.gw-intake-state')?.textContent.includes('retained privately')`);
 await upload('Customer safeguards.docx');await until(`!!document.querySelector('.gw-document-summary')&&document.querySelector('.gov-form button[type=submit]')?.disabled===false`);
 const before=await ev(`document.querySelector('[name=body]').value`);
 await ev(`var policy=document.querySelector('.gov-form select');policy.value='1';policy.dispatchEvent(new Event('change'));`);
 await until(`document.querySelector('[name=title]')?.value==='Information handling'&&document.querySelector('[name=version_no]')?.value===''`);
 check('Selecting an existing policy preserves uploaded replacement content',before===await ev(`document.querySelector('[name=body]').value`));
 await ev(`document.querySelector('[name=version_no]').value='2.0';document.querySelector('[name=confirm_document]').checked=true;document.querySelector('.gw-live-preview').scrollIntoView({block:'center'});`);
 await shot('09-imported-revision-preview');
 await ev(`document.querySelector('.gov-form').requestSubmit()`);await until(`location.hash.startsWith('#governance/')&&!!document.querySelector('.gov-review')`);
 check('Imported revision persists as a reviewed working copy',await ev(`document.querySelector('.gov-detail-head').textContent.includes('draft')`));
 check('Revision comparison shows published guidance and uploaded replacement',await ev(`document.querySelector('.gov-diff').textContent.includes('Contact your department owner')&&document.querySelector('.gov-diff').textContent.includes('Verify authorization')`));
 await ev(`document.querySelector('.gov-comparison').scrollIntoView({block:'center'})`);await shot('10-published-versus-imported-revision');
 check('Revision browser has no runtime exceptions',errors.length===0);
}catch(error){checks.push({name:'Revision workflow completion',pass:false,detail:error.message});console.error(error);await shot('attempt-revision-failure');process.exitCode=1;}
finally{fs.writeFileSync(output+'revision-browser-results.json',JSON.stringify({checks,errors},null,2)+'\n');ws.close();}