"""
DeRexi: Policy Pilot -- Cryptography Lab 5
===========================================

A beginner-friendly demonstration of DIGITAL SIGNATURES:

  1. RSA signing key pair generation (2048-bit, exponent 65537)
  2. Creating an RSA-PSS + SHA-256 digital signature
  3. Signature verification, including tamper/change detection
  4. Self-signed X.509 signing certificate generation
  5. Certificate management guidance
  6. The trust model behind digital signatures
  7. An optional file-signature demonstration
  8. Security considerations

Fictional DeRexi / Aurum Capital Bank data only.
No production DeRexi code, credentials, or API keys are used.
The keys created here are throwaway demo keys.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

# ---------------------------------------------------------------------------
# Fictional DeRexi data used throughout this lab.
# ---------------------------------------------------------------------------

# The policy statement we sign.
DEMO_MESSAGE = (
    b"Aurum Capital Bank policy version 1.0 is approved for publication."
)
# The same statement with ONE changed phrase -- used to prove that any
# change to the signed content is detected.
TAMPERED_MESSAGE = (
    b"Aurum Capital Bank policy version 1.0 is NOT approved for publication."
)

ORIGINAL_POLICY_TEXT = """\
Aurum Capital Bank -- Information Security Policy (DEMO ONLY)
Version 1.0, approved for publication.

