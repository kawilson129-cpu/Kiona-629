// Verify only the new static coursework demo. No application/API server or fetch mock.
// Dedicated Chrome: CDP 9251, .runtime/demo-browser inside this course folder.
// Run from repo root: node html_1/verify_demo.mjs
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const assignment = path.join(root, 'Assignment 4 - Hyperlinks');
const output = path.join(root, 'evidence', 'browser-verification.json');
if (fs.existsSync(output)) throw Error('Preserve prior browser evidence; use a separately reviewed new output for reruns');
const browserInfo = await (await fetch('http://127.0.0.1:9251/json/version')).json();
const tabs = await (await fetch('http://127.0.0.1:9251/json/list')).json();
const ws = new WebSocket(tabs.find(v => v.type === 'page').webSocketDebuggerUrl);
await new Promise((resolve,reject) => { ws.onopen = resolve; ws.onerror = reject; });
let sequence=0;
const pending=new Map(), checks=[], exceptions=[];
ws.onmessage = event => {
  const m=JSON.parse(event.data);
  if(m.id){const job=pending.get(m.id);if(!job)return;pending.delete(m.id);clearTimeout(job.timer);m.error?job.reject(Error(m.error.message)):job.resolve(m.result);}
  else if(m.method==='Runtime.exceptionThrown')exceptions.push(m.params.exceptionDetails.text);
};
function send(method,params={}){return new Promise((resolve,reject)=>{const id=++sequence;const timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method));},12000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(expression){for(let i=0;i<100;i++){try{if(await evaluate(expression))return;}catch{}await sleep(50);}throw Error('Demo state not reached '+expression);}
function check(name,ok,detail){checks.push({name,status:ok?'PASS':'FAIL',detail});}
try{
  await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
  await send('Network.setBlockedURLs',{urls:['http://*','https://*']});
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:pathToFileURL(path.join(assignment,'index.html')).href});
  await until(`document.readyState==='complete'&&!!document.getElementById('publication-link')`);
  check('Initial document is the coursework reading desk',await evaluate(`document.title==='DeRexi · Reading desk · Coursework demo'`));
  const link=await evaluate(`({href:document.getElementById('publication-link').getAttribute('href'),current:location.pathname,fragment:location.hash})`);
  check('Actual DOM anchor has a separate-file href rather than a hash',link.href==='publication.html'&&!link.fragment,link);
  await evaluate(`document.getElementById('publication-link').click()`);
  await until(`document.readyState==='complete'&&!!document.getElementById('return-link')`);
  const destination=await evaluate(`({title:document.title,path:location.pathname,fragment:location.hash,heading:document.querySelector('h1').textContent})`);
  check('Click opens a different HTML document with the retained article heading',destination.path!==link.current&&destination.path.endsWith('/publication.html')&&!destination.fragment&&destination.heading==='Reserve Requirements of Depository Institutions',destination);
  const png=await send('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync(path.join(assignment,'evidence','demo-separate-page.png'),Buffer.from(png.data,'base64'));
  await evaluate(`document.getElementById('return-link').click()`);
  await until(`document.readyState==='complete'&&!!document.getElementById('publication-link')`);
  check('Return anchor navigates back to the original separate file',await evaluate(`location.pathname===${JSON.stringify(link.current)}`));
  check('Demo contains no API scripts and no runtime exceptions',await evaluate(`document.querySelectorAll('script').length===0`)&&exceptions.length===0,exceptions);
}catch(error){check('Demo verification completes',false,String(error));}
finally{
  fs.writeFileSync(output,JSON.stringify({timestamp:new Date().toISOString(),
    scope:'NEW static coursework-demo navigation only. Original DeRexi/API and external publisher not visited. HTTP/HTTPS blocked for the page.',
    browser:browserInfo.Browser,checks,passed:checks.filter(c=>c.status==='PASS').length,failed:checks.filter(c=>c.status==='FAIL').length,
    screenshot:'Assignment 4 - Hyperlinks/evidence/demo-separate-page.png',
    screenshot_label:'New static coursework DEMONSTRATION, not production app or original publisher'},null,2)+'\n');
  ws.close();
}
console.log(JSON.stringify({passed:checks.filter(c=>c.status==='PASS').length,failed:checks.filter(c=>c.status==='FAIL').length}));
if(checks.some(c=>c.status==='FAIL'))process.exitCode=1;
