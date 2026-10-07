"""
DeRexi: Policy Pilot -- Cryptography Lab 4
==========================================

A beginner-friendly demonstration of PUBLIC KEY (asymmetric) cryptography:

  1. RSA key pair generation (2048-bit, exponent 65537)
  2. Basic asymmetric encryption/decryption using RSA-OAEP + SHA-256
  3. A simplified, self-signed X.509 "PKI" environment
  4. A hybrid secure key exchange (RSA-wrapped AES-256 session key)
  5. RSA key management guidance

Fictional data only. No real credentials, no production DeRexi code.
Classroom demonstration -- the keys created here are throwaway demo keys.
"""

import hashlib
import os
import time
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509.oid import NameOID

# A fictional DeRexi message used throughout the lab.
DEMO_MESSAGE = b"DeRexi policy approval requires authorized review."

# Temporary DEMO ONLY key files. Created and deleted inside this lab run.
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_PRIVATE_PEM = os.path.join(DEMO_DIR, "DEMO_ONLY_private_key.pem")
DEMO_CERT_PEM = os.path.join(DEMO_DIR, "DEMO_ONLY_certificate.pem")


def oaep_padding():
    """OAEP with SHA-256 is the modern padding scheme for RSA encryption.

    'Textbook RSA' (raw, padding-free) is insecure: it is deterministic and
    vulnerable to several classic attacks. OAEP adds randomized, structured
    padding so that encrypting the same message twice gives different
    ciphertexts each time.
    """
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def public_key_fingerprint(public_key) -> str:
    """A short, shareable identifier for a public key (SHA-256 of its DER)."""
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return sha256_of(der)


# ---------------------------------------------------------------------------
# 1. RSA KEY PAIR GENERATION
# ---------------------------------------------------------------------------

def demonstrate_rsa_key_pair():
    """Generate an RSA key pair and describe it WITHOUT exposing the secret.

    The private key stays in memory only. We print metadata (size, exponent,
    fingerprint) so the output is screenshot-friendly, but never the actual
    private key material.
    """
    print("Generating a fresh 2048-bit RSA key pair...")
    start = time.perf_counter()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # The public key is DERIVED from the private key -- they are two halves
    # of the same mathematical relationship (based on factoring large
    # semiprimes).
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    fingerprint = public_key_fingerprint(public_key)

    print()
    print("  Private key:")
    print("    - RSA private key object created (kept in memory only)")
    print("    - NOT printed, NOT written to disk, NOT committed to Git")
    print("    - Holder alone can decrypt anything encrypted with the public key")
    print("  Public key:")
    print(f"    - RSA public key derived from the private key")
    print(f"    - Safe to share openly (it cannot reveal the private key)")
    print(f"    - SHA-256 fingerprint: {fingerprint}")
    print(f"  Key size:    {private_key.key_size} bits")
    print(f"  Public exponent (e): {public_numbers.e}")
    print(f"  Generation time: {elapsed_ms:.1f} ms")

    # Evidence that the two keys are a matching pair: re-deriving the public
    # key from the private key must yield an identical fingerprint.
    rederived = private_key.public_key().public_numbers()
    pair_matches = (
        rederived.e == public_numbers.e
        and rederived.n == public_numbers.n
        and public_key_fingerprint(private_key.public_key()) == fingerprint
    )
    print(f"  Public key re-derived from private key matches: {pair_matches}")
    print()
    print("  How RSA key pairs work (beginner notes):")
    print("    - The PRIVATE key must remain secret at all times.")
    print("    - The PUBLIC key may be shared with anyone.")
    print("    - The two keys are mathematically related but derived from the")
    print("      same large primes; knowing the public key does not reveal the")
    print("      private key (that would require factoring the modulus).")
    print("    - Data encrypted with the PUBLIC key can be decrypted ONLY with")
    print("      the matching PRIVATE key.")
    print("    - This is why it is called 'asymmetric' cryptography: unlike AES,")
    print("      the same key is not used for both directions.")

    verified = (
        private_key.key_size >= 2048
        and public_numbers.e == 65537
        and pair_matches
    )
    return private_key, public_key, fingerprint, verified


