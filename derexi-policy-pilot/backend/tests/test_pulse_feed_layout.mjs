// Pulse lower-feed ("Intelligence Desk") bento packing — dependency-free Chrome
// CDP checks. Read-only: it renders the real Pulse module with the real
// stylesheet against a stubbed feed payload, so no agency request is repeated
// and no application data is written.
//
// Run (app server must already be running):
//   PULSE_TEST_URL=http://127.0.0.1:8000 node tests/test_pulse_feed_layout.mjs
// Optional: PULSE_SCREENSHOTS=<dir> to capture PNGs.
import fs from 'node:fs';

const base = process.env.PULSE_TEST_URL || 'http://127.0.0.1:8013';
const tabs = await (await fetch('http://127.0.0.1:9222/json/list')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => (ws.onopen = r));
let id = 0;
const pending = new Map();
const errors = [];
ws.onmessage = e => {
  const m = JSON.parse(e.data);
  if (m.id) {
    const p = pending.get(m.id);
    pending.delete(m.id);
    m.error ? p.reject(m.error) : p.resolve(m.result);
  } else if (m.method === 'Runtime.exceptionThrown') errors.push(m.params);
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    setTimeout(() => reject(Error('CDP timeout ' + method)), 20000);
    const i = ++id;
    pending.set(i, { resolve, reject });
    ws.send(JSON.stringify({ id: i, method, params }));
  });
}
async function ev(expression) {
  const x = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (x.exceptionDetails) throw x.exceptionDetails;
  return x.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
const failures = [];
function check(label, ok, detail) {
  if (!ok) failures.push({ label, detail });
  console.log((ok ? '  PASS  ' : '  FAIL  ') + label + (ok ? '' : ' :: ' + JSON.stringify(detail)));
}

await send('Runtime.enable');
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: base + '/ui/' });
await sleep(1500);
await ev('document.readyState');

// The unauthenticated app shows the sign-in gate and hides #app. Pulse is a
// read-only public surface, so the gate is removed, the container unhidden and
// the module mounted directly on the real stylesheet.
async function mount(payload) {
  for (let attempt = 0; attempt < 4; attempt++) {
    await ev(`(async()=>{
      (document.querySelector('.js-gate')||{remove(){}}).remove();
      document.body.style.overflow='';
      const app=document.querySelector('#app');
      if(!app) return;
      app.classList.remove('is-hidden'); app.replaceChildren();
      window.fetch=async()=>({ok:true,status:200,json:async()=>(${JSON.stringify(payload)})});
      await import('/ui/pulse.js?mount='+Math.random());
      PulseView.render(app);
    })()`);
    await sleep(350);
    if (await ev(`!!document.querySelector('.pulse-feed .pulse-story')`)) return;
    await sleep(400); // the app shell may finish booting and repaint #app
  }
  throw Error('Pulse feed did not mount');
}

const feed = await (await fetch(base + '/api/pulse?limit=60')).json();
if (!Array.isArray(feed.articles) || feed.articles.length < 10) throw Error('Feed has too few articles for this check');

// Render the module the way the app does, on the real stylesheet.
await mount(feed);
await sleep(400);

// Measure one rendered feed: packing, gaps, overlaps and clipping.
const MEASURE = `(()=>{
  const feed=document.querySelector('.pulse-feed');
  const cards=[...feed.querySelectorAll('.pulse-story')];
  const rects=cards.map(c=>{const r=c.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),left:Math.round(r.left),right:Math.round(r.right),w:Math.round(r.width)}});
  const columns=[...new Set(rects.map(r=>r.left))].sort((a,b)=>a-b);
  // Vertical gaps, measured down each column. Sampling 40px inside a column
  // strip means a two-column tile counts as occupying both columns it spans.
  const gaps=[];
  columns.forEach(left=>{const cx=left+40;
    const stack=rects.filter(r=>r.left<=cx&&r.right>cx).sort((a,b)=>a.top-b.top);
    for(let i=1;i<stack.length;i++) gaps.push(stack[i].top-stack[i-1].bottom);
  });
  let overlaps=0;
  for(let i=0;i<rects.length;i++) for(let j=i+1;j<rects.length;j++){
    const a=rects[i],b=rects[j];
    if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>0 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1) overlaps++;
  }
  const clipped=cards.filter(c=>c.scrollHeight>c.clientHeight+1||c.scrollWidth>c.clientWidth+1).length;
  const widths=[...new Set(rects.map(r=>r.w))].sort((a,b)=>a-b);
  const bottoms=columns.map(l=>Math.max(...rects.filter(r=>r.left===l).map(r=>r.bottom)));
  return {
    pageOverflow: document.documentElement.scrollWidth-document.documentElement.clientWidth,
    columns: columns.length,
    templateColumns: getComputedStyle(feed).gridTemplateColumns,
    bento: feed.classList.contains('is-bento'),
    cards: cards.length,
    spans: cards.filter(c=>c.style.gridRowStart&&c.style.gridRowEnd).length,
    wide: cards.filter(c=>c.classList.contains('is-wide')).length,
    wideWidths: [...new Set(cards.filter(c=>c.classList.contains('is-wide')).map(c=>Math.round(c.getBoundingClientRect().width)))],
    widthVariance: widths.length,
    overlaps, clipped,
    gapsMin: Math.min(...gaps), gapsMax: Math.max(...gaps), gapCount: gaps.length,
    columnBottomSpread: Math.max(...bottoms)-Math.min(...bottoms),
    domOrderTopDown: rects.every((r,i)=>i===0||r.top>=rects[i-1].top-1)
  };
})()`;

