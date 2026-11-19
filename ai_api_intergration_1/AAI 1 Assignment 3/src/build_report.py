"""Build Item 3 from the existing sanitized transcript; preserve supplied PDFs."""
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT.parent
EVIDENCE = COURSE / 'AAI 1 Assignment 1/evidence/20261118-api'
DATA = json.loads((EVIDENCE / 'http-results.json').read_text(encoding='utf-8'))
GET = next(r for r in DATA['requests'] if r['url'].endswith('/policies') and r['status_code'] == 200)
POST = next(r for r in DATA['requests'] if r['url'].endswith('/ask') and r['status_code'] == 200)
INK = colors.HexColor('#2D251F')
GOLD = colors.HexColor('#A5783D')
PAPER = colors.HexColor('#F8F5EF')
MUTED = colors.HexColor('#776D63')
LINE = colors.HexColor('#E4D7C5')

for name, filename in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Title','georgia.ttf'),('Italic','georgiai.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))

OUTPUT = ROOT / 'AI_API_Integration_1_Rubric_03_Report.pdf'
C = canvas.Canvas(str(OUTPUT), pagesize=(612, 792), pageCompression=1)
C.setTitle('DeRexi - Structuring API Requests and Responses')
C.setAuthor('Kiona Wilson | Aurum Capital Bank / DeRexi coursework')


def text(value, x, y, size=10, font='Body', color=INK, width=526):
    style = ParagraphStyle('p', fontName=font, fontSize=size, leading=size*1.4, textColor=color)
    para = Paragraph(value, style)
    _, height = para.wrap(width, 700)
    para.drawOn(C, x, y-height)
    return y-height


def label(value, y):
    return text(value, 43, y, 10, 'Bold')-10