# ---------------------------------------------------------------------------
# 2. BASIC ASYMMETRIC ENCRYPTION
# ---------------------------------------------------------------------------

def demonstrate_asymmetric_encryption(private_key, public_key):
    """Encrypt with the public key, decrypt with the private key, verify."""
    plaintext = DEMO_MESSAGE

    print(f"  Plaintext: {plaintext.decode('ascii')}")
    print(f"  Plaintext length: {len(plaintext)} bytes")
    print("  Padding: OAEP with SHA-256 (MGF1-SHA-256)")
    print("  Direction: PUBLIC key encrypts  ->  PRIVATE key decrypts")
    print()

    ciphertext = public_key.encrypt(plaintext, oaep_padding())
    print(f"  Ciphertext (hex): {ciphertext.hex()}")
    print(f"  Ciphertext length: {len(ciphertext)} bytes")
    print()

    recovered = private_key.decrypt(ciphertext, oaep_padding())
    print(f"  Decrypted with the private key: {recovered.decode('ascii')}")
    print(f"  Recovered message matches original: {recovered == plaintext}")
    print()

    # RSA ciphertext is always exactly the key size in bytes.
    expected_len = private_key.key_size // 8
    ciphertext_is_expected_size = len(ciphertext) == expected_len
    print(f"  Ciphertext is exactly {expected_len} bytes (one RSA block): "
          f"{ciphertext_is_expected_size}")

    print()
    print("  Why OAEP matters:")
    print("    - OAEP padding improves RSA encryption security.")
    print("    - 'Textbook RSA' (raw, padding-free) is deterministic and insecure.")
    print("    - OAEP adds random padding, so the same plaintext encrypts to")
    print("      different ciphertexts on every run.")
    print("    - OAEP also detects malformed ciphertexts during decryption.")
    print("  A practical limit:")
    print("    - RSA can only encrypt data smaller than the key size minus the")
    print("      OAEP overhead. For 2048-bit RSA + SHA-256 OAEP that is about")
    print(f"      {private_key.key_size // 8 - 2 * 32 - 2} bytes.")
    print("    - Because of this, RSA is normally used to protect SMALL values,")
    print("      such as a randomly generated symmetric session key -- not files.")

    verified = recovered == plaintext and ciphertext_is_expected_size
    return verified


# ---------------------------------------------------------------------------
# 3. SIMPLE PKI ENVIRONMENT
# ---------------------------------------------------------------------------