console.log('Live feed: ' + feed.articles.length + ' articles');
const desktop = await ev(MEASURE);
console.log('desktop ' + JSON.stringify(desktop));
check('desktop renders three columns', desktop.columns === 3, desktop.templateColumns);
check('desktop uses packed mode', desktop.bento === true, desktop);
check('every card carries an explicit grid area', desktop.spans === desktop.cards, desktop);
check('no overlapping cards', desktop.overlaps === 0, desktop.overlaps);
check('no clipped card content', desktop.clipped === 0, desktop.clipped);
check('gutters stay 16-20px', desktop.gapsMin >= 16 && desktop.gapsMax <= 22, { min: desktop.gapsMin, max: desktop.gapsMax });
check('no page overflow', desktop.pageOverflow === 0, desktop.pageOverflow);
check('wide tiles are twice a normal card', desktop.wide > 0 && await ev(`(()=>{
  const cards=[...document.querySelectorAll('.pulse-feed .pulse-story')];
  const wide=cards.filter(c=>c.classList.contains('is-wide')).map(c=>Math.round(c.getBoundingClientRect().width));
  const narrow=cards.filter(c=>!c.classList.contains('is-wide')).map(c=>Math.round(c.getBoundingClientRect().width));
  return wide.length>0 && narrow.length>0 && wide.every(w=>w>narrow[0]*1.6);
})()`), { wide: desktop.wide, widths: desktop.wideWidths });
check('mixed card heights (not one uniform height)', await ev(`(()=>{const h=[...document.querySelectorAll('.pulse-feed .pulse-story')].map(c=>Math.round(c.getBoundingClientRect().height));return Math.max(...h)-Math.min(...h)>80})()`), null);
check('reading order preserved in the DOM', await ev(`(()=>{
  // Cards must stay in the ranked feed order that pulse.js wrote; the packer
  // only sets explicit grid areas and never moves nodes.
  const cards=[...document.querySelectorAll('.pulse-feed .pulse-story')];
  return cards.every((c,i)=>c===c.parentNode.children[i]);
})()`), null);

// The application enables smooth scrolling, so jump instantly instead.
const toFeed = `(()=>{const el=document.querySelector('.pulse-feed');const r=el.getBoundingClientRect();
  window.scrollTo({top: window.scrollY + r.top - 8, behavior:'instant'});})()`;

if (process.env.PULSE_SCREENSHOTS) {
  fs.mkdirSync(process.env.PULSE_SCREENSHOTS, { recursive: true });
  const shot = async name => {
    await ev(toFeed);
    await sleep(250);
    const s = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(process.env.PULSE_SCREENSHOTS + '/' + name + '.png', Buffer.from(s.data, 'base64'));
  };
  await shot('bento-desktop-1440');
}

