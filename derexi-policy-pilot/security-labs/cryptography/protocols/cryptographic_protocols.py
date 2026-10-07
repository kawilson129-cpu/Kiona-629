"""
DeRexi: Policy Pilot -- Cryptography Lab 6
===========================================

A beginner-friendly demonstration of CONFIGURING CRYPTOGRAPHIC PROTOCOLS:

  1. TLS configuration for a web server (isolated HTTPS demo on localhost)
  2. SSH key-based authentication (throwaway Ed25519 key, no system changes)
  3. A secure communication channel (HTTPS round trip)
  4. Wireshark analysis preparation (steps + filters for a LIVE capture)
  5. Protocol security analysis (TLS vs SSH vs insecure alternatives)

CLASSROOM DEMONSTRATION ONLY.
  * Fictional DeRexi / Aurum Capital Bank data only.
  * Binds to 127.0.0.1 -- never exposed to the network.
  * Does NOT touch production DeRexi, .env, or any real SSH configuration.
  * Does NOT enable macOS Remote Login, edit ~/.ssh/authorized_keys, change
    firewall settings, install software, or modify system certificates.

Run:   python cryptographic_protocols.py
"""

import os
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tls_demo_server as tls_server  # noqa: E402  (local classroom module)

# ---------------------------------------------------------------------------
# Classroom-only file names. Everything lives in THIS folder.
# ---------------------------------------------------------------------------
CERT_FILE = tls_server.CERT_FILE
KEY_FILE = tls_server.KEY_FILE
SSH_KEY_FILE = os.path.join(HERE, "DEMO_ONLY_derexi_ssh_key")
SSH_PUB_FILE = SSH_KEY_FILE + ".pub"
SSH_AUTH_KEYS_SIM = os.path.join(HERE, "DEMO_ONLY_authorized_keys")

DEMO_FILES = [CERT_FILE, KEY_FILE, SSH_KEY_FILE, SSH_PUB_FILE,
              SSH_AUTH_KEYS_SIM]

HOST = tls_server.HOST
PORT = tls_server.PORT
SERVER_NAME = tls_server.SERVER_NAME
PAYLOAD = tls_server.MESSAGE          # "DeRexi secure policy channel test"

SSH_USER = "derexi"
SSH_KEY_COMMENT = "derexi-classroom-demo"
SSH_PORT = 22


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def rule(text=""):
    print(text)


def find_free_port(candidates=(8443, 8465, 8843, 9443)):
    """Pick the first free localhost port so the lab never fails to bind."""
    for port in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((HOST, port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free localhost port found for the TLS demo.")


def port_is_open(port, timeout=1.5):
    try:
        with socket.create_connection((HOST, port), timeout=timeout):
            return True
    except OSError:
        return False


def https_request(port, path="/secure", timeout=5):
    """One HTTPS GET that returns negotiated session details."""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile=CERT_FILE)
    context.check_hostname = False       # we dial 127.0.0.1, not the CN
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    raw = socket.create_connection((HOST, port), timeout=timeout)
    try:
        with context.wrap_socket(raw, server_hostname=SERVER_NAME) as tls:
            version = tls.version()
            cipher_name, cipher_protocol, cipher_bits = tls.cipher()
            peer_der = tls.getpeercert(binary_form=True)
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {SERVER_NAME}:{port}\r\n"
                "User-Agent: DeRexiCryptoLab6/1.0\r\n"
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
    import json
    try:
        payload = json.loads(body_blob.decode("utf-8"))
    except ValueError:
        payload = {}
    return {
        "version": version,
        "cipher_name": cipher_name,
        "cipher_protocol": cipher_protocol,
        "cipher_bits": cipher_bits,
        "peer_der": peer_der,
        "status_line": status_line,
        "payload": payload,
        "request_bytes": request,
    }


def run_command(args, timeout=30):
    """Run a local command safely and capture combined output."""
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout, cwd=HERE
        )
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        return 127, f"command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "command timed out"


# ---------------------------------------------------------------------------
# 1. TLS WEB SERVER
# ---------------------------------------------------------------------------

