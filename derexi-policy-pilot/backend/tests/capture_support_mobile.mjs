// Targeted read-only reframe of an existing mock-accepted reference, no new send.
import fs from 'node:fs';
const out=process.env.DEREXI_SPRINT_EVIDENCE;
const tabs=await(await fetch('http://127.0.0.1:9241/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}}};
function send(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function ev(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;}
async function wait(expr){for(let i=0;i<100;i++){if(await ev(expr))return;await new Promise(r=>setTimeout(r,100));}throw Error('Missing '+expr);}
try{
 await send('Network.enable');await send('Network.setCacheDisabled',{cacheDisabled:true});await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await send('Page.navigate',{url:'http://127.0.0.1:8041/ui/'});await wait(`!!document.querySelector('#app')`);
 await ev(`fetch('/auth/logout',{method:'POST',headers:{'X-Derexi-Request':'1'}})`);await send('Page.reload');await wait(`!!document.querySelector('#auth-email')`);
 await ev(`document.querySelector('#auth-email').value='fixture8@example.invalid';document.querySelector('#auth-password').value='fixture-password';document.querySelector('.auth-form').requestSubmit()`);
 await wait(`!document.querySelector('#auth-email')`);await ev(`location.hash='#assist'`);await wait(`!!document.querySelector('#app .view')`);
 await ev(`[...document.querySelectorAll('#app .tabs button')].find(b=>b.textContent==='Report an incident').click()`);
 await wait(`[...document.querySelectorAll('#app button')].some(b=>b.textContent.includes('accepted'))`);
 await ev(`[...document.querySelectorAll('#app button')].find(b=>b.textContent.includes('accepted')).click()`);
 await wait(`[...document.querySelectorAll('.support-status')].some(n=>n.textContent.includes('not confirmed'))`);
 await ev(`(()=>{const n=[...document.querySelectorAll('.support-status')].find(n=>n.textContent.includes('not confirmed'));n.scrollIntoView({block:'center',behavior:'instant'});const tag=document.createElement('div');tag.style.cssText='position:fixed;bottom:0;left:0;right:0;padding:6px;background:#251d18;color:white;font:11px monospace;z-index:99999';tag.textContent='ISOLATED DEMONSTRATION · Mock email acceptance only';document.body.appendChild(tag);})()`);
 await new Promise(r=>setTimeout(r,250));
 const visible=await ev(`(()=>{const r=[...document.querySelectorAll('.support-status')].find(n=>n.textContent.includes('not confirmed')).getBoundingClientRect();return r.top>=0&&r.bottom<innerHeight-35;})()`);
 const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(out+'/screenshots/07-final-acceptance-mobile.png',Buffer.from(shot.data,'base64'));
 fs.writeFileSync(out+'/mobile-capture-check.json',JSON.stringify({passed:visible?1:0,failed:visible?0:1,notice:'Targeted read-only reframing; existing mock-accepted record; no new send'},null,2));
 console.log('Mobile acceptance notice visible:',visible);process.exitCode=visible?0:1;
}finally{ws.close();}
