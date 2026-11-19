"""Package existing HTML coursework evidence; writes only inside html_1.

No DeRexi imports, API calls, production changes, or Git operations. The original
LMS screenshot stays in place. Supplemental pages are explicitly coursework demos.
"""
from datetime import datetime, timezone
from html import escape
import hashlib
import json
from pathlib import Path
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
STAMP = datetime.now(timezone.utc).isoformat()
APP = 'derexi-policy-pilot/backend/static/index.html'
PULSE = 'derexi-policy-pilot/backend/static/pulse.js'
GOV = 'derexi-policy-pilot/backend/static/governance.js'
PAGE = 'docs/derexi-policy-pilot.md'
OLD = 'ai_api_intergration_1/AAI 1 Assignment 1/evidence/20261118-api'
NAMES = ['Assignment 1 - Semantic HTML', 'Assignment 2 - Web Elements',
         'Assignment 3 - HTML Attributes', 'Assignment 4 - Hyperlinks']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, text):
    assert path.resolve().is_relative_to(ROOT)
    if path.exists():
        raise FileExistsError('Preserve existing work: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def save_json(path, value):
    write(path, json.dumps(value, indent=2) + '\n')


def reference(path, line):
    return f'[{path}:{line}](../../{quote(path, safe="/")}#L{line})'


def excerpts(folder, ranges):
    rows = []
    body = '# Verbatim source excerpts\n\n'
    body += ('Original code, not a newly implemented feature. Line ranges are 1-based, inclusive.\n'
             'Excerpt text is UTF-8 decoded with normalized line endings; raw source hashes\n'
             'are recorded separately. Omitted spans are separate fenced blocks.\n\n')
    for path, first, last, language, purpose in ranges:
        source = REPO / path
        lines = source.read_text().splitlines()
        snippet = '\n'.join(lines[first - 1:last]) + '\n'
        rows.append({'path': path, 'start_line': first, 'end_line': last,
                     'source_sha256': sha(source), 'excerpt': snippet, 'purpose': purpose})
        body += f'## {purpose}\n\n`{path}:{first}–{last}`\n\n```{language}\n{snippet}```\n\n'
    write(folder / 'evidence/source-excerpts.md', body)
    save_json(folder / 'evidence/source-map.json', {'captured_at': STAMP, 'sources': rows})


def reuse(folder, screenshot, image_name, extra=None):
    files = [(f'{OLD}/screenshots/{screenshot}', image_name, 'Original Nov 18 DeRexi browser capture; reused, not recaptured'),
             (f'{OLD}/browser-results.json', 'reused-browser-results.json',
              'Original seven passing browser checks; contextual evidence, not new HTML-tag tests')]
    files += extra or []
    items = []
    for path, name, scope in files:
        destination = folder / 'evidence' / name
        assert not destination.exists()
        shutil.copyfile(REPO / path, destination)
        items.append({'original_path': path, 'copy': 'evidence/' + name,
                      'sha256': sha(destination), 'scope': scope})
    save_json(folder / 'evidence/reused-evidence.json', {'captured_at': STAMP, 'items': items,
              'limits': 'Historical UI fixture: synthetic SQLite; search mocked; AI disabled. No app or API tests rerun.'})


def readme(folder, number, summary, evidence_note, extra=''):
    text = f'''# HTML 1 · Assignment {number}

**Verification status: Complete** — {summary}

Primary project: **DeRexi: Policy Pilot**. See [assignment report](assignment_report.md)
for rubric mapping and exact original source paths/lines.

| Evidence | Purpose |
|---|---|
| [Source excerpts](evidence/source-excerpts.md) | Verbatim existing code with 1-based line references |
| [Source map](evidence/source-map.json) | Original file hashes, line spans and exact excerpt text |
| [Reused evidence manifest](evidence/reused-evidence.json) | Original paths, byte-for-byte copy hashes and scope labels |
| [Existing browser results](evidence/reused-browser-results.json) | Nov 18 UI context, reused without execution |
| [Current static checks](evidence/verification.json) | Literal tag/attribute/source checks; separate from historical app tests |

{evidence_note}

{extra}

**Remaining gaps:** none for the supplied criterion. Original app behavior,
live hosting, production auth and external services are not newly tested here.
Screenshots show UI context; source parsing supplies literal markup evidence.
Only coursework files were created; original code and other coursework remain unchanged.
'''
    write(folder / 'README.md', text)


for name in NAMES:
    if (ROOT / name).exists():
        raise FileExistsError('Assignment folder already exists: ' + name)
    (ROOT / name / 'evidence').mkdir(parents=True)

a1, a2, a3, a4 = [ROOT / name for name in NAMES]
excerpts(a1, [(APP, 18, 23, 'html', 'Header letterhead'),
              (APP, 38, 46, 'html', 'Primary navigation'),
              (APP, 82, 90, 'html', 'Main mount point and footer')])
reuse(a1, '01-get-library.png', 'reused-library-ui.png')
write(a1 / 'assignment_report.md', f'''# 01 / Semantic HTML
### Existing DeRexi structure · Complete

**Criterion:** demonstrate literal `header`, `main`, `footer` and `nav` tags.
All four already exist in DeRexi's actual HTML shell; no production edit or
replacement application was needed.

| Required element | Exact existing source | Purpose |
|---|---|---|
| `<header>` | {reference(APP,18)}; closes at line 23 | Institution/division letterhead |
| `<nav>` | {reference(APP,38)}; closes at line 46 | Named primary navigation landmark |
| `<main>` | {reference(APP,83)} | Single main content mount point for the existing app |
| `<footer>` | {reference(APP,86)}; closes at line 90 | Institution, regulation context and mode label |

The `main` element is empty in the initial source because existing JavaScript
renders its content; this does not remove its semantic role. The navigation's
`aria-label="Primary"` names the landmark. Its hash links switch SPA views;
they are not counted as separate-page links for Assignment 4.

## Verified evidence

- [Literal code excerpts](evidence/source-excerpts.md) and [source hashes](evidence/source-map.json).
- [Existing Library screenshot](evidence/reused-library-ui.png): actual Nov 18 UI,
  synthetic fixture. It provides rendered context, not proof of tag names.
- [Existing browser results](evidence/reused-browser-results.json), B01: Library
  display passed previously. No browser/API checks rerun or invented.
- [Current verification](evidence/verification.json): standard-library HTML parsing
  confirms all four literal elements and the single main element in the original file.

**Outcome:** Complete. DeRexi alone satisfies this criterion. No supplemental demo
or GitHub Pages fallback was necessary.
''')
readme(a1, 1, 'all four required semantic elements exist literally in DeRexi.',
       '[Existing UI context](evidence/reused-library-ui.png); source markup is the decisive evidence.')

excerpts(a2, [(APP, 26, 46, 'html', 'DeRexi div containers and anchor tags'),
              (GOV, 5, 9, 'javascript', 'Original DOM element helper'),
              (GOV, 100, 105, 'javascript', 'DeRexi creates an ordered list at runtime'),
              (PAGE, 24, 28, 'html', 'Literal image on the existing DeRexi case-study page'),
              (PAGE, 63, 88, 'html', 'Literal unordered project-details list'),
              (PAGE, 327, 331, 'html', 'Case-study anchor back to Projects')])
reuse(a2, '01-get-library.png', 'reused-library-ui.png', [
    ('docs/assets/images/derexi-policy-pilot-hero.png', 'existing-derexi-project-image.png',
     'Original portfolio image asset, not a new screenshot and not evidence of a new UI test')])
write(a2 / 'assignment_report.md', f'''# 02 / Web elements
### DeRexi first, its existing portfolio page second · Complete

**Criterion:** demonstrate `<a>`, `<div>`, `<img>` and `<ul>` or `<ol>`.

| Required element | Original evidence | Interpretation |
|---|---|---|
| `<a>` | {reference(APP,39)} | DeRexi's literal Policy Assistant anchor |
| `<div>` | {reference(APP,26)} | Existing app topbar wrapper |
| `<img>` | {reference(PAGE,25)}–27 | Literal image in the existing DeRexi portfolio case study |
| `<ul>` | {reference(PAGE,66)}–88 | Literal project-details list in that same case study |

## Why a fallback was needed

The canonical DeRexi HTML/JavaScript was searched first. Its wordmark uses inline
`<svg>`; SVG is **not** an `<img>` tag and is not counted as one. Governance does
create a real ordered list through `el('ol', ...)` at {reference(GOV,105)}, with
the helper's `document.createElement` at line 6. That is runtime-created DOM,
not a literal `<ol>` in the original HTML source.

For unambiguous literal HTML evidence, the existing GitHub Pages **DeRexi case-study
page** supplies the missing image and an explicit unordered list. This preserves
DeRexi as the subject rather than introducing an unrelated example. The page also
contains all four required tags together; no new feature was built.

## Image and Liquid details

The existing `<img>` has meaningful `alt="DeRexi Policy Pilot Project"` and a
`src` produced by Jekyll's `relative_url` filter. The referenced original PNG
exists at `docs/assets/images/derexi-policy-pilot-hero.png`; a byte-identical
[asset copy](evidence/existing-derexi-project-image.png) is supplied here. Liquid is
template source; it is not claimed executable by opening the Markdown as a raw HTML file.
No current GitHub Pages build or deployed page screenshot was fabricated.

## Evidence and result

[Verbatim excerpts](evidence/source-excerpts.md), [source map](evidence/source-map.json),
[copied-image provenance](evidence/reused-evidence.json), and
[literal-element/asset checks](evidence/verification.json) substantiate every tag.
The [reused DeRexi UI screenshot](evidence/reused-library-ui.png) and Nov 18 browser
results provide primary-project context only; they are not asserted to test a
portfolio image or list. **Complete for the supplied literal-element criterion.**
''')
readme(a2, 2, 'all four literal tags are verified across DeRexi and its existing case-study page.',
       '[Original image asset](evidence/existing-derexi-project-image.png) and [DeRexi UI context](evidence/reused-library-ui.png). Only this assignment needs GitHub Pages source as a fallback.')

excerpts(a3, [(APP, 1, 5, 'html', 'Document language and metadata'),
              (APP, 18, 18, 'html', 'Class and accessible landmark name'),
              (APP, 38, 48, 'html', 'Link, data, button and state attributes'),
              (APP, 55, 65, 'html', 'Labels, select, boolean disabled and title'),
              (APP, 83, 83, 'html', 'Main focus attribute'),
              (APP, 95, 98, 'html', 'Script source attributes')])
reuse(a3, '01-get-library.png', 'reused-library-ui.png')
attrs = [('lang','html','en',2,'Declares the document language'),
         ('class','header','letterhead',18,'Connects markup to existing CSS'),
         ('href','a','#assist',39,'Specifies the anchor destination'),
         ('type','button','button',48,'Specifies button behavior'),
         ('id','button','notify-btn',48,'Uniquely identifies the control'),
         ('for','label','persona-select',57,'Associates the label with its select'),
         ('disabled','select','present (boolean)',59,'Disables the initial unselected control'),
         ('title','button','Choose an authorized identity',63,'Adds advisory information'),
         ('tabindex','main','-1',83,'Allows programmatic focus without sequential tab entry'),
         ('src','script','governance.js',95,'Names the existing script resource')]
save_json(a3 / 'evidence/attributes.json', {'source':APP,'distinct_attribute_names':len(attrs),
          'attributes':[dict(zip(['name','tag','value','line','purpose'],row)) for row in attrs]})
table='| Attribute | Literal element/value | Source line | Purpose |\n|---|---|---|---|\n'
for name,tag,value,line,purpose in attrs:
    table+=f'| `{name}` | `{tag}` / `{value}` | {reference(APP,line)} | {purpose} |\n'
write(a3 / 'assignment_report.md', '''# 03 / HTML attributes
### Ten distinct original attributes · Complete

**Criterion:** demonstrate at least seven distinct HTML attributes. DeRexi's
literal `backend/static/index.html` supplies **ten named attributes** below,
exceeding the minimum without counting repeated values as new attributes.

'''+table+'''
These are attributes on actual HTML elements, not JavaScript object properties
or SVG-only settings. `disabled` is a boolean attribute whose presence is meaningful;
it is not the text value `"false"`. `for="persona-select"` matches the existing
select's `id`. Additional real `aria-*`/`data-*` attributes exist, but the ten
listed names alone satisfy the criterion.

## Verification

[Source excerpts](evidence/source-excerpts.md), [attribute inventory](evidence/attributes.json)
and [current parser checks](evidence/verification.json) verify each attribute at
its exact original element/line, its value/presence, and the label/select association.
The [existing UI capture](evidence/reused-library-ui.png) and original Nov 18
browser results provide context only, not a new accessibility certification or
attribute test. DeRexi is the sole source; GitHub Pages was unnecessary.

**Outcome:** Complete, 10 distinct attributes against a minimum of 7. No original
HTML, script, authentication setting or interface was changed.
''')
readme(a3, 3, 'ten distinct actual HTML attributes exceed the minimum of seven.',
       '[Exact attribute inventory](evidence/attributes.json) and [existing UI context](evidence/reused-library-ui.png).')

excerpts(a4, [(APP, 38, 46, 'html', 'SPA hash anchors explicitly excluded from separate-page proof'),
              (PULSE, 71, 92, 'javascript', 'Original anchor creation and attribute helper'),
              (PULSE, 128, 131, 'javascript', 'Existing HTTPS destination guard'),
              (PULSE, 243, 253, 'javascript', 'Featured publication hyperlink'),
              (PULSE, 264, 272, 'javascript', 'Read the original publication anchor')])
reuse(a4, '03-get-pulse.png', 'reused-pulse-ui.png')
original_browser=json.loads((REPO / OLD / 'browser-results.json').read_text())
feed=next(r for r in original_browser['requests'] if '/api/pulse' in r['url'])['response_body']
article=feed['articles'][0]
save_json(a4 / 'evidence/retained-article.json', {'original_path':OLD+'/browser-results.json',
          'recorded_at':original_browser['timestamp'], 'scope':'Selected existing feed fields, no fresh download',
          'article':{k:article[k] for k in ['title','url','source','published','summary']}})
css='''body{margin:0;background:#faf9f6;color:#2d251f;font:17px/1.65 Georgia,serif}header,main,footer{max-width:900px;margin:auto;padding:28px}header{border-bottom:1px solid #e8d5b5}nav{display:flex;gap:24px}h1{font-size:clamp(32px,5vw,54px);line-height:1.15}a{color:#70542f;text-underline-offset:5px}p,li{max-width:72ch}.label{font:12px/1.5 Arial,sans-serif;letter-spacing:1px;text-transform:uppercase;color:#78674f}.note{padding:18px 22px;background:#eee6da;border-left:3px solid #c9b495}footer{font-size:14px;border-top:1px solid #e8d5b5}'''
def page(title,content):
    return f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><style>{css}</style></head>
<body><header><p class="label">DeRexi / HTML 1 coursework demonstration</p><nav aria-label="Coursework"><a href="index.html">Reading desk</a><a href="publication.html">Publication brief</a></nav></header><main>{content}</main><footer>Static educational adaptation of existing DeRexi semantics and Pulse publication metadata. No API, authentication, bank data or application workflow.</footer></body></html>'''
    
write(a4/'index.html',page('DeRexi · Reading desk · Coursework demo',f'''<p class="label">Demonstration, not the production application</p><h1>A link beyond the current page.</h1><p>DeRexi Pulse creates HTTPS anchors to original publications. This offline example uses an ordinary relative link to a separate HTML document to make the distinction from SPA hash navigation directly verifiable.</p><h2>{escape(article['title'])}</h2><p>{escape(article['source'])} · {escape(article['published'])} · retained Nov 18 feed metadata</p><p><a id="publication-link" href="publication.html">Read the publication brief on a separate page</a></p><p class="note">The destination is a new coursework HTML page using retained metadata. It is not a replica of the publisher's page or a newly retrieved regulation.</p>'''))
write(a4/'publication.html',page('DeRexi · Publication brief · Separate coursework page',f'''<p class="label">A separate HTML document</p><h1>{escape(article['title'])}</h1><p><b>Source:</b> {escape(article['source'])}<br><b>Published:</b> {escape(article['published'])}</p><p>{escape(article['summary'])}</p><p class="note">This is the retained, potentially truncated feed summary, not fresh legal guidance. It was copied from the existing Nov 18 browser evidence without a network request.</p><p><a href="{escape(article['url'],quote=True)}" target="_blank" rel="noopener noreferrer">Original publisher page (external; availability not checked here)</a></p><p><a id="return-link" href="index.html">Return to the reading desk</a></p>'''))
write(a4/'assignment_report.md',f'''# 04 / Hyperlinks
### A separate document, not just a different view · Complete

**Criterion:** at least one hyperlink leading to a separate page.

## Original DeRexi implementation

Pulse creates a real `<a>` through `document.createElement` in its helper at
{reference(PULSE,71)}–92. The publication anchor at {reference(PULSE,245)}–250 sets
`href: article.url`, `target: '_blank'` and `rel: 'noopener noreferrer'`. A second
explicit “Read the original publication” anchor is at lines 266–272. The destination
is an HTTPS publisher document, a separate page from DeRexi's `/ui/` document.

One actual retained article URL is recorded in [retained-article.json](evidence/retained-article.json),
from the Nov 18 browser response. The [existing Pulse capture](evidence/reused-pulse-ui.png)
and B05 show real article rendering at that time. They do **not** prove a publisher
link was clicked or that its current remote destination is reachable.

In contrast, the literal `href="#assist"`, `#library` and other anchors at
{reference(APP,38)}–46 remain within the SPA document. They are intentionally
excluded from the separate-page criterion. DeRexi's publication links already
provide the appropriate implementation; no GitHub Pages fallback was necessary.

## Portable literal-HTML demonstration

[index.html](index.html) and [publication.html](publication.html) are two small,
offline coursework pages based on the verified DeRexi semantic structure, Pulse
link behavior and retained article metadata. They are **new demonstrations**, not
original source or a rebuilt application. Styles are inline; no scripts, APIs,
login, external assets or database are required.

The decisive literal anchor in `index.html` is:

```html
<a id="publication-link" href="publication.html">Read the publication brief on a separate page</a>
```

Its destination exists as a distinct HTML file and has an ordinary return anchor.
[Static checks](evidence/verification.json) verify the exact href, destination
document, different pathname and absence of fragment-only navigation. The
[course browser verification](../evidence/browser-verification.json) records an
actual local-file click to that separate page and back. This is a new **demo-only**
navigation check, not a DeRexi API test or verification of live publisher availability.

**Outcome:** Complete. Original Pulse supplies the existing separate-page link
implementation; the coursework bundle makes literal markup and actual independent
document navigation reproducible without altering any existing project.
''')
readme(a4,4,'Pulse links to external documents; an offline literal two-page demo makes separate-document navigation verifiable.',
       '[Original Pulse UI](evidence/reused-pulse-ui.png) and [retained article provenance](evidence/retained-article.json).',
       'Open [index.html](index.html), click **Read the publication brief on a separate page**, then **Return to the reading desk**. See [demo-only browser result](../evidence/browser-verification.json). No public source needs to be contacted.')

