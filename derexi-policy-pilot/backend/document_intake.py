"""Bounded, non-executing document text intake and optional private originals.

Original files are never mounted by StaticFiles. Parser subprocesses have a hard
wall-clock limit. No OCR, macros, hyperlinks, embedded objects or PDF actions run.
"""
import hashlib
import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
import unicodedata
import zipfile
from dataclasses import dataclass
from fastapi import HTTPException

log=logging.getLogger(__name__)
MAX_BYTES=5*1024*1024
MAX_TEXT=20000
TTL=20*60
PDF_MIME='application/pdf'
DOCX_MIME='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
POLICY_SECTIONS=('Purpose','Scope','Policy requirements','Responsibilities','Exceptions','Related guidance')
TEMPLATES=[
 {'id':'standard','name':'Standard policy','description':'A clear foundation for department policies.',
  'body':'Purpose\nDescribe why this policy is required.\n\nScope\nIdentify the people, systems and activities covered.\n\nPolicy requirements\nSet out mandatory controls and procedures.\n\nResponsibilities\nIdentify accountable roles.\n\nExceptions\nExplain how exceptions are requested and reviewed.\n\nRelated guidance\nList relevant regulations and supporting policies.'},
 {'id':'information-security','name':'Information security','description':'Controls, responsibilities and incident escalation.',
  'body':'Purpose\nProtect the confidentiality, integrity and availability of bank information.\n\nScope\nDefine covered information, systems and staff.\n\nPolicy requirements\nDescribe access controls, handling requirements and incident reporting.\n\nResponsibilities\nAssign control owners and oversight.\n\nExceptions\nDefine approval and expiry requirements.\n\nRelated guidance\nIdentify applicable safeguards and supporting procedures.'},
 {'id':'operating-procedure','name':'Operating procedure','description':'Repeatable procedures with clear ownership.',
  'body':'Purpose\nDescribe the intended outcome.\n\nScope\nDefine when this procedure applies.\n\nPolicy requirements\n1. Record the request.\n2. Verify required approvals.\n3. Complete and document the activity.\n\nResponsibilities\nIdentify who performs and oversees each step.\n\nExceptions\nDescribe escalation when requirements cannot be met.\n\nRelated guidance\nList supporting policies and records.'}]

class DocumentError(ValueError):pass


def normalize(text):
    text=unicodedata.normalize('NFKC',text).replace('\r\n','\n').replace('\r','\n')
    text=''.join(c for c in text if c in '\n\t' or unicodedata.category(c)[0]!='C')
    lines=[' '.join(line.split()) for line in text.splitlines()]
    return '\n'.join(lines).strip()


def standardize(text):
    """Preserve extracted words; group unstructured text without inventing policy."""
    text=normalize(text)
    if not text:raise DocumentError('No readable text was found. Upload a text-based document or create a policy manually.')
    words={line.strip().lower().rstrip(':') for line in text.splitlines()}
    if {'purpose','scope','policy requirements'}.issubset(words):return text
    return ('Purpose\n[Add the purpose of this policy.]\n\nScope\n[Define who and what this policy covers.]\n\n'
            'Policy requirements\n'+text+'\n\nResponsibilities\n[Identify accountable roles.]\n\n'
            'Exceptions\n[Describe the exception process.]\n\nRelated guidance\n[Add applicable regulations and policies.]')


def extract_docx(data):
    from defusedxml import ElementTree as ET
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            items=z.infolist()
            if len(items)>256 or len({x.filename for x in items})!=len(items):raise DocumentError('This document contains an unsupported archive structure.')
            total=0
            for item in items:
                name=item.filename.lower()
                if item.flag_bits & 1 or item.filename.startswith(('/', '\\')) or '..' in Path(item.filename.replace('\\','/')).parts:
                    raise DocumentError('This document contains an unsupported archive structure.')
                total+=item.file_size
                if total>12*1024*1024 or item.file_size>4*1024*1024 or item.file_size/max(item.compress_size,1)>150:
                    raise DocumentError('This document exceeds the processing limits.')
                if any(x in name for x in ('vbaproject','/embeddings/','/activex/','externallink','attachedtemplate')):
                    raise DocumentError('Upload a document without macros or embedded files.')
            if '[Content_Types].xml' not in z.namelist() or 'word/document.xml' not in z.namelist():raise DocumentError('The uploaded file is not a valid DOCX document.')
            for item in items:
                if item.filename.endswith(('.xml','.rels')):
                    raw=z.read(item)
                    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise DocumentError('This document contains unsupported XML content.')
                    tree=ET.fromstring(raw)
                    if item.filename.endswith('.rels'):
                        for rel in tree:
                            if rel.attrib.get('TargetMode','').lower()=='external' and not rel.attrib.get('Type','').endswith('/hyperlink'):
                                raise DocumentError('Upload a document without external templates or linked content.')
                    if item.filename=='[Content_Types].xml' and b'macroenabled' in raw.lower():raise DocumentError('Macro-enabled documents are not supported.')
            tree=ET.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs=[''.join(n.text or '' for n in p.findall('.//w:t',ns)) for p in tree.findall('.//w:p',ns)]
            return '\n'.join(paragraphs)
    except DocumentError:raise
    except Exception:raise DocumentError('The DOCX document could not be read. Export a fresh copy and try again.')


