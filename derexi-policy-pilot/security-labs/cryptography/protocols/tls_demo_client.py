"""
DeRexi: Policy Pilot -- Cryptography Lab 6
===========================================
Standalone HTTPS client for the TLS demo server (CLASSROOM USE ONLY).

Start the server first:

    python tls_demo_server.py

Then run this client (this is the traffic you capture in Wireshark):

    python tls_demo_client.py

The client deliberately trusts ONLY the throwaway demo certificate, which is
how a self-signed certificate must be handled: you have to explicitly tell
your client to trust it. Production systems use a CA-issued certificate that
the operating system already trusts.
"""

import json
import os
import socket
import ssl
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(HERE, "DEMO_ONLY_tls_cert.pem")

HOST = "127.0.0.1"
PORT = 8443
SERVER_NAME = "derexi-tls-demo.local"
MESSAGE = "DeRexi secure policy channel test"


def https_get(host=HOST, port=PORT, server_name=SERVER_NAME,
              path="/secure", timeout=5):
    """Perform one HTTPS GET and return details about the negotiated session."""
    if not os.path.exists(CERT_FILE):
        raise SystemExit(
            f"  {os.path.basename(CERT_FILE)} not found.\n"
            "  Start the server first:  python tls_demo_server.py"
        )

    # Explicit trust: the demo certificate is added to THIS client's trust
    # store. This is exactly why self-signed certificates are inconvenient --
    # and why production systems use certificates from a real CA.
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile=CERT_FILE)
    context.check_hostname = False        # we dial 127.0.0.1, not the CN
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    raw = socket.create_connection((host, port), timeout=timeout)
    try:
        with context.wrap_socket(raw, server_hostname=server_name) as tls:
            version = tls.version()
            cipher_name, cipher_protocol, cipher_bits = tls.cipher()
            peer_der = tls.getpeercert(binary_form=True)

            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {server_name}:{port}\r\n"
                "User-Agent: DeRexiTLSDemoClient/1.0\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("ascii")

            tls.sendall(request)

            chunks = []
            while True:
                data = tls.recv(4096)
                if not data:
                    break
                chunks.append(data)
            response = b"".join(chunks)
    finally:
        raw.close()

    header_blob, _, body_blob = response.partition(b"\r\n\r\n")
    status_line = header_blob.split(b"\r\n", 1)[0].decode("ascii", "replace")
    try:
        payload = json.loads(body_blob.decode("utf-8"))
    except ValueError:
        payload = {}

    return {
        "tls_version": version,
        "cipher_name": cipher_name,
        "cipher_protocol": cipher_protocol,
        "cipher_bits": cipher_bits,
        "peer_certificate_der": peer_der,
        "status_line": status_line,
        "response_text": body_blob.decode("utf-8", "replace"),
        "payload": payload,
        "request_bytes": request,
    }


def main():
    print("=== TLS CLIENT (standalone) ===")
    try:
        result = https_get()
    except ssl.SSLCertVerificationError as exc:
        print("  Certificate NOT trusted by this client.")
        print(f"  {exc.verify_message}")
        print("  (This is the expected behaviour for an untrusted self-signed"
              " certificate.)")
        return 1
    except (ConnectionRefusedError, socket.timeout, OSError) as exc:
        print(f"  Could not connect to {HOST}:{PORT} -> {exc}")
        print("  Start the server first:  python tls_demo_server.py")
        return 1

    print(f"  Connected to:            {HOST}:{PORT} ({SERVER_NAME})")
    print(f"  Negotiated TLS version:  {result['tls_version']}")
    print(f"  Negotiated cipher:       {result['cipher_name']} "
          f"({result['cipher_bits']}-bit)")
    print(f"  Certificate verified:    yes (explicitly trusted by client)")
    print(f"  HTTP status:             {result['status_line']}")
    print()
    print("  Response body:")
    for line in result["response_text"].splitlines():
        print(f"    {line}")
    print()

    received = result["payload"].get("message")
    if received == MESSAGE:
        print(f"  Round-trip integrity: PASS (received == sent)")
        print(f"  Message: {received}")
        return 0

    print(f"  Round-trip integrity: FAIL (got {received!r})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
