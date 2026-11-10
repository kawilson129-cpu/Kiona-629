"""Supabase password sessions using HttpOnly cookies; no signup or employee writes."""
import hashlib
import json
import os
import time
from collections import OrderedDict
from threading import Lock
from urllib import request as http
from urllib.error import HTTPError
from urllib.parse import urlsplit

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from sqlalchemy.orm import Session
import dev_auth
from database import get_db
from security import get_identity, resolve_identity, subject_bindings, verify_token

router = APIRouter(tags=['authentication'])
_ATTEMPTS = OrderedDict()
_LOCK = Lock()


class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    email: str = Field(min_length=3, max_length=254, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    password: SecretStr = Field(min_length=1, max_length=1024)


def settings():
    origin = (os.getenv('SUPABASE_URL') or '').rstrip('/')
    parsed = urlsplit(origin)
    key = os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY') or ''
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise HTTPException(503, 'Sign-in is not configured')
    valid_key = key.startswith('sb_publishable_')
    if not valid_key:
        try:
            # This checks the configured public key type, never authenticates a user.
            valid_key = jwt.decode(key, options={'verify_signature': False}).get('role') == 'anon'
        except Exception:
            valid_key = False
    if not valid_key or not subject_bindings():
        raise HTTPException(503, 'Sign-in is not configured')
    if dev_auth.current_environment() not in {'development','test'}:
        public = urlsplit(os.getenv('DEREXI_PUBLIC_ORIGIN', ''))
        if public.scheme != 'https' or not public.hostname or public.path or public.query or public.fragment or public.username:
            raise HTTPException(503, 'Sign-in is not configured')
    return origin, key


def public_configuration():
    try:
        settings()
        return {'sign_in_enabled': True}
    except HTTPException:
        return {'sign_in_enabled': False}


def require_same_origin(request):
    expected = os.getenv('DEREXI_PUBLIC_ORIGIN') or f'{request.url.scheme}://{request.url.netloc}'
    if request.headers.get('origin') != expected or request.headers.get('x-derexi-request') != '1':
        raise HTTPException(403, 'Same-origin request required')
    local = (dev_auth.current_environment() in {'development','test'}
             and request.url.hostname in {'localhost','127.0.0.1','::1','testserver'}
             and dev_auth._is_loopback(request.client.host if request.client else None))
    if request.url.scheme != 'https' and not local:
        raise HTTPException(403, 'HTTPS is required')


def throttle(request):
    peer = hashlib.sha256((request.client.host if request.client else 'unknown').encode()).digest()
    now = time.monotonic()
    with _LOCK:
        since, count = _ATTEMPTS.get(peer, (now, 0))
        count = count + 1 if now - since < 60 else 1
        if now - since >= 60: since = now
        _ATTEMPTS[peer] = (since, count)
        _ATTEMPTS.move_to_end(peer)
        if len(_ATTEMPTS) > 2048: _ATTEMPTS.popitem(last=False)
        if count > 8:
            raise HTTPException(429, 'Too many sign-in attempts. Please wait and try again.', headers={'Retry-After':'60'})


class NoRedirect(http.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def provider_request(path, payload=None, access_token=None):
    origin, key = settings()
    headers = {'apikey': key, 'Content-Type':'application/json'}
    if access_token: headers['Authorization'] = 'Bearer ' + access_token
    req = http.Request(origin + '/auth/v1/' + path, method='POST',
                       headers=headers, data=json.dumps(payload or {}).encode())
    try:
        with http.build_opener(NoRedirect()).open(req, timeout=6) as result:
            raw = result.read(131073)
            if len(raw) > 131072: raise ValueError()
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        if exc.code in {400,401,403,422}:
            raise HTTPException(401, 'Sign-in failed. Check your credentials.')
        if exc.code == 429:
            raise HTTPException(429, 'Too many sign-in attempts. Please try again later.')
        raise HTTPException(503, 'Sign-in service is temporarily unavailable')
    except Exception:
        raise HTTPException(503, 'Sign-in service is temporarily unavailable')


def clear_cookies(response, request):
    for name, path in (('derexi_access','/'), ('derexi_refresh','/auth')):
        response.delete_cookie(name, path=path, httponly=True, secure=request.url.scheme == 'https', samesite='strict')


def establish(request, response, data, db):
    access, refresh = data.get('access_token'), data.get('refresh_token')
    if not isinstance(access, str) or not isinstance(refresh, str) or not refresh:
        raise HTTPException(503, 'Sign-in service is temporarily unavailable')
    claims, source = verify_token(access)
    if source != 'supabase': raise HTTPException(401, 'Invalid sign-in session')
    identity = resolve_identity(request, claims, source, db)
    secure = request.url.scheme == 'https'
    for name, value, path, ttl in [('derexi_access',access,'/',max(0,int(claims['exp']-time.time()))),
                                    ('derexi_refresh',refresh,'/auth',604800)]:
        response.set_cookie(name,value,max_age=ttl,httponly=True,secure=secure,samesite='strict',path=path)
    response.headers['Cache-Control'] = 'no-store'
    return {'authenticated':True,'user':{'id':identity.user_id,'full_name':identity.full_name,'role':identity.role}}


@router.post('/auth/login')
def login(payload: Credentials, request: Request, response: Response, db: Session = Depends(get_db)):
    require_same_origin(request)
    throttle(request)
    data = provider_request('token?grant_type=password', {'email':payload.email,'password':payload.password.get_secret_value()})
    return establish(request,response,data,db)


@router.get('/auth/session')
def session(response: Response, identity=Depends(get_identity)):
    response.headers['Cache-Control'] = 'no-store'
    return {'authenticated':True,'user_id':identity.user_id}


@router.post('/auth/refresh')
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    require_same_origin(request)
    token = request.cookies.get('derexi_refresh')
    if not token: raise HTTPException(401, 'Sign-in required')
    data = provider_request('token?grant_type=refresh_token', {'refresh_token':token})
    return establish(request,response,data,db)


@router.post('/auth/logout')
def logout(request: Request, db: Session = Depends(get_db)):
    require_same_origin(request)
    response = JSONResponse({'signed_out':True})
    access = request.cookies.get('derexi_access')
    if access:
        try:
            claims,source = verify_token(access)
            if source == 'supabase': resolve_identity(request,claims,source,db)
        except HTTPException:
            pass  # Expired/unmapped sessions must still be clearable.
        try:
            provider_request('logout?scope=local', access_token=access)
        except HTTPException:
            response = JSONResponse({'signed_out':True,'provider_revoked':False,
                'detail':'Signed out locally. Remote session revocation could not be confirmed.'},status_code=503)
    clear_cookies(response,request)
    response.headers['Cache-Control'] = 'no-store'
    return response