def extract_pdf(data):
    from pypdf import PdfReader
    try:
        reader=PdfReader(io.BytesIO(data),strict=True)
        if reader.is_encrypted:raise DocumentError('Password-protected PDFs are not supported. Upload an unprotected text copy.')
        root=reader.trailer['/Root']
        names=root.get('/Names')
        if '/OpenAction' in root or '/AA' in root or (names and any(k in names.get_object() for k in ('/JavaScript','/EmbeddedFiles'))):
            raise DocumentError('Upload a PDF without active content or embedded files.')
        if len(reader.pages)>50:raise DocumentError('Upload a PDF with 50 pages or fewer.')
        parts=[]
        for page in reader.pages:
            if '/AA' in page:raise DocumentError('Upload a PDF without active content.')
            for ref in page.get('/Annots',[]):
                annotation=ref.get_object()
                if '/A' in annotation or '/AA' in annotation or annotation.get('/Subtype')=='/FileAttachment':
                    raise DocumentError('Upload a PDF without interactive actions or attachments.')
            content=page.get_contents()
            if content and len(content.get_data())>2*1024*1024:raise DocumentError('This PDF page exceeds the processing limits.')
            parts.append(page.extract_text() or '')
            if sum(map(len,parts))>MAX_TEXT:raise DocumentError('The extracted text exceeds 20,000 characters. Split the document before uploading.')
        return '\n\n'.join(parts)
    except DocumentError:raise
    except Exception:raise DocumentError('The PDF could not be read. Export a text-based PDF and try again.')


def parse(data,kind):
    text=extract_pdf(data) if kind=='pdf' else extract_docx(data)
    body=standardize(text)
    if len(body)>MAX_TEXT:raise DocumentError('The policy exceeds 20,000 characters. Split the document before uploading.')
    return {'body':body,'extracted_text':normalize(text),'warnings':['Review extracted text, section headings and metadata before saving. Text extraction does not verify policy accuracy.']}


_parsers=threading.BoundedSemaphore(2)