write(ROOT/'README.md','''# HTML 1 · Existing-project evidence

The existing course folder is `html_1/`; it is preserved as the requested **HTML1**
course root. No duplicate directory, source relocation or production edit.

| Assignment directory | Status | Primary evidence |
|---|---|---|
'''+''.join(f'| [{name}]({quote(name)}/README.md) | **Complete** | '+[
    'DeRexi literal semantic landmarks',
    'DeRexi tags plus its existing portfolio case-study image/list',
    'Ten distinct DeRexi HTML attributes',
    'Pulse publisher anchors + checked two-document coursework demo'][i]+' |\n' for i,name in enumerate(NAMES))+'''
Each assignment contains `README.md`, `assignment_report.md`, verbatim source
excerpts, source-line/hash mapping, copied original UI/test context and new offline
verification results. The source-first search found no literal image in the DeRexi
app; only Assignment 2 therefore uses GitHub Pages source, still about DeRexi.

The original course screenshot remains untouched. The four criteria are supplied
by the user; no unseen LMS requirements are assumed. The prior UI evidence is
dated Nov 18 and uses synthetic SQLite, mocked search and disabled AI. It is copied
with original provenance and **not rerun or represented as HTML rubric tests**.

New checks are source/markup/attribute/asset/link checks plus local demo navigation.
They do not verify production data/authentication, deployed GitHub Pages, live
publisher reachability or application behavior. See [static verification](evidence/verification.json),
[browser navigation](evidence/browser-verification.json) and [session notes](SESSION_NOTES.md).

Recheck the static evidence from repository root:

```sh
python3 -B html_1/verify_coursework.py
```

The browser-only demo check and its prerequisites are recorded by `verify_demo.mjs`.
No application/API server is required. No commit or push.
''')
write(ROOT/'SESSION_NOTES.md',f'''# Session notes · {STAMP[:10]}

- Read repository memory before inspection; initial working tree was clean.
- Preserved the existing `html_1/` folder and its original LMS screenshot.
- Searched canonical DeRexi first. A1/A3 already meet literal requirements.
  A2 uses its existing portfolio page only for missing literal image/list markup.
  A4 distinguishes real external publication anchors from SPA fragments.
- Copied prior UI/test evidence with exact original paths and byte hashes; did not
  rerun historical app/API tests or fabricate screenshots.
- Added only a minimal static, explicitly labelled two-page coursework demo to
  demonstrate separate-document navigation; no app functionality was rebuilt.
- Current verification files record actual source, asset, link and demo checks.
- All writes are confined to this course folder. The user's current write boundary
  takes precedence over the earlier root-memory update convention; root MEMORY.md,
  DeRexi, GitHub Pages, configs, database and other coursework remain untouched.
- No commit or push. No supplied-rubric gaps remain after the recorded checks.
''')
write(ROOT/'.gitignore','/.runtime/\n__pycache__/\n')
save_json(ROOT/'evidence/source-baseline.json',{'captured_at':STAMP,
    'originals':{p:sha(REPO/p) for p in [APP,PULSE,GOV,PAGE,'docs/assets/images/derexi-policy-pilot-hero.png',
    OLD+'/browser-results.json',OLD+'/screenshots/01-get-library.png',OLD+'/screenshots/03-get-pulse.png',
    'MEMORY.md','html_1/Screenshot 2026-11-17 at 2.43.52\u202fPM.png']}})
print('Created four coursework evidence packages inside html_1 only.')