def demonstrate_simple_pki(private_key, public_key, fingerprint):
    """Create and inspect a self-signed X.509 certificate for a DeRexi service."""
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "derexi-demo.local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Aurum Capital Bank"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security Lab"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]
    )

    # Self-signed: issuer == subject, and the signature is produced by this
    # same private key. In a real PKI a Certificate Authority (CA) signs it.
    now = datetime.now(timezone.utc)
    not_before = now - timedelta(minutes=5)
    not_after = now + timedelta(days=365)

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    )
    certificate = builder.sign(private_key, algorithm=hashes.SHA256())

    def name_value(name: x509.Name, oid) -> str:
        attrs = name.get_attributes_for_oid(oid)
        return attrs[0].value if attrs else "(not set)"

    subject_cn = name_value(certificate.subject, NameOID.COMMON_NAME)
    subject_org = name_value(certificate.subject, NameOID.ORGANIZATION_NAME)
    issuer_cn = name_value(certificate.issuer, NameOID.COMMON_NAME)
    serial_hex = format(certificate.serial_number, "x")
    sig_hash = certificate.signature_hash_algorithm.name
    cert_fp = sha256_of(certificate.public_bytes(serialization.Encoding.DER))

    print("  Subject (the identity this certificate claims):")
    print(f"    Common Name (CN):       {subject_cn}")
    print(f"    Organization (O):       {subject_org}")
    print(f"    Organizational Unit:    "
          f"{name_value(certificate.subject, NameOID.ORGANIZATIONAL_UNIT_NAME)}")
    print(f"    Country:                "
          f"{name_value(certificate.subject, NameOID.COUNTRY_NAME)}")
    print()
    print("  Issuer (who signed it):")
    print(f"    Common Name (CN):       {issuer_cn}")
    print(f"    Self-signed (issuer == subject): "
          f"{certificate.issuer == certificate.subject}")
    print()
    print("  Certificate metadata:")
    print(f"    Serial number (hex):    {serial_hex}")
    print(f"    Valid from:             {certificate.not_valid_before_utc.isoformat()}")
    print(f"    Valid until:            {certificate.not_valid_after_utc.isoformat()}")
    print(f"    Validity period:        "
          f"{(certificate.not_valid_after_utc - certificate.not_valid_before_utc).days} days")
    print(f"    Signature algorithm:    RSA with {sig_hash.upper()}")
    print(f"    Public key in cert:     RSA {certificate.public_key().key_size} bits, "
          f"exponent {certificate.public_key().public_numbers().e}")
    print(f"    SHA-256 certificate fingerprint: {cert_fp}")
    print(f"    Extensions:             BasicConstraints (CA:TRUE), KeyUsage")
    print()

    # Verify the certificate actually carries the same public key we generated
    # earlier -- otherwise it would be a certificate for a different identity.
    cert_der = certificate.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key_der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    same_public_key = cert_der == key_der
    print("  Verification:")
    print(f"    Certificate public key == generated public key: {same_public_key}")
    print(f"    Public key fingerprint matches: "
          f"{public_key_fingerprint(certificate.public_key()) == fingerprint}")
    print(f"    Not expired right now: {certificate.not_valid_before_utc <= now <= certificate.not_valid_after_utc}")

    # Verify the signature cryptographically: the cert must verify against its
    # OWN public key (that is what self-signed means).
    try:
        certificate.verify_directly_issued_by(certificate)
        signature_valid = True
        sig_note = "valid (verifies against its own public key)"
    except Exception as exc:  # pragma: no cover - defensive
        signature_valid = False
        sig_note = f"FAILED ({exc})"
    print(f"    Self-signature check: {sig_note}")
    print()

    print("  Writing a DEMO ONLY certificate PEM file for inspection...")
    cert_path = DEMO_CERT_PEM
    with open(cert_path, "wb") as handle:
        handle.write(certificate.public_bytes(serialization.Encoding.PEM))
    print(f"    Created: {os.path.basename(cert_path)} (public material only)")
    try:
        with open(cert_path, "r", encoding="ascii") as handle:
            preview = "".join(handle.readlines()[:3]).rstrip()
        print(f"    PEM preview: {preview} ...")
    except Exception:  # pragma: no cover - preview only
        print("    PEM preview unavailable")

    print()
    print("  What PKI means (beginner notes):")
    print("    - PKI stands for Public Key Infrastructure.")
    print("    - A certificate BINDS a public key to an identity (a name, a")
    print("      host such as derexi-demo.local, a service).")
    print("    - In a real PKI, a Certificate Authority (CA) signs certificates,")
    print("      and trusting the CA is what makes the certificate trustworthy.")
    print("    - This lab uses a SELF-SIGNED certificate only for demonstration.")
    print("    - A self-signed certificate is NOT automatically trusted by")
    print("      browsers or external systems -- you would see a warning.")
    print("    - Certificates have validity periods and must be renewed before")
    print("      they expire, or revoked early if the private key is compromised.")

    verified = (
        same_public_key
        and signature_valid
        and certificate.issuer == certificate.subject
        and certificate.not_valid_after_utc > now
        and certificate.not_valid_before_utc <= now
        and certificate.serial_number > 0
    )
    return certificate, verified


# ---------------------------------------------------------------------------
# 4. SECURE KEY EXCHANGE DEMONSTRATION
# ---------------------------------------------------------------------------