def parse_bounded(data,kind):
    if not _parsers.acquire(blocking=False):
        raise DocumentError('Document intake is busy. Please try again shortly.')
    try:
        worker=subprocess.run([sys.executable,'-I',str(Path(__file__).resolve()),'--parse',kind],
            env={k:v for k,v in os.environ.items() if k.upper() in {'SYSTEMROOT','WINDIR','TEMP','TMP'}},
            input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=12,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except subprocess.TimeoutExpired:
        raise DocumentError('This document took too long to process. Upload a smaller text-based document.')
    finally:
        _parsers.release()
    if worker.returncode or len(worker.stdout)>250000:
        log.warning('Document parser subprocess failed or exceeded output limit')
        raise DocumentError('This document could not be processed safely. Export a fresh copy and try again.')
    result=json.loads(worker.stdout)
    if 'error' in result:raise DocumentError(result['error'])
    return result


def storage_root():
    configured=os.getenv('DEREXI_DOCUMENT_STORAGE_DIR','').strip()
    if not configured:return None
    path=Path(configured)
    if not path.is_absolute():raise OSError('Storage path must be absolute')
    path=path.resolve()
    repo=Path(__file__).resolve().parents[2]
    for public in (Path(__file__).resolve().parent/'static',repo/'docs'):
        if path==public or public in path.parents:raise OSError('Public storage paths are forbidden')
    if not path.is_dir() or not os.access(path,os.W_OK|os.R_OK):raise OSError('Private storage directory is unavailable')
    return path


def capabilities():
    parser=all(importlib.util.find_spec(name) for name in ('pypdf','defusedxml'))
    try:
        original=storage_root() is not None
        storage_state='available' if original else 'not_configured'
    except OSError:original=False;storage_state='unavailable'
    return {'upload_available':bool(parser) and storage_state!='unavailable','original_retention':original,
            'storage_state':storage_state,'max_bytes':MAX_BYTES,'formats':['docx','pdf']}

@dataclass
class Intake:
    user_id:int
    filename:str
    kind:str
    data:bytes
    digest:str
    expires:float
    retention:bool
    claimed:bool=False

_cache={}
_lock=threading.Lock()

def preview(data,filename,mime,user_id):
    if not capabilities()['upload_available']:raise HTTPException(503,'Document intake is temporarily unavailable. Please try again later.')
    filename=Path(filename.replace('\\','/')).name
    if not filename or len(filename)>180 or any(ord(c)<32 for c in filename):raise HTTPException(422,'Choose a document with a valid filename.')
    kind=filename.rsplit('.',1)[-1].lower()
    if kind not in ('docx','pdf') or (kind=='pdf' and mime!=PDF_MIME) or (kind=='docx' and mime!=DOCX_MIME):
        raise HTTPException(415,'Choose a DOCX or PDF document.')
    if not data or len(data)>MAX_BYTES:raise HTTPException(413,'Choose a document smaller than 5 MB.')
    if (kind=='pdf' and not data.startswith(b'%PDF-')) or (kind=='docx' and not data.startswith(b'PK\x03\x04')):
        raise HTTPException(422,'The file contents do not match the document type.')
    try:result=parse_bounded(data,kind)
    except DocumentError as e:raise HTTPException(422,str(e))
    token=secrets.token_urlsafe(32)
    with _lock:
        for key in list(_cache):
            if _cache[key].expires<time.monotonic():del _cache[key]
        if len(_cache)>=20 or sum(x.user_id==user_id for x in _cache.values())>=3:
            raise HTTPException(429,'Please finish or discard an existing document before uploading another.')
        _cache[token]=Intake(user_id,filename,kind,data,hashlib.sha256(data).hexdigest(),time.monotonic()+TTL,capabilities()['original_retention'])
    return {**result,'import_id':token,'filename':filename,'original_retention':_cache[token].retention,
            'suggested_title':normalize(filename.rsplit('.',1)[0].replace('_',' ').replace('-',' '))[:200],
            'expires_in_seconds':TTL}


def claim(token,user_id,confirmed):
    if not confirmed:raise HTTPException(422,'Confirm that you have reviewed the document before saving.')
    with _lock:
        item=_cache.get(token)
        if not item or item.user_id!=user_id or item.expires<time.monotonic():raise HTTPException(404,'The document preview has expired or is unavailable. Upload the document again.')
        if item.claimed:raise HTTPException(409,'This document is already being saved.')
        item.claimed=True
    return item


def retain(item):
    metadata={'filename':item.filename,'sha256':item.digest,'kind':item.kind,'retained':False}
    if item.retention:
        path=None
        try:
            root=storage_root()
            if root is None:raise OSError('Configured retention no longer available')
            key=secrets.token_hex(24)+'.'+item.kind
            path=root/key
            with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:f.write(item.data)
            metadata.update(retained=True,key=key)
        except OSError:
            if path:
                try:path.unlink(missing_ok=True)
                except OSError:log.error('Incomplete original cleanup required')
            log.exception('Private document retention failed')
            raise HTTPException(503,'The original document could not be stored securely. Your draft has not been saved.')
    return metadata


def release(token,metadata=None,success=False):
    with _lock:
        item=_cache.get(token)
        if success:_cache.pop(token,None)
        elif item:item.claimed=False
    if not success and metadata and metadata.get('retained'):
        try:
            root=storage_root()
            if root:(root/metadata['key']).unlink(missing_ok=True)
        except OSError:log.exception('Orphaned document cleanup required')


def discard(token,user_id):
    with _lock:
        item=_cache.get(token)
        if item and item.user_id==user_id and not item.claimed:_cache.pop(token,None)

if __name__=='__main__':
    # Parser has no database imports or credentials in its output.
    logging.disable(logging.CRITICAL)
    try:
        import runpy
        runpy.run_path(str(Path(__file__).with_name('document_limits.py')))['limit_parser']()
        result=parse(sys.stdin.buffer.read(MAX_BYTES+1),sys.argv[2])
    except DocumentError as exc:result={'error':str(exc)}
    except Exception:result={'error':'This document could not be processed safely.'}
    sys.stdout.buffer.write(json.dumps(result).encode('utf-8'))
