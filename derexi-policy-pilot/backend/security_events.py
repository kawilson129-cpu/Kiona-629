"""Structured, content-free security telemetry. Configure durable collection externally."""
import json
import logging
from datetime import datetime, timezone
from urllib.parse import unquote

logger = logging.getLogger('derexi.security')
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
logger.propagate = False


class AccessPathFilter(logging.Filter):
    """Keep Uvicorn access logs from exposing query text or preview tokens."""
    def __init__(self, routes):
        super().__init__()
        self.routes = routes

    def filter(self, record):
        if isinstance(record.args, tuple) and len(record.args) == 5:
            path = unquote(str(record.args[2]).split('?', 1)[0])
            template = next((route.path for route in self.routes()
                             if getattr(route, 'path_regex', None) and route.path_regex.match(path)), 'unmatched')
            record.args = (*record.args[:2], template, *record.args[3:])
        return True


def emit(event, request, status, action=None):
    actor = getattr(request.state, 'identity', None)
    route = getattr(request.scope.get('route'), 'path', None) or 'unmatched'
    # Never include request URLs, query strings, headers, bodies, exceptions,
    # email addresses, filenames, preview tokens, or provider response text.
    data = {'timestamp': datetime.now(timezone.utc).isoformat(),
            'event': event, 'request_id': getattr(request.state, 'request_id', None),
            'method': request.method, 'route': route, 'status': status,
            'actor_id': actor.user_id if actor else None,
            'role': actor.role if actor else None}
    if action in {'submit','peer_approve','peer_reject','peer_changes','final_approve',
                  'final_reject','final_changes','publish'}:
        data['action'] = action
    logger.info(json.dumps(data, separators=(',', ':')))
