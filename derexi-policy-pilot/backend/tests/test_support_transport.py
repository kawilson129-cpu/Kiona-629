"""TLS/SMTP failure semantics with stdlib mocks, no sockets or provider access."""
import json
import os
from pathlib import Path
import smtplib
import ssl
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parent))
import messaging_fixture
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from incident_assistance import SMTPTransport, registry, DisabledTransport, transport
from transport import protected_database_url

checks=[]
def check(name,passed):checks.append({'name':name,'pass':bool(passed)})
with patch.dict(os.environ,{'DEREXI_ENV':'production'}):
    check('Production default verifies hostname','sslmode=verify-full' in protected_database_url('postgresql://user:private@db.example.invalid/app'))
    for mode in ['require','verify-ca','disable','prefer']:
        try:protected_database_url('postgresql://user:private@db.example.invalid/app?sslmode='+mode);valid=True
        except RuntimeError:valid=False
        check('Production refuses insufficient TLS '+mode,not valid)
with patch.dict(os.environ,{'DEREXI_OUTBOUND_EMAIL':'off'}):check('OFF selects no-network adapter',isinstance(transport(),DisabledTransport))
with patch.dict(os.environ,{'DEREXI_SMTP_HOST':'smtp.example.invalid','DEREXI_SMTP_FROM':'support@example.invalid','DEREXI_SMTP_USERNAME':'service','DEREXI_SMTP_PASSWORD':'synthetic-only'}):
    smtp=MagicMock();smtp.send_message.return_value={}
    with patch('smtplib.SMTP_SSL',return_value=smtp) as connect:
        outcome=SMTPTransport().send('security@example.invalid','Fixed subject','Fictional request','<reference@derexi.invalid>')
        check('SMTP accepts only transport acknowledgement',outcome=='accepted')
        context=connect.call_args.kwargs['context']
        check('Implicit TLS validates CA and hostname',context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname and connect.call_args.kwargs['port']==465)
        check('Recipient envelope fixed to supplied approved target',smtp.send_message.call_args.kwargs['to_addrs']==['security@example.invalid'])
        check('Connection closed after send',smtp.close.called)
    with patch('smtplib.SMTP_SSL',side_effect=OSError('synthetic connection failure')):
        check('Before-send connection failure retryable',SMTPTransport().send('security@example.invalid','Subject','Body','<id>')=='retryable')
    for exception in [smtplib.SMTPServerDisconnected('private provider text'),smtplib.SMTPDataError(451,b'private provider text')]:
        smtp=MagicMock();smtp.send_message.side_effect=exception
        with patch('smtplib.SMTP_SSL',return_value=smtp):check('Ambiguous send never marked retryable '+type(exception).__name__,SMTPTransport().send('security@example.invalid','Subject','Body','<id>')=='unknown')
    smtp=MagicMock();smtp.send_message.side_effect=smtplib.SMTPRecipientsRefused({'security@example.invalid':(550,b'not accepted')})
    with patch('smtplib.SMTP_SSL',return_value=smtp):check('Explicit recipient rejection retained',SMTPTransport().send('security@example.invalid','Subject','Body','<id>')=='rejected')
    with patch.dict(os.environ,{'DEREXI_SMTP_FROM':'support@example.invalid\r\nBcc: attacker@example.invalid'}):
        with patch('smtplib.SMTP_SSL') as connect:
            check('Sender header injection fails before network',SMTPTransport().send('security@example.invalid','Subject','Body','<id>')=='configuration_error' and not connect.called)
for bad in ['[]','{"key":{"address":"security@example.invalid\\r\\nBcc:attacker@example.invalid","label":"Security","channel":"security"}}']:
    with patch.dict(os.environ,{'DEREXI_APPROVED_MAILBOXES':bad}):
        try:registry();valid=True
        except Exception:valid=False
        check('Malformed/injected registry fails closed',not valid)
report={'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks}
Path(os.environ['DEREXI_SPRINT_EVIDENCE'],'transport-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2));sys.exit(bool(report['failed']))
