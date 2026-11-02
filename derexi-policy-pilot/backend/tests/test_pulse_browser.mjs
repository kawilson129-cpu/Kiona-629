// Read-only Chrome CDP verification; simulated responses are labeled in filenames.
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const base=process.env.PULSE_TEST_URL || 'http://127.0.0.1:8013';
const tabs=await (await fetch('http://127.0.0.1:9222/json/list')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let id=0;const pending=new Map(), errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params)};
function send(method,params={}){return new Promise((resolve,reject)=>{setTimeout(()=>reject(Error('CDP timeout '+method+' '+JSON.stringify(params).slice(0,250))),20000);const i=++id;pending.set(i,{resolve,reject});ws.send(JSON.stringify({id:i,method,params}))})}
async function ev(expression){const x=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(x.exceptionDetails)throw x.exceptionDetails;return x.result.value}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(exp){for(let i=0;i<120;i++){if(await ev(exp))return;await sleep(500)}throw Error('Timeout '+exp)}
const shots=process.env.PULSE_SCREENSHOTS || fileURLToPath(new URL('../../docs/compliance-assignment-2/screenshots/phase3', import.meta.url));fs.mkdirSync(shots,{recursive:true});
async function shot(name,selector){if(selector)await ev(`document.querySelector(${JSON.stringify(selector)}).scrollIntoView({block:'start'})`);await sleep(200);const s=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(shots+'/'+name+'.png',Buffer.from(s.data,'base64'))}
await send('Runtime.enable');await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:base+'/ui/#pulse'});await send('Page.reload',{ignoreCache:true});await sleep(1000);await until('document.readyState === "complete"');
await ev("localStorage.setItem('derexi.personaId','8')");await send('Page.reload',{ignoreCache:true});await sleep(1200);await until('!!document.querySelector(".pulse-lead")');
console.log('live DOM loaded');const data=await (await fetch(base+'/api/pulse?limit=60')).json();fs.writeFileSync('/private/tmp/pulse-live-data.json',JSON.stringify(data));
const log={sources:data.sources,articles:data.articles.length,errors};
log.initial=await ev(`({title:document.querySelector('.pulse-title').textContent,cards:document.querySelectorAll('.pulse-mosaic article,.pulse-feed article').length,radar:document.querySelectorAll('.radar-entry').length,lead:document.querySelector('.lead-title').textContent,links:[...document.querySelectorAll('.pulse-view a')].every(a=>a.href.startsWith('https://')&&a.rel==='noopener noreferrer'&&a.target==='_blank')})`);
await shot('01-masthead-featured');await shot('12-featured-story','.pulse-lead');await shot('02-editorial-mosaic','.pulse-spotlight');await shot('03-radar','.pulse-radar');await shot('04-intelligence-desk','.pulse-river');
// Exhaustive cross-product verifies visible counts and focus for both facets.
if(log.initial.cards!==data.articles.length || !log.initial.links)throw Error('Article/link integrity failed');
if(log.initial.lead!==data.articles.slice().sort((a,b)=>b.score-a.score||b.published.localeCompare(a.published)||b.title.localeCompare(a.title))[0].title)throw Error('Lead rank failed');
log.filters=[];for(const topic of ['All Updates','Banking & Finance','Regulations','Cybersecurity','Privacy & Data Protection','Supervisory Guidance'])for(const type of ['All Types','Final Rules','Proposed Rules','Notices','Guidance','Standards Drafts','General News']){
 const r=await ev(`(()=>{function click(d,v){[...document.querySelectorAll('[data-facet]')].find(b=>b.dataset.facet===d&&b.dataset.value===v).click()}click('filter',${JSON.stringify(topic)});click('type',${JSON.stringify(type)});const summary=document.querySelector('.pulse-results p').textContent;const n=Number(summary.split(' ')[0]);return {topic:${JSON.stringify(topic)},type:${JSON.stringify(type)},count:n,cards:document.querySelectorAll('.pulse-mosaic article,.pulse-feed article').length,focused:document.activeElement.dataset.value===${JSON.stringify(type)},counts:[...document.querySelectorAll('[data-facet]')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>Number(b.querySelector('.pchip-count').textContent))}})()`);
 if(r.count!==r.cards||!r.focused||r.counts.some(n=>n!==r.count))throw Error(JSON.stringify(r));log.filters.push(r);
}
await ev(`[...document.querySelectorAll('[data-facet]')].find(b=>b.dataset.value==='Banking & Finance').click();[...document.querySelectorAll('[data-facet]')].find(b=>b.dataset.value==='Final Rules').click()`);await shot('05-combined-filters','.pulse-filter-group');
await ev(`document.querySelector('.pulse-results button').click()`);
log.responsive=[];for(const width of [1440,1280,1024,820,390]){await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});await ev('window.scrollTo(0,0)');await sleep(200);log.responsive.push(await ev(`({width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,deskColumns:getComputedStyle(document.querySelector('.pulse-feed')).gridTemplateColumns})`));if(width===820||width===390)await shot('06-responsive-'+width);if(width===390)await shot('07-mobile-mosaic','.pulse-spotlight')}
if(log.responsive.some(r=>r.overflow!==0))throw Error('Horizontal page overflow');
// Render the isolated module with simulated responses; the full app remains untouched.
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
async function fixture(body,status=200){await ev(`(async()=>{window.fetch=async()=>({ok:${status===200},status:${status},json:async()=>(${JSON.stringify(body)})});await import('/ui/pulse.js?test='+Math.random());const app=document.querySelector('#app');app.replaceChildren();PulseView.render(app);})()`);await sleep(200)}
log.states={};console.log('responsive done');await fixture({...data,articles:[],radar:[]});log.states.empty=await ev(`document.querySelector('#app').textContent.includes('No updates are available')`);await shot('08-empty-simulated','#app');
await fixture({},503);log.states.error=await ev(`document.querySelector('#app').textContent.includes('Pulse could not be reached')`);await shot('09-error-simulated','#app');
const bad={...data,articles:[{...data.articles[0],title:'<img src=x onerror="window.pulseXss=1">',summary:'<script>window.pulseXss=1</script>',url:'javascript:alert(1)'}],radar:[]};await fixture(bad);log.states.xss=await ev(`!window.pulseXss && !document.querySelector('.pulse-view img,.pulse-view script,.pulse-view a[href^="javascript:"]')`);
await fixture({...data,sources:{...data.sources,FDIC:{ok:false,count:0,error:'Simulated timeout',stale:true}}});log.states.degraded=await ev(`document.querySelector('.is-down').textContent.includes('showing last good fetch')`);await shot('10-degraded-simulated','.pulse-sources');
await ev(`(async()=>{window.fetch=()=>new Promise(()=>{});await import('/ui/pulse.js?loading='+Math.random());document.querySelector('#app').replaceChildren();PulseView.render(document.querySelector('#app'))})()`);log.states.loading=await ev(`!!document.querySelector('[aria-busy="true"]')`);await shot('11-loading-simulated','#app');
await send('Page.reload',{ignoreCache:true});await sleep(1000);await until('!!document.querySelector(".pulse-lead")');
console.log('states and filters complete');log.navigation=[];for(const hash of ['assist','library','messages','governance','pulse']){await ev(`location.hash=${JSON.stringify(hash)}`);await sleep(1200);log.navigation.push({hash,pulse:await ev(`!!document.querySelector('.pulse-view')`)});}
if(Object.values(log.states).some(v=>v!==true))throw Error('State verification failed');
log.api=[];for(const path of ['/api/pulse?limit=3','/api/pulse?limit=0','/api/pulse?limit=999','/api/pulse/health','/health','/users','/roles','/categories','/policies','/dashboard/policy-health']){const r=await fetch(base+path);log.api.push({path,status:r.status})}
fs.writeFileSync(process.env.PULSE_TEST_REPORT || '/private/tmp/pulse-browser-results.json',JSON.stringify(log,null,2));console.log(JSON.stringify(log,null,2));ws.close();process.exit(0);