def demo_tls_web_server():
    """Generate a throwaway cert, start HTTPS on localhost, and call it."""
    port = find_free_port()

    certificate = tls_server.generate_self_signed_cert()
    summary = tls_server.certificate_summary(certificate)

    print("  Generating / reusing a throwaway self-signed certificate...")
    print(f"    Certificate file: {os.path.basename(CERT_FILE)}")
    print(f"    Private key file: {os.path.basename(KEY_FILE)} "
          f"(DEMO ONLY, chmod 600)")
    print(f"    Key type:         RSA {certificate.public_key().key_size} bits")
    print(f"    Hash algorithm:   {summary['signature_algorithm']}")
    print()

    httpd = tls_server.build_https_server(host=HOST, port=port,
                                          certificate=certificate)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.4)

    print("  TLS enabled:            yes (HTTPS)")
    print(f"  Host:                   {HOST}  (localhost only, not 0.0.0.0)")
    print(f"  Port:                   {port}")
    print(f"  Server name:            {SERVER_NAME}")
    print(f"  Certificate subject:    CN={summary['subject_common_name']}, "
          f"O={summary['subject_organization']}")
    print(f"                          OU={summary['subject_ou']}, C=US")
    print(f"  Certificate issuer:     CN={summary['issuer_common_name']} "
          f"(self-signed: issuer == subject)")
    print(f"  Certificate serial:     {summary['serial_hex']}")
    print(f"  Certificate validity:   {summary['not_before']}")
    print(f"                          -> {summary['not_after']}")
    print(f"  Minimum TLS version:    TLS 1.2 (SSL/TLS 1.0 and 1.1 disabled)")
    print()

    # --- Prove an HTTPS client can actually connect ---
    print("  Sending an HTTPS request to the server...")
    try:
        result = https_request(port)
        connected = True
    except Exception as exc:                       # pragma: no cover
        connected = False
        result = None
        print(f"    Connection failed: {exc}")

    if connected:
        from cryptography import x509
        from cryptography.hazmat.primitives import serialization as _ser

        peer_cert = x509.load_der_x509_certificate(result["peer_der"])
        cert_matches = (
            result["peer_der"]
            == certificate.public_bytes(_ser.Encoding.DER)
        )
        print(f"    HTTPS request:          {result['status_line']}")
        print(f"    Negotiated TLS version: {result['version']}")
        print(f"    Negotiated cipher:      {result['cipher_name']} "
              f"({result['cipher_bits']}-bit)")
        print(f"    Certificate verified:   yes "
              f"(client explicitly trusted {os.path.basename(CERT_FILE)})")
        print(f"    Served certificate matches generated certificate: "
              f"{cert_matches}")
        print(f"    Served certificate subject: "
              f"{peer_cert.subject.rfc4514_string()}")
        print()
        print("    Successful HTTPS request: YES")
    print()

    print("  What TLS gives us:")
    print("    - CONFIDENTIALITY: the request and response are encrypted in")
    print("      transit, so eavesdroppers cannot read the content.")
    print("    - INTEGRITY: any modification in transit breaks the MAC and the")
    print("      connection fails instead of delivering tampered data.")
    print("    - SERVER AUTHENTICATION: the certificate lets the client check")
    print("      it is talking to the identity it expects.")
    print("    - CERTIFICATES PROVIDE SERVER IDENTITY: the certificate binds a")
    print("      public key to a name (here CN=derexi-tls-demo.local).")
    print("    - SELF-SIGNED CERTIFICATES REQUIRE EXPLICIT TRUST: this lab's")
    print("      client had to be told to trust the demo certificate. Ordinary")
    print("      browsers would show a warning.")
    print("    - PRODUCTION SYSTEMS SHOULD USE CA-ISSUED CERTIFICATES so that")
    print("      clients already trust the issuer (e.g. a public CA).")
    print("    - OBSOLETE SSL/TLS VERSIONS SHOULD NOT BE USED: SSLv2/v3 and")
    print("      TLS 1.0/1.1 are deprecated and must be disabled. This server")
    print("      enforces a minimum of TLS 1.2.")
    print("    - On this machine TLS 1.3 is unavailable (the system Python")
    print("      links LibreSSL 2.8.3), so the negotiated version is TLS 1.2.")
    print("      On a modern OpenSSL build you would expect TLS 1.3 here.")

    return connected, httpd, thread, port, summary


