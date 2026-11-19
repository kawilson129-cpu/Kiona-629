"""Read-only evidence checks; writes only the course finalization manifest."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

from PIL import Image
from pypdf import PdfReader

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT.parent
REPO = COURSE.parent
SHARED = COURSE / 'AAI 1 Assignment 1'
EVIDENCE = SHARED / 'evidence/20261118-api'
checks = []
hashes = {}


def check(name, condition, detail=None):
    checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((EVIDENCE / name).read_text(encoding='utf-8'))


http, browser, fixture, old = [read(n) for n in ('http-results.json','browser-results.json','fixture.json','validation.json')]
for name, data, count in [('HTTP',http,15),('Browser',browser,7)]:
    check('Retained '+name+' successful result count',len(data['checks']) == count and all(c['status']=='PASS' for c in data['checks']),f'{count} reused; not rerun')
public = read('public-network.json')
check('Four retained public HTTP 200 responses',len(public)==4 and all(r['status_code']==200 for r in public))
check('Fixture explicitly labels mocked search and disabled AI','MOCKED' in fixture['search'] and 'DISABLED' in fixture['ai_provider'])

get = next(r for r in http['requests'] if r['url'].endswith('/policies') and r['status_code']==200)
post = next(r for r in http['requests'] if r['url'].endswith('/ask') and r['status_code']==200)
for r in (get,post):
    check(r['method']+' transcript contains all required fields', all(k in r for k in ('method','url','request_headers','request_body','status_code','response_headers','response_body')))
    check(r['method']+' JSON response/no-store headers', 'application/json' in r['response_headers']['content-type'] and r['response_headers']['cache-control']=='no-store')
check('GET has no request body; POST carries question',get['request_body'] is None and post['request_body']=={'question':'How should I handle a hypothetical policy exception?'})
check('Captured authentication/validation/authorization/private-record statuses',{401,422,403,404} <= {r['status_code'] for r in http['requests']})
check('POST captures clarification rather than a provider answer',post['response_body']['needs_clarification'] and post['response_body']['confidence']==0 and post['response_body']['citations']==[])

def inspect(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in ('authorization','access_token','refresh_token','cookie','set-cookie'):
                check('Sensitive field redacted: '+key,item=='[REDACTED]')
            else:
                inspect(item)
    elif isinstance(value,list):
        for item in value:
            inspect(item)

inspect(http); inspect(browser)
for name in ('http-results.json','browser-results.json'):
    check('No JWT-shaped token in '+name,not re.search(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.',(EVIDENCE/name).read_text()))

for name,expected in fixture['source_hashes'].items():
    raw=(REPO/name).read_bytes()
    normalized=sha(raw.replace(b'\r\n',b'\n'))
    check('LF-normalized source matches fixture: '+name,normalized==expected)
    hashes[name]={'raw':sha(raw),'lf_normalized':normalized,'fixture':expected}

preserved=('fixture.json','http-results.json','browser-results.json','public-network.json',
           'screenshots/01-get-library.png','screenshots/02-post-assistant.png','screenshots/03-get-pulse.png')
for name in preserved:
    path=EVIDENCE/name
    key='evidence/20261118-api/'+name
    raw=path.read_bytes()
    expected=old['artifact_hashes'][key]
    check('Retained evidence matches prior manifest: '+name,expected in (sha(raw),sha(raw.replace(b'\r\n',b'\n'))))

reports={2:COURSE/'AAI 1 Assignment 2/AI_API_Integration_1_Rubric_02_Report.pdf',
         3:ROOT/'AI_API_Integration_1_Rubric_03_Report.pdf',
         4:COURSE/'AAI 1 Assignment 4/AI_API_Integration_1_Rubric_04_Report.pdf'}
report_data={}
for item,path in reports.items():
    pdf=PdfReader(path)
    text='\n'.join(page.extract_text() or '' for page in pdf.pages)
    check(f'Item {item} page limit',len(pdf.pages)==(2 if item==3 else 1))
    check(f'Item {item} honest scope labels','disabled' in text.lower() and 'unverified' in text.lower() or 'not verified' in text.lower())
    report_data[str(item)]={'path':str(path.relative_to(COURSE)),'pages':len(pdf.pages),'sha256':sha(path.read_bytes()),'visual_review':'Passed manual inspection of final rendered pages'}
    if item in (2,4):
        screenshot=Image.open(EVIDENCE/('screenshots/01-get-library.png' if item==2 else 'screenshots/03-get-pulse.png')).convert('RGB')
        matches=[image.image.convert('RGB').size==screenshot.size and image.image.convert('RGB').tobytes()==screenshot.tobytes() for image in pdf.pages[0].images]
        check(f'Item {item} embeds the existing actual screenshot',any(matches))
    else:
        for term in ('http://127.0.0.1:8041/policies','http://127.0.0.1:8041/ask','Content-Type: application/json','Authorization: Bearer [REDACTED]','401','422','403','404',post['request_body']['question'],'2-1,000'):
            check('Item 3 required content: '+term,term in text)
        check('Item 3 selected response fields match actual transcript',all(str(post['response_body'][k]).lower() in text.lower() for k in ('conversation_id','needs_clarification','confidence')))

check('No final Item 1 PDF created',not list(SHARED.glob('*.pdf')))
required=[SHARED/'README.md',SHARED/'rubric-checklist.md',SHARED/'api-evidence.md',SHARED/'test-results.md',ROOT/'README.md',ROOT/'evidence/finalization-review.md']
for doc in required:
    body=doc.read_text(encoding='utf-8')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',body):
        if target.startswith(('https://','http://','#')):
            continue
        path=doc.parent/unquote(target.split('#')[0].strip('<>'))
        check('Local link '+doc.name+' -> '+target,path.exists())
    hashes[str(doc.relative_to(REPO))]={'raw':sha(doc.read_bytes())}

passed=sum(c['status']=='PASS' for c in checks)
failed=len(checks)-passed
result={'timestamp':datetime.now(timezone.utc).isoformat(),'scope':'New offline artifact checks only; 22 application checks reused, not rerun',
        'passed':passed,'failed':failed,'checks':checks,'reports':report_data,'source_and_document_hashes':hashes,
        'gaps':['Item 1 final report deferred and manual HTTP captures pending','Expanded official LMS rubric rows not present in supplied screenshot','Production/Supabase/external AI response unverified; not claimed']}
(ROOT/'evidence/finalization-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':passed,'failed':failed,'failures':[c for c in checks if c['status']=='FAIL']},indent=2))
sys.exit(bool(failed))
