/* Policy governance workspace. Existing lifecycle and verified session API. */
(function () {
  'use strict';
  var pulseSource = null;
  function el(tag, text, cls) {
    var n = document.createElement(tag);
    if (text !== null && text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    return n;
  }
  function button(text, fn, cls) {
    var b = el('button', text, cls || 'btn btn-ghost'); b.type = 'button';
    b.addEventListener('click', fn); return b;
  }
  function label(state) { return String(state || '').replace(/_/g, ' '); }
  function render(app, ctx) {
    var active = ctx.active, api = ctx.api, me = ctx.me;
    var admin = me.role === 'System Administrator';
    var root = el('section', null, 'view lifecycle'); app.appendChild(root);
    var status = el('p', '', 'gov-status'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
    var head = el('header', null, 'view-head');
    head.appendChild(el('p', 'Policy governance / Aurum Capital Bank', 'view-kicker'));
    head.appendChild(el('h1', 'Policy governance', 'view-title'));
    head.appendChild(el('p', 'Independent department review. Administrator approval. A complete decision record.', 'view-sub'));
    root.appendChild(head); root.appendChild(status);
    var pane = el('div'); root.appendChild(pane);
    var owners = [], policies = [], departments = [], categories = [], busy = false;
    var capability = {save_available:false, upload_available:false, templates:[]};
    var referencesReady = false, referencesPromise, pendingDocument = null, contentSequence = 0;
    function message(err) {
      if (err.status === 401) return 'Your session has expired. Please sign in again.';
      if (err.status === 403) return 'You do not have access to this policy workspace.';
      if (!err.status || err.status >= 500 || /week\s*\d|migration|fixture|capstone|seed|database|test(?:ing)?/i.test(err.message || ''))
        return 'Policy workspace is temporarily unavailable. Please try again later.';
      return err.message || 'We could not complete this request. Please try again.';
    }
    function error(err) { if (active()) { status.textContent = message(err); status.classList.add('gov-error'); } }
    function request(path, opts) {
      if (!active()) return Promise.reject(new Error('Session changed'));
      var controller = new AbortController(), timer = setTimeout(function(){controller.abort();},15000);
      opts = Object.assign({}, opts || {}, {signal:controller.signal});
      return api(path, opts).then(function(data){
        if (!active()) throw new Error('Session changed'); return data;
      }).finally(function(){clearTimeout(timer);});
    }
    function mutate(path, method, body, next) {
      if (busy || !active()) return; busy = true;
      root.setAttribute('aria-busy', 'true'); status.textContent = 'Saving…'; status.classList.remove('gov-error');
      root.querySelectorAll('button').forEach(function (b) { b.disabled = true; });
      request(path, {method:method, body:JSON.stringify(body)}).then(function (data) {
        if (!active()) return;
        status.textContent = 'Saved. Decision history and notifications updated.';
        ctx.refreshNotifications(); next(data);
      }).catch(error).finally(function () {
        busy = false; root.removeAttribute('aria-busy');
        root.querySelectorAll('button').forEach(function (b) { b.disabled = b.dataset.locked === '1'; });
      });
    }
    function field(form, caption, name, value, type, required) {
      var wrap = el('label', null, 'gov-field'); wrap.appendChild(el('span',caption));
      var input = el(type === 'textarea' ? 'textarea' : 'input');
      input.name = name; if (type !== 'textarea') input.type = type || 'text';
      input.value = value || ''; input.required = !!required;
      if (name === 'body') { input.rows = 15; input.maxLength = 20000; }
      if (name === 'title') input.maxLength = 200;
      if (name === 'summary') input.maxLength = 1000;
      if (name === 'version_no') input.maxLength = 20;
      wrap.appendChild(input); form.appendChild(wrap); return input;
    }
    function select(form, caption, values, value) {
      var wrap = el('label',null,'gov-field'); wrap.appendChild(el('span',caption));
      var n = el('select'); values.forEach(function (v) { var o = el('option',v.name || v.title); o.value = v.id || ''; n.appendChild(o); });
      n.value = value || (values.length ? values[0].id || '' : ''); wrap.appendChild(n); form.appendChild(wrap); return n;
    }
    function open(id) { location.hash = '#governance/' + id; }
    function list() {
      contentSequence++;
      pane.replaceChildren();
      var intro=el('div',null,'gw-intro');
      intro.appendChild(el('p','Your policy desk','view-kicker'));
      intro.appendChild(el('h1','Bring clarity to every policy.','gw-title'));
      intro.appendChild(el('p','Start with a document or a considered template. Shape the guidance, invite an independent review, and follow every decision.','gw-dek'));
      pane.appendChild(intro);
      var creation=el('div',null,'gw-create-grid');pane.appendChild(creation);
      var upload=el('section',null,'gw-upload');upload.setAttribute('aria-label','Document upload');
      var drop=el('div',null,'gw-drop'); drop.setAttribute('role','group');drop.setAttribute('aria-label','Choose or drop a DOCX or PDF document');
      var art=el('div',null,'gw-paper-art');art.setAttribute('aria-hidden','true');art.appendChild(el('span','POLICY'));art.appendChild(el('i'));art.appendChild(el('i'));art.appendChild(el('i'));drop.appendChild(art);
      drop.appendChild(el('span','A new chapter starts here','gw-overline'));
      drop.appendChild(el('h3','Drop your policy document'));
      drop.appendChild(el('p','DOCX or PDF · Up to 5 MB · Text-based documents'));
      var file=el('input');file.type='file';file.tabIndex=-1;file.accept='.docx,.pdf';file.className='gw-file';file.setAttribute('aria-label','Browse policy documents');
      var browse=button('Browse documents',function(e){e.stopPropagation();file.click();},'btn btn-primary');drop.appendChild(browse);drop.appendChild(file);upload.appendChild(drop);
      var intakeState=el('p','Checking document intake…','gw-intake-state');intakeState.setAttribute('role','status');upload.appendChild(intakeState);creation.appendChild(upload);
      drop.addEventListener('click',function(e){if(capability.upload_available&&e.target!==file&&!e.target.closest('button'))file.click();});
      drop.addEventListener('keydown',function(e){if(e.target===drop&&(e.key==='Enter'||e.key===' ')){e.preventDefault();file.click();}});
      ['dragenter','dragover'].forEach(function(name){drop.addEventListener(name,function(e){e.preventDefault();drop.classList.add('is-dragging');});});
      ['dragleave','drop'].forEach(function(name){drop.addEventListener(name,function(e){e.preventDefault();drop.classList.remove('is-dragging');});});
      drop.addEventListener('drop',function(e){if(e.dataTransfer.files.length!==1){intakeState.textContent='Choose one document at a time.';return;}intake(e.dataTransfer.files[0]);});
      file.addEventListener('change',function(){if(file.files[0])intake(file.files[0]);file.value='';});
      var templates=el('section',null,'gw-template-card');templates.appendChild(el('p','A structured beginning','view-kicker'));
      templates.appendChild(el('h3','Create from a template'));
      templates.appendChild(el('p','A consistent foundation for new policies, security requirements and operating procedures.'));
      var templateAction=button('Create from Template',chooseTemplate,'btn btn-ghost');templates.appendChild(templateAction);
      templates.appendChild(button('Write a policy',function(){editor(null);},'gw-text-action'));
      var steps=el('ol',null,'gw-steps');['Draft with purpose','Independent peer review','Final approval','Controlled publication'].forEach(function(x){steps.appendChild(el('li',x));});templates.appendChild(steps);creation.appendChild(templates);
      var banner=el('div',null,'gw-service-state');banner.setAttribute('role','status');pane.appendChild(banner);
      var nav=el('nav',null,'gw-section-nav');nav.setAttribute('aria-label','Policy workspaces');pane.appendChild(nav);
      var groups=[
        ['My Drafts',function(d){return d.author_id===me.id&&['draft','rejected','revisions_requested'].includes(d.status);},'Continue shaping your policies.'],
        ['Peer Reviews',function(d){return d.reviewer_id===me.id&&d.status==='pending_peer_review';},'Independent reviews assigned to you.'],
        ['Publication',function(d){return d.status==='approved_pending_publication';},'Approved guidance awaiting its effective date or publication.'],
        ['Audit History',function(d){return true;},'Trace policy versions and recorded decisions.']
      ];
      if(admin)groups.splice(2,0,['Final Approvals',function(d){return d.status==='pending_final_approval';},'Policies ready for your final decision.']);
      var grid=el('div',null,'gw-queues');pane.appendChild(grid);
      var panels=groups.map(function(g,i){
        var section=el('section',null,'gw-queue');section.id='policy-queue-'+i;
        var heading=el('div',null,'gw-queue-heading');heading.appendChild(el('h3',g[0]));var count=el('span','—','gw-count');heading.appendChild(count);section.appendChild(heading);section.appendChild(el('p',g[2],'gw-queue-description'));
        var body=el('div',null,'gw-queue-body');body.setAttribute('aria-live','polite');section.appendChild(body);grid.appendChild(section);
        nav.appendChild(button(g[0],function(){section.scrollIntoView({behavior:'smooth',block:'start'});},'gw-nav-item'));
        return {group:g,body:body,count:count};
      });
      var queueGeneration=0;
      function loadQueues(){
        var generation=++queueGeneration;
        panels.forEach(function(p){p.count.textContent='—';p.body.replaceChildren(el('p','Loading policies…','gw-queue-state'));p.body.setAttribute('aria-busy','true');});
        request('/governance/drafts').then(function(rows){
          if(!active()||!grid.isConnected||generation!==queueGeneration)return;
          panels.forEach(function(p){
            var items=rows.filter(p.group[1]);p.count.textContent=items.length;p.body.replaceChildren();
            if(!items.length)p.body.appendChild(el('p','No policies here at the moment.','gw-queue-state'));
            items.forEach(function(d){var row=button('',function(){open(d.id);},'gw-review-row');var name=el('span');name.appendChild(el('strong',d.title));name.appendChild(el('small','Version '+d.version_no));row.appendChild(name);row.appendChild(el('span',label(d.status),'gw-policy-status'));p.body.appendChild(row);});
          });
        }).catch(function(err){
          if(!active()||!grid.isConnected||generation!==queueGeneration)return;
          panels.forEach(function(p){p.count.textContent='—';p.body.replaceChildren(el('p',message(err),'gw-queue-state is-error'),button('Try again',loadQueues,'gw-text-action'));});
        }).finally(function(){if(generation===queueGeneration)panels.forEach(function(p){p.body.removeAttribute('aria-busy');});});
      }
      function availability(){
        request('/governance/availability').then(function(data){
          capability=data;if(!active()||!banner.isConnected)return;
          banner.replaceChildren();
          if(!data.save_available)banner.appendChild(el('p','Policy workspace is temporarily unavailable. You can preview a document or prepare a policy; saving and review actions are currently unavailable.'));
          intakeState.textContent=data.upload_available?(data.original_retention?'Original documents are retained privately when you save.':'Preview and edit your policy text. Original files are not retained.'):'Document intake is temporarily unavailable. You can still create a policy from a template.';
          browse.disabled=!data.upload_available;file.disabled=!data.upload_available;drop.setAttribute('aria-disabled',String(!data.upload_available));
        }).catch(function(err){if(banner.isConnected){banner.replaceChildren(el('p',message(err)));intakeState.textContent='Document intake is temporarily unavailable.';browse.disabled=true;}});
      }
      function intake(document){
        if(!capability.upload_available){intakeState.textContent='Document intake is temporarily unavailable. Please try again later.';return;}
        if(!/\.(docx|pdf)$/i.test(document.name)||document.size>5*1024*1024||!document.size){intakeState.textContent='Choose a DOCX or PDF document smaller than 5 MB.';return;}
        if(busy)return;busy=true;browse.disabled=true;drop.setAttribute('aria-busy','true');intakeState.textContent='Reading your document…';
        var type=/\.pdf$/i.test(document.name)?'application/pdf':'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
        request('/governance/documents/preview',{method:'POST',body:document,contentType:type,fileName:document.name}).then(function(result){
          if(!active()||!drop.isConnected)return;
          pendingDocument=result;status.textContent='Document ready for your review. Nothing has been saved.';editor(null,{title:result.suggested_title,body:result.body});
        }).catch(function(err){if(drop.isConnected)intakeState.textContent=message(err);}).finally(function(){busy=false;if(drop.isConnected){browse.disabled=!capability.upload_available;drop.removeAttribute('aria-busy');}});
      }
      loadQueues();availability();
    }
    function chooseTemplate(){
      pane.replaceChildren();pane.appendChild(button('← Policy workspace',list));pane.appendChild(el('h1','Choose a policy template','gov-section-title'));
      var grid=el('div',null,'gw-template-grid');pane.appendChild(grid);
      function paint(){grid.replaceChildren();
        (capability.templates||[]).forEach(function(t){var card=el('article',null,'gw-template-choice');card.appendChild(el('p','Policy template','view-kicker'));card.appendChild(el('h3',t.name));card.appendChild(el('p',t.description));card.appendChild(button('Use template',function(){pendingDocument=null;editor(null,{body:t.body,title:''});},'btn btn-primary'));grid.appendChild(card);});
        if(!capability.templates.length)grid.appendChild(el('p','Templates are temporarily unavailable. You can start with a blank policy.','gw-queue-state'));
      }
      if(capability.templates.length)paint();else{grid.appendChild(el('p','Loading templates…'));request('/governance/availability').then(function(data){capability=data;if(grid.isConnected)paint();}).catch(function(){if(grid.isConnected)paint();});}
      grid.appendChild(button('Start a blank policy',function(){editor(null);},'gw-text-action'));
    }
    function editor(d, initial) {
      initial=initial||{};contentSequence++;
      pane.replaceChildren();
      pane.appendChild(button('← Back to '+(d?'policy':'queues'),function(){d?detail(d.id):list();}));
      pane.appendChild(el('h1',d?'Edit policy':'Document workspace','gov-section-title'));
      pane.appendChild(el('p','Saving an edit clears all approvals. Published guidance remains available until an approved replacement is published.','gov-note'));
      var form=el('form',null,'gov-form'); pane.appendChild(form);
      var baseSelect=null;
      if (!d) baseSelect=select(form,'Policy', [{id:'',title:'New policy'}].concat(policies), '');
      var dept=select(form,'Department',departments, d?d.department_id:me.department_id);
      dept.disabled=!admin || !!d;
      var title=field(form,'Policy title','title',d?d.title:initial.title,'text',true);
      var summary=field(form,'Summary','summary',d&&d.summary,'textarea',false);
      var version=field(form,'Version number','version_no',d?d.version_no:'1.0','text',true);
      var cat=select(form,'Category',[{id:'',name:'Uncategorized'}].concat(categories),d&&d.category_id);
      var effective=field(form,'Effective date (publication is blocked until this date)','effective_date',d&&d.effective_date,'date');
      var review=field(form,'Next review date','review_date',d&&d.review_date,'date');
      var body=field(form,'Policy content','body',d?d.body:initial.body,'textarea',true);
      var source=d?d.source:pulseSource;
      var document=pendingDocument;
      if(document&&!d){
        var summaryBox=el('aside',null,'gw-document-summary');summaryBox.appendChild(el('p','Document imported','view-kicker'));summaryBox.appendChild(el('strong',document.filename));
        summaryBox.appendChild(el('p','Extracted text has been arranged into the policy format. Review all sections and replace any guidance in brackets.'));
        summaryBox.appendChild(el('p',document.original_retention?'The original will be retained privately when this draft is saved.':'The original file will not be retained. Only the confirmed policy text will be saved.'));
        var original=el('details');original.appendChild(el('summary','View extracted document text'));original.appendChild(el('pre',document.extracted_text,'gov-policy-body'));summaryBox.appendChild(original);form.prepend(summaryBox);
      }
      var preview=el('section',null,'gw-live-preview');preview.appendChild(el('p','Policy Library preview','view-kicker'));var previewTitle=el('h3');var previewBody=el('div',null,'gov-policy-body');preview.appendChild(previewTitle);preview.appendChild(previewBody);form.appendChild(preview);
      function updatePreview(){
        previewTitle.textContent=title.value||'Untitled policy';previewBody.replaceChildren();
        (body.value||'Your policy content will appear here.').split('\n').forEach(function(line){
          if(!line.trim())return;
          if(/^(purpose|scope|policy requirements|responsibilities|exceptions|related guidance):?$/i.test(line.trim()))previewBody.appendChild(el('h4',line));
          else previewBody.appendChild(el('p',line));
        });
      }
      title.addEventListener('input',updatePreview);body.addEventListener('input',updatePreview);updatePreview();
      var confirmation=el('label',null,'gw-confirmation');var checkbox=el('input');checkbox.type='checkbox';checkbox.required=true;checkbox.name='confirm_document';confirmation.appendChild(checkbox);confirmation.appendChild(el('span','I have reviewed the policy text and metadata and confirm this is ready to save as a draft.'));form.appendChild(confirmation);
      var saveState=el('p','Checking workspace availability…','gw-save-state');saveState.setAttribute('role','status');form.appendChild(saveState);

      if (source) { var note=el('aside',null,'gov-source'); note.appendChild(el('strong','Pulse source · human review required'));
        note.appendChild(el('p',source.title)); var a=el('a','Read source publication'); a.href=source.url;a.target='_blank';a.rel='noopener noreferrer';note.appendChild(a);
        note.appendChild(el('p',(source.published||'Undated')+' · '+source.context)); form.appendChild(note); }
      if (baseSelect) baseSelect.addEventListener('change',function(){
        var selected=baseSelect.value;var id=Number(selected); if (!id) return;
        request('/policies/'+id).then(function(p){
          title.value=p.title;summary.value=p.summary||'';cat.value=p.category_id||'';
          var versions=p.versions||[];var v=versions[versions.length-1]; if(v) {if(!document&&!initial.body)body.value=v.body; version.value=''; version.focus();updatePreview();}
          var owner=ctx.users.find(function(u){return u.id===p.owner_id;});if(owner)dept.value=owner.department_id;
        }).catch(error);
      });
      var save=el('button','Save draft','btn btn-primary');save.type='submit';save.disabled=true;save.dataset.locked='1';form.appendChild(save);
      function checkSave(){request('/governance/availability').then(function(data){capability=data;return referencesReady?referencesPromise:loadReferences();}).then(function(){
        if(!form.isConnected||!active())return;
        var allowed=capability.save_available&&referencesReady;
        save.disabled=!allowed;save.dataset.locked=allowed?'0':'1';
        saveState.textContent=allowed?'Save a draft for review. This does not approve or publish the policy.':'Policy workspace is temporarily unavailable. Your changes have not been saved. You can continue reviewing this document.';
        if(baseSelect&&baseSelect.options.length===1)policies.forEach(function(x){var o=el('option',x.title);o.value=x.id;baseSelect.appendChild(o);});
        if(cat.options.length===1)categories.forEach(function(x){var o=el('option',x.name);o.value=x.id;cat.appendChild(o);});
        if(!d&&departments.length&&!dept.options.length){dept.replaceChildren();departments.forEach(function(x){var o=el('option',x.name);o.value=x.id;dept.appendChild(o);});dept.value=me.department_id||departments[0].id;}
      }).catch(function(){if(form.isConnected)saveState.textContent='Policy workspace is temporarily unavailable. Your changes have not been saved.';});}
      checkSave();form.appendChild(button('Check availability',checkSave,'gw-text-action'));
      form.appendChild(button('Discard changes',function(){if(document)request('/governance/documents/preview/'+document.import_id,{method:'DELETE'}).catch(function(){});pendingDocument=null;list();},'gw-text-action'));

      form.addEventListener('submit',function(evt){evt.preventDefault();
        if(save.disabled||!capability.save_available||!referencesReady){saveState.textContent='Policy workspace is temporarily unavailable. Your changes have not been saved.';return;}
        if(!checkbox.checked){checkbox.focus();return;}
        var payload={title:title.value,summary:summary.value||null,body:body.value,version_no:version.value,
          category_id:Number(cat.value)||null,effective_date:effective.value||null,review_date:review.value||null,source:source||null};
        if(d)payload.expected_revision=d.revision;
        else {payload.policy_id=Number(baseSelect.value)||null;payload.department_id=Number(dept.value);if(document){payload.import_id=document.import_id;payload.confirm_document=checkbox.checked;}}
        mutate('/governance/drafts'+(d?'/'+d.id:''),d?'PATCH':'POST',payload,function(result){pulseSource=null;pendingDocument=null;open(result.id);detail(result.id);});
      });
    }
    function detail(id) {
      contentSequence++;pane.replaceChildren(el('p','Loading policy and decision history…'));
      request('/governance/drafts/'+id).then(function(d){
        pane.replaceChildren();pane.appendChild(button('← Governance queues',function(){location.hash='#governance';}));
        var title=el('div',null,'gov-detail-head'); title.appendChild(el('h1',d.title,'gov-section-title'));title.appendChild(el('span',label(d.status),'stamp'));pane.appendChild(title);
        pane.appendChild(el('p','Version '+d.version_no+' · Revision '+d.revision+' · Effective '+(d.effective_date||'on publication'),'gov-note'));
        if(d.source){var s=el('aside',null,'gov-source');s.appendChild(el('strong','Pulse regulatory context'));s.appendChild(el('p',d.source.title+' · '+(d.source.published||'Undated')));
          var a=el('a','Original source');a.href=d.source.url;a.target='_blank';a.rel='noopener noreferrer';s.appendChild(a);s.appendChild(el('p',d.source.context));pane.appendChild(s);}
        var columns=el('div',null,'gov-workspace');var content=el('section');var controls=el('aside',null,'gov-review'); columns.appendChild(content);columns.appendChild(controls);pane.appendChild(columns);
        content.appendChild(el('h3','Working policy'));content.appendChild(el('pre',d.body,'gov-policy-body'));
        controls.appendChild(el('h3','Review & decisions'));
        var original=(d.history[0]&&d.history[0].snapshot.original_document);
        if(original&&original.retained)controls.appendChild(button('Download original',function(){
          request('/governance/drafts/'+d.id+'/original',{responseType:'blob'}).then(function(blob){
            var url=URL.createObjectURL(blob),link=el('a');link.href=url;link.download=original.filename;link.click();setTimeout(function(){URL.revokeObjectURL(url);},1000);
          }).catch(error);
        }));
        if(d.author_id===me.id&&d.status!=='published')controls.appendChild(button('Edit working copy',function(){editor(d);}));
        var comment=field(controls,'Review comment (required for rejection or changes)','comment','','textarea');comment.maxLength=4000;
        function action(code, caption, reviewer) {
          var b=button(caption,function(){
            if(/_(reject|changes)$/.test(code)&&!comment.value.trim()){status.textContent='Add a review comment before this decision.';comment.focus();return;}
            mutate('/governance/drafts/'+d.id+'/actions','POST',{expected_revision:d.revision,action:code,comment:comment.value||null,reviewer_id:reviewer?Number(reviewer.value):null},function(){detail(d.id);});
          },code==='publish'?'btn btn-primary':'btn btn-ghost');controls.appendChild(b);return b;
        }
        if(d.author_id===me.id&&['draft','revisions_requested','rejected'].includes(d.status)) {
          var eligible=owners.filter(function(u){return u.id!==me.id&&u.department_id===d.department_id;});
          var reviewer=select(controls,'Independent peer reviewer',eligible,'');
          if(!eligible.length)controls.appendChild(el('p','A second department Policy Owner is required. Contact your administrator to assign an independent reviewer.','gov-error'));
          var submit=action('submit','Submit for peer review',reviewer);if(!eligible.length){submit.disabled=true;submit.dataset.locked='1';}
        }
        if(d.reviewer_id===me.id&&me.role==='Policy Owner'&&d.status==='pending_peer_review'){
          action('peer_approve','Approve peer review');action('peer_changes','Request changes');action('peer_reject','Reject submission');}
        if(admin&&me.id!==d.author_id&&d.status==='pending_final_approval'){
          action('final_approve','Grant final approval');action('final_changes','Request changes');action('final_reject','Reject submission');}
        if(admin&&me.id!==d.author_id&&d.status==='approved_pending_publication'){
          var publish=action('publish','Publish approved version');
          if(d.effective_date&&d.effective_date>new Date().toLocaleDateString('en-CA')){publish.disabled=true;publish.dataset.locked='1';controls.appendChild(el('p','Ready for administrator publication on '+d.effective_date+'.','gov-note'));}}
        var comparison=el('section',null,'gov-comparison');comparison.appendChild(el('h3','Version comparison'));pane.appendChild(comparison);
        var versions=[{id:'base',name:'Published base version'}].concat(d.history.map(function(e){return{id:String(e.id),name:label(e.action)+' · '+e.actor};}));
        var pick=select(comparison,'Compare working copy with',versions,'base'); var diff=el('div',null,'gov-diff');comparison.appendChild(diff);
        function compare(){var baseline=pick.value==='base'?d.base_version:(d.history.find(function(e){return String(e.id)===pick.value;})||{}).snapshot;
          diff.replaceChildren();var left=el('div');left.appendChild(el('h4',baseline?'Previous content':'New policy — no published base'));left.appendChild(el('pre',baseline?baseline.body:'','gov-policy-body'));
          var right=el('div');right.appendChild(el('h4','Current working copy'));var pre=el('pre',null,'gov-policy-body');var old=(baseline?baseline.body:'').split('\n');
          d.body.split('\n').forEach(function(line,i){pre.appendChild(el('span',(old[i]===line?'  ':'+ ')+line+'\n',old[i]===line?'':'gov-added'));});right.appendChild(pre);diff.appendChild(left);diff.appendChild(right);}
        pick.addEventListener('change',compare);compare();
        var history=el('section',null,'gov-history');history.appendChild(el('h3','Approval & audit history'));var ol=el('ol');
        d.history.slice().reverse().forEach(function(e){var li=el('li');li.appendChild(el('strong',label(e.action)+' · '+e.actor));li.appendChild(el('time',new Date(e.at).toLocaleString()));if(e.comment)li.appendChild(el('p',e.comment));ol.appendChild(li);});history.appendChild(ol);pane.appendChild(history);
      }).catch(function(err){if(active()){pane.replaceChildren(el('p',message(err),'gw-queue-state is-error'),button('Return to policy workspace',list));error(err);}});
    }
    function loadReferences(){referencesPromise=Promise.allSettled([request('/governance/owners'),request('/policies'),request('/departments'),request('/categories')]).then(function(results){
      owners=results[0].status==='fulfilled'?results[0].value:[];
      policies=results[1].status==='fulfilled'?results[1].value:[];
      departments=results[2].status==='fulfilled'?results[2].value:[];
      categories=results[3].status==='fulfilled'?results[3].value:[];
      referencesReady=results.every(function(r){return r.status==='fulfilled';});
      return referencesReady;
    });return referencesPromise;}
    loadReferences();
    var match=location.hash.match(/^#governance\/(\d+)$/);
    if(match)referencesPromise.then(function(){detail(Number(match[1]));});
    else if(pulseSource)referencesPromise.then(function(){editor(null);});
    else list();

  }
  window.GovernanceView={render:render,fromPulse:function(article){
    if (!/^https:\/\//i.test(String(article.url || ''))) return;
    pulseSource={url:article.url,title:article.title,published:article.published||null,
      context:[article.source,article.agency,article.category,article.status,article.summary].filter(Boolean).join(' · ').slice(0,4000)};
    location.hash='#governance';
  },clear:function(){pulseSource=null;}};
}());