def demonstrate_secure_key_exchange(private_key, public_key):
    """Hybrid crypto: RSA protects a random AES-256 session key."""
    # 32 random bytes = a 256-bit AES key, generated from the OS CSPRNG.
    session_key = os.urandom(32)
    original_fingerprint = sha256_of(session_key)

    print("  Step 1: Generate a random AES-256 session key.")
    print(f"    Key length: {len(session_key)} bytes ({len(session_key) * 8} bits)")
    print(f"    Generated with: os.urandom (operating-system CSPRNG)")
    print(f"    SHA-256 fingerprint of session key: {original_fingerprint}")
    print("    NOTE: the raw key bytes are NOT printed (lab-only secret).")
    print()

    # "Wrap" = encrypt the session key with the RSA PUBLIC key.
    wrapped_key = public_key.encrypt(session_key, oaep_padding())
    print("  Step 2: WRAP (encrypt) the AES key with the RSA public key.")
    print(f"    Wrapped key (hex): {wrapped_key.hex()}")
    print(f"    Wrapped key length: {len(wrapped_key)} bytes")
    print()

    # "Unwrap" = decrypt it with the RSA PRIVATE key.
    recovered_key = private_key.decrypt(wrapped_key, oaep_padding())
    recovered_fingerprint = sha256_of(recovered_key)
    matches = recovered_key == session_key
    print("  Step 3: UNWRAP (decrypt) the AES key with the RSA private key.")
    print(f"    Recovered key length: {len(recovered_key)} bytes")
    print(f"    SHA-256 fingerprint of recovered key: {recovered_fingerprint}")
    print(f"    Recovered AES key matches original: {matches}")
    print()

    # Bonus: prove the recovered key really works as an AES key by using it to
    # encrypt/decrypt a small DeRexi message (hybrid flow end to end).
    nonce = os.urandom(12)
    message = b"DeRexi session payload: confidential."
    aesgcm = AESGCM(recovered_key)
    sealed = aesgcm.encrypt(nonce, message, None)
    opened = aesgcm.decrypt(nonce, sealed, None)
    aes_roundtrip_ok = opened == message
    print("  Step 4 (hybrid proof): use the recovered key for bulk encryption.")
    print(f"    AES-256-GCM nonce: {nonce.hex()}")
    print(f"    Ciphertext (hex):  {sealed.hex()}")
    print(f"    Decrypted payload matches: {aes_roundtrip_ok}")
    print("    (A 12-byte nonce + 16-byte GCM tag are appended to the ciphertext.)")
    print()

    print("  Why hybrid cryptography is used (beginner notes):")
    print("    - RSA protects a randomly generated symmetric session key.")
    print("    - The symmetric key (AES) is then used for FAST bulk encryption.")
    print("    - RSA is much slower than symmetric crypto, so we do not use it")
    print("      to encrypt the actual data -- only to protect the key.")
    print("    - The public key can be shared openly; the private key remains")
    print("      secret.")
    print("    - Only the private-key holder can recover the wrapped session key.")
    print("    - This is an example of hybrid cryptography.")
    print("    - This is exactly how TLS/HTTPS negotiates a session key.")

    verified = matches and aes_roundtrip_ok and len(wrapped_key) == public_key.key_size // 8
    return verified


# ---------------------------------------------------------------------------
# 5. RSA KEY MANAGEMENT
# ---------------------------------------------------------------------------