def table(rows, widths, y, sizes=9.3):
    formatted = [[Paragraph(escape(str(v)).replace('\n','<br/>'), ParagraphStyle('cell',fontName='Body',fontSize=sizes,leading=sizes*1.4,textColor=INK)) for v in row] for row in rows]
    obj = Table(formatted, colWidths=widths, hAlign='LEFT')
    obj.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDE5D9')),
        ('LINEBELOW',(0,0),(-1,-1),0.45,LINE), ('LEFTPADDING',(0,0),(-1,-1),9),
        ('RIGHTPADDING',(0,0),(-1,-1),9), ('TOPPADDING',(0,0),(-1,-1),9),
        ('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    _, height = obj.wrap(526, 700)
    obj.drawOn(C,43,y-height)
    return y-height


def code(value, x, y, width):
    for line in value.splitlines():
        y=text(escape(line).replace(' ','&nbsp;'),x,y,8.7,'Courier',width=width)-1
    return y


def header(title, subtitle, page):
    C.setFillColor(PAPER); C.rect(0,0,612,792,fill=1,stroke=0)
    C.setFillColor(INK); C.rect(0,783,612,9,fill=1,stroke=0)
    text('AURUM CAPITAL BANK / DeRexi',43,761,9,'Bold',GOLD)
    C.setFillColor(colors.HexColor('#E1ECE5')); C.roundRect(456,734,113,27,10,fill=1,stroke=0)
    text('VERIFIED / LOCAL',467,754,8,'Bold',colors.HexColor('#426951'),width=100)
    text('AI API INTEGRATION 1',43,735,9,color=MUTED)
    text(title,43,709,27,'Title')
    text(subtitle,43,665,11,'Italic',GOLD)
    C.setStrokeColor(LINE); C.line(43,641,569,641)
    C.line(43,75,569,75)
    text('VERIFICATION SCOPE',43,65,7.4,'Bold',GOLD)
    text('Local HTTP / synthetic SQLite / search mocked / external AI disabled.',43,51,8,color=MUTED)
    text('Production Supabase and live AI-provider responses remain unverified.',43,38,8,color=MUTED)
    text(f'03 / 04  |  {page} / 2',480,65,8,'Bold',GOLD,width=90)


header('Requests & responses','A question in. Structured guidance out.',1)
y=label('THE REQUEST / RESPONSE LIFECYCLE',621)
y=table([['1 / CLIENT','2 / VALIDATE','3 / PROCESS','4 / DISPLAY'],
         ['GET a resource or POST JSON.','Verify signed identity; validate schema and role.','Read policies or persist a fixture conversation.','Return JSON + status; render rows or guidance.']], [131.5]*4,y,9)
y=label('TWO EXISTING ENDPOINTS',y-22)
y=table([['Method / URL','Request','Actual response'],
         ['GET\nhttp://127.0.0.1:8041/policies','Accept: application/json\nAuthorization: Bearer [REDACTED]\nBody: none','200 OK\nJSON array -> Policy Library'],
         ['POST\nhttp://127.0.0.1:8041/ask','Same headers, plus\nContent-Type: application/json\nJSON question below','200 OK\nJSON object -> Assistant']], [190,210,126],y,9)
y=label('ACTUAL POST BODY',y-21)
y=code(json.dumps(POST['request_body'],indent=2),52,y,508)
y=text('Both successful responses have <b>Content-Type: application/json</b> and <b>Cache-Control: no-store</b>. GET retrieves data; this POST creates conversation/message/clarification records in the disposable database. The existing contract returns 200, not 201.',43,y-12,9.3)
y=text('Evidence: H04, H07-H09 and B02/B03/B06, captured November 18, 2026. No new application run was needed. Full sanitized exchanges: Assignment 1 / api-evidence.md and evidence/20261118-api/http-results.json.',43,y-14,8.6,color=MUTED)
assert y>85, f'Page 1 overflow: {y}'
C.showPage()

header('JSON, identity & errors','Explicit contracts make the exchange explainable.',2)
y=label('OBSERVED SUCCESS RESPONSES / SELECTED FIELDS',621)
get_fields={k:GET['response_body'][1][k] for k in ('id','title','owner','latest_version')}
post_fields={k:POST['response_body'][k] for k in ('conversation_id','citations','needs_clarification','clarification_request_id','confidence')}
text('GET / one of two policy records',43,y,9,'Bold')
text('POST / routing and resource fields',310,y,9,'Bold',width=259)
left=code(json.dumps([get_fields],indent=2),43,y-21,246)
right=code(json.dumps(post_fields,indent=2),310,y-21,259)
y=min(left,right)-12
y=text('<b>Actual answer:</b> '+escape(POST['response_body']['answer']),43,y,9.3)
y=text('The answer is deterministic clarification, not an AI-provider response. Remaining fields are shown in the full transcript; the excerpts above intentionally select fields.',43,y-8,8.6,color=MUTED)
y=label('OBSERVED AUTHENTICATION / VALIDATION ERRORS',y-20)
error_rows=[['Request condition','Status','Actual JSON detail']]
for r in DATA['requests']:
    if r['status_code'] in (401,422,403,404):
        condition={401:'GET /policies: no bearer',422:'POST /ask: question is whitespace',403:'POST /ask: user_id 2 with employee 8 identity',404:'GET /conversations/1: another employee'}[r['status_code']]
        error_rows.append([condition,str(r['status_code']),json.dumps(r['response_body'])])
y=table(error_rows,[217,43,266],y,8.5)
y=text('<b>Identity:</b> the server derives the user from the verified token. The test-only, loopback POST /dev-auth/token issues a signed development token; it does not prove production sign-in. Missing credentials include a WWW-Authenticate: Bearer challenge.',43,y-14,9)
y=text('<b>Schema (source inspected):</b> question is trimmed and limited to 2-1,000 characters; topic is optional (max 1,000). A legacy user_id must match the authenticated identity. Other /ask branches exist but were not observed in this fixture.',43,y-10,9)
y=text('Evidence: H02/H03, H10-H12; existing main.py / schemas.py; api-evidence.md. Item 3 COMPLETE within the supplied request/response criterion. Original browser screenshot 02 shows this guidance; a new documentation-panel screenshot is optional.',43,y-11,8.4,color=MUTED)
assert y>85, f'Page 2 overflow: {y}'
C.save()
print(OUTPUT)