# ---------------------------------------------------------------------------
# 2. SSH KEY-BASED AUTHENTICATION
# ---------------------------------------------------------------------------

def demo_ssh_key_auth():
    """Generate a throwaway key pair and document the flow (no system edits)."""
    # --- a. Does ssh-keygen exist? Try Ed25519, fall back to RSA 3072 ---
    key_type = None
    for key_spec in (["-t", "ed25519"], ["-t", "rsa", "-b", "3072"]):
        for stale in (SSH_KEY_FILE, SSH_PUB_FILE):
            if os.path.exists(stale):
                os.remove(stale)
        rc, out = run_command(
            ["ssh-keygen"] + key_spec
            + ["-f", SSH_KEY_FILE, "-N", "", "-C", SSH_KEY_COMMENT, "-q"]
        )
        if rc == 0 and os.path.exists(SSH_PUB_FILE):
            key_type = "Ed25519" if "-t" in key_spec and \
                key_spec[key_spec.index("-t") + 1] == "ed25519" else "RSA"
            break

    if key_type is None:
        print("  ssh-keygen unavailable or failed; demonstrating with the")
        print("  Python 'cryptography' library instead.")
        return demo_ssh_key_auth_fallback()

    print(f"  Key generation tool:  ssh-keygen ({key_type})")
    print(f"  Key pair name:        {os.path.basename(SSH_KEY_FILE)}")
    print(f"  Passphrase:           none (acceptable ONLY for this disposable")
    print(f"                         classroom key -- production private keys")
    print(f"                         should normally be protected by a")
    print(f"                         passphrase or a hardware token)")
    print(f"  Comment:              {SSH_KEY_COMMENT}")
    print()

    # --- b. Fingerprints and public key (safe to show) ---
    rc_fp, fingerprint = run_command(["ssh-keygen", "-lf", SSH_PUB_FILE])
    rc_fp2, fingerprint_priv = run_command(["ssh-keygen", "-lf", SSH_KEY_FILE])
    print("  Public key fingerprint:")
    print(f"    {fingerprint}")
    if fingerprint_priv and fingerprint_priv != fingerprint:
        print("  Private key fingerprint (same key, no material shown):")
        print(f"    {fingerprint_priv}")
    print()

    with open(SSH_PUB_FILE, "r", encoding="utf-8") as handle:
        public_key_line = handle.read().strip()
    print("  PUBLIC key (safe to share -- this is what you install on the server):")
    print(f"    {public_key_line}")
    print()
    print("  PRIVATE key:")
    print(f"    Stored in {os.path.basename(SSH_KEY_FILE)} -- body NOT printed.")
    print("    Remains with the CLIENT and must never leave the client.")
    print()

    # Show that the public key can be re-derived from the private key.
    rc_der, derived = run_command(["ssh-keygen", "-y", "-f", SSH_KEY_FILE])
    derived_matches = rc_der == 0 and derived.strip().split()[0:2] == \
        public_key_line.split()[0:2]
    print(f"  Public key re-derived from private key matches: "
          f"{derived_matches}")
    print()

    # --- c. Where the public key would be installed (NOT done for real) ---
    auth_keys_path = os.path.expanduser("~/.ssh/authorized_keys")
    ssh_dir_exists = os.path.isdir(os.path.expanduser("~/.ssh"))
    authorized_exists = os.path.exists(auth_keys_path)

    with open(SSH_AUTH_KEYS_SIM, "w", encoding="utf-8") as handle:
        handle.write(public_key_line + "\n")
    try:
        os.chmod(SSH_AUTH_KEYS_SIM, 0o600)
    except OSError:                                   # pragma: no cover
        pass

    print("  Expected authorized_keys placement (DEMONSTRATED, NOT APPLIED):")
    print(f"    Simulated file written here: "
          f"{os.path.basename(SSH_AUTH_KEYS_SIM)}")
    print(f"    On a real server it would be appended to:")
    print(f"      {auth_keys_path}")
    print(f"    ~/.ssh exists on this Mac:  {ssh_dir_exists}")
    print(f"    ~/.ssh/authorized_keys exists: {authorized_exists}")
    print("    >>> This lab did NOT modify ~/.ssh/authorized_keys. <<<")
    print("    (Changing real SSH configuration requires your explicit approval.)")
    print()

    print("  Expected commands (run these yourself if you enable Remote Login):")
    print("    # 1. install the public key on the server")
    print(f"    cat {os.path.basename(SSH_PUB_FILE)} >> ~/.ssh/authorized_keys")
    print("    chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys")
    print("    # 2. connect using the private key")
    print(f"    ssh -i {os.path.basename(SSH_KEY_FILE)} "
          f"-o IdentitiesOnly=yes {SSH_USER}@{HOST} -p {SSH_PORT}")
    print()

    # --- d. Is an SSH server already reachable? (read-only check) ---
    ssh_open = port_is_open(SSH_PORT, timeout=1.5)
    print("  Localhost SSH server check (read-only, nothing was changed):")
    print(f"    {HOST}:{SSH_PORT} reachable: {ssh_open}")
    if ssh_open:
        print("    Remote Login appears to be enabled. This lab still did NOT")
        print("    install any key -- do that yourself only if you intend to.")
        method = "live-key-check-available"
    else:
        print("    Remote Login is NOT enabled on this Mac.")
        print("    >>> This lab did NOT enable Remote Login. Enabling it is a")
        print("        system-level change and requires your approval. <<<")
        print("    Evidence below is therefore a safe local demonstration of")
        print("    the key material, fingerprints and exact commands.")
        method = "safe-simulated"
    print()

    print("  How public-key authentication works:")
    print("    1. The PRIVATE key remains with the client and is never sent.")
    print("    2. The PUBLIC key is installed on the server (authorized_keys).")
    print("    3. The server sends a random challenge encrypted with the public")
    print("       key; only a client holding the private key can decrypt it and")
    print("       answer correctly -- so the server PROVES the client possesses")
    print("       the private key.")
    print("    4. No password ever crosses the network, so key-based")
    print("       authentication avoids transmitting reusable passwords.")
    print("    5. Private keys must be protected (passphrase, tight file")
    print("       permissions, hardware tokens) and NEVER committed to Git.")
    print()

    # Safety check: the private key file must exist but never be world/group
    # readable, and only its filename/fingerprint were printed above.
    private_perms_ok = False
    if os.path.exists(SSH_KEY_FILE):
        mode = os.stat(SSH_KEY_FILE).st_mode & 0o777
        private_perms_ok = (mode & 0o077) == 0
        print(f"  Private key file permissions: {oct(mode)} "
              f"({'not group/world readable' if private_perms_ok else 'WARNING: too open'})")
        print("  Private key body was NOT printed to the terminal.")
        print()

    ok = (
        os.path.exists(SSH_KEY_FILE)
        and os.path.exists(SSH_PUB_FILE)
        and rc_fp == 0
        and fingerprint.strip() != ""
        and derived_matches
        and private_perms_ok
    )
    return ok, method, fingerprint, key_type


