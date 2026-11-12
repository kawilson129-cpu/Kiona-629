"""Fail closed for plaintext remote database transport; no connection is opened here."""
from sqlalchemy.engine import make_url
import os


def protected_database_url(value):
    url = make_url(value)
    local = url.host in {'localhost', '127.0.0.1', '::1'}
    if url.get_backend_name() == 'postgresql' and not local:
        production = os.getenv('DEREXI_ENV', 'production').lower() not in {'development', 'test'}
        mode = url.query.get('sslmode', 'verify-full' if production else 'require')
        if production and mode != 'verify-full':
            raise RuntimeError('Production PostgreSQL requires certificate and hostname verification (sslmode=verify-full)')
        if mode not in {'require', 'verify-ca', 'verify-full'}:
            raise RuntimeError('Remote PostgreSQL requires TLS; set sslmode=require or verify-full')
        url = url.update_query_dict({'sslmode': mode})
    return url.render_as_string(hide_password=False)