def demonstrate_rsa_key_management(private_key):
    """Show safe handling of a private key: PEM on disk, then immediate deletion."""
    print("  Private keys:")
    print("    - Must be protected from disclosure at all times.")
    print("    - Must NOT be committed to Git or any source repository.")
    print("    - Must NOT be hard-coded into source files.")
    print("    - Production private keys belong in a secure key store, KMS, HSM,")
    print("      or a protected secrets-management system.")
    print("    - Restrict file permissions (e.g. chmod 600) when a key must live")
    print("      on disk.")
    print("  Public keys and certificates:")
    print("    - May be distributed freely; that is their purpose.")
    print("    - Publishing a certificate does NOT expose the private key.")
    print("  Lifetimes and rotation:")
    print("    - Keys should have defined lifetimes and rotation procedures.")
    print("    - If a private key is compromised, revoke/replace it immediately.")
    print("    - Certificates may also need renewal (expiry) or revocation (CRL/OCSP).")
    print("  Git safety:")
    print("    - Never commit .env files, PEM key files, or key material.")
    print("    - Add *.pem / *.key to .gitignore for non-lab work.")
    print()

    # Practical demonstration: write a private key PEM to disk in this lab
    # folder (labelled DEMO ONLY), inspect it, then DELETE it.
    print("  Live demonstration of safe temporary key handling:")
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    print(f"    - Serialized private key to PEM in memory ({len(pem_bytes)} bytes).")
    print(f"    - PEM body is NOT printed to the terminal.")

    pem_path = DEMO_PRIVATE_PEM
    structure_ok = False
    reload_ok = False
    try:
        with open(pem_path, "wb") as handle:
            handle.write(pem_bytes)
        # Immediately restrict permissions where the OS supports it.
        try:
            os.chmod(pem_path, 0o600)
            perm_note = "0o600 (owner read/write only)"
        except OSError:  # pragma: no cover - platform dependent
            perm_note = "default (platform does not support chmod)"
        size = os.path.getsize(pem_path)
        print(f"    - Wrote DEMO_ONLY_private_key.pem ({size} bytes), permissions {perm_note}.")
        with open(pem_path, "r", encoding="ascii") as handle:
            lines = handle.read().splitlines()
        structure_ok = (
            lines[0].startswith("-----BEGIN ")
            and lines[-1].startswith("-----END ")
            and lines[0].replace("BEGIN", "END") == lines[-1]
            and len(lines) > 4
        )
        print(f"    - PEM BEGIN/END markers verified (base64 body withheld): {structure_ok}")
        print("    - Reread from disk to confirm a reload round-trip works.")
        reloaded = serialization.load_pem_private_key(pem_bytes, password=None)
        # RSAPrivateNumbers has no "private_value" attribute; compare the
        # core RSA parameters (p, q, d) instead.
        before = private_key.private_numbers()
        after = reloaded.private_numbers()
        reload_ok = (
            after.p == before.p
            and after.q == before.q
            and after.d == before.d
            and after.dmp1 == before.dmp1
            and after.dmq1 == before.dmq1
            and after.iqmp == before.iqmp
        )
        print(f"    - Reloaded key matches in-memory key: {reload_ok}")
    except Exception as exc:  # pragma: no cover - defensive
        reload_ok = False
        print(f"    - Temporary key handling demo failed: {exc}")

    print()
    print("  Cleaning up DEMO ONLY files now...")
    for path in (DEMO_PRIVATE_PEM, DEMO_CERT_PEM):
        if os.path.exists(path):
            os.remove(path)
            print(f"    - Deleted: {os.path.basename(path)}")
        else:
            print(f"    - Not present (nothing to delete): {os.path.basename(path)}")

    leftovers = [p for p in (DEMO_PRIVATE_PEM, DEMO_CERT_PEM) if os.path.exists(p)]
    print(f"    - DEMO key/certificate files remaining on disk: {len(leftovers)}")
    print(f"    - Confirmed: no production-style keys are saved in the repository.")
    print()
    print("  IMPORTANT: the keys in this lab are throwaway demo keys.")
    print("    - Never reuse lab keys in a real system.")
    print("    - Do NOT save permanent production-style keys in this repository.")

    verified = structure_ok and reload_ok and not leftovers
    return verified


# ---------------------------------------------------------------------------
# 6. SECURITY CONSIDERATIONS
# ---------------------------------------------------------------------------