def demo_ssh_key_auth_fallback():
    """Fallback path if ssh-keygen is unavailable."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    private_key = ed25519.Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(SSH_KEY_FILE, "wb") as handle:
        handle.write(private_bytes)
    public_line = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode("ascii") + " " + SSH_KEY_COMMENT
    with open(SSH_PUB_FILE, "w", encoding="utf-8") as handle:
        handle.write(public_line + "\n")

    print("  Generated an Ed25519 key pair with the 'cryptography' library.")
    print(f"  PUBLIC key: {public_line}")
    print(f"  PRIVATE key stored in {os.path.basename(SSH_KEY_FILE)} "
          f"(body NOT printed)")
    print("  >>> This lab did NOT modify ~/.ssh/authorized_keys. <<<")
    ok = os.path.exists(SSH_KEY_FILE) and os.path.exists(SSH_PUB_FILE)
    return ok, "safe-simulated", "(library-generated Ed25519)", "Ed25519"


# ---------------------------------------------------------------------------
# 3. SECURE COMMUNICATION CHANNEL
# ---------------------------------------------------------------------------

def demo_secure_channel(port):
    """Send the fictional DeRexi payload over HTTPS and verify the round trip."""
    print(f"  Channel: HTTPS (HTTP carried inside TLS) on {HOST}:{port}")
    print(f"  Payload to transmit: {PAYLOAD!r}")
    print()

    result = https_request(port, path="/secure")
    received = result["payload"].get("message")
    integrity_ok = received == PAYLOAD

    print("  Application-layer request bytes (BEFORE TLS encrypts them):")
    for line in result["request_bytes"].decode("ascii").split("\r\n"):
        if line:
            print(f"    {line}")
    print()
    print("  Server response:")
    print(f"    {result['status_line']}")
    for key, value in result["payload"].items():
        print(f"    {key}: {value}")
    print()
    print(f"  Negotiated TLS version: {result['version']}")
    print(f"  Negotiated cipher:      {result['cipher_name']} "
          f"({result['cipher_bits']}-bit)")
    print(f"  Round-trip integrity:   "
          f"{'PASS' if integrity_ok else 'FAIL'} "
          f"(received {'==' if integrity_ok else '!='} sent)")
    print()

    print("  Why HTTPS matters:")
    print("    - HTTPS = HTTP carried INSIDE TLS. The HTTP request/response is")
    print("      the payload; TLS provides encryption, integrity and server")
    print("      authentication around it.")
    print("    - Plaintext HTTP would expose the content in transit: anyone")
    print("      able to read the packets would see the exact request lines")
    print("      and response body printed above.")
    print("    - On an encrypted connection those same bytes appear only as")
    print("      TLS Application Data records -- unreadable without the keys.")
    print("    - Integrity is confirmed by the round-trip check: the client")
    print("      received the original message unaltered.")

    return integrity_ok, result


# ---------------------------------------------------------------------------
# 4. WIRESHARK ANALYSIS PREPARATION
# ---------------------------------------------------------------------------

def wireshark_analysis_preparation(port):
    """Print live-capture instructions. NO capture is fabricated here."""
    print("  This section prepares you for a LIVE Wireshark capture.")
    print("  >>> No capture has been made or fabricated by this lab. <<<")
    print("    You will perform the capture yourself and screenshot it.")
    print()
    print("  STEP 1 -- Start the traffic source (terminal 1):")
    print(f"      cd {os.path.relpath(HERE, os.getcwd())}")
    print("      python tls_demo_server.py")
    print()
    print("  STEP 2 -- Open Wireshark (macOS):")
    print("      open -a Wireshark        # or launch it from Applications")
    print()
    print("  STEP 3 -- Select the loopback interface:")
    print("      On macOS this appears as 'lo0' (sometimes 'Loopback').")
    print("      Do NOT use Wi-Fi/ethernet -- this lab only talks to 127.0.0.1.")
    print("      Tip: capture on lo0 BEFORE starting the client, so you do not")
    print("      miss the handshake.")
    print()
    print("  STEP 4 -- Start the capture (the shark-fin / Start button).")
    print()
    print("  STEP 5 -- Generate the HTTPS traffic (terminal 2):")
    print("      python tls_demo_client.py")
    print("      (repeat it a few times if you want a longer capture)")
    print()
    print("  STEP 6 -- Stop the capture.")
    print()
    print("  STEP 7 -- Apply display filters:")
    print("      tls                       # all TLS traffic")
    print(f"      tcp.port == {port}             # only the TLS demo port")
    print("      tls.handshake             # negotiation packets only")
    print("      tls.record                # individual TLS records")
    print("      ip.addr == 127.0.0.1      # restrict to loopback")
    print()
    print("  STEP 8 -- Expand the handshake packets and screenshot:")
    print("      - Client Hello   (offered TLS versions, cipher suites, SNI)")
    print("      - Server Hello   (chosen TLS version + chosen cipher suite)")
    print("      - Certificate    (the demo certificate's subject/issuer)")
    print("      - Negotiated TLS version and cipher suite")
    print("      - Application Data records (encrypted)")
    print("      - The ABSENCE of readable application plaintext")
    print()
    print("  What you should expect to SEE vs NOT see:")
    print("    Visible without extra configuration:")
    print("      - handshake metadata, certificate fields, TLS version,")
    print("        cipher suite, packet sizes and timing")
    print("    NOT visible (because TLS decryption is not configured):")
    print("      - the HTTP request line 'GET /secure HTTP/1.1'")
    print("      - the JSON response body and the DeRexi message")
    print("      These appear only as encrypted Application Data records.")
    print("      That is exactly the confidentiality property TLS provides.")
    print()
    print("  If you WANT to decrypt later (optional, not required):")
    print("      export SSLKEYLOGFILE=$PWD/DEMO_ONLY_sslkeys.log")
    print("      python tls_demo_client.py     # with SSLKEYLOGFILE set")
    print("      Wireshark -> Preferences -> Protocols -> TLS ->")
    print("      (Pre)-Master-Secret log filename -> point at that file")
    print("      >> Delete DEMO_ONLY_sslkeys.log afterwards; keys are secret. <<")
    print()
    print("  Suggested screenshot checklist:")
    print("      [ ] lo0 selected and capture running")
    print("      [ ] Client Hello expanded (TLS version + ciphers)")
    print("      [ ] Server Hello expanded (chosen version + cipher)")
    print("      [ ] Certificate details (subject / issuer)")
    print("      [ ] Application Data records showing no readable plaintext")
    print("      [ ] Display filter bar showing one of the filters above")

    return True


# ---------------------------------------------------------------------------
# 5. PROTOCOL SECURITY ANALYSIS
# ---------------------------------------------------------------------------

def protocol_security_analysis(port):
    print("  TLS:")
    print("    - Confidentiality: encrypts application data in transit.")
    print("    - Integrity: tampering in transit is detected and the record is")
    print("      rejected.")
    print("    - Server authentication: the certificate proves the server's")
    print("      identity to the client.")
    print("    - Certificate trust: clients must trust the issuer; a self-signed")
    print("      certificate needs explicit trust and is not automatically")
    print("      accepted.")
    print("    - Use modern versions: TLS 1.2 minimum, TLS 1.3 preferred.")
    print("      Disable SSLv2/v3, TLS 1.0 and TLS 1.1.")
    print("    - Use secure cipher suites: prefer AEAD ciphers with forward")
    print("      secrecy (TLS 1.3 mandates this; avoid CBC and RC4/3DES).")
    print("    - Downgrade / legacy concerns: attackers may try to force an")
    print("      older protocol version; enforcing a minimum version and")
    print("      disabling legacy renegotiation prevents this.")
    print()
    print("  SSH:")
    print("    - Encrypts the interactive session, file transfers and tunnel")
    print("      traffic between client and server.")
    print("    - Provides integrity protection for everything on the channel.")
    print("    - Server identity comes from HOST KEYS: the client compares the")
    print("      host key fingerprint before trusting a new server.")
    print("    - Client authentication uses public keys (as demonstrated above).")
    print("    - Risk of private-key theft: a stolen, unencrypted private key is")
    print("      game over, so protect it with a passphrase or hardware token.")
    print("    - Always verify host fingerprints out-of-band on first contact")
    print("      (and investigate changed fingerprints -- possible MITM).")
    print("    - Advantage over plaintext remote protocols: credentials, output")
    print("      and data are never sent in the clear.")
    print()
    print("  Comparison with insecure alternatives:")
    print("    - HTTP     : sends request, response, cookies and often passwords")
    print("                 as readable plaintext.")
    print("    - Telnet   : transmits login credentials and every keystroke in")
    print("                 the clear; no encryption or integrity protection.")
    print("    - FTP      : sends usernames/passwords and file contents in the")
    print("                 clear (use SFTP/FTPS instead).")
    print()
    print("  All three can expose credentials or data if used without a")
    print("  protective encrypted layer. HTTPS = HTTP + TLS, SSH replaces")
    print("  Telnet/rsh, and SFTP/SCP replace plain FTP.")
    print()
    print("  DeRexi classroom context:")
    print("    - This lab's demo server binds to 127.0.0.1:%d only." % port)
    print("    - Production DeRexi would be served over HTTPS with a")
    print("      CA-issued certificate, TLS 1.2+/1.3, and HSTS.")
    print("    - Nothing in this lab changes production configuration.")

    return True


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def cleanup():
    """Remove every DEMO_ONLY artefact created by this lab."""
    print("  Cleaning up DEMO ONLY files...")
    removed = 0
    for path in DEMO_FILES:
        if os.path.exists(path):
            os.remove(path)
            removed += 1
            print(f"    - Deleted: {os.path.basename(path)}")
        else:
            print(f"    - Not present: {os.path.basename(path)}")
    leftovers = [p for p in DEMO_FILES if os.path.exists(p)]
    print(f"    - DEMO files remaining in this folder: {len(leftovers)}")
    print("    - Nothing was written outside this folder.")
    print("    - ~/.ssh was NOT modified, Remote Login was NOT enabled, and")
    print("      the production .env was NOT touched.")
    return not leftovers, removed


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> int:
    httpd = None
    exit_code = 0

    print()
    print("=== DEREXI CRYPTOGRAPHY LAB 6 ===")
    print("Configuring Cryptographic Protocols -- classroom demonstration")
    print("Fictional DeRexi data only. Localhost only. No production changes.")
    print()

    try:
        # ---------------- 1. TLS ----------------
        print("=== TLS WEB SERVER ===")
        tls_ok, httpd, thread, port, summary = demo_tls_web_server()
        print()
        print("TLS web server configuration:", "PASS" if tls_ok else "FAIL")
        print()

        # ---------------- 2. SSH ----------------
        print("=== SSH KEY AUTHENTICATION ===")
        ssh_ok, ssh_method, fingerprint, key_type = demo_ssh_key_auth()
        print()
        print("SSH key-based authentication demonstration:",
              "PASS" if ssh_ok else "FAIL")
        print()

        # ------------- 3. SECURE CHANNEL -------------
        print("=== SECURE COMMUNICATION CHANNEL ===")
        channel_ok, channel_result = demo_secure_channel(port)
        print()
        print("Secure communication channel:", "PASS" if channel_ok else "FAIL")
        print()

        # ------------- 4. WIRESHARK -------------
        print("=== WIRESHARK ANALYSIS ===")
        wireshark_ok = wireshark_analysis_preparation(port)
        print()
        print("Wireshark analysis preparation:",
              "PASS" if wireshark_ok else "FAIL")
        print()

        # ------------- 5. ANALYSIS -------------
        print("=== PROTOCOL SECURITY ANALYSIS ===")
        analysis_ok = protocol_security_analysis(port)
        print()
        print("Protocol security analysis documented:",
              "PASS" if analysis_ok else "FAIL")
        print()

        # ---------------- SUMMARY ----------------
        print("=== SUMMARY ===")
        print("TLS web server configuration:", "PASS" if tls_ok else "FAIL")
        print("SSH key-based authentication demonstration:",
              "PASS" if ssh_ok else "FAIL")
        print("Secure communication channel:", "PASS" if channel_ok else "FAIL")
        print("Wireshark analysis preparation:",
              "PASS" if wireshark_ok else "FAIL")
        print("Protocol security analysis documented:",
              "PASS" if analysis_ok else "FAIL")
        print()
        print("DeRexi cryptographic protocols lab completed.")
        print()

        if not all([tls_ok, ssh_ok, channel_ok, wireshark_ok, analysis_ok]):
            exit_code = 1

    finally:
        # Stop the HTTPS server before removing its certificate/key files.
        if httpd is not None:
            try:
                httpd.shutdown()
                httpd.server_close()
            except Exception:                          # pragma: no cover
                pass
        print("=== CLEANUP ===")
        cleanup()
        print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
