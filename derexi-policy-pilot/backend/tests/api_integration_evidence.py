"""Real loopback HTTP evidence for the existing DeRexi app; never production data.

serve: reuse messaging_fixture's in-memory SQLite, PostgreSQL tripwire and actual
routes/UI/auth. Its PostgreSQL search is explicitly stubbed to return no matches.
Public Pulse downloads are real, optional, allowlisted and recorded separately.
http: send actual socket requests, saving sanitized request/response transcripts.
All output is confined to the existing ai_api_intergration_1 course directory.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from threading import Lock

sys.dont_write_bytecode = True
BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parents[1]
COURSE = REPO / 'ai_api_intergration_1'
BASE = 'http://127.0.0.1:8041'
QUESTION = 'How should I handle a hypothetical policy exception?'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def output_path(value):
    result = Path(value).resolve()
    if not result.is_relative_to(COURSE.resolve()) or result == COURSE.resolve():
        raise ValueError('Evidence must be inside the existing course directory')
    return result


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def sanitized(value):
    if isinstance(value, dict):
        return {k: '[REDACTED]' if k.lower() in {
            'access_token', 'refresh_token', 'authorization', 'cookie', 'set-cookie'
        } else sanitized(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitized(v) for v in value]
    return value


def serve(out, live_public):
    out.mkdir(parents=True, exist_ok=False)
    # Only process-local settings; no .env or other secret files are modified.
    os.environ['OPENAI_API_KEY'] = ''
    os.environ['DEREXI_INCIDENT_AI'] = 'off'
    os.environ['DEREXI_OUTBOUND_EMAIL'] = 'off'
    os.environ['DEREXI_DEV_AUTH_SECRET'] = ''  # existing provider generates in memory
    sys.path[:0] = [str(BACKEND / 'tests'), str(BACKEND)]
    from messaging_fixture import isolated_database
    import main
    from database import get_db
    import pulse.sources as sources
    import urllib.request
    import uvicorn

    engine, factory = isolated_database()
    factory.configure(bind=engine)
    request_lock = Lock()

    def fixture_db():
        with request_lock, factory() as db:
            yield db

    main.app.dependency_overrides[get_db] = fixture_db
    original_open = urllib.request.urlopen
    allowed = {v['url']: k for k, v in sources.SOURCES.items()}
    network = []

    def observed_open(request, *args, **kwargs):
        url = getattr(request, 'full_url', str(request))
        if not live_public or url not in allowed:
            raise RuntimeError('External request disabled by isolated evidence fixture')
        item = {'timestamp': stamp(), 'source': allowed[url], 'method': 'GET',
                'url': url, 'request_headers': dict(request.header_items()),
                'request_body': None, 'mode': 'REAL PUBLIC NETWORK REQUEST'}
        try:
            response = original_open(request, *args, **kwargs)
            item.update(status_code=response.status,
                        content_type=response.headers.get('Content-Type'),
                        final_url=response.url)
            return response
        except Exception as exc:
            item.update(status_code=getattr(exc, 'code', None), error=type(exc).__name__)
            raise
        finally:
            network.append(item)
            save(out / 'public-network.json', network)

    urllib.request.urlopen = observed_open
    files = [BACKEND / n for n in ['main.py', 'ai.py', 'security.py', 'dev_auth.py',
             'static/app.js', 'static/pulse.js', 'pulse/routes.py', 'pulse/sources.py',
             'pulse/service.py', 'tests/messaging_fixture.py',
             'tests/api_integration_evidence.py']]
    save(out / 'fixture.json', {
        'timestamp': stamp(), 'base_url': BASE, 'app': 'Existing main.app and static UI',
        'database': 'Disposable in-memory SQLite with existing PostgreSQL tripwire',
        'authentication': 'Existing loopback development provider; real signed tokens/RBAC',
        'search': 'MOCKED: existing OfflineSession returns no PostgreSQL search matches',
        'ai_provider': 'DISABLED: no external AI calls; fallback/clarification only',
        'public_feeds': 'LIVE, allowlisted existing sources' if live_public else 'DISABLED',
        'source_hashes': {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in files}})
    print('EXISTING DEREXI APP: real HTTP/UI/auth, synthetic SQLite; no Supabase/AI/mail', flush=True)
    try:
        uvicorn.run(main.app, host='127.0.0.1', port=8041, proxy_headers=False,
                    access_log=False, log_level='warning')
    finally:
        main.app.dependency_overrides.clear()
        urllib.request.urlopen = original_open
        engine.dispose()


def verify_http(out, live_public):
    import httpx
    if not (out / 'fixture.json').is_file():
        raise ValueError('Start the dedicated evidence fixture before verification')
    if (out / 'http-results.json').exists():
        raise ValueError('Use a fresh evidence run; do not overwrite prior results')
    checks, transcripts = [], []

    def check(name, condition):
        checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL'})

    with httpx.Client(base_url=BASE, trust_env=False, timeout=70) as client:
        def request(method, path, body=None, token=None):
            headers = {'Accept': 'application/json'}
            if body is not None:
                headers['Content-Type'] = 'application/json'
            if token:
                headers['Authorization'] = 'Bearer ' + token
            response = client.request(method, path, headers=headers,
                                      **({'json': body} if body is not None else {}))
            try:
                data = response.json()
            except ValueError:
                data = {'non_json_body': response.text[:200]}
            transcripts.append({'timestamp': stamp(), 'method': method,
                'url': BASE + path, 'request_headers': sanitized(headers),
                'request_body': body, 'status_code': response.status_code,
                'response_headers': {k: v for k, v in response.headers.items()
                                     if k in {'content-type', 'cache-control', 'www-authenticate', 'x-request-id'}},
                'response_body': sanitized(data)})
            return response, data

        try:
            r, data = request('GET', '/')
            check('H01 Existing DeRexi service metadata over real HTTP', r.status_code == 200 and 'DeRexi' in data.get('service', ''))
            r, data = request('GET', '/policies')
            check('H02 Missing credentials rejected with 401/Bearer challenge', r.status_code == 401 and r.headers.get('www-authenticate') == 'Bearer')
            r, auth = request('POST', '/dev-auth/token', {'user_id': 8})
            check('H03 Existing local identity provider issues signed token', r.status_code == 200 and bool(auth.get('access_token')))
            token = auth['access_token']
            r, policies = request('GET', '/policies', token=token)
            check('H04 Authenticated GET returns two synthetic policy resources', r.status_code == 200 and len(policies) == 2 and all(p['status'] == 'approved' for p in policies))
            check('H05 GET response identifies JSON', r.headers.get('content-type', '').startswith('application/json'))
            r, detail = request('GET', '/policies/48', token=token)
            check('H06 Policy detail exposes version/body for existing Library display', r.status_code == 200 and detail['title'] == 'Employee Leave' and bool(detail['versions'][0]['body']))
            r, answer = request('POST', '/ask', {'question': QUESTION}, token=token)
            check('H07 POST accepts JSON question and returns helpful clarification', r.status_code == 200 and answer.get('needs_clarification') is True and 'policy owner' in answer.get('answer', ''))
            check('H08 POST returns resource identifiers and JSON', isinstance(answer.get('conversation_id'), int) and r.headers.get('content-type', '').startswith('application/json'))
            r, conversation = request('GET', '/conversations/' + str(answer['conversation_id']), token=token)
            check('H09 Follow-up GET proves POST persisted only to disposable database', r.status_code == 200 and any(m['body'] == QUESTION for m in conversation['messages']) and any(m['body'] == answer['answer'] for m in conversation['messages']))
            r, data = request('POST', '/ask', {'question': '   '}, token=token)
            check('H10 Invalid JSON fields yield safe 422 response', r.status_code == 422 and data == {'detail': 'Check the submitted fields and try again.'})
            r, data = request('POST', '/ask', {'question': QUESTION, 'user_id': 2}, token=token)
            check('H11 Client-supplied identity mismatch rejected with 403', r.status_code == 403)
            r, other = request('POST', '/dev-auth/token', {'user_id': 3})
            r, data = request('GET', '/conversations/' + str(answer['conversation_id']), token=other['access_token'])
            check('H12 Another employee cannot read the private POST result', r.status_code == 404)
            if live_public:
                r, feed = request('GET', '/api/pulse?limit=5')
                check('H13 Existing Pulse REST endpoint returns JSON envelope', r.status_code == 200 and isinstance(feed.get('articles'), list) and bool(feed.get('sources')))
                check('H14 At least one real JSON upstream works (not RSS alone)', any(feed['sources'].get(n, {}).get('ok') and feed['sources'][n]['count'] > 0 for n in ['Federal Register', 'NIST']))
                check('H15 Live normalized output retains source/title/URL/date', bool(feed['articles']) and all(all(k in a for k in ['title', 'source', 'url', 'published']) for a in feed['articles']))
        except Exception as exc:
            checks.append({'name': 'HTTP verification completed', 'status': 'FAIL', 'error': type(exc).__name__})
    result = {'timestamp': stamp(), 'mode': 'REAL LOOPBACK HTTP, actual app/routes/auth; synthetic SQLite, MOCKED PostgreSQL search, AI disabled',
              'live_public_requested': live_public, 'checks': checks, 'requests': transcripts,
              'passed': sum(c['status'] == 'PASS' for c in checks),
              'failed': sum(c['status'] == 'FAIL' for c in checks)}
    save(out / 'http-results.json', result)
    print(json.dumps({k: result[k] for k in ['passed', 'failed', 'live_public_requested']}))
    return 1 if result['failed'] else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['serve', 'http'])
    parser.add_argument('--output', required=True, help='Fresh course evidence directory')
    parser.add_argument('--live-public', action='store_true', help='Allow real read-only agency requests')
    args = parser.parse_args()
    out = output_path(args.output)
    if args.mode == 'serve':
        serve(out, args.live_public)
    else:
        raise SystemExit(verify_http(out, args.live_public))