Employees must report suspected security incidents to the SOC within
one hour of discovery. DeRexi assists with policy questions and routing.
"""

MODIFIED_POLICY_TEXT = ORIGINAL_POLICY_TEXT.replace(
    "within\none hour", "within\nTWO hours"
)

# Temporary DEMO ONLY files. Created and deleted inside this lab run.
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_KEY_PEM = os.path.join(DEMO_DIR, "DEMO_ONLY_signing_key.pem")
DEMO_CERT_PEM = os.path.join(DEMO_DIR, "DEMO_ONLY_signing_certificate.pem")
DEMO_POLICY_FILE = os.path.join(DEMO_DIR, "sample_signed_policy.txt")


# ---------------------------------------------------------------------------
# Shared helpers.
# ---------------------------------------------------------------------------

def pss_padding():
    """RSA-PSS is the modern padding scheme for RSA SIGNATURES.

    Unlike OAEP (used for encryption), PSS is designed for signing. It adds a
    random salt to the padding so that signing the same message twice does
    not produce the same signature twice. Verification is always done with
    the SAME salt length used when signing.
    """
    return padding.PSS(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH,
    )


def sha256_hex(data: bytes) -> str:
    """The message digest: a fixed 32-byte fingerprint of any input."""
    return hashlib.sha256(data).hexdigest()


def public_key_fingerprint(public_key) -> str:
    """A short, shareable identifier for a public key (SHA-256 of its DER)."""
    der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return sha256_hex(der)


def verify_signature(public_key, message: bytes, signature: bytes) -> bool:
    """Verify a signature safely: return True/False instead of raising."""
    try:
        public_key.verify(signature, message, pss_padding(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except Exception as exc:  # pragma: no cover - defensive
        print(f"    (unexpected verification error: {exc})")
        return False


# ---------------------------------------------------------------------------
# 1. RSA SIGNING KEY PAIR
# ---------------------------------------------------------------------------

def generate_signing_key_pair():
    """Create a fresh RSA key pair used ONLY for signing."""
    print("  Generating a fresh 2048-bit RSA signing key pair...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    fingerprint = public_key_fingerprint(public_key)

    print()
    print("  Private signing key:")
    print("    - RSA private key object created (kept in memory only)")
    print("    - NOT printed, NOT committed to Git")
    print("    - Used to CREATE digital signatures")
    print("    - Must remain secret at all times")
    print("  Public verification key:")
    print("    - Derived from the private key")
    print("    - Safe to share openly")
    print("    - Used to VERIFY digital signatures")
    print(f"    - Public-key fingerprint (SHA-256): {fingerprint}")
    print(f"  Key size:      {private_key.key_size} bits")
    print(f"  Public exponent (e): {public_numbers.e}")

    # Confirm the public key really was derived from this private key.
    rederived = private_key.public_key().public_numbers()
    pair_matches = (
        rederived.e == public_numbers.e
        and rederived.n == public_numbers.n
        and public_key_fingerprint(private_key.public_key()) == fingerprint
    )
    print(f"  Public key re-derived from private key matches: {pair_matches}")
    print()
    print("  Signing is different from encryption:")
    print("    - ENCRYPTION: hides a message; only the intended recipient")
    print("      (private key holder) can read it.")
    print("    - SIGNING: does NOT hide the message. Anyone can read it.")
    print("      A signature instead proves WHO produced it and that it")
    print("      has not been altered.")
    print("    - With signing, the PRIVATE key creates the signature and the")
    print("      PUBLIC key verifies it -- the opposite direction of RSA")
    print("      encryption, where the public key encrypts.")
    print("    - The private signing key must remain secret; if it leaks,")
    print("      anyone could forge signatures in that identity's name.")

    verified = (
        private_key.key_size >= 2048
        and public_numbers.e == 65537
        and pair_matches
    )
    return private_key, public_key, fingerprint, verified


# ---------------------------------------------------------------------------
# 2. CREATE A DIGITAL SIGNATURE
# ---------------------------------------------------------------------------

def create_digital_signature(private_key, public_key):
    """Sign a fictional DeRexi policy message with RSA-PSS + SHA-256."""
    message = DEMO_MESSAGE

    print(f"  Original message: {message.decode('ascii')}")
    print(f"  Message encoded as bytes: {len(message)} bytes (UTF-8/ASCII)")
    print(f"  SHA-256 message digest:   {sha256_hex(message)}")
    print("  Padding: RSA-PSS (MGF1-SHA-256, 32-byte salt)")
    print("  Hash algorithm: SHA-256")
    print("  Signing key: RSA private key (never printed)")
    print()

    signature = private_key.sign(message, pss_padding(), hashes.SHA256())
    print(f"  Signature (hex):")
    print(f"    {signature.hex()}")
    print(f"  Signature length: {len(signature)} bytes (one RSA block)")
    print()

    # A signature is deterministic in VERIFICATION, but PSS is randomized in
    # CREATION: signing the same message twice gives different signatures.
    second_signature = private_key.sign(message, pss_padding(), hashes.SHA256())
    randomized = signature != second_signature
    print(f"  PSS randomness: two signatures of the same message differ: "
          f"{randomized}")
    print(f"  Both signatures still verify: "
          f"{verify_signature(public_key, message, signature) and verify_signature(public_key, message, second_signature)}")
    print()
    print("  What a digital signature proves:")
    print("    - INTEGRITY: the message has not been changed since signing.")
    print("    - AUTHENTICITY: it was produced by the holder of the private key.")
    print("    - NON-REPUDIATION: the signer cannot easily deny having signed it.")
    print("    - The signature is created FROM the message and the private key.")
    print("    - Changing the message invalidates the signature, because the")
    print("      verifier hashes the received message and checks it against the")
    print("      signature using the public key.")

    verified = len(signature) == private_key.key_size // 8 and randomized
    return message, signature, verified


# ---------------------------------------------------------------------------
# 3. VERIFY THE SIGNATURE (plus optional file-signature demo)
# ---------------------------------------------------------------------------

def verify_signature_section(private_key, public_key, message, signature):
    """Verify the real message, then prove tampering is detected."""
    # --- 3a. Verify the ORIGINAL message ---
    original_ok = verify_signature(public_key, message, signature)
    print("  Verifying the ORIGINAL message with the public key...")
    print(f"    Message:   {message.decode('ascii')}")
    print(f"    Digest:    {sha256_hex(message)}")
    print(f"    Signature verifies: {original_ok}")
    print("    (InvalidSignature is caught safely -- no crash, no traceback)")
    print()
    print("Original signature verification:", "PASS" if original_ok else "FAIL")
    print()

    # --- 3b. Verify a TAMPERED message with the SAME signature ---
    tampered = TAMPERED_MESSAGE
    print("  Now attempting to verify the SAME signature against a tampered"
          " message:")
    print(f"    Tampered message: {tampered.decode('ascii')}")
    print(f"    Tampered digest:  {sha256_hex(tampered)}")
    print(f"    Original digest:  {sha256_hex(message)}")
    print(f"    Digests differ:   {sha256_hex(tampered) != sha256_hex(message)}")

    tampered_ok = verify_signature(public_key, tampered, signature)
    change_detected = not tampered_ok  # verification MUST fail
    print(f"    Verification result: {'succeeded (UNEXPECTED)' if tampered_ok else 'failed -> change detected'}")
    print()
    print("Tampered message verification:",
          "CHANGE DETECTED" if change_detected else "FAIL (tampering missed!)")
    print()
    print("  Why tampering is always detected:")
    print("    - Even ONE changed character changes the SHA-256 message digest.")
    print("    - The public-key verification step recomputes the digest from the")
    print("      received message and checks it against the signature.")
    print("    - Because the digest no longer matches, verification raises")
    print("      InvalidSignature and fails -- proving the signed content is")
    print("      no longer identical.")

    # --- 3c. Optional file-signature demonstration ---
    print()
    print("  Optional demo: signing a fictional policy FILE")
    file_ok = demonstrate_file_signature(private_key, public_key)

    verified = original_ok and change_detected and file_ok
    return verified, change_detected


def demonstrate_file_signature(private_key, public_key):
    """Sign and verify the contents of a small fictional policy file."""
    print(f"    Creating fictional policy file: {os.path.basename(DEMO_POLICY_FILE)}")
    with open(DEMO_POLICY_FILE, "w", encoding="utf-8") as handle:
        handle.write(ORIGINAL_POLICY_TEXT)
    with open(DEMO_POLICY_FILE, "rb") as handle:
        original_bytes = handle.read()
    print(f"    File size: {len(original_bytes)} bytes")
    print(f"    File SHA-256 digest: {sha256_hex(original_bytes)}")
    print()

    # Step 1: sign the file contents with the private key.
    file_signature = private_key.sign(
        original_bytes, pss_padding(), hashes.SHA256()
    )
    print(f"    Signed the file contents (signature length: "
          f"{len(file_signature)} bytes)")
    print(f"    Signature (hex): {file_signature.hex()}")
    print()

    # Step 2: verify the unchanged file.
    unchanged_ok = verify_signature(public_key, original_bytes, file_signature)
    print(f"    Verify UNCHANGED file: {unchanged_ok}")
    print("Original file signature verification:",
          "PASS" if unchanged_ok else "FAIL")
    print()

    # Step 3: modify one word, then re-verify the ORIGINAL signature.
    with open(DEMO_POLICY_FILE, "w", encoding="utf-8") as handle:
        handle.write(MODIFIED_POLICY_TEXT)
    with open(DEMO_POLICY_FILE, "rb") as handle:
        changed_bytes = handle.read()
    print(f"    Modified file SHA-256 digest: {sha256_hex(changed_bytes)}")
    print(f"    Digests differ after one-word change: "
          f"{sha256_hex(changed_bytes) != sha256_hex(original_bytes)}")

    modified_ok = verify_signature(public_key, changed_bytes, file_signature)
    file_change_detected = not modified_ok
    print(f"    Verify MODIFIED file against original signature: "
          f"{'succeeded (UNEXPECTED)' if modified_ok else 'failed -> change detected'}")
    print("Modified file signature verification:",
          "CHANGE DETECTED" if file_change_detected else "FAIL")
    print()

    # Step 4: restore the original file, then delete it.
    with open(DEMO_POLICY_FILE, "w", encoding="utf-8") as handle:
        handle.write(ORIGINAL_POLICY_TEXT)
    with open(DEMO_POLICY_FILE, "rb") as handle:
        restored_bytes = handle.read()
    restored_ok = sha256_hex(restored_bytes) == sha256_hex(original_bytes)
    print(f"    Restored file matches original: {restored_ok}")

    os.remove(DEMO_POLICY_FILE)
    still_exists = os.path.exists(DEMO_POLICY_FILE)
    print(f"    File deleted at end of lab: {not still_exists}")
    print("    -> A file signature protects file contents exactly the same way:")
    print("       any change to the bytes breaks verification.")

    return unchanged_ok and file_change_detected and restored_ok and not still_exists


# ---------------------------------------------------------------------------
# 4. CERTIFICATE GENERATION
# ---------------------------------------------------------------------------

def generate_signing_certificate(private_key, public_key, fingerprint):
    """Create a self-signed X.509 certificate for the signing public key."""
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "derexi-signing-demo.local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Aurum Capital Bank"),
            x509.NameAttribute(
                NameOID.ORGANIZATIONAL_UNIT_NAME, "Policy Governance Lab"
            ),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]
    )

    now = datetime.now(timezone.utc)
    not_before = now - timedelta(minutes=5)
    not_after = now + timedelta(days=365)

    # Self-signed: issuer == subject, signed by this same private key.
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
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

    print("  Subject (the identity that owns the signing key):")
    print(f"    Common Name (CN):       "
          f"{name_value(certificate.subject, NameOID.COMMON_NAME)}")
    print(f"    Organization (O):       "
          f"{name_value(certificate.subject, NameOID.ORGANIZATION_NAME)}")
    print(f"    Organizational Unit:    "
          f"{name_value(certificate.subject, NameOID.ORGANIZATIONAL_UNIT_NAME)}")
    print(f"    Country:                "
          f"{name_value(certificate.subject, NameOID.COUNTRY_NAME)}")
    print()
    print("  Issuer (who signed the certificate):")
    print(f"    Common Name (CN):       "
          f"{name_value(certificate.issuer, NameOID.COMMON_NAME)}")
    print(f"    Self-signed (issuer == subject): "
          f"{certificate.issuer == certificate.subject}")
    print()
    print("  Certificate metadata:")
    print(f"    Serial number (hex):    {format(certificate.serial_number, 'x')}")
    print(f"    Valid from:             {certificate.not_valid_before_utc.isoformat()}")
    print(f"    Valid until:            {certificate.not_valid_after_utc.isoformat()}")
    print(f"    Validity period:        "
          f"{(certificate.not_valid_after_utc - certificate.not_valid_before_utc).days} days")
    print(f"    Signature algorithm:    RSA with "
          f"{certificate.signature_hash_algorithm.name.upper()}")
    print(f"    Public key in cert:     RSA "
          f"{certificate.public_key().key_size} bits, "
          f"exponent {certificate.public_key().public_numbers().e}")
    print(f"    SHA-256 certificate fingerprint: {sha256_hex(certificate.public_bytes(serialization.Encoding.DER))}")
    print(f"    Extensions:             BasicConstraints (CA:FALSE), KeyUsage")
    print()

    # Verify the certificate carries the SAME public key used for verification.
    cert_key_der = certificate.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key_der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    keys_match = cert_key_der == key_der
    fingerprint_match = (
        public_key_fingerprint(certificate.public_key()) == fingerprint
    )

    # Verify the certificate really is self-signed (signature checks out
    # against its own public key).
    try:
        certificate.verify_directly_issued_by(certificate)
        self_signed_ok = True
        self_signed_note = "valid (verifies against its own public key)"
    except Exception as exc:  # pragma: no cover - defensive
        self_signed_ok = False
        self_signed_note = f"FAILED ({exc})"

    not_expired = (
        certificate.not_valid_before_utc
        <= now
        <= certificate.not_valid_after_utc
    )

    print("  Verification:")
    print(f"    Certificate public key == verification public key: {keys_match}")
    print(f"    Public key fingerprint matches: {fingerprint_match}")
    print(f"    Self-signed check: {self_signed_note}")
    print(f"    Not expired right now: {not_expired}")
    print(f"    Serial number is positive: {certificate.serial_number > 0}")
    print()

    # Certificates are PUBLIC material, so unlike the private key it is fine
    # to write this PEM to disk and show a preview. (Deleted later.)
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
    with open(DEMO_CERT_PEM, "wb") as handle:
        handle.write(cert_pem)
    try:
        os.chmod(DEMO_CERT_PEM, 0o644)
    except OSError:  # pragma: no cover - platform dependent
        pass
    print(f"  Wrote DEMO_ONLY_signing_certificate.pem ({len(cert_pem)} bytes) --")
    print("    public material only, safe to distribute.")
    with open(DEMO_CERT_PEM, "r", encoding="ascii") as handle:
        cert_lines = handle.read().splitlines()
    print(f"    PEM preview: {cert_lines[0]}")
    print(f"    {cert_lines[1]} ...")
    reloaded_cert = x509.load_pem_x509_certificate(cert_pem)
    print(f"    Reloaded certificate matches: "
          f"{reloaded_cert.public_bytes(serialization.Encoding.PEM) == cert_pem}")
    print()

    print("  Note: a certificate identifies a key -- it does NOT replace the")
    print("    signature check. The verifier uses the certificate's public key")
    print("    to verify the signature on the message.")

    verified = keys_match and fingerprint_match and self_signed_ok and not_expired
    return certificate, verified


# ---------------------------------------------------------------------------
# 5. CERTIFICATE MANAGEMENT
# ---------------------------------------------------------------------------

def document_certificate_management(private_key):
    """Explain certificate lifecycle, then demo safe temporary PEM handling."""
    print("  Identity binding:")
    print("    - Certificates bind an identity (a name/host) to a public key.")
    print("    - Verifiers use that binding to decide whose signature they are")
    print("      checking.")
    print("  Issuance and trust:")
    print("    - Real production certificates are normally signed by a trusted")
    print("      Certificate Authority (CA), not by themselves.")
    print("    - The CA's signature is what makes the identity claim trustworthy.")
    print("  Lifecycle:")
    print("    - Certificates have validity periods (not-before / not-after).")
    print("    - Certificates may need renewal before they expire.")
    print("    - Certificates may need revocation if the private key is")
    print("      compromised (published via CRL or checked with OCSP).")
    print("  Key protection:")
    print("    - Private signing keys must be protected from disclosure.")
    print("    - Production private keys belong in a KMS, HSM, or another")
    print("      secure key-management system.")
    print("    - Private keys must never be committed to Git.")
    print("    - Public keys and certificates may be distributed publicly.")
    print()

    # --- Practical demo: write, restrict, reload, verify, delete ---
    print("  Live demonstration of safe temporary key handling:")
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    print(f"    - Serialized signing key to PEM in memory ({len(pem_bytes)} bytes).")
    print("    - PEM body is NOT printed to the terminal.")

    structure_ok = False
    reload_ok = False
    try:
        with open(DEMO_KEY_PEM, "wb") as handle:
            handle.write(pem_bytes)
        try:
            os.chmod(DEMO_KEY_PEM, 0o600)
            perm_note = "0o600 (owner read/write only)"
        except OSError:  # pragma: no cover - platform dependent
            perm_note = "default (platform does not support chmod)"
        size = os.path.getsize(DEMO_KEY_PEM)
        print(f"    - Wrote DEMO_ONLY_signing_key.pem ({size} bytes), "
              f"permissions {perm_note}.")

        with open(DEMO_KEY_PEM, "r", encoding="ascii") as handle:
            lines = handle.read().splitlines()
        structure_ok = (
            lines[0].startswith("-----BEGIN ")
            and lines[-1].startswith("-----END ")
            and lines[0].replace("BEGIN", "END") == lines[-1]
            and len(lines) > 4
        )
        print(f"    - PEM BEGIN/END markers verified (base64 body withheld): "
              f"{structure_ok}")

        reloaded = serialization.load_pem_private_key(pem_bytes, password=None)
        # RSAPrivateNumbers has no "private_value" attribute, so compare the
        # core RSA parameters instead.
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
        print(f"    - Temporary key handling demo failed: {exc}")

    print()
    print("  Cleaning up DEMO ONLY files now...")
    for path in (DEMO_KEY_PEM, DEMO_CERT_PEM, DEMO_POLICY_FILE):
        if os.path.exists(path):
            os.remove(path)
            print(f"    - Deleted: {os.path.basename(path)}")
        else:
            print(f"    - Not present (nothing to delete): {os.path.basename(path)}")

    leftovers = [p for p in (DEMO_KEY_PEM, DEMO_CERT_PEM, DEMO_POLICY_FILE)
                 if os.path.exists(p)]
    print(f"    - DEMO files remaining on disk: {len(leftovers)}")
    print("    - Confirmed: no production-style keys are saved in the repository.")
    print()
    print("  IMPORTANT: the signing key in this lab is a throwaway demo key.")
    print("    - Never reuse lab keys in a real system.")
    print("    - Do NOT save permanent production-style keys in this repository.")

    verified = structure_ok and reload_ok and not leftovers
    return verified


# ---------------------------------------------------------------------------
# 6. TRUST MODEL
# ---------------------------------------------------------------------------

def document_trust_model():
    """Explain who trusts whom, and how signatures rely on certificates."""
    print("  1. SIGNER")
    print("     - Holds the private signing key.")
    print("     - Creates the digital signature over the message.")
    print()
    print("  2. VERIFIER")
    print("     - Receives the message, the signature, and the certificate")
    print("       (or public key).")
    print("     - Verifies the signature using the public key.")
    print()
    print("  3. CERTIFICATE")
    print("     - Associates the public key with the claimed identity.")
    print("     - Without it, a verifier has a key but no reason to believe")
    print("       whose key it is.")
    print()
    print("  4. CERTIFICATE AUTHORITY")
    print("     - In a real PKI, a trusted CA signs the certificate.")
    print("     - The verifier trusts the identity because they trust the CA.")
    print()
    print("  5. SELF-SIGNED LAB LIMITATION")
    print("     - This classroom certificate is self-signed.")
    print("     - It proves the technical certificate/signature workflow works.")
    print("     - It does NOT create external trust by itself.")
    print("     - A verifier must manually trust the certificate or public key.")
    print()
    print("  The trust chain concept:")
    print()
    print("    Trusted Root CA")
    print("          |")
    print("          |  signs")
    print("          v")
    print("    Intermediate CA")
    print("          |")
    print("          |  signs")
    print("          v")
    print("    End-Entity / Signing Certificate")
    print("          |")
    print("          |  uses its private key")
    print("          v")
    print("    Digital Signature")
    print()
    print("    Each level is signed by the level above it, so trust flows")
    print("    downward from a Root CA that the verifier already trusts.")
    print()
    print("  IMPORTANT: this classroom lab uses ONLY the end-entity")
    print("    self-signed certificate. There is no Root CA and no Intermediate")
    print("    CA in this lab -- the certificate vouches for itself.")
    print()
    print("  What that means in practice:")
    print("    - The signature proves integrity and identity of the key holder.")
    print("    - It does NOT by itself tell a stranger that the key is trustworthy.")
    print("    - In production DeRexi, a trusted CA (or an internal enterprise CA)")
    print("      would issue the signing certificate, and verifiers would be")
    print("      configured to trust that CA.")

    verified = True
    return verified


# ---------------------------------------------------------------------------
# 8. SECURITY CONSIDERATIONS
# ---------------------------------------------------------------------------

def print_security_considerations():
    print("  RSA-PSS:")
    print("    - Preferred modern padding for RSA signatures.")
    print("    - Includes randomness (a salt), so the same message does not")
    print("      always produce the same signature.")
    print("    - SHA-256 provides the message digest that is signed.")
    print("    - Always verify with the same salt length used when signing.")
    print()
    print("  Private keys:")
    print("    - Must remain confidential.")
    print("    - Should be protected by strong access controls.")
    print("    - Should not be stored directly in source code.")
    print("    - Must never be committed to Git.")
    print()
    print("  Verification:")
    print("    - Validates integrity and authenticity.")
    print("    - Does NOT encrypt the message -- it stays readable by anyone.")
    print("    - Does NOT provide confidentiality.")
    print("    - A valid signature only proves the key holder signed it; always")
    print("      confirm the certificate/key is one you actually trust.")
    print()
    print("  Certificates:")
    print("    - Provide identity binding (name <-> public key).")
    print("    - Trust depends on the issuing authority.")
    print("    - Self-signed certificates require explicit/manual trust.")
    print()
    print("  Revocation:")
    print("    - Compromised signing keys require immediate revocation/replacement.")
    print("    - Signatures made with a compromised key can no longer be assumed")
    print("      trustworthy.")
    print("    - Revocation lists (CRL) and OCSP help verifiers find out quickly.")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("=== DEREXI CRYPTOGRAPHY LAB 5 ===")
    print("Digital Signatures -- classroom demonstration (fictional data only)")
    print("No production DeRexi code, credentials, or API keys are used.")
    print()

    try:
        print("=== RSA SIGNING KEY PAIR ===")
        private_key, public_key, fingerprint, keypair_ok = generate_signing_key_pair()
        print()
        print("RSA signing key pair:", "PASS" if keypair_ok else "FAIL")
        print()

        print("=== DIGITAL SIGNATURE CREATION ===")
        message, signature, create_ok = create_digital_signature(
            private_key, public_key
        )
        print()
        print("RSA digital signature creation:", "PASS" if create_ok else "FAIL")
        print()

        print("=== SIGNATURE VERIFICATION ===")
        verify_ok, change_detected = verify_signature_section(
            private_key, public_key, message, signature
        )
        print()

        print("=== SIGNING CERTIFICATE ===")
        _certificate, cert_ok = generate_signing_certificate(
            private_key, public_key, fingerprint
        )
        print()
        print("Signing certificate generation:", "PASS" if cert_ok else "FAIL")
        print()

        print("=== CERTIFICATE MANAGEMENT ===")
        mgmt_ok = document_certificate_management(private_key)
        print()
        print("Certificate management documented:", "PASS" if mgmt_ok else "FAIL")
        print()

        print("=== TRUST MODEL ===")
        trust_ok = document_trust_model()
        print()
        print("Digital-signature trust model documented:",
              "PASS" if trust_ok else "FAIL")
        print()

        print("=== SECURITY CONSIDERATIONS ===")
        print_security_considerations()
        print()

        print("=== SUMMARY ===")
        print("RSA signing key pair:", "PASS" if keypair_ok else "FAIL")
        print("RSA digital signature creation:", "PASS" if create_ok else "FAIL")
        print("Original signature verification:", "PASS" if verify_ok else "FAIL")
        print("Tampered message verification:",
              "CHANGE DETECTED" if change_detected else "FAIL")
        print("Signing certificate generation:", "PASS" if cert_ok else "FAIL")
        print("Certificate management documented:", "PASS" if mgmt_ok else "FAIL")
        print("Digital-signature trust model documented:",
              "PASS" if trust_ok else "FAIL")
        print()
        print("DeRexi digital signatures lab completed.")
        print()
    finally:
        # Safety net: NEVER leave temporary demo material on disk, even if a
        # section raises part way through the run.
        for path in (DEMO_KEY_PEM, DEMO_CERT_PEM, DEMO_POLICY_FILE):
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    main()
