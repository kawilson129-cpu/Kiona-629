/* Real Chromium verification; all data is synthetic and the server is isolated. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async function () {
  const metadata = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const output = process.argv[3];
  fs.mkdirSync(output, {recursive:true});
  const checks = [], errors = [];
  function check(id, passed) { checks.push({id,status:passed?'PASS':'FAIL'}); if(!passed) throw Error('Failed '+id); }
  const browser = await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page = await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  page.on('pageerror',e=>errors.push(e.message));
  let dialogs = 0;
  page.on('dialog',async d=>{dialogs++; await d.dismiss();});
  try {
    await page.goto(metadata.base+'/ui/');
    check('UI-01-activation-required',page.url().endsWith('/__dev/login'));
    const key = fs.readFileSync(metadata.activation_key_path,'utf8');
    await page.fill('#key',key);
    await page.click('button');
    await page.waitForURL('**/ui/');
    await page.waitForFunction(()=>document.querySelector('#persona-select')?.options.length===4);
    check('UI-02-original-selector-retained',await page.locator('#persona-select').count()===1);
    check('UI-03-signed-employee',await page.evaluate(async()=> (await (await fetch('/me')).json()).role)==='Employee');
    check('UI-04-employee-governance-hidden',!(await page.locator('.js-gov-link').isVisible()));
    let activity = page.waitForResponse(r=>r.url().endsWith('/policies'));
    await page.click('[data-view="library"]');
    const library = await activity;
    check('UI-11-employee-approved-library',library.status()===200 && (await library.json()).every(p=>p.status==='approved'));
    await page.click('[data-view="assist"]');
    await page.getByLabel('Your policy question').fill('How should I report phishing?');
    activity = page.waitForResponse(r=>r.url().endsWith('/ask') && r.request().method()==='POST');
    await page.getByRole('button',{name:'Ask DeRexi',exact:true}).click();
    const answer = await activity;
    check('UI-12-assistant-signed-write',answer.status()===200 && (await answer.json()).citations.length>0);
    await page.getByRole('tab',{name:'Report an incident',exact:true}).click();
    await page.waitForFunction(()=>document.querySelector('#inc-cat')?.options.length>1);
    await page.selectOption('#inc-cat','97001');
    await page.fill('#inc-desc','Synthetic browser incident report');
    activity = page.waitForResponse(r=>r.url().endsWith('/incidents') && r.request().method()==='POST');
    await page.getByRole('button',{name:'Report incident',exact:true}).click();
    check('UI-13-incident-signed-write',(await activity).status()===201);
    activity = page.waitForResponse(r=>r.url().includes('/messages?'));
    await page.click('[data-view="messages"]');
    const messages = await activity;
    await page.getByText('Messages unavailable',{exact:true}).waitFor();
    checks.push({id:'MSG-001',status:messages.status()===404?'BLOCKED':'FAIL',reason:'Pre-existing missing Messages endpoint'});
    await Promise.all([page.waitForEvent('domcontentloaded'),page.selectOption('#persona-select','91002')]);
    await page.waitForFunction(()=>window.DeRexiIdentity?.userId===91002);
    check('UI-05-signed-owner-switch',await page.evaluate(async()=> (await (await fetch('/me')).json()).role)==='Policy Owner');
    check('UI-06-owner-governance-visible',await page.locator('.js-gov-link').isVisible());
    const governance = page.waitForResponse(r=>r.url().includes('/dashboard/policy-health'));
    await page.click('[data-view="governance"]');
    check('UI-07-governance-api', (await governance).status()===200);
    await Promise.all([page.waitForEvent('domcontentloaded'),page.selectOption('#persona-select','91003')]);
    await page.waitForFunction(()=>window.DeRexiIdentity?.userId===91003);
    check('UI-08-signed-admin-switch',await page.evaluate(async()=> (await (await fetch('/me')).json()).role)==='System Administrator');
    const pulse = page.waitForResponse(r=>r.url().includes('/api/pulse?'));
    await page.click('[data-view="pulse"]');
    check('UI-09-real-pulse-api',(await pulse).status()===200);
    await page.getByText('Synthetic capital final rule',{exact:false}).first().waitFor();
    await page.screenshot({path:path.join(output,'signed-local-pulse.png'),fullPage:true});
    // Bypass the server filter only in this browser fixture to test the renderer
    // against a compromised response, as required by original check C03-55.
    await page.route('**/api/pulse?*',async route=>{
      const data=await (await route.fetch()).json();
      data.articles=[{...data.articles[0],id:'hostile-fixture',title:'<img id="pulse-injected" src=x onerror="window.pulseInjected=true">',
        summary:'<script>window.pulseInjected=true</script>',url:'javascript:window.pulseInjected=true'}];
      data.radar=[];
      await route.fulfill({json:data});
    });
    await page.reload();
    await page.waitForFunction(()=>document.body.textContent.includes('<img id="pulse-injected"'));
    const hostileSafe=await page.evaluate(()=> !window.pulseInjected && !document.querySelector('#pulse-injected')
      && !document.querySelector('a[href^="javascript:"]'));
    check('C03-55',hostileSafe && dialogs===0);
    await page.screenshot({path:path.join(output,'hostile-feed-inert.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:path.join(output,'local-pulse-mobile.png'),fullPage:true});
    check('UI-10-no-runtime-exceptions',errors.length===0);
  } finally {
    fs.writeFileSync(path.join(output,'browser_results.json'),JSON.stringify({date:new Date().toISOString(),mode:'real Chromium; synthetic data only',checks,errors},null,2));
    await browser.close();
  }
  console.log(JSON.stringify({passed:checks.filter(c=>c.status==='PASS').length,failed:checks.filter(c=>c.status==='FAIL').length,output}));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
