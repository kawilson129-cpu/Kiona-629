"""
DeRexi: Policy Pilot -- Cryptography Lab 6
===========================================
Standalone HTTPS / TLS demo server (CLASSROOM USE ONLY).

Run it directly to start an HTTPS endpoint on localhost:

    python tls_demo_server.py

It will:
  * create a throwaway self-signed certificate if one does not exist
    (DEMO_ONLY_tls_cert.pem / DEMO_ONLY_tls_key.pem)
  * bind to 127.0.0.1 ONLY (never exposed to the network)
  * serve HTTPS with a minimum of TLS 1.2
  * print the certificate details and how to connect

Then generate traffic in a second terminal with:

    python tls_demo_client.py

...which is what you capture in Wireshark.

This file is deliberately isolated from production DeRexi. It contains no
real credentials, no API keys and no Supabase configuration.
"""

import datetime
import json
import os
import ssl
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

HERE = os.path.dirname(os.path.abspath(__file__))

CERT_FILE = os.path.join(HERE, "DEMO_ONLY_tls_cert.pem")
KEY_FILE = os.path.join(HERE, "DEMO_ONLY_tls_key.pem")

HOST = "127.0.0.1"   # localhost only -- never 0.0.0.0
PORT = 8443          # standard HTTPS test port
SERVER_NAME = "derexi-tls-demo.local"

# Fictional DeRexi payload returned to every HTTPS request.
MESSAGE = "DeRexi secure policy channel test"


# ---------------------------------------------------------------------------
# Self-signed throwaway certificate
# ---------------------------------------------------------------------------

def generate_self_signed_cert(cert_path=CERT_FILE, key_path=KEY_FILE,
                              force=False):
    """Create (or reuse) a 2048-bit RSA self-signed certificate.

    Returns the x509 certificate object. The key is a throwaway demo key and
    is never printed, never committed, and safe to regenerate at any time.
    """
    if not force and os.path.exists(cert_path) and os.path.exists(key_path):
        with open(cert_path, "rb") as handle:
            return x509.load_pem_x509_certificate(handle.read())

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )
    # Use timezone-aware datetimes (required by modern cryptography releases).
    now = datetime.datetime.now(datetime.timezone.utc)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, SERVER_NAME),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Aurum Capital Bank"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME,
                               "DeRexi Policy Pilot - TLS Lab"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]
    )
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)              # self-signed: issuer == subject
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False,
        )
        .sign(private_key, algorithm=hashes.SHA256())
    )

    with open(cert_path, "wb") as handle:
        handle.write(certificate.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as handle:
        handle.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    try:                       # restrict key permissions where the OS allows
        os.chmod(key_path, 0o600)
        os.chmod(cert_path, 0o644)
    except OSError:            # pragma: no cover - platform dependent
        pass
    return certificate


# ---------------------------------------------------------------------------
# HTTPS request handler
# ---------------------------------------------------------------------------

class DeRexiDemoHandler(BaseHTTPRequestHandler):
    """Tiny handler that answers over HTTPS with fictional DeRexi content."""

    server_version = "DeRexiTLSDemo/1.0 (classroom only)"

    def _respond(self, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-DeRexi-Demo", "classroom-only")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                    # noqa: N802 (stdlib naming)
        self._respond(
            {
                "service": "DeRexi Policy Pilot",
                "environment": "classroom demonstration only",
                "message": MESSAGE,
                "note": "Fictional data. No real credentials are used.",
            }
        )

    def do_POST(self):                   # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        received = self.rfile.read(length) if length else b""
        try:
            parsed = json.loads(received.decode("utf-8")) if received else {}
        except ValueError:
            parsed = {"raw": received.decode("utf-8", "replace")}
        self._respond(
            {
                "service": "DeRexi Policy Pilot",
                "environment": "classroom demonstration only",
                "echo": parsed,
                "message": MESSAGE,
            }
        )

    def log_message(self, fmt, *args):    # keep terminal output screenshot-clean
        sys.stdout.write("    [server] %s\n" % (fmt % args))
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Server construction
# ---------------------------------------------------------------------------

def build_https_server(host=HOST, port=PORT, certificate=None):
    """Build a TLS-wrapped HTTPServer. Does not start serving yet."""
    if certificate is None:
        certificate = generate_self_signed_cert()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Obsolete versions must NOT be used: require TLS 1.2 or newer.
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    httpd = HTTPServer((host, port), DeRexiDemoHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    return httpd


def certificate_summary(certificate):
    """Return printable certificate metadata (no key material)."""
    def name_value(name, oid):
        attrs = name.get_attributes_for_oid(oid)
        return attrs[0].value if attrs else "(not set)"

    return {
        "subject_common_name": name_value(certificate.subject,
                                           NameOID.COMMON_NAME),
        "subject_organization": name_value(certificate.subject,
                                            NameOID.ORGANIZATION_NAME),
        "subject_ou": name_value(certificate.subject,
                                 NameOID.ORGANIZATIONAL_UNIT_NAME),
        "issuer_common_name": name_value(certificate.issuer,
                                         NameOID.COMMON_NAME),
        "serial_hex": format(certificate.serial_number, "x"),
        "not_before": certificate.not_valid_before_utc.strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "not_after": certificate.not_valid_after_utc.strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "signature_algorithm": (certificate.signature_hash_algorithm.name
                                .upper()),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    certificate = generate_self_signed_cert()
    summary = certificate_summary(certificate)

    print("=== TLS WEB SERVER (standalone) ===")
    print("  TLS enabled:            yes (HTTPS)")
    print(f"  Host:                   {HOST}  (localhost only)")
    print(f"  Port:                   {PORT}")
    print(f"  Server name:            {SERVER_NAME}")
    print(f"  Certificate subject:    CN={summary['subject_common_name']}, "
          f"O={summary['subject_organization']}")
    print(f"  Certificate issuer:     CN={summary['issuer_common_name']} "
          f"(self-signed)")
    print(f"  Certificate validity:   {summary['not_before']} -> "
          f"{summary['not_after']}")
    print(f"  Signature algorithm:    RSA with "
          f"{summary['signature_algorithm']}")
    print(f"  Minimum TLS version:    TLS 1.2")
    print(f"  Certificate file:       {os.path.basename(CERT_FILE)}")
    print(f"  Private key file:       {os.path.basename(KEY_FILE)} "
          f"(DEMO ONLY, permissions 0600)")
    print()
    print("  Connect from another terminal with:")
    print(f"    python tls_demo_client.py")
    print(f"    curl --cacert {os.path.basename(CERT_FILE)} "
          f"https://{SERVER_NAME}:{PORT}/ --resolve {SERVER_NAME}:{PORT}:127.0.0.1")
    print()
    print("  Press Ctrl-C to stop.")
    print()
    sys.stdout.flush()

    httpd = build_https_server(certificate=certificate)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:            # pragma: no cover - interactive
        print("\n  Server stopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