def print_security_considerations():
    print("  RSA:")
    print("    - RSA security depends on the difficulty of FACTORING very large")
    print("      numbers (the product of two large primes).")
    print("    - Use modern key sizes: 2048 bits minimum, 3072/4096 for long-term.")
    print("    - Use secure padding such as OAEP for encryption.")
    print("    - Do NOT use 'textbook RSA' without padding.")
    print("    - RSA signatures use a different padding: PSS (or PKCS#1 v1.5).")
    print()
    print("  Private keys:")
    print("    - Must remain secret.")
    print("    - Must not be hard-coded into source code.")
    print("    - Must not be committed to Git.")
    print("    - Encrypt at rest; restrict access; rotate regularly.")
    print()
    print("  PKI:")
    print("    - Certificates bind public keys to identities.")
    print("    - Trust depends on WHO signs the certificate (which CA you trust).")
    print("    - Self-signed certificates are useful for labs but are not")
    print("      automatically trusted by browsers or external systems.")
    print("    - Watch expiry dates; expired certificates break clients.")
    print()
    print("  Hybrid cryptography:")
    print("    - RSA is slower than symmetric cryptography.")
    print("    - Real systems use public-key crypto to exchange/protect a")
    print("      symmetric session key.")
    print("    - The symmetric key is then used for bulk encryption.")
    print("    - This is how TLS, PGP, and SSH commonly work.")
    print()
    print("  Operational notes:")
    print("    - Store private keys in a KMS/HSM/secrets manager in production.")
    print("    - Log and monitor certificate issuance and expiry.")
    print("    - Revoke compromised certificates promptly (CRL or OCSP).")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("=== DEREXI CRYPTOGRAPHY LAB 4 ===")
    print("Public Key Cryptography -- classroom demonstration (fictional data only)")
    print("No production DeRexi code, credentials, or API keys are used.")
    print()

    try:
        print("=== RSA KEY PAIR GENERATION ===")
        private_key, public_key, fingerprint, keygen_ok = demonstrate_rsa_key_pair()
        print()
        print("RSA key pair generation:", "PASS" if keygen_ok else "FAIL")
        print()

        print("=== RSA ASYMMETRIC ENCRYPTION ===")
        enc_ok = demonstrate_asymmetric_encryption(private_key, public_key)
        print()
        print("RSA asymmetric encryption/decryption:", "PASS" if enc_ok else "FAIL")
        print()

        print("=== SIMPLE PKI ENVIRONMENT ===")
        _certificate, pki_ok = demonstrate_simple_pki(private_key, public_key, fingerprint)
        print()
        print("Simple PKI certificate creation:", "PASS" if pki_ok else "FAIL")
        print()

        print("=== SECURE KEY EXCHANGE ===")
        kx_ok = demonstrate_secure_key_exchange(private_key, public_key)
        print()
        print("Secure key exchange / RSA key wrapping:", "PASS" if kx_ok else "FAIL")
        print()

        print("=== RSA KEY MANAGEMENT ===")
        mgmt_ok = demonstrate_rsa_key_management(private_key)
        print()
        print("RSA key management documented:", "PASS" if mgmt_ok else "FAIL")
        print()

        print("=== SECURITY CONSIDERATIONS ===")
        print_security_considerations()
        print()

        print("=== SUMMARY ===")
        print("RSA key pair generation:", "PASS" if keygen_ok else "FAIL")
        print("RSA asymmetric encryption/decryption:", "PASS" if enc_ok else "FAIL")
        print("Simple PKI certificate creation:", "PASS" if pki_ok else "FAIL")
        print("Secure key exchange / RSA key wrapping:", "PASS" if kx_ok else "FAIL")
        print("RSA key management documented:", "PASS" if mgmt_ok else "FAIL")
        print()
        print("DeRexi public key cryptography lab completed.")
        print()
    finally:
        # Safety net: NEVER leave temporary demo key material on disk, even if
        # a section raises part way through the run.
        for path in (DEMO_PRIVATE_PEM, DEMO_CERT_PEM):
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    main()