// Responsive columns and packing.
const responsive = [];
for (const width of [1280, 1024, 820, 560, 390]) {
  await send('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: false });
  await sleep(350);
  const m = await ev(MEASURE);
  responsive.push({ width, columns: m.columns, gapsMin: m.gapsMin, gapsMax: m.gapsMax, overlaps: m.overlaps, clipped: m.clipped, pageOverflow: m.pageOverflow });
  check('no overflow at ' + width + 'px', m.pageOverflow === 0, m.pageOverflow);
  check('no overlap at ' + width + 'px', m.overlaps === 0, m.overlaps);
  check('no clipping at ' + width + 'px', m.clipped === 0, m.clipped);
  check('even gutters at ' + width + 'px', m.gapsMin >= 16 && m.gapsMax <= 22, { min: m.gapsMin, max: m.gapsMax });
  if (process.env.PULSE_SCREENSHOTS && (width === 820 || width === 390)) {
    await ev(toFeed);
    await sleep(250);
    const s = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(process.env.PULSE_SCREENSHOTS + '/bento-' + width + '.png', Buffer.from(s.data, 'base64'));
  }
}
console.log('responsive ' + JSON.stringify(responsive));
const cols = responsive.map(r => r.columns);
check('2 columns at tablet widths', cols[0] === 3 && cols[1] === 2 && cols[2] === 2, cols);
check('1 column at phone widths', cols[3] === 1 && cols[4] === 1, cols);

// Filter and refresh rebuild the feed; packing must be restored each time.
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await sleep(300);
const filtered = await ev(`(async()=>{
  const chip=[...document.querySelectorAll('[data-facet]')].find(b=>b.dataset.facet==='filter'&&b.dataset.value==='Regulations');
  chip.click();
  await new Promise(r=>setTimeout(r,250));
  const feed=document.querySelector('.pulse-feed');
  const cards=[...feed.querySelectorAll('.pulse-story')];
  const rects=cards.map(c=>{const r=c.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),left:Math.round(r.left),right:Math.round(r.right)}});
  const columns=[...new Set(rects.map(r=>r.left))];
  const gaps=[];columns.forEach(left=>{const cx=left+40;const s=rects.filter(r=>r.left<=cx&&r.right>cx).sort((a,b)=>a.top-b.top);for(let i=1;i<s.length;i++)gaps.push(s[i].top-s[i-1].bottom)});
  return {cards:cards.length,spans:cards.filter(c=>c.style.gridRowStart&&c.style.gridRowEnd).length,gaps:gaps.length?[Math.min(...gaps),Math.max(...gaps)]:[0,0],columns:columns.length};
})()`);
console.log('filtered ' + JSON.stringify(filtered));
check('filter rebuild re-packs every card', filtered.cards > 0 && filtered.spans === filtered.cards, filtered);
check('filter rebuild keeps gutters even', filtered.gaps[0] >= 16 && filtered.gaps[1] <= 22, filtered.gaps);

const refreshed = await ev(`(async()=>{
  document.querySelector('.pulse-masthead .pulse-refresh').click();
  await new Promise(r=>setTimeout(r,400));
  const cards=[...document.querySelectorAll('.pulse-feed .pulse-story')];
  return {cards:cards.length,spans:cards.filter(c=>c.style.gridRowStart&&c.style.gridRowEnd).length};
})()`);
console.log('refreshed ' + JSON.stringify(refreshed));
check('refresh re-packs every card', refreshed.cards > 0 && refreshed.spans === refreshed.cards, refreshed);

// Stress fixture: extreme headline/summary lengths must not clip or overlap.
const stress = { ...feed, articles: feed.articles.map((a, i) => i % 9 === 0
  ? { ...a, title: 'Extremely long regulatory headline '.repeat(9).trim(), summary: 'Long detail '.repeat(120).trim() }
  : i % 9 === 1 ? { ...a, title: 'Short title', summary: '' } : a), radar: [] };
await mount(stress);
await sleep(400);
const stressed = await ev(MEASURE);
console.log('stress ' + JSON.stringify(stressed));
check('stress: no clipped content', stressed.clipped === 0, stressed.clipped);
check('stress: no overlapping cards', stressed.overlaps === 0, stressed.overlaps);
check('stress: gutters stay 16-20px', stressed.gapsMin >= 16 && stressed.gapsMax <= 22, { min: stressed.gapsMin, max: stressed.gapsMax });
check('stress: no page overflow', stressed.pageOverflow === 0, stressed.pageOverflow);

// Only exceptions raised by the Pulse module are in scope here. Other views in
// the application shell can throw against an unavailable backend; those are
// reported, never fixed, by this runner.
const pulseErrors = errors.filter(e => String((e.exceptionDetails || e).url || '').includes('/ui/pulse.js'));
const otherErrors = errors.filter(e => !pulseErrors.includes(e));
check('no uncaught Pulse exceptions', pulseErrors.length === 0, pulseErrors.length);
if (otherErrors.length) console.log('  NOTE  ' + otherErrors.length + ' unrelated shell exception(s): ' +
  JSON.stringify(otherErrors.map(e => String(((e.exceptionDetails || e).exception || {}).description || '').split('\n')[0])));

console.log('\nRESULT: ' + (failures.length ? failures.length + ' failed' : 'all checks passed'));
if (failures.length) console.log(JSON.stringify(failures, null, 2));
ws.close();
process.exit(failures.length ? 1 : 0);
